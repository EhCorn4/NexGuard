import { spawn, ChildProcess } from 'child_process';
import { resolve } from 'path';
import WebSocket from 'ws';

export class BotManager {
  private botProcess: ChildProcess | null = null;
  private isRunning = false;
  private lastStatus: any = null;
  private statusUpdateInterval: NodeJS.Timer | null = null;

  constructor() {
    this.setupBotStatusUpdates();
  }

  private setupBotStatusUpdates() {
    // Update bot status every 30 seconds
    this.statusUpdateInterval = setInterval(() => {
      this.updateBotStatus();
    }, 30000);
  }

  private async updateBotStatus() {
    if (this.isRunning) {
      // For now, use mock data - later this will be updated by the Python bot
      this.lastStatus = {
        online: true,
        guilds: 100,
        users: 15000,
        uptime: this.getUptime(),
        lastUpdated: new Date().toISOString()
      };
    } else {
      this.lastStatus = {
        online: false,
        guilds: 0,
        users: 0,
        uptime: '0s',
        lastUpdated: new Date().toISOString()
      };
    }
  }

  private getUptime(): string {
    if (!this.botProcess) return '0s';
    const startTime = this.botProcess.spawnargs.includes('--start-time') ? 
      parseInt(this.botProcess.spawnargs[this.botProcess.spawnargs.indexOf('--start-time') + 1]) : 
      Date.now();
    const uptime = Date.now() - startTime;
    const seconds = Math.floor(uptime / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h ${minutes % 60}m`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }

  public async startBot(): Promise<boolean> {
    if (this.isRunning) {
      console.log('Bot is already running');
      return true;
    }

    try {
      const botPath = resolve(__dirname, '../bot-python/main.py');
      
      this.botProcess = spawn('python', [botPath], {
        cwd: resolve(__dirname, '../bot-python'),
        env: {
          ...process.env,
          DISCORD_TOKEN: process.env.DISCORD_BOT_TOKEN,
          NEXGUARD_API_URL: 'http://localhost:5000',
          DATABASE_URL: process.env.DATABASE_URL
        },
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.botProcess.stdout?.on('data', (data) => {
        console.log(`[Bot] ${data.toString()}`);
      });

      this.botProcess.stderr?.on('data', (data) => {
        console.error(`[Bot Error] ${data.toString()}`);
      });

      this.botProcess.on('close', (code) => {
        console.log(`Bot process exited with code ${code}`);
        this.isRunning = false;
        this.updateBotStatus();
      });

      this.botProcess.on('error', (error) => {
        console.error('Bot process error:', error);
        this.isRunning = false;
        this.updateBotStatus();
      });

      this.isRunning = true;
      this.updateBotStatus();
      
      console.log('Bot started successfully');
      return true;
    } catch (error) {
      console.error('Failed to start bot:', error);
      this.isRunning = false;
      this.updateBotStatus();
      return false;
    }
  }

  public async stopBot(): Promise<boolean> {
    if (!this.isRunning || !this.botProcess) {
      console.log('Bot is not running');
      return true;
    }

    try {
      this.botProcess.kill('SIGTERM');
      
      // Wait for graceful shutdown
      await new Promise<void>((resolve) => {
        const timeout = setTimeout(() => {
          if (this.botProcess) {
            this.botProcess.kill('SIGKILL');
          }
          resolve();
        }, 10000);

        this.botProcess!.on('close', () => {
          clearTimeout(timeout);
          resolve();
        });
      });

      this.isRunning = false;
      this.botProcess = null;
      this.updateBotStatus();
      
      console.log('Bot stopped successfully');
      return true;
    } catch (error) {
      console.error('Failed to stop bot:', error);
      return false;
    }
  }

  public getStatus() {
    return this.lastStatus || {
      online: false,
      guilds: 0,
      users: 0,
      uptime: '0s',
      lastUpdated: new Date().toISOString()
    };
  }

  public isOnline(): boolean {
    return this.isRunning;
  }

  public async restart(): Promise<boolean> {
    console.log('Restarting bot...');
    await this.stopBot();
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
    return await this.startBot();
  }

  public cleanup() {
    if (this.statusUpdateInterval) {
      clearInterval(this.statusUpdateInterval);
    }
    if (this.isRunning) {
      this.stopBot();
    }
  }
}

export const botManager = new BotManager();