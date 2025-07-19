"""
Handlers package for RexSint Bot
Contains all message and command handlers
"""

from .start import StartHandler
from .search import SearchHandler
from .admin import AdminHandler
from .shop import ShopHandler
from .settings import SettingsHandler

# Version info
__version__ = "1.0.0"
__author__ = "RexSint Team"
__description__ = "Message and command handlers for RexSint OSINT Bot"

# Export all handler classes
__all__ = [
    "StartHandler",
    "SearchHandler", 
    "AdminHandler",
    "ShopHandler",
    "SettingsHandler"
]

# Handler registry for easy access
HANDLER_REGISTRY = {
    "start": StartHandler,
    "search": SearchHandler,
    "admin": AdminHandler,
    "shop": ShopHandler,
    "settings": SettingsHandler
}

# Handler configuration
HANDLER_CONFIG = {
    "start": {
        "description": "Handles /start command and onboarding",
        "commands": ["/start"],
        "features": ["channel_verification", "user_registration", "welcome_message"]
    },
    "search": {
        "description": "Handles all search operations",
        "commands": [],
        "features": ["osint_search", "bulk_search", "file_upload", "ai_summary"]
    },
    "admin": {
        "description": "Handles admin panel operations",
        "commands": ["/admin", "/activatetrial", "/generate", "/setnewapi"],
        "features": ["user_management", "api_management", "statistics", "broadcast"]
    },
    "shop": {
        "description": "Handles payment and subscription",
        "commands": [],
        "features": ["payment_processing", "subscription_management", "qris_payment"]
    },
    "settings": {
        "description": "Handles user settings and preferences",
        "commands": [],
        "features": ["timezone_settings", "language_settings", "preferences_reset"]
    }
}

def create_handler_instance(handler_type: str, *args, **kwargs):
    """Create handler instance by type"""
    if handler_type not in HANDLER_REGISTRY:
        raise ValueError(f"Unknown handler type: {handler_type}")
    
    handler_class = HANDLER_REGISTRY[handler_type]
    return handler_class(*args, **kwargs)

def create_all_handlers(db_manager, api_manager, auth_manager, config: dict) -> dict:
    """Create all handler instances"""
    handlers = {
        "start": StartHandler(db_manager, auth_manager),
        "search": SearchHandler(db_manager, api_manager),
        "admin": AdminHandler(db_manager, config),
        "shop": ShopHandler(db_manager, config),
        "settings": SettingsHandler(db_manager)
    }
    
    return handlers

def get_handler_info(handler_type: str = None) -> dict:
    """Get handler information"""
    if handler_type:
        return HANDLER_CONFIG.get(handler_type, {})
    return HANDLER_CONFIG

def get_all_commands() -> list:
    """Get all registered commands"""
    commands = []
    for handler_info in HANDLER_CONFIG.values():
        commands.extend(handler_info.get("commands", []))
    return commands

def get_handler_by_command(command: str) -> str:
    """Get handler type by command"""
    for handler_type, handler_info in HANDLER_CONFIG.items():
        if command in handler_info.get("commands", []):
            return handler_type
    return None

def validate_handlers() -> dict:
    """Validate all handlers"""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check if all handlers are importable
    for handler_name, handler_class in HANDLER_REGISTRY.items():
        try:
            # Try to get class methods
            required_methods = ["handle_callback"]
            for method in required_methods:
                if not hasattr(handler_class, method):
                    validation_result["warnings"].append(
                        f"{handler_name} handler missing method: {method}"
                    )
        except Exception as e:
            validation_result["errors"].append(
                f"Error validating {handler_name} handler: {e}"
            )
            validation_result["valid"] = False
    
    return validation_result

def get_handlers_summary() -> dict:
    """Get summary of all handlers"""
    return {
        "total_handlers": len(HANDLER_REGISTRY),
        "total_commands": len(get_all_commands()),
        "handlers": list(HANDLER_REGISTRY.keys()),
        "commands": get_all_commands(),
        "version": __version__
    }

