  private async registerSlashCommands(token: string) {
    try {
      const clientId = process.env.DISCORD_CLIENT_ID;
      if (!clientId) {
        console.error('DISCORD_CLIENT_ID is not set');
        return;
      }

      // Commands based on the actual Python bot files provided
      const commands = pythonBotCommands;

      const rest = new REST({ version: '10' }).setToken(token);

      console.log(`Started refreshing application (/) commands. Total: ${commands.length}`);
      await rest.put(
        Routes.applicationCommands(clientId),
        { body: commands },
      );

      console.log(`Successfully reloaded application (/) commands. Total: ${commands.length}`);
      
      // Update status with correct command count
      this.statusData.commands = commands.length;

      // Setup command handlers
      this.client?.on('interactionCreate', async (interaction) => {
        if (!interaction.isChatInputCommand()) return;

        const { commandName } = interaction;

        if (commandName === 'ping') {
          await interaction.reply('Pong!');
        } else if (commandName === 'help') {
          const helpEmbed = {
            title: 'NexGuard Bot Commands',
            color: 0x00ff88,
            description: 'Here are all available commands:',
            fields: [
              { name: 'Moderation', value: '`/ban` `/kick` `/mute` `/unmute` `/warn` `/warnings` `/purge` `/purgebot` `/unban` `/banlist` `/mutelist` `/timeout` `/untimeout` `/slowmode` `/lock` `/unlock`', inline: false },
              { name: 'Utility', value: '`/userinfo` `/avatar` `/serverinfo` `/commands` `/embed` `/embed-help` `/embed-json`', inline: false },
              { name: 'Admin', value: '`/prefix` `/resetprefix` `/modrole` `/resetmodrole` `/logging` `/changelog` `/changelog-test` `/changelog-disable`', inline: false },
              { name: 'Tickets', value: '`/ticket` `/ticket-setup` `/ticket-panel` `/ticket-close` `/ticket-info` `/ticket-list` `/ticket-stats` `/ticket-cleanup` `/ticket-embed` `/ticket-enhanced` `/transcript`', inline: false },
            ],
            timestamp: new Date(),
            footer: { text: 'NexGuard Bot' }
          };
          await interaction.reply({ embeds: [helpEmbed] });
        } else {
          await interaction.reply('⚠️ This command is currently under development. Please use the dashboard at https://nexguard.replit.app to configure bot settings.');
        }
      });

    } catch (error) {
      console.error('Error registering slash commands:', error);
    }
  }