import { db } from "../db";
import { sql } from "drizzle-orm";

// Complete interface for all bot configuration options
export interface BotConfig {
  // Basic guild info
  guild_id: string;
  guild_name: string;
  icon?: string | null;
  member_count?: number;
  
  // Core settings
  prefix?: string | null;
  language?: string | null;
  timezone?: string | null;
  
  // Welcome system
  welcome_enabled?: boolean;
  welcome_channel_id?: string | null;
  welcome_message?: string | null;
  welcome_embed_enabled?: boolean;
  welcome_role_id?: string | null;
  welcome_dm_enabled?: boolean;
  
  // Goodbye system
  goodbye_enabled?: boolean;
  goodbye_channel_id?: string | null;
  goodbye_message?: string | null;
  
  // Moderation settings
  moderation_enabled?: boolean;
  mod_role_id?: string | null;
  admin_role_id?: string | null;
  mute_role_id?: string | null;
  
  // AutoMod configuration
  automod_enabled?: boolean;
  spam_detection?: boolean;
  caps_detection?: boolean;
  link_detection?: boolean;
  invite_detection?: boolean;
  bad_words_detection?: boolean;
  mention_spam_detection?: boolean;
  duplicate_message_detection?: boolean;
  automod_action?: string | null; // warn, mute, kick, ban
  automod_threshold?: number;
  
  // Logging channels
  log_channel_id?: string | null;
  general_log_channel_id?: string | null;
  member_log_channel_id?: string | null;
  message_log_channel_id?: string | null;
  voice_log_channel_id?: string | null;
  channel_log_channel_id?: string | null;
  role_log_channel_id?: string | null;
  moderation_log_channel_id?: string | null;
  server_log_channel_id?: string | null;
  invite_log_channel_id?: string | null;
  
  // Security settings
  anti_raid_enabled?: boolean;
  anti_nuke_enabled?: boolean;
  verification_enabled?: boolean;
  verification_role_id?: string | null;
  verification_channel_id?: string | null;
  
  // Auto-role settings
  autorole_enabled?: boolean;
  autorole_id?: string | null;
  autorole_delay?: number;
  
  // Ticket system
  ticket_enabled?: boolean;
  ticket_category_id?: string | null;
  ticket_support_role_id?: string | null;
  ticket_log_channel_id?: string | null;
  
  // Server stats
  stats_enabled?: boolean;
  member_count_channel_id?: string | null;
  bot_count_channel_id?: string | null;
  channel_count_channel_id?: string | null;
  
  // Economy system
  economy_enabled?: boolean;
  currency_name?: string | null;
  daily_amount?: number;
  
  // Reaction roles
  reaction_roles_enabled?: boolean;
  
  // Custom commands
  custom_commands_enabled?: boolean;
  
  // AI features
  ai_enabled?: boolean;
  ai_channel_id?: string | null;
  
  // Music settings
  music_enabled?: boolean;
  default_volume?: number;
  
  // Audit settings
  audit_enabled?: boolean;
  audit_channel_id?: string | null;
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

