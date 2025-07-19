"""
Shop Handler for RexSint Bot
Handles payment system and subscription management
"""

import logging
import os
from typing import Dict, Any
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from core.database import DatabaseManager
from core.utils import (
    get_shop_keyboard,
    format_currency,
    create_error_message,
    create_success_message,
    create_warning_message,
    format_datetime
)

class ShopHandler:
    """Handles shop operations and payments"""
    
    def __init__(self, db_manager: DatabaseManager, config: Dict[str, Any]):
        self.db_manager = db_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Payment packages
        self.packages = {
            'activate_trial': {
                'name_id': 'Aktifkan Fitur Pencarian',
                'name_en': 'Activate Search Features',
                'price_idr': 50000,
                'price_usd': 3.06,
                'tokens': 0,
                'duration_days': 0,
                'description_id': 'Aktivasi fitur pencarian untuk trial 7 hari',
                'description_en': 'Activate search features for 7-day trial'
            },
            'week': {
                'name_id': 'Berlangganan 1 Minggu',
                'name_en': '1 Week Subscription',
                'price_idr': 65240,
                'price_usd': 4.00,
                'tokens': 10,
                'duration_days': 7,
                'description_id': 'Perpanjang akses premium selama 1 minggu + 10 token',
                'description_en': 'Extend premium access for 1 week + 10 tokens'
            },
            'month': {
                'name_id': 'Berlangganan 1 Bulan',
                'name_en': '1 Month Subscription',
                'price_idr': 163100,
                'price_usd': 10.00,
                'tokens': 10,
                'duration_days': 30,
                'description_id': 'Perpanjang akses premium selama 1 bulan + 10 token',
                'description_en': 'Extend premium access for 1 month + 10 tokens'
            },
            'year': {
                'name_id': 'Berlangganan 1 Tahun',
                'name_en': '1 Year Subscription',
                'price_idr': 815000,
                'price_usd': 50.00,
                'tokens': 10,
                'duration_days': 365,
                'description_id': 'Perpanjang akses premium selama 1 tahun + 10 token',
                'description_en': 'Extend premium access for 1 year + 10 tokens'
            },
            'lifetime': {
                'name_id': 'Berlangganan Selamanya',
                'name_en': 'Lifetime Subscription',
                'price_idr': 3262000,
                'price_usd': 200.00,
                'tokens': 10,
                'duration_days': 36500,  # 100 years
                'description_id': 'Akses premium selamanya + 10 token',
                'description_en': 'Lifetime premium access + 10 tokens'
            }
        }
    
    async def shop_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show shop menu"""
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
            
           # Get subscription status
            subscription_end = user_data.get('subscription_end_date')
            is_trial_activated = user_data.get('is_trial_activated', False)
            token_balance = user_data.get('token_balance', 0)
            
            # Check if subscription is active
            subscription_active = False
            if subscription_end:
                try:
                    if isinstance(subscription_end, str):
                        end_date = datetime.fromisoformat(subscription_end.replace('Z', '+00:00'))
                    else:
                        end_date = subscription_end
                    subscription_active = datetime.now() < end_date
                except Exception:
                    subscription_active = False
            
            if lang == 'id':
                status_text = "🔴 Belum Aktif"
                if is_trial_activated:
                    if subscription_active:
                        status_text = "🟢 Aktif"
                    else:
                        status_text = "🟡 Expired"
                
                message = f"""
🛒 **Toko RexSint**

💎 **Status Akun Anda:**
• Status: {status_text}
• Token: {token_balance} 🪙
• Berakhir: {format_datetime(subscription_end, user_data.get('timezone', 'Asia/Jakarta'))}

💰 **Paket Berlangganan:**

🔓 **Aktivasi Trial - Rp 50.000**
• Mengaktifkan fitur pencarian
• Akses ke semua database
• Trial 7 hari gratis

🍺 **1 Minggu - $4 (Rp 65.240)**
• Perpanjang 1 minggu
• +10 token pencarian
• Semua fitur premium

