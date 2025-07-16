import sqlite3
import logging
from typing import Optional, List, Dict, Any
import os

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
                auto_role INTEGER,
                automod_settings TEXT DEFAULT '{}',
                autorole_settings TEXT DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add missing columns if they don't exist
        try:
            cursor.execute('ALTER TABLE guild_settings ADD COLUMN autorole_settings TEXT DEFAULT "{}"')
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        try:
            cursor.execute('ALTER TABLE guild_settings ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP')
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Warnings table
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
        
        # Mutes table
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
        
        # Message logs table
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
        
        # Command permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_permissions (
                guild_id INTEGER,
                command_name TEXT,
                entity_id INTEGER,
                entity_type TEXT,
                allowed BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, command_name, entity_id)
            )
        ''')
        
        # Member join/leave logs
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
        
        # Migrate existing guild_settings to add automod_settings column
        cursor.execute("PRAGMA table_info(guild_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add autorole_settings column if it doesn't exist
        if 'autorole_settings' not in columns:
            cursor.execute('ALTER TABLE guild_settings ADD COLUMN autorole_settings TEXT DEFAULT \'{"enabled": false, "roles": []}\'')
            conn.commit()
            print("Added autorole_settings column to guild_settings table")
        
        if 'automod_settings' not in columns:
            cursor.execute('ALTER TABLE guild_settings ADD COLUMN automod_settings TEXT DEFAULT "{}"')
            logger.info("Added automod_settings column to guild_settings table")
        
        # Automod settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automod_settings (
                guild_id INTEGER PRIMARY KEY,
                spam_detection BOOLEAN DEFAULT FALSE,
                link_filtering BOOLEAN DEFAULT FALSE,
                word_filtering BOOLEAN DEFAULT FALSE,
                max_mentions INTEGER DEFAULT 5,
                max_messages INTEGER DEFAULT 5,
                time_window INTEGER DEFAULT 10,
                punishment TEXT DEFAULT 'mute'
            )
        ''')
        
        # Filtered words
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filtered_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                word TEXT,
                severity INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Changelog configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS changelog_config (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                last_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced tickets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                ticket_number INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                subject TEXT,
                description TEXT,
                category TEXT DEFAULT 'General Support',
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'open',
                assigned_to INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME,
                closed_by INTEGER,
                closing_reason TEXT,
                additional_info TEXT,
                rating INTEGER,
                rating_feedback TEXT
            )
        ''')
        
        # Ticket notes table for internal staff notes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number INTEGER,
                guild_id INTEGER,
                user_id INTEGER,
                note TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ticket settings table for guild-specific configurations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_settings (
                guild_id INTEGER PRIMARY KEY,
                config TEXT DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add enhanced columns to existing tickets table if they don't exist
        cursor.execute("PRAGMA table_info(tickets)")
        ticket_columns = [column[1] for column in cursor.fetchall()]
        
        enhanced_columns = [
            ('category', 'TEXT DEFAULT "General Support"'),
            ('priority', 'TEXT DEFAULT "Medium"'),
            ('assigned_to', 'INTEGER'),
            ('closing_reason', 'TEXT'),
            ('additional_info', 'TEXT'),
            ('rating', 'INTEGER'),
            ('rating_feedback', 'TEXT')
        ]
        
        for column_name, column_def in enhanced_columns:
            if column_name not in ticket_columns:
                try:
                    cursor.execute(f'ALTER TABLE tickets ADD COLUMN {column_name} {column_def}')
                    logger.info(f"Added {column_name} column to tickets table")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Could not add {column_name} column: {e}")
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_warnings_guild_user ON warnings(guild_id, user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_logs_guild ON message_logs(guild_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_mutes_guild ON mutes(guild_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_logs_guild ON member_logs(guild_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_guild ON tickets(guild_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_number ON tickets(guild_id, ticket_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_notes_guild ON ticket_notes(guild_id, ticket_number)')
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Execute a SELECT query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_guild_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get guild settings"""
        query = '''
            SELECT prefix, log_channel, mute_role, welcome_channel, auto_role
            FROM guild_settings WHERE guild_id = ?
        '''
        
        result = self.execute_query(query, (guild_id,))
        if result:
            return {
                'prefix': result[0][0],
                'log_channel': result[0][1],
                'mute_role': result[0][2],
                'welcome_channel': result[0][3],
                'auto_role': result[0][4]
            }
        return None
    
    def update_guild_setting(self, guild_id: int, setting: str, value: Any):
        """Update a specific guild setting"""
        # First ensure the guild exists in the database
        self.execute_update(
            'INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)',
            (guild_id,)
        )
        
        # Then update the setting
        query = f'UPDATE guild_settings SET {setting} = ?, updated_at = CURRENT_TIMESTAMP WHERE guild_id = ?'
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
        query = '''
            DELETE FROM message_logs 
            WHERE timestamp < datetime('now', '-{} days')
        '''.format(days)
        
        deleted = self.execute_update(query)
        logger.info(f"Cleaned up {deleted} old message logs")
        
        query = '''
            DELETE FROM member_logs 
            WHERE timestamp < datetime('now', '-{} days')
        '''.format(days)
        
        deleted = self.execute_update(query)
        logger.info(f"Cleaned up {deleted} old member logs")
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {}
        
        tables = ['guild_settings', 'warnings', 'mutes', 'message_logs', 'member_logs', 'command_permissions']
        
        for table in tables:
            query = f'SELECT COUNT(*) FROM {table}'
            result = self.execute_query(query)
            stats[table] = result[0][0] if result else 0
        
        return stats
