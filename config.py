import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """secrets."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    DATABASE_PATH = BASE_DIR / 'src' / 'db' / 'db.sqlite3'
    
    GOOGLE_CREDENTIALS_PATH = BASE_DIR / 'credentials.json'
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

# Dictionary to hold the configuration classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}