🌙 **1 Bulan - $10 (Rp 163.100)**
• Perpanjang 1 bulan  
• +10 token pencarian
• Semua fitur premium

🎄 **1 Tahun - $50 (Rp 815.000)**
• Perpanjang 1 tahun
• +10 token pencarian
• Semua fitur premium

🔥 **Selamanya - $200 (Rp 3.262.000)**
• Akses selamanya
• +10 token pencarian
• Semua fitur premium

📱 **Metode Pembayaran:**
• QRIS (Otomatis)
• Transfer Bank
• E-Wallet
• Cryptocurrency

Pilih paket yang sesuai dengan kebutuhan Anda!
                """
            else:
                status_text = "🔴 Not Active"
                if is_trial_activated:
                    if subscription_active:
                        status_text = "🟢 Active"
                    else:
                        status_text = "🟡 Expired"
                
                message = f"""
🛒 **RexSint Shop**

💎 **Your Account Status:**
• Status: {status_text}
• Tokens: {token_balance} 🪙
• Expires: {format_datetime(subscription_end, user_data.get('timezone', 'Asia/Jakarta'))}

💰 **Subscription Packages:**

🔓 **Trial Activation - Rp 50,000**
• Activate search features
• Access to all databases
• 7-day free trial

🍺 **1 Week - $4 (Rp 65,240)**
• Extend 1 week
• +10 search tokens
• All premium features

🌙 **1 Month - $10 (Rp 163,100)**
• Extend 1 month
• +10 search tokens
• All premium features

🎄 **1 Year - $50 (Rp 815,000)**
• Extend 1 year
• +10 search tokens
• All premium features

🔥 **Lifetime - $200 (Rp 3,262,000)**
• Lifetime access
• +10 search tokens
• All premium features

📱 **Payment Methods:**
• QRIS (Automatic)
• Bank Transfer
• E-Wallet
• Cryptocurrency

