import { Client, EmbedBuilder, TextChannel } from 'discord.js';
import { db } from '../db';
import { changelogs } from '@shared/schema';
import { desc, eq } from 'drizzle-orm';

export class ChangelogPublisher {
  private client: Client;
  private targetChannelId: string = '1389986013404991498';

  constructor(client: Client) {
    this.client = client;
  }

  async publishLatestChangelog(): Promise<boolean> {
    try {
      // Get the latest unpublished changelog
      const [latestChangelog] = await db.select()
        .from(changelogs)
        .where(eq(changelogs.isPublished, false))
        .orderBy(desc(changelogs.releaseDate))
        .limit(1);

      if (!latestChangelog) {
        console.log('📝 No unpublished changelog found');
        return false;
      }

      return await this.publishChangelog(latestChangelog);
    } catch (error) {
      console.error('❌ Error publishing latest changelog:', error);
      return false;
    }
  }

  async publishChangelogByVersion(version: string): Promise<boolean> {
    try {
      const [changelog] = await db.select()
        .from(changelogs)
        .where(eq(changelogs.version, version))
        .limit(1);

      if (!changelog) {
        console.log(`📝 Changelog for version ${version} not found`);
        return false;
      }

      return await this.publishChangelog(changelog);
    } catch (error) {
      console.error(`❌ Error publishing changelog for version ${version}:`, error);
      return false;
    }
  }

  private async publishChangelog(changelog: typeof changelogs.$inferSelect): Promise<boolean> {
    try {
      const channel = this.client.channels.cache.get(this.targetChannelId) as TextChannel;
      if (!channel) {
        console.error(`❌ Target channel ${this.targetChannelId} not found`);
        return false;
      }

      const embed = this.createChangelogEmbed(changelog);
      
      await channel.send({
        content: `🚀 **NexGuard Update - Version ${changelog.version}**\n\n@everyone`,
        embeds: [embed]
      });

      // Mark as published
      await db.update(changelogs)
        .set({ isPublished: true })
        .where(eq(changelogs.id, changelog.id));

      console.log(`✅ Changelog v${changelog.version} published successfully to ${this.targetChannelId}`);
      return true;
    } catch (error) {
      console.error('❌ Error sending changelog to Discord:', error);
      return false;
    }
  }

  private createChangelogEmbed(changelog: typeof changelogs.$inferSelect): EmbedBuilder {
    const typeEmoji = {
      major: '🚀',
      minor: '✨',
      patch: '🐛',
      hotfix: '🔥'
    }[changelog.type] || '📝';

    const typeColor = {
      major: 0xFF6B6B,  // Red for major
      minor: 0x4ECDC4,  // Teal for minor
      patch: 0x45B7D1,  // Blue for patch
      hotfix: 0xFF9F43  // Orange for hotfix
    }[changelog.type] || 0x00FFFF;

    const embed = new EmbedBuilder()
      .setTitle(`${typeEmoji} NexGuard v${changelog.version} - ${changelog.title}`)
      .setDescription(changelog.description)
      .setColor(typeColor)
      .setTimestamp(new Date(changelog.releaseDate))
      .setFooter({ 
        text: `NexGuard Development Team • ${changelog.type.toUpperCase()} Release`,
        iconURL: 'https://cdn.discordapp.com/attachments/your-server/nexguard-logo.png'
      })
      .setThumbnail('https://cdn.discordapp.com/attachments/your-server/nexguard-icon.png');

    // Add changes field with better formatting
    if (changelog.changes && changelog.changes.length > 0) {
      const changesSections = this.organizeChanges(changelog.changes);
      
      Object.entries(changesSections).forEach(([section, changes]) => {
        if (changes.length > 0) {
          const sectionEmoji = {
            'NEW': '🎉',
            'IMPROVED': '⚡',
            'FIXED': '🔧',
            'REMOVED': '🗑️',
            'SECURITY': '🔐',
            'OTHER': '📝'
          }[section] || '•';

          embed.addFields({
            name: `${sectionEmoji} ${section}`,
            value: changes.map(change => `• ${change}`).join('\n'),
            inline: false
          });
        }
      });
    }

    // Add metadata
    embed.addFields(
      {
        name: '📊 Release Info',
        value: [
          `**Type:** ${changelog.type.toUpperCase()}`,
          `**Date:** ${new Date(changelog.releaseDate).toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}`,
          `**Status:** Live`
        ].join('\n'),
        inline: true
      },
      {
        name: '🔗 Links',
        value: [
          '[Dashboard](https://your-domain.replit.app)',
          '[Documentation](https://your-domain.replit.app/guides)',
          '[Support Server](https://discord.gg/nexguard)'
        ].join('\n'),
        inline: true
      }
    );

    return embed;
  }

  private organizeChanges(changes: string[]): Record<string, string[]> {
    const sections: Record<string, string[]> = {
      'NEW': [],
      'IMPROVED': [],
      'FIXED': [],
      'REMOVED': [],
      'SECURITY': [],
      'OTHER': []
    };

    changes.forEach(change => {
      const lowerChange = change.toLowerCase();
      
      if (lowerChange.includes('added') || lowerChange.includes('new') || lowerChange.includes('introduced')) {
        sections.NEW.push(change);
      } else if (lowerChange.includes('fixed') || lowerChange.includes('resolved') || lowerChange.includes('corrected')) {
        sections.FIXED.push(change);
      } else if (lowerChange.includes('improved') || lowerChange.includes('enhanced') || lowerChange.includes('optimized') || lowerChange.includes('updated')) {
        sections.IMPROVED.push(change);
      } else if (lowerChange.includes('removed') || lowerChange.includes('deleted') || lowerChange.includes('deprecated')) {
        sections.REMOVED.push(change);
      } else if (lowerChange.includes('security') || lowerChange.includes('vulnerability') || lowerChange.includes('auth')) {
        sections.SECURITY.push(change);
      } else {
        sections.OTHER.push(change);
      }
    });

    return sections;
  }

  async publishCustomChangelog(data: {
    version: string;
    title: string;
    description: string;
    changes: string[];
    type: 'major' | 'minor' | 'patch' | 'hotfix';
  }): Promise<boolean> {
    try {
      // Create changelog in database
      const [newChangelog] = await db.insert(changelogs)
        .values({
          version: data.version,
          title: data.title,
          description: data.description,
          changes: data.changes,
          type: data.type,
          isPublished: false
        })
        .returning();

      // Publish it
      return await this.publishChangelog(newChangelog);
    } catch (error) {
      console.error('❌ Error creating and publishing custom changelog:', error);
      return false;
    }
  }
}