"""
Models package for RexSint Bot
Contains data models and repositories for the bot
"""
from datetime import datetime
# Import all models and enums
from .user import (
    User,
    UserStatus,
    SubscriptionType,
    UserRepository
)

from .bot_status import (
    BotStatus,
    BotMode,
    APITokenStatus,
    BotStatusRepository,
    BotStatusMonitor
)

# Version info
__version__ = "1.0.0"
__author__ = "RexSint Team"

# Export all public classes
__all__ = [
    # User models
    "User",
    "UserStatus", 
    "SubscriptionType",
    "UserRepository",
    
    # Bot Status models
    "BotStatus",
    "BotMode",
    "APITokenStatus", 
    "BotStatusRepository",
    "BotStatusMonitor",
]

# Model factory functions
def create_user_repository(db_manager):
    """Create user repository with database manager"""
    return UserRepository(db_manager)

def create_bot_status_repository(db_manager):
    """Create bot status repository with database manager"""
    return BotStatusRepository(db_manager)

def create_bot_status_monitor(db_manager):
    """Create bot status monitor with database manager"""
    bot_status_repo = create_bot_status_repository(db_manager)
    return BotStatusMonitor(bot_status_repo)

# Model validation functions
def validate_user_data(user_data: dict) -> bool:
    """Validate user data dictionary"""
    required_fields = ['user_id', 'first_name']
    return all(field in user_data for field in required_fields)

def validate_bot_status_data(status_data: dict) -> bool:
    """Validate bot status data dictionary"""
    required_fields = ['id']
    return all(field in status_data for field in required_fields)

# Model helper functions
def get_user_status_display(status: UserStatus, lang: str = 'id') -> str:
    """Get localized user status display"""
    if lang == 'id':
        status_map = {
            UserStatus.INACTIVE: 'Tidak Aktif',
            UserStatus.TRIAL: 'Trial',
            UserStatus.ACTIVE: 'Aktif',
            UserStatus.EXPIRED: 'Berakhir',
            UserStatus.BLOCKED: 'Diblokir'
        }
    else:
        status_map = {
            UserStatus.INACTIVE: 'Inactive',
            UserStatus.TRIAL: 'Trial',
            UserStatus.ACTIVE: 'Active',
            UserStatus.EXPIRED: 'Expired',
            UserStatus.BLOCKED: 'Blocked'
        }
    
    return status_map.get(status, 'Unknown')

def get_bot_mode_display(mode: BotMode, lang: str = 'id') -> str:
    """Get localized bot mode display"""
    if lang == 'id':
        mode_map = {
            BotMode.NORMAL: '🟢 Normal',
            BotMode.MAINTENANCE: '🔴 Maintenance',
            BotMode.LIMITED: '🟡 Terbatas',
            BotMode.EMERGENCY: '🚨 Darurat'
        }
    else:
        mode_map = {
            BotMode.NORMAL: '🟢 Normal',
            BotMode.MAINTENANCE: '🔴 Maintenance',
            BotMode.LIMITED: '🟡 Limited',
            BotMode.EMERGENCY: '🚨 Emergency'
        }
    
    return mode_map.get(mode, 'Unknown')

def get_subscription_type_display(sub_type: SubscriptionType, lang: str = 'id') -> str:
    """Get localized subscription type display"""
    if lang == 'id':
        type_map = {
            SubscriptionType.TRIAL: 'Trial',
            SubscriptionType.WEEK: '1 Minggu',
            SubscriptionType.MONTH: '1 Bulan',
            SubscriptionType.YEAR: '1 Tahun',
            SubscriptionType.LIFETIME: 'Selamanya'
        }
    else:
        type_map = {
            SubscriptionType.TRIAL: 'Trial',
            SubscriptionType.WEEK: '1 Week',
            SubscriptionType.MONTH: '1 Month',
            SubscriptionType.YEAR: '1 Year',
            SubscriptionType.LIFETIME: 'Lifetime'
        }
    
    return type_map.get(sub_type, 'Unknown')

# Model statistics functions
def get_user_statistics_summary(user_repo: UserRepository) -> dict:
    """Get summary statistics for all users"""
    try:
        stats = user_repo.get_user_count_by_status()
        return {
            'total_users': stats.get('total', 0),
            'active_users': stats.get('active', 0),
            'blocked_users': stats.get('blocked', 0),
            'new_users_today': stats.get('new_today', 0),
            'active_percentage': (stats.get('active', 0) / max(1, stats.get('total', 1))) * 100
        }
    except Exception:
        return {}

