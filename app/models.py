from app import db, bcrypt
from sqlalchemy import DateTime, func, event
from flask_login import UserMixin

# user table
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) #length to store hashed passwords

    #for auditing
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())

    #relationships
    cycle_settings=db.relationship("CycleSettings", backref="user", uselist=False, cascade="all, delete") #1-1
    period_log=db.relationship("PeriodLog", backref="user", lazy=True, cascade="all, delete") #1-many

    # store passwords securely
    def set_password(self, raw_password):
        self.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password, raw_password)

# cycle settings table
class CycleSettings(db.Model):
    __tablename__ = 'cycle_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    regular_cycle = db.Column(db.Boolean, nullable=False, default=True)  # true if regular, false if irregular
    avg_period_length = db.Column(db.Integer, nullable=False, default=5)
    avg_cycle_length = db.Column(db.Integer, nullable=False, default=28)

    updated_at = db.Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

#event listener to automatically insert default cycle settings when a new user is created
@event.listens_for(User, "after_insert")
def create_default_related_rows(mapper, connection, target):
    connection.execute(
        CycleSettings.__table__.insert().values(
            user_id=target.id,
            regular_cycle=True,
            avg_period_length=5,
            avg_cycle_length=28
        )
    )

#individual period table
class PeriodLog(db.Model):
    __tablename__ = 'period_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    period_start = db.Column(db.Date, nullable=True)
    period_end = db.Column(db.Date, nullable=True)

    created_at = db.Column(DateTime(timezone=True), server_default=func.now())

    #
    __table_args__ = (
        db.UniqueConstraint('user_id', 'period_start', 'period_end', name='unique_period_per_user'),)