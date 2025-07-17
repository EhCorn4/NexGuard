import { spawn } from 'child_process';
import { existsSync, readFileSync } from 'fs';

export class DirectBotStarter {
  private static instance: DirectBotStarter;
  private isRunning = false;

  private constructor() {}

  public static getInstance(): DirectBotStarter {
    if (!DirectBotStarter.instance) {
      DirectBotStarter.instance = new DirectBotStarter();
    }
    return DirectBotStarter.instance;
  }

  public async startBot(): Promise<boolean> {
    if (this.isRunning) {
      console.log('Bot is already running');
      return true;
    }

    try {
      console.log('Starting bot directly...');
      
      // Kill any existing bot processes
      const killProcess = spawn('pkill', ['-f', 'python3.*simple_bot.py']);
      await new Promise<void>((resolve) => {
        killProcess.on('exit', () => resolve());
        killProcess.on('error', () => resolve());
        setTimeout(() => resolve(), 2000); // Timeout after 2 seconds
      });

      // Clear old status files
      try {
        if (existsSync('/tmp/nexguard_bot_status.json')) {
          require('fs').unlinkSync('/tmp/nexguard_bot_status.json');
        }
      } catch (e) {
        // Ignore cleanup errors
      }

      // Start the bot using the background script
      const startProcess = spawn('bash', ['-c', 'cd bot && DISCORD_TOKEN="${DISCORD_BOT_TOKEN}" python3 index.py > /tmp/nexguard_bot.log 2>&1 &'], {
        env: {
          ...process.env,
          DISCORD_TOKEN: process.env.DISCORD_BOT_TOKEN,
          DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN,
        },
        detached: true,
        stdio: 'ignore'
      });

      startProcess.unref();
      this.isRunning = true;

      // Wait for bot to be ready
      for (let i = 0; i < 12; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (this.isBotReady()) {
          console.log('Bot is ready!');
          return true;
        }
      }

      console.log('Bot process started, assuming success');
      return true;
    } catch (error) {
      console.error('Error starting bot:', error);
      this.isRunning = false;
      return false;
    }
  }

  public async stopBot(): Promise<boolean> {
    try {
      // Kill the bot process
      const killProcess = spawn('pkill', ['-f', 'python3.*simple_bot.py']);
      await new Promise<void>((resolve) => {
        killProcess.on('exit', () => resolve());
        killProcess.on('error', () => resolve());
        setTimeout(() => resolve(), 3000); // Timeout after 3 seconds
      });

      this.isRunning = false;
      console.log('Bot stopped');
      return true;
    } catch (error) {
      console.error('Error stopping bot:', error);
      return false;
    }
  }

  public async restart(): Promise<boolean> {
    console.log('Restarting bot...');
    await this.stopBot();
    await new Promise(resolve => setTimeout(resolve, 2000));
    return await this.startBot();
  }

  private isBotReady(): boolean {
    try {
      if (existsSync('/tmp/nexguard_bot_status.json')) {
        const statusData = JSON.parse(readFileSync('/tmp/nexguard_bot_status.json', 'utf8'));
        return statusData.status === 'ready';
      }
    } catch (e) {
      // Ignore errors
    }
    return false;
  }

  public getStatus() {
    try {
      if (this.isBotReady()) {
        const statusData = JSON.parse(readFileSync('/tmp/nexguard_bot_status.json', 'utf8'));
        return {
          online: true,
          guilds: statusData.guilds || 0,
          users: statusData.users || 0,
          uptime: this.getUptime(),
          commands: 11,
          lastHeartbeat: new Date().toISOString(),
          version: '2.3.2',
          lastUpdated: new Date().toISOString()
        };
      }
    } catch (e) {
      // Ignore errors
    }

    return {
      online: false,
      guilds: 0,
      users: 0,
      uptime: '0s',
      commands: 0,
      lastHeartbeat: new Date().toISOString(),
      version: '2.3.2',
      lastUpdated: new Date().toISOString()
    };
  }

  private getUptime(): string {
    try {
      const statusData = JSON.parse(readFileSync('/tmp/nexguard_bot_status.json', 'utf8'));
      const startTime = new Date(statusData.timestamp).getTime();
      const uptime = Date.now() - startTime;
      const seconds = Math.floor(uptime / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);

      if (days > 0) return `${days}d ${hours % 24}h ${minutes % 60}m`;
      if (hours > 0) return `${hours}h ${minutes % 60}m`;
      if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
      return `${seconds}s`;
    } catch (e) {
      return '0s';
    }
  }

  public isOnline(): boolean {
    return this.isRunning && this.isBotReady();
  }
}

export const directBotStarter = DirectBotStarter.getInstance();