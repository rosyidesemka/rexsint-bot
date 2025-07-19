"""
Admin Handler for RexSint Bot
Handles admin panel and administrative operations
"""
import os
import json
import logging
import json
import os
from typing import Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.database import DatabaseManager
from core.utils import (
    get_admin_keyboard,
    get_api_management_keyboard,
    format_bot_status,
    get_system_info,
    validate_admin_command,
    create_error_message,
    create_success_message,
    create_warning_message,
    mask_sensitive_data
)

class AdminHandler:
    """Handles admin panel and operations"""
    
    def __init__(self, db_manager: DatabaseManager, config: Dict[str, Any]):
        self.db_manager = db_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.admin_chat_id = config.get('Admin', {}).get('admin_chat_id')
        self.admin_context = {}  # Store admin operation context
    
    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show admin menu"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if not self.db_manager.is_admin(user_id):
                await update.message.reply_text(
                    "❌ Akses ditolak. Anda bukan admin.",
                    parse_mode='Markdown'
                )
                return
            
            # Get system info
            system_info = get_system_info()
            bot_status = self.db_manager.get_bot_status()
            user_stats = self.db_manager.get_user_stats()
            
            admin_message = f"""
🛡️ **Panel Admin RexSint**

📊 **Statistik Sistem:**
• Total Pengguna: {user_stats.get('total_users', 0)}
• Pengguna Aktif: {user_stats.get('active_users', 0)}
• Pengguna Baru Hari Ini: {user_stats.get('new_users_today', 0)}
• Pengguna Diblokir: {user_stats.get('blocked_users', 0)}

🤖 **Status Bot:**
• API Request: {bot_status.get('api_request_count', 0) if bot_status else 0}/99
• Maintenance: {'🔴 Ya' if bot_status and bot_status.get('is_maintenance') else '🟢 Tidak'}
• Memory Usage: {system_info.get('memory_percent', 0):.1f}%
• CPU Usage: {system_info.get('cpu_percent', 0):.1f}%

⚡ **Quick Actions:**
Gunakan menu di bawah untuk mengelola bot dan pengguna.
            """
            
            await update.message.reply_text(
                admin_message,
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing admin menu: {e}")
            await update.message.reply_text(
                create_error_message("Gagal menampilkan panel admin"),
                parse_mode='Markdown'
            )
    
    async def activate_trial(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /activatetrial command"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if not self.db_manager.is_admin(user_id):
                await update.message.reply_text(
                    "❌ Akses ditolak. Anda bukan admin.",
                    parse_mode='Markdown'
                )
                return
            
            # Validate command format
            command_text = update.message.text
            validation = validate_admin_command(command_text, user_id)
            
            if not validation['valid']:
                await update.message.reply_text(
                    create_error_message(validation['error']),
                    parse_mode='Markdown'
                )
                return
            
            target_user_id = validation['user_id']
            
            # Check if user exists
            target_user = self.db_manager.get_user(target_user_id)
            if not target_user:
                await update.message.reply_text(
                    create_error_message(f"Pengguna dengan ID {target_user_id} tidak ditemukan"),
                    parse_mode='Markdown'
                )
                return
            
            # Activate trial
            success = self.db_manager.activate_trial(target_user_id)
            
            if success:
                # Notify target user
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text="""
✅ **Fitur Pencarian Diaktifkan!**

🎉 **Selamat!** Admin telah mengaktifkan fitur pencarian untuk akun Anda.

💎 **Fitur yang tersedia:**
• Pencarian di semua database
• AI Summary hasil pencarian
• Unduh laporan lengkap
• Akses premium features

🚀 **Mulai sekarang Anda dapat menggunakan menu 🔎 Fitur Pencarian Data!**
                        """,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    self.logger.warning(f"Could not notify user {target_user_id}: {e}")
                
                await update.message.reply_text(
                    create_success_message(f"Trial berhasil diaktifkan untuk pengguna {target_user.get('first_name', 'N/A')} (ID: {target_user_id})"),
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    create_error_message("Gagal mengaktifkan trial"),
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            self.logger.error(f"Error activating trial: {e}")
            await update.message.reply_text(
                create_error_message("Gagal memproses perintah aktivasi trial"),
                parse_mode='Markdown'
            )
    
    async def generate_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /generate command"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if not self.db_manager.is_admin(user_id):
                await update.message.reply_text(
                    "❌ Akses ditolak. Anda bukan admin.",
                    parse_mode='Markdown'
                )
                return
            
            # Validate command format
            command_text = update.message.text
            validation = validate_admin_command(command_text, user_id)
            
            if not validation['valid']:
                await update.message.reply_text(
                    create_error_message(validation['error']),
                    parse_mode='Markdown'
                )
                return
            
            target_user_id = validation['user_id']
            
            # Get user data
            target_user = self.db_manager.get_user(target_user_id)
            if not target_user:
                await update.message.reply_text(
                    create_error_message(f"Pengguna dengan ID {target_user_id} tidak ditemukan"),
                    parse_mode='Markdown'
                )
                return
            
            # Get API token
            api_token = target_user.get('api_token')
            if not api_token:
                await update.message.reply_text(
                    create_error_message("Token API tidak ditemukan untuk pengguna ini"),
                    parse_mode='Markdown'
                )
                return
            
            # Send masked token to admin
            masked_token = mask_sensitive_data(api_token)
            full_token = api_token
            
            response_message = f"""
🔑 **Token API Pengguna**

👤 **Pengguna:** {target_user.get('first_name', 'N/A')} (ID: {target_user_id})
🔐 **Token (Masked):** {masked_token}

⚠️ **PERINGATAN:** Token lengkap akan dikirim dalam pesan terpisah untuk keamanan.
            """
            
            await update.message.reply_text(
                response_message,
                parse_mode='Markdown'
            )
            
            # Send full token in separate message
            await update.message.reply_text(
                f"🔑 **Token Lengkap:**\n\n`{full_token}`",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error generating token: {e}")
            await update.message.reply_text(
                create_error_message("Gagal mengambil token API"),
                parse_mode='Markdown'
            )
    
    async def set_new_api(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /setnewapi command"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is admin
            if not self.db_manager.is_admin(user_id):
                await update.message.reply_text(
                    "❌ Akses ditolak. Anda bukan admin.",
                    parse_mode='Markdown'
                )
                return
            
            # Validate command format
            command_text = update.message.text
            validation = validate_admin_command(command_text, user_id)
            
            if not validation['valid']:
                await update.message.reply_text(
                    create_error_message(validation['error']),
                    parse_mode='Markdown'
                )
                return
            
            new_token = validation['token']
            
            # Update bot status with new API token
            success = self.db_manager.set_new_api_token(new_token)
            
            if success:
                await update.message.reply_text(
                    create_success_message("API token berhasil diperbarui! Bot kini kembali online."),
                    parse_mode='Markdown'
                )
                
                # Log the change
                self.logger.info(f"API token updated by admin {user_id}")
                
            else:
                await update.message.reply_text(
                    create_error_message("Gagal memperbarui API token"),
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            self.logger.error(f"Error setting new API: {e}")
            await update.message.reply_text(
                create_error_message("Gagal memperbarui API token"),
                parse_mode='Markdown'
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle admin callback queries"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            # Check if user is admin
            if not self.db_manager.is_admin(user_id):
                await query.edit_message_text("❌ Akses ditolak. Anda bukan admin.")
                return
            
            if data == "admin_stats":
                await self._show_user_stats(query)
            elif data == "admin_manage_admins":
                await self._show_admin_management(query)
            elif data == "admin_manage_users":
                await self._show_user_management(query)
            elif data == "admin_activate_trial":
                await self._show_trial_activation(query)
            elif data == "admin_broadcast":
                await self._show_broadcast_menu(query)
            elif data == "admin_bot_status":
                await self._show_bot_status(query)
            elif data == "admin_logs":
                await self._show_logs(query)
            elif data == "admin_api_management":
                await self._show_api_management(query)
            elif data.startswith("api_"):
                await self._handle_api_callback(query, data, context)
            elif data.startswith("user_"):
                await self._handle_user_callback(query, data, context)
            elif data.startswith("broadcast_"):
                await self._handle_broadcast_callback(query, data, context)
            elif data == "back_to_admin":
                await self._back_to_admin_menu(query)
            
        except Exception as e:
            self.logger.error(f"Error handling admin callback: {e}")
            await query.edit_message_text(
                create_error_message("Terjadi kesalahan dalam memproses permintaan admin")
            )
    
    async def _show_user_stats(self, query) -> None:
        """Show detailed user statistics"""
        try:
            user_stats = self.db_manager.get_user_stats()
            
            # Get additional statistics
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get top users by requests
            cursor.execute('''
                SELECT first_name, total_requests, file_requests 
                FROM users 
                ORDER BY total_requests DESC 
                LIMIT 5
            ''')
            top_users = cursor.fetchall()
            
            # Get recent registrations
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE DATE(registration_date) >= DATE('now', '-7 days')
            ''')
            new_users_week = cursor.fetchone()[0]
            
            # Get subscription statistics
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE subscription_end_date > datetime('now')
            ''')
            active_subscriptions = cursor.fetchone()[0]
            
            conn.close()
            
            stats_message = f"""
📊 **Statistik Pengguna Detail**

👥 **Overview:**
• Total Pengguna: {user_stats.get('total_users', 0)}
• Pengguna Aktif: {user_stats.get('active_users', 0)}
• Pengguna Diblokir: {user_stats.get('blocked_users', 0)}
• Berlangganan Aktif: {active_subscriptions}

📈 **Pendaftaran:**
• Hari ini: {user_stats.get('new_users_today', 0)}
• Minggu ini: {new_users_week}

🏆 **Top Users (By Requests):**
            """
            
            for i, user in enumerate(top_users, 1):
                stats_message += f"{i}. {user[0]} - {user[1]} searches ({user[2]} file)\n"
            
            keyboard = [[InlineKeyboardButton("⬅️ Kembali ke Panel Admin", callback_data="back_to_admin")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                stats_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing user stats: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan statistik pengguna")
            )
    
    async def _show_api_management(self, query) -> None:
        """Show API management menu"""
        try:
            bot_status = self.db_manager.get_bot_status()
            
            if not bot_status:
                message = "❌ Status bot tidak ditemukan"
            else:
                message = format_bot_status(bot_status)
            
            await query.edit_message_text(
                message,
                reply_markup=get_api_management_keyboard(),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing API management: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan manajemen API")
            )
    
    async def _show_bot_status(self, query) -> None:
        """Show detailed bot status"""
        try:
            bot_status = self.db_manager.get_bot_status()
            system_info = get_system_info()
            
            status_message = f"""
🤖 **Status Bot Detail**

{format_bot_status(bot_status)}

💻 **Sistem:**
• Platform: {system_info.get('platform', 'N/A')}
• Python: {system_info.get('python_version', 'N/A')}
• Memory: {system_info.get('process_memory', 'N/A')}
• Uptime: {system_info.get('uptime', 'N/A')}

💾 **Storage:**
• Disk Usage: {system_info.get('disk_percent', 0):.1f}%
• Available: {system_info.get('disk_total', 'N/A')}
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh Status", callback_data="admin_bot_status")],
                [InlineKeyboardButton("⬅️ Kembali ke Panel Admin", callback_data="back_to_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                status_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing bot status: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan status bot")
            )
    
    async def _show_logs(self, query) -> None:
        """Show recent logs"""
        try:
            # Read log history
            log_file = "assets/log_history.json"
            
            if not os.path.exists(log_file):
                message = "📜 **Log History**\n\n❌ Tidak ada log ditemukan."
            else:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                if not logs:
                    message = "📜 **Log History**\n\n❌ Log kosong."
                else:
                    # Show last 10 logs
                    recent_logs = logs[-10:]
                    message = "📜 **Log History (10 Terakhir)**\n\n"
                    
                    for log in recent_logs:
                        timestamp = log.get('timestamp', 'N/A')[:16]  # YYYY-MM-DD HH:MM
                        user_id = log.get('user_id', 'N/A')
                        search_type = log.get('search_type', 'N/A')
                        query = log.get('query', 'N/A')[:30]  # First 30 chars
                        
                        message += f"• {timestamp} - User {user_id}\n"
                        message += f"  {search_type}: {query}...\n\n"
            
            keyboard = [
                [InlineKeyboardButton("📥 Download Full Log", callback_data="download_full_log")],
                [InlineKeyboardButton("⬅️ Kembali ke Panel Admin", callback_data="back_to_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing logs: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan log")
            )
    
    async def _show_broadcast_menu(self, query) -> None:
        """Show broadcast menu"""
        try:
            user_stats = self.db_manager.get_user_stats()
            
            message = f"""
📢 **Broadcast Pesan**

📊 **Target:**
• Total Pengguna: {user_stats.get('total_users', 0)}
• Pengguna Aktif: {user_stats.get('active_users', 0)}
• Pengguna Non-Blokir: {user_stats.get('total_users', 0) - user_stats.get('blocked_users', 0)}

💡 **Cara Penggunaan:**
1. Pilih target broadcast
2. Ketik pesan yang ingin dikirim
3. Konfirmasi pengiriman

⚠️ **Catatan:**
• Pesan akan dikirim ke semua pengguna yang tidak diblokir
• Proses pengiriman mungkin membutuhkan waktu
• Bot akan memberikan laporan progress

Pilih target broadcast di bawah ini:
            """
            
            keyboard = [
                [InlineKeyboardButton("📢 Broadcast ke Semua", callback_data="broadcast_all")],
                [InlineKeyboardButton("💎 Broadcast ke Pengguna Aktif", callback_data="broadcast_active")],
                [InlineKeyboardButton("⬅️ Kembali ke Panel Admin", callback_data="back_to_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing broadcast menu: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan menu broadcast")
            )
    
    async def _handle_api_callback(self, query, data: str, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle API management callbacks"""
        try:
            if data == "api_current_status":
                await self._show_api_management(query)
            elif data == "api_get_user_token":
                await self._prompt_user_id_for_token(query)
            elif data == "api_set_new_token":
                await self._prompt_new_api_token(query)
            elif data == "api_restart_bot":
                await self._restart_bot(query, context)
            
        except Exception as e:
            self.logger.error(f"Error handling API callback: {e}")
            await query.edit_message_text(
                create_error_message("Gagal memproses permintaan API")
            )
    
    async def _prompt_user_id_for_token(self, query) -> None:
        """Prompt admin to enter user ID for token retrieval"""
        try:
            message = """
🔍 **Dapatkan Token Pengguna**

📝 **Instruksi:**
Ketik perintah berikut untuk mendapatkan token API pengguna:

`/generate <user_id>`

**Contoh:**
`/generate 123456789`

⚠️ **Catatan:**
• User ID harus berupa angka
• User harus terdaftar di sistem
• Token akan ditampilkan dalam format masked untuk keamanan
            """
            
            keyboard = [[InlineKeyboardButton("⬅️ Kembali ke API Management", callback_data="admin_api_management")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error prompting user ID: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan prompt")
            )
    
    async def _prompt_new_api_token(self, query) -> None:
        """Prompt admin to enter new API token"""
        try:
            message = """
🚀 **Atur Token API Baru**

📝 **Instruksi:**
Ketik perintah berikut untuk mengatur token API baru:

`/setnewapi <api_token>`

**Contoh:**
`/setnewapi 987654321:abcdefghijk`

⚠️ **Catatan:**
• Token harus valid dan aktif
• Bot akan keluar dari mode maintenance
• Counter request akan direset ke 0
• Semua pengguna akan dapat menggunakan bot kembali

🔄 **Proses:**
1. Bot akan validasi token
2. Update database status
3. Reset counter dan aktivasi
4. Konfirmasi perubahan
            """
            
            keyboard = [[InlineKeyboardButton("⬅️ Kembali ke API Management", callback_data="admin_api_management")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error prompting new API token: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan prompt")
            )
    
    async def _restart_bot(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Restart bot (simulate restart by clearing cache)"""
        try:
            # Clear user context
            context.user_data.clear()
            context.chat_data.clear()
            
            # Reset maintenance mode
            self.db_manager.set_maintenance_mode(False)
            
            await query.edit_message_text(
                create_success_message("Bot berhasil direstart! Semua cache telah dibersihkan."),
                parse_mode='Markdown'
            )
            
            self.logger.info("Bot restarted by admin")
            
        except Exception as e:
            self.logger.error(f"Error restarting bot: {e}")
            await query.edit_message_text(
                create_error_message("Gagal merestart bot")
            )
    
    async def _back_to_admin_menu(self, query) -> None:
        """Go back to admin menu"""
        try:
            # Get fresh statistics
            system_info = get_system_info()
            bot_status = self.db_manager.get_bot_status()
            user_stats = self.db_manager.get_user_stats()
            
            admin_message = f"""
🛡️ **Panel Admin RexSint**

📊 **Statistik Sistem:**
• Total Pengguna: {user_stats.get('total_users', 0)}
• Pengguna Aktif: {user_stats.get('active_users', 0)}
• Pengguna Baru Hari Ini: {user_stats.get('new_users_today', 0)}
• Pengguna Diblokir: {user_stats.get('blocked_users', 0)}

🤖 **Status Bot:**
• API Request: {bot_status.get('api_request_count', 0) if bot_status else 0}/99
• Maintenance: {'🔴 Ya' if bot_status and bot_status.get('is_maintenance') else '🟢 Tidak'}
• Memory Usage: {system_info.get('memory_percent', 0):.1f}%
• CPU Usage: {system_info.get('cpu_percent', 0):.1f}%

⚡ **Quick Actions:**
Gunakan menu di bawah untuk mengelola bot dan pengguna.
            """
            
            await query.edit_message_text(
                admin_message,
                reply_markup=get_admin_keyboard(),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error going back to admin menu: {e}")
            await query.edit_message_text(
                create_error_message("Gagal kembali ke menu admin")
            )