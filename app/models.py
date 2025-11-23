from app import db
from sqlalchemy import DateTime, func
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) #length to store hashed passwords

    # store passwords securely
    def set_password(self, raw_password):
        self.password = Bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password):
        return Bcrypt.check_password_hash(self.password, raw_password)

    #optional info
    dob = db.Column(db.Date, nullable=True)
    regular_cycle = db.Column(db.Boolean, nullable=True, default=True) #true if regular, false if irregular
    avg_period_length = db.Column(db.Integer, nullable=True, default=5)
    avg_cycle_length = db.Column(db.Integer, nullable=True, default=28)
    last_period_start = db.Column(db.Date, nullable=True)
    last_period_end = db.Column(db.Date, nullable=True)

    #for auditing
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())