Choose the package that suits your needs!
                """
            
            await update.message.reply_text(
                message,
                reply_markup=get_shop_keyboard(lang),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing shop menu: {e}")
            await update.message.reply_text(
                create_error_message("Gagal menampilkan menu toko"),
                parse_mode='Markdown'
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle shop callback queries"""
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
            
            if data.startswith("shop_"):
                package_id = data.replace("shop_", "")
                
                if package_id == "qris":
                    await self._show_qris_payment(query, lang)
                elif package_id == "other_payment":
                    await self._show_other_payment(query, lang)
                elif package_id == "back":
                    await self._back_to_main_menu(query, lang)
                elif package_id in self.packages:
                    await self._show_package_details(query, package_id, lang)
                else:
                    await query.edit_message_text(
                        create_error_message("Paket tidak ditemukan")
                    )
            elif data.startswith("buy_"):
                package_id = data.replace("buy_", "")
                await self._process_purchase(query, package_id, lang, context)
            elif data.startswith("payment_"):
                await self._handle_payment_callback(query, data, lang, context)
            
        except Exception as e:
            self.logger.error(f"Error handling shop callback: {e}")
            await query.edit_message_text(
                create_error_message("Terjadi kesalahan dalam memproses pembelian")
            )
    
    async def _show_package_details(self, query, package_id: str, lang: str) -> None:
        """Show package details"""
        try:
            if package_id not in self.packages:
                await query.edit_message_text(
                    create_error_message("Paket tidak ditemukan")
                )
                return
            
            package = self.packages[package_id]
            
            if lang == 'id':
                message = f"""
📦 **Detail Paket**

🎯 **{package['name_id']}**

💰 **Harga:**
• IDR: {format_currency(package['price_idr'], 'IDR')}
• USD: {format_currency(package['price_usd'], 'USD')}

🎁 **Yang Anda Dapatkan:**
• {package['description_id']}
• Bonus: {package['tokens']} token pencarian
• Durasi: {package['duration_days']} hari
• Akses premium features
• AI Summary
• Laporan HTML lengkap

💳 **Metode Pembayaran:**
• QRIS (Rekomendasi)
• Transfer Bank
• E-Wallet (OVO, DANA, GoPay)
• Cryptocurrency

⚡ **Proses Aktivasi:**
1. Pilih metode pembayaran
2. Lakukan pembayaran
3. Kirim bukti pembayaran
4. Tim kami akan verifikasi (1-24 jam)
5. Akun Anda akan diaktivasi otomatis

Lanjutkan dengan pembelian?
                """
            else:
                message = f"""
📦 **Package Details**

🎯 **{package['name_en']}**

💰 **Price:**
• IDR: {format_currency(package['price_idr'], 'IDR')}
• USD: {format_currency(package['price_usd'], 'USD')}

🎁 **What You Get:**
• {package['description_en']}
• Bonus: {package['tokens']} search tokens
• Duration: {package['duration_days']} days
• Premium features access
• AI Summary
• Complete HTML reports

💳 **Payment Methods:**
• QRIS (Recommended)
• Bank Transfer
• E-Wallet (OVO, DANA, GoPay)
• Cryptocurrency

⚡ **Activation Process:**
1. Choose payment method
2. Make payment
3. Send payment proof
4. Our team will verify (1-24 hours)
5. Your account will be activated automatically

Proceed with purchase?
                """
            
            keyboard = [
                [InlineKeyboardButton("💳 Beli Sekarang" if lang == 'id' else "💳 Buy Now", 
                                    callback_data=f"buy_{package_id}")],
                [InlineKeyboardButton("⬅️ Kembali ke Toko" if lang == 'id' else "⬅️ Back to Shop", 
                                    callback_data="shop_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing package details: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan detail paket")
            )
    
    async def _process_purchase(self, query, package_id: str, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process purchase"""
        try:
            if package_id not in self.packages:
                await query.edit_message_text(
                    create_error_message("Paket tidak ditemukan")
                )
                return
            
            package = self.packages[package_id]
            user_id = query.from_user.id
            
            # Generate order ID
            order_id = f"RX{user_id}{int(datetime.now().timestamp())}"
            
            # Store purchase context
            context.user_data['pending_purchase'] = {
                'order_id': order_id,
                'package_id': package_id,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
            
            if lang == 'id':
                message = f"""
🛒 **Konfirmasi Pembelian**

📦 **Paket:** {package['name_id']}
💰 **Total:** {format_currency(package['price_idr'], 'IDR')} / {format_currency(package['price_usd'], 'USD')}
🆔 **Order ID:** `{order_id}`

📋 **Ringkasan:**
• Durasi: {package['duration_days']} hari
• Bonus Token: {package['tokens']} 🪙
• Fitur Premium: ✅
• AI Summary: ✅
• Laporan HTML: ✅

💳 **Pilih Metode Pembayaran:**
                """
            else:
                message = f"""
🛒 **Purchase Confirmation**

📦 **Package:** {package['name_en']}
💰 **Total:** {format_currency(package['price_idr'], 'IDR')} / {format_currency(package['price_usd'], 'USD')}
🆔 **Order ID:** `{order_id}`

📋 **Summary:**
• Duration: {package['duration_days']} days
• Bonus Tokens: {package['tokens']} 🪙
• Premium Features: ✅
• AI Summary: ✅
• HTML Reports: ✅

💳 **Choose Payment Method:**
                """
            
            keyboard = [
                [InlineKeyboardButton("📱 QRIS", callback_data=f"payment_qris_{package_id}")],
                [InlineKeyboardButton("🏦 Transfer Bank", callback_data=f"payment_bank_{package_id}")],
                [InlineKeyboardButton("💳 E-Wallet", callback_data=f"payment_ewallet_{package_id}")],
                [InlineKeyboardButton("₿ Cryptocurrency", callback_data=f"payment_crypto_{package_id}")],
                [InlineKeyboardButton("⬅️ Kembali" if lang == 'id' else "⬅️ Back", 
                                    callback_data="shop_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error processing purchase: {e}")
            await query.edit_message_text(
                create_error_message("Gagal memproses pembelian")
            )
    
    async def _handle_payment_callback(self, query, data: str, lang: str, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle payment method callbacks"""
        try:
            parts = data.split('_')
            if len(parts) < 3:
                await query.edit_message_text(
                    create_error_message("Format callback tidak valid")
                )
                return
            
            payment_method = parts[1]
            package_id = parts[2]
            
            if payment_method == "qris":
                await self._show_qris_payment(query, lang, package_id)
            elif payment_method == "bank":
                await self._show_bank_payment(query, lang, package_id)
            elif payment_method == "ewallet":
                await self._show_ewallet_payment(query, lang, package_id)
            elif payment_method == "crypto":
                await self._show_crypto_payment(query, lang, package_id)
            
        except Exception as e:
            self.logger.error(f"Error handling payment callback: {e}")
            await query.edit_message_text(
                create_error_message("Gagal memproses metode pembayaran")
            )
    
    async def _show_qris_payment(self, query, lang: str, package_id: str = None) -> None:
        """Show QRIS payment"""
        try:
            qris_file = "assets/qris.png"
            
            if not os.path.exists(qris_file):
                if lang == 'id':
                    message = "❌ File QRIS tidak ditemukan. Silakan hubungi admin."
                else:
                    message = "❌ QRIS file not found. Please contact admin."
                
                await query.edit_message_text(message)
                return
            
            # Get package details if provided
            package_info = ""
            if package_id and package_id in self.packages:
                package = self.packages[package_id]
                if lang == 'id':
                    package_info = f"""
📦 **Paket:** {package['name_id']}
💰 **Total:** {format_currency(package['price_idr'], 'IDR')}
                    """
                else:
                    package_info = f"""
📦 **Package:** {package['name_en']}
💰 **Total:** {format_currency(package['price_idr'], 'IDR')}
                    """
            
            if lang == 'id':
                message = f"""
📱 **Pembayaran QRIS**

{package_info}

📋 **Cara Pembayaran:**
1. Scan QR Code di bawah
2. Bayar sesuai nominal yang tertera
3. Simpan bukti pembayaran
4. Kirim screenshot bukti ke chat ini
5. Tunggu verifikasi (1-24 jam)

⚠️ **Penting:**
• Pastikan nominal pembayaran sesuai
• Jangan lupa kirim bukti pembayaran
• Verifikasi dilakukan otomatis oleh sistem

📞 **Bantuan:**
Jika ada masalah, hubungi admin melalui tombol di bawah.
                """
            else:
                message = f"""
📱 **QRIS Payment**

{package_info}

📋 **Payment Steps:**
1. Scan QR Code below
2. Pay according to the specified amount
3. Save payment proof
4. Send screenshot proof to this chat
5. Wait for verification (1-24 hours)

⚠️ **Important:**
• Make sure payment amount is correct
• Don't forget to send payment proof
• Verification is done automatically by system

📞 **Support:**
If you have any problems, contact admin via button below.
                """
            
            # Send QRIS image
            with open(qris_file, 'rb') as f:
                await query.message.reply_photo(
                    photo=InputFile(f),
                    caption=message,
                    parse_mode='Markdown'
                )
            
            # Edit original message to show instructions
            keyboard = [
                [InlineKeyboardButton("✅ Sudah Bayar" if lang == 'id' else "✅ Already Paid", 
                                    callback_data="payment_confirm")],
                [InlineKeyboardButton("💬 Hubungi Admin" if lang == 'id' else "💬 Contact Admin", 
                                    callback_data="contact_admin")],
                [InlineKeyboardButton("⬅️ Kembali" if lang == 'id' else "⬅️ Back", 
                                    callback_data="shop_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📱 QRIS telah dikirim. Silakan ikuti instruksi di atas." if lang == 'id' 
                else "📱 QRIS has been sent. Please follow the instructions above.",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error showing QRIS payment: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan pembayaran QRIS")
            )
    
    async def _show_bank_payment(self, query, lang: str, package_id: str) -> None:
        """Show bank transfer payment"""
        try:
            if package_id not in self.packages:
                await query.edit_message_text(
                    create_error_message("Paket tidak ditemukan")
                )
                return
            
            package = self.packages[package_id]
            
            if lang == 'id':
                message = f"""
🏦 **Transfer Bank**

📦 **Paket:** {package['name_id']}
💰 **Total:** {format_currency(package['price_idr'], 'IDR')}

🏦 **Rekening Tujuan:**

**BCA**
• Nomor: 1234567890
• Nama: REXSINT INDONESIA
• Kode: 014

**Mandiri**
• Nomor: 1234567890
• Nama: REXSINT INDONESIA
• Kode: 008

**BRI**
• Nomor: 1234567890
• Nama: REXSINT INDONESIA
• Kode: 002

📋 **Cara Transfer:**
1. Transfer ke salah satu rekening di atas
2. Gunakan nominal yang tepat
3. Simpan bukti transfer
4. Kirim foto bukti ke chat ini
5. Tunggu verifikasi (1-24 jam)

⚠️ **Penting:**
• Transfer harus dari rekening atas nama sendiri
• Sertakan keterangan: Order ID
• Bukti transfer wajib dikirim
                """
            else:
                message = f"""
🏦 **Bank Transfer**

📦 **Package:** {package['name_en']}
💰 **Total:** {format_currency(package['price_idr'], 'IDR')}

🏦 **Destination Account:**

**BCA**
• Number: 1234567890
• Name: REXSINT INDONESIA
• Code: 014

**Mandiri**
• Number: 1234567890
• Name: REXSINT INDONESIA
• Code: 008

**BRI**
• Number: 1234567890
• Name: REXSINT INDONESIA
• Code: 002

📋 **Transfer Steps:**
1. Transfer to one of the accounts above
2. Use the exact amount
3. Save transfer proof
4. Send photo proof to this chat
5. Wait for verification (1-24 hours)

⚠️ **Important:**
• Transfer must be from account under your name
• Include note: Order ID
• Transfer proof must be sent
                """
            
            keyboard = [
                [InlineKeyboardButton("✅ Sudah Transfer" if lang == 'id' else "✅ Already Transferred", 
                                    callback_data="payment_confirm")],
                [InlineKeyboardButton("💬 Hubungi Admin" if lang == 'id' else "💬 Contact Admin", 
                                    callback_data="contact_admin")],
                [InlineKeyboardButton("⬅️ Kembali" if lang == 'id' else "⬅️ Back", 
                                    callback_data="shop_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing bank payment: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan pembayaran bank")
            )
    
    async def _show_other_payment(self, query, lang: str) -> None:
        """Show other payment methods"""
        try:
            if lang == 'id':
                message = """
💳 **Metode Pembayaran Lainnya**

🔄 **Dalam Pengembangan:**
• PayPal
• Stripe
• Perfect Money
• Payoneer

💬 **Hubungi Admin:**
Untuk pembayaran dengan metode lain, silakan hubungi admin langsung.

📞 **Kontak:**
• Telegram: @admin_rexsint
• Email: admin@rexsint.com

⚡ **Proses Khusus:**
• Diskusi metode pembayaran
• Konfirmasi harga dan paket
• Proses manual oleh admin
• Aktivasi dalam 1-24 jam
                """
            else:
                message = """
💳 **Other Payment Methods**

🔄 **In Development:**
• PayPal
• Stripe
• Perfect Money
• Payoneer

💬 **Contact Admin:**
For payments with other methods, please contact admin directly.

📞 **Contact:**
• Telegram: @admin_rexsint
• Email: admin@rexsint.com

⚡ **Special Process:**
• Discuss payment method
• Confirm price and package
• Manual process by admin
• Activation within 1-24 hours
                """
            
            keyboard = [
                [InlineKeyboardButton("💬 Hubungi Admin" if lang == 'id' else "💬 Contact Admin", 
                                    callback_data="contact_admin")],
                [InlineKeyboardButton("⬅️ Kembali ke Toko" if lang == 'id' else "⬅️ Back to Shop", 
                                    callback_data="shop_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing other payment: {e}")
            await query.edit_message_text(
                create_error_message("Gagal menampilkan metode pembayaran lain")
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