def get_bot_health_summary(bot_status_repo: BotStatusRepository) -> dict:
    """Get bot health summary"""
    try:
        health_check = bot_status_repo.perform_health_check()
        return {
            'is_healthy': health_check.get('healthy', False),
            'health_score': health_check.get('health_score', 0),
            'mode': health_check.get('mode', 'unknown'),
            'uptime_hours': health_check.get('uptime_hours', 0),
            'requests_remaining': health_check.get('requests_remaining', 0),
            'error_count': health_check.get('error_count', 0)
        }
    except Exception:
        return {}

# Model export/import functions
def export_all_models_data(db_manager) -> dict:
    """Export all models data for backup"""
    try:
        user_repo = create_user_repository(db_manager)
        bot_status_repo = create_bot_status_repository(db_manager)
        
        return {
            'users': {
                'statistics': get_user_statistics_summary(user_repo),
                'export_timestamp': datetime.now().isoformat()
            },
            'bot_status': bot_status_repo.export_status_data(),
            'metadata': {
                'version': __version__,
                'export_date': datetime.now().isoformat(),
                'model_count': 2
            }
        }
    except Exception as e:
        return {'error': str(e)}

def import_all_models_data(db_manager, data: dict) -> bool:
    """Import all models data from backup"""
    try:
        if 'bot_status' in data:
            bot_status_repo = create_bot_status_repository(db_manager)
            bot_status_repo.import_status_data(data['bot_status'])
        
        # User data import would be handled by UserRepository
        # if 'users' in data:
        #     user_repo = create_user_repository(db_manager)
        #     user_repo.import_users_data(data['users'])
        
        return True
    except Exception:
        return False

# Model configuration
MODEL_CONFIG = {
    'default_timezone': 'Asia/Jakarta',
    'default_language': 'id',
    'default_token_balance': 10,
    'trial_duration_days': 7,
    'max_api_requests': 99,
    'max_token_age_days': 7,
    'max_error_count': 10,
    'health_check_interval': 300,  # 5 minutes
    'maintenance_check_interval': 60  # 1 minute
}

# Model validation schemas (for future use with pydantic or similar)
USER_SCHEMA = {
    'user_id': int,
    'first_name': str,
    'username': (str, type(None)),
    'token_balance': int,
    'is_trial_activated': bool,
    'timezone': str,
    'language_code': str,
    'is_blocked': bool,
    'total_requests': int,
    'file_requests': int
}

BOT_STATUS_SCHEMA = {
    'id': int,
    'active_api_token': (str, type(None)),
    'api_request_count': int,
    'is_maintenance': bool,
    'error_count': int
}

# Model event handlers (for future use)
class ModelEventHandler:
    """Base class for model event handlers"""
    
    def on_user_created(self, user: User):
        """Called when a new user is created"""
        pass
    
    def on_user_updated(self, user: User):
        """Called when a user is updated"""
        pass
    
    def on_user_blocked(self, user: User):
        """Called when a user is blocked"""
        pass
    
    def on_bot_maintenance_mode_changed(self, bot_status: BotStatus):
        """Called when bot maintenance mode changes"""
        pass
    
    def on_api_token_updated(self, bot_status: BotStatus):
        """Called when API token is updated"""
        pass
    
    def on_health_check_failed(self, bot_status: BotStatus):
        """Called when health check fails"""
        pass

# Import datetime for timestamp functions
from datetime import datetime

# Model constants
MAX_USERNAME_LENGTH = 50
MAX_FIRST_NAME_LENGTH = 100
MAX_API_TOKEN_LENGTH = 200
MAX_ERROR_MESSAGE_LENGTH = 500
MAX_TIMEZONE_LENGTH = 50
MAX_LANGUAGE_CODE_LENGTH = 5

# Model utility functions
def truncate_string(text: str, max_length: int) -> str:
    """Truncate string to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def validate_timezone(timezone: str) -> bool:
    """Validate timezone string"""
    try:
        import pytz
        pytz.timezone(timezone)
        return True
    except:
        return False

def validate_language_code(lang_code: str) -> bool:
    """Validate language code"""
    return lang_code in ['id', 'en']

def sanitize_user_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove dangerous characters
    import re
    cleaned = re.sub(r'[<>"\']', '', text)
    return cleaned.strip()

# Model error classes
class ModelError(Exception):
    """Base model error"""
    pass

class UserValidationError(ModelError):
    """User validation error"""
    pass

class BotStatusError(ModelError):
    """Bot status error"""
    pass

class RepositoryError(ModelError):
    """Repository operation error"""
    pass