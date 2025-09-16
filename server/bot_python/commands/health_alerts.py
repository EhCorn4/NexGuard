#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import aiohttp
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class BotHealthAlerts(commands.Cog):
    """Bot health monitoring and alerting system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.health_monitoring_active = True
        
        # Health check intervals
        self.HEALTH_CHECK_INTERVAL = 30  # seconds
        self.HEARTBEAT_INTERVAL = 60  # seconds
        self.CONNECTION_TIMEOUT = 10  # seconds
        
        # Alert thresholds
        self.OFFLINE_ALERT_DELAY = 120  # seconds before offline alert
        self.RESPONSE_TIME_THRESHOLD = 5000  # ms
        self.ERROR_RATE_THRESHOLD = 0.1  # 10% error rate
        
        # Health state tracking
        self.last_heartbeat = datetime.utcnow()
        self.consecutive_failures = 0
        self.is_healthy = True
        self.error_count = 0
        self.total_requests = 0
        self.alert_sent = False
        
        # Failed guild connections
        self.failed_guilds: Set[int] = set()
        self.connection_errors: List[Dict] = []
        
        # Alert channels and webhooks
        self.alert_channels: List[int] = []
        self.webhook_urls: List[str] = []
        self.email_alerts_enabled = False
        
        # Start health monitoring
        self.health_check_loop.start()
        self.heartbeat_loop.start()
        self.connection_monitor.start()
        logger.info("Bot health alerts system initialized")
    
    def sanitize_health_data(self, data):
        """Sanitize health data to remove NaN and infinity values that can't be JSON serialized"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                sanitized[key] = self.sanitize_health_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self.sanitize_health_data(item) for item in data]
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                return 0.0  # Replace NaN/infinity with 0.0
            return data
        else:
            return data
    
    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.health_check_loop.cancel()
        self.heartbeat_loop.cancel()
        self.connection_monitor.cancel()
    
    @tasks.loop(seconds=30)
    async def health_check_loop(self):
        """Perform comprehensive health checks"""
        try:
            health_status = await self.perform_health_check()
            
            # Log health status
            await self.log_health_status(health_status)
            
            # Check for health degradation
            if not health_status['overall_healthy']:
                if self.is_healthy:  # Health just degraded
                    await self.send_health_alert('degraded', health_status)
                    self.is_healthy = False
                self.consecutive_failures += 1
            else:
                if not self.is_healthy:  # Health restored
                    await self.send_health_alert('restored', health_status)
                    self.is_healthy = True
                self.consecutive_failures = 0
            
            # Send critical alerts for sustained issues
            if self.consecutive_failures >= 4:  # 2 minutes of failures
                await self.send_health_alert('critical', health_status)
                
        except Exception as e:
            logger.error(f"Error in health check loop: {e}")
            self.consecutive_failures += 1
    
    @tasks.loop(minutes=1)
    async def heartbeat_loop(self):
        """Send heartbeat and update last seen timestamp"""
        try:
            self.last_heartbeat = datetime.utcnow()
            
            # Send heartbeat to external monitoring
            await self.send_heartbeat()
            
            # Update bot status in database
            await self.update_bot_status()
            
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")
    
    @tasks.loop(minutes=5)
    async def connection_monitor(self):
        """Monitor Discord connection quality"""
        try:
            # Check Discord connection
            connection_status = await self.check_discord_connection()
            
            # Monitor guild connectivity
            guild_health = await self.check_guild_connections()
            
            # Check for connection issues
            if not connection_status['connected'] or guild_health['failed_guilds'] > 0:
                await self.handle_connection_issues(connection_status, guild_health)
                
        except Exception as e:
            logger.error(f"Error in connection monitor: {e}")
    
    async def perform_health_check(self) -> Dict:
        """Perform comprehensive bot health check"""
        try:
            health_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_healthy': True,
                'checks': {}
            }
            
            # Discord API connectivity
            api_health = await self.check_discord_api()
            health_data['checks']['discord_api'] = api_health
            if not api_health['healthy']:
                health_data['overall_healthy'] = False
            
            # Database connectivity
            db_health = await self.check_database()
            health_data['checks']['database'] = db_health
            if not db_health['healthy']:
                health_data['overall_healthy'] = False
            
            # Bot responsiveness
            response_health = await self.check_bot_responsiveness()
            health_data['checks']['responsiveness'] = response_health
            if not response_health['healthy']:
                health_data['overall_healthy'] = False
            
            # Memory and CPU health
            system_health = await self.check_system_resources()
            health_data['checks']['system'] = system_health
            if not system_health['healthy']:
                health_data['overall_healthy'] = False
            
            # Command execution health
            command_health = await self.check_command_health()
            health_data['checks']['commands'] = command_health
            if not command_health['healthy']:
                health_data['overall_healthy'] = False
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_healthy': False,
                'error': str(e),
                'checks': {}
            }
    
    async def check_discord_api(self) -> Dict:
        """Check Discord API connectivity and latency"""
        try:
            start_time = datetime.utcnow()
            
            # Test API call
            if self.bot.user:
                await self.bot.fetch_user(self.bot.user.id)
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                'healthy': response_time < self.RESPONSE_TIME_THRESHOLD,
                'response_time_ms': round(response_time, 2),
                'latency_ms': round(self.bot.latency * 1000, 2) if self.bot.latency else 0,
                'connected': not self.bot.is_closed()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'response_time_ms': 0,
                'latency_ms': 0,
                'connected': False
            }
    
    async def check_database(self) -> Dict:
        """Check database connectivity and performance"""
        try:
            if not self.bot.db_pool:
                return {
                    'healthy': False,
                    'error': 'No database pool available'
                }
            
            start_time = datetime.utcnow()
            
            async with self.bot.db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                'healthy': response_time < 1000,  # 1 second threshold
                'response_time_ms': round(response_time, 2),
                'pool_size': len(self.bot.db_pool._holders) if hasattr(self.bot.db_pool, '_holders') else 0
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'response_time_ms': 0
            }
    
    async def check_bot_responsiveness(self) -> Dict:
        """Check bot command responsiveness"""
        try:
            # Check recent command success rate
            error_rate = 0
            if self.total_requests > 0:
                error_rate = self.error_count / self.total_requests
            
            return {
                'healthy': error_rate < self.ERROR_RATE_THRESHOLD,
                'error_rate': round(error_rate, 3),
                'total_requests': self.total_requests,
                'error_count': self.error_count,
                'consecutive_failures': self.consecutive_failures
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    async def check_system_resources(self) -> Dict:
        """Check system resource usage"""
        try:
            import psutil
            
            # Get current resource usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Handle NaN values that can occur under system load
            if math.isnan(cpu_percent) or math.isinf(cpu_percent):
                cpu_percent = 0.0
            if math.isnan(memory.percent) or math.isinf(memory.percent):
                memory_percent = 0.0
            else:
                memory_percent = memory.percent
            
            # Define health thresholds
            cpu_healthy = cpu_percent < 90
            memory_healthy = memory_percent < 90
            
            return {
                'healthy': cpu_healthy and memory_healthy,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'cpu_healthy': cpu_healthy,
                'memory_healthy': memory_healthy
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    async def check_command_health(self) -> Dict:
        """Check command system health"""
        try:
            # Count registered commands
            app_commands = len(self.bot.tree.get_commands())
            
            # Check if commands are synced
            commands_synced = app_commands > 0
            
            return {
                'healthy': commands_synced,
                'app_commands_count': app_commands,
                'commands_synced': commands_synced
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    async def check_discord_connection(self) -> Dict:
        """Check Discord connection status"""
        try:
            # Handle potential NaN values in bot latency
            latency_ms = 0
            if self.bot.latency and not math.isnan(self.bot.latency) and not math.isinf(self.bot.latency):
                latency_ms = round(self.bot.latency * 1000, 2)
            
            return {
                'connected': not self.bot.is_closed(),
                'latency_ms': latency_ms,
                'guild_count': len(self.bot.guilds),
                'ready': self.bot.is_ready()
            }
            
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
    
    async def check_guild_connections(self) -> Dict:
        """Check connectivity to individual guilds"""
        try:
            failed_guilds = 0
            total_guilds = len(self.bot.guilds)
            
            for guild in self.bot.guilds:
                try:
                    # Try to fetch guild info to test connectivity
                    await guild.fetch_channels()
                except discord.Forbidden:
                    # This is expected for some guilds
                    pass
                except Exception:
                    failed_guilds += 1
                    if guild.id not in self.failed_guilds:
                        self.failed_guilds.add(guild.id)
                        logger.warning(f"Lost connection to guild: {guild.name}")
            
            return {
                'total_guilds': total_guilds,
                'failed_guilds': failed_guilds,
                'success_rate': (total_guilds - failed_guilds) / total_guilds if total_guilds > 0 else 0
            }
            
        except Exception as e:
            return {
                'total_guilds': 0,
                'failed_guilds': 0,
                'error': str(e)
            }
    
    async def send_health_alert(self, alert_type: str, health_status: Dict):
        """Send health alert notifications"""
        try:
            # Create alert embed
            embed = await self.create_health_alert_embed(alert_type, health_status)
            
            # Send to Discord channels
            await self.send_discord_alerts(embed)
            
            # Send webhook notifications
            await self.send_webhook_alerts(alert_type, health_status)
            
            # Send email alerts if enabled
            if self.email_alerts_enabled:
                await self.send_email_alert(alert_type, health_status)
            
            # Log alert
            await self.log_health_alert(alert_type, health_status)
            
        except Exception as e:
            logger.error(f"Error sending health alert: {e}")
    
    async def create_health_alert_embed(self, alert_type: str, health_status: Dict) -> discord.Embed:
        """Create Discord embed for health alerts"""
        colors = {
            'degraded': 0xFF6600,  # Orange
            'critical': 0xFF0000,  # Red
            'restored': 0x00FF00   # Green
        }
        
        titles = {
            'degraded': '⚠️ Bot Health Degraded',
            'critical': '🚨 Critical Bot Health Alert',
            'restored': '✅ Bot Health Restored'
        }
        
        embed = discord.Embed(
            title=titles.get(alert_type, '📊 Bot Health Alert'),
            color=colors.get(alert_type, 0xFFFF00),
            timestamp=datetime.utcnow()
        )
        
        # Add health check results
        checks = health_status.get('checks', {})
        for check_name, check_data in checks.items():
            status = "✅ Healthy" if check_data.get('healthy', False) else "❌ Unhealthy"
            value = status
            
            if 'response_time_ms' in check_data:
                value += f"\nResponse: {check_data['response_time_ms']:.1f}ms"
            
            if 'error' in check_data:
                value += f"\nError: {check_data['error'][:50]}..."
            
            embed.add_field(
                name=check_name.replace('_', ' ').title(),
                value=value,
                inline=True
            )
        
        # Add summary information
        embed.add_field(
            name="Overall Status",
            value="Healthy" if health_status.get('overall_healthy', False) else "Unhealthy",
            inline=True
        )
        
        embed.add_field(
            name="Consecutive Failures",
            value=str(self.consecutive_failures),
            inline=True
        )
        
        embed.add_field(
            name="Last Heartbeat",
            value=f"<t:{int(self.last_heartbeat.timestamp())}:R>",
            inline=True
        )
        
        return embed
    
    async def send_discord_alerts(self, embed: discord.Embed):
        """Send alerts to configured Discord channels"""
        try:
            # Send only to specific channel ID: 1408340635676708946
            target_channel_id = 1408340635676708946
            alert_channel = self.bot.get_channel(target_channel_id)
            
            if alert_channel:
                try:
                    await alert_channel.send(embed=embed)
                    logger.info(f"Health alert sent to {alert_channel.name} in {alert_channel.guild.name}")
                except discord.Forbidden:
                    logger.warning(f"No permission to send health alert to channel {target_channel_id}")
                except Exception as e:
                    logger.error(f"Error sending health alert to channel {target_channel_id}: {e}")
            else:
                logger.warning(f"Target health alert channel {target_channel_id} not found")
                        
        except Exception as e:
            logger.error(f"Error sending Discord alerts: {e}")
    
    async def send_webhook_alerts(self, alert_type: str, health_status: Dict):
        """Send webhook notifications"""
        try:
            payload = {
                'timestamp': datetime.utcnow().isoformat(),
                'alert_type': alert_type,
                'health_status': health_status,
                'bot_info': {
                    'name': 'NexGuard',
                    'version': '2.5.1',
                    'guild_count': len(self.bot.guilds),
                    'user_id': str(self.bot.user.id) if self.bot.user else None
                }
            }
            
            # Send to internal webhook endpoint
            async with aiohttp.ClientSession() as session:
                try:
                    await session.post(
                        'http://localhost:5000/api/bot/health-alert',
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=5)
                    )
                except Exception as e:
                    logger.debug(f"Internal webhook failed: {e}")
                
        except Exception as e:
            logger.error(f"Error sending webhook alerts: {e}")
    
    async def send_heartbeat(self):
        """Send heartbeat to monitoring systems"""
        try:
            heartbeat_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'alive',
                'guilds': len(self.bot.guilds),
                'latency': round(self.bot.latency * 1000, 2) if self.bot.latency else 0,
                'version': '2.5.1'
            }
            
            # Send to webhook endpoint
            async with aiohttp.ClientSession() as session:
                try:
                    await session.post(
                        'http://localhost:5000/api/bot/heartbeat',
                        json=heartbeat_data,
                        timeout=aiohttp.ClientTimeout(total=3)
                    )
                except Exception as e:
                    logger.debug(f"Heartbeat failed: {e}")
                    
        except Exception as e:
            logger.debug(f"Error sending heartbeat: {e}")
    
    async def log_health_status(self, health_status: Dict):
        """Log health status to database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_health_logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL,
                        overall_healthy BOOLEAN,
                        consecutive_failures INTEGER,
                        health_data JSONB
                    )
                """)
                
                # Sanitize health data before JSON serialization
                sanitized_health_status = self.sanitize_health_data(health_status)
                
                await conn.execute("""
                    INSERT INTO bot_health_logs (
                        timestamp, overall_healthy, consecutive_failures, health_data
                    ) VALUES ($1, $2, $3, $4)
                """, 
                    datetime.utcnow(),
                    sanitized_health_status.get('overall_healthy', False),
                    self.consecutive_failures,
                    json.dumps(sanitized_health_status)
                )
                
        except Exception as e:
            logger.error(f"Error logging health status: {e}")
    
    async def log_health_alert(self, alert_type: str, health_status: Dict):
        """Log health alert to database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_health_alerts (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL,
                        alert_type VARCHAR(50),
                        health_data JSONB
                    )
                """)
                
                # Sanitize health data before JSON serialization
                sanitized_health_status = self.sanitize_health_data(health_status)
                
                await conn.execute("""
                    INSERT INTO bot_health_alerts (timestamp, alert_type, health_data)
                    VALUES ($1, $2, $3)
                """, datetime.utcnow(), alert_type, json.dumps(sanitized_health_status))
                
        except Exception as e:
            logger.error(f"Error logging health alert: {e}")
    
    async def update_bot_status(self):
        """Update bot status in database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                # Update existing bot status record
                await conn.execute("""
                    UPDATE bot_status SET
                        is_online = $1,
                        guilds_count = $2,
                        users_count = $3,
                        uptime = $4,
                        last_restart = $5,
                        updated_at = $6
                    WHERE id = 1
                """, 
                    True,
                    len(self.bot.guilds),
                    sum(guild.member_count or 0 for guild in self.bot.guilds),
                    str(datetime.utcnow() - self.bot.bot_start_time),
                    self.bot.bot_start_time,
                    datetime.utcnow()
                )
                
        except Exception as e:
            logger.debug(f"Error updating bot status: {e}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Track command errors for health monitoring"""
        self.error_count += 1
        # Don't increment total_requests here - it's handled by on_command
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Track successful commands"""
        # Don't increment total_requests here - it's handled by on_command
        pass
        
    @commands.Cog.listener() 
    async def on_command(self, ctx):
        """Track all traditional command attempts"""
        # This fires for every command attempt, successful or not
        self.total_requests += 1
        
    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command):
        """Track app command (slash command) completions"""
        self.total_requests += 1
    
    @discord.app_commands.command(name="health")
    @discord.app_commands.describe(action="Health action to perform")
    async def health_command(self, interaction: discord.Interaction, action: str = "status"):
        """View bot health monitoring information"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need 'Manage Server' permission to use this command.",
                ephemeral=True
            )
            return
        
        if action.lower() == "status":
            # Get current health status
            health_status = await self.perform_health_check()
            
            embed = discord.Embed(
                title="🏥 Bot Health Status",
                color=0x00FF00 if health_status.get('overall_healthy', False) else 0xFF0000,
                timestamp=datetime.utcnow()
            )
            
            # Overall status
            overall_status = "✅ Healthy" if health_status.get('overall_healthy', False) else "❌ Unhealthy"
            embed.add_field(name="Overall Status", value=overall_status, inline=True)
            embed.add_field(name="Consecutive Failures", value=str(self.consecutive_failures), inline=True)
            embed.add_field(name="Monitoring", value="Active" if self.health_monitoring_active else "Disabled", inline=True)
            
            # Health checks
            checks = health_status.get('checks', {})
            for check_name, check_data in list(checks.items())[:6]:  # Show first 6 checks
                status = "✅" if check_data.get('healthy', False) else "❌"
                value = status
                
                if 'response_time_ms' in check_data:
                    value += f" ({check_data['response_time_ms']:.1f}ms)"
                
                embed.add_field(
                    name=check_name.replace('_', ' ').title(),
                    value=value,
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif action.lower() == "test":
            # Send test alert
            test_health = {
                'overall_healthy': False,
                'checks': {
                    'test': {'healthy': False, 'error': 'This is a test alert'}
                }
            }
            await self.send_health_alert('test', test_health)
            await interaction.response.send_message("🧪 Test alert sent!", ephemeral=True)
            
        else:
            await interaction.response.send_message(
                "❌ Invalid action. Use: `status`, `test`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(BotHealthAlerts(bot))