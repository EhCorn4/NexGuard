#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

class PerformanceMonitor(commands.Cog):
    """Advanced performance monitoring and alerting system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.monitoring_active = True
        
        # Performance thresholds
        self.CPU_CRITICAL = 90.0  # CPU usage %
        self.CPU_WARNING = 75.0
        self.MEMORY_CRITICAL = 90.0  # Memory usage %
        self.MEMORY_WARNING = 80.0
        self.DISK_CRITICAL = 95.0  # Disk usage %
        self.DISK_WARNING = 85.0
        self.LATENCY_CRITICAL = 1000  # Discord latency ms
        self.LATENCY_WARNING = 500
        
        # Alert tracking
        self.alert_history: Dict[str, datetime] = {}
        self.alert_cooldown = timedelta(minutes=15)  # Prevent spam
        self.performance_data: List[Dict] = []
        
        # Start monitoring tasks
        self.monitor_performance.start()
        self.cleanup_performance_data.start()
        logger.info("Performance monitoring system initialized")
    
    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.monitor_performance.cancel()
        self.cleanup_performance_data.cancel()
    
    @tasks.loop(minutes=1)
    async def monitor_performance(self):
        """Monitor system performance every minute"""
        try:
            # Collect performance metrics
            metrics = await self.collect_metrics()
            
            # Store metrics in database
            await self.store_metrics(metrics)
            
            # Check for alerts
            await self.check_performance_alerts(metrics)
            
            # Keep recent data in memory for trending
            self.performance_data.append({
                'timestamp': datetime.utcnow(),
                'metrics': metrics
            })
            
        except Exception as e:
            logger.error(f"Error in performance monitoring: {e}")
    
    @tasks.loop(hours=1)
    async def cleanup_performance_data(self):
        """Clean up old performance data"""
        try:
            # Keep only last 24 hours of data in memory
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.performance_data = [
                data for data in self.performance_data
                if data['timestamp'] > cutoff_time
            ]
            
            # Clean up old database records (keep 30 days)
            if self.bot.db_pool:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute("""
                        DELETE FROM performance_metrics 
                        WHERE timestamp < $1
                    """, datetime.utcnow() - timedelta(days=30))
                    
        except Exception as e:
            logger.error(f"Error cleaning up performance data: {e}")
    
    async def collect_metrics(self) -> Dict:
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Bot-specific metrics
            bot_latency = round(self.bot.latency * 1000, 2) if self.bot.latency else 0
            guild_count = len(self.bot.guilds)
            user_count = sum(guild.member_count or 0 for guild in self.bot.guilds)
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss / (1024**2)  # MB
            process_cpu = process.cpu_percent()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'percent': float(cpu_percent) if cpu_percent and not (isinstance(cpu_percent, float) and cpu_percent != cpu_percent) else 0.0,
                    'count': cpu_count,
                    'process_percent': float(process_cpu) if process_cpu and not (isinstance(process_cpu, float) and process_cpu != process_cpu) else 0.0
                },
                'memory': {
                    'percent': float(memory_percent) if memory_percent else 0.0,
                    'used_gb': round(memory_used_gb, 2) if memory_used_gb else 0.0,
                    'total_gb': round(memory_total_gb, 2) if memory_total_gb else 0.0,
                    'process_mb': round(process_memory, 2) if process_memory else 0.0
                },
                'disk': {
                    'percent': round(disk_percent, 2) if disk_percent else 0.0,
                    'used_gb': round(disk_used_gb, 2) if disk_used_gb else 0.0,
                    'total_gb': round(disk_total_gb, 2) if disk_total_gb else 0.0
                },
                'network': {
                    'bytes_sent': int(network.bytes_sent) if network.bytes_sent else 0,
                    'bytes_recv': int(network.bytes_recv) if network.bytes_recv else 0,
                    'packets_sent': int(network.packets_sent) if network.packets_sent else 0,
                    'packets_recv': int(network.packets_recv) if network.packets_recv else 0
                },
                'bot': {
                    'latency_ms': float(bot_latency) if bot_latency and not (isinstance(bot_latency, float) and bot_latency != bot_latency) else 0.0,
                    'guilds': int(guild_count) if guild_count else 0,
                    'users': int(user_count) if user_count else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {}
    
    async def store_metrics(self, metrics: Dict):
        """Store metrics in database"""
        try:
            if not self.bot.db_pool or not metrics:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                # Ensure performance_metrics table exists
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL,
                        cpu_percent FLOAT,
                        memory_percent FLOAT,
                        disk_percent FLOAT,
                        bot_latency FLOAT,
                        guild_count INTEGER,
                        user_count INTEGER,
                        process_memory_mb FLOAT,
                        process_cpu_percent FLOAT,
                        raw_data JSONB
                    )
                """)
                
                await conn.execute("""
                    INSERT INTO performance_metrics (
                        timestamp, cpu_percent, memory_percent, disk_percent,
                        bot_latency, guild_count, user_count, process_memory_mb,
                        process_cpu_percent, raw_data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                    datetime.utcnow(),
                    metrics.get('cpu', {}).get('percent', 0),
                    metrics.get('memory', {}).get('percent', 0),
                    metrics.get('disk', {}).get('percent', 0),
                    metrics.get('bot', {}).get('latency_ms', 0),
                    metrics.get('bot', {}).get('guilds', 0),
                    metrics.get('bot', {}).get('users', 0),
                    metrics.get('memory', {}).get('process_mb', 0),
                    metrics.get('cpu', {}).get('process_percent', 0),
                    json.dumps(metrics)
                )
                
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    async def check_performance_alerts(self, metrics: Dict):
        """Check metrics against thresholds and send alerts"""
        try:
            if not metrics:
                return
                
            alerts_to_send = []
            
            # Check CPU usage
            cpu_percent = metrics.get('cpu', {}).get('percent', 0)
            if cpu_percent >= self.CPU_CRITICAL:
                alerts_to_send.append({
                    'type': 'cpu_critical',
                    'level': 'critical',
                    'message': f'CPU usage critical: {cpu_percent:.1f}%',
                    'value': cpu_percent,
                    'threshold': self.CPU_CRITICAL
                })
            elif cpu_percent >= self.CPU_WARNING:
                alerts_to_send.append({
                    'type': 'cpu_warning',
                    'level': 'warning',
                    'message': f'CPU usage high: {cpu_percent:.1f}%',
                    'value': cpu_percent,
                    'threshold': self.CPU_WARNING
                })
            
            # Check Memory usage
            memory_percent = metrics.get('memory', {}).get('percent', 0)
            if memory_percent >= self.MEMORY_CRITICAL:
                alerts_to_send.append({
                    'type': 'memory_critical',
                    'level': 'critical',
                    'message': f'Memory usage critical: {memory_percent:.1f}%',
                    'value': memory_percent,
                    'threshold': self.MEMORY_CRITICAL
                })
            elif memory_percent >= self.MEMORY_WARNING:
                alerts_to_send.append({
                    'type': 'memory_warning',
                    'level': 'warning',
                    'message': f'Memory usage high: {memory_percent:.1f}%',
                    'value': memory_percent,
                    'threshold': self.MEMORY_WARNING
                })
            
            # Check Disk usage
            disk_percent = metrics.get('disk', {}).get('percent', 0)
            if disk_percent >= self.DISK_CRITICAL:
                alerts_to_send.append({
                    'type': 'disk_critical',
                    'level': 'critical',
                    'message': f'Disk usage critical: {disk_percent:.1f}%',
                    'value': disk_percent,
                    'threshold': self.DISK_CRITICAL
                })
            elif disk_percent >= self.DISK_WARNING:
                alerts_to_send.append({
                    'type': 'disk_warning',
                    'level': 'warning',
                    'message': f'Disk usage high: {disk_percent:.1f}%',
                    'value': disk_percent,
                    'threshold': self.DISK_WARNING
                })
            
            # Check Bot latency
            latency = metrics.get('bot', {}).get('latency_ms', 0)
            if latency >= self.LATENCY_CRITICAL:
                alerts_to_send.append({
                    'type': 'latency_critical',
                    'level': 'critical',
                    'message': f'Bot latency critical: {latency:.1f}ms',
                    'value': latency,
                    'threshold': self.LATENCY_CRITICAL
                })
            elif latency >= self.LATENCY_WARNING:
                alerts_to_send.append({
                    'type': 'latency_warning',
                    'level': 'warning',
                    'message': f'Bot latency high: {latency:.1f}ms',
                    'value': latency,
                    'threshold': self.LATENCY_WARNING
                })
            
            # Send alerts (with cooldown)
            for alert in alerts_to_send:
                await self.send_alert(alert)
                
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")
    
    async def send_alert(self, alert: Dict):
        """Send performance alert with cooldown"""
        try:
            alert_key = f"{alert['type']}_{alert['level']}"
            current_time = datetime.utcnow()
            
            # Check cooldown
            if alert_key in self.alert_history:
                if current_time - self.alert_history[alert_key] < self.alert_cooldown:
                    return  # Still in cooldown
            
            self.alert_history[alert_key] = current_time
            
            # Create alert embed
            color = 0xFF0000 if alert['level'] == 'critical' else 0xFF6600
            embed = discord.Embed(
                title=f"🚨 Performance Alert - {alert['level'].title()}",
                description=alert['message'],
                color=color,
                timestamp=current_time
            )
            
            embed.add_field(
                name="Current Value",
                value=f"{alert['value']:.1f}",
                inline=True
            )
            embed.add_field(
                name="Threshold",
                value=f"{alert['threshold']:.1f}",
                inline=True
            )
            embed.add_field(
                name="Alert Type",
                value=alert['type'].replace('_', ' ').title(),
                inline=True
            )
            
            # Send to all available alert channels
            await self.broadcast_alert(embed)
            
            # Log alert
            await self.log_alert(alert)
            
            # Send webhook notification
            await self.send_webhook_alert(alert)
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def broadcast_alert(self, embed: discord.Embed):
        """Broadcast alert to all configured channels"""
        try:
            for guild in self.bot.guilds:
                # Look specifically for general-events or general-logs channels first
                target_channel = None
                for channel in guild.text_channels:
                    if channel.name.lower() in ['general-events', 'general-logs']:
                        if channel.permissions_for(guild.me).send_messages:
                            target_channel = channel
                            break
                
                # If no general-events or general-logs channels, look for other alert channels
                if not target_channel:
                    for channel in guild.text_channels:
                        if any(keyword in channel.name.lower() for keyword in ['alert', 'monitor', 'performance', 'log', 'events']):
                            if channel.permissions_for(guild.me).send_messages:
                                target_channel = channel
                                break
                
                # If no specific channels, use system channel
                if not target_channel and guild.system_channel:
                    if guild.system_channel.permissions_for(guild.me).send_messages:
                        target_channel = guild.system_channel
                
                # Send to found channel
                if target_channel:
                    try:
                        await target_channel.send(embed=embed)
                        logger.info(f"Performance alert sent to {target_channel.name} in {guild.name}")
                    except discord.Forbidden:
                        logger.warning(f"No permission to send performance alert in {guild.name}")
                        
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")
    
    async def log_alert(self, alert: Dict):
        """Log alert to database"""
        try:
            if not self.bot.db_pool:
                return
                
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_alerts (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL,
                        alert_type VARCHAR(50),
                        level VARCHAR(20),
                        message TEXT,
                        value FLOAT,
                        threshold FLOAT,
                        raw_data JSONB
                    )
                """)
                
                await conn.execute("""
                    INSERT INTO performance_alerts (
                        timestamp, alert_type, level, message, value, threshold, raw_data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                    datetime.utcnow(),
                    alert['type'],
                    alert['level'],
                    alert['message'],
                    alert['value'],
                    alert['threshold'],
                    json.dumps(alert)
                )
                
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
    
    async def send_webhook_alert(self, alert: Dict):
        """Send alert via webhook for external monitoring"""
        try:
            webhook_url = "http://localhost:5001/api/bot/performance-alert"
            
            async with aiohttp.ClientSession() as session:
                await session.post(webhook_url, json={
                    'timestamp': datetime.utcnow().isoformat(),
                    'alert': alert,
                    'source': 'nexguard_performance_monitor'
                })
                
        except Exception as e:
            logger.debug(f"Webhook alert failed (expected): {e}")
    
    @discord.app_commands.command(name="performance")
    @discord.app_commands.describe(action="Action to perform")
    async def performance_command(self, interaction: discord.Interaction, action: str = "status"):
        """View performance monitoring information"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ You need 'Manage Server' permission to use this command.",
                ephemeral=True
            )
            return
        
        if action.lower() == "status":
            # Get current metrics
            current_metrics = await self.collect_metrics()
            
            embed = discord.Embed(
                title="📊 Performance Status",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            
            if current_metrics:
                cpu = current_metrics.get('cpu', {})
                memory = current_metrics.get('memory', {})
                disk = current_metrics.get('disk', {})
                bot = current_metrics.get('bot', {})
                
                embed.add_field(
                    name="🖥️ CPU Usage",
                    value=f"{cpu.get('percent', 0):.1f}%",
                    inline=True
                )
                embed.add_field(
                    name="💾 Memory Usage",
                    value=f"{memory.get('percent', 0):.1f}%\n({memory.get('used_gb', 0):.1f}GB / {memory.get('total_gb', 0):.1f}GB)",
                    inline=True
                )
                embed.add_field(
                    name="💽 Disk Usage",
                    value=f"{disk.get('percent', 0):.1f}%\n({disk.get('used_gb', 0):.1f}GB / {disk.get('total_gb', 0):.1f}GB)",
                    inline=True
                )
                embed.add_field(
                    name="📡 Bot Latency",
                    value=f"{bot.get('latency_ms', 0):.1f}ms",
                    inline=True
                )
                embed.add_field(
                    name="🏰 Servers",
                    value=f"{bot.get('guilds', 0):,}",
                    inline=True
                )
                embed.add_field(
                    name="👥 Users",
                    value=f"{bot.get('users', 0):,}",
                    inline=True
                )
            
            embed.add_field(
                name="📈 Monitoring",
                value="Active" if self.monitoring_active else "Disabled",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        else:
            await interaction.response.send_message(
                "❌ Invalid action. Use: `status`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(PerformanceMonitor(bot))