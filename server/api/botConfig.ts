import { db } from "../db";
import { sql } from "drizzle-orm";

// Interface for bot configuration
export interface BotConfig {
  guild_id: string;
  guild_name: string;
  prefix?: string | null;
  welcome_enabled?: boolean;
  welcome_channel_id?: string | null;
  welcome_message?: string | null;
  automod_enabled?: boolean;
  moderation_enabled?: boolean;
  log_channel_id?: string | null;
  general_log_channel_id?: string | null;
  member_log_channel_id?: string | null;
  message_log_channel_id?: string | null;
  voice_log_channel_id?: string | null;
  channel_log_channel_id?: string | null;
  role_log_channel_id?: string | null;
  moderation_log_channel_id?: string | null;
}

// Interface for Discord guild basic info
export interface GuildInfo {
  id: string;
  name: string;
  icon?: string | null;
  member_count?: number;
  channel_count?: number;
}

export class BotConfigService {
  
  // Get list of guilds the bot is in
  static async getBotGuilds(): Promise<GuildInfo[]> {
    try {
      const result = await db.execute(sql`
        SELECT DISTINCT g.id, g.name, g.icon, g.member_count, 
               (SELECT COUNT(*) FROM channels WHERE guild_id = g.id) as channel_count
        FROM guilds g 
        ORDER BY g.name
      `);
      
      return result.rows.map(row => ({
        id: row.id as string,
        name: row.name as string,
        icon: row.icon as string || null,
        member_count: row.member_count as number || 0,
        channel_count: row.channel_count as number || 0
      }));
    } catch (error) {
      console.error('Error fetching bot guilds:', error);
      return [];
    }
  }

  // Get configuration for a specific guild
  static async getGuildConfig(guildId: string): Promise<BotConfig | null> {
    try {
      // Get main guild config
      const guildResult = await db.execute(sql`
        SELECT id, name, prefix, welcome_enabled, welcome_channel_id, 
               welcome_message, automod_enabled, moderation_enabled, 
               log_channel_id, icon, member_count
        FROM guilds 
        WHERE id = ${guildId}
      `);

      if (guildResult.rows.length === 0) {
        return null;
      }

      const guild = guildResult.rows[0];

      // Get logging channel configurations
      const loggingResult = await db.execute(sql`
        SELECT general_log_channel_id, member_log_channel_id, 
               message_log_channel_id, voice_log_channel_id,
               channel_log_channel_id, role_log_channel_id,
               moderation_log_channel_id
        FROM guild_settings 
        WHERE guild_id = ${guildId}
      `);

      const logging = loggingResult.rows[0] || {};

      return {
        guild_id: guild.id as string,
        guild_name: guild.name as string,
        prefix: guild.prefix as string || "!",
        welcome_enabled: guild.welcome_enabled as boolean || false,
        welcome_channel_id: guild.welcome_channel_id as string || null,
        welcome_message: guild.welcome_message as string || null,
        automod_enabled: guild.automod_enabled as boolean || false,
        moderation_enabled: guild.moderation_enabled as boolean || false,
        log_channel_id: guild.log_channel_id as string || null,
        general_log_channel_id: logging.general_log_channel_id as string || null,
        member_log_channel_id: logging.member_log_channel_id as string || null,
        message_log_channel_id: logging.message_log_channel_id as string || null,
        voice_log_channel_id: logging.voice_log_channel_id as string || null,
        channel_log_channel_id: logging.channel_log_channel_id as string || null,
        role_log_channel_id: logging.role_log_channel_id as string || null,
        moderation_log_channel_id: logging.moderation_log_channel_id as string || null
      };
    } catch (error) {
      console.error('Error fetching guild config:', error);
      return null;
    }
  }

  // Update guild configuration
  static async updateGuildConfig(guildId: string, updates: Partial<BotConfig>): Promise<boolean> {
    try {
      // Separate main guild updates from logging updates
      const guildUpdates: any = {};
      const loggingUpdates: any = {};

      // Map updates to appropriate tables
      for (const [key, value] of Object.entries(updates)) {
        if (key.includes('_log_channel_id')) {
          loggingUpdates[key] = value;
        } else if (key !== 'guild_id' && key !== 'guild_name') {
          guildUpdates[key] = value;
        }
      }

      // Update guilds table
      if (Object.keys(guildUpdates).length > 0) {
        // Use simple UPDATE query for each field
        for (const [key, value] of Object.entries(guildUpdates)) {
          await db.execute(sql`
            UPDATE guilds 
            SET ${sql.identifier(key)} = ${value}, updated_at = NOW()
            WHERE id = ${guildId}
          `);
        }
      }

      // Update guild_settings table
      if (Object.keys(loggingUpdates).length > 0) {
        // Use simple UPDATE for each logging field
        for (const [key, value] of Object.entries(loggingUpdates)) {
          await db.execute(sql`
            INSERT INTO guild_settings (guild_id, ${sql.identifier(key)})
            VALUES (${guildId}, ${value})
            ON CONFLICT (guild_id) DO UPDATE SET ${sql.identifier(key)} = ${value}
          `);
        }
      }

      console.log(`Updated guild config for ${guildId}:`, updates);
      return true;
    } catch (error) {
      console.error('Error updating guild config:', error);
      return false;
    }
  }

  // Get guild channels for dropdown selection
  static async getGuildChannels(guildId: string) {
    try {
      const result = await db.execute(sql`
        SELECT id, name, type 
        FROM channels 
        WHERE guild_id = ${guildId} AND type = 0
        ORDER BY name
      `);
      
      return result.rows.map(row => ({
        id: row.id as string,
        name: row.name as string,
        type: row.type as number
      }));
    } catch (error) {
      console.error('Error fetching guild channels:', error);
      return [];
    }
  }
}