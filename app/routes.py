import hashlib
import traceback
from flask import request, render_template, redirect, url_for, session, Blueprint, flash, current_app, abort
from functools import wraps

from app import db, limiter, bcrypt
from app.forms import RegisterForm, LoginForm, LogoutForm, UpdateProfileForm, ChangePasswordForm, UpdateCycleSettingsForm, DeleteAccountForm
from app.models import User
from app.cycle_calc import calculate_cycle_predictions

main = Blueprint('main', __name__)

#helper method to hash sensitive data for logging
def hash_for_log(value):
    return hashlib.sha256(str(value).encode()).hexdigest()

@main.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    user_ip = request.remote_addr or "Unknown IP" #must be INSIDE route

    if register_form.validate_on_submit():
        try:
            name = register_form.name.data.strip()
            email= register_form.email.data.strip()
            password = register_form.password.data.strip()

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
        if register_form.errors:
            for field, errors in register_form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", 'error')
                    current_app.logger.warning(f"Registration validation failed. Field: {field}, "
                                               f"Error: {error}, IP: {hash_for_log(user_ip)}.")
    return render_template('register.html', register_form=register_form)

#method to protect the dashboard, ensures user must log in before being granted access
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return wrap

@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    login_form = LoginForm()
    user_ip = request.remote_addr or "Unknown IP"
    if login_form.validate_on_submit():
        try:
            user = User.query.filter_by(email=login_form.email.data).first()

            if user and bcrypt.check_password_hash(user.password, login_form.password.data):
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
    return render_template('login.html', login_form=login_form)

@main.route('/logout', methods=['POST'])
@login_required
def logout():
    user_ip = request.remote_addr or "Unknown IP"
    user_id = session.get('user_id')
    session.clear()
    current_app.logger.info(f"Logged out user: {hash_for_log(user_id)}, IP: {hash_for_log(user_ip)}")
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.login'))


#helper methods for rendering dashboard template
def get_current_user():
    user_id = session.get('user_id')
    return db.session.get(User, user_id) if user_id else None

def dashboard_context():
    user = get_current_user()

    return {
        "user": user,
        "logout_form": LogoutForm(),
        "update_profile_form": UpdateProfileForm(),
        "change_password_form": ChangePasswordForm(),
        "update_cycle_settings_form": UpdateCycleSettingsForm(),
        "delete_account_form": DeleteAccountForm(),
        "cycle_pred": calculate_cycle_predictions(user)
    }

@main.route('/')
def base():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', **dashboard_context())

#MY ACCOUNT TAB
@main.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    update_profile_form = UpdateProfileForm()
    user_ip = request.remote_addr or "Unknown IP"
    user = get_current_user()

    if update_profile_form.validate_on_submit():
        try:
            old_name = user.name
            old_email = user.email

            user.name = update_profile_form.name.data.strip()
            user.email = update_profile_form.email.data.strip()
            db.session.commit()

            flash("Profile updated successfully.", "success")
            current_app.logger.info(
                f"Profile updated. User ID: {hash_for_log(user.id)}, "
                f"Old Name: {hash_for_log(old_name)}, New Name: {hash_for_log(user.name)}, "
                f"Old Email: {hash_for_log(old_email)}, New Email: {hash_for_log(user.email)}, "
                f"IP: {hash_for_log(user_ip)}"
            )

        except Exception:
            db.session.rollback()
            flash("An unexpected error occurred while updating your profile.", "error")
            current_app.logger.error(
                f"Failed to update profile. User ID: {hash_for_log(user.id)}, IP: {hash_for_log(user_ip)}",
                exc_info=True
            )
    else:
        for field, errors in update_profile_form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
                current_app.logger.warning(
                    f"Update profile validation failed. Field: {field}, Error: {error}, "
                    f"User ID: {hash_for_log(user.id)}, IP: {hash_for_log(user_ip)}"
                )
    return render_template('dashboard.html', **dashboard_context())


@main.route('/change_password', methods=['POST'])
@login_required
def change_password():
    change_password_form = ChangePasswordForm()

    user_ip = request.remote_addr or "Unknown IP"
    user = get_current_user()

    if not user:
        current_app.logger.warning(
            f"Unauthorized password change attempt. Invalid user_id in session. "
            f"user_id={hash_for_log(user.id)}, IP={hash_for_log(user_ip)}"
        )
        abort(403, description="Access denied.")

    if change_password_form.validate_on_submit():
        try:
            if not user.check_password(change_password_form.current_password.data):
                flash('Current password is incorrect.', 'error')
            elif user.check_password(change_password_form.new_password.data):
                flash('New password must be different from the current password.', 'error')
            else:
                user.set_password(change_password_form.new_password.data)
                db.session.commit()
                flash('Password changed successfully.', 'success')
                current_app.logger.info(
                    f"Password changed successfully. User: {hash_for_log(user.name)}, "
                    f"user_id={hash_for_log(user.id)}, IP={hash_for_log(user_ip)}"
                )
                return redirect(url_for('main.dashboard'))

        except Exception:
            db.session.rollback()
            flash("An unexpected error occurred while changing the password.", "error")
            current_app.logger.error(
                f"Password change failed. User: {hash_for_log(user.name)}, "
                f"user_id={hash_for_log(user.id)}, IP={hash_for_log(user_ip)}",
                exc_info=True
            )

    else:
        # Log all form validation errors
        for field, errors in change_password_form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
                current_app.logger.warning(
                    f"Change password validation failed. Field: {field}, Error: {error}, "
                    f"User: {hash_for_log(user.name)}, user_id={hash_for_log(user.id)}, IP={hash_for_log(user_ip)}"
                )

    return render_template('dashboard.html', **dashboard_context())

@main.route('/update_cycle_settings', methods=['POST'])
@login_required
def update_cycle_settings():
    form = UpdateCycleSettingsForm()
    user = get_current_user()
    user_ip = request.remote_addr or "Unknown IP"

    if form.validate_on_submit():
        try:
            user.avg_period_length = form.avg_period_length.data
            user.avg_cycle_length = form.avg_cycle_length.data
            db.session.commit()
            flash("Cycle settings updated successfully.", "success")
            current_app.logger.info(
                f"Cycle settings updated. User: {hash_for_log(user.id)}, IP: {hash_for_log(user_ip)}"
            )
        except Exception:
            db.session.rollback()
            flash("An unexpected error occurred while updating cycle settings.", "error")
            current_app.logger.error(
                f"Failed to update cycle settings. User: {hash_for_log(user.id)}, IP: {hash_for_log(user_ip)}",
                exc_info=True
            )
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "error")
                current_app.logger.warning(
                    f"Update cycle settings validation failed. Field: {field}, Error: {error}, "
                    f"User: {hash_for_log(user.id)}, IP: {hash_for_log(user_ip)}"
                )

    return render_template('dashboard.html', **dashboard_context())

@main.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = get_current_user()
    user_ip = request.remote_addr or "Unknown IP"

    if not user:
        current_app.logger.warning(
            f"Unauthorized delete account attempt. Invalid user_id in session. IP: {hash_for_log(user_ip)}"
        )
        abort(403, description="Access denied.")

    form = DeleteAccountForm()
    if form.validate_on_submit():
        try:
            user_id_hash = hash_for_log(user.id)
            db.session.delete(user)
            db.session.commit()
            session.clear()
            flash("Your account has been deleted successfully.", "success")
            current_app.logger.info(
                f"Account deleted. User: {user_id_hash}, IP: {hash_for_log(user_ip)}"
            )
            return redirect(url_for('main.register'))  # or login page
        except Exception:
            db.session.rollback()
            flash("An unexpected error occurred while deleting your account.", "error")
            current_app.logger.error(
                f"Failed to delete account. User: {hash_for_log(user.id)}, IP: {hash_for_log(user_ip)}",
                exc_info=True
            )

    else:
        flash("Form submission invalid. Please try again.", "error")
        current_app.logger.warning(
            f"Delete account form validation failed. User: {hash_for_log(user.id)}, IP: {hash_for_log(user_ip)}"
        )

    return render_template('login.html', login_form=LoginForm())

