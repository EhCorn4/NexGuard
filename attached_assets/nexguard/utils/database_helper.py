"""
Database Helper for NexGuard Discord Bot
Provides standardized database operations and connection management
"""

import sqlite3
import logging
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)

class DatabaseHelper:
    """Centralized database helper for consistent database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection_lock = threading.Lock()
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dictionaries"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT, UPDATE, or DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Execute INSERT query and return the last inserted row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
    
    def execute_many(self, query: str, param_list: List[tuple]) -> int:
        """Execute query with multiple parameter sets"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, param_list)
            conn.commit()
            return cursor.rowcount
    
    def get_single_value(self, query: str, params: tuple = None) -> Any:
        """Execute query and return single value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_single_row(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute query and return single row as dictionary"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def record_exists(self, table: str, conditions: Dict[str, Any]) -> bool:
        """Check if a record exists with given conditions"""
        where_clause = " AND ".join(f"{key} = ?" for key in conditions.keys())
        query = f"SELECT 1 FROM {table} WHERE {where_clause} LIMIT 1"
        params = tuple(conditions.values())
        return self.get_single_value(query, params) is not None
    
    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get all guild settings"""
        query = "SELECT * FROM guild_settings WHERE guild_id = ?"
        result = self.get_single_row(query, (guild_id,))
        
        if not result:
            # Create default settings
            default_settings = {
                'guild_id': guild_id,
                'prefix': '!',
                'mod_role': None,
                'log_channel': None,
                'automod_settings': '{}',
                'autorole_settings': '{}',
                'welcome_settings': '{}'
            }
            
            # Insert default settings
            columns = ', '.join(default_settings.keys())
            placeholders = ', '.join(['?' for _ in default_settings])
            insert_query = f"INSERT OR IGNORE INTO guild_settings ({columns}) VALUES ({placeholders})"
            self.execute_insert(insert_query, tuple(default_settings.values()))
            
            return default_settings
        
        return result
    
    def update_guild_setting(self, guild_id: int, setting: str, value: Any):
        """Update a specific guild setting"""
        query = f"UPDATE guild_settings SET {setting} = ? WHERE guild_id = ?"
        rows_affected = self.execute_update(query, (value, guild_id))
        
        if rows_affected == 0:
            # Insert new record if it doesn't exist
            insert_query = f"INSERT INTO guild_settings (guild_id, {setting}) VALUES (?, ?)"
            self.execute_insert(insert_query, (guild_id, value))
    
    def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
        """Add a warning and return the new warning count"""
        # Insert warning
        insert_query = """
            INSERT INTO warnings (guild_id, user_id, moderator_id, reason, timestamp)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        self.execute_insert(insert_query, (guild_id, user_id, moderator_id, reason))
        
        # Get warning count
        count_query = "SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?"
        return self.get_single_value(count_query, (guild_id, user_id))
    
    def get_warnings(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all warnings for a user"""
        query = """
            SELECT id, moderator_id, reason, timestamp 
            FROM warnings 
            WHERE guild_id = ? AND user_id = ?
            ORDER BY timestamp DESC
        """
        return self.execute_query(query, (guild_id, user_id))
    
    def clear_warnings(self, guild_id: int, user_id: int) -> int:
        """Clear all warnings for a user"""
        query = "DELETE FROM warnings WHERE guild_id = ? AND user_id = ?"
        return self.execute_update(query, (guild_id, user_id))
    
    def add_mute(self, guild_id: int, user_id: int, moderator_id: int, reason: str, expires_at: str = None):
        """Add a mute record"""
        query = """
            INSERT INTO mutes (guild_id, user_id, moderator_id, reason, expires_at, timestamp)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        self.execute_insert(query, (guild_id, user_id, moderator_id, reason, expires_at))
    
    def remove_mute(self, guild_id: int, user_id: int):
        """Remove a mute record"""
        query = "DELETE FROM mutes WHERE guild_id = ? AND user_id = ?"
        self.execute_update(query, (guild_id, user_id))
    
    def get_active_mutes(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all active mutes for a guild"""
        query = """
            SELECT user_id, moderator_id, reason, expires_at, timestamp
            FROM mutes 
            WHERE guild_id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            ORDER BY timestamp DESC
        """
        return self.execute_query(query, (guild_id,))
    
    def log_message_event(self, guild_id: int, channel_id: int, user_id: int, message_id: int, 
                         content: str, action: str, additional_data: str = None):
        """Log a message event"""
        query = """
            INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action, additional_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        self.execute_insert(query, (guild_id, channel_id, user_id, message_id, content, action, additional_data))
    
    def log_member_event(self, guild_id: int, user_id: int, action: str, additional_info: str = None):
        """Log a member event"""
        query = """
            INSERT INTO member_logs (guild_id, user_id, action, additional_info, timestamp)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        self.execute_insert(query, (guild_id, user_id, action, additional_info))
    
    def get_ticket_config(self, guild_id: int) -> Dict[str, Any]:
        """Get ticket configuration for a guild"""
        query = "SELECT * FROM ticket_config WHERE guild_id = ?"
        result = self.get_single_row(query, (guild_id,))
        
        if not result:
            # Create default config
            default_config = {
                'guild_id': guild_id,
                'title': 'Support Ticket System',
                'description': 'Need help? Create a support ticket!',
                'ping_roles': '[]',
                'enabled': True
            }
            
            # Insert default config
            columns = ', '.join(default_config.keys())
            placeholders = ', '.join(['?' for _ in default_config])
            insert_query = f"INSERT INTO ticket_config ({columns}) VALUES ({placeholders})"
            self.execute_insert(insert_query, tuple(default_config.values()))
            
            return default_config
        
        return result
    
    def create_ticket(self, guild_id: int, channel_id: int, user_id: int, 
                     subject: str, description: str) -> int:
        """Create a new ticket and return ticket number"""
        # Get next ticket number
        max_number = self.get_single_value(
            "SELECT MAX(ticket_number) FROM tickets WHERE guild_id = ?", 
            (guild_id,)
        )
        ticket_number = (max_number or 0) + 1
        
        # Insert ticket
        query = """
            INSERT INTO tickets (guild_id, channel_id, user_id, ticket_number, subject, description, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'open', CURRENT_TIMESTAMP)
        """
        self.execute_insert(query, (guild_id, channel_id, user_id, ticket_number, subject, description))
        
        return ticket_number
    
    def close_ticket(self, channel_id: int, closed_by: int):
        """Close a ticket"""
        query = """
            UPDATE tickets 
            SET status = 'closed', closed_at = CURRENT_TIMESTAMP, closed_by = ?
            WHERE channel_id = ?
        """
        self.execute_update(query, (closed_by, channel_id))
    
    def get_ticket_stats(self, guild_id: int) -> Dict[str, Any]:
        """Get ticket statistics for a guild"""
        stats = {}
        
        # Total tickets
        stats['total'] = self.get_single_value(
            "SELECT COUNT(*) FROM tickets WHERE guild_id = ?", 
            (guild_id,)
        ) or 0
        
        # Open tickets
        stats['open'] = self.get_single_value(
            "SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = 'open'", 
            (guild_id,)
        ) or 0
        
        # Closed tickets
        stats['closed'] = self.get_single_value(
            "SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = 'closed'", 
            (guild_id,)
        ) or 0
        
        return stats
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old logs to prevent database bloat"""
        cutoff_date = f"datetime('now', '-{days} days')"
        
        # Clean message logs
        message_query = f"DELETE FROM message_logs WHERE timestamp < {cutoff_date}"
        message_deleted = self.execute_update(message_query)
        
        # Clean member logs
        member_query = f"DELETE FROM member_logs WHERE timestamp < {cutoff_date}"
        member_deleted = self.execute_update(member_query)
        
        logger.info(f"Cleaned up {message_deleted} message logs and {member_deleted} member logs older than {days} days")
        
        return message_deleted + member_deleted
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {}
        
        tables = ['guild_settings', 'warnings', 'mutes', 'tickets', 'message_logs', 'member_logs']
        
        for table in tables:
            try:
                count = self.get_single_value(f"SELECT COUNT(*) FROM {table}")
                stats[table] = count or 0
            except sqlite3.Error:
                stats[table] = 0
        
        return stats

# Global database helper instance
_db_helper = None

def get_database_helper(db_path: str) -> DatabaseHelper:
    """Get the global database helper instance"""
    global _db_helper
    if _db_helper is None:
        _db_helper = DatabaseHelper(db_path)
    return _db_helper

def get_db_connection():
    """Get a database connection context manager for direct usage"""
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'nexguard.db')
    helper = get_database_helper(db_path)
    return helper.get_connection()