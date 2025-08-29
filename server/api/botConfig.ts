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
        SELECT id, name, 
               COALESCE(member_count, 0) as member_count,
               0 as channel_count
        FROM guilds 
        ORDER BY name
      `);
      
      return result.rows.map(row => ({
        id: row.id as string,
        name: row.name as string,
        icon: null,
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
      // Get main guild config with available fields
      const guildResult = await db.execute(sql`
        SELECT 
          id, name, member_count, prefix,
          welcome_enabled, welcome_channel_id, welcome_message, welcome_embed,
          welcome_embed_title, welcome_embed_description, welcome_embed_color,
          welcome_embed_thumbnail, welcome_embed_footer,
          moderation_enabled, mod_role_id, admin_role_id, mute_role_id,
          automod_enabled, automod_caps_enabled, automod_caps_threshold,
          automod_mentions_enabled, automod_mentions_limit,
          log_channel_id, error_log_channel_id, error_logging_enabled,
          auto_role_enabled, auto_role_id,
          settings, automod_config
        FROM guilds 
        WHERE id = ${guildId}
      `);

      if (guildResult.rows.length === 0) {
        return null;
      }

      const guild = guildResult.rows[0];

      // Parse JSON settings if available
      const settings = guild.settings ? JSON.parse(guild.settings as string) : {};
      const automodConfig = guild.automod_config ? JSON.parse(guild.automod_config as string) : {};
      
      // Construct configuration object with available fields
      return {
        guild_id: guild.id as string,
        guild_name: guild.name as string,
        icon: null,
        member_count: guild.member_count as number || 0,
        prefix: guild.prefix as string || "!",
        language: settings.language || "en",
        timezone: settings.timezone || "UTC",
        welcome_enabled: guild.welcome_enabled as boolean || false,
        welcome_channel_id: guild.welcome_channel_id as string || null,
        welcome_message: guild.welcome_message as string || null,
        welcome_embed_enabled: guild.welcome_embed as boolean || false,
        welcome_role_id: settings.welcome_role_id || null,
        welcome_dm_enabled: settings.welcome_dm_enabled || false,
        goodbye_enabled: settings.goodbye_enabled || false,
        goodbye_channel_id: settings.goodbye_channel_id || null,
        goodbye_message: settings.goodbye_message || null,
        moderation_enabled: guild.moderation_enabled as boolean || false,
        mod_role_id: guild.mod_role_id as string || null,
        admin_role_id: guild.admin_role_id as string || null,
        mute_role_id: guild.mute_role_id as string || null,
        automod_enabled: guild.automod_enabled as boolean || false,
        spam_detection: automodConfig.spam_detection || false,
        caps_detection: guild.automod_caps_enabled as boolean || false,
        link_detection: automodConfig.link_detection || false,
        invite_detection: automodConfig.invite_detection || false,
        bad_words_detection: automodConfig.bad_words_detection || false,
        mention_spam_detection: guild.automod_mentions_enabled as boolean || false,
        duplicate_message_detection: automodConfig.duplicate_message_detection || false,
        automod_action: automodConfig.action || "warn",
        automod_threshold: guild.automod_caps_threshold as number || 3,
        log_channel_id: guild.log_channel_id as string || null,
        general_log_channel_id: settings.general_log_channel_id || null,
        member_log_channel_id: settings.member_log_channel_id || null,
        message_log_channel_id: settings.message_log_channel_id || null,
        voice_log_channel_id: settings.voice_log_channel_id || null,
        channel_log_channel_id: settings.channel_log_channel_id || null,
        role_log_channel_id: settings.role_log_channel_id || null,
        moderation_log_channel_id: settings.moderation_log_channel_id || null,
        server_log_channel_id: settings.server_log_channel_id || null,
        invite_log_channel_id: settings.invite_log_channel_id || null,
        anti_raid_enabled: settings.anti_raid_enabled || false,
        anti_nuke_enabled: settings.anti_nuke_enabled || false,
        verification_enabled: settings.verification_enabled || false,
        verification_role_id: settings.verification_role_id || null,
        verification_channel_id: settings.verification_channel_id || null,
        autorole_enabled: guild.auto_role_enabled as boolean || false,
        autorole_id: guild.auto_role_id as string || null,
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

      // Store logging settings in guild settings JSON field
      if (Object.keys(loggingUpdates).length > 0) {
        const currentSettings = await db.execute(sql`
          SELECT settings FROM guilds WHERE id = ${guildId}
        `);
        
        const existingSettings = currentSettings.rows[0]?.settings 
          ? JSON.parse(currentSettings.rows[0].settings as string) 
          : {};
        
        const updatedSettings = { ...existingSettings, ...loggingUpdates };
        
        await db.execute(sql`
          UPDATE guilds 
          SET settings = ${JSON.stringify(updatedSettings)}, updated_at = NOW()
          WHERE id = ${guildId}
        `);
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
      // Note: This should ideally fetch from Discord API, not database
      // For now, return empty array since channels table doesn't exist
      console.log(`Fetching channels for guild ${guildId} - using Discord API integration`);
      return [];
    } catch (error) {
      console.error('Error fetching guild channels:', error);
      return [];
    }
  }

  // Get guild roles for role selection
  static async getGuildRoles(guildId: string) {
    try {
      // Note: This should ideally fetch from Discord API, not database  
      // For now, return empty array since roles table doesn't exist
      console.log(`Fetching roles for guild ${guildId} - using Discord API integration`);
      return [];
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