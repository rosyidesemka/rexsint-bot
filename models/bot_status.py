"""
Bot Status Model for RexSint Bot
Manages bot operational status and API token rotation
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class BotMode(Enum):
    """Bot operational modes"""
    NORMAL = "normal"
    MAINTENANCE = "maintenance"
    LIMITED = "limited"
    EMERGENCY = "emergency"

class APITokenStatus(Enum):
    """API token status"""
    ACTIVE = "active"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    INVALID = "invalid"

@dataclass
class BotStatus:
    """Bot status data model"""
    id: int = 1
    active_api_token: Optional[str] = None
    api_request_count: int = 0
    api_activation_date: Optional[datetime] = None
    is_maintenance: bool = False
    last_health_check: Optional[datetime] = None
    uptime_start: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.api_activation_date is None:
            self.api_activation_date = datetime.now()
        
        if self.uptime_start is None:
            self.uptime_start = datetime.now()
    
    @property
    def mode(self) -> BotMode:
        """Get current bot mode"""
        if self.is_maintenance:
            return BotMode.MAINTENANCE
        
        if self.error_count > 10:
            return BotMode.EMERGENCY
        
        if self.api_token_status == APITokenStatus.EXPIRING:
            return BotMode.LIMITED
        
        return BotMode.NORMAL
    
    @property
    def api_token_status(self) -> APITokenStatus:
        """Get API token status"""
        if not self.active_api_token:
            return APITokenStatus.INVALID
        
        if self.api_request_count >= 99:
            return APITokenStatus.EXPIRED
        
        if self.api_activation_date:
            days_active = (datetime.now() - self.api_activation_date).days
            if days_active >= 7:
                return APITokenStatus.EXPIRED
            elif days_active >= 6:
                return APITokenStatus.EXPIRING
        
        return APITokenStatus.ACTIVE
    
    @property
    def is_operational(self) -> bool:
        """Check if bot is operational"""
        return (
            not self.is_maintenance and
            self.active_api_token is not None and
            self.api_token_status in [APITokenStatus.ACTIVE, APITokenStatus.EXPIRING]
        )
    
    @property
    def requests_remaining(self) -> int:
        """Get remaining API requests"""
        return max(0, 99 - self.api_request_count)
    
    @property
    def token_age_days(self) -> int:
        """Get token age in days"""
        if self.api_activation_date:
            return (datetime.now() - self.api_activation_date).days
        return 0
    
    @property
    def uptime_hours(self) -> float:
        """Get uptime in hours"""
        if self.uptime_start:
            delta = datetime.now() - self.uptime_start
            return delta.total_seconds() / 3600
        return 0
    
    @property
    def health_score(self) -> float:
        """Calculate health score (0-100)"""
        score = 100.0
        
        # Deduct for maintenance mode
        if self.is_maintenance:
            score -= 50
        
        # Deduct for API token issues
        if self.api_token_status == APITokenStatus.EXPIRED:
            score -= 30
        elif self.api_token_status == APITokenStatus.EXPIRING:
            score -= 10
        elif self.api_token_status == APITokenStatus.INVALID:
            score -= 40
        
        # Deduct for errors
        if self.error_count > 0:
            score -= min(20, self.error_count * 2)
        
        # Deduct for high API usage
        usage_ratio = self.api_request_count / 99
        if usage_ratio > 0.8:
            score -= 15
        elif usage_ratio > 0.6:
            score -= 10
        
        return max(0, score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'active_api_token': self.active_api_token,
            'api_request_count': self.api_request_count,
            'api_activation_date': self.api_activation_date.isoformat() if self.api_activation_date else None,
            'is_maintenance': self.is_maintenance,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'uptime_start': self.uptime_start.isoformat() if self.uptime_start else None,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None,
            'mode': self.mode.value,
            'api_token_status': self.api_token_status.value,
            'is_operational': self.is_operational,
            'requests_remaining': self.requests_remaining,
            'token_age_days': self.token_age_days,
            'uptime_hours': self.uptime_hours,
            'health_score': self.health_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BotStatus':
        """Create from dictionary"""
        bot_status = cls(
            id=data.get('id', 1),
            active_api_token=data.get('active_api_token'),
            api_request_count=data.get('api_request_count', 0),
            is_maintenance=data.get('is_maintenance', False),
            error_count=data.get('error_count', 0),
            last_error=data.get('last_error')
        )
        
        # Handle datetime fields
        datetime_fields = [
            'api_activation_date', 'last_health_check', 
            'uptime_start', 'last_error_time'
        ]
        
        for field in datetime_fields:
            if data.get(field):
                try:
                    setattr(bot_status, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                except (ValueError, AttributeError):
                    setattr(bot_status, field, None)
        
        return bot_status
    
    def set_maintenance_mode(self, maintenance: bool, reason: str = None) -> bool:
        """Set maintenance mode"""
        try:
            self.is_maintenance = maintenance
            if maintenance and reason:
                self.last_error = f"Maintenance: {reason}"
                self.last_error_time = datetime.now()
            return True
        except Exception as e:
            logging.error(f"Error setting maintenance mode: {e}")
            return False
    
    def update_api_token(self, new_token: str) -> bool:
        """Update API token"""
        try:
            self.active_api_token = new_token
            self.api_request_count = 0
            self.api_activation_date = datetime.now()
            self.is_maintenance = False
            return True
        except Exception as e:
            logging.error(f"Error updating API token: {e}")
            return False
    
    def increment_request_count(self) -> bool:
        """Increment API request count"""
        try:
            self.api_request_count += 1
            
            # Check if we need to enter maintenance mode
            if self.api_request_count >= 99:
                self.set_maintenance_mode(True, "API request limit reached")
            
            return True
        except Exception as e:
            logging.error(f"Error incrementing request count: {e}")
            return False
    
    def log_error(self, error_message: str) -> bool:
        """Log an error"""
        try:
            self.error_count += 1
            self.last_error = error_message
            self.last_error_time = datetime.now()
            
            # Enter emergency mode if too many errors
            if self.error_count > 10:
                self.set_maintenance_mode(True, "Too many errors")
            
            return True
        except Exception as e:
            logging.error(f"Error logging error: {e}")
            return False
    
    def clear_errors(self) -> bool:
        """Clear error count"""
        try:
            self.error_count = 0
            self.last_error = None
            self.last_error_time = None
            return True
        except Exception as e:
            logging.error(f"Error clearing errors: {e}")
            return False
    
    def update_health_check(self) -> bool:
        """Update health check timestamp"""
        try:
            self.last_health_check = datetime.now()
            return True
        except Exception as e:
            logging.error(f"Error updating health check: {e}")
            return False
    
    def restart_bot(self) -> bool:
        """Restart bot (reset uptime and clear errors)"""
        try:
            self.uptime_start = datetime.now()
            self.error_count = 0
            self.last_error = None
            self.last_error_time = None
            self.is_maintenance = False
            return True
        except Exception as e:
            logging.error(f"Error restarting bot: {e}")
            return False
    
    def get_status_summary(self, lang: str = 'id') -> Dict[str, str]:
        """Get localized status summary"""
        if lang == 'id':
            mode_map = {
                BotMode.NORMAL: '🟢 Normal',
                BotMode.MAINTENANCE: '🔴 Maintenance',
                BotMode.LIMITED: '🟡 Terbatas',
                BotMode.EMERGENCY: '🚨 Darurat'
            }
            
            token_status_map = {
                APITokenStatus.ACTIVE: '🟢 Aktif',
                APITokenStatus.EXPIRING: '🟡 Hampir Habis',
                APITokenStatus.EXPIRED: '🔴 Habis',
                APITokenStatus.INVALID: '❌ Tidak Valid'
            }
        else:
            mode_map = {
                BotMode.NORMAL: '🟢 Normal',
                BotMode.MAINTENANCE: '🔴 Maintenance',
                BotMode.LIMITED: '🟡 Limited',
                BotMode.EMERGENCY: '🚨 Emergency'
            }
            
            token_status_map = {
                APITokenStatus.ACTIVE: '🟢 Active',
                APITokenStatus.EXPIRING: '🟡 Expiring',
                APITokenStatus.EXPIRED: '🔴 Expired',
                APITokenStatus.INVALID: '❌ Invalid'
            }
        
        return {
            'mode': mode_map.get(self.mode, 'Unknown'),
            'token_status': token_status_map.get(self.api_token_status, 'Unknown'),
            'operational': '✅ Ya' if self.is_operational else '❌ Tidak' if lang == 'id' else '✅ Yes' if self.is_operational else '❌ No'
        }
    
    def get_detailed_status(self, lang: str = 'id') -> str:
        """Get detailed status message"""
        summary = self.get_status_summary(lang)
        
        if lang == 'id':
            message = f"""
