import os
import secrets
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables first
load_dotenv()

class Config:
    """Base configuration with default settings"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application settings
    PREDICTION_MODELS_DIR = os.path.join(os.path.dirname(__file__), '../models')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB upload limit
    
    # API settings
    COINGECKO_API_URL = os.environ.get('COINGECKO_API_URL', 'https://api.coingecko.com/api/v3')
    REQUEST_TIMEOUT = 30  # seconds
    
    @classmethod
    def check_required_vars(cls):
        """Validate required environment variables"""
        if not os.environ.get('SECRET_KEY') and cls.FLASK_ENV == 'production':
            raise ValueError("SECRET_KEY must be set in production environment")

class DevelopmentConfig(Config):
    """Development-specific configuration"""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = False  # Allow non-HTTPS in dev
    
    # Enable more verbose logging
    LOG_LEVEL = 'DEBUG'
    
    # Use local cache
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SECRET_KEY = 'testing-secret-key'  # Hardcoded for test consistency
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    
    # Enhanced security
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Production cache (example with Redis)
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

def get_config(env: str = None) -> Config:
    """Factory method to get appropriate config"""
    env = env or os.environ.get('FLASK_ENV', 'production')
    
    config_mapping: Dict[str, Any] = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    config = config_mapping.get(env.lower(), ProductionConfig)
    config.check_required_vars()
    return config

# Initialize configuration
current_config = get_config()

# Warning for development
if current_config.FLASK_ENV == 'development' and not os.environ.get('SECRET_KEY'):
    print("⚠️  Warning: Using temporary secret key. Set SECRET_KEY in .env for production!")