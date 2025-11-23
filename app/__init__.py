import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
import logging
from logging.handlers import RotatingFileHandler

csrf = CSRFProtect()
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address) #adding a rate limiter to prevent brute force login attempts

def create_app():
    app = Flask(__name__)
    limiter.init_app(app)
    app.config.from_object(Config)

    #csrf protection
    csrf.init_app(app) #csrf protect

    # configuring logging for log rotation
    log_dir='logs'
    if not os.path.exists(log_dir): #check if directory exists
        os.makedirs(log_dir)

    #rotating logging
    log_file = os.path.join(log_dir, 'app.log')
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%d-%m-%Y %H:%M:%S')
    handler.setFormatter(formatter)

    #clear default handlers
    app.logger.handlers=[]
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    db.init_app(app)

    return app

