import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-misis-2025'
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')
    
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
