import os

class Config:
    """Application configuration class"""
    # Flask config
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'instagpt_secret_key')
    DEBUG = True
    
    # OpenAI Config
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Admin config
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Memory storage config
    MEMORY_DIR = os.environ.get('MEMORY_DIR', '.')
    MAX_MEMORY_MESSAGES = 50  # Maximum number of messages to store per user
