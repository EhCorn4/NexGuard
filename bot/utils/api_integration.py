"""
API Integration utilities for NexGuard Dashboard
"""

import requests
import logging
import os

logger = logging.getLogger(__name__)

class APIIntegration:
    def __init__(self):
        self.base_url = os.getenv('DASHBOARD_URL', 'https://nexguard.replit.app')
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        
    def get_server_config(self, guild_id):
        """Get server configuration from dashboard"""
        try:
            response = requests.get(
                f"{self.base_url}/api/bot/servers/{guild_id}/config",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error fetching server config: {e}")
            return None
    
    def create_custom_command(self, guild_id, name, response, user_id):
        """Create a custom command"""
        try:
            data = {
                "name": name,
                "response": response,
                "createdBy": user_id
            }
            response = requests.post(
                f"{self.base_url}/api/bot/servers/{guild_id}/commands",
                json=data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error creating custom command: {e}")
            return False

# Global instance
api = APIIntegration()