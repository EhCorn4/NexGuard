"""
NexGuard API Integration Module
Connects the Discord bot with the web dashboard for real-time configuration sync
"""

import requests
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class NexGuardAPI:
    """API client for NexGuard dashboard integration"""
    
    def __init__(self):
        # Use your current development domain for API calls
        self.base_url = os.getenv('NEXGUARD_API_URL', 'http://localhost:8080')
        self.token = os.getenv('DISCORD_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_server_config(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Fetch server configuration from dashboard"""
        try:
            response = self.session.get(f'{self.base_url}/api/bot/servers/{guild_id}/config')
            if response.status_code == 200:
                return response.json()
            logger.warning(f'Config fetch failed for guild {guild_id}: {response.status_code}')
            return None
        except Exception as e:
            logger.error(f'Config fetch error for guild {guild_id}: {e}')
            return None
    
    def get_custom_commands(self, guild_id: str) -> List[Dict[str, Any]]:
        """Fetch custom commands from dashboard"""
        try:
            response = self.session.get(f'{self.base_url}/api/bot/servers/{guild_id}/commands')
            if response.status_code == 200:
                return response.json()
            logger.warning(f'Commands fetch failed for guild {guild_id}: {response.status_code}')
            return []
        except Exception as e:
            logger.error(f'Commands fetch error for guild {guild_id}: {e}')
            return []
    
    def create_custom_command(self, guild_id: str, name: str, response_text: str, created_by: str) -> Optional[Dict[str, Any]]:
        """Create a custom command via dashboard"""
        try:
            data = {
                'name': name,
                'response': response_text,
                'createdBy': created_by
            }
            response = self.session.post(f'{self.base_url}/api/bot/servers/{guild_id}/commands', json=data)
            if response.status_code == 200:
                return response.json()
            logger.warning(f'Command creation failed for guild {guild_id}: {response.status_code}')
            return None
        except Exception as e:
            logger.error(f'Command creation error for guild {guild_id}: {e}')
            return None
    
    def log_moderation(self, guild_id: str, action_type: str, user_id: str, moderator_id: str, reason: str) -> bool:
        """Log moderation action to dashboard"""
        try:
            data = {
                'type': action_type,
                'userId': user_id,
                'moderatorId': moderator_id,
                'reason': reason
            }
            response = self.session.post(f'{self.base_url}/api/bot/servers/{guild_id}/moderation/log', json=data)
            if response.status_code == 200:
                logger.info(f'Logged {action_type} action for user {user_id} in guild {guild_id}')
                return True
            logger.warning(f'Moderation log failed for guild {guild_id}: {response.status_code}')
            return False
        except Exception as e:
            logger.error(f'Moderation log error for guild {guild_id}: {e}')
            return False
    
    def update_bot_status(self, guild_count: int, user_count: int, uptime: str) -> bool:
        """Update bot status in dashboard"""
        try:
            data = {
                'guilds': guild_count,
                'users': user_count,
                'uptime': uptime,
                'status': 'online'
            }
            response = self.session.post(f'{self.base_url}/api/bot/status', json=data)
            if response.status_code == 200:
                logger.debug(f'Updated bot status: {guild_count} guilds, {user_count} users')
                return True
            return False
        except Exception as e:
            logger.error(f'Bot status update error: {e}')
            return False
    
    def get_automod_config(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get automod configuration from dashboard"""
        try:
            response = self.session.get(f'{self.base_url}/api/bot/servers/{guild_id}/automod')
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f'Automod config fetch error for guild {guild_id}: {e}')
            return None
    
    def get_welcome_config(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get welcome system configuration from dashboard"""
        try:
            response = self.session.get(f'{self.base_url}/api/bot/servers/{guild_id}/welcome')
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f'Welcome config fetch error for guild {guild_id}: {e}')
            return None
    
    def log_command_usage(self, guild_id: str, user_id: str, command_name: str, success: bool, execution_time: float) -> bool:
        """Log command usage to dashboard"""
        try:
            data = {
                'userId': user_id,
                'commandName': command_name,
                'success': success,
                'executionTime': execution_time
            }
            response = self.session.post(f'{self.base_url}/api/bot/servers/{guild_id}/commands/log', json=data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f'Command usage log error for guild {guild_id}: {e}')
            return False

# Global API instance
api = NexGuardAPI()