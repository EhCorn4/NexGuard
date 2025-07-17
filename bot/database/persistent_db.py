import sqlite3
import logging
from typing import Optional, List, Dict, Any
import os
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize the SQLite database and create all necessary tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Guild settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                prefix TEXT DEFAULT '!',
                log_channel INTEGER,
                mute_role INTEGER,
                welcome_channel INTEGER,
                automod_settings TEXT DEFAULT '{}',
                autorole_settings TEXT DEFAULT '{}',
                welcome_settings TEXT DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add missing columns
        columns_to_add = [
            'autorole_settings TEXT DEFAULT "{}"',
            'welcome_settings TEXT DEFAULT "{}"'
        ]
        
        cursor.execute("PRAGMA table_info(guild_settings)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        for column in columns_to_add:
            column_name = column.split()[0]
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE guild_settings ADD COLUMN {column}')
                except sqlite3.OperationalError:
                    pass
        
        # Core tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mutes (
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                active BOOLEAN DEFAULT TRUE,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                channel_id INTEGER,
                user_id INTEGER,
                message_id INTEGER,
                content TEXT,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                additional_data TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                additional_info TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                ticket_number INTEGER NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                closed_by INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_config (
                guild_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                ping_roles TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Execute a SELECT query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get guild settings"""
        query = 'SELECT * FROM guild_settings WHERE guild_id = ?'
        results = self.execute_query(query, (guild_id,))
        
        if results:
            row = results[0]
            return {
                'prefix': row[1] if len(row) > 1 else '!',
                'log_channel': row[2] if len(row) > 2 else None,
                'mute_role': row[3] if len(row) > 3 else None,
                'welcome_channel': row[4] if len(row) > 4 else None,
                'automod_settings': row[5] if len(row) > 5 else '{}',
                'autorole_settings': row[6] if len(row) > 6 else '{}',
                'welcome_settings': row[7] if len(row) > 7 else '{}'
            }
        
        # Create default entry
        self.execute_update(
            'INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)',
            (guild_id,)
        )
        return {
            'prefix': '!',
            'log_channel': None,
            'mute_role': None,
            'welcome_channel': None,
            'automod_settings': '{}',
            'autorole_settings': '{}',
            'welcome_settings': '{}'
        }
    
    def update_guild_setting(self, guild_id: int, setting: str, value: Any):
        """Update a specific guild setting"""
        # Ensure guild exists
        self.execute_update(
            'INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)',
            (guild_id,)
        )
        
        # Update setting
        query = f'UPDATE guild_settings SET {setting} = ? WHERE guild_id = ?'
        self.execute_update(query, (value, guild_id))
    
    def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
        """Add a warning and return the new warning count"""
        query = '''
            INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
            VALUES (?, ?, ?, ?)
        '''
        self.execute_update(query, (guild_id, user_id, moderator_id, reason))
        
        # Get warning count
        count_query = 'SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ? AND active = TRUE'
        result = self.execute_query(count_query, (guild_id, user_id))
        return result[0][0] if result else 0
    
    def get_warnings(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get warnings for a user"""
        query = '''
            SELECT id, reason, moderator_id, timestamp
            FROM warnings
            WHERE guild_id = ? AND user_id = ? AND active = TRUE
            ORDER BY timestamp DESC
        '''
        
        results = self.execute_query(query, (guild_id, user_id))
        return [
            {
                'id': row[0],
                'reason': row[1],
                'moderator_id': row[2],
                'timestamp': row[3]
            }
            for row in results
        ]
    
    def clear_warnings(self, guild_id: int, user_id: int) -> int:
        """Clear all warnings for a user"""
        query = 'UPDATE warnings SET active = FALSE WHERE guild_id = ? AND user_id = ?'
        return self.execute_update(query, (guild_id, user_id))
    
    def add_mute(self, guild_id: int, user_id: int, moderator_id: int, reason: str, expires_at: str = None):
        """Add a mute record"""
        query = '''
            INSERT OR REPLACE INTO mutes (guild_id, user_id, moderator_id, reason, expires_at)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.execute_update(query, (guild_id, user_id, moderator_id, reason, expires_at))
    
    def remove_mute(self, guild_id: int, user_id: int):
        """Remove a mute record"""
        query = 'DELETE FROM mutes WHERE guild_id = ? AND user_id = ?'
        self.execute_update(query, (guild_id, user_id))
    
    def get_mutes(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all active mutes for a guild"""
        query = '''
            SELECT user_id, moderator_id, reason, timestamp, expires_at
            FROM mutes
            WHERE guild_id = ? AND active = TRUE
            ORDER BY timestamp DESC
        '''
        
        results = self.execute_query(query, (guild_id,))
        return [
            {
                'user_id': row[0],
                'moderator_id': row[1],
                'reason': row[2],
                'timestamp': row[3],
                'expires_at': row[4]
            }
            for row in results
        ]
    
    def log_message_event(self, guild_id: int, channel_id: int, user_id: int, message_id: int, content: str, action: str, additional_data: str = None):
        """Log a message event"""
        query = '''
            INSERT INTO message_logs (guild_id, channel_id, user_id, message_id, content, action, additional_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_update(query, (guild_id, channel_id, user_id, message_id, content, action, additional_data))
    
    def log_member_event(self, guild_id: int, user_id: int, action: str, additional_info: str = None):
        """Log a member event"""
        query = '''
            INSERT INTO member_logs (guild_id, user_id, action, additional_info)
            VALUES (?, ?, ?, ?)
        '''
        self.execute_update(query, (guild_id, user_id, action, additional_info))
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old logs to prevent database bloat"""
        queries = [
            f"DELETE FROM message_logs WHERE timestamp < datetime('now', '-{days} days')",
            f"DELETE FROM member_logs WHERE timestamp < datetime('now', '-{days} days')"
        ]
        
        for query in queries:
            deleted = self.execute_update(query)
            logger.info(f"Cleaned up {deleted} old logs")
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {}
        tables = ['guild_settings', 'warnings', 'mutes', 'message_logs', 'member_logs', 'tickets']
        
        for table in tables:
            query = f'SELECT COUNT(*) FROM {table}'
            result = self.execute_query(query)
            stats[table] = result[0][0] if result else 0
        
        return stats