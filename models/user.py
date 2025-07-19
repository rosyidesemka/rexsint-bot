"""
User Model for RexSint Bot
Defines user data structure and operations
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

class UserStatus(Enum):
    """User status enumeration"""
    INACTIVE = "inactive"
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    BLOCKED = "blocked"

class SubscriptionType(Enum):
    """Subscription type enumeration"""
    TRIAL = "trial"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    LIFETIME = "lifetime"

@dataclass
class User:
    """User data model"""
    user_id: int
    first_name: str
    username: Optional[str] = None
    registration_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    token_balance: int = 0
    api_token: Optional[str] = None
    is_trial_activated: bool = False
    timezone: str = "Asia/Jakarta"
    language_code: str = "id"
    is_blocked: bool = False
    total_requests: int = 0
    file_requests: int = 0
    
    def __post_init__(self):
        """Initialize default values after object creation"""
        if self.registration_date is None:
            self.registration_date = datetime.now()
        
        if self.subscription_end_date is None and self.is_trial_activated:
            # Set trial period to 7 days
            self.subscription_end_date = datetime.now() + timedelta(days=7)
    
    @property
    def status(self) -> UserStatus:
        """Get user status"""
        if self.is_blocked:
            return UserStatus.BLOCKED
        
        if not self.is_trial_activated:
            return UserStatus.INACTIVE
        
        if self.subscription_end_date is None:
            return UserStatus.TRIAL
        
        if datetime.now() > self.subscription_end_date:
            return UserStatus.EXPIRED
        
        return UserStatus.ACTIVE
    
    @property
    def is_subscription_active(self) -> bool:
        """Check if subscription is active"""
        if not self.is_trial_activated:
            return False
        
        if self.subscription_end_date is None:
            return False
        
        return datetime.now() <= self.subscription_end_date
    
    @property
    def subscription_days_left(self) -> int:
        """Get days left in subscription"""
        if not self.is_subscription_active:
            return 0
        
        if self.subscription_end_date is None:
            return 0
        
        delta = self.subscription_end_date - datetime.now()
        return max(0, delta.days)
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium access"""
        return self.status in [UserStatus.ACTIVE, UserStatus.TRIAL]
    
    @property
    def can_search(self) -> bool:
        """Check if user can perform searches"""
        return (
            self.status in [UserStatus.ACTIVE, UserStatus.TRIAL] and
            self.token_balance > 0 and
            not self.is_blocked
        )
    
    @property
    def display_name(self) -> str:
        """Get user display name"""
        if self.username:
            return f"{self.first_name} (@{self.username})"
        return self.first_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'username': self.username,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'token_balance': self.token_balance,
            'api_token': self.api_token,
            'is_trial_activated': self.is_trial_activated,
            'timezone': self.timezone,
            'language_code': self.language_code,
            'is_blocked': self.is_blocked,
            'total_requests': self.total_requests,
            'file_requests': self.file_requests,
            'status': self.status.value,
            'subscription_days_left': self.subscription_days_left,
            'is_premium': self.is_premium,
            'can_search': self.can_search
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        user = cls(
            user_id=data['user_id'],
            first_name=data['first_name'],
            username=data.get('username'),
            token_balance=data.get('token_balance', 0),
            api_token=data.get('api_token'),
            is_trial_activated=data.get('is_trial_activated', False),
            timezone=data.get('timezone', 'Asia/Jakarta'),
            language_code=data.get('language_code', 'id'),
            is_blocked=data.get('is_blocked', False),
            total_requests=data.get('total_requests', 0),
            file_requests=data.get('file_requests', 0)
        )
        
        # Handle datetime fields
        if data.get('registration_date'):
            try:
                user.registration_date = datetime.fromisoformat(data['registration_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                user.registration_date = datetime.now()
        
        if data.get('subscription_end_date'):
            try:
                user.subscription_end_date = datetime.fromisoformat(data['subscription_end_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                user.subscription_end_date = None
        
        return user
    
    def activate_trial(self, duration_days: int = 7) -> bool:
        """Activate trial for user"""
        try:
            self.is_trial_activated = True
            self.subscription_end_date = datetime.now() + timedelta(days=duration_days)
            if self.token_balance <= 0:
                self.token_balance = 10  # Give initial tokens
            return True
        except Exception as e:
            logging.error(f"Error activating trial for user {self.user_id}: {e}")
            return False
    
    def extend_subscription(self, duration_days: int, bonus_tokens: int = 0) -> bool:
        """Extend user subscription"""
        try:
            if self.subscription_end_date is None or self.subscription_end_date < datetime.now():
                # If expired or no subscription, start from now
                self.subscription_end_date = datetime.now() + timedelta(days=duration_days)
            else:
                # If active, extend from current end date
                self.subscription_end_date += timedelta(days=duration_days)
            
            self.token_balance += bonus_tokens
            self.is_trial_activated = True
            return True
        except Exception as e:
            logging.error(f"Error extending subscription for user {self.user_id}: {e}")
            return False
    
    def consume_token(self, amount: int = 1) -> bool:
        """Consume search tokens"""
        if self.token_balance >= amount:
            self.token_balance -= amount
            return True
        return False
    
    def add_tokens(self, amount: int) -> bool:
        """Add tokens to user balance"""
        try:
            self.token_balance += amount
            return True
        except Exception as e:
            logging.error(f"Error adding tokens to user {self.user_id}: {e}")
            return False
    
    def increment_requests(self, is_file_request: bool = False) -> None:
        """Increment request counters"""
        self.total_requests += 1
        if is_file_request:
            self.file_requests += 1
    
    def block_user(self, blocked: bool = True) -> bool:
        """Block or unblock user"""
        try:
            self.is_blocked = blocked
            return True
        except Exception as e:
            logging.error(f"Error blocking user {self.user_id}: {e}")
            return False
    
    def update_language(self, language_code: str) -> bool:
        """Update user language"""
        try:
            if language_code in ['id', 'en']:
                self.language_code = language_code
                return True
            return False
        except Exception as e:
            logging.error(f"Error updating language for user {self.user_id}: {e}")
            return False
    
    def update_timezone(self, timezone: str) -> bool:
        """Update user timezone"""
        try:
            import pytz
            # Validate timezone
            pytz.timezone(timezone)
            self.timezone = timezone
            return True
        except Exception as e:
            logging.error(f"Error updating timezone for user {self.user_id}: {e}")
            return False
    
    def get_subscription_info(self) -> Dict[str, Any]:
        """Get subscription information"""
        return {
            'status': self.status.value,
            'is_active': self.is_subscription_active,
            'days_left': self.subscription_days_left,
            'end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'is_premium': self.is_premium,
            'can_search': self.can_search,
            'token_balance': self.token_balance
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get user usage statistics"""
        return {
            'total_requests': self.total_requests,
            'file_requests': self.file_requests,
            'search_requests': self.total_requests - self.file_requests,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'days_since_registration': (datetime.now() - self.registration_date).days if self.registration_date else 0,
            'average_requests_per_day': self.total_requests / max(1, (datetime.now() - self.registration_date).days) if self.registration_date else 0
        }
    
    def validate_permissions(self, action: str) -> Dict[str, Any]:
        """Validate user permissions for specific actions"""
        permissions = {
            'can_search': self.can_search,
            'can_bulk_search': self.is_premium,
            'can_ip_search': self.is_premium,
            'can_advanced_search': self.is_premium,
            'can_download_reports': self.is_premium,
            'can_use_ai_summary': self.is_premium
        }
        
        result = {
            'allowed': permissions.get(action, False),
            'reason': ''
        }
        
        if not result['allowed']:
            if self.is_blocked:
                result['reason'] = 'User is blocked'
            elif not self.is_trial_activated:
                result['reason'] = 'Trial not activated'
            elif not self.is_subscription_active:
                result['reason'] = 'Subscription expired'
            elif self.token_balance <= 0:
                result['reason'] = 'No tokens remaining'
            elif action in ['can_bulk_search', 'can_ip_search', 'can_advanced_search'] and not self.is_premium:
                result['reason'] = 'Premium feature requires active subscription'
        
        return result
    
    def get_localized_info(self) -> Dict[str, str]:
        """Get localized user information"""
        lang = self.language_code
        
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
        
        return {
            'status': status_map.get(self.status, 'Unknown'),
            'language': '🇮🇩 Indonesia' if lang == 'id' else '🇬🇧 English',
            'timezone': self.timezone
        }
    
    def __str__(self) -> str:
        """String representation of user"""
        return f"User(id={self.user_id}, name={self.first_name}, status={self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"User(user_id={self.user_id}, first_name='{self.first_name}', "
            f"username='{self.username}', status='{self.status.value}', "
            f"token_balance={self.token_balance}, is_premium={self.is_premium})"
        )

class UserRepository:
    """Repository for user operations"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """Create a new user"""
        try:
            user = User.from_dict(user_data)
            
            # Add user to database
            success = self.db_manager.add_user(
                user.user_id,
                user.first_name,
                user.username,
                user.api_token
            )
            
            if success:
                return user
            return None
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            user_data = self.db_manager.get_user(user_id)
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def update_user(self, user: User) -> bool:
        """Update user in database"""
        try:
            return self.db_manager.update_user(
                user.user_id,
                first_name=user.first_name,
                username=user.username,
                subscription_end_date=user.subscription_end_date,
                token_balance=user.token_balance,
                api_token=user.api_token,
                is_trial_activated=user.is_trial_activated,
                timezone=user.timezone,
                language_code=user.language_code,
                is_blocked=user.is_blocked,
                total_requests=user.total_requests,
                file_requests=user.file_requests
            )
        except Exception as e:
            self.logger.error(f"Error updating user {user.user_id}: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user from database"""
        try:
            # Note: This would require implementing delete functionality in DatabaseManager
            # For now, we'll just block the user
            return self.db_manager.block_user(user_id, True)
        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    def get_users_by_status(self, status: UserStatus) -> List[User]:
        """Get users by status"""
        try:
            # This would require more complex database queries
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.error(f"Error getting users by status {status}: {e}")
            return []
    
    def get_premium_users(self) -> List[User]:
        """Get all premium users"""
        try:
            # This would require complex database queries
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.error(f"Error getting premium users: {e}")
            return []
    
    def get_user_count_by_status(self) -> Dict[str, int]:
        """Get user count by status"""
        try:
            stats = self.db_manager.get_user_stats()
            return {
                'total': stats.get('total_users', 0),
                'active': stats.get('active_users', 0),
                'blocked': stats.get('blocked_users', 0),
                'new_today': stats.get('new_users_today', 0)
            }
        except Exception as e:
            self.logger.error(f"Error getting user count by status: {e}")
            return {}