🤖 **Status Bot Detail**

⚡ **Mode:** {summary['mode']}
🔑 **Token API:** {summary['token_status']}
🔧 **Operasional:** {summary['operational']}

📊 **Statistik:**
• Request: {self.api_request_count}/99
• Sisa: {self.requests_remaining}
• Umur Token: {self.token_age_days} hari
• Uptime: {self.uptime_hours:.1f} jam

🔍 **Health Score:** {self.health_score:.1f}/100

📈 **Error Count:** {self.error_count}
            """
        else:
            message = f"""
🤖 **Detailed Bot Status**

⚡ **Mode:** {summary['mode']}
🔑 **API Token:** {summary['token_status']}
🔧 **Operational:** {summary['operational']}

📊 **Statistics:**
• Requests: {self.api_request_count}/99
• Remaining: {self.requests_remaining}
• Token Age: {self.token_age_days} days
• Uptime: {self.uptime_hours:.1f} hours

🔍 **Health Score:** {self.health_score:.1f}/100

📈 **Error Count:** {self.error_count}
            """
        
        if self.last_error:
            if lang == 'id':
                message += f"\n❌ **Error Terakhir:** {self.last_error}"
                if self.last_error_time:
                    message += f"\n⏰ **Waktu Error:** {self.last_error_time.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                message += f"\n❌ **Last Error:** {self.last_error}"
                if self.last_error_time:
                    message += f"\n⏰ **Error Time:** {self.last_error_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message.strip()
    
    def get_maintenance_message(self, lang: str = 'id') -> str:
        """Get maintenance mode message"""
        if lang == 'id':
            return """
