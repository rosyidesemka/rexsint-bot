"""
Authentication Manager for RexSint Bot
Handles channel verification and user permissions
"""

import logging
from typing import Dict, Any, Optional
from telegram import Bot, ChatMember, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

class AuthManager:
    """Manages authentication and authorization for RexSint Bot"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.required_channel = config.get('Channel', {}).get('channel_id')
        self.admin_chat_id = config.get('Admin', {}).get('admin_chat_id')
        
        if not self.required_channel:
            self.logger.warning("No required channel configured")
        
        if not self.admin_chat_id:
            self.logger.warning("No admin chat ID configured")
    
    async def check_channel_membership(self, bot: Bot, user_id: int) -> bool:
        """Check if user is member of required channel"""
        if not self.required_channel:
            return True  # No channel requirement
        
        try:
            # Get user's membership status
            member = await bot.get_chat_member(self.required_channel, user_id)
            
            # Check if user is member, administrator, or creator
            if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                return True
            else:
                self.logger.info(f"User {user_id} is not a member of required channel")
                return False
                
        except TelegramError as e:
            self.logger.error(f"Error checking channel membership for user {user_id}: {e}")
            # If we can't check (e.g., channel is private), assume user is not a member
            return False
    
    async def get_channel_invite_link(self, bot: Bot) -> Optional[str]:
        """Get invite link for the required channel"""
        if not self.required_channel:
            return None
        
        try:
            # If channel starts with @, it's a public channel
            if self.required_channel.startswith('@'):
                return f"https://t.me/{self.required_channel[1:]}"
            
            # For private channels, try to get invite link
            try:
                invite_link = await bot.export_chat_invite_link(self.required_channel)
                return invite_link
            except TelegramError:
                # If we can't get invite link, return None
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting channel invite link: {e}")
            return None
    
    async def send_channel_verification_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Send channel verification message to user"""
        try:
            invite_link = await self.get_channel_invite_link(context.bot)
            
            if invite_link:
                keyboard = [
                    [InlineKeyboardButton("🔗 Bergabung dengan Channel", url=invite_link)],
                    [InlineKeyboardButton("✅ Saya Sudah Bergabung", callback_data="verify_membership")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                message = (
                    "🔐 **Verifikasi Keanggotaan Channel**\n\n"
                    "Untuk menggunakan bot ini, Anda harus bergabung dengan channel resmi kami terlebih dahulu.\n\n"
                    "📢 **Manfaat bergabung:**\n"
                    "• Update informasi keamanan terbaru\n"
                    "• Tips OSINT dan cyber security\n"
                    "• Notifikasi fitur baru\n"
                    "• Akses prioritas ke layanan premium\n\n"
                    "👆 Klik tombol di bawah untuk bergabung, lalu klik **'Saya Sudah Bergabung'**"
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("🔄 Coba Lagi", callback_data="verify_membership")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                message = (
                    "🔐 **Verifikasi Keanggotaan Channel**\n\n"
                    "Untuk menggunakan bot ini, Anda harus bergabung dengan channel resmi kami:\n\n"
                    f"📢 **Channel:** {self.required_channel}\n\n"
                    "Setelah bergabung, klik tombol **'Coba Lagi'** di bawah."
                )
            
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending channel verification message: {e}")
            return False
    
    async def verify_membership_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle membership verification callback"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Check membership
        is_member = await self.check_channel_membership(context.bot, user_id)
        
        if is_member:
            await query.edit_message_text(
                "✅ **Verifikasi Berhasil!**\n\n"
                "Selamat! Anda telah berhasil bergabung dengan channel.\n"
                "Sekarang Anda dapat menggunakan semua fitur bot.\n\n"
                "Gunakan /start untuk memulai."
            )
            return True
        else:
            await query.edit_message_text(
                "❌ **Verifikasi Gagal**\n\n"
                "Anda belum bergabung dengan channel yang diperlukan.\n"
                "Silakan bergabung terlebih dahulu, lalu coba lagi.\n\n"
                "Gunakan /start untuk mencoba lagi."
            )
            return False
    
    async def check_trial_activation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if user can access search features"""
        if not user_data:
            return {
                "can_search": False,
                "message": "❌ Data pengguna tidak ditemukan. Silakan /start ulang."
            }
        
        if user_data.get('is_blocked', False):
            return {
                "can_search": False,
                "message": "🚫 Akun Anda telah diblokir. Hubungi admin untuk informasi lebih lanjut."
            }
        
        if not user_data.get('is_trial_activated', False):
            return {
                "can_search": False,
                "message": (
                    "⚠️ **Fitur Pencarian Belum Aktif**\n\n"
                    "Untuk dapat melakukan pencarian, silakan lakukan pembayaran aktivasi "
                    "sebesar **50.000 Rp** melalui menu **🛒 Toko**.\n\n"
                    "💎 **Yang Anda dapatkan:**\n"
                    "• Akses pencarian semua database\n"
                    "• 10 token pencarian gratis\n"
                    "• Fitur AI summary\n"
                    "• Laporan lengkap (HTML)\n"
                    "• Trial 7 hari premium"
                )
            }
        
        # Check subscription status
        from datetime import datetime
        subscription_end = user_data.get('subscription_end_date')
        if subscription_end:
            try:
                if isinstance(subscription_end, str):
                    subscription_end = datetime.fromisoformat(subscription_end.replace('Z', '+00:00'))
                
                if datetime.now() > subscription_end:
                    return {
                        "can_search": False,
                        "message": (
                            "⏰ **Masa Trial Berakhir**\n\n"
                            "Trial 7 hari Anda telah berakhir. Untuk melanjutkan pencarian, "
                            "silakan perpanjang langganan melalui menu **🛒 Toko**.\n\n"
                            "💰 **Paket Berlangganan:**\n"
                            "• 1 Minggu: $4 (65.240 Rp)\n"
                            "• 1 Bulan: $10 (163.100 Rp)\n"
                            "• 1 Tahun: $50 (815.000 Rp)\n"
                            "• Selamanya: $200 (3.262.000 Rp)"
                        )
                    }
            except Exception as e:
                self.logger.error(f"Error parsing subscription date: {e}")
        
        # Check token balance
        token_balance = user_data.get('token_balance', 0)
        if token_balance <= 0:
            return {
                "can_search": False,
                "message": (
                    "🪙 **Token Habis**\n\n"
                    "Token pencarian Anda telah habis. Untuk mendapatkan token tambahan, "
                    "silakan perpanjang langganan melalui menu **🛒 Toko**.\n\n"
                    "💡 **Info:** Setiap pembelian paket berlangganan mendapat bonus +10 token."
                )
            }
        
        return {
            "can_search": True,
            "message": "✅ Akses pencarian aktif",
            "remaining_tokens": token_balance
        }
    
    async def check_premium_feature(self, user_data: Dict[str, Any], feature: str) -> bool:
        """Check if user can access premium features"""
        if not user_data or not user_data.get('is_trial_activated', False):
            return False
        
        # Premium features that require active subscription
        premium_features = ['ip_search', 'bulk_search', 'advanced_search', 'unlimited_queries']
        
        if feature not in premium_features:
            return True  # Non-premium feature
        
        # Check subscription status
        from datetime import datetime
        subscription_end = user_data.get('subscription_end_date')
        if subscription_end:
            try:
                if isinstance(subscription_end, str):
                    subscription_end = datetime.fromisoformat(subscription_end.replace('Z', '+00:00'))
                
                return datetime.now() <= subscription_end
            except Exception:
                return False
        
        return False
    
    async def notify_admin(self, context: ContextTypes.DEFAULT_TYPE, message: str) -> bool:
        """Send notification to admin"""
        if not self.admin_chat_id:
            return False
        
        try:
            await context.bot.send_message(
                chat_id=self.admin_chat_id,
                text=f"🤖 **Bot Notification**\n\n{message}",
                parse_mode='Markdown'
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending admin notification: {e}")
            return False
    
    async def log_user_activity(self, user_id: int, activity: str, details: str = "") -> None:
        """Log user activity for admin monitoring"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = {
                "timestamp": timestamp,
                "user_id": user_id,
                "activity": activity,
                "details": details
            }
            
            # Log to file or database
            self.logger.info(f"User Activity - {user_id}: {activity} - {details}")
            
            # Optionally store in database for admin panel
            # This would require database manager integration
            
        except Exception as e:
            self.logger.error(f"Error logging user activity: {e}")
    
    def is_admin_command(self, text: str) -> bool:
        """Check if message is an admin command"""
        admin_commands = [
            '/admin', '/activatetrial', '/generate', '/setnewapi',
            '/broadcast', '/stats', '/block', '/unblock'
        ]
        
        if not text:
            return False
        
        for command in admin_commands:
            if text.startswith(command):
                return True
        
        return False
    
    async def check_rate_limit(self, user_id: int, action: str) -> bool:
        """Check if user is within rate limits"""
        # Simple rate limiting - can be enhanced with Redis
        try:
            # For now, just return True
            # In production, implement proper rate limiting
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {e}")
            return True
    
    def get_user_permissions(self, user_data: Dict[str, Any]) -> Dict[str, bool]:
        """Get user permissions based on subscription status"""
        if not user_data:
            return {
                "can_search": False,
                "can_bulk_search": False,
                "can_ip_search": False,
                "can_download_reports": False,
                "can_use_ai_summary": False
            }
        
        is_activated = user_data.get('is_trial_activated', False)
        has_valid_subscription = self.check_premium_feature(user_data, 'premium')
        
        return {
            "can_search": is_activated,
            "can_bulk_search": has_valid_subscription,
            "can_ip_search": has_valid_subscription,
            "can_download_reports": is_activated,
            "can_use_ai_summary": is_activated
        }