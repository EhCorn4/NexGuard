import { spawn, ChildProcess } from 'child_process';
import { resolve } from 'path';
import { existsSync, readFileSync } from 'fs';
import * as path from 'path';

class SimpleBotManager {
  private static instance: SimpleBotManager;
  private botProcess: ChildProcess | null = null;
  private isRunning = false;
  private statusInterval: NodeJS.Timeout | null = null;
  
  private constructor() {}

  public static getInstance(): SimpleBotManager {
    if (!SimpleBotManager.instance) {
      SimpleBotManager.instance = new SimpleBotManager();
    }
    return SimpleBotManager.instance;
  }

  public async startBot(): Promise<boolean> {
    if (this.isRunning) {
      console.log('Bot is already running');
      return true;
    }

    try {
      console.log('Starting simple Discord bot...');
      
      // Kill any existing bot processes
      try {
        const killProcess = spawn('pkill', ['-f', 'python3.*simple_bot.py']);
        await new Promise<void>((resolve) => {
          killProcess.on('exit', () => resolve());
          killProcess.on('error', () => resolve());
        });
      } catch (e) {
        // Ignore kill errors
      }

      // Clear old status files
      try {
        const fs = require('fs');
        if (fs.existsSync('/tmp/nexguard_bot_status.json')) {
          fs.unlinkSync('/tmp/nexguard_bot_status.json');
        }
      } catch (e) {
        // Ignore cleanup errors
      }

      // Start the bot
      this.botProcess = spawn('python3', ['simple_bot.py'], {
        cwd: './bot-python',
        env: {
          ...process.env,
          DISCORD_TOKEN: process.env.DISCORD_BOT_TOKEN,
          DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN,
        },
        stdio: 'inherit'
      });

      this.isRunning = true;

      // Set up process exit handler
      this.botProcess.on('exit', (code) => {
        console.log(`Bot process exited with code ${code}`);
        this.isRunning = false;
        this.botProcess = null;
      });

      this.botProcess.on('error', (error) => {
        console.error('Bot process error:', error);
        this.isRunning = false;
        this.botProcess = null;
      });

      // Wait for bot to be ready
      for (let i = 0; i < 10; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (this.isBotReady()) {
          console.log('Bot is ready!');
          return true;
        }
      }

      // If we get here, assume success if process is still running
      if (this.botProcess && this.botProcess.exitCode === null) {
        console.log('Bot process is running, assuming success');
        return true;
      } else {
        console.error('Bot failed to start');
        this.isRunning = false;
        return false;
      }
    } catch (error) {
      console.error('Error starting bot:', error);
      this.isRunning = false;
      return false;
    }
  }

  public async stopBot(): Promise<boolean> {
    if (!this.isRunning) {
      console.log('Bot is not running');
      return true;
    }

    try {
      // Kill the bot process
      if (this.botProcess) {
        this.botProcess.kill('SIGTERM');
        await new Promise<void>((resolve) => {
          const timeout = setTimeout(() => {
            if (this.botProcess) {
              this.botProcess.kill('SIGKILL');
            }
            resolve();
          }, 5000);

          this.botProcess!.on('exit', () => {
            clearTimeout(timeout);
            resolve();
          });
        });
      }

      // Also kill any python processes
      try {
        const killProcess = spawn('pkill', ['-f', 'python3.*simple_bot.py']);
        await new Promise<void>((resolve) => {
          killProcess.on('exit', () => resolve());
          killProcess.on('error', () => resolve());
        });
      } catch (e) {
        // Ignore kill errors
      }

      this.isRunning = false;
      this.botProcess = null;
      console.log('Bot stopped');
      return true;
    } catch (error) {
      console.error('Error stopping bot:', error);
      return false;
    }
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
          commands: 11, // Number of basic commands
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
    if (!this.botProcess) return '0s';
    
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

  public async restart(): Promise<boolean> {
    console.log('Restarting bot...');
    await this.stopBot();
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
    return await this.startBot();
  }

  public isOnline(): boolean {
    return this.isRunning && this.isBotReady();
  }
}

export const simpleBotManager = SimpleBotManager.getInstance();