🔧 **Bot Sedang Maintenance**

⚠️ **Status:** Bot sedang dalam tahap pemeliharaan untuk meningkatkan performa dan keamanan.

🔄 **Kemungkinan Penyebab:**
• Pembaruan API token
• Maintenance rutin sistem
• Perbaikan bug atau error
• Upgrade fitur baru

⏰ **Estimasi:** 5-15 menit
📞 **Bantuan:** Hubungi admin jika maintenance berlangsung lebih dari 30 menit

Terima kasih atas kesabaran Anda!
            """
        else:
            return """
🔧 **Bot Under Maintenance**

⚠️ **Status:** Bot is currently under maintenance to improve performance and security.

🔄 **Possible Causes:**
• API token update
• Routine system maintenance
• Bug fixes or errors
• New feature upgrades

⏰ **Estimated:** 5-15 minutes
📞 **Support:** Contact admin if maintenance lasts more than 30 minutes

Thank you for your patience!
            """
    
    def check_auto_maintenance_triggers(self) -> Dict[str, bool]:
        """Check if auto-maintenance should be triggered"""
        triggers = {
            'api_limit_reached': self.api_request_count >= 99,
            'token_expired': self.api_token_status == APITokenStatus.EXPIRED,
            'too_many_errors': self.error_count > 10,
            'token_too_old': self.token_age_days >= 7
        }
        
        return triggers
    
    def should_enter_maintenance(self) -> bool:
        """Check if bot should enter maintenance mode"""
        triggers = self.check_auto_maintenance_triggers()
        return any(triggers.values())
    
    def get_maintenance_reason(self) -> str:
        """Get reason for maintenance mode"""
        triggers = self.check_auto_maintenance_triggers()
        
        if triggers['api_limit_reached']:
            return "API request limit reached (99/99)"
        elif triggers['token_expired']:
            return "API token expired"
        elif triggers['too_many_errors']:
            return f"Too many errors ({self.error_count})"
        elif triggers['token_too_old']:
            return f"Token too old ({self.token_age_days} days)"
        else:
            return "Manual maintenance mode"
    
    def __str__(self) -> str:
        """String representation"""
        return f"BotStatus(mode={self.mode.value}, operational={self.is_operational}, health={self.health_score:.1f})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"BotStatus(id={self.id}, mode={self.mode.value}, "
            f"api_requests={self.api_request_count}/99, "
            f"token_status={self.api_token_status.value}, "
            f"maintenance={self.is_maintenance}, "
            f"health_score={self.health_score:.1f})"
        )

class BotStatusRepository:
    """Repository for bot status operations"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def get_bot_status(self) -> Optional[BotStatus]:
        """Get current bot status"""
        try:
            status_data = self.db_manager.get_bot_status()
            if status_data:
                return BotStatus.from_dict(status_data)
            
            # Create default status if none exists
            return self._create_default_status()
        except Exception as e:
            self.logger.error(f"Error getting bot status: {e}")
            return None
    
    def update_bot_status(self, bot_status: BotStatus) -> bool:
        """Update bot status in database"""
        try:
            return self.db_manager.update_bot_status(
                active_api_token=bot_status.active_api_token,
                api_request_count=bot_status.api_request_count,
                api_activation_date=bot_status.api_activation_date,
                is_maintenance=bot_status.is_maintenance
            )
        except Exception as e:
            self.logger.error(f"Error updating bot status: {e}")
            return False
    
    def _create_default_status(self) -> BotStatus:
        """Create default bot status"""
        return BotStatus(
            id=1,
            active_api_token=None,
            api_request_count=0,
            api_activation_date=datetime.now(),
            is_maintenance=True,  # Start in maintenance until configured
            uptime_start=datetime.now()
        )
    
    def set_maintenance_mode(self, maintenance: bool, reason: str = None) -> bool:
        """Set maintenance mode"""
        try:
            bot_status = self.get_bot_status()
            if bot_status:
                bot_status.set_maintenance_mode(maintenance, reason)
                return self.update_bot_status(bot_status)
            return False
        except Exception as e:
            self.logger.error(f"Error setting maintenance mode: {e}")
            return False
    
    def update_api_token(self, new_token: str) -> bool:
        """Update API token"""
        try:
            bot_status = self.get_bot_status()
            if bot_status:
                bot_status.update_api_token(new_token)
                return self.update_bot_status(bot_status)
            return False
        except Exception as e:
            self.logger.error(f"Error updating API token: {e}")
            return False
    
    def increment_request_count(self) -> bool:
        """Increment API request count"""
        try:
            bot_status = self.get_bot_status()
            if bot_status:
                bot_status.increment_request_count()
                return self.update_bot_status(bot_status)
            return False
        except Exception as e:
            self.logger.error(f"Error incrementing request count: {e}")
            return False
    
    def log_error(self, error_message: str) -> bool:
        """Log an error"""
        try:
            bot_status = self.get_bot_status()
            if bot_status:
                bot_status.log_error(error_message)
                return self.update_bot_status(bot_status)
            return False
        except Exception as e:
            self.logger.error(f"Error logging error: {e}")
            return False
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            bot_status = self.get_bot_status()
            if not bot_status:
                return {'healthy': False, 'reason': 'No bot status found'}
            
            bot_status.update_health_check()
            
            # Check if maintenance is needed
            if bot_status.should_enter_maintenance() and not bot_status.is_maintenance:
                reason = bot_status.get_maintenance_reason()
                bot_status.set_maintenance_mode(True, reason)
                self.update_bot_status(bot_status)
            
            health_info = {
                'healthy': bot_status.is_operational,
                'health_score': bot_status.health_score,
                'mode': bot_status.mode.value,
                'api_token_status': bot_status.api_token_status.value,
                'requests_remaining': bot_status.requests_remaining,
                'uptime_hours': bot_status.uptime_hours,
                'error_count': bot_status.error_count,
                'maintenance_triggers': bot_status.check_auto_maintenance_triggers()
            }
            
            if not bot_status.is_operational:
                health_info['reason'] = bot_status.get_maintenance_reason()
            
            return health_info
        except Exception as e:
            self.logger.error(f"Error performing health check: {e}")
            return {'healthy': False, 'reason': f'Health check failed: {str(e)}'}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            bot_status = self.get_bot_status()
            if not bot_status:
                return {}
            
            # Get system info
            import psutil
            import platform
            
            metrics = {
                'bot_status': bot_status.to_dict(),
                'system': {
                    'platform': platform.system(),
                    'python_version': platform.python_version(),
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent if psutil.disk_usage('/') else 0
                },
                'performance': {
                    'uptime_hours': bot_status.uptime_hours,
                    'requests_per_hour': bot_status.api_request_count / max(1, bot_status.uptime_hours),
                    'error_rate': bot_status.error_count / max(1, bot_status.api_request_count) if bot_status.api_request_count > 0 else 0,
                    'health_score': bot_status.health_score
                }
            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def reset_bot_status(self) -> bool:
        """Reset bot status to default"""
        try:
            default_status = self._create_default_status()
            return self.update_bot_status(default_status)
        except Exception as e:
            self.logger.error(f"Error resetting bot status: {e}")
            return False
    
    def get_status_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get status history (placeholder for future implementation)"""
        try:
            # This would require a separate status_history table
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.error(f"Error getting status history: {e}")
            return []
    
    def export_status_data(self) -> Dict[str, Any]:
        """Export bot status data for backup"""
        try:
            bot_status = self.get_bot_status()
            if bot_status:
                return {
                    'bot_status': bot_status.to_dict(),
                    'system_metrics': self.get_system_metrics(),
                    'export_timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                }
            return {}
        except Exception as e:
            self.logger.error(f"Error exporting status data: {e}")
            return {}
    
    def import_status_data(self, data: Dict[str, Any]) -> bool:
        """Import bot status data from backup"""
        try:
            if not data or 'bot_status' not in data:
                return False
            
            bot_status = BotStatus.from_dict(data['bot_status'])
            return self.update_bot_status(bot_status)
        except Exception as e:
            self.logger.error(f"Error importing status data: {e}")
            return False

class BotStatusMonitor:
    """Monitor bot status and trigger alerts"""
    
    def __init__(self, bot_status_repo: BotStatusRepository):
        self.repo = bot_status_repo
        self.logger = logging.getLogger(__name__)
    
    def monitor_status(self) -> Dict[str, Any]:
        """Monitor bot status and return alerts"""
        try:
            health_check = self.repo.perform_health_check()
            alerts = []
            
            if not health_check['healthy']:
                alerts.append({
                    'level': 'critical',
                    'message': f"Bot is not operational: {health_check.get('reason', 'Unknown')}",
                    'timestamp': datetime.now().isoformat()
                })
            
            if health_check.get('health_score', 0) < 50:
                alerts.append({
                    'level': 'warning',
                    'message': f"Low health score: {health_check['health_score']:.1f}/100",
                    'timestamp': datetime.now().isoformat()
                })
            
            if health_check.get('requests_remaining', 0) < 10:
                alerts.append({
                    'level': 'warning',
                    'message': f"Low API requests remaining: {health_check['requests_remaining']}",
                    'timestamp': datetime.now().isoformat()
                })
            
            if health_check.get('error_count', 0) > 5:
                alerts.append({
                    'level': 'error',
                    'message': f"High error count: {health_check['error_count']}",
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                'status': 'healthy' if not alerts else 'degraded',
                'alerts': alerts,
                'health_check': health_check,
                'check_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error monitoring status: {e}")
            return {
                'status': 'error',
                'alerts': [{
                    'level': 'critical',
                    'message': f"Status monitoring failed: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }],
                'health_check': {},
                'check_timestamp': datetime.now().isoformat()
            }
    
    def should_notify_admin(self, alerts: List[Dict[str, Any]]) -> bool:
        """Check if admin should be notified"""
        critical_alerts = [a for a in alerts if a['level'] == 'critical']
        return len(critical_alerts) > 0
    
    def format_alert_message(self, monitoring_result: Dict[str, Any], lang: str = 'id') -> str:
        """Format alert message for admin"""
        alerts = monitoring_result.get('alerts', [])
        
        if not alerts:
            return ""
        
        if lang == 'id':
            message = "🚨 **Alert Bot RexSint**\n\n"
        else:
            message = "🚨 **RexSint Bot Alert**\n\n"
        
        for alert in alerts:
            level_emoji = {
                'critical': '🔴',
                'error': '🟠',
                'warning': '🟡',
                'info': '🔵'
            }
            
            emoji = level_emoji.get(alert['level'], '⚪')
            message += f"{emoji} **{alert['level'].upper()}**: {alert['message']}\n"
        
        if lang == 'id':
            message += f"\n⏰ **Waktu:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            message += f"\n⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message