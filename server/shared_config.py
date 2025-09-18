#!/usr/bin/env python3

import os

class Config:
    """Shared configuration for Python components"""
    
    @staticmethod
    def get_database_url():
        """Get the shared database URL - prioritize SHARED_DATABASE_URL for cross-environment consistency"""
        # Check for shared database URL first (takes precedence)
        shared_database_url = os.getenv('SHARED_DATABASE_URL')
        fallback_database_url = os.getenv('DATABASE_URL')
        
        if shared_database_url:
            database_url = shared_database_url
            source = 'SHARED_DATABASE_URL (enforced cross-environment)'
        elif fallback_database_url:
            database_url = fallback_database_url
            source = 'DATABASE_URL (environment-specific)'
        else:
            raise ValueError("Either SHARED_DATABASE_URL or DATABASE_URL must be set. Did you forget to provision a database?")
            
        # Log which database source is being used (mask credentials)
        import re
        masked_url = re.sub(r'(://[^:]+:)[^@]+(@)', r'\1***\2', database_url)
        print(f"🗄️  Python Database: Using {source} - {masked_url}")
        return database_url
    
    @staticmethod
    def get_environment():
        """Get the current environment"""
        return os.getenv('NODE_ENV', 'development')

# Export singleton config
config = Config()