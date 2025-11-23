import os
from datetime import timedelta

class Config:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY: #raise error if not set
        print("WARNING: SECRET_KEY not set — using insecure development key.")
        SECRET_KEY = "dev-temp-secret-key"

    WTF_CSRF_ENABLED = True # enabling csrf protection

    SESSION_COOKIE_HTTPONLY = True
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_SAMESITE = 'Lax' #mitigates csrf risks

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30) #session expiry

    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # logging config
    LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOGGING_LEVEL = 'INFO'
