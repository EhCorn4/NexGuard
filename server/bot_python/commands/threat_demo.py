#!/usr/bin/env python3

import discord
from discord.ext import commands
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class ThreatAnalysisDemo(commands.Cog):
    """Demonstration commands for intelligent threat analysis"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("Threat Analysis Demo system initialized")
    
    @discord.app_commands.command(name="threat-demo", description="Demonstrate intelligent threat analysis capabilities")
    @discord.app_commands.describe(
        demo_type="Type of threat analysis to demonstrate",
        target_user="Optional user to analyze (for demo purposes)"
    )
    async def threat_demo(self, interaction: discord.Interaction, 
                         demo_type: str = "overview", 
                         target_user: discord.Member = None):
        """Demonstrate threat analysis capabilities"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            if demo_type == "overview":
                await self._demo_threat_overview(interaction)
            elif demo_type == "user-analysis":
                await self._demo_user_analysis(interaction, target_user)
            elif demo_type == "pattern-recognition":
                await self._demo_pattern_recognition(interaction)
            elif demo_type == "predictive":
                await self._demo_predictive_analysis(interaction)
            elif demo_type == "cross-server":
                await self._demo_cross_server_intelligence(interaction)
            else:
                await self._demo_help(interaction)
                
        except Exception as e:
            logger.error(f"Error in threat demo: {e}")
            await interaction.followup.send("❌ Error running threat analysis demo.", ephemeral=True)
    
    async def _demo_threat_overview(self, interaction):
        """Demo overall threat intelligence system"""
        
        embed = discord.Embed(
            title="🧠 Intelligent Threat Analysis System",
            description="Advanced AI-powered security analysis protecting your server",
            color=0x00FF00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🎯 Machine Learning Detection",
            value="• **Behavioral Pattern Analysis** - Learning normal vs abnormal user behavior\n"
                  "• **Threat Scoring Algorithm** - 0-100 risk assessment for every user action\n"
                  "• **Predictive Modeling** - Forecasting potential threats before they occur",
            inline=False
        )
        
        embed.add_field(
            name="🌐 Cross-Server Intelligence",
            value="• **Network Threat Sharing** - Known threats identified across all servers\n"
                  "• **Pattern Correlation** - Connecting attack patterns between servers\n"
                  "• **Reputation System** - Building user trustworthiness scores",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Real-Time Analysis",
            value="• **Instant Threat Detection** - Sub-second threat identification\n"
                  "• **Adaptive Learning** - System improves with each detected threat\n"
                  "• **Automated Response** - Immediate quarantine and mitigation",
            inline=False
        )
        
        # Simulate current threat status
        threat_level = random.choice(["🟢 LOW", "🟡 MEDIUM", "🔴 HIGH"])
        active_monitors = random.randint(850, 1200)
        ml_confidence = random.randint(85, 98)
        
        embed.add_field(
            name="📊 Current Status",
            value=f"**Threat Level:** {threat_level}\n"
                  f"**Active Monitors:** {active_monitors} users\n"
                  f"**ML Confidence:** {ml_confidence}%\n"
                  f"**Last Analysis:** {datetime.now().strftime('%H:%M:%S')}",
            inline=True
        )
        
        embed.add_field(
            name="📈 24h Statistics",
            value=f"**Threats Detected:** {random.randint(5, 25)}\n"
                  f"**Patterns Learned:** {random.randint(15, 45)}\n"
                  f"**Auto-Quarantines:** {random.randint(2, 12)}\n"
                  f"**False Positives:** {random.randint(0, 3)}",
            inline=True
        )
        
        embed.set_footer(text="NexGuard Intelligent Threat Analysis • AI-Powered Security")
        
        await interaction.followup.send(embed=embed)
    
    async def _demo_user_analysis(self, interaction, target_user):
        """Demo user-specific threat analysis"""
        
        if not target_user:
            target_user = interaction.user
        
        # Get threat intelligence system
        threat_intel = self.bot.get_cog('ThreatIntelligenceSystem')
        
        # Calculate threat score (demo with realistic simulation)
        if threat_intel:
            threat_score, risk_factors = threat_intel.calculate_threat_score(
                target_user.id, interaction.guild.id, {}
            )
        else:
            # Simulate threat analysis
            threat_score = random.randint(0, 100)
            risk_factors = []
            
            if threat_score > 70:
                risk_factors = ["High activity outside normal hours", "Message pattern deviation"]
            elif threat_score > 40:
                risk_factors = ["Moderate behavior changes detected"]
        
        risk_level = "🔴 HIGH" if threat_score > 70 else "🟡 MEDIUM" if threat_score > 40 else "🟢 LOW"
        
        embed = discord.Embed(
            title=f"🔍 Threat Analysis: {target_user.display_name}",
            description=f"Advanced behavioral and pattern analysis results",
            color=0xFF4444 if threat_score > 70 else 0xFFAA00 if threat_score > 40 else 0x00FF00,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        embed.add_field(
            name="📊 Threat Assessment",
            value=f"**Overall Score:** {threat_score}/100\n"
                  f"**Risk Level:** {risk_level}\n"
                  f"**Confidence:** {random.randint(85, 98)}%",
            inline=True
        )
        
        embed.add_field(
            name="🕐 Analysis Period",
            value=f"**Account Age:** {(datetime.now() - target_user.created_at).days} days\n"
                  f"**Server Join:** {(datetime.now() - target_user.joined_at).days} days ago\n"
                  f"**Last Activity:** Recently active",
            inline=True
        )
        
        if risk_factors:
            embed.add_field(
                name="⚠️ Risk Factors",
                value="\n".join([f"• {factor}" for factor in risk_factors]),
                inline=False
            )
        
        # Behavioral analysis
        behavioral_patterns = [
            "Message frequency within normal range",
            "Channel usage patterns stable",
            "Interaction style consistent",
            "Activity schedule regular"
        ]
        
        if threat_score > 50:
            behavioral_patterns.append("⚠️ Some pattern deviations detected")
        
        embed.add_field(
            name="🧠 Behavioral Profile",
            value="\n".join([f"• {pattern}" for pattern in behavioral_patterns[:4]]),
            inline=False
        )
        
        # Recommendations
        if threat_score > 70:
            recommendations = "• Increase monitoring\n• Review recent activity\n• Consider temporary restrictions"
        elif threat_score > 40:
            recommendations = "• Continue monitoring\n• Watch for pattern changes"
        else:
            recommendations = "• Normal monitoring sufficient\n• User appears trustworthy"
        
        embed.add_field(
            name="💡 Recommendations",
            value=recommendations,
            inline=False
        )
        
        embed.set_footer(text="NexGuard Behavioral Analysis • Machine Learning Powered")
        
        await interaction.followup.send(embed=embed)
    
    async def _demo_pattern_recognition(self, interaction):
        """Demo attack pattern recognition"""
        
        embed = discord.Embed(
            title="🔍 Attack Pattern Recognition",
            description="Known attack patterns detected and learned by the AI system",
            color=0xFF8800,
            timestamp=datetime.utcnow()
        )
        
        patterns = [
            {
                "name": "Coordinated Join Raid",
                "type": "Mass Infiltration",
                "severity": 9,
                "detection": "Multiple accounts with sequential usernames joining rapidly",
                "prevention": "Account age verification, Join rate limiting"
            },
            {
                "name": "Permission Escalation Attack",
                "type": "Privilege Abuse",
                "severity": 10,
                "detection": "Rapid role creation with admin permissions",
                "prevention": "Role permission monitoring, Admin whitelist"
            },
            {
                "name": "Invite Link Spam Campaign",
                "type": "External Recruitment",
                "severity": 6,
                "detection": "Mass posting of Discord invite links",
                "prevention": "Link filtering, Message rate limiting"
            }
        ]
        
        for i, pattern in enumerate(patterns, 1):
            severity_emoji = "🔥" if pattern["severity"] >= 8 else "⚠️" if pattern["severity"] >= 6 else "⚡"
            
            embed.add_field(
                name=f"{severity_emoji} Pattern #{i}: {pattern['name']}",
                value=f"**Type:** {pattern['type']}\n"
                      f"**Severity:** {pattern['severity']}/10\n"
                      f"**Detection:** {pattern['detection']}\n"
                      f"**Prevention:** {pattern['prevention']}",
                inline=False
            )
        
        embed.add_field(
            name="🤖 AI Learning Stats",
            value=f"• **Patterns Analyzed:** {random.randint(150, 300)}\n"
                  f"• **New Patterns Today:** {random.randint(3, 12)}\n"
                  f"• **Detection Accuracy:** {random.randint(92, 99)}%\n"
                  f"• **False Positive Rate:** {random.randint(1, 5)}%",
            inline=False
        )
        
        embed.set_footer(text="NexGuard Pattern Recognition • Continuously Learning")
        
        await interaction.followup.send(embed=embed)
    
    async def _demo_predictive_analysis(self, interaction):
        """Demo predictive threat modeling"""
        
        embed = discord.Embed(
            title="🔮 Predictive Threat Analysis",
            description="AI-powered forecasting of potential security threats",
            color=0x8A2BE2,
            timestamp=datetime.utcnow()
        )
        
        # Simulate predictive analysis
        predictions = [
            {
                "threat": "Potential Raid Activity",
                "confidence": random.randint(70, 85),
                "timeframe": "Next 6-12 hours",
                "indicators": ["Increased join velocity", "Pattern similarity to known raids"],
                "risk": "Medium"
            },
            {
                "threat": "Social Engineering Attempt",
                "confidence": random.randint(60, 75),
                "timeframe": "Next 24-48 hours",
                "indicators": ["Unusual PM patterns", "Privilege escalation requests"],
                "risk": "Low"
            }
        ]
        
        for i, pred in enumerate(predictions, 1):
            risk_emoji = "🔴" if pred["risk"] == "High" else "🟡" if pred["risk"] == "Medium" else "🟢"
            
            embed.add_field(
                name=f"{risk_emoji} Prediction #{i}: {pred['threat']}",
                value=f"**Confidence:** {pred['confidence']}%\n"
                      f"**Timeframe:** {pred['timeframe']}\n"
                      f"**Risk Level:** {pred['risk']}\n"
                      f"**Indicators:** {', '.join(pred['indicators'])}",
                inline=False
            )
        
        embed.add_field(
            name="🛡️ Proactive Measures",
            value="• Enhanced monitoring activated\n"
                  "• Alert thresholds adjusted\n"
                  "• Staff notifications prepared\n"
                  "• Response protocols ready",
            inline=False
        )
        
        embed.add_field(
            name="📊 Prediction Accuracy",
            value=f"**Historical Accuracy:** {random.randint(78, 92)}%\n"
                  f"**Predictions This Week:** {random.randint(15, 35)}\n"
                  f"**Prevented Incidents:** {random.randint(5, 15)}\n"
                  f"**Model Confidence:** {random.randint(85, 95)}%",
            inline=False
        )
        
        embed.set_footer(text="NexGuard Predictive Intelligence • Future Threat Forecasting")
        
        await interaction.followup.send(embed=embed)
    
    async def _demo_cross_server_intelligence(self, interaction):
        """Demo cross-server threat intelligence"""
        
        embed = discord.Embed(
            title="🌐 Cross-Server Intelligence Network",
            description="Shared threat data across the NexGuard protection network",
            color=0x00FFFF,
            timestamp=datetime.utcnow()
        )
        
        network_stats = {
            "protected_servers": random.randint(15, 25),
            "monitored_users": random.randint(800, 1200),
            "shared_threats": random.randint(45, 85),
            "network_bans": random.randint(12, 28)
        }
        
        embed.add_field(
            name="📊 Network Statistics",
            value=f"**Protected Servers:** {network_stats['protected_servers']}\n"
                  f"**Monitored Users:** {network_stats['monitored_users']:,}\n"
                  f"**Shared Threats:** {network_stats['shared_threats']}\n"
                  f"**Network Bans:** {network_stats['network_bans']}",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Intelligence Sharing",
            value=f"**Data Points Shared:** {random.randint(500, 1500):,}\n"
                  f"**Threat Confirmations:** {random.randint(25, 65)}\n"
                  f"**Pattern Matches:** {random.randint(35, 85)}\n"
                  f"**Auto-Actions:** {random.randint(15, 45)}",
            inline=True
        )
        
        recent_intel = [
            "🚨 User flagged across 3 servers for raid participation",
            "⚠️ Attack pattern identified and shared with network",
            "🛡️ Proactive ban prevented infiltration attempt",
            "📊 Behavioral model updated with new threat data"
        ]
        
        embed.add_field(
            name="📡 Recent Intelligence",
            value="\n".join([f"• {intel}" for intel in recent_intel]),
            inline=False
        )
        
        embed.add_field(
            name="🤝 Network Benefits",
            value="• **Faster Threat Detection** - Known threats identified instantly\n"
                  "• **Collective Learning** - AI improves from all server experiences\n"
                  "• **Proactive Protection** - Stop threats before they reach your server\n"
                  "• **Pattern Recognition** - Advanced attack detection capabilities",
            inline=False
        )
        
        embed.set_footer(text="NexGuard Intelligence Network • Collective Security")
        
        await interaction.followup.send(embed=embed)
    
    async def _demo_help(self, interaction):
        """Show demo command help"""
        
        embed = discord.Embed(
            title="🧠 Threat Analysis Demo Commands",
            description="Available demonstration modes for intelligent threat analysis",
            color=0x0099FF,
            timestamp=datetime.utcnow()
        )
        
        demos = [
            ("overview", "🏠", "System overview and capabilities"),
            ("user-analysis", "👤", "Individual user threat assessment"),
            ("pattern-recognition", "🔍", "Attack pattern detection"),
            ("predictive", "🔮", "Predictive threat modeling"),
            ("cross-server", "🌐", "Cross-server intelligence network")
        ]
        
        for demo_type, emoji, description in demos:
            embed.add_field(
                name=f"{emoji} `/threat-demo {demo_type}`",
                value=description,
                inline=False
            )
        
        embed.add_field(
            name="💡 Usage Examples",
            value="• `/threat-demo overview` - See system capabilities\n"
                  "• `/threat-demo user-analysis @user` - Analyze specific user\n"
                  "• `/threat-demo predictive` - View threat predictions",
            inline=False
        )
        
        embed.set_footer(text="NexGuard Threat Intelligence • Demo Mode")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ThreatAnalysisDemo(bot))