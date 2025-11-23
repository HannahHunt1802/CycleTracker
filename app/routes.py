import hashlib
import traceback
from flask import request, render_template, redirect, url_for, session, Blueprint, flash, abort, current_app
from app import db, limiter, bcrypt
from app.forms import RegisterForm, LoginForm
from app.models import User

main = Blueprint('main', __name__)

#helper method to hash sensitive data for logging
def hash_for_log(value):
    return hashlib.sha256(str(value).encode()).hexdigest()

@main.route('/')
def base():
    return render_template('base.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    user_ip = request.remote_addr or "Unknown IP" #must be INSIDE route

    if form.validate_on_submit():
        try:
            name = form.name.data.strip()
            email= form.email.data.strip()
            password = form.password.data.strip()

            new_user = User()
            new_user.name = name
            new_user.email = email
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            current_app.logger.info(f"New registration. Username: {hash_for_log(name)}, IP Address: {hash_for_log(user_ip)}")

            #clear existing session to prevent session fixation
            session.clear()
            session['name']= name
            session['email'] = email
            return redirect(url_for('main.login'))

        except Exception:
            db.session.rollback()
            current_app.logger.error(f"Registration failed, {traceback.format_exc()}, IP: {hash_for_log(user_ip)}")
            flash("An unexpected error has occurred, please try again.", "error")

    else:
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", 'error')
                    current_app.logger.warning(f"Registration validation failed. Field: {field}, "
                                               f"Error: {error}, IP: {hash_for_log(user_ip)}.")
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    user_ip = request.remote_addr or "Unknown IP"
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()

            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session.clear()
                session.permanent=True
                session['user_id'] = user.id
                session['name'] = user.name

                flash('Login successful!', 'success')
                current_app.logger.info(f'Successfully logged in. Username: {hash_for_log(user.name)}, IP Address: {hash_for_log(user_ip)}')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid username or password.', 'error')
                current_app.logger.warning(f'Failed login attempt. IP: {hash_for_log(user_ip)}.')
        except Exception:
            db.session.rollback()
            current_app.logger.error(f"Login failed: {traceback.format_exc()}, IP: {hash_for_log(user_ip)}")
            flash("An unexpected error occurred. Please try again.", "error")
    return render_template('login.html', form=form)

@main.route('/dashboard')
def dashboard():
    return "DASHBOARD"