  // Get comprehensive configuration for a specific guild
  static async getGuildConfig(guildId: string): Promise<BotConfig | null> {
    try {
      // Get main guild config with all available fields
      const guildResult = await db.execute(sql`
        SELECT 
          id, name, icon, member_count, prefix, language, timezone,
          welcome_enabled, welcome_channel_id, welcome_message, welcome_embed_enabled, 
          welcome_role_id, welcome_dm_enabled,
          goodbye_enabled, goodbye_channel_id, goodbye_message,
          moderation_enabled, mod_role_id, admin_role_id, mute_role_id,
          automod_enabled, spam_detection, caps_detection, link_detection, 
          invite_detection, bad_words_detection, mention_spam_detection,
          duplicate_message_detection, automod_action, automod_threshold,
          log_channel_id, anti_raid_enabled, anti_nuke_enabled,
          verification_enabled, verification_role_id, verification_channel_id,
          autorole_enabled, autorole_id, autorole_delay,
          ticket_enabled, ticket_category_id, ticket_support_role_id, ticket_log_channel_id,
          stats_enabled, member_count_channel_id, bot_count_channel_id, channel_count_channel_id,
          economy_enabled, currency_name, daily_amount,
          reaction_roles_enabled, custom_commands_enabled,
          ai_enabled, ai_channel_id, music_enabled, default_volume,
          audit_enabled, audit_channel_id
        FROM guilds 
        WHERE id = ${guildId}
      `);

      if (guildResult.rows.length === 0) {
        return null;
      }

      const guild = guildResult.rows[0];

      // Get logging channel configurations
      const loggingResult = await db.execute(sql`
        SELECT 
          general_log_channel_id, member_log_channel_id, message_log_channel_id,
          voice_log_channel_id, channel_log_channel_id, role_log_channel_id,
          moderation_log_channel_id, server_log_channel_id, invite_log_channel_id
        FROM guild_settings 
        WHERE guild_id = ${guildId}
      `);

      const logging = loggingResult.rows[0] || {};

      // Construct complete configuration object
      return {
        guild_id: guild.id as string,
        guild_name: guild.name as string,
        icon: guild.icon as string || null,
        member_count: guild.member_count as number || 0,
        
        // Core settings
        prefix: guild.prefix as string || "!",
        language: guild.language as string || "en",
        timezone: guild.timezone as string || "UTC",
        
        // Welcome system
        welcome_enabled: guild.welcome_enabled as boolean || false,
        welcome_channel_id: guild.welcome_channel_id as string || null,
        welcome_message: guild.welcome_message as string || null,
        welcome_embed_enabled: guild.welcome_embed_enabled as boolean || false,
        welcome_role_id: guild.welcome_role_id as string || null,
        welcome_dm_enabled: guild.welcome_dm_enabled as boolean || false,
        
        // Goodbye system
        goodbye_enabled: guild.goodbye_enabled as boolean || false,
        goodbye_channel_id: guild.goodbye_channel_id as string || null,
        goodbye_message: guild.goodbye_message as string || null,
        
        // Moderation settings
        moderation_enabled: guild.moderation_enabled as boolean || false,
        mod_role_id: guild.mod_role_id as string || null,
        admin_role_id: guild.admin_role_id as string || null,
        mute_role_id: guild.mute_role_id as string || null,
        
        // AutoMod configuration
        automod_enabled: guild.automod_enabled as boolean || false,
        spam_detection: guild.spam_detection as boolean || true,
        caps_detection: guild.caps_detection as boolean || true,
        link_detection: guild.link_detection as boolean || false,
        invite_detection: guild.invite_detection as boolean || true,
        bad_words_detection: guild.bad_words_detection as boolean || true,
        mention_spam_detection: guild.mention_spam_detection as boolean || true,
        duplicate_message_detection: guild.duplicate_message_detection as boolean || true,
        automod_action: guild.automod_action as string || "warn",
        automod_threshold: guild.automod_threshold as number || 3,
        
        // Logging channels
        log_channel_id: guild.log_channel_id as string || null,
        general_log_channel_id: logging.general_log_channel_id as string || null,
        member_log_channel_id: logging.member_log_channel_id as string || null,
        message_log_channel_id: logging.message_log_channel_id as string || null,
        voice_log_channel_id: logging.voice_log_channel_id as string || null,
        channel_log_channel_id: logging.channel_log_channel_id as string || null,
        role_log_channel_id: logging.role_log_channel_id as string || null,
        moderation_log_channel_id: logging.moderation_log_channel_id as string || null,
        server_log_channel_id: logging.server_log_channel_id as string || null,
        invite_log_channel_id: logging.invite_log_channel_id as string || null,
        
        // Security settings
        anti_raid_enabled: guild.anti_raid_enabled as boolean || true,
        anti_nuke_enabled: guild.anti_nuke_enabled as boolean || true,
        verification_enabled: guild.verification_enabled as boolean || false,
        verification_role_id: guild.verification_role_id as string || null,
        verification_channel_id: guild.verification_channel_id as string || null,
        
        // Auto-role settings
        autorole_enabled: guild.autorole_enabled as boolean || false,
        autorole_id: guild.autorole_id as string || null,
        autorole_delay: guild.autorole_delay as number || 0,
        
        // Ticket system
        ticket_enabled: guild.ticket_enabled as boolean || false,
        ticket_category_id: guild.ticket_category_id as string || null,
        ticket_support_role_id: guild.ticket_support_role_id as string || null,
        ticket_log_channel_id: guild.ticket_log_channel_id as string || null,
        
        // Server stats
        stats_enabled: guild.stats_enabled as boolean || false,
        member_count_channel_id: guild.member_count_channel_id as string || null,
        bot_count_channel_id: guild.bot_count_channel_id as string || null,
        channel_count_channel_id: guild.channel_count_channel_id as string || null,
        
        // Economy system
        economy_enabled: guild.economy_enabled as boolean || false,
        currency_name: guild.currency_name as string || "coins",
        daily_amount: guild.daily_amount as number || 100,
        
        // Feature toggles
        reaction_roles_enabled: guild.reaction_roles_enabled as boolean || false,
        custom_commands_enabled: guild.custom_commands_enabled as boolean || false,
        
        // AI features
        ai_enabled: guild.ai_enabled as boolean || false,
        ai_channel_id: guild.ai_channel_id as string || null,
        
        // Music settings
        music_enabled: guild.music_enabled as boolean || false,
        default_volume: guild.default_volume as number || 50,
        
        // Audit settings
        audit_enabled: guild.audit_enabled as boolean || false,
        audit_channel_id: guild.audit_channel_id as string || null
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

  // Get guild channels and roles for dropdown selection
  static async getGuildChannels(guildId: string) {
    try {
      const result = await db.execute(sql`
        SELECT id, name, type 
        FROM channels 
        WHERE guild_id = ${guildId} AND type IN (0, 2, 4)
        ORDER BY type, name
      `);
      
      return result.rows.map(row => ({
        id: row.id as string,
        name: row.name as string,
        type: row.type as number // 0=text, 2=voice, 4=category
      }));
    } catch (error) {
      console.error('Error fetching guild channels:', error);
      return [];
    }
  }

  // Get guild roles for role selection
  static async getGuildRoles(guildId: string) {
    try {
      const result = await db.execute(sql`
        SELECT id, name, color, position, managed
        FROM roles 
        WHERE guild_id = ${guildId} AND name != '@everyone'
        ORDER BY position DESC
      `);
      
      return result.rows.map(row => ({
        id: row.id as string,
        name: row.name as string,
        color: row.color as number || 0,
        position: row.position as number || 0,
        managed: row.managed as boolean || false
      }));
    } catch (error) {
      console.error('Error fetching guild roles:', error);
      return [];
    }
  }

  // Get auto-reply configurations for a guild
  static async getAutoReplies(guildId: string) {
    try {
      const result = await db.execute(sql`
        SELECT id, trigger, response_title, response_description, 
               response_color, trigger_type, is_active, rule_name
        FROM auto_replies 
        WHERE guild_id = ${guildId}
        ORDER BY created_at DESC
      `);
      
      return result.rows.map(row => ({
        id: row.id as number,
        trigger: row.trigger as string,
        response_title: row.response_title as string,
        response_description: row.response_description as string,
        response_color: row.response_color as string,
        trigger_type: row.trigger_type as string,
        is_active: row.is_active as boolean,
        rule_name: row.rule_name as string
      }));
    } catch (error) {
      console.error('Error fetching auto-replies:', error);
      return [];
    }
  }
}