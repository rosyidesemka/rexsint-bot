"""
Locales package for RexSint Bot
Multi-language support and localization utilities
"""

from .localization import (
    LocalizationManager,
    get_localization_manager,
    get_text,
    format_currency,
    format_date,
    format_time_ago,
    create_user_welcome_message,
    create_search_results_message,
    create_error_message,
    create_success_message,
    create_maintenance_message,
    create_permission_denied_message,
    create_subscription_status_message,
    detect_user_language
)

# Version info
__version__ = "1.0.0"
__author__ = "RexSint Team"

# Supported languages
SUPPORTED_LANGUAGES = ["id", "en"]
DEFAULT_LANGUAGE = "id"

# Language metadata
LANGUAGE_INFO = {
    "id": {
        "name": "Bahasa Indonesia",
        "native_name": "Bahasa Indonesia",
        "flag": "🇮🇩",
        "code": "id"
    },
    "en": {
        "name": "English",
        "native_name": "English",
        "flag": "🇬🇧",
        "code": "en"
    }
}

# Export all public functions
__all__ = [
    "LocalizationManager",
    "get_localization_manager",
    "get_text",
    "format_currency",
    "format_date",
    "format_time_ago",
    "create_user_welcome_message",
    "create_search_results_message",
    "create_error_message",
    "create_success_message",
    "create_maintenance_message",
    "create_permission_denied_message",
    "create_subscription_status_message",
    "detect_user_language",
    "SUPPORTED_LANGUAGES",
    "DEFAULT_LANGUAGE",
    "LANGUAGE_INFO"
]

# Common text templates
COMMON_TEMPLATES = {
    "welcome_new_user": {
        "id": "✅ Selamat datang di RexSint, {name}! Akun Anda berhasil dibuat.",
        "en": "✅ Welcome to RexSint, {name}! Your account has been created successfully."
    },
    "trial_activated": {
        "id": "🎉 Trial 7 hari Anda telah diaktifkan! Selamat mencoba fitur premium.",
        "en": "🎉 Your 7-day trial has been activated! Enjoy exploring premium features."
    },
    "subscription_expired": {
        "id": "⏰ Berlangganan Anda telah berakhir. Silakan perpanjang di menu Toko.",
        "en": "⏰ Your subscription has expired. Please renew in the Shop menu."
    },
    "search_completed": {
        "id": "✅ Pencarian selesai! Ditemukan {count} hasil dalam {databases} database.",
        "en": "✅ Search completed! Found {count} results in {databases} databases."
    },
    "payment_pending": {
        "id": "💳 Pembayaran Anda sedang diproses. Kami akan mengonfirmasi dalam 1-24 jam.",
        "en": "💳 Your payment is being processed. We will confirm within 1-24 hours."
    }
}

# Error message templates
ERROR_TEMPLATES = {
    "insufficient_tokens": {
        "id": "🪙 Token tidak mencukupi. Sisa token: {remaining}. Silakan beli token di menu Toko.",
        "en": "🪙 Insufficient tokens. Remaining: {remaining}. Please buy tokens in Shop menu."
    },
    "search_failed": {
        "id": "❌ Pencarian gagal: {reason}. Silakan coba lagi atau hubungi admin.",
        "en": "❌ Search failed: {reason}. Please try again or contact admin."
    },
    "file_processing_error": {
        "id": "📁 Gagal memproses file: {error}. Pastikan format file benar.",
        "en": "📁 Failed to process file: {error}. Please ensure file format is correct."
    },
    "rate_limit_exceeded": {
        "id": "⏰ Terlalu banyak permintaan. Silakan tunggu {seconds} detik.",
        "en": "⏰ Too many requests. Please wait {seconds} seconds."
    },
    "premium_feature_locked": {
        "id": "🔒 Fitur ini hanya untuk pengguna premium. Upgrade akun Anda di menu Toko.",
        "en": "🔒 This feature is for premium users only. Upgrade your account in Shop menu."
    }
}

# Success message templates
SUCCESS_TEMPLATES = {
    "settings_updated": {
        "id": "⚙️ Pengaturan berhasil disimpan!",
        "en": "⚙️ Settings saved successfully!"
    },
    "payment_confirmed": {
        "id": "💰 Pembayaran berhasil dikonfirmasi! Akun Anda telah diaktifkan.",
        "en": "💰 Payment confirmed successfully! Your account has been activated."
    },
    "report_generated": {
        "id": "📄 Laporan berhasil dibuat dan dikirim!",
        "en": "📄 Report generated and sent successfully!"
    },
    "subscription_extended": {
        "id": "📅 Berlangganan berhasil diperpanjang hingga {date}.",
        "en": "📅 Subscription extended successfully until {date}."
    },
    "bulk_search_completed": {
        "id": "📊 Pencarian massal selesai! Diproses {processed} dari {total} query.",
        "en": "📊 Bulk search completed! Processed {processed} out of {total} queries."
    }
}

