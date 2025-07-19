"""
Start Handler for RexSint Bot
Handles /start command and main menu interactions
"""

import logging
from typing import Dict, Any
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from core.database import DatabaseManager
from core.auth import AuthManager
from core.utils import (
    get_main_keyboard, 
    get_info_menu_keyboard, 
    get_faq_keyboard,
    get_faq_data,
    format_user_info,
    create_success_message,
    create_error_message
)

class StartHandler:
    """Handles start command and main menu interactions"""
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        self.db_manager = db_manager
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        try:
            user = update.effective_user
            user_id = user.id
            first_name = user.first_name or "User"
            username = user.username
            
            # Check channel membership
            is_member = await self.auth_manager.check_channel_membership(context.bot, user_id)
            
            if not is_member:
                await self.auth_manager.send_channel_verification_message(update, context)
                return
            
            # Check if user exists
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                # Generate API token for new user
                bot_status = self.db_manager.get_bot_status()
                active_token = bot_status.get('active_api_token') if bot_status else None
                
                if not active_token:
                    await update.message.reply_text(
                        "❌ Bot belum dikonfigurasi. Hubungi admin untuk mengaktifkan bot.",
                        parse_mode='Markdown'
                    )
                    return
                
                # Add new user to database
                success = self.db_manager.add_user(user_id, first_name, username)
                
                if success:
                    # Notify admin about new user
                    await self.auth_manager.notify_admin(
                        context,
                        f"📝 **Pengguna Baru Terdaftar**\n\n"
                        f"🆔 **ID:** {user_id}\n"
                        f"👤 **Nama:** {first_name}\n"
                        f"👤 **Username:** @{username or 'N/A'}\n\n"
                        f"✅ Trial 7 hari telah diberikan otomatis."
                    )
                    
                    # Get updated user data
                    user_data = self.db_manager.get_user(user_id)
                    
                    # Welcome message
                    welcome_message = f"""
✅ **Selamat datang, {first_name}!**

🎉 **Akun Anda berhasil dibuat!**

💎 **Yang Anda dapatkan:**
• Trial premium 7 hari
• 10 token pencarian gratis
• Akses ke semua database
• Fitur AI summary
• Laporan lengkap (HTML)

⚠️ **PENTING:** Untuk mengaktifkan fitur pencarian, diperlukan pembayaran aktivasi sebesar **50.000 Rp**. Silakan kunjungi menu **🛒 Toko** untuk melakukan aktivasi.

📖 **Panduan Singkat:**
• Gunakan **🔎 Fitur Pencarian Data** untuk mencari informasi
• Lihat **ℹ️ Informasi** untuk status akun Anda
• Kunjungi **🛒 Toko** untuk aktivasi dan berlangganan
• Atur **⚙️ Pengaturan** sesuai preferensi Anda

🚀 **Siap untuk memulai? Pilih menu di bawah!**
                    """
                    
                    await update.message.reply_text(
                        welcome_message,
                        reply_markup=get_main_keyboard(user_data.get('language_code', 'id')),
                        parse_mode='Markdown'
                    )
                    
                    # Log user activity
                    await self.auth_manager.log_user_activity(
                        user_id, "user_registered", f"New user registration: {first_name}"
                    )
                    
                else:
                    await update.message.reply_text(
                        "❌ Terjadi kesalahan saat mendaftarkan akun. Silakan coba lagi.",
                        parse_mode='Markdown'
                    )
                    
            else:
                # Existing user
                lang = user_data.get('language_code', 'id')
                
                if lang == 'id':
                    message = f"""
🏠 **Selamat datang kembali, {first_name}!**

🤖 **RexSint OSINT Bot** siap membantu Anda!

💡 **Fitur yang tersedia:**
• 🔎 Pencarian data kebocoran
• 📊 Informasi akun dan statistik
• 🛒 Toko untuk berlangganan
• ⚙️ Pengaturan personal
• 📖 Panduan dan FAQ

Silakan pilih menu yang Anda butuhkan di bawah ini.
                    """
                else:
                    message = f"""
🏠 **Welcome back, {first_name}!**

🤖 **RexSint OSINT Bot** is ready to help you!

💡 **Available features:**
• 🔎 Data breach search
• 📊 Account information and statistics
• 🛒 Shop for subscriptions
• ⚙️ Personal settings
• 📖 Guides and FAQ

Please select the menu you need below.
                    """
                
                await update.message.reply_text(
                    message,
                    reply_markup=get_main_keyboard(lang),
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            self.logger.error(f"Error in start handler: {e}")
            await update.message.reply_text(
                "❌ Terjadi kesalahan. Silakan coba lagi atau hubungi admin.",
                parse_mode='Markdown'
            )
    
    async def user_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user information"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text(
                    "❌ Data pengguna tidak ditemukan. Silakan /start ulang.",
                    parse_mode='Markdown'
                )
                return
            
            lang = user_data.get('language_code', 'id')
            
            # Format user information
            info_text = format_user_info(user_data, lang)
            
            await update.message.reply_text(
                info_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing user info: {e}")
            await update.message.reply_text(
                create_error_message("Gagal menampilkan informasi pengguna"),
                parse_mode='Markdown'
            )
    
    async def info_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show info menu"""
        try:
            user_id = update.effective_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                await update.message.reply_text(
                    "❌ Data pengguna tidak ditemukan. Silakan /start ulang.",
                    parse_mode='Markdown'
                )
                return
            
            lang = user_data.get('language_code', 'id')
            
            if lang == 'id':
                message = """
📖 **Menu Informasi RexSint**

🔍 **Tentang RexSint OSINT Bot:**
Bot ini menyediakan akses ke database kebocoran data dari berbagai sumber terpercaya untuk tujuan keamanan dan penelitian.

📊 **Database yang tersedia:**
• 3000+ database kebocoran
• 50+ juta record data
• Update berkala dari sumber terpercaya
• Verifikasi dan validasi data

🛡️ **Keamanan & Privasi:**
• Data dienkripsi saat penyimpanan
• Akses terbatas dan termonitor
• Audit trail setiap aktivitas
• Compliance dengan regulasi

Pilih menu di bawah untuk informasi lebih lanjut.
                """
            else:
                message = """
📖 **RexSint Information Menu**

🔍 **About RexSint OSINT Bot:**
This bot provides access to data breach databases from trusted sources for security and research purposes.

📊 **Available databases:**
• 3000+ breach databases
• 50+ million data records
• Regular updates from trusted sources
• Data verification and validation

🛡️ **Security & Privacy:**
• Encrypted data storage
• Limited and monitored access
• Audit trail for all activities
• Regulatory compliance

Select a menu below for more information.
                """
            
            await update.message.reply_text(
                message,
                reply_markup=get_info_menu_keyboard(lang),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing info menu: {e}")
            await update.message.reply_text(
                create_error_message("Gagal menampilkan menu informasi"),
                parse_mode='Markdown'
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries for info menu"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                await query.edit_message_text("❌ Data pengguna tidak ditemukan. Silakan /start ulang.")
                return
            
            lang = user_data.get('language_code', 'id')
            
            if data == "info_database_list":
                await self._show_database_list(query, lang)
            elif data == "info_faq":
                await self._show_faq_menu(query, lang)
            elif data.startswith("faq_"):
                await self._show_faq_answer(query, data, lang)
            elif data == "info_back":
                await self._back_to_main_menu(query, lang)
            elif data == "back_to_info":
                await self._back_to_info_menu(query, lang)
            elif data == "verify_membership":
                await self.auth_manager.verify_membership_callback(update, context)
            
        except Exception as e:
            self.logger.error(f"Error handling callback: {e}")
            await query.edit_message_text(
                create_error_message("Terjadi kesalahan dalam memproses permintaan")
            )
    
    async def _show_database_list(self, query, lang: str) -> None:
        """Show database list information"""
        try:
            if lang == 'id':
                message = """
📊 **Daftar Total Kebocoran Database**

🔢 **Statistik:**
• Total Database: 3000+
• Total Record: 50+ juta
• Update Terakhir: Harian
• Sumber: Terpercaya dan terverifikasi

📈 **Kategori Database:**
• Website komersial: 40%
• Platform sosial media: 25%
• Forum dan komunitas: 20%
• Layanan gaming: 10%
• Lainnya: 5%

📋 **Jenis Data:**
• Email address
• Password (hashed)
• Nama lengkap
• Nomor telepon
• Alamat IP
• Data profil lainnya

💾 **Unduh daftar lengkap database untuk melihat semua kebocoran yang tersedia.**
                """
            else:
                message = """
📊 **Total Database Breach List**

🔢 **Statistics:**
• Total Databases: 3000+
• Total Records: 50+ million
• Last Update: Daily
• Sources: Trusted and verified

📈 **Database Categories:**
• Commercial websites: 40%
• Social media platforms: 25%
• Forums and communities: 20%
• Gaming services: 10%
• Others: 5%

📋 **Data Types:**
• Email addresses
• Passwords (hashed)
• Full names
• Phone numbers
• IP addresses
• Other profile data

💾 **Download the complete database list to view all available breaches.**
                """
            
            # Create keyboard with download button
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            if lang == 'id':
                keyboard = [
                    [InlineKeyboardButton("📥 Unduh Daftar Database", callback_data="download_database_list")],
                    [InlineKeyboardButton("⬅️ Kembali ke Menu Info", callback_data="back_to_info")]
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("📥 Download Database List", callback_data="download_database_list")],
                    [InlineKeyboardButton("⬅️ Back to Info Menu", callback_data="back_to_info")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing database list: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan daftar database")
            )
    
    async def _show_faq_menu(self, query, lang: str) -> None:
        """Show FAQ menu"""
        try:
            if lang == 'id':
                message = """
❓ **Pertanyaan yang Sering Diajukan (FAQ)**

Pilih pertanyaan yang ingin Anda ketahui jawabannya:

🔍 **Topik yang tersedia:**
• Cara kerja kebocoran data
• Enkripsi dan keamanan password
• Perlindungan diri dari kebocoran
• Penggunaan legal data kebocoran
• Sumber dan validitas data

Klik tombol di bawah untuk melihat jawaban lengkap.
                """
            else:
                message = """
❓ **Frequently Asked Questions (FAQ)**

Select the question you want to know the answer to:

🔍 **Available topics:**
• How data breaches work
• Password encryption and security
• Self-protection from breaches
• Legal use of breach data
• Data sources and validity

Click the button below to see the complete answer.
                """
            
            await query.edit_message_text(
                message,
                reply_markup=get_faq_keyboard(lang),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing FAQ menu: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan menu FAQ")
            )
    
    async def _show_faq_answer(self, query, data: str, lang: str) -> None:
        """Show FAQ answer"""
        try:
            faq_data = get_faq_data(lang)
            faq_key = data.replace("faq_", "")
            
            if faq_key in faq_data:
                answer = faq_data[faq_key]
                
                # Create back button
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                if lang == 'id':
                    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke FAQ", callback_data="info_faq")]]
                else:
                    keyboard = [[InlineKeyboardButton("⬅️ Back to FAQ", callback_data="info_faq")]]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    answer,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    create_error_message("Jawaban FAQ tidak ditemukan")
                )
                
        except Exception as e:
            self.logger.error(f"Error showing FAQ answer: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan jawaban FAQ")
            )
    
    async def _back_to_main_menu(self, query, lang: str) -> None:
        """Back to main menu"""
        try:
            if lang == 'id':
                message = """
🏠 **Menu Utama RexSint OSINT Bot**

Selamat datang kembali di menu utama! Pilih fitur yang ingin Anda gunakan:

🔎 **Fitur Pencarian Data** - Cari informasi di database kebocoran
ℹ️ **Informasi** - Lihat status akun dan statistik
🛒 **Toko** - Berlangganan dan aktivasi fitur
⚙️ **Pengaturan** - Atur preferensi personal
📖 **Menu** - Panduan dan informasi tambahan

Silakan pilih menu yang Anda butuhkan.
                """
            else:
                message = """
🏠 **RexSint OSINT Bot Main Menu**

Welcome back to the main menu! Choose the feature you want to use:

🔎 **Search Features** - Search information in breach databases
ℹ️ **Information** - View account status and statistics
🛒 **Shop** - Subscriptions and feature activation
⚙️ **Settings** - Configure personal preferences
📖 **Menu** - Guides and additional information

Please select the menu you need.
                """
            
            await query.edit_message_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error going back to main menu: {e}")
            await query.edit_message_text(
                create_error_message("Gagal kembali ke menu utama")
            )
    
    async def _back_to_info_menu(self, query, lang: str) -> None:
        """Back to info menu"""
        try:
            if lang == 'id':
                message = """
📖 **Menu Informasi RexSint**

🔍 **Tentang RexSint OSINT Bot:**
Bot ini menyediakan akses ke database kebocoran data dari berbagai sumber terpercaya untuk tujuan keamanan dan penelitian.

📊 **Database yang tersedia:**
• 3000+ database kebocoran
• 50+ juta record data
• Update berkala dari sumber terpercaya
• Verifikasi dan validasi data

🛡️ **Keamanan & Privasi:**
• Data dienkripsi saat penyimpanan
• Akses terbatas dan termonitor
• Audit trail setiap aktivitas
• Compliance dengan regulasi

Pilih menu di bawah untuk informasi lebih lanjut.
                """
            else:
                message = """
📖 **RexSint Information Menu**

🔍 **About RexSint OSINT Bot:**
This bot provides access to data breach databases from trusted sources for security and research purposes.

📊 **Available databases:**
• 3000+ breach databases
• 50+ million data records
• Regular updates from trusted sources
• Data verification and validation

🛡️ **Security & Privacy:**
• Encrypted data storage
• Limited and monitored access
• Audit trail for all activities
• Regulatory compliance

Select a menu below for more information.
                """
            
            await query.edit_message_text(
                message,
                reply_markup=get_info_menu_keyboard(lang),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error going back to info menu: {e}")
            await query.edit_message_text(
                create_error_message("Gagal kembali ke menu informasi")
            )