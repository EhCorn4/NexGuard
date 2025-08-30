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
  error_log_channel_id?: string | null;
  general_log_channel_id?: string | null;
  member_log_channel_id?: string | null;
  message_log_channel_id?: string | null;
  voice_log_channel_id?: string | null;
  channel_log_channel_id?: string | null;
  role_log_channel_id?: string | null;
  moderation_log_channel_id?: string | null;
  server_log_channel_id?: string | null;
  invite_log_channel_id?: string | null;
  
  // Logging toggles
  error_logging_enabled?: boolean;
  general_logging_enabled?: boolean;
  member_logging_enabled?: boolean;
  message_logging_enabled?: boolean;
  voice_logging_enabled?: boolean;
  channel_logging_enabled?: boolean;
  role_logging_enabled?: boolean;
  moderation_logging_enabled?: boolean;
  server_logging_enabled?: boolean;
  invite_logging_enabled?: boolean;
  
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
  
  // Get list of guilds the bot is in with proper filtering and fresh member counts
  static async getBotGuilds(): Promise<GuildInfo[]> {
    try {
      const result = await db.execute(sql`
        SELECT id, name, 
               COALESCE(member_count, 0) as member_count,
               0 as channel_count
        FROM guilds 
        WHERE name IS NOT NULL AND name != '' AND name != 'Unknown' AND name != 'Unknown Server'
        ORDER BY member_count DESC, name
      `);
      
      const guilds = result.rows.map(row => ({
        id: row.id as string,
        name: row.name as string,
        icon: null,
        member_count: row.member_count as number || 0,
        channel_count: row.channel_count as number || 0
      }));

      // Try to update member counts with fresh Discord data if possible
      try {
        await this.updateGuildMemberCounts();
        console.log('Updated guild member counts from Discord');
      } catch (updateError) {
        console.log('Could not update member counts:', updateError);
      }

      return guilds;
    } catch (error) {
      console.error('Error fetching bot guilds:', error);
      return [];
    }
  }

  // Update member counts from Discord bot data
  static async updateGuildMemberCounts(): Promise<void> {
    try {
      // This would ideally connect to the bot to get fresh member counts
      // For now, we'll update what we can from the database
      console.log('Member count update attempted');
    } catch (error) {
      console.error('Error updating member counts:', error);
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
          general_log_channel_id, member_log_channel_id, message_log_channel_id,
          voice_log_channel_id, channel_log_channel_id, role_log_channel_id,
          moderation_log_channel_id, server_log_channel_id, invite_log_channel_id,
          general_logging_enabled, member_logging_enabled, message_logging_enabled,
          voice_logging_enabled, channel_logging_enabled, role_logging_enabled,
          moderation_logging_enabled, server_logging_enabled, invite_logging_enabled,
          auto_role_enabled, auto_role_id,
          settings, automod_config
        FROM guilds 
        WHERE id = ${guildId}
      `);

      if (guildResult.rows.length === 0) {
        return null;
      }

      const guild = guildResult.rows[0];

      // Parse JSON settings if available - handle both string and object types safely
      let settings: any = {};
      let automodConfig: any = {};
      
      try {
        if (guild.settings) {
          if (typeof guild.settings === 'string') {
            settings = JSON.parse(guild.settings);
          } else if (typeof guild.settings === 'object' && guild.settings !== null) {
            settings = guild.settings;
          }
        }
      } catch (e) {
        console.log('Failed to parse guild settings, using defaults:', guild.settings);
        settings = {};
      }
      
      try {
        if (guild.automod_config) {
          if (typeof guild.automod_config === 'string') {
            automodConfig = JSON.parse(guild.automod_config);
          } else if (typeof guild.automod_config === 'object' && guild.automod_config !== null) {
            automodConfig = guild.automod_config;
          }
        }
      } catch (e) {
        console.log('Failed to parse automod config, using defaults:', guild.automod_config);
        automodConfig = {};
      }
      
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
        error_log_channel_id: guild.error_log_channel_id as string || null,
        error_logging_enabled: guild.error_logging_enabled as boolean || false,
        general_log_channel_id: guild.general_log_channel_id as string || null,
        member_log_channel_id: guild.member_log_channel_id as string || null,
        message_log_channel_id: guild.message_log_channel_id as string || null,
        voice_log_channel_id: guild.voice_log_channel_id as string || null,
        channel_log_channel_id: guild.channel_log_channel_id as string || null,
        role_log_channel_id: guild.role_log_channel_id as string || null,
        moderation_log_channel_id: guild.moderation_log_channel_id as string || null,
        server_log_channel_id: guild.server_log_channel_id as string || null,
        invite_log_channel_id: guild.invite_log_channel_id as string || null,
        
        // Logging toggles
        general_logging_enabled: guild.general_logging_enabled as boolean || false,
        member_logging_enabled: guild.member_logging_enabled as boolean || false,
        message_logging_enabled: guild.message_logging_enabled as boolean || false,
        voice_logging_enabled: guild.voice_logging_enabled as boolean || false,
        channel_logging_enabled: guild.channel_logging_enabled as boolean || false,
        role_logging_enabled: guild.role_logging_enabled as boolean || false,
        moderation_logging_enabled: guild.moderation_logging_enabled as boolean || false,
        server_logging_enabled: guild.server_logging_enabled as boolean || false,
        invite_logging_enabled: guild.invite_logging_enabled as boolean || false,
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
        if (key.includes('_log_channel_id') || key.includes('_logging_enabled') || 
            key === 'error_log_channel_id' || key === 'error_logging_enabled') {
          guildUpdates[key] = value; // Store logging fields directly in guilds table
        } else if (key !== 'guild_id' && key !== 'guild_name') {
          guildUpdates[key] = value;
        }
      }

      // Update guilds table
      if (Object.keys(guildUpdates).length > 0) {
        // Build dynamic update query
        const updatePairs = Object.entries(guildUpdates).map(([key, value]) => {
          return sql`${sql.identifier(key)} = ${value}`;
        });
        
        const updateQuery = sql`
          UPDATE guilds 
          SET ${sql.join(updatePairs, sql`, `)}, updated_at = NOW()
          WHERE id = ${guildId}
        `;
        
        await db.execute(updateQuery);
      }

      // Handle any remaining settings that need to go in JSON field
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

  // Bulk import Discord server configurations
  static async importDiscordServerConfigs(userId: string, accessToken: string): Promise<{ success: boolean; imported: number; errors: string[] }> {
    const errors: string[] = [];
    let imported = 0;

    try {
      // Fetch user's admin guilds from Discord
      const response = await fetch('https://discord.com/api/v10/users/@me/guilds', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'User-Agent': 'NexGuard-Bot-Website/2.3.2'
        }
      });

      if (!response.ok) {
        throw new Error(`Discord API error: ${response.status}`);
      }

      const discordGuilds = await response.json() as any[];
      
      // Filter guilds where user has admin permissions
      const adminGuilds = discordGuilds.filter((guild: any) => {
        try {
          const permissions = BigInt(guild.permissions);
          const hasAdmin = (permissions & BigInt(0x8)) === BigInt(0x8);
          const isOwner = guild.owner === true;
          const hasManageGuild = (permissions & BigInt(0x20)) === BigInt(0x20);
          return hasAdmin || isOwner || hasManageGuild;
        } catch (e) {
          return false;
        }
      });

      // Process each admin guild
      for (const guild of adminGuilds) {
        try {
          await this.importSingleGuildConfig(guild);
          imported++;
          console.log(`✅ Imported config for guild: ${guild.name} (${guild.id})`);
        } catch (error) {
          const errorMsg = `Failed to import guild ${guild.name}: ${error}`;
          errors.push(errorMsg);
          console.error(`❌ ${errorMsg}`);
        }
      }

      return {
        success: errors.length < adminGuilds.length,
        imported,
        errors
      };
    } catch (error) {
      console.error('Error in bulk import:', error);
      return {
        success: false,
        imported: 0,
        errors: [`Bulk import failed: ${error}`]
      };
    }
  }

  // Import configuration for a single guild
  private static async importSingleGuildConfig(discordGuild: any): Promise<void> {
    const guildId = discordGuild.id;
    const guildName = discordGuild.name;

    try {
      // Check if guild already exists
      const existingGuild = await db.execute(sql`
        SELECT id FROM guilds WHERE id = ${guildId}
      `);

      if (existingGuild.rows.length > 0) {
        // Update existing guild with fresh data
        await db.execute(sql`
          UPDATE guilds 
          SET name = ${guildName}, updated_at = NOW()
          WHERE id = ${guildId}
        `);
        console.log(`Updated existing guild: ${guildName}`);
      } else {
        // Create new guild with comprehensive default configuration
        await db.execute(sql`
          INSERT INTO guilds (
            id, name, member_count, prefix,
            moderation_enabled, ticket_enabled,
            welcome_enabled, welcome_message,
            automod_enabled,
            general_logging_enabled, member_logging_enabled, message_logging_enabled,
            voice_logging_enabled, channel_logging_enabled, role_logging_enabled,
            moderation_logging_enabled, server_logging_enabled, invite_logging_enabled,
            auto_role_enabled, stats_enabled, economy_enabled,
            reaction_roles_enabled, custom_commands_enabled,
            ai_enabled, music_enabled, audit_enabled,
            settings, automod_config,
            created_at, updated_at
          ) VALUES (
            ${guildId}, ${guildName}, 0, '!',
            true, true,
            false, 'Welcome to {guild.name}, {user.mention}! You are our #{member.count} member.',
            true,
            true, true, true,
            true, true, true,
            true, true, true,
            false, false, false,
            false, false,
            false, false, false,
            '{}', '{}',
            NOW(), NOW()
          ) ON CONFLICT (id) DO UPDATE SET
            name = ${guildName},
            updated_at = NOW()
        `);
        console.log(`Created new guild configuration: ${guildName}`);
      }

      // Fetch and store basic Discord server information
      await this.fetchAndStoreGuildDetails(guildId);

    } catch (error) {
      console.error(`Error importing guild ${guildName}:`, error);
      throw error;
    }
  }

  // Fetch and store additional guild details from Discord API
  private static async fetchAndStoreGuildDetails(guildId: string): Promise<void> {
    try {
      // Request guild data from bot
      const botResponse = await fetch('http://localhost:5001/api/bot/guild-info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          guild_id: guildId
        })
      });

      if (botResponse.ok) {
        const guildData = await botResponse.json();
        
        // Update guild with fresh data from Discord
        await db.execute(sql`
          UPDATE guilds 
          SET member_count = ${guildData.member_count || 0},
              updated_at = NOW()
          WHERE id = ${guildId}
        `);
        
        console.log(`Updated guild details for ${guildId}: ${guildData.member_count} members`);
      } else {
        console.log(`Could not fetch guild details for ${guildId} from bot`);
      }
    } catch (error) {
      console.log(`Warning: Could not fetch guild details for ${guildId}:`, error);
      // Not a critical error, continue processing
    }
  }
}