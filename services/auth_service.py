from flask import session
from flask_login import login_user, logout_user
from models.user import User
from models.database import db
from utils.validators import validate_user_input

class AuthService:
    
    @staticmethod
    def register_user(fullname, username, email, password, user_type='individual'):
        """Register a new user"""
        validation_error = validate_user_input({
            'fullname': fullname,
            'username': username,
            'email': email,
            'password': password
        })
        
        if validation_error:
            return False, validation_error
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return False, 'Username already exists'
        
        if User.query.filter_by(email=email).first():
            return False, 'Email already exists'
        
        # Create new user
        user = User(
            full_name=fullname,
            username=username,
            email=email,
            user_type=user_type
        )
        user.password = password
        
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            
            # Set session variables
            session['user_id'] = user.id
            session['username'] = user.username
            session['fullname'] = user.full_name
            session['user_type'] = user.user_type
            
            return True, 'Registration successful'
        except Exception as e:
            db.session.rollback()
            return False, f'Registration failed: {str(e)}'
    
    @staticmethod
    def login_user(username, password):
        """Authenticate and login user"""
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.verify_password(password):
            login_user(user)
            
            # Set session variables
            session['user_id'] = user.id
            session['username'] = user.username
            session['fullname'] = user.full_name
            session['user_type'] = user.user_type
            
            return True, 'Login successful'
        
        return False, 'Invalid username or password'
    
    @staticmethod
    def logout_user():
        """Logout current user"""
        logout_user()
        session.clear()
        return True, 'Logged out successfully'