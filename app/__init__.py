import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from config import Config
import logging
from logging.handlers import RotatingFileHandler

csrf = CSRFProtect()
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address) #adding a rate limiter to prevent brute force login attempts
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app) #for pw hashing in models.py
    limiter.init_app(app)
    csrf.init_app(app) #csrf protect

    from app.routes import main
    app.register_blueprint(main)

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

    #prevent broswer from caching pages that contain forms to avoid stale csrf token issues (400 Bad Request)
    @app.after_request
    def add_security_headers(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    with app.app_context():
        from .models import User, CycleSettings, PeriodLog
        db.create_all()

        try:
            if not User.query.first():
                sample_users = [
                    {"name": "Alice", "email": "alice@example.com", "password": "Password123!"},
                    {"name": "Bob", "email": "bob@example.com", "password": "SecurePass1@"},
                    {"name": "Charlie", "email": "charlie@example.com", "password": "MyPass!2025"}
                ]
                for u in sample_users:
                    user = User()
                    user.name = u["name"]
                    user.email = u["email"]
                    user.set_password(u["password"])
                    db.session.add(user)
                db.session.commit()
                app.logger.info("Database initialized with default users.")
        except Exception as e:
            app.logger.error("Failed to insert sample users.", exc_info=e)

    return app

