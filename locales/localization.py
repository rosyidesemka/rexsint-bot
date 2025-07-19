"""
Localization Helper for RexSint Bot
Handles multi-language support and text formatting
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

class LocalizationManager:
    """Manages localization for the bot"""
    
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = locales_dir
        self.logger = logging.getLogger(__name__)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.default_language = "id"
        self.supported_languages = ["id", "en"]
        
        # Load all translations
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        try:
            for lang in self.supported_languages:
                file_path = os.path.join(self.locales_dir, f"{lang}.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                    self.logger.info(f"Loaded translations for language: {lang}")
                else:
                    self.logger.warning(f"Translation file not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading translations: {e}")
    
    def get_text(self, key: str, lang: str = None, **kwargs) -> str:
        """Get localized text by key"""
        if lang is None:
            lang = self.default_language
        
        if lang not in self.supported_languages:
            lang = self.default_language
        
        try:
            # Navigate through nested keys (e.g., "common.yes")
            keys = key.split(".")
            text = self.translations.get(lang, {})
            
            for k in keys:
                if isinstance(text, dict) and k in text:
                    text = text[k]
                else:
                    # Fallback to default language
                    text = self.translations.get(self.default_language, {})
                    for k in keys:
                        if isinstance(text, dict) and k in text:
                            text = text[k]
                        else:
                            return f"[{key}]"  # Return key if not found
                    break
            
            # Format text with parameters
            if isinstance(text, str) and kwargs:
                try:
                    return text.format(**kwargs)
                except KeyError as e:
                    self.logger.warning(f"Missing parameter {e} for key {key}")
                    return text
            
            return str(text) if text is not None else f"[{key}]"
            
        except Exception as e:
            self.logger.error(f"Error getting text for key {key}: {e}")
            return f"[{key}]"
    
    def get_buttons(self, section: str, lang: str = None) -> Dict[str, str]:
        """Get button texts for a section"""
        if lang is None:
            lang = self.default_language
        
        try:
            buttons = self.translations.get(lang, {}).get("buttons", {})
            if section:
                return {k: v for k, v in buttons.items() if k.startswith(section)}
            return buttons
        except Exception as e:
            self.logger.error(f"Error getting buttons for section {section}: {e}")
            return {}
    
    def get_status_text(self, status: str, lang: str = None) -> str:
        """Get status text"""
        return self.get_text(f"status.{status}", lang)
    
    def get_error_text(self, error_type: str, lang: str = None) -> str:
        """Get error message text"""
        return self.get_text(f"errors.{error_type}", lang)
    
    def get_success_text(self, success_type: str, lang: str = None) -> str:
        """Get success message text"""
        return self.get_text(f"success.{success_type}", lang)
    
    def format_currency(self, amount: float, currency: str = "idr", lang: str = None) -> str:
        """Format currency according to locale"""
        if lang is None:
            lang = self.default_language
        
        try:
            format_key = f"formats.currency.{currency.lower()}"
            format_template = self.get_text(format_key, lang)
            
            # Format amount based on currency
            if currency.lower() == "idr":
                # Indonesian Rupiah formatting
                formatted_amount = f"{amount:,.0f}".replace(",", ".")
            else:
                # USD and other currencies
                formatted_amount = f"{amount:,.2f}"
            
            return format_template.replace("{amount}", formatted_amount)
        except Exception as e:
            self.logger.error(f"Error formatting currency: {e}")
            return f"{amount} {currency.upper()}"
    
    def format_date(self, date: datetime, format_type: str = "short", lang: str = None) -> str:
        """Format date according to locale"""
        if lang is None:
            lang = self.default_language
        
        try:
            if lang == "id":
                # Indonesian date formatting
                if format_type == "short":
                    return date.strftime("%d/%m/%Y")
                elif format_type == "long":
                    months = [
                        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
                    ]
                    return f"{date.day} {months[date.month-1]} {date.year}"
                elif format_type == "with_time":
                    return date.strftime("%d/%m/%Y %H:%M")
            else:
                # English date formatting
                if format_type == "short":
                    return date.strftime("%m/%d/%Y")
                elif format_type == "long":
                    return date.strftime("%B %d, %Y")
                elif format_type == "with_time":
                    return date.strftime("%m/%d/%Y %H:%M")
            
            return date.strftime("%Y-%m-%d")
        except Exception as e:
            self.logger.error(f"Error formatting date: {e}")
            return date.strftime("%Y-%m-%d")
    
    def format_number(self, number: int, lang: str = None) -> str:
        """Format large numbers with appropriate suffixes"""
        if lang is None:
            lang = self.default_language
        
        try:
            if number >= 1_000_000_000:
                suffix = self.get_text("formats.number.billion", lang)
                return f"{number / 1_000_000_000:.1f}{suffix}"
            elif number >= 1_000_000:
                suffix = self.get_text("formats.number.million", lang)
                return f"{number / 1_000_000:.1f}{suffix}"
            elif number >= 1_000:
                suffix = self.get_text("formats.number.thousand", lang)
                return f"{number / 1_000:.1f}{suffix}"
            else:
                return f"{number:,}"
        except Exception as e:
            self.logger.error(f"Error formatting number: {e}")
            return str(number)
    
    def format_time_ago(self, date: datetime, lang: str = None) -> str:
        """Format time ago in human readable format"""
        if lang is None:
            lang = self.default_language
        
        try:
            now = datetime.now()
            delta = now - date
            
            if delta.days > 365:
                years = delta.days // 365
                unit = self.get_text("time.years", lang)
                return f"{years} {unit} {self.get_text('time.ago', lang)}"
            elif delta.days > 30:
                months = delta.days // 30
                unit = self.get_text("time.months", lang)
                return f"{months} {unit} {self.get_text('time.ago', lang)}"
            elif delta.days > 0:
                unit = self.get_text("time.days", lang)
                return f"{delta.days} {unit} {self.get_text('time.ago', lang)}"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                unit = self.get_text("time.hours", lang)
                return f"{hours} {unit} {self.get_text('time.ago', lang)}"
            elif delta.seconds > 60:
                minutes = delta.seconds // 60
                unit = self.get_text("time.minutes", lang)
                return f"{minutes} {unit} {self.get_text('time.ago', lang)}"
            else:
                return self.get_text("time.just_now", lang)
        except Exception as e:
            self.logger.error(f"Error formatting time ago: {e}")
            return str(date)
    
    def get_language_info(self, lang: str) -> Dict[str, str]:
        """Get language metadata"""
        try:
            return self.translations.get(lang, {}).get("meta", {})
        except Exception:
            return {}
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        languages = []
        for lang in self.supported_languages:
            meta = self.get_language_info(lang)
            if meta:
                languages.append({
                    "code": lang,
                    "name": meta.get("name", lang),
                    "flag": meta.get("flag", "")
                })
        return languages
    
    def validate_language(self, lang: str) -> bool:
        """Validate if language is supported"""
        return lang in self.supported_languages
    
    def get_validation_message(self, validation_type: str, lang: str = None, **kwargs) -> str:
        """Get validation message"""
        key = f"validation.{validation_type}"
        return self.get_text(key, lang, **kwargs)
    
    def get_notification_text(self, notification_type: str, lang: str = None) -> str:
        """Get notification text"""
        return self.get_text(f"notifications.{notification_type}", lang)
    
    def interpolate_text(self, text: str, variables: Dict[str, Any]) -> str:
        """Interpolate variables in text"""
        try:
            # Replace {variable} patterns with actual values
            for key, value in variables.items():
                pattern = f"{{{key}}}"
                text = text.replace(pattern, str(value))
            return text
        except Exception as e:
            self.logger.error(f"Error interpolating text: {e}")
            return text
    
    def get_menu_text(self, menu_section: str, lang: str = None) -> Dict[str, str]:
        """Get menu texts for a section"""
        try:
            return self.translations.get(lang or self.default_language, {}).get(menu_section, {})
        except Exception as e:
            self.logger.error(f"Error getting menu text for {menu_section}: {e}")
            return {}
    
    def create_formatted_message(self, template_key: str, lang: str = None, **kwargs) -> str:
        """Create formatted message from template"""
        template = self.get_text(template_key, lang)
        return self.interpolate_text(template, kwargs)
    
    def get_plural_form(self, count: int, singular_key: str, plural_key: str, lang: str = None) -> str:
        """Get plural form based on count"""
        if lang is None:
            lang = self.default_language
        
        if count == 1:
            return self.get_text(singular_key, lang)
        else:
            return self.get_text(plural_key, lang)
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text for safe display"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        if len(text) > 4000:
            text = text[:3997] + "..."
        
        return text.strip()
    
    def reload_translations(self):
        """Reload all translation files"""
        self.translations.clear()
        self._load_translations()
        self.logger.info("Translations reloaded")
    
    def add_dynamic_translation(self, lang: str, key: str, value: str):
        """Add dynamic translation at runtime"""
        try:
            if lang not in self.translations:
                self.translations[lang] = {}
            
            # Navigate through nested keys
            keys = key.split(".")
            current = self.translations[lang]
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            self.logger.info(f"Added dynamic translation: {lang}.{key}")
        except Exception as e:
            self.logger.error(f"Error adding dynamic translation: {e}")
    
    def export_translations(self, lang: str) -> Dict[str, Any]:
        """Export translations for backup"""
        return self.translations.get(lang, {})
    
    def import_translations(self, lang: str, data: Dict[str, Any]) -> bool:
        """Import translations from backup"""
        try:
            self.translations[lang] = data
            return True
        except Exception as e:
            self.logger.error(f"Error importing translations: {e}")
            return False
    
    def get_missing_translations(self, lang: str) -> List[str]:
        """Get list of missing translations for a language"""
        try:
            default_keys = self._get_all_keys(self.translations[self.default_language])
            lang_keys = self._get_all_keys(self.translations.get(lang, {}))
            return list(set(default_keys) - set(lang_keys))
        except Exception as e:
            self.logger.error(f"Error getting missing translations: {e}")
            return []
    
    def _get_all_keys(self, data: Dict[str, Any], prefix: str = "") -> List[str]:
        """Get all keys from nested dictionary"""
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys.extend(self._get_all_keys(value, full_key))
            else:
                keys.append(full_key)
        return keys
    
    def get_translation_coverage(self, lang: str) -> float:
        """Get translation coverage percentage"""
        try:
            default_keys = self._get_all_keys(self.translations[self.default_language])
            lang_keys = self._get_all_keys(self.translations.get(lang, {}))
            
            if not default_keys:
                return 0.0
            
            coverage = len(lang_keys) / len(default_keys) * 100
            return round(coverage, 2)
        except Exception as e:
            self.logger.error(f"Error calculating translation coverage: {e}")
            return 0.0

# Global localization manager instance
_localization_manager = None

def get_localization_manager() -> LocalizationManager:
    """Get global localization manager instance"""
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager()
    return _localization_manager

def get_text(key: str, lang: str = None, **kwargs) -> str:
    """Shortcut function to get localized text"""
    return get_localization_manager().get_text(key, lang, **kwargs)

def format_currency(amount: float, currency: str = "idr", lang: str = None) -> str:
    """Shortcut function to format currency"""
    return get_localization_manager().format_currency(amount, currency, lang)

def format_date(date: datetime, format_type: str = "short", lang: str = None) -> str:
    """Shortcut function to format date"""
    return get_localization_manager().format_date(date, format_type, lang)

def format_time_ago(date: datetime, lang: str = None) -> str:
    """Shortcut function to format time ago"""
    return get_localization_manager().format_time_ago(date, lang)

# Template functions for common use cases
def create_user_welcome_message(user_name: str, lang: str = None) -> str:
    """Create welcome message for new user"""
    return get_text("messages.welcome_back", lang, name=user_name)

def create_search_results_message(count: int, lang: str = None) -> str:
    """Create search results message"""
    return get_text("search.status.results_found", lang, count=count)

def create_error_message(error_type: str, lang: str = None) -> str:
    """Create error message"""
    return get_text(f"errors.{error_type}", lang)

def create_success_message(success_type: str, lang: str = None) -> str:
    """Create success message"""
    return get_text(f"success.{success_type}", lang)

def create_maintenance_message(lang: str = None) -> str:
    """Create maintenance message"""
    return get_text("bot.maintenance.message", lang)

def create_permission_denied_message(lang: str = None) -> str:
    """Create permission denied message"""
    return get_text("messages.permission_denied", lang)

def create_subscription_status_message(status: str, days_left: int, lang: str = None) -> str:
    """Create subscription status message"""
    status_text = get_text(f"user.subscription.{status}", lang)
    if days_left > 0:
        return get_text("shop.subscription.days_left", lang, days=days_left)
    return status_text

# Language detection helper
def detect_user_language(user_language_code: str) -> str:
    """Detect user language from Telegram language code"""
    if user_language_code:
        # Extract language code (e.g., 'en-US' -> 'en')
        lang_code = user_language_code.split('-')[0].lower()
        if lang_code in ['id', 'in']:
            return 'id'
        elif lang_code in ['en']:
            return 'en'
    
    # Default to Indonesian
    return 'id'