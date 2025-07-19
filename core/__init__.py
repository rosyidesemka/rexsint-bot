"""
Core package for RexSint Bot
Contains essential components for bot functionality
"""

from .database import DatabaseManager
from .api_manager import APIManager
from .auth import AuthManager
from .utils import (
    load_config,
    setup_logging,
    get_main_keyboard,
    get_search_keyboard,
    get_settings_inline_keyboard,
    get_timezone_keyboard,
    get_language_keyboard,
    get_info_menu_keyboard,
    get_shop_keyboard,
    get_admin_keyboard,
    format_user_info,
    format_datetime,
    format_currency,
    validate_user_input,
    parse_file_content,
    sanitize_filename,
    generate_report_filename,
    log_search_activity,
    create_error_message,
    create_success_message,
    create_warning_message,
    create_info_message,
    get_maintenance_message,
    get_rate_limit_message,
    get_faq_data,
    get_system_info,
    validate_admin_command,
    mask_sensitive_data,
    init_directories,
    auto_cleanup
)

# Version info
__version__ = "1.0.0"
__author__ = "RexSint Team"
__description__ = "Core components for RexSint OSINT Bot"

# Export all public classes and functions
__all__ = [
    # Core managers
    "DatabaseManager",
    "APIManager", 
    "AuthManager",
    
    # Configuration and logging
    "load_config",
    "setup_logging",
    
    # UI components
    "get_main_keyboard",
    "get_search_keyboard",
    "get_settings_inline_keyboard",
    "get_timezone_keyboard",
    "get_language_keyboard",
    "get_info_menu_keyboard",
    "get_shop_keyboard",
    "get_admin_keyboard",
    
    # Formatting utilities
    "format_user_info",
    "format_datetime",
    "format_currency",
    
    # Validation and parsing
    "validate_user_input",
    "parse_file_content",
    "sanitize_filename",
    "generate_report_filename",
    
    # Logging and monitoring
    "log_search_activity",
    "get_system_info",
    "validate_admin_command",
    "mask_sensitive_data",
    
    # Message creation
    "create_error_message",
    "create_success_message", 
    "create_warning_message",
    "create_info_message",
    "get_maintenance_message",
    "get_rate_limit_message",
    "get_faq_data",
    
    # System utilities
    "init_directories",
    "auto_cleanup"
]

# Core configuration
CORE_CONFIG = {
    "database": {
        "default_name": "rex_sint_bot.db",
        "backup_enabled": True,
        "auto_vacuum": True
    },
    "api": {
        "timeout": 30,
        "retries": 3,
        "rate_limit": 10
    },
    "auth": {
        "channel_check_enabled": True,
        "admin_required": True
    },
    "logging": {
        "level": "INFO",
        "file": "rexsint_bot.log",
        "max_size": "10MB",
        "backup_count": 5
    },
    "cache": {
        "enabled": True,
        "ttl": 3600,
        "max_size": 1000
    }
}

# Component factory functions
def create_database_manager(config: dict = None) -> DatabaseManager:
    """Create DatabaseManager instance"""
    db_config = config.get("Database", {}) if config else {}
    db_name = db_config.get("db_name", CORE_CONFIG["database"]["default_name"])
    return DatabaseManager(db_name)

def create_api_manager(config: dict = None) -> APIManager:
    """Create APIManager instance"""
    if not config:
        raise ValueError("Configuration required for APIManager")
    return APIManager(config)

def create_auth_manager(config: dict = None) -> AuthManager:
    """Create AuthManager instance"""
    if not config:
        raise ValueError("Configuration required for AuthManager")
    return AuthManager(config)

def create_bot_components(config_file: str = "config.ini") -> dict:
    """Create all bot components with configuration"""
    # Load configuration
    config = load_config(config_file)
    
    if not config:
        raise ValueError(f"Could not load configuration from {config_file}")
    
    # Setup logging
    setup_logging()
    
    # Initialize directories
    init_directories()
    
    # Create components
    components = {
        "config": config,
        "database_manager": create_database_manager(config),
        "api_manager": create_api_manager(config),
        "auth_manager": create_auth_manager(config)
    }
    
    return components

def validate_core_dependencies() -> dict:
    """Validate core dependencies and configuration"""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check required directories
    required_dirs = ["logs", "assets", "temp", "reports"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            validation_result["warnings"].append(f"Directory missing: {directory}")
    
    # Check configuration file
    if not os.path.exists("config.ini"):
        validation_result["errors"].append("Configuration file (config.ini) not found")
        validation_result["valid"] = False
    
    # Check required assets
    required_assets = ["assets/database_list.html", "assets/log_history.json"]
    for asset in required_assets:
        if not os.path.exists(asset):
            validation_result["warnings"].append(f"Asset file missing: {asset}")
    
    return validation_result

def get_core_info() -> dict:
    """Get core package information"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": len(__all__),
        "config": CORE_CONFIG
    }

# Module initialization
import os
import logging

# Initialize logging on import
logger = logging.getLogger(__name__)

# Validate dependencies on import
try:
    validation = validate_core_dependencies()
    if not validation["valid"]:
        logger.error("Core validation failed:")
        for error in validation["errors"]:
            logger.error(f"  - {error}")
    
    if validation["warnings"]:
        for warning in validation["warnings"]:
            logger.warning(f"  - {warning}")
        
except Exception as e:
    logger.error(f"Error during core validation: {e}")

logger.info(f"Core package initialized (v{__version__})")