# Handler factory class
class HandlerFactory:
    """Factory for creating handler instances"""
    
    def __init__(self, db_manager, api_manager, auth_manager, config: dict):
        self.db_manager = db_manager
        self.api_manager = api_manager
        self.auth_manager = auth_manager
        self.config = config
        self._handlers = {}
    
    def get_handler(self, handler_type: str):
        """Get handler instance (lazy loading)"""
        if handler_type not in self._handlers:
            self._handlers[handler_type] = self._create_handler(handler_type)
        return self._handlers[handler_type]
    
    def _create_handler(self, handler_type: str):
        """Create handler instance"""
        if handler_type == "start":
            return StartHandler(self.db_manager, self.auth_manager)
        elif handler_type == "search":
            return SearchHandler(self.db_manager, self.api_manager)
        elif handler_type == "admin":
            return AdminHandler(self.db_manager, self.config)
        elif handler_type == "shop":
            return ShopHandler(self.db_manager, self.config)
        elif handler_type == "settings":
            return SettingsHandler(self.db_manager)
        else:
            raise ValueError(f"Unknown handler type: {handler_type}")
    
    def get_all_handlers(self) -> dict:
        """Get all handler instances"""
        for handler_type in HANDLER_REGISTRY.keys():
            self.get_handler(handler_type)
        return self._handlers
    
    def reload_handler(self, handler_type: str):
        """Reload specific handler"""
        if handler_type in self._handlers:
            del self._handlers[handler_type]
        return self.get_handler(handler_type)

# Handler decorators
def admin_required(func):
    """Decorator to require admin access"""
    async def wrapper(self, update, context):
        user_id = update.effective_user.id
        if not self.db_manager.is_admin(user_id):
            await update.message.reply_text(
                "❌ Akses ditolak. Anda bukan admin.",
                parse_mode='Markdown'
            )
            return
        return await func(self, update, context)
    return wrapper

def channel_member_required(func):
    """Decorator to require channel membership"""
    async def wrapper(self, update, context):
        user_id = update.effective_user.id
        # Check channel membership logic here
        return await func(self, update, context)
    return wrapper

def trial_activated_required(func):
    """Decorator to require trial activation"""
    async def wrapper(self, update, context):
        user_id = update.effective_user.id
        user_data = self.db_manager.get_user(user_id)
        
        if not user_data or not user_data.get('is_trial_activated'):
            await update.message.reply_text(
                "❌ Fitur pencarian belum aktif. Silakan lakukan aktivasi di menu 🛒 Toko.",
                parse_mode='Markdown'
            )
            return
        return await func(self, update, context)
    return wrapper

def rate_limit(max_calls: int = 10, window_seconds: int = 60):
    """Decorator for rate limiting"""
    def decorator(func):
        async def wrapper(self, update, context):
            # Rate limiting logic here
            return await func(self, update, context)
        return wrapper
    return decorator

# Handler utilities
def extract_user_info(update):
    """Extract user information from update"""
    user = update.effective_user
    return {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "language_code": user.language_code
    }

def extract_chat_info(update):
    """Extract chat information from update"""
    chat = update.effective_chat
    return {
        "chat_id": chat.id,
        "chat_type": chat.type,
        "chat_title": chat.title
    }

def extract_message_info(update):
    """Extract message information from update"""
    message = update.effective_message
    if not message:
        return {}
    
    return {
        "message_id": message.message_id,
        "text": message.text,
        "date": message.date,
        "reply_to_message": message.reply_to_message
    }

def log_handler_activity(handler_name: str, user_id: int, action: str, details: str = ""):
    """Log handler activity"""
    import logging
    logger = logging.getLogger(f"handlers.{handler_name}")
    logger.info(f"User {user_id} - {action}: {details}")

def create_handler_context(update, context, handler_name: str) -> dict:
    """Create handler context with common information"""
    return {
        "handler": handler_name,
        "user": extract_user_info(update),
        "chat": extract_chat_info(update),
        "message": extract_message_info(update),
        "context": context
    }

# Module initialization
import logging

logger = logging.getLogger(__name__)

# Validate handlers on import
try:
    validation = validate_handlers()
    if not validation["valid"]:
        logger.error("Handlers validation failed:")
        for error in validation["errors"]:
            logger.error(f"  - {error}")
    
    if validation["warnings"]:
        for warning in validation["warnings"]:
            logger.warning(f"  - {warning}")

except Exception as e:
    logger.error(f"Error during handlers validation: {e}")

logger.info(f"Handlers package initialized (v{__version__})")