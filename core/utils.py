"""
Utility functions for RexSint Bot
Common helper functions and configurations
"""

import logging
import configparser
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytz
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def load_config(config_file: str = "config.ini") -> Dict[str, Any]:
    """Load configuration from INI file"""
    config = configparser.ConfigParser()
    
    try:
        config.read(config_file)
        
        # Convert to dictionary for easier access
        config_dict = {}
        for section in config.sections():
            config_dict[section] = dict(config.items(section))
        
        return config_dict
        
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return {}

def setup_logging(log_level: str = "INFO", log_file: str = "rexsint_bot.log"):
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Setup logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(f"logs/{log_file}", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_main_keyboard(lang: str = "id") -> ReplyKeyboardMarkup:
    """Get main reply keyboard"""
    if lang == "id":
        keyboard = [
            [KeyboardButton("🔎 Fitur Pencarian Data")],
            [KeyboardButton("ℹ️ Informasi"), KeyboardButton("🛒 Toko")],
            [KeyboardButton("⚙️ Pengaturan"), KeyboardButton("📖 Menu")]
        ]
    else:  # English
        keyboard = [
            [KeyboardButton("🔎 Search Features")],
            [KeyboardButton("ℹ️ Information"), KeyboardButton("🛒 Shop")],
            [KeyboardButton("⚙️ Settings"), KeyboardButton("📖 Menu")]
        ]
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_search_keyboard(lang: str = "id") -> ReplyKeyboardMarkup:
    """Get search options keyboard"""
    if lang == "id":
        keyboard = [
            [KeyboardButton("📧 Cari melalui Email")],
            [KeyboardButton("👤 Cari dengan Nama"), KeyboardButton("🔑 Pencarian Kata Sandi")],
            [KeyboardButton("🚗 Cari Kendaraan"), KeyboardButton("✈️ Cari Akun Telegram")],
            [KeyboardButton("📘 Cari Akun Facebook"), KeyboardButton("📸 Cari Akun Instagram")],
            [KeyboardButton("📍 Cari dengan IP"), KeyboardButton("📃 Pencarian Massal")],
            [KeyboardButton("🧩 Pencarian Gabungan")],
            [KeyboardButton("🏠 Kembali ke Menu Utama")]
        ]
    else:  # English
        keyboard = [
            [KeyboardButton("📧 Search by Email")],
            [KeyboardButton("👤 Search by Name"), KeyboardButton("🔑 Password Search")],
            [KeyboardButton("🚗 Vehicle Search"), KeyboardButton("✈️ Telegram Account Search")],
            [KeyboardButton("📘 Facebook Account Search"), KeyboardButton("📸 Instagram Account Search")],
            [KeyboardButton("📍 IP Search"), KeyboardButton("📃 Bulk Search")],
            [KeyboardButton("🧩 Combined Search")],
            [KeyboardButton("🏠 Back to Main Menu")]
        ]
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_settings_inline_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    """Get settings inline keyboard"""
    if lang == "id":
        keyboard = [
            [InlineKeyboardButton("⌚ Zona Waktu", callback_data="settings_timezone")],
            [InlineKeyboardButton("🌐 Bahasa", callback_data="settings_language")],
            [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="settings_back")]
        ]
    else:  # English
        keyboard = [
            [InlineKeyboardButton("⌚ Timezone", callback_data="settings_timezone")],
            [InlineKeyboardButton("🌐 Language", callback_data="settings_language")],
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="settings_back")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def get_timezone_keyboard(current_timezone: str = "Asia/Jakarta") -> InlineKeyboardMarkup:
    """Get timezone selection keyboard"""
    timezones = [
        ("🇮🇩 Jakarta", "Asia/Jakarta"),
        ("🇮🇩 Makassar", "Asia/Makassar"),
        ("🇮🇩 Jayapura", "Asia/Jayapura"),
        ("🇸🇬 Singapore", "Asia/Singapore"),
        ("🇺🇸 New York", "America/New_York"),
        ("🇬🇧 London", "Europe/London"),
        ("🇯🇵 Tokyo", "Asia/Tokyo"),
        ("🇦🇺 Sydney", "Australia/Sydney")
    ]
    
    keyboard = []
    for name, tz in timezones:
        if tz == current_timezone:
            name += " ✅"
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_timezone_{tz}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data="settings_main")])
    
    return InlineKeyboardMarkup(keyboard)

def get_language_keyboard(current_lang: str = "id") -> InlineKeyboardMarkup:
    """Get language selection keyboard"""
    languages = [
        ("🇮🇩 Bahasa Indonesia", "id"),
        ("🇬🇧 English", "en")
    ]
    
    keyboard = []
    for name, lang in languages:
        if lang == current_lang:
            name += " ✅"
        keyboard.append([InlineKeyboardButton(name, callback_data=f"set_language_{lang}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data="settings_main")])
    
    return InlineKeyboardMarkup(keyboard)

def get_info_menu_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    """Get info menu keyboard"""
    if lang == "id":
        keyboard = [
            [InlineKeyboardButton("📊 Daftar Total Kebocoran", callback_data="info_database_list")],
            [InlineKeyboardButton("❓ Pertanyaan (FAQ)", callback_data="info_faq")],
            [InlineKeyboardButton("↩️ Kembali ke Menu Utama", callback_data="info_back")]
        ]
    else:  # English
        keyboard = [
            [InlineKeyboardButton("📊 Total Breach List", callback_data="info_database_list")],
            [InlineKeyboardButton("❓ FAQ", callback_data="info_faq")],
            [InlineKeyboardButton("↩️ Back to Main Menu", callback_data="info_back")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def format_user_info(user_data: Dict[str, Any], lang: str = "id") -> str:
    """Format user information for display"""
    if lang == "id":
        info = f"""
🆔 **ID:** {user_data.get('user_id', 'N/A')}
👤 **Nama:** {user_data.get('first_name', 'N/A')}
👤 **Username:** @{user_data.get('username', 'N/A')}
💎 **Status:** {'Trial Aktif' if user_data.get('is_trial_activated') else 'Belum Aktif'}
⌛ **Berakhir:** {format_datetime(user_data.get('subscription_end_date'), user_data.get('timezone', 'Asia/Jakarta'))}
🪙 **Token:** {user_data.get('token_balance', 0)}
📊 **Total Permintaan:** {user_data.get('total_requests', 0)}
📝 **Permintaan File:** {user_data.get('file_requests', 0)}
⌚ **Zona Waktu:** {user_data.get('timezone', 'Asia/Jakarta')}
📅 **Terdaftar:** {format_datetime(user_data.get('registration_date'), user_data.get('timezone', 'Asia/Jakarta'))}
        """
    else:  # English
        info = f"""
🆔 **ID:** {user_data.get('user_id', 'N/A')}
👤 **Name:** {user_data.get('first_name', 'N/A')}
👤 **Username:** @{user_data.get('username', 'N/A')}
💎 **Status:** {'Trial Active' if user_data.get('is_trial_activated') else 'Not Active'}
⌛ **Expires:** {format_datetime(user_data.get('subscription_end_date'), user_data.get('timezone', 'Asia/Jakarta'))}
🪙 **Tokens:** {user_data.get('token_balance', 0)}
📊 **Total Requests:** {user_data.get('total_requests', 0)}
📝 **File Requests:** {user_data.get('file_requests', 0)}
⌚ **Timezone:** {user_data.get('timezone', 'Asia/Jakarta')}
📅 **Registered:** {format_datetime(user_data.get('registration_date'), user_data.get('timezone', 'Asia/Jakarta'))}
        """
    
    return info.strip()

def format_datetime(dt_str: str, timezone: str = "Asia/Jakarta") -> str:
    """Format datetime string with timezone"""
    if not dt_str:
        return "N/A"
    
    try:
        # Parse datetime
        if isinstance(dt_str, str):
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        else:
            dt = dt_str
        
        # Convert to target timezone
        target_tz = pytz.timezone(timezone)
        dt_local = dt.astimezone(target_tz)
        
        return dt_local.strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception:
        return str(dt_str)

def parse_file_content(content: bytes, filename: str) -> List[str]:
    """Parse file content and extract search queries"""
    queries = []
    
    try:
        # Decode content
        text_content = content.decode('utf-8')
        
        # Split by lines and clean
        lines = text_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                queries.append(line)
        
        return queries[:100]  # Limit to 100 queries
        
    except Exception as e:
        logging.error(f"Error parsing file {filename}: {e}")
        return []

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe usage"""
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:90] + ext
    
    return filename

def create_pagination_keyboard(current_page: int, total_pages: int, callback_prefix: str) -> InlineKeyboardMarkup:
    """Create pagination keyboard"""
    keyboard = []
    
    if total_pages <= 1:
        return InlineKeyboardMarkup(keyboard)
    
    # Navigation buttons
    nav_buttons = []
    
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"{callback_prefix}_{current_page - 1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="pagination_info"))
    
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"{callback_prefix}_{current_page + 1}"))
    
    keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def log_search_activity(user_id: int, query: str, search_type: str, results_count: int = 0):
    """Log search activity to JSON file"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "query": query[:100],  # Limit query length for privacy
            "search_type": search_type,
            "results_count": results_count
        }
        
        log_file = "assets/log_history.json"
        
        # Create file if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        # Read existing logs
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # Add new log
        logs.append(log_entry)
        
        # Keep only last 1000 logs
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Write back
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    except Exception as e:
        logging.error(f"Error logging search activity: {e}")

def get_faq_data(lang: str = "id") -> Dict[str, str]:
    """Get FAQ data"""
    if lang == "id":
        return {
            "breach_how": """
🔍 **Bagaimana kebocoran terjadi?**

Kebocoran data terjadi karena berbagai faktor:

**1. Serangan Siber**
• Hacking dan peretasan sistem
• SQL injection dan vulnerability exploit
• Malware dan ransomware

**2. Keamanan Lemah**
• Password yang lemah
• Sistem keamanan yang tidak update
• Konfigurasi server yang salah

**3. Faktor Manusia**
• Social engineering
• Phishing attacks
• Kelalaian karyawan

**4. Faktor Teknis**
• Bug dalam aplikasi
• Misconfigured databases
• Unsecured APIs

Penting untuk selalu menggunakan password yang kuat dan unik untuk setiap akun!
            """,
            "encryption": """
🔒 **Mengapa kata sandi dienkripsi?**

Enkripsi password adalah standar keamanan:

**Hash Functions:**
• MD5 (sudah tidak aman)
• SHA-1 (sudah tidak aman)
• SHA-256 (lebih aman)
• bcrypt (sangat aman)

**Mengapa dienkripsi?**
• Melindungi password asli
• Compliance dengan regulasi
• Mengurangi dampak kebocoran

**Namun perlu diingat:**
• Hash bisa di-crack dengan brute force
• Dictionary attacks masih mungkin
• Rainbow tables untuk hash umum

**Tip Keamanan:**
• Gunakan password yang panjang dan kompleks
• Aktifkan 2FA dimana memungkinkan
• Jangan gunakan password yang sama
            """,
            "protection": """
🛡️ **Bagaimana melindungi diri dari kebocoran?**

**Pencegahan Dasar:**
• Gunakan password manager
• Aktifkan two-factor authentication (2FA)
• Update software secara berkala
• Hindari WiFi publik untuk hal sensitif

**Password Security:**
• Minimal 12 karakter
• Kombinasi huruf, angka, dan simbol
• Unik untuk setiap akun
• Hindari informasi personal

**Monitoring:**
• Periksa akun secara berkala
• Set up alerts untuk login
• Monitor rekening bank
• Gunakan credit monitoring

**Jika Terkena Breach:**
• Segera ganti password
• Aktifkan 2FA
• Monitor aktivitas akun
• Laporkan ke pihak berwenang jika perlu
            """,
            "usage": """
⚖️ **Untuk apa penggunaan kebocoran?**

**Penggunaan Legal:**
• Security research
• Penetration testing
• Vulnerability assessment
• Digital forensics
• Academic research

**Penggunaan Personal:**
• Cek apakah data Anda bocor
• Audit keamanan personal
• Verifikasi identitas
• Background checks (legal)

**PERINGATAN:**
• Jangan gunakan untuk hacking
• Jangan gunakan untuk penipuan
• Jangan jual atau distribusi data
• Hormati privasi orang lain
• Patuhi hukum setempat

**Ethical Usage:**
• Gunakan hanya untuk keamanan
• Laporkan vulnerability yang ditemukan
• Bantu korban melindungi diri
• Edukasi tentang keamanan siber
            """,
            "sources": """
🔍 **Sumber data**

Data kebocoran dalam database kami berasal dari:

**Sumber Publik:**
• Breach databases yang dipublikasikan
• Security research reports
• Academic publications
• Government disclosures

**Validasi Data:**
• Verifikasi keaslian
• Cross-reference dengan sumber lain
• Filtering data sensitif
• Regular updates

**Keamanan Data:**
• Enkripsi penyimpanan
• Akses terbatas
• Audit trail
• Compliance dengan regulasi

**Disclaimer:**
• Data hanya untuk tujuan edukasi
• Kami tidak bertanggung jawab atas penyalahgunaan
• Gunakan dengan bijak dan legal
• Privasi tetap menjadi prioritas
            """
        }
    else:  # English
        return {
            "breach_how": """
🔍 **How do breaches occur?**

Data breaches happen due to various factors:

**1. Cyber Attacks**
• Hacking and system intrusion
• SQL injection and vulnerability exploits
• Malware and ransomware

**2. Weak Security**
• Weak passwords
• Outdated security systems
• Server misconfigurations

**3. Human Factors**
• Social engineering
• Phishing attacks
• Employee negligence

**4. Technical Issues**
• Application bugs
• Misconfigured databases
• Unsecured APIs

Always use strong, unique passwords for each account!
            """,
            "encryption": """
🔒 **Why are passwords encrypted?**

Password encryption is a security standard:

**Hash Functions:**
• MD5 (no longer secure)
• SHA-1 (no longer secure)
• SHA-256 (more secure)
• bcrypt (very secure)

**Why encrypt?**
• Protect original passwords
• Compliance with regulations
• Reduce breach impact

**However, remember:**
• Hashes can be cracked with brute force
• Dictionary attacks are still possible
• Rainbow tables for common hashes

**Security Tips:**
• Use long, complex passwords
• Enable 2FA where possible
• Don't reuse passwords
            """,
            "protection": """
🛡️ **How to protect yourself from breaches?**

**Basic Prevention:**
• Use a password manager
• Enable two-factor authentication (2FA)
• Keep software updated
• Avoid public WiFi for sensitive activities

**Password Security:**
• Minimum 12 characters
• Mix of letters, numbers, and symbols
• Unique for each account
• Avoid personal information

**Monitoring:**
• Check accounts regularly
• Set up login alerts
• Monitor bank statements
• Use credit monitoring

**If Breached:**
• Change passwords immediately
• Enable 2FA
• Monitor account activity
• Report to authorities if needed
            """,
            "usage": """
⚖️ **What are breaches used for?**

**Legal Usage:**
• Security research
• Penetration testing
• Vulnerability assessment
• Digital forensics
• Academic research

**Personal Usage:**
• Check if your data is breached
• Personal security audit
• Identity verification
• Background checks (legal)

**WARNING:**
• Don't use for hacking
• Don't use for fraud
• Don't sell or distribute data
• Respect others' privacy
• Follow local laws

**Ethical Usage:**
• Use only for security purposes
• Report vulnerabilities found
• Help victims protect themselves
• Educate about cybersecurity
            """,
            "sources": """
🔍 **Data sources**

Breach data in our database comes from:

**Public Sources:**
• Published breach databases
• Security research reports
• Academic publications
• Government disclosures

**Data Validation:**
• Authenticity verification
• Cross-reference with other sources
• Sensitive data filtering
• Regular updates

**Data Security:**
• Encrypted storage
• Limited access
• Audit trail
• Regulatory compliance

**Disclaimer:**
• Data is for educational purposes only
• We're not responsible for misuse
• Use wisely and legally
• Privacy remains a priority
            """
        }

def get_shop_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    """Get shop keyboard"""
    if lang == "id":
        keyboard = [
            [InlineKeyboardButton("🔓 Aktifkan Fitur Pencarian (50.000 Rp)", callback_data="shop_activate_trial")],
            [InlineKeyboardButton("🍺 1 Minggu - $4 (65.240 Rp)", callback_data="shop_week")],
            [InlineKeyboardButton("🌙 1 Bulan - $10 (163.100 Rp)", callback_data="shop_month")],
            [InlineKeyboardButton("🎄 1 Tahun - $50 (815.000 Rp)", callback_data="shop_year")],
            [InlineKeyboardButton("🔥 Selamanya - $200 (3.262.000 Rp)", callback_data="shop_lifetime")],
            [InlineKeyboardButton("💳 QRIS", callback_data="shop_qris")],
            [InlineKeyboardButton("💬 Pembayaran Lain", callback_data="shop_other_payment")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="shop_back")]
        ]
    else:  # English
        keyboard = [
            [InlineKeyboardButton("🔓 Activate Search (50.000 Rp)", callback_data="shop_activate_trial")],
            [InlineKeyboardButton("🍺 1 Week - $4 (65.240 Rp)", callback_data="shop_week")],
            [InlineKeyboardButton("🌙 1 Month - $10 (163.100 Rp)", callback_data="shop_month")],
            [InlineKeyboardButton("🎄 1 Year - $50 (815.000 Rp)", callback_data="shop_year")],
            [InlineKeyboardButton("🔥 Lifetime - $200 (3.262.000 Rp)", callback_data="shop_lifetime")],
            [InlineKeyboardButton("💳 QRIS", callback_data="shop_qris")],
            [InlineKeyboardButton("💬 Other Payment", callback_data="shop_other_payment")],
            [InlineKeyboardButton("⬅️ Back", callback_data="shop_back")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    """Get admin panel keyboard"""
    if lang == "id":
        keyboard = [
            [InlineKeyboardButton("📊 Statistik Pengguna", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Kelola Admin", callback_data="admin_manage_admins")],
            [InlineKeyboardButton("🚫 Kelola Pengguna", callback_data="admin_manage_users")],
            [InlineKeyboardButton("✅ Aktivasi Trial", callback_data="admin_activate_trial")],
            [InlineKeyboardButton("📢 Broadcast Pesan", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⚙️ Status Bot", callback_data="admin_bot_status")],
            [InlineKeyboardButton("📜 Log History", callback_data="admin_logs")],
            [InlineKeyboardButton("🔑 Manajemen API", callback_data="admin_api_management")]
        ]
    else:  # English
        keyboard = [
            [InlineKeyboardButton("📊 User Statistics", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Manage Admins", callback_data="admin_manage_admins")],
            [InlineKeyboardButton("🚫 Manage Users", callback_data="admin_manage_users")],
            [InlineKeyboardButton("✅ Activate Trial", callback_data="admin_activate_trial")],
            [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⚙️ Bot Status", callback_data="admin_bot_status")],
            [InlineKeyboardButton("📜 Log History", callback_data="admin_logs")],
            [InlineKeyboardButton("🔑 API Management", callback_data="admin_api_management")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def format_bot_status(bot_data: Dict[str, Any], lang: str = "id") -> str:
    """Format bot status for admin"""
    if lang == "id":
        return f"""
🤖 **Status Bot RexSint**

🔑 **API Token Aktif:** {bot_data.get('active_api_token', 'N/A')[:20]}...
📊 **Jumlah Request:** {bot_data.get('api_request_count', 0)}/99
📅 **Aktivasi:** {format_datetime(bot_data.get('api_activation_date'))}
🔧 **Maintenance:** {'Ya' if bot_data.get('is_maintenance') else 'Tidak'}

⚡ **Status:** {'🔴 Maintenance' if bot_data.get('is_maintenance') else '🟢 Online'}
        """
    else:  # English
        return f"""
🤖 **RexSint Bot Status**

🔑 **Active API Token:** {bot_data.get('active_api_token', 'N/A')[:20]}...
📊 **Request Count:** {bot_data.get('api_request_count', 0)}/99
📅 **Activated:** {format_datetime(bot_data.get('api_activation_date'))}
🔧 **Maintenance:** {'Yes' if bot_data.get('is_maintenance') else 'No'}

⚡ **Status:** {'🔴 Maintenance' if bot_data.get('is_maintenance') else '🟢 Online'}
        """

def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text to fit Telegram message limits"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - 50]
    return truncated + "\n\n... (teks terpotong, unduh laporan lengkap)"

def validate_user_input(text: str, input_type: str) -> Dict[str, Any]:
    """Validate user input"""
    import re
    
    if not text or not text.strip():
        return {"valid": False, "error": "Input tidak boleh kosong"}
    
    text = text.strip()
    
    if input_type == "email":
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, text):
            return {"valid": False, "error": "Format email tidak valid"}
    
    elif input_type == "phone":
        phone_pattern = r'^\+?[\d\s\-\(\)]{8,20}$'
        if not re.match(phone_pattern, text):
            return {"valid": False, "error": "Format nomor telepon tidak valid"}
    
    elif input_type == "ip":
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(ip_pattern, text):
            return {"valid": False, "error": "Format IP address tidak valid"}
    
    elif input_type == "name":
        if len(text) < 2:
            return {"valid": False, "error": "Nama minimal 2 karakter"}
        if len(text) > 100:
            return {"valid": False, "error": "Nama maksimal 100 karakter"}
    
    return {"valid": True, "cleaned": text}

def get_search_result_keyboard(has_results: bool = True, lang: str = "id") -> InlineKeyboardMarkup:
    """Get search result keyboard"""
    keyboard = []
    
    if has_results:
        if lang == "id":
            keyboard.append([InlineKeyboardButton("📄 Unduh Laporan Lengkap", callback_data="download_full_report")])
            keyboard.append([InlineKeyboardButton("🔍 Pencarian Baru", callback_data="new_search")])
        else:
            if lang == "id":
                keyboard.append([InlineKeyboardButton("🔍 Coba Pencarian Lain", callback_data="new_search")])
            else:
                keyboard.append([InlineKeyboardButton("🔍 Try Another Search", callback_data="new_search")])
    
    if lang == "id":
        keyboard.append([InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data="back_to_main")])
    else:
        keyboard.append([InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)

def get_file_search_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    """Get file search result keyboard"""
    if lang == "id":
        keyboard = [
            [InlineKeyboardButton("📊 Lihat Ringkasan", callback_data="view_summary")],
            [InlineKeyboardButton("📄 Unduh Laporan Lengkap", callback_data="download_bulk_report")],
            [InlineKeyboardButton("🔍 Pencarian Baru", callback_data="new_search")],
            [InlineKeyboardButton("🏠 Kembali ke Menu Utama", callback_data="back_to_main")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📊 View Summary", callback_data="view_summary")],
            [InlineKeyboardButton("📄 Download Full Report", callback_data="download_bulk_report")],
            [InlineKeyboardButton("🔍 New Search", callback_data="new_search")],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def get_faq_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    """Get FAQ selection keyboard"""
    if lang == "id":
        keyboard = [
            [InlineKeyboardButton("❓ Bagaimana kebocoran terjadi?", callback_data="faq_breach_how")],
            [InlineKeyboardButton("🔒 Mengapa kata sandi dienkripsi?", callback_data="faq_encryption")],
            [InlineKeyboardButton("🛡️ Bagaimana melindungi diri?", callback_data="faq_protection")],
            [InlineKeyboardButton("⚖️ Untuk apa penggunaan kebocoran?", callback_data="faq_usage")],
            [InlineKeyboardButton("🔍 Sumber data", callback_data="faq_sources")],
            [InlineKeyboardButton("⬅️ Kembali ke Menu Info", callback_data="back_to_info")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("❓ How do breaches occur?", callback_data="faq_breach_how")],
            [InlineKeyboardButton("🔒 Why are passwords encrypted?", callback_data="faq_encryption")],
            [InlineKeyboardButton("🛡️ How to protect yourself?", callback_data="faq_protection")],
            [InlineKeyboardButton("⚖️ What are breaches used for?", callback_data="faq_usage")],
            [InlineKeyboardButton("🔍 Data sources", callback_data="faq_sources")],
            [InlineKeyboardButton("⬅️ Back to Info Menu", callback_data="back_to_info")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def get_api_management_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    """Get API management keyboard for admin"""
    if lang == "id":
        keyboard = [
            [InlineKeyboardButton("ℹ️ Status API Saat Ini", callback_data="api_current_status")],
            [InlineKeyboardButton("🔍 Dapatkan Token Pengguna", callback_data="api_get_user_token")],
            [InlineKeyboardButton("🚀 Atur Token Baru", callback_data="api_set_new_token")],
            [InlineKeyboardButton("🔁 Restart Bot", callback_data="api_restart_bot")],
            [InlineKeyboardButton("⬅️ Kembali ke Panel Admin", callback_data="back_to_admin")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("ℹ️ Current API Status", callback_data="api_current_status")],
            [InlineKeyboardButton("🔍 Get User Token", callback_data="api_get_user_token")],
            [InlineKeyboardButton("🚀 Set New Token", callback_data="api_set_new_token")],
            [InlineKeyboardButton("🔁 Restart Bot", callback_data="api_restart_bot")],
            [InlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="back_to_admin")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def create_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Create progress bar for file processing"""
    if total == 0:
        return "▱" * width
    
    progress = current / total
    filled_width = int(progress * width)
    bar = "▰" * filled_width + "▱" * (width - filled_width)
    percentage = int(progress * 100)
    
    return f"{bar} {percentage}%"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_system_info() -> Dict[str, Any]:
    """Get system information for admin"""
    import psutil
    import platform
    
    try:
        # Get CPU and memory info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get process info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_percent": cpu_percent,
            "memory_total": format_file_size(memory.total),
            "memory_used": format_file_size(memory.used),
            "memory_percent": memory.percent,
            "disk_total": format_file_size(disk.total),
            "disk_used": format_file_size(disk.used),
            "disk_percent": (disk.used / disk.total) * 100,
            "process_memory": format_file_size(process_memory.rss),
            "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        return {}

def clean_old_files(directory: str, days_old: int = 7):
    """Clean old files from directory"""
    try:
        import glob
        from pathlib import Path
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        
        for file_path in glob.glob(os.path.join(directory, "*")):
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_time:
                    os.remove(file_path)
                    logging.info(f"Deleted old file: {file_path}")
                    
    except Exception as e:
        logging.error(f"Error cleaning old files: {e}")

def generate_report_filename(query: str, search_type: str) -> str:
    """Generate filename for reports"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_query = sanitize_filename(query[:20])
    return f"RexSint_{search_type}_{clean_query}_{timestamp}.html"

def create_backup_filename() -> str:
    """Create backup filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"rexsint_backup_{timestamp}.db"

def validate_admin_command(command: str, user_id: int) -> Dict[str, Any]:
    """Validate admin command format"""
    parts = command.split()
    
    if len(parts) < 2:
        return {"valid": False, "error": "Format command tidak valid"}
    
    cmd = parts[0].lower()
    
    if cmd == "/activatetrial":
        if len(parts) != 2:
            return {"valid": False, "error": "Format: /activatetrial <user_id>"}
        try:
            target_user_id = int(parts[1])
            return {"valid": True, "command": "activate_trial", "user_id": target_user_id}
        except ValueError:
            return {"valid": False, "error": "User ID harus berupa angka"}
    
    elif cmd == "/generate":
        if len(parts) != 2:
            return {"valid": False, "error": "Format: /generate <user_id>"}
        try:
            target_user_id = int(parts[1])
            return {"valid": True, "command": "generate_token", "user_id": target_user_id}
        except ValueError:
            return {"valid": False, "error": "User ID harus berupa angka"}
    
    elif cmd == "/setnewapi":
        if len(parts) != 2:
            return {"valid": False, "error": "Format: /setnewapi <api_token>"}
        api_token = parts[1]
        if len(api_token) < 10:
            return {"valid": False, "error": "API token terlalu pendek"}
        return {"valid": True, "command": "set_new_api", "token": api_token}
    
    elif cmd == "/block":
        if len(parts) != 2:
            return {"valid": False, "error": "Format: /block <user_id>"}
        try:
            target_user_id = int(parts[1])
            return {"valid": True, "command": "block_user", "user_id": target_user_id}
        except ValueError:
            return {"valid": False, "error": "User ID harus berupa angka"}
    
    elif cmd == "/unblock":
        if len(parts) != 2:
            return {"valid": False, "error": "Format: /unblock <user_id>"}
        try:
            target_user_id = int(parts[1])
            return {"valid": True, "command": "unblock_user", "user_id": target_user_id}
        except ValueError:
            return {"valid": False, "error": "User ID harus berupa angka"}
    
    return {"valid": False, "error": "Command tidak dikenali"}

def escape_markdown(text: str) -> str:
    """Escape markdown characters for Telegram"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_currency(amount: float, currency: str = "IDR") -> str:
    """Format currency for display"""
    if currency == "IDR":
        return f"Rp {amount:,.0f}".replace(",", ".")
    elif currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"

def get_local_time(timezone: str = "Asia/Jakarta") -> str:
    """Get current local time in specified timezone"""
    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.now(tz)
        return local_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """Mask sensitive data for logging"""
    if not data or len(data) < 4:
        return mask_char * len(data) if data else ""
    
    # Show first 2 and last 2 characters
    visible_chars = 2
    if len(data) <= visible_chars * 2:
        return data[:1] + mask_char * (len(data) - 2) + data[-1:]
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars * 2) + data[-visible_chars:]

def check_file_type(filename: str) -> str:
    """Check and return file type"""
    import mimetypes
    
    mime_type, _ = mimetypes.guess_type(filename)
    
    if mime_type:
        if mime_type.startswith('text/'):
            return 'text'
        elif mime_type == 'application/json':
            return 'json'
        elif mime_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            return 'excel'
        elif mime_type == 'application/pdf':
            return 'pdf'
    
    # Check by extension
    ext = filename.lower().split('.')[-1]
    if ext in ['txt', 'csv']:
        return 'text'
    elif ext == 'json':
        return 'json'
    elif ext in ['xls', 'xlsx']:
        return 'excel'
    elif ext == 'pdf':
        return 'pdf'
    
    return 'unknown'

def create_error_message(error: str, lang: str = "id") -> str:
    """Create formatted error message"""
    if lang == "id":
        return f"❌ **Error:** {error}\n\nSilakan coba lagi atau hubungi admin jika masalah berlanjut."
    else:
        return f"❌ **Error:** {error}\n\nPlease try again or contact admin if the problem persists."

def create_success_message(message: str, lang: str = "id") -> str:
    """Create formatted success message"""
    if lang == "id":
        return f"✅ **Berhasil:** {message}"
    else:
        return f"✅ **Success:** {message}"

def create_warning_message(message: str, lang: str = "id") -> str:
    """Create formatted warning message"""
    if lang == "id":
        return f"⚠️ **Peringatan:** {message}"
    else:
        return f"⚠️ **Warning:** {message}"

def create_info_message(message: str, lang: str = "id") -> str:
    """Create formatted info message"""
    if lang == "id":
        return f"ℹ️ **Info:** {message}"
    else:
        return f"ℹ️ **Info:** {message}"

def get_maintenance_message(lang: str = "id") -> str:
    """Get maintenance mode message"""
    if lang == "id":
        return """
🔧 **Bot Sedang Dalam Maintenance**

Maaf, bot sedang dalam tahap pemeliharaan untuk meningkatkan performa dan keamanan.

⏰ **Estimasi:** 5-15 menit
🔄 **Status:** Pembaruan sistem
📧 **Info:** Hubungi admin untuk informasi lebih lanjut

Terima kasih atas kesabaran Anda!
        """
    else:
        return """
🔧 **Bot Under Maintenance**

Sorry, the bot is currently under maintenance to improve performance and security.

⏰ **Estimated:** 5-15 minutes
🔄 **Status:** System update
📧 **Info:** Contact admin for more information

Thank you for your patience!
        """

def get_rate_limit_message(lang: str = "id") -> str:
    """Get rate limit message"""
    if lang == "id":
        return """
⏰ **Batas Kecepatan Tercapai**

Anda telah mencapai batas maksimal permintaan per menit.

🔄 **Coba lagi dalam:** 1 menit
📊 **Batas:** 10 permintaan per menit
💡 **Tips:** Gunakan pencarian massal untuk query multiple

Terima kasih atas pengertian Anda!
        """
    else:
        return """
⏰ **Rate Limit Reached**

You have reached the maximum number of requests per minute.

🔄 **Try again in:** 1 minute
📊 **Limit:** 10 requests per minute
💡 **Tip:** Use bulk search for multiple queries

Thank you for your understanding!
        """

# Initialize required directories
def init_directories():
    """Initialize required directories"""
    directories = ['logs', 'assets', 'temp', 'reports']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Auto-cleanup function
def auto_cleanup():
    """Auto cleanup old files"""
    try:
        # Clean temp files older than 1 day
        clean_old_files('temp', 1)
        
        # Clean report files older than 7 days
        clean_old_files('reports', 7)
        
        # Clean log files older than 30 days
        clean_old_files('logs', 30)
        
        logging.info("Auto cleanup completed")
    except Exception as e:
        logging.error(f"Auto cleanup failed: {e}")