-- Complete Database Copy: Development Features → Production
-- This script will replace ALL features in production with the exact data from development

-- Step 1: Clear existing features
DELETE FROM features;

-- Step 2: Copy all 13 features from development
INSERT INTO features (title, description, icon, benefits) VALUES 
('Advanced Moderation & Auto-Filtering', 'Automated content filtering with 26 pre-configured bad words, smart spam detection, and customizable punishment systems to keep your server clean and family-friendly.', 'gavel', '{"Pre-configured bad words filter (26+ words)", "Automatic content deletion", "Smart spam & raid protection", "Customizable warning system", "Zero setup required"}'),

('Enterprise Security Suite', 'Military-grade anti-nuke protection, threat intelligence, and behavioral analysis that automatically quarantines attackers and protects your server from raids and nukes.', 'shield-check', '{"Anti-nuke protection (always active)", "Automatic attacker quarantine", "Threat pattern recognition", "Real-time audit log monitoring", "Cross-server intelligence sharing"}'),

('Professional Ticket System', 'Comprehensive support management with persistent panels, smart routing, staff assignment, and complete Discord integration for professional customer service.', 'ticket', '{"Persistent ticket panels", "Multi-category support", "Staff assignment system", "Button-based interactions", "Professional service hub"}'),

('Live Server Analytics', 'Real-time insights into server activity, member engagement, growth patterns, and comprehensive moderation statistics with beautiful charts and reports.', 'activity', '{"Real-time activity tracking", "Member engagement metrics", "Growth analytics & trends", "Moderation statistics", "Beautiful data visualization"}'),

('Performance Monitoring', 'Enterprise-grade bot health monitoring with CPU, memory, and disk usage tracking plus automated alerts for optimal performance.', 'heart-pulse', '{"Real-time performance metrics", "CPU & memory monitoring", "Automated health alerts", "Uptime tracking", "Error rate analysis"}'),

('External API Integration', 'Professional RESTful API endpoints for third-party integrations, custom dashboard development, and external applications.', 'plug', '{"RESTful API endpoints", "Third-party integrations", "Custom dashboard support", "External app connectivity", "Developer-friendly documentation"}'),

('Live Server Statistics', 'Real-time Discord embeds showing server activity, member counts, bot uptime, and command usage statistics that update automatically every minute.', 'chart-line', '{"Live Discord stat embeds", "Auto-updating every minute", "Server & member metrics", "Bot performance tracking", "Professional status displays"}'),

('Reaction Roles & Auto-Assignment', 'Advanced role management with button-based reaction roles, automatic role assignment for new members, and comprehensive permission templates.', 'users', '{"Button-based reaction roles", "Automatic role assignment", "Permission templates", "Role hierarchy management", "20+ active reaction roles"}'),

('Comprehensive Event Logging', 'Professional audit trail with 7 logging categories covering member, message, voice, channel, role, and moderation events with detailed Discord embeds.', 'bell', '{"7 logging categories", "Professional Discord embeds", "Member activity tracking", "Comprehensive audit trails", "Auto-setup with /botlogs command"}'),

('AI Assistant & Advanced Commands', 'Intelligent chatbot assistance powered by OpenAI integration, plus 67+ slash commands covering administration, moderation, utilities, and server management.', 'gamepad', '{"67+ professional slash commands", "AI-powered assistance", "Admin & moderation tools", "Utility commands", "Server info & management"}'),

('Professional Web Dashboard', 'Comprehensive web-based management interface with real-time server configuration, Discord integration, and bulk import functionality for effortless administration.', 'cog', '{"Real-time web dashboard", "Discord server integration", "Bulk config import", "Live channel/role selection", "Professional admin interface"}'),

('Automated Discord Publishing', 'Professional changelog publishing system that automatically distributes updates to Discord with beautiful embeds, handling long messages and multiple channels seamlessly.', 'file-text', '{"Automated changelog publishing", "Professional Discord embeds", "Multi-channel distribution", "Long message handling", "Beautiful formatting"}'),

('Real-Time Cross-Server Intelligence', 'Advanced threat intelligence system that shares behavioral patterns, attack signatures, and security insights across all connected servers for enhanced protection.', 'shield-alert', '{"Cross-server threat sharing", "Behavioral pattern analysis", "Attack signature detection", "Predictive threat modeling", "Enterprise-grade security"}');

-- Verify the copy worked
SELECT COUNT(*) as total_features FROM features;