"""
Settings Handler for RexSint Bot
Handles user settings and preferences
"""

import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.database import DatabaseManager
from core.utils import (
    get_settings_inline_keyboard,
    get_timezone_keyboard,
    get_language_keyboard,
    get_local_time,
    create_error_message,
    create_success_message
)

class SettingsHandler:
    """Handles user settings and preferences"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    async def settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show settings menu"""
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
            timezone = user_data.get('timezone', 'Asia/Jakarta')
            current_time = get_local_time(timezone)
            
            if lang == 'id':
                message = f"""
⚙️ **Pengaturan Akun**

👤 **Informasi Akun:**
• Nama: {user_data.get('first_name', 'N/A')}
• Username: @{user_data.get('username', 'N/A')}
• ID: {user_data.get('user_id', 'N/A')}

🌐 **Preferensi:**
• Bahasa: {'🇮🇩 Indonesia' if lang == 'id' else '🇬🇧 English'}
• Zona Waktu: {timezone}
• Waktu Lokal: {current_time}

📊 **Statistik:**
• Total Pencarian: {user_data.get('total_requests', 0)}
• Pencarian File: {user_data.get('file_requests', 0)}
• Token Tersisa: {user_data.get('token_balance', 0)} 🪙

⚙️ **Pengaturan yang Tersedia:**
• Ubah zona waktu
• Ganti bahasa interface
• Reset preferensi

Pilih pengaturan yang ingin diubah:
                """
            else:
                message = f"""
⚙️ **Account Settings**

👤 **Account Information:**
• Name: {user_data.get('first_name', 'N/A')}
• Username: @{user_data.get('username', 'N/A')}
• ID: {user_data.get('user_id', 'N/A')}

🌐 **Preferences:**
• Language: {'🇮🇩 Indonesia' if lang == 'id' else '🇬🇧 English'}
• Timezone: {timezone}
• Local Time: {current_time}

📊 **Statistics:**
• Total Searches: {user_data.get('total_requests', 0)}
• File Searches: {user_data.get('file_requests', 0)}
• Remaining Tokens: {user_data.get('token_balance', 0)} 🪙

⚙️ **Available Settings:**
• Change timezone
• Change interface language
• Reset preferences

Select the setting you want to change:
                """
            
            await update.message.reply_text(
                message,
                reply_markup=get_settings_inline_keyboard(lang),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing settings menu: {e}")
            await update.message.reply_text(
                create_error_message("Gagal menampilkan menu pengaturan"),
                parse_mode='Markdown'
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle settings callback queries"""
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
            
            if data == "settings_timezone":
                await self._show_timezone_selection(query, user_data, lang)
            elif data == "settings_language":
                await self._show_language_selection(query, user_data, lang)
            elif data == "settings_back":
                await self._back_to_main_menu(query, lang)
            elif data == "settings_main":
                await self._back_to_settings_menu(query, user_data, lang)
            elif data.startswith("set_timezone_"):
                timezone = data.replace("set_timezone_", "")
                await self._set_timezone(query, user_id, timezone, lang)
            elif data.startswith("set_language_"):
                new_lang = data.replace("set_language_", "")
                await self._set_language(query, user_id, new_lang, user_data)
            elif data == "reset_preferences":
                await self._reset_preferences(query, user_id, lang)
            elif data == "confirm_reset":
                await self._confirm_reset_preferences(query, user_id, lang)
            elif data == "cancel_reset":
                await self._back_to_settings_menu(query, user_data, lang)
            
        except Exception as e:
            self.logger.error(f"Error handling settings callback: {e}")
            await query.edit_message_text(
                create_error_message("Terjadi kesalahan dalam memproses pengaturan")
            )
    
    async def _show_timezone_selection(self, query, user_data: Dict[str, Any], lang: str) -> None:
        """Show timezone selection"""
        try:
            current_timezone = user_data.get('timezone', 'Asia/Jakarta')
            current_time = get_local_time(current_timezone)
            
            if lang == 'id':
                message = f"""
⌚ **Pengaturan Zona Waktu**

🌍 **Zona Waktu Saat Ini:**
• {current_timezone}
• Waktu Lokal: {current_time}

💡 **Manfaat Mengatur Zona Waktu:**
• Tampilan waktu yang akurat
• Laporan dengan timestamp lokal
• Notifikasi sesuai waktu setempat
• Statistik berdasarkan zona waktu

🔄 **Pilih Zona Waktu Baru:**
Zona waktu yang dipilih akan ditandai dengan ✅
                """
            else:
                message = f"""
⌚ **Timezone Settings**

🌍 **Current Timezone:**
• {current_timezone}
• Local Time: {current_time}

💡 **Benefits of Setting Timezone:**
• Accurate time display
• Reports with local timestamps
• Notifications according to local time
• Statistics based on timezone

🔄 **Select New Timezone:**
Selected timezone will be marked with ✅
                """
            
            await query.edit_message_text(
                message,
                reply_markup=get_timezone_keyboard(current_timezone),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing timezone selection: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan pilihan zona waktu")
            )
    
    async def _show_language_selection(self, query, user_data: Dict[str, Any], lang: str) -> None:
        """Show language selection"""
        try:
            current_lang = user_data.get('language_code', 'id')
            
            if lang == 'id':
                message = f"""
🌐 **Pengaturan Bahasa**

🗣️ **Bahasa Saat Ini:**
• {'🇮🇩 Bahasa Indonesia' if current_lang == 'id' else '🇬🇧 English'}

💡 **Tentang Pengaturan Bahasa:**
• Mengubah bahasa interface bot
• Semua menu dan pesan akan berubah
• Laporan dan hasil pencarian akan disesuaikan
• Pengaturan dapat diubah kapan saja

🔄 **Pilih Bahasa Baru:**
Bahasa yang dipilih akan ditandai dengan ✅
                """
            else:
                message = f"""
🌐 **Language Settings**

🗣️ **Current Language:**
• {'🇮🇩 Bahasa Indonesia' if current_lang == 'id' else '🇬🇧 English'}

💡 **About Language Settings:**
• Changes bot interface language
• All menus and messages will change
• Reports and search results will be adjusted
• Settings can be changed anytime

🔄 **Select New Language:**
Selected language will be marked with ✅
                """
            
            await query.edit_message_text(
                message,
                reply_markup=get_language_keyboard(current_lang),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing language selection: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan pilihan bahasa")
            )
    
    async def _set_timezone(self, query, user_id: int, timezone: str, lang: str) -> None:
        """Set user timezone"""
        try:
            # Validate timezone
            import pytz
            try:
                pytz.timezone(timezone)
            except pytz.UnknownTimeZoneError:
                await query.edit_message_text(
                    create_error_message("Zona waktu tidak valid")
                )
                return
            
            # Update user timezone
            success = self.db_manager.update_user(user_id, timezone=timezone)
            
            if success:
                new_time = get_local_time(timezone)
                
                if lang == 'id':
                    message = f"""
✅ **Zona Waktu Berhasil Diubah**

⌚ **Zona Waktu Baru:**
• {timezone}
• Waktu Lokal: {new_time}

🔄 **Perubahan Diterapkan:**
• Semua tampilan waktu akan menggunakan zona waktu baru
• Laporan akan menampilkan timestamp lokal
• Statistik akan disesuaikan dengan zona waktu

💡 **Pengaturan telah disimpan dan akan berlaku segera.**
                    """
                else:
                    message = f"""
✅ **Timezone Successfully Changed**

⌚ **New Timezone:**
• {timezone}
• Local Time: {new_time}

🔄 **Changes Applied:**
• All time displays will use the new timezone
• Reports will show local timestamps
• Statistics will be adjusted to timezone

💡 **Settings have been saved and will take effect immediately.**
                    """
                
                keyboard = [
                    [InlineKeyboardButton("⌚ Ubah Lagi" if lang == 'id' else "⌚ Change Again", 
                                        callback_data="settings_timezone")],
                    [InlineKeyboardButton("⚙️ Kembali ke Pengaturan" if lang == 'id' else "⚙️ Back to Settings", 
                                        callback_data="settings_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    create_error_message("Gagal mengubah zona waktu")
                )
                
        except Exception as e:
            self.logger.error(f"Error setting timezone: {e}")
            await query.edit_message_text(
                create_error_message("Gagal mengatur zona waktu")
            )
    
    async def _set_language(self, query, user_id: int, new_lang: str, user_data: Dict[str, Any]) -> None:
        """Set user language"""
        try:
            # Validate language
            if new_lang not in ['id', 'en']:
                await query.edit_message_text(
                    create_error_message("Bahasa tidak valid")
                )
                return
            
            # Update user language
            success = self.db_manager.update_user(user_id, language_code=new_lang)
            
            if success:
                if new_lang == 'id':
                    message = f"""
✅ **Bahasa Berhasil Diubah**

🌐 **Bahasa Baru:**
• 🇮🇩 Bahasa Indonesia

🔄 **Perubahan Diterapkan:**
• Semua menu akan dalam Bahasa Indonesia
• Pesan bot akan dalam Bahasa Indonesia
• Laporan dan hasil pencarian dalam Bahasa Indonesia
• FAQ dan panduan dalam Bahasa Indonesia

💡 **Pengaturan telah disimpan dan berlaku segera.**
                    """
                else:
                    message = f"""
✅ **Language Successfully Changed**

🌐 **New Language:**
• 🇬🇧 English

🔄 **Changes Applied:**
• All menus will be in English
• Bot messages will be in English
• Reports and search results in English
• FAQ and guides in English

💡 **Settings have been saved and take effect immediately.**
                    """
                
                keyboard = [
                    [InlineKeyboardButton("🌐 Ubah Lagi" if new_lang == 'id' else "🌐 Change Again", 
                                        callback_data="settings_language")],
                    [InlineKeyboardButton("⚙️ Kembali ke Pengaturan" if new_lang == 'id' else "⚙️ Back to Settings", 
                                        callback_data="settings_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    create_error_message("Gagal mengubah bahasa")
                )
                
        except Exception as e:
            self.logger.error(f"Error setting language: {e}")
            await query.edit_message_text(
                create_error_message("Gagal mengatur bahasa")
            )
    
    async def _reset_preferences(self, query, user_id: int, lang: str) -> None:
        """Show reset preferences confirmation"""
        try:
            if lang == 'id':
                message = """
🔄 **Reset Pengaturan**

⚠️ **Peringatan:**
Tindakan ini akan mengembalikan semua pengaturan ke nilai default:

📋 **Yang akan direset:**
• Bahasa: Bahasa Indonesia
• Zona Waktu: Asia/Jakarta
• Preferensi interface
• Cache pencarian

💡 **Yang TIDAK akan direset:**
• Token balance
• Riwayat pencarian
• Status berlangganan
• Data akun

❓ **Apakah Anda yakin ingin melanjutkan?**
                """
            else:
                message = """
🔄 **Reset Preferences**

⚠️ **Warning:**
This action will restore all settings to default values:

📋 **What will be reset:**
• Language: Indonesian
• Timezone: Asia/Jakarta
• Interface preferences
• Search cache

💡 **What will NOT be reset:**
• Token balance
• Search history
• Subscription status
• Account data

❓ **Are you sure you want to continue?**
                """
            
            keyboard = [
                [InlineKeyboardButton("✅ Ya, Reset" if lang == 'id' else "✅ Yes, Reset", 
                                    callback_data="confirm_reset")],
                [InlineKeyboardButton("❌ Batal" if lang == 'id' else "❌ Cancel", 
                                    callback_data="cancel_reset")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing reset confirmation: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan konfirmasi reset")
            )
    
    async def _confirm_reset_preferences(self, query, user_id: int, lang: str) -> None:
        """Confirm reset preferences"""
        try:
            # Reset user preferences to default
            success = self.db_manager.update_user(
                user_id,
                timezone='Asia/Jakarta',
                language_code='id'
            )
            
            if success:
                message = """
✅ **Pengaturan Berhasil Direset**

🔄 **Pengaturan Baru:**
• Bahasa: 🇮🇩 Bahasa Indonesia
• Zona Waktu: Asia/Jakarta
• Interface: Default

💡 **Semua pengaturan telah dikembalikan ke nilai default.**

⚙️ **Anda dapat mengubah pengaturan kapan saja melalui menu pengaturan.**
                """
                
                keyboard = [
                    [InlineKeyboardButton("⚙️ Buka Pengaturan", callback_data="settings_main")],
                    [InlineKeyboardButton("🏠 Menu Utama", callback_data="settings_back")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    create_error_message("Gagal mereset pengaturan")
                )
                
        except Exception as e:
            self.logger.error(f"Error confirming reset: {e}")
            await query.edit_message_text(
                create_error_message("Gagal melakukan reset")
            )
    
    async def _back_to_settings_menu(self, query, user_data: Dict[str, Any], lang: str) -> None:
        """Back to settings menu"""
        try:
            # Get fresh user data
            user_id = user_data.get('user_id')
            updated_user_data = self.db_manager.get_user(user_id)
            
            if not updated_user_data:
                await query.edit_message_text(
                    create_error_message("Gagal memuat data pengguna")
                )
                return
            
            lang = updated_user_data.get('language_code', 'id')
            timezone = updated_user_data.get('timezone', 'Asia/Jakarta')
            current_time = get_local_time(timezone)
            
            if lang == 'id':
                message = f"""
⚙️ **Pengaturan Akun**

👤 **Informasi Akun:**
• Nama: {updated_user_data.get('first_name', 'N/A')}
• Username: @{updated_user_data.get('username', 'N/A')}
• ID: {updated_user_data.get('user_id', 'N/A')}

🌐 **Preferensi:**
• Bahasa: {'🇮🇩 Indonesia' if lang == 'id' else '🇬🇧 English'}
• Zona Waktu: {timezone}
• Waktu Lokal: {current_time}

📊 **Statistik:**
• Total Pencarian: {updated_user_data.get('total_requests', 0)}
• Pencarian File: {updated_user_data.get('file_requests', 0)}
• Token Tersisa: {updated_user_data.get('token_balance', 0)} 🪙

⚙️ **Pengaturan yang Tersedia:**
• Ubah zona waktu
• Ganti bahasa interface
• Reset preferensi

Pilih pengaturan yang ingin diubah:
                """
            else:
                message = f"""
⚙️ **Account Settings**

👤 **Account Information:**
• Name: {updated_user_data.get('first_name', 'N/A')}
• Username: @{updated_user_data.get('username', 'N/A')}
• ID: {updated_user_data.get('user_id', 'N/A')}

🌐 **Preferences:**
• Language: {'🇮🇩 Indonesia' if lang == 'id' else '🇬🇧 English'}
• Timezone: {timezone}
• Local Time: {current_time}

📊 **Statistics:**
• Total Searches: {updated_user_data.get('total_requests', 0)}
• File Searches: {updated_user_data.get('file_requests', 0)}
• Remaining Tokens: {updated_user_data.get('token_balance', 0)} 🪙

⚙️ **Available Settings:**
• Change timezone
• Change interface language
• Reset preferences

Select the setting you want to change:
                """
            
            # Add reset option to keyboard
            keyboard = [
                [InlineKeyboardButton("⌚ Zona Waktu" if lang == 'id' else "⌚ Timezone", 
                                    callback_data="settings_timezone")],
                [InlineKeyboardButton("🌐 Bahasa" if lang == 'id' else "🌐 Language", 
                                    callback_data="settings_language")],
                [InlineKeyboardButton("🔄 Reset Pengaturan" if lang == 'id' else "🔄 Reset Settings", 
                                    callback_data="reset_preferences")],
                [InlineKeyboardButton("⬅️ Kembali ke Menu Utama" if lang == 'id' else "⬅️ Back to Main Menu", 
                                    callback_data="settings_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error going back to settings menu: {e}")
            await query.edit_message_text(
                create_error_message("Gagal kembali ke menu pengaturan")
            )
    
    async def _back_to_main_menu(self, query, lang: str) -> None:
        """Back to main menu"""
        try:
            if lang == 'id':
                message = """
🏠 **Menu Utama**

Selamat datang kembali di menu utama RexSint OSINT Bot!

🔎 **Fitur Pencarian Data** - Cari informasi di database kebocoran
ℹ️ **Informasi** - Lihat status akun dan statistik
🛒 **Toko** - Berlangganan dan aktivasi fitur
⚙️ **Pengaturan** - Atur preferensi personal
📖 **Menu** - Panduan dan informasi tambahan

Silakan gunakan menu reply keyboard di bawah untuk navigasi.
                """
            else:
                message = """
🏠 **Main Menu**

Welcome back to RexSint OSINT Bot main menu!

🔎 **Search Features** - Search information in breach databases
ℹ️ **Information** - View account status and statistics
🛒 **Shop** - Subscriptions and feature activation
⚙️ **Settings** - Configure personal preferences
📖 **Menu** - Guides and additional information

Please use the reply keyboard menu below for navigation.
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
    
    async def export_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Export user settings for backup"""
        try:
            user_data = self.db_manager.get_user(user_id)
            
            if not user_data:
                return {}
            
            # Export only settings, not sensitive data
            settings_export = {
                'timezone': user_data.get('timezone', 'Asia/Jakarta'),
                'language_code': user_data.get('language_code', 'id'),
                'export_timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            return settings_export
            
        except Exception as e:
            self.logger.error(f"Error exporting user settings: {e}")
            return {}
    
    async def import_user_settings(self, user_id: int, settings_data: Dict[str, Any]) -> bool:
        """Import user settings from backup"""
        try:
            if not settings_data:
                return False
            
            # Validate settings data
            timezone = settings_data.get('timezone', 'Asia/Jakarta')
            language_code = settings_data.get('language_code', 'id')
            
            # Validate timezone
            import pytz
            try:
                pytz.timezone(timezone)
            except pytz.UnknownTimeZoneError:
                timezone = 'Asia/Jakarta'
            
            # Validate language
            if language_code not in ['id', 'en']:
                language_code = 'id'
            
            # Update user settings
            success = self.db_manager.update_user(
                user_id,
                timezone=timezone,
                language_code=language_code
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error importing user settings: {e}")
            return False