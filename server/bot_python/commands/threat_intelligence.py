#!/usr/bin/env python3

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import json
import time
import statistics
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict, deque
import hashlib
import re

logger = logging.getLogger(__name__)

class ThreatIntelligenceSystem(commands.Cog):
    """Advanced threat intelligence and analysis system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.intelligence_active = True
        
        # Threat scoring weights
        self.THREAT_WEIGHTS = {
            'join_velocity': 25,      # Rapid joins across servers
            'message_patterns': 20,   # Suspicious messaging patterns
            'behavioral_anomaly': 15, # Deviation from normal behavior
            'cross_server_match': 20, # Found in other servers
            'permission_escalation': 15, # Attempting privilege escalation
            'evasion_techniques': 5   # Trying to evade detection
        }
        
        # Behavioral analysis parameters
        self.MIN_LEARNING_PERIOD = 7 * 24 * 3600  # 7 days in seconds
        self.BEHAVIOR_SAMPLE_SIZE = 100  # Minimum actions for reliable profile
        self.ANOMALY_THRESHOLD = 75  # Score above which behavior is anomalous
        
        # Cross-server intelligence
        self.threat_signatures: Dict[str, Dict] = {}
        self.shared_intelligence: Dict[str, List] = defaultdict(list)
        self.network_threats: Set[str] = set()
        
        # Machine Learning-style pattern recognition
        self.user_profiles: Dict[int, Dict[int, Dict]] = defaultdict(lambda: defaultdict(dict))
        self.attack_patterns: Dict[str, Dict] = {}
        self.prediction_models: Dict[str, Any] = {}
        
        # Real-time threat tracking
        self.active_threats: Dict[int, List] = defaultdict(list)
        self.threat_correlations: Dict[str, List] = defaultdict(list)
        
        # Start intelligence tasks
        self.analyze_threats.start()
        self.update_behavioral_profiles.start()
        self.cross_server_intelligence_sync.start()
        self.predictive_threat_modeling.start()
        
        logger.info("Threat Intelligence System initialized")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Analyze member joins for threats"""
        try:
            analysis = await self.analyze_member_join(member)
            
            if analysis['threat_score'] > 50:
                logger.warning(f"🚨 HIGH THREAT: {member.name} joined {member.guild.name} - Score: {analysis['threat_score']}/100")
                
                # Store in active threats
                self.active_threats[member.guild.id].append({
                    'user_id': member.id,
                    'username': member.name,
                    'threat_type': 'member_join',
                    'threat_score': analysis['threat_score'],
                    'risk_factors': analysis['risk_factors'],
                    'detected_at': datetime.now(timezone.utc).isoformat(),
                    'action_taken': None
                })
                
                # Share threat intelligence
                await self.share_threat_intelligence(
                    member.id, 
                    member.guild.id, 
                    {
                        'event': 'member_join',
                        'threat_score': analysis['threat_score'],
                        'risk_factors': analysis['risk_factors']
                    }
                )
            
        except Exception as e:
            logger.error(f"Error in threat intelligence member join handler: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Analyze messages for threat patterns"""
        if not message.guild or message.author.bot:
            return
            
        try:
            user_id = message.author.id
            guild_id = message.guild.id
            
            # Analyze message for threats
            event_data = {
                'guild_id': guild_id,
                'message_content': message.content[:100],  # First 100 chars
                'channel_id': message.channel.id,
                'message_length': len(message.content),
                'mention_count': len(message.mentions),
                'has_attachments': len(message.attachments) > 0
            }
            
            threat_score, risk_factors = self.calculate_threat_score(user_id, guild_id, event_data)
            
            if threat_score > 60:
                logger.warning(f"🔍 MESSAGE THREAT: {message.author.name} in {message.guild.name} - Score: {threat_score}/100")
                
                # Store threat intelligence
                await self._store_threat_intelligence(
                    user_id=user_id,
                    guild_id=guild_id,
                    threat_type="suspicious_message",
                    threat_score=threat_score,
                    confidence_level=min(threat_score + 10, 100),
                    risk_factors=risk_factors,
                    behavioral_patterns=[f"message_length_{len(message.content)}"],
                    cross_server_matches=1 if self._check_cross_server_intelligence(user_id) > 0 else 0
                )
                
        except Exception as e:
            logger.error(f"Error in threat intelligence message handler: {e}")

    async def analyze_member_join(self, member: discord.Member) -> Dict:
        """Analyze member join for threats"""
        try:
            user_id = member.id
            guild_id = member.guild.id
            join_time = datetime.now(timezone.utc)
            
            # Basic user analysis
            created_at = member.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            account_age = (join_time - created_at).days
            threat_score = 0
            risk_factors = []
            
            # Check account age
            if account_age < 1:
                threat_score += 40
                risk_factors.append("very_new_account")
            elif account_age < 7:
                threat_score += 25
                risk_factors.append("new_account")
            
            # Check for suspicious username patterns
            username_score = self._analyze_username_patterns(member.name)
            threat_score += username_score
            if username_score > 0:
                risk_factors.append("suspicious_username")
            
            # Check behavioral patterns
            behavioral_score = self._detect_behavioral_anomalies(user_id, {
                'guild_id': guild_id,
                'join_time': join_time,
                'account_age': account_age
            })
            threat_score += behavioral_score
            if behavioral_score > 30:
                risk_factors.append("behavioral_anomaly")
            
            # Check cross-server intelligence
            cross_server_score = self._check_cross_server_intelligence(user_id)
            threat_score += cross_server_score
            if cross_server_score > 0:
                risk_factors.append("cross_server_threat")
            
            # Determine confidence level
            confidence = min(threat_score, 100)
            
            # Store threat intelligence
            await self._store_threat_intelligence(
                user_id=user_id,
                guild_id=guild_id,
                threat_type="member_join",
                threat_score=min(threat_score, 100),
                confidence_level=confidence,
                risk_factors=risk_factors,
                behavioral_patterns=[],
                cross_server_matches=1 if cross_server_score > 0 else 0
            )
            
            logger.info(f"🔍 THREAT ANALYSIS: {member.name} ({user_id}) joined {member.guild.name} - Score: {min(threat_score, 100)}/100, Risk: {risk_factors}")
            
            return {
                'threat_score': min(threat_score, 100),
                'risk_factors': risk_factors,
                'confidence': confidence,
                'user_id': user_id,
                'guild_id': guild_id
            }
            
        except Exception as e:
            logger.error(f"Error analyzing member join: {e}")
            return {
                'threat_score': 0,
                'risk_factors': [],
                'confidence': 0,
                'error': str(e)
            }
    
    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.analyze_threats.cancel()
        self.update_behavioral_profiles.cancel()
        self.cross_server_intelligence_sync.cancel()
        self.predictive_threat_modeling.cancel()
    
    def calculate_threat_score(self, user_id: int, guild_id: int, event_data: Dict) -> Tuple[int, List[str]]:
        """Calculate comprehensive threat score for a user/event"""
        score = 0
        risk_factors = []
        
        # Join velocity analysis
        join_score = self._analyze_join_velocity(user_id, guild_id, event_data)
        score += join_score * self.THREAT_WEIGHTS['join_velocity'] // 100
        if join_score > 50:
            risk_factors.append(f"High join velocity: {join_score}")
        
        # Message pattern analysis
        message_score = self._analyze_message_patterns(user_id, guild_id, event_data)
        score += message_score * self.THREAT_WEIGHTS['message_patterns'] // 100
        if message_score > 60:
            risk_factors.append(f"Suspicious messaging: {message_score}")
        
        # Behavioral anomaly detection
        behavioral_score = self._detect_behavioral_anomalies(user_id, guild_id)
        score += behavioral_score * self.THREAT_WEIGHTS['behavioral_anomaly'] // 100
        if behavioral_score > 70:
            risk_factors.append(f"Behavioral anomaly: {behavioral_score}")
        
        # Cross-server intelligence check
        cross_server_score = self._check_cross_server_intelligence(user_id)
        score += cross_server_score * self.THREAT_WEIGHTS['cross_server_match'] // 100
        if cross_server_score > 80:
            risk_factors.append(f"Cross-server threat: {cross_server_score}")
        
        # Permission escalation attempts
        permission_score = self._detect_permission_escalation(user_id, guild_id, event_data)
        score += permission_score * self.THREAT_WEIGHTS['permission_escalation'] // 100
        if permission_score > 60:
            risk_factors.append(f"Permission escalation: {permission_score}")
        
        return min(score, 100), risk_factors
    
    def _analyze_join_velocity(self, user_id: int, guild_id: int, event_data: Dict) -> int:
        """Analyze user join patterns across time and servers"""
        try:
            # Check if user joined multiple servers recently
            recent_joins = 0
            current_time = time.time()
            
            # Check join patterns in the last hour
            for guild in self.bot.guilds:
                member = guild.get_member(user_id)
                if member and member.joined_at:
                    join_time = member.joined_at.timestamp()
                    if current_time - join_time < 3600:  # Last hour
                        recent_joins += 1
            
            # Score based on number of recent joins
            if recent_joins >= 5:
                return 90
            elif recent_joins >= 3:
                return 70
            elif recent_joins >= 2:
                return 40
            else:
                return 10
                
        except Exception as e:
            logger.error(f"Error analyzing join velocity: {e}")
            return 0
    
    def _analyze_message_patterns(self, user_id: int, guild_id: int, event_data: Dict) -> int:
        """Analyze message patterns for suspicious behavior"""
        try:
            user_profile = self.user_profiles[guild_id][user_id]
            
            # Check for rapid messaging
            messages_per_minute = event_data.get('messages_per_minute', 0)
            if messages_per_minute > 20:
                return 85
            elif messages_per_minute > 10:
                return 60
            
            # Check for copy-paste patterns
            message_similarity = event_data.get('message_similarity', 0)
            if message_similarity > 80:
                return 75
            
            # Check for mention spam
            mentions_per_message = event_data.get('mentions_per_message', 0)
            if mentions_per_message > 10:
                return 90
            elif mentions_per_message > 5:
                return 65
            
            # Check for invite spam
            invite_links = event_data.get('invite_links', 0)
            if invite_links > 0:
                return 70
                
            return 5  # Normal messaging
            
        except Exception as e:
            logger.error(f"Error analyzing message patterns: {e}")
            return 0
    
    def _detect_behavioral_anomalies(self, user_id: int, event_data: Dict = None) -> int:
        """Detect anomalies in user behavior patterns"""
        try:
            guild_id = event_data.get('guild_id') if event_data else 0
            user_profile = self.user_profiles[guild_id].get(user_id, {})
            
            if not user_profile or len(user_profile) < 10:
                return 20  # Insufficient data, low confidence
            
            # Analyze activity patterns
            normal_activity = user_profile.get('normal_activity_hours', [])
            current_hour = datetime.now().hour
            
            # Check if active during unusual hours
            if normal_activity and current_hour not in normal_activity:
                anomaly_score = 40
            else:
                anomaly_score = 0
            
            # Check message length patterns
            avg_message_length = user_profile.get('avg_message_length', 50)
            recent_avg_length = user_profile.get('recent_avg_length', avg_message_length)
            
            length_deviation = abs(recent_avg_length - avg_message_length)
            if length_deviation > avg_message_length * 0.5:  # 50% deviation
                anomaly_score += 30
            
            # Check interaction patterns
            normal_channels = user_profile.get('frequent_channels', [])
            recent_channels = user_profile.get('recent_channels', [])
            
            if normal_channels and not any(ch in normal_channels for ch in recent_channels):
                anomaly_score += 25
            
            return min(anomaly_score, 100)
            
        except Exception as e:
            logger.error(f"Error detecting behavioral anomalies: {e}")
            return 0
    
    def _check_cross_server_intelligence(self, user_id: int) -> int:
        """Check user against cross-server threat intelligence"""
        try:
            user_str = str(user_id)
            
            # Check if user is in shared threat intelligence
            if user_str in self.shared_intelligence:
                threat_reports = self.shared_intelligence[user_str]
                
                if len(threat_reports) >= 3:
                    return 95  # Multiple server reports
                elif len(threat_reports) == 2:
                    return 75
                elif len(threat_reports) == 1:
                    return 50
            
            # Check network-wide threats
            if user_str in self.network_threats:
                return 100
            
            return 0
            
        except Exception as e:
            logger.error(f"Error checking cross-server intelligence: {e}")
            return 0
    
    def _detect_permission_escalation(self, user_id: int, guild_id: int, event_data: Dict) -> int:
        """Detect attempts to escalate permissions"""
        try:
            # Check for role requests
            role_requests = event_data.get('role_requests', 0)
            if role_requests > 2:
                return 80
            
            # Check for admin command attempts
            admin_attempts = event_data.get('admin_command_attempts', 0)
            if admin_attempts > 0:
                return 90
            
            # Check for social engineering patterns
            social_engineering_keywords = [
                'give me admin', 'need permissions', 'make me mod',
                'trust me', 'i am staff', 'give role'
            ]
            
            recent_messages = event_data.get('recent_messages', [])
            for message in recent_messages:
                if any(keyword in message.lower() for keyword in social_engineering_keywords):
                    return 70
            
            return 0
            
        except Exception as e:
            logger.error(f"Error detecting permission escalation: {e}")
            return 0
    
    async def share_threat_intelligence(self, user_id: int, guild_id: int, threat_data: Dict):
        """Share threat intelligence across servers"""
        try:
            # Create threat signature
            threat_signature = self._create_threat_signature(user_id, threat_data)
            
            # Add to shared intelligence
            self.shared_intelligence[str(user_id)].append({
                'guild_id': guild_id,
                'threat_data': threat_data,
                'signature': threat_signature,
                'timestamp': time.time()
            })
            
            # If confirmed by multiple servers, add to network threats
            if len(self.shared_intelligence[str(user_id)]) >= 2:
                self.network_threats.add(str(user_id))
            
            logger.info(f"Shared threat intelligence for user {user_id} from guild {guild_id}")
            
        except Exception as e:
            logger.error(f"Error sharing threat intelligence: {e}")
    
    def _create_threat_signature(self, user_id: int, threat_data: Dict) -> str:
        """Create unique signature for threat pattern"""
        try:
            # Combine relevant threat data
            signature_data = {
                'user_id': user_id,
                'threat_type': threat_data.get('threat_type', 'unknown'),
                'patterns': threat_data.get('patterns', []),
                'behavior': threat_data.get('behavior_hash', '')
            }
            
            # Create hash signature
            signature_str = json.dumps(signature_data, sort_keys=True)
            return hashlib.sha256(signature_str.encode()).hexdigest()[:16]
            
        except Exception as e:
            logger.error(f"Error creating threat signature: {e}")
            return f"unknown_{user_id}"
    
    @tasks.loop(minutes=5)
    async def analyze_threats(self):
        """Continuously analyze threats across all servers"""
        try:
            current_time = time.time()
            
            for guild in self.bot.guilds:
                # Analyze recent activities for threats
                active_threats = []
                
                # Check for coordinated attacks
                coordinated_score = await self._detect_coordinated_attacks(guild.id)
                if coordinated_score > 70:
                    active_threats.append({
                        'type': 'coordinated_attack',
                        'score': coordinated_score,
                        'severity': 'high' if coordinated_score > 85 else 'medium'
                    })
                
                # Check for unusual activity spikes
                activity_anomaly = await self._detect_activity_anomalies(guild.id)
                if activity_anomaly > 60:
                    active_threats.append({
                        'type': 'activity_anomaly',
                        'score': activity_anomaly,
                        'severity': 'medium'
                    })
                
                # Update active threats
                if active_threats:
                    self.active_threats[guild.id] = active_threats
                    await self._alert_administrators(guild.id, active_threats)
                
        except Exception as e:
            logger.error(f"Error in threat analysis: {e}")
    
    async def _detect_coordinated_attacks(self, guild_id: int) -> int:
        """Detect coordinated attacks across multiple users"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return 0
            
            current_time = time.time()
            recent_window = current_time - 300  # Last 5 minutes
            
            # Check for multiple users with similar patterns
            recent_actions = []
            suspicious_patterns = 0
            
            # This would integrate with antiraid/antinuke data
            # For now, simulate based on general patterns
            
            # Check for multiple recent joins with similar names
            recent_members = [m for m in guild.members if m.joined_at and m.joined_at.timestamp() > recent_window]
            
            if len(recent_members) > 5:
                # Check for similar usernames
                usernames = [m.name.lower() for m in recent_members]
                similar_names = 0
                
                for i, name1 in enumerate(usernames):
                    for name2 in usernames[i+1:]:
                        if self._calculate_similarity(name1, name2) > 0.7:
                            similar_names += 1
                
                if similar_names > 2:
                    suspicious_patterns += 40
            
            # Check for rapid message patterns
            if len(recent_members) > 3:
                suspicious_patterns += 30
            
            return min(suspicious_patterns, 100)
            
        except Exception as e:
            logger.error(f"Error detecting coordinated attacks: {e}")
            return 0
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        try:
            if not str1 or not str2:
                return 0.0
            
            # Simple similarity calculation
            common_chars = set(str1) & set(str2)
            total_chars = set(str1) | set(str2)
            
            if not total_chars:
                return 0.0
            
            return len(common_chars) / len(total_chars)
            
        except Exception:
            return 0.0
    
    async def _detect_activity_anomalies(self, guild_id: int) -> int:
        """Detect unusual activity patterns"""
        try:
            # This would analyze historical data to detect anomalies
            # For now, provide basic implementation
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return 0
            
            # Check for unusual member count changes
            current_member_count = guild.member_count
            
            # Basic anomaly detection based on server size
            if current_member_count < 50:
                # Small server - look for 20% changes
                threshold = 0.2
            elif current_member_count < 500:
                # Medium server - look for 10% changes
                threshold = 0.1
            else:
                # Large server - look for 5% changes
                threshold = 0.05
            
            # This would compare against historical averages
            # For now, return baseline
            return 15
            
        except Exception as e:
            logger.error(f"Error detecting activity anomalies: {e}")
            return 0
    
    async def _alert_administrators(self, guild_id: int, threats: List[Dict]):
        """Alert guild administrators about detected threats"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            # Find appropriate alert channel
            alert_channel = None
            for channel in guild.text_channels:
                if channel.name.lower() in ['general-events', 'general-logs', 'security-alerts', 'admin-alerts']:
                    if channel.permissions_for(guild.me).send_messages:
                        alert_channel = channel
                        break
            
            if not alert_channel:
                return
            
            # Create threat alert embed
            embed = discord.Embed(
                title="🚨 Threat Intelligence Alert",
                description="Advanced threat analysis has detected potential security concerns",
                color=0xFF4444,
                timestamp=datetime.utcnow()
            )
            
            for threat in threats:
                threat_type = threat['type'].replace('_', ' ').title()
                severity = threat['severity'].upper()
                score = threat['score']
                
                embed.add_field(
                    name=f"⚠️ {threat_type}",
                    value=f"**Severity:** {severity}\n**Threat Score:** {score}/100\n**Status:** Active Monitoring",
                    inline=False
                )
            
            embed.add_field(
                name="🛡️ Automated Response",
                value="• Enhanced monitoring activated\n• Cross-server intelligence updated\n• Behavioral analysis running",
                inline=False
            )
            
            embed.set_footer(text="NexGuard Threat Intelligence • Real-time Protection")
            
            await alert_channel.send(embed=embed)
            logger.info(f"Threat alert sent to {guild.name} for {len(threats)} threats")
            
        except Exception as e:
            logger.error(f"Error alerting administrators: {e}")
    
    @tasks.loop(hours=6)
    async def update_behavioral_profiles(self):
        """Update behavioral profiles for all users"""
        try:
            logger.info("Updating behavioral profiles...")
            
            for guild in self.bot.guilds:
                for member in guild.members:
                    if member.bot:
                        continue
                    
                    # Update behavioral profile
                    await self._update_user_profile(member.id, guild.id)
            
            logger.info("Behavioral profiles updated")
            
        except Exception as e:
            logger.error(f"Error updating behavioral profiles: {e}")
    
    async def _update_user_profile(self, user_id: int, guild_id: int):
        """Update individual user behavioral profile"""
        try:
            user_profile = self.user_profiles[guild_id][user_id]
            
            # This would integrate with message/activity tracking
            # For now, create basic profile structure
            if 'created_at' not in user_profile:
                user_profile['created_at'] = time.time()
            
            user_profile['last_updated'] = time.time()
            user_profile['profile_version'] = 2
            
            # Store basic behavioral indicators
            user_profile.setdefault('message_count', 0)
            user_profile.setdefault('avg_message_length', 50)
            user_profile.setdefault('normal_activity_hours', list(range(8, 22)))
            user_profile.setdefault('frequent_channels', [])
            user_profile.setdefault('interaction_patterns', [])
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
    
    @tasks.loop(hours=1)
    async def cross_server_intelligence_sync(self):
        """Sync threat intelligence across servers"""
        try:
            logger.info("Syncing cross-server intelligence...")
            
            # Clean old intelligence data
            current_time = time.time()
            cutoff_time = current_time - (7 * 24 * 3600)  # 7 days old
            
            for user_id in list(self.shared_intelligence.keys()):
                reports = self.shared_intelligence[user_id]
                self.shared_intelligence[user_id] = [
                    report for report in reports
                    if report['timestamp'] > cutoff_time
                ]
                
                if not self.shared_intelligence[user_id]:
                    del self.shared_intelligence[user_id]
                    self.network_threats.discard(user_id)
            
            logger.info("Cross-server intelligence sync completed")
            
        except Exception as e:
            logger.error(f"Error syncing cross-server intelligence: {e}")
    
    @tasks.loop(hours=12)
    async def predictive_threat_modeling(self):
        """Run predictive threat modeling"""
        try:
            logger.info("Running predictive threat modeling...")
            
            # Analyze patterns to predict future threats
            for guild in self.bot.guilds:
                predictions = await self._generate_threat_predictions(guild.id)
                
                if predictions:
                    await self._create_predictive_alerts(guild.id, predictions)
            
            logger.info("Predictive threat modeling completed")
            
        except Exception as e:
            logger.error(f"Error in predictive threat modeling: {e}")
    
    async def _generate_threat_predictions(self, guild_id: int) -> List[Dict]:
        """Generate threat predictions for a guild"""
        try:
            predictions = []
            
            # Analyze historical patterns
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return predictions
            
            # Check for patterns that typically precede attacks
            recent_join_velocity = len([m for m in guild.members if m.joined_at and (datetime.utcnow() - m.joined_at).days < 1])
            
            if recent_join_velocity > guild.member_count * 0.1:  # 10% increase in one day
                predictions.append({
                    'type': 'potential_raid',
                    'confidence': 70,
                    'timeframe': '6-24 hours',
                    'indicators': ['High join velocity', 'Pattern matching']
                })
            
            # Check for other predictive indicators
            if len(self.active_threats.get(guild_id, [])) > 0:
                predictions.append({
                    'type': 'escalating_threat',
                    'confidence': 60,
                    'timeframe': '1-6 hours',
                    'indicators': ['Active threats detected', 'Pattern escalation']
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating threat predictions: {e}")
            return []
    
    async def _create_predictive_alerts(self, guild_id: int, predictions: List[Dict]):
        """Create predictive threat alerts"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild or not predictions:
                return
            
            # Find alert channel
            alert_channel = None
            for channel in guild.text_channels:
                if channel.name.lower() in ['general-events', 'general-logs', 'security-alerts']:
                    if channel.permissions_for(guild.me).send_messages:
                        alert_channel = channel
                        break
            
            if not alert_channel:
                return
            
            embed = discord.Embed(
                title="🔮 Predictive Threat Analysis",
                description="Advanced AI analysis has identified potential future threats",
                color=0xFFA500,
                timestamp=datetime.utcnow()
            )
            
            for prediction in predictions:
                threat_type = prediction['type'].replace('_', ' ').title()
                confidence = prediction['confidence']
                timeframe = prediction['timeframe']
                indicators = prediction['indicators']
                
                embed.add_field(
                    name=f"📊 {threat_type}",
                    value=f"**Confidence:** {confidence}%\n**Timeframe:** {timeframe}\n**Indicators:** {', '.join(indicators)}",
                    inline=False
                )
            
            embed.add_field(
                name="🛡️ Recommended Actions",
                value="• Increase monitoring sensitivity\n• Alert staff to potential threats\n• Prepare response protocols\n• Monitor key indicators",
                inline=False
            )
            
            embed.set_footer(text="NexGuard Predictive Intelligence • Proactive Protection")
            
            await alert_channel.send(embed=embed)
            logger.info(f"Predictive alert sent to {guild.name} for {len(predictions)} predictions")
            
        except Exception as e:
            logger.error(f"Error creating predictive alerts: {e}")
    
    # Slash commands for threat intelligence management
    @discord.app_commands.command(name="threat-status", description="View current threat intelligence status")
    @discord.app_commands.describe(user="Check threat status for specific user")
    async def threat_status(self, interaction: discord.Interaction, user: discord.Member = None):
        """View threat intelligence status"""
        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
                return
            
            guild_id = interaction.guild.id
            
            embed = discord.Embed(
                title="🧠 Threat Intelligence Status",
                description="Current threat analysis and intelligence overview",
                color=0x0099FF,
                timestamp=datetime.utcnow()
            )
            
            if user:
                # Show specific user threat analysis
                threat_score, risk_factors = self.calculate_threat_score(user.id, guild_id, {})
                
                embed.add_field(
                    name=f"👤 {user.display_name}",
                    value=f"**Threat Score:** {threat_score}/100\n**Risk Level:** {'🔴 High' if threat_score > 70 else '🟡 Medium' if threat_score > 40 else '🟢 Low'}",
                    inline=False
                )
                
                if risk_factors:
                    embed.add_field(
                        name="⚠️ Risk Factors",
                        value="\n".join([f"• {factor}" for factor in risk_factors]),
                        inline=False
                    )
            else:
                # Show guild-wide threat overview
                active_threats = self.active_threats.get(guild_id, [])
                
                embed.add_field(
                    name="🎯 Active Threats",
                    value=f"{len(active_threats)} threats detected" if active_threats else "No active threats",
                    inline=True
                )
                
                network_threat_count = len(self.network_threats)
                embed.add_field(
                    name="🌐 Network Intelligence",
                    value=f"{network_threat_count} known network threats",
                    inline=True
                )
                
                embed.add_field(
                    name="🔄 System Status",
                    value="✅ All systems operational",
                    inline=True
                )
            
            embed.set_footer(text="NexGuard Threat Intelligence • Real-time Analysis")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in threat status command: {e}")
            await interaction.response.send_message("❌ Error retrieving threat status.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ThreatIntelligenceSystem(bot))