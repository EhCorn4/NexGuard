import { Pool, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-serverless';
import ws from "ws";
import * as schema from "@shared/schema";
import { config } from "@shared/config";

neonConfig.webSocketConstructor = ws;

console.log(`🗄️  Database: Connecting to shared database for ${config.environment} environment`);
export const pool = new Pool({ connectionString: config.databaseUrl });
export const db = drizzle({ client: pool, schema });