# Button text collections
BUTTON_COLLECTIONS = {
    "navigation": {
        "id": {
            "main_menu": "🏠 Menu Utama",
            "back": "⬅️ Kembali",
            "next": "➡️ Lanjut",
            "cancel": "❌ Batal",
            "confirm": "✅ Konfirmasi"
        },
        "en": {
            "main_menu": "🏠 Main Menu",
            "back": "⬅️ Back",
            "next": "➡️ Next",
            "cancel": "❌ Cancel",
            "confirm": "✅ Confirm"
        }
    },
    "search": {
        "id": {
            "new_search": "🔍 Pencarian Baru",
            "download_report": "📄 Unduh Laporan",
            "view_results": "👀 Lihat Hasil",
            "search_again": "🔄 Cari Lagi"
        },
        "en": {
            "new_search": "🔍 New Search",
            "download_report": "📄 Download Report",
            "view_results": "👀 View Results",
            "search_again": "🔄 Search Again"
        }
    },
    "payment": {
        "id": {
            "pay_now": "💳 Bayar Sekarang",
            "payment_proof": "📸 Kirim Bukti",
            "check_payment": "🔍 Cek Pembayaran",
            "contact_support": "💬 Hubungi CS"
        },
        "en": {
            "pay_now": "💳 Pay Now",
            "payment_proof": "📸 Send Proof",
            "check_payment": "🔍 Check Payment",
            "contact_support": "💬 Contact Support"
        }
    }
}

# Status indicators
STATUS_INDICATORS = {
    "user_status": {
        "id": {
            "active": "🟢 Aktif",
            "inactive": "🔴 Tidak Aktif",
            "trial": "🟡 Trial",
            "expired": "⏰ Berakhir",
            "blocked": "🚫 Diblokir"
        },
        "en": {
            "active": "🟢 Active",
            "inactive": "🔴 Inactive",
            "trial": "🟡 Trial",
            "expired": "⏰ Expired",
            "blocked": "🚫 Blocked"
        }
    },
    "bot_status": {
        "id": {
            "online": "🟢 Online",
            "maintenance": "🔧 Maintenance",
            "limited": "🟡 Terbatas",
            "error": "🔴 Error"
        },
        "en": {
            "online": "🟢 Online",
            "maintenance": "🔧 Maintenance",
            "limited": "🟡 Limited",
            "error": "🔴 Error"
        }
    }
}

# Utility functions for common operations
def get_template_text(template_name: str, lang: str = None, **kwargs) -> str:
    """Get text from common templates"""
    lang = lang or DEFAULT_LANGUAGE
    
    # Try common templates first
    if template_name in COMMON_TEMPLATES:
        template = COMMON_TEMPLATES[template_name].get(lang, COMMON_TEMPLATES[template_name].get(DEFAULT_LANGUAGE, ""))
        return template.format(**kwargs) if kwargs else template
    
    # Try error templates
    if template_name in ERROR_TEMPLATES:
        template = ERROR_TEMPLATES[template_name].get(lang, ERROR_TEMPLATES[template_name].get(DEFAULT_LANGUAGE, ""))
        return template.format(**kwargs) if kwargs else template
    
    # Try success templates
    if template_name in SUCCESS_TEMPLATES:
        template = SUCCESS_TEMPLATES[template_name].get(lang, SUCCESS_TEMPLATES[template_name].get(DEFAULT_LANGUAGE, ""))
        return template.format(**kwargs) if kwargs else template
    
    return f"[{template_name}]"

def get_button_text(collection: str, button: str, lang: str = None) -> str:
    """Get button text from collections"""
    lang = lang or DEFAULT_LANGUAGE
    
    if collection in BUTTON_COLLECTIONS:
        return BUTTON_COLLECTIONS[collection].get(lang, {}).get(button, button)
    
    return button

def get_status_indicator(status_type: str, status: str, lang: str = None) -> str:
    """Get status indicator with emoji"""
    lang = lang or DEFAULT_LANGUAGE
    
    if status_type in STATUS_INDICATORS:
        return STATUS_INDICATORS[status_type].get(lang, {}).get(status, status)
    
    return status

def format_user_count(count: int, lang: str = None) -> str:
    """Format user count with proper pluralization"""
    lang = lang or DEFAULT_LANGUAGE
    
    if lang == "id":
        return f"{count:,} pengguna"
    else:
        return f"{count:,} user{'s' if count != 1 else ''}"

def format_search_count(count: int, lang: str = None) -> str:
    """Format search count with proper pluralization"""
    lang = lang or DEFAULT_LANGUAGE
    
    if lang == "id":
        return f"{count:,} pencarian"
    else:
        return f"{count:,} search{'es' if count != 1 else ''}"

