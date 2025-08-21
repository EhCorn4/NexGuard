INSERT INTO changelogs (version, title, description, changes, type, is_published) VALUES 
('2.3.2', 'Automated Changelog Publishing System', 'Introducing professional Discord changelog publishing with comprehensive automation features for seamless update notifications.', ARRAY[
'Added automated Discord changelog publishing to dedicated channel',
'Implemented professional Discord embed formatting with color-coded release types',
'Created comprehensive changelog management interface with real-time publishing',
'Added support for major, minor, patch, and hotfix release classifications',
'Enhanced changelog database schema with publication tracking',
'Integrated changelog publishing with existing Discord bot infrastructure'
], 'minor', false),

('2.3.1', 'Comprehensive Documentation System', 'Major expansion of PDF documentation system with enterprise-level guides and improved user experience.', ARRAY[
'Added 6 comprehensive downloadable PDF guides (85+ pages total)',
'Enhanced PDF generation with professional formatting and NexGuard branding',
'Updated all website statistics to reflect current 16+ servers and 600+ users',
'Improved ticket system with enhanced rename functionality and validation',
'Added comprehensive troubleshooting sections to all documentation',
'Implemented proper headers, footers, and professional styling across all guides'
], 'minor', true),

('2.3.0', 'Major Ticket System Overhaul', 'Complete restructuring of the ticket system with enhanced reliability, persistent button functionality, and improved user permissions.', ARRAY[
'Fixed ticket panel edit functionality resolving "invalid action" error',
'Enhanced ticket control button persistence across bot restarts',
'Improved ticket close permissions for enhanced user accessibility',
'Added individual control view instances for better interaction handling',
'Implemented intelligent ticket channel detection with custom panel support',
'Enhanced transcript generation and automatic delivery system',
'Added customizable deletion delays (0-300 seconds) for ticket closure'
], 'major', true)

ON CONFLICT (version) DO NOTHING;