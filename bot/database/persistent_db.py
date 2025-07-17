"""
Persistent database manager for NexGuard
"""

import sqlite3
import json
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def save_autorole_settings(self, guild_id, settings):
        """Save autorole settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO guild_settings (guild_id, autorole_settings)
                VALUES (?, ?)
            ''', (guild_id, json.dumps(settings)))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving autorole settings: {e}")
            return False
        finally:
            conn.close()
    
    def get_autorole_settings(self, guild_id):
        """Get autorole settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT autorole_settings FROM guild_settings WHERE guild_id = ?', (guild_id,))
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            return {"enabled": False, "roles": []}
        except Exception as e:
            logger.error(f"Error getting autorole settings: {e}")
            return {"enabled": False, "roles": []}
        finally:
            conn.close()
    
    def save_automod_settings(self, guild_id, settings):
        """Save automod settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO guild_settings (guild_id, automod_settings)
                VALUES (?, ?)
            ''', (guild_id, json.dumps(settings)))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving automod settings: {e}")
            return False
        finally:
            conn.close()
    
    def get_automod_settings(self, guild_id):
        """Get automod settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT automod_settings FROM guild_settings WHERE guild_id = ?', (guild_id,))
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            return {}
        except Exception as e:
            logger.error(f"Error getting automod settings: {e}")
            return {}
        finally:
            conn.close()
    
    def save_welcome_settings(self, guild_id, settings):
        """Save welcome settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO guild_settings (guild_id, welcome_settings)
                VALUES (?, ?)
            ''', (guild_id, json.dumps(settings)))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving welcome settings: {e}")
            return False
        finally:
            conn.close()
    
    def get_welcome_settings(self, guild_id):
        """Get welcome settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT welcome_settings FROM guild_settings WHERE guild_id = ?', (guild_id,))
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            return {}
        except Exception as e:
            logger.error(f"Error getting welcome settings: {e}")
            return {}
        finally:
            conn.close()