def format_database_count(count: int, lang: str = None) -> str:
    """Format database count with proper pluralization"""
    lang = lang or DEFAULT_LANGUAGE
    
    if lang == "id":
        return f"{count:,} database"
    else:
        return f"{count:,} database{'s' if count != 1 else ''}"

def format_token_count(count: int, lang: str = None) -> str:
    """Format token count with proper pluralization"""
    lang = lang or DEFAULT_LANGUAGE
    
    if lang == "id":
        return f"{count:,} token"
    else:
        return f"{count:,} token{'s' if count != 1 else ''}"

def get_time_unit(unit: str, lang: str = None) -> str:
    """Get localized time unit"""
    lang = lang or DEFAULT_LANGUAGE
    
    time_units = {
        "id": {
            "second": "detik",
            "minute": "menit",
            "hour": "jam",
            "day": "hari",
            "week": "minggu",
            "month": "bulan",
            "year": "tahun"
        },
        "en": {
            "second": "second",
            "minute": "minute",
            "hour": "hour",
            "day": "day",
            "week": "week",
            "month": "month",
            "year": "year"
        }
    }
    
    return time_units.get(lang, {}).get(unit, unit)

def create_progress_text(current: int, total: int, lang: str = None) -> str:
    """Create progress text"""
    lang = lang or DEFAULT_LANGUAGE
    
    if lang == "id":
        return f"Memproses {current} dari {total}..."
    else:
        return f"Processing {current} of {total}..."

def create_countdown_text(seconds: int, lang: str = None) -> str:
    """Create countdown text"""
    lang = lang or DEFAULT_LANGUAGE
    
    if seconds <= 0:
        return get_text("time.just_now", lang)
    
    if seconds < 60:
        unit = get_time_unit("second", lang)
        return f"{seconds} {unit}"
    elif seconds < 3600:
        minutes = seconds // 60
        unit = get_time_unit("minute", lang)
        return f"{minutes} {unit}"
    else:
        hours = seconds // 3600
        unit = get_time_unit("hour", lang)
        return f"{hours} {unit}"

def create_file_size_text(bytes_size: int, lang: str = None) -> str:
    """Create file size text"""
    lang = lang or DEFAULT_LANGUAGE
    
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"

def create_percentage_text(value: float, total: float, lang: str = None) -> str:
    """Create percentage text"""
    if total == 0:
        return "0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"

def validate_language_code(lang_code: str) -> str:
    """Validate and normalize language code"""
    if not lang_code:
        return DEFAULT_LANGUAGE
    
    # Extract base language code
    base_lang = lang_code.split('-')[0].lower()
    
    # Map common language codes
    language_map = {
        'id': 'id',
        'in': 'id',  # Indonesian alternative
        'en': 'en',
        'eng': 'en'
    }
    
    return language_map.get(base_lang, DEFAULT_LANGUAGE)

def get_language_direction(lang: str) -> str:
    """Get text direction for language (ltr/rtl)"""
    # All currently supported languages are left-to-right
    return "ltr"

def get_language_flag(lang: str) -> str:
    """Get flag emoji for language"""
    return LANGUAGE_INFO.get(lang, {}).get("flag", "🏳️")

def get_language_name(lang: str, display_lang: str = None) -> str:
    """Get language name in specified display language"""
    display_lang = display_lang or lang
    
    if display_lang == "id":
        names = {
            "id": "Bahasa Indonesia",
            "en": "Bahasa Inggris"
        }
    else:
        names = {
            "id": "Indonesian",
            "en": "English"
        }
    
    return names.get(lang, lang)

# Localization configuration
LOCALIZATION_CONFIG = {
    "default_language": DEFAULT_LANGUAGE,
    "supported_languages": SUPPORTED_LANGUAGES,
    "fallback_enabled": True,
    "auto_detect_language": True,
    "cache_translations": True,
    "reload_on_change": False,
    "strict_mode": False  # If True, missing translations will raise errors
}

# Initialize global localization manager
_global_manager = None

def init_localization(config: dict = None):
    """Initialize global localization manager"""
    global _global_manager
    
    if config:
        LOCALIZATION_CONFIG.update(config)
    
    _global_manager = LocalizationManager()
    return _global_manager

def get_global_manager():
    """Get global localization manager"""
    global _global_manager
    if _global_manager is None:
        _global_manager = init_localization()
    return _global_manager

# Convenience functions using global manager
def t(key: str, lang: str = None, **kwargs) -> str:
    """Short alias for get_text"""
    return get_global_manager().get_text(key, lang, **kwargs)

def tt(template_name: str, lang: str = None, **kwargs) -> str:
    """Short alias for get_template_text"""
    return get_template_text(template_name, lang, **kwargs)

def tb(collection: str, button: str, lang: str = None) -> str:
    """Short alias for get_button_text"""
    return get_button_text(collection, button, lang)

def ts(status_type: str, status: str, lang: str = None) -> str:
    """Short alias for get_status_indicator"""
    return get_status_indicator(status_type, status, lang)