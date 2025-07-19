"""
Database Manager for RexSint Bot
Handles SQLite database operations for users and bot status
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import threading

class DatabaseManager:
    """Manages database operations for RexSint Bot"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        username TEXT,
                        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        subscription_end_date DATETIME,
                        token_balance INTEGER DEFAULT 0,
                        api_token TEXT,
                        is_trial_activated BOOLEAN DEFAULT FALSE,
                        timezone TEXT DEFAULT 'Asia/Jakarta',
                        language_code TEXT DEFAULT 'id',
                        is_blocked BOOLEAN DEFAULT FALSE,
                        total_requests INTEGER DEFAULT 0,
                        file_requests INTEGER DEFAULT 0
                    )
                ''')
                
                # Create bot_status table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bot_status (
                        id INTEGER PRIMARY KEY DEFAULT 1,
                        active_api_token TEXT,
                        api_request_count INTEGER DEFAULT 0,
                        api_activation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_maintenance BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Create admin table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS admins (
                        admin_id INTEGER PRIMARY KEY,
                        added_date DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Insert default bot status if not exists
                cursor.execute('SELECT COUNT(*) FROM bot_status WHERE id = 1')
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO bot_status (id, active_api_token, api_request_count, api_activation_date, is_maintenance)
                        VALUES (1, NULL, 0, CURRENT_TIMESTAMP, FALSE)
                    ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
            except Exception as e:
                self.logger.error(f"Error initializing database: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def add_user(self, user_id: int, first_name: str, username: str = None, api_token: str = None) -> bool:
        """Add new user to database"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                # Set trial end date to 7 days from now
                trial_end_date = datetime.now() + timedelta(days=7)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, first_name, username, registration_date, subscription_end_date, 
                     token_balance, api_token, is_trial_activated, timezone, language_code, 
                     is_blocked, total_requests, file_requests)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, 10, ?, FALSE, 'Asia/Jakarta', 'id', FALSE, 0, 0)
                ''', (user_id, first_name, username, trial_end_date, api_token))
                
                conn.commit()
                self.logger.info(f"User {user_id} added successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Error adding user {user_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}")
            return None
        finally:
            conn.close()
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user data"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in kwargs.items():
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                if not set_clauses:
                    return False
                
                values.append(user_id)
                query = f"UPDATE users SET {', '.join(set_clauses)} WHERE user_id = ?"
                
                cursor.execute(query, values)
                conn.commit()
                
                return cursor.rowcount > 0
                
            except Exception as e:
                self.logger.error(f"Error updating user {user_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def activate_trial(self, user_id: int) -> bool:
        """Activate trial for user"""
        return self.update_user(user_id, is_trial_activated=True)
    
    def block_user(self, user_id: int, block: bool = True) -> bool:
        """Block or unblock user"""
        return self.update_user(user_id, is_blocked=block)
    
    def increment_requests(self, user_id: int, file_request: bool = False) -> bool:
        """Increment user request count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if file_request:
                cursor.execute('''
                    UPDATE users 
                    SET total_requests = total_requests + 1, file_requests = file_requests + 1
                    WHERE user_id = ?
                ''', (user_id,))
            else:
                cursor.execute('''
                    UPDATE users 
                    SET total_requests = total_requests + 1
                    WHERE user_id = ?
                ''', (user_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Error incrementing requests for user {user_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_bot_status(self) -> Optional[Dict[str, Any]]:
        """Get bot status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM bot_status WHERE id = 1')
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting bot status: {e}")
            return None
        finally:
            conn.close()
    
    def update_bot_status(self, **kwargs) -> bool:
        """Update bot status"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                set_clauses = []
                values = []
                
                for key, value in kwargs.items():
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                if not set_clauses:
                    return False
                
                query = f"UPDATE bot_status SET {', '.join(set_clauses)} WHERE id = 1"
                cursor.execute(query, values)
                conn.commit()
                
                return cursor.rowcount > 0
                
            except Exception as e:
                self.logger.error(f"Error updating bot status: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def set_maintenance_mode(self, maintenance: bool) -> bool:
        """Set maintenance mode"""
        return self.update_bot_status(is_maintenance=maintenance)
    
    def increment_api_count(self) -> bool:
        """Increment API request count"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    UPDATE bot_status 
                    SET api_request_count = api_request_count + 1
                    WHERE id = 1
                ''')
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                self.logger.error(f"Error incrementing API count: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def set_new_api_token(self, token: str) -> bool:
        """Set new API token and reset counters"""
        return self.update_bot_status(
            active_api_token=token,
            api_request_count=0,
            api_activation_date=datetime.now(),
            is_maintenance=False
        )
    
    def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Active users (trial activated)
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_trial_activated = TRUE')
            active_users = cursor.fetchone()[0]
            
            # New users today
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE DATE(registration_date) = DATE('now')
            ''')
            new_users_today = cursor.fetchone()[0]
            
            # Blocked users
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_blocked = TRUE')
            blocked_users = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'new_users_today': new_users_today,
                'blocked_users': blocked_users
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user stats: {e}")
            return {}
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for broadcast"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT user_id, first_name, is_blocked FROM users WHERE is_blocked = FALSE')
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            self.logger.error(f"Error getting all users: {e}")
            return []
        finally:
            conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM admins WHERE admin_id = ?', (user_id,))
            return cursor.fetchone()[0] > 0
            
        except Exception as e:
            self.logger.error(f"Error checking admin status for {user_id}: {e}")
            return False
        finally:
            conn.close()
    
    def add_admin(self, admin_id: int) -> bool:
        """Add new admin"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO admins (admin_id, added_date)
                    VALUES (?, CURRENT_TIMESTAMP)
                ''', (admin_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                self.logger.error(f"Error adding admin {admin_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    
    def remove_admin(self, admin_id: int) -> bool:
        """Remove admin"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM admins WHERE admin_id = ?', (admin_id,))
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                self.logger.error(f"Error removing admin {admin_id}: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()