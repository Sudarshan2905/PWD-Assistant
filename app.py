from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from functools import wraps

app = Flask(__name__, 
            static_url_path='/static', 
            static_folder='static', 
            template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# MySQL Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306))
}


def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# ===== SIMPLIFIED MIDDLEWARE =====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def ngo_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'ngo':
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

# ===== BASIC ROUTES (Matching your original structure) =====
@app.route('/')
def index():
    """Main landing page"""
    return render_template('abcd.html')

@app.route('/index')
def index_redirect():
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, username))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['fullname'] = user['full_name']
                    session['user_type'] = user.get('user_type', 'individual')
                    session['email'] = user['email']
                    session['created_at'] = user.get('created_at', 'Recently')
                    
                    flash('Login successful!', 'success')
                    if session['user_type'] == 'ngo':
                        return redirect('/ngo/dashboard')
                    else:
                        return redirect('/home')
        
        flash('Invalid username or password', 'error')
        return redirect('/login')
    
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type', 'individual')
    
    if not all([fullname, username, email, password]):
        flash('All fields are required', 'error')
        return redirect('/login')
    
    if len(password) < 6:
        flash('Password must be at least 6 characters', 'error')
        return redirect('/login')
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (full_name, username, email, password, user_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (fullname, username, email, hashed_password, user_type))
            conn.commit()
            
            cursor.execute("""
                SELECT id, full_name, username, user_type, email, created_at 
                FROM users WHERE username = %s
            """, (username,))
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user[0]
                session['fullname'] = user[1]
                session['username'] = user[2]
                session['user_type'] = user[3] or 'individual'
                session['email'] = user[4]
                session['created_at'] = user[5]
            
            cursor.close()
            conn.close()
            
            flash('Registration successful!', 'success')
            if user_type == 'ngo':
                return redirect('/ngo/dashboard')
            else:
                return redirect('/home')
                
        except Error as e:
            cursor.close()
            conn.close()
            if "Duplicate entry" in str(e):
                flash('Username or email already exists', 'error')
            else:
                flash('Registration failed. Please try again.', 'error')
            return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect('/')

# ===== PROFILE ROUTES =====
@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Get user data with created_at timestamp
        cursor.execute("""
            SELECT *, DATE_FORMAT(created_at, '%Y-%m-%d') as created_date 
            FROM users WHERE id = %s
        """, (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            # Add additional user data to session for template
            session['email'] = user['email']
            session['created_at'] = user['created_date']
            return render_template('profile.html', user=session)
    
    flash('Unable to load profile', 'error')
    return redirect('/home')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    
    if not fullname or not email:
        flash('All fields are required', 'error')
        return redirect('/profile')
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users 
                SET full_name = %s, email = %s
                WHERE id = %s
            """, (fullname, email, session['user_id']))
            conn.commit()
            
            # Update session
            session['fullname'] = fullname
            session['email'] = email
            
            cursor.close()
            conn.close()
            flash('Profile updated successfully!', 'success')
            return redirect('/profile')
        except Error as e:
            cursor.close()
            conn.close()
            if "Duplicate entry" in str(e):
                flash('Email already exists', 'error')
            else:
                flash(f'Error updating profile: {str(e)}', 'error')
            return redirect('/profile')
    return redirect('/profile')

# ===== INDIVIDUAL USER ROUTES =====
@app.route('/home')
@login_required
def home():
    if session.get('user_type') == 'ngo':
        return redirect('/ngo/dashboard')
    return render_template('index.html', user=session)

@app.route('/services')
@login_required
def services():
    if session.get('user_type') == 'ngo':
        return redirect('/ngo/dashboard')
    return render_template('planner.html', user=session)

@app.route('/resources')
@login_required
def resources():
    if session.get('user_type') == 'ngo':
        return redirect('/ngo/dashboard')
    return render_template('guide.html', user=session)

@app.route('/community')
@login_required
def community():
    if session.get('user_type') == 'ngo':
        return redirect('/ngo/dashboard')
    return render_template('community.html', user=session)

@app.route('/about')
@login_required
def about():
    if session.get('user_type') == 'ngo':
        return redirect('/ngo/dashboard')
    return render_template('about.html', user=session)

# ===== NGO ROUTES =====
@app.route('/ngo/dashboard')
@ngo_required
def ngo_dashboard():
    return render_template('sample.html', user=session)

@app.route('/ngo/analyze')
@ngo_required
def ngo_analyze():
    return render_template('login_ngo.html', user=session)

# ===== API ROUTES =====
@app.route('/api/students', methods=['GET'])
@ngo_required
def get_students():
    # Additional check to ensure user is NGO
    if session.get('user_type') != 'ngo':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ngo_students WHERE ngo_id = %s ORDER BY created_at DESC", (session['user_id'],))
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(students)
    return jsonify([])

@app.route('/api/students', methods=['POST'])
@ngo_required
def add_student():
    if session.get('user_type') != 'ngo':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.json
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ngo_students (ngo_id, name, age, certificate_file)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], data['name'], data['age'], data.get('certificate_file')))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/students/<int:student_id>', methods=['PUT'])
@ngo_required
def update_student(student_id):
    if session.get('user_type') != 'ngo':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.json
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ngo_students 
            SET name = %s, age = %s, certificate_file = %s
            WHERE id = %s AND ngo_id = %s
        """, (data['name'], data['age'], data.get('certificate_file'), student_id, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@ngo_required
def delete_student(student_id):
    if session.get('user_type') != 'ngo':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ngo_students WHERE id = %s AND ngo_id = %s", (student_id, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    return jsonify({'success': False})

# ===== INITIALIZATION =====
def setup_database():
    """Setup database with required tables"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if users table has user_type column
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'pwd_assistant' 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'user_type'
            """)
            
            if not cursor.fetchone():
                print("Adding user_type column to users table...")
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN user_type ENUM('individual', 'ngo') DEFAULT 'individual'
                """)
                print("✓ Added user_type column")
            
            # Create ngo_students table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ngo_students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ngo_id INT,
                    name VARCHAR(100) NOT NULL,
                    age INT,
                    disability_type VARCHAR(100),
                    certificate_file VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ngo_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✓ Database setup completed")
            return True
            
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("PWD Assistant Server Starting...")
    print("=" * 50)
    
    if setup_database():
        print("✓ Database is ready")
    else:
        print("✗ Database setup failed")
    
    print("\nServer running at: http://localhost:5000")
    print("\nAvailable routes:")
    print("  /              - Landing page (Individual/NGO)")
    print("  /login         - Login page")
    print("  /signup        - Signup page")
    print("  /logout        - Logout")
    print("  /profile       - User Profile")
    print("  /update_profile - Update Profile")
    print("  /home          - Individual home")
    print("  /services      - Services hub")
    print("  /resources     - Resources")
    print("  /community     - Community")
    print("  /about         - About us")
    print("  /ngo/dashboard - NGO Dashboard")
    print("  /ngo/analyze   - NGO Analysis")
    print("\nAPI endpoints:")
    print("  /api/students  - NGO student management")
    print("=" * 50)
    
    app.run(debug=True, port=5000)