from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, message = AuthService.login_user(username, password)
        
        if success:
            flash(message, 'success')
            
            # Redirect based on user type
            if session.get('user_type') == 'ngo':
                return redirect(url_for('ngo.dashboard'))
            else:
                return redirect(url_for('individual.home'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type', 'individual')
    
    success, message = AuthService.register_user(
        fullname, username, email, password, user_type
    )
    
    if success:
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash(message, 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    AuthService.logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))