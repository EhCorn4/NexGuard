// Shared configuration for both development and production environments
// This ensures both environments use the same database URL

interface AppConfig {
  databaseUrl: string;
  environment: string;
  botHttpPort: number;
}

// Get the shared database URL - prioritize SHARED_DATABASE_URL to force same DB across environments
function getDatabaseUrl(): string {
  // Check for shared database URL first (takes precedence over individual env DATABASE_URLs)
  const sharedDatabaseUrl = process.env.SHARED_DATABASE_URL;
  const fallbackDatabaseUrl = process.env.DATABASE_URL;
  
  let databaseUrl: string;
  let source: string;
  
  if (sharedDatabaseUrl) {
    databaseUrl = sharedDatabaseUrl;
    source = 'SHARED_DATABASE_URL (enforced cross-environment)';
  } else if (fallbackDatabaseUrl) {
    databaseUrl = fallbackDatabaseUrl;
    source = 'DATABASE_URL (environment-specific)';
  } else {
    throw new Error(
      "Either SHARED_DATABASE_URL or DATABASE_URL must be set. Did you forget to provision a database?"
    );
  }

  // Log which database source is being used (mask credentials)
  const maskedUrl = databaseUrl.replace(/(:\/\/[^:]+:)[^@]+(@)/, '$1***$2');
  console.log(`🗄️  Database: Using ${source} - ${maskedUrl}`);
  
  return databaseUrl;
}

export const config: AppConfig = {
  databaseUrl: getDatabaseUrl(),
  environment: process.env.NODE_ENV || 'development',
  botHttpPort: parseInt(process.env.BOT_HTTP_PORT || '5001'),
};

// Export for legacy compatibility
export const DATABASE_URL = config.databaseUrl;