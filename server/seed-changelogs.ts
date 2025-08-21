import { db } from './db';
import { changelogs } from '@shared/schema';

async function seedChangelogs() {
  try {
    console.log('🌱 Seeding changelogs...');

    const sampleChangelogs = [
      {
        version: '2.3.2',
        title: 'Automated Changelog Publishing System',
        description: 'Introducing professional Discord changelog publishing with comprehensive automation features for seamless update notifications.',
        changes: [
          'Added automated Discord changelog publishing to dedicated channel',
          'Implemented professional Discord embed formatting with color-coded release types',
          'Created comprehensive changelog management interface with real-time publishing',
          'Added support for major, minor, patch, and hotfix release classifications',
          'Enhanced changelog database schema with publication tracking',
          'Integrated changelog publishing with existing Discord bot infrastructure'
        ],
        type: 'minor' as const,
        isPublished: false
      },
      {
        version: '2.3.1',
        title: 'Comprehensive Documentation System',
        description: 'Major expansion of PDF documentation system with enterprise-level guides and improved user experience.',
        changes: [
          'Added 6 comprehensive downloadable PDF guides (85+ pages total)',
          'Enhanced PDF generation with professional formatting and NexGuard branding',
          'Updated all website statistics to reflect current 16+ servers and 600+ users',
          'Improved ticket system with enhanced rename functionality and validation',
          'Added comprehensive troubleshooting sections to all documentation',
          'Implemented proper headers, footers, and professional styling across all guides'
        ],
        type: 'minor' as const,
        isPublished: true
      },
      {
        version: '2.3.0',
        title: 'Major Ticket System Overhaul',
        description: 'Complete restructuring of the ticket system with enhanced reliability, persistent button functionality, and improved user permissions.',
        changes: [
          'Fixed ticket panel edit functionality resolving "invalid action" error',
          'Enhanced ticket control button persistence across bot restarts',
          'Improved ticket close permissions for enhanced user accessibility',
          'Added individual control view instances for better interaction handling',
          'Implemented intelligent ticket channel detection with custom panel support',
          'Enhanced transcript generation and automatic delivery system',
          'Added customizable deletion delays (0-300 seconds) for ticket closure'
        ],
        type: 'major' as const,
        isPublished: true
      }
    ];

    for (const changelog of sampleChangelogs) {
      await db.insert(changelogs)
        .values(changelog)
        .onConflictDoNothing();
    }

    console.log('✅ Changelogs seeded successfully');
  } catch (error) {
    console.error('❌ Error seeding changelogs:', error);
  }
}

// Remove require.main check for ES modules

export { seedChangelogs };