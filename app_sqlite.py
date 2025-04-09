import os
import sqlite3
import hashlib
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, flash, g, session, abort, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from slugify import slugify
import uuid
import threading
import time
import requests
import socket
import json
import zipfile
from io import BytesIO

# Function to get local IP address
def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        # Create a socket connection to determine the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback to localhost if unable to determine IP
        return '127.0.0.1'

# Create and configure app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['DATABASE'] = os.path.join('instance', 'portfolio.db')
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'img/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

# Ensure instance directory exists
os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Log some initial information
app.logger.info('Application started')

# Helper function to check if file has allowed extension
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Database helper functions
def get_db():
    """Get database connection for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection at the end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def migrate_db():
    """Add missing columns to existing tables."""
    db = get_db()
    cursor = db.cursor()
    
    # Check if certificate_pdf column exists in Achievement table
    cursor.execute("PRAGMA table_info(Achievement)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'certificate_pdf' not in columns:
        print("Adding certificate_pdf column to Achievement table...")
        cursor.execute("ALTER TABLE Achievement ADD COLUMN certificate_pdf TEXT")
    
    # Check if linkedin_url column exists in Achievement table
    if 'linkedin_url' not in columns:
        print("Adding linkedin_url column to Achievement table...")
        cursor.execute("ALTER TABLE Achievement ADD COLUMN linkedin_url TEXT")
    
    # Check if event_type column exists in Achievement table
    if 'event_type' not in columns:
        print("Adding event_type column to Achievement table...")
        cursor.execute("ALTER TABLE Achievement ADD COLUMN event_type TEXT")
    
    # Check if achievement_type column exists in Achievement table
    if 'achievement_type' not in columns:
        print("Adding achievement_type column to Achievement table...")
        cursor.execute("ALTER TABLE Achievement ADD COLUMN achievement_type TEXT")
    
    # Check if certificate_pdf column exists in BlogPost table
    cursor.execute("PRAGMA table_info(BlogPost)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'certificate_pdf' not in columns:
        print("Adding certificate_pdf column to BlogPost table...")
        cursor.execute("ALTER TABLE BlogPost ADD COLUMN certificate_pdf TEXT")
    
    # Check if updated_at column exists in BlogPost table
    if 'updated_at' not in columns:
        print("Adding updated_at column to BlogPost table...")
        # SQLite doesn't allow CURRENT_TIMESTAMP as default in ALTER TABLE
        cursor.execute("ALTER TABLE BlogPost ADD COLUMN updated_at TIMESTAMP")
        # Update all existing rows to set updated_at equal to created_at
        cursor.execute("UPDATE BlogPost SET updated_at = created_at")
    
    # Check if display_order column exists in Skill table
    cursor.execute("PRAGMA table_info(Skill)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'display_order' not in columns:
        print("Adding display_order column to Skill table...")
        # Use a constant default value for SQLite ALTER TABLE compatibility
        cursor.execute("ALTER TABLE Skill ADD COLUMN display_order INTEGER DEFAULT 0")
    
    # Check if icon column exists in Skill table
    if 'icon' not in columns:
        print("Adding icon column to Skill table...")
        cursor.execute("ALTER TABLE Skill ADD COLUMN icon TEXT")
    
    # Check if created_at column exists in Project table
    cursor.execute("PRAGMA table_info(Project)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'created_at' not in columns:
        print("Adding created_at column to Project table...")
        # SQLite doesn't allow CURRENT_TIMESTAMP as default in ALTER TABLE
        cursor.execute("ALTER TABLE Project ADD COLUMN created_at TIMESTAMP")
        # Update all existing rows to set created_at to current time
        cursor.execute("UPDATE Project SET created_at = datetime('now')")
    
    # Check if category column exists in Project table
    if 'category' not in columns:
        print("Adding category column to Project table...")
        cursor.execute("ALTER TABLE Project ADD COLUMN category TEXT")
    
    # Check if featured column exists in Project table
    if 'featured' not in columns:
        print("Adding featured column to Project table...")
        cursor.execute("ALTER TABLE Project ADD COLUMN featured INTEGER DEFAULT 0")
    
    db.commit()
    print("Database migration completed.")

def create_tables():
    """Create tables if they don't exist."""
    db = get_db()
    cursor = db.cursor()
    
    # Create tables if they don't exist
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS About (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT (datetime('now'))
    );
    
    CREATE TABLE IF NOT EXISTS Skill (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        proficiency INTEGER NOT NULL,
        icon TEXT,
        display_order INTEGER DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS Project (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        image TEXT,
        github_link TEXT,
        live_link TEXT,
        categories TEXT,
        category TEXT,
        featured INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT (datetime('now'))
    );
    
    CREATE TABLE IF NOT EXISTS Achievement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        date DATE,
        image TEXT,
        certificate_pdf TEXT
    );
    
    CREATE TABLE IF NOT EXISTS Education (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institution TEXT NOT NULL,
        degree TEXT NOT NULL,
        field TEXT NOT NULL,
        start_date DATE,
        end_date DATE,
        description TEXT
    );
    
    CREATE TABLE IF NOT EXISTS BlogPost (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        image TEXT,
        certificate_pdf TEXT,
        created_at TIMESTAMP DEFAULT (datetime('now')),
        updated_at TIMESTAMP DEFAULT (datetime('now')),
        slug TEXT UNIQUE
    );
    
    CREATE TABLE IF NOT EXISTS Contact (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT (datetime('now')),
        is_read INTEGER DEFAULT 0
    );
    ''')
    
    db.commit()

def init_db():
    """Initialize the database."""
    # Create tables if they don't exist
    create_tables()
    
    # Migrate database to add any missing columns
    migrate_db()
    
    # Check if admin user exists and create one if not
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM User WHERE is_admin = 1')
    admin = cursor.fetchone()
    
    if not admin:
        from werkzeug.security import generate_password_hash
        cursor.execute(
            'INSERT INTO User (username, password, is_admin) VALUES (?, ?, ?)',
            ('admin', generate_password_hash('admin'), 1)
        )
        db.commit()
        print("Created default admin user (username: admin, password: admin)")

# Initialize the database
with app.app_context():
    init_db()

# Register close_db to be called when the application context ends
app.teardown_appcontext(close_db)

# Authentication functions
def login_required(view):
    """Decorator to require login for views."""
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return view(**kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view

def admin_required(view):
    """Decorator to require admin privileges for views."""
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT * FROM User WHERE id = ?', (session['user_id'],)).fetchone()
        
        if not user or not user['is_admin']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
            
        return view(**kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view

# Pagination class
class Pagination:
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return max(1, (self.total_count + self.per_page - 1) // self.per_page)

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None

    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=2, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge 
                or (self.page - left_current <= num <= self.page + right_current)
                or num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num

# Helper functions
def format_datetime(value, format='%B %d, %Y'):
    """Format a datetime object."""
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
    return value.strftime(format)

def nl2br(value):
    """Convert newlines to <br> tags."""
    if not value:
        return ''
    return value.replace('\n', '<br>')

# Register template filters
app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['nl2br'] = nl2br

# Context processors
@app.context_processor
def inject_now():
    """Inject current datetime into templates."""
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_user():
    """Inject current user into templates."""
    user = None
    if 'user_id' in session:
        db = get_db()
        user = db.execute('SELECT * FROM User WHERE id = ?', (session['user_id'],)).fetchone()
    return {'current_user': user}

@app.context_processor
def inject_unread_messages():
    """Make unread message count available in admin templates."""
    # Only calculate if user is logged in
    if 'user_id' in session:
        db = get_db()
        unread_message_count = db.execute(
            'SELECT COUNT(*) FROM Contact WHERE is_read = 0'
        ).fetchone()[0]
        return {'unread_message_count': unread_message_count}
    return {'unread_message_count': 0}

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors with custom template."""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors with custom template."""
    return render_template('errors/500.html'), 500

# Routes
@app.route('/')
def index():
    """Main portfolio page."""
    db = get_db()
    
    # Get about content
    about = db.execute('SELECT * FROM About ORDER BY id DESC LIMIT 1').fetchone()
    
    # Get skills by category
    skills = db.execute('SELECT * FROM Skill ORDER BY category').fetchall()
    skills_by_category = {}
    for skill in skills:
        if skill['category'] not in skills_by_category:
            skills_by_category[skill['category']] = []
        skills_by_category[skill['category']].append(skill)
    
    # Get featured projects
    featured_projects_raw = db.execute('SELECT * FROM Project WHERE github_link IS NOT NULL').fetchall()
    
    # Convert to dictionaries and add technologies field for template compatibility
    featured_projects = []
    for project in featured_projects_raw:
        project_dict = dict(project)
        # Map categories to technologies for template compatibility
        project_dict['technologies'] = project_dict.get('categories', '')
        # Map other field names for template compatibility
        project_dict['url'] = project_dict.get('live_link', '')
        project_dict['github_url'] = project_dict.get('github_link', '')
        featured_projects.append(project_dict)
    
    # Get other projects
    other_projects_raw = db.execute('SELECT * FROM Project WHERE github_link IS NULL LIMIT 3').fetchall()
    
    # Convert to dictionaries and add technologies field for template compatibility
    other_projects = []
    for project in other_projects_raw:
        project_dict = dict(project)
        # Map categories to technologies for template compatibility
        project_dict['technologies'] = project_dict.get('categories', '')
        # Map other field names for template compatibility
        project_dict['url'] = project_dict.get('live_link', '')
        project_dict['github_url'] = project_dict.get('github_link', '')
        other_projects.append(project_dict)
    
    # Get achievements - handle date format issue by using strftime to format the date
    try:
        # Fetch all achievements and events in one query
        achievements = db.execute(
            '''SELECT id, title, description, image, certificate_pdf, linkedin_url, event_type, achievement_type,
                  strftime('%Y-%m-%d', date) as formatted_date 
               FROM Achievement 
               ORDER BY date DESC'''
        ).fetchall()
        
        # Convert achievements to a list of dictionaries with properly formatted dates
        formatted_achievements = []
        for achievement in achievements:
            achievement_dict = dict(achievement)
            # Add a 'date' field with the properly formatted date
            achievement_dict['date'] = achievement_dict.get('formatted_date', '')
            # Convert string date to datetime object for template
            if achievement_dict['date']:
                try:
                    achievement_dict['date'] = datetime.strptime(achievement_dict['date'], '%Y-%m-%d')
                except ValueError:
                    pass
                    
            # Add special flag for competition wins (used for styling)
            if achievement_dict.get('achievement_type') == 'Competition' and ('1st' in achievement_dict.get('title', '') or 'Winner' in achievement_dict.get('title', '')):
                achievement_dict['is_winner'] = True
            else:
                achievement_dict['is_winner'] = False
                
            # Add special flag for certifications (used for styling)
            if achievement_dict.get('achievement_type') == 'Certification':
                achievement_dict['is_certification'] = True
            else:
                achievement_dict['is_certification'] = False
                
            formatted_achievements.append(achievement_dict)
        
        # Group achievements by type for the template
        achievements_by_type = {}
        for achievement in formatted_achievements:
            if achievement.get('achievement_type'):
                achievement_type = achievement.get('achievement_type', 'Other')
                if achievement_type not in achievements_by_type:
                    achievements_by_type[achievement_type] = []
                achievements_by_type[achievement_type].append(achievement)
            elif achievement.get('event_type'):
                event_type = achievement.get('event_type', 'Other')
                if event_type not in achievements_by_type:
                    achievements_by_type[event_type] = []
                achievements_by_type[event_type].append(achievement)
        
    except Exception as e:
        print(f"Error formatting achievement dates: {str(e)}")
        # Fallback to simpler query if there's an error
        achievements = db.execute(
            '''SELECT id, title, description, image, certificate_pdf, linkedin_url, event_type, achievement_type
               FROM Achievement'''
        ).fetchall()
        formatted_achievements = list(achievements)
        achievements_by_type = {'Other': formatted_achievements}
    
    # Note: We no longer need a separate events query as we merged them into achievements
    
    # Get education - handle date format issue by using strftime to format the dates
    try:
        education_items = db.execute(
            '''SELECT id, institution, degree, field, description, 
                  strftime('%Y-%m-%d', start_date) as formatted_start_date,
                  strftime('%Y-%m-%d', end_date) as formatted_end_date
               FROM Education ORDER BY start_date DESC'''
        ).fetchall()
        
        # Convert education items to a list of dictionaries with properly formatted dates
        formatted_education = []
        for edu in education_items:
            edu_dict = dict(edu)
            # Convert string dates to datetime objects for template
            if edu_dict.get('formatted_start_date'):
                try:
                    edu_dict['start_date'] = datetime.strptime(edu_dict['formatted_start_date'], '%Y-%m-%d')
                except ValueError:
                    edu_dict['start_date'] = ''
            if edu_dict.get('formatted_end_date'):
                try:
                    edu_dict['end_date'] = datetime.strptime(edu_dict['formatted_end_date'], '%Y-%m-%d')
                except ValueError:
                    edu_dict['end_date'] = ''
            formatted_education.append(edu_dict)
            
    except Exception as e:
        print(f"Error formatting education dates: {str(e)}")
        # Fallback to simpler query if there's an error
        education_items = db.execute('SELECT id, institution, degree, field, description FROM Education').fetchall()
        formatted_education = list(education_items)
    
    # Get blog posts
    blog_posts = db.execute('SELECT * FROM BlogPost ORDER BY created_at DESC LIMIT 3').fetchall()
    
    return render_template('index.html',
                          about=about,
                          skills_by_category=skills_by_category,
                          featured_projects=featured_projects,
                          other_projects=other_projects,
                          achievements=formatted_achievements,
                          achievements_by_type=achievements_by_type,
                          education=formatted_education,
                          blog_posts=blog_posts)

@app.route('/blog')
def blog():
    """Blog listing page."""
    db = get_db()
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    # Get total post count
    total = db.execute('SELECT COUNT(*) as count FROM BlogPost').fetchone()['count']
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get posts for current page
    blog_posts = db.execute(
        'SELECT * FROM BlogPost ORDER BY created_at DESC LIMIT ? OFFSET ?',
        (per_page, offset)
    ).fetchall()
    
    # Create pagination object
    pagination = Pagination(page, per_page, total)
    
    return render_template('blog.html', blog_posts=blog_posts, pagination=pagination)

@app.route('/blog/<slug>')
def blog_post(slug):
    """Display a single blog post."""
    db = get_db()
    
    # Get post by slug
    post = db.execute('SELECT * FROM BlogPost WHERE slug = ?', (slug,)).fetchone()
    
    if post is None:
        abort(404)
    
    # Get related posts
    related_posts = db.execute(
        'SELECT * FROM BlogPost WHERE id != ? ORDER BY created_at DESC LIMIT 2',
        (post['id'],)
    ).fetchall()
    
    return render_template('blog_post.html', post=post, related_posts=related_posts)

@app.route('/projects')
def projects():
    """Projects page."""
    db = get_db()
    all_projects_raw = db.execute('SELECT * FROM Project ORDER BY created_at DESC').fetchall()
    
    # Convert to dictionaries and add fields for template compatibility
    all_projects = []
    for project in all_projects_raw:
        project_dict = dict(project)
        # Map categories to technologies for template compatibility
        project_dict['technologies'] = project_dict.get('categories', '')
        # Map other field names for template compatibility
        project_dict['url'] = project_dict.get('live_link', '')
        project_dict['github_url'] = project_dict.get('github_link', '')
        all_projects.append(project_dict)
    
    # Get categories
    categories = db.execute(
        'SELECT DISTINCT category FROM Project WHERE category IS NOT NULL'
    ).fetchall()
    categories = [cat['category'] for cat in categories]
    categories.sort()
    
    return render_template('projects.html', projects=all_projects, categories=categories)

@app.route('/projects/<int:id>')
def project_detail(id):
    """Display a single project in full page."""
    db = get_db()
    
    # Get project by id
    project_raw = db.execute('SELECT * FROM Project WHERE id = ?', (id,)).fetchone()
    
    if project_raw is None:
        abort(404)
    
    # Convert to dictionary and add fields for template compatibility
    project = dict(project_raw)
    # Map categories to technologies for template compatibility
    project['technologies'] = project.get('categories', '')
    # Map other field names for template compatibility
    project['url'] = project.get('live_link', '')
    project['github_url'] = project.get('github_link', '')
    
    # Get other projects for related projects section
    related_projects_raw = db.execute(
        '''SELECT * FROM Project 
           WHERE id != ? AND (category = ? OR categories LIKE ?) 
           ORDER BY created_at DESC LIMIT 3''', 
        (project['id'], project['category'], f'%{project["categories"].split(",")[0] if project["categories"] else ""}%')
    ).fetchall()
    
    # Convert related projects for template compatibility
    related_projects = []
    for related in related_projects_raw:
        related_dict = dict(related)
        related_dict['technologies'] = related_dict.get('categories', '')
        related_dict['url'] = related_dict.get('live_link', '')
        related_dict['github_url'] = related_dict.get('github_link', '')
        related_projects.append(related_dict)
    
    return render_template('project_detail.html', project=project, related_projects=related_projects)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not all([name, email, subject, message]):
            flash('Please fill out all required fields.', 'warning')
            return redirect(url_for('contact'))
        
        db = get_db()
        db.execute(
            'INSERT INTO Contact (name, email, subject, message) VALUES (?, ?, ?, ?)',
            (name, email, subject, message)
        )
        db.commit()
        
        flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('index'))
    
    return render_template('contact.html')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        db = get_db()
        user = db.execute('SELECT * FROM User WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            
            if remember:
                # Session will last longer if remember is checked
                session.permanent = True
                
            return redirect(url_for('admin_dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@app.route('/auth/logout')
def logout():
    """Logout route."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/auth/reset-admin-password', methods=['GET', 'POST'])
def reset_admin_password():
    """Reset admin password."""
    if request.method == 'POST':
        username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, current_password, new_password, confirm_password]):
            flash('Please fill out all fields', 'warning')
            return redirect(url_for('reset_admin_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match!', 'danger')
            return redirect(url_for('reset_admin_password'))
        
        db = get_db()
        user = db.execute('SELECT * FROM User WHERE username = ?', (username,)).fetchone()
        
        if not user:
            flash('User not found!', 'danger')
            return redirect(url_for('reset_admin_password'))
        
        if not check_password_hash(user['password'], current_password):
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('reset_admin_password'))
        
        try:
            db.execute(
                'UPDATE User SET password = ? WHERE username = ?',
                (generate_password_hash(new_password), username)
            )
            db.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating password: {str(e)}', 'danger')
            return redirect(url_for('reset_admin_password'))
    
    return render_template('auth/reset_admin_password.html')

@app.route('/auth/create-admin', methods=['GET', 'POST'])
def create_admin():
    """Create a new admin user."""
    db = get_db()
    
    # Check if an admin already exists
    admin_exists = db.execute('SELECT COUNT(*) as count FROM User WHERE is_admin = 1').fetchone()['count'] > 0
    
    if admin_exists:
        flash('Admin user already exists! Please login first to create additional admin users.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, password, confirm_password]):
            flash('Please fill out all fields', 'warning')
            return redirect(url_for('create_admin'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('create_admin'))
        
        # Check if username exists
        if db.execute('SELECT id FROM User WHERE username = ?', (username,)).fetchone():
            flash('Username already exists!', 'danger')
            return redirect(url_for('create_admin'))
        
        # Create user
        db.execute(
            'INSERT INTO User (username, password, is_admin) VALUES (?, ?, 1)',
            (username, generate_password_hash(password))
        )
        db.commit()
        
        flash('Admin user created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/create_admin.html')

@app.route('/auth/add-admin', methods=['GET', 'POST'])
@admin_required
def add_admin():
    """Add additional admin users when logged in as admin."""
    db = get_db()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, password, confirm_password]):
            flash('All fields are required', 'warning')
            return redirect(url_for('add_admin'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('add_admin'))
        
        # Check if username exists
        if db.execute('SELECT id FROM User WHERE username = ?', (username,)).fetchone():
            flash('Username already exists!', 'danger')
            return redirect(url_for('add_admin'))
        
        # Create user
        db.execute(
            'INSERT INTO User (username, password, is_admin) VALUES (?, ?, 1)',
            (username, generate_password_hash(password))
        )
        db.commit()
        
        flash('New admin user created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('auth/add_admin.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    db = get_db()
    
    # Get counts for stats
    stats = {
        'about_count': db.execute('SELECT COUNT(*) as count FROM About').fetchone()['count'],
        'skills_count': db.execute('SELECT COUNT(*) as count FROM Skill').fetchone()['count'],
        'projects_count': db.execute('SELECT COUNT(*) as count FROM Project').fetchone()['count'],
        'achievements_count': db.execute('SELECT COUNT(*) as count FROM Achievement').fetchone()['count'],
        'education_count': db.execute('SELECT COUNT(*) as count FROM Education').fetchone()['count'],
        'blog_posts_count': db.execute('SELECT COUNT(*) as count FROM BlogPost').fetchone()['count'],
        'unread_messages': db.execute('SELECT COUNT(*) as count FROM Contact WHERE is_read = 0').fetchone()['count']
    }
    
    # Get recent messages
    recent_messages = db.execute(
        'SELECT * FROM Contact ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    
    return render_template('admin/dashboard.html', 
                          stats=stats, 
                          recent_messages=recent_messages,
                          unread_message_count=stats['unread_messages'])

# Admin routes for content management
@app.route('/admin/about', methods=['GET', 'POST'])
@admin_required
def admin_about():
    """Manage about content."""
    db = get_db()
    about = db.execute('SELECT * FROM about ORDER BY id DESC LIMIT 1').fetchone()
    
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content:
            flash('Content is required.', 'warning')
            return redirect(url_for('admin_about'))
            
        if about:
            # Update existing about content
            db.execute(
                'UPDATE about SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (content, about['id'])
            )
        else:
            # Create new about content
            db.execute(
                'INSERT INTO about (content) VALUES (?)',
                (content,)
            )
            
        db.commit()
        flash('About content updated successfully.', 'success')
        return redirect(url_for('admin_about'))
        
    return render_template('admin/about.html', about=about)

@app.route('/admin/skills')
@admin_required
def admin_skills():
    """List all skills."""
    db = get_db()
    skills = db.execute('SELECT * FROM Skill ORDER BY category, display_order').fetchall()
    return render_template('admin/skills.html', skills=skills)

@app.route('/admin/skills/add', methods=['GET', 'POST'])
@admin_required
def admin_add_skill():
    """Add a new skill."""
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        proficiency = request.form.get('proficiency')
        icon = request.form.get('icon')
        display_order = request.form.get('display_order', 0)
        
        if not all([name, category, proficiency]):
            flash('Name, category, and proficiency are required.', 'warning')
            return redirect(url_for('admin_add_skill'))
            
        db = get_db()
        db.execute(
            'INSERT INTO Skill (name, category, proficiency, icon, display_order) VALUES (?, ?, ?, ?, ?)',
            (name, category, proficiency, icon, display_order)
        )
        db.commit()
        
        flash('Skill added successfully.', 'success')
        return redirect(url_for('admin_skills'))
        
    return render_template('admin/skill_form.html')

@app.route('/admin/skills/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_skill(id):
    """Edit an existing skill."""
    db = get_db()
    skill = db.execute('SELECT * FROM Skill WHERE id = ?', (id,)).fetchone()
    
    if skill is None:
        flash('Skill not found.', 'danger')
        return redirect(url_for('admin_skills'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        proficiency = request.form.get('proficiency')
        icon = request.form.get('icon')
        display_order = request.form.get('display_order', 0)
        
        if not all([name, category, proficiency]):
            flash('Name, category, and proficiency are required.', 'warning')
            return redirect(url_for('admin_edit_skill', id=id))
            
        db.execute(
            '''UPDATE Skill 
               SET name = ?, category = ?, proficiency = ?, icon = ?, display_order = ?
               WHERE id = ?''',
            (name, category, proficiency, icon, display_order, id)
        )
        db.commit()
        
        flash('Skill updated successfully.', 'success')
        return redirect(url_for('admin_skills'))
        
    return render_template('admin/skill_form.html', skill=skill)

@app.route('/admin/skills/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_skill(id):
    """Delete a skill."""
    db = get_db()
    skill = db.execute('SELECT * FROM Skill WHERE id = ?', (id,)).fetchone()
    
    if skill is None:
        flash('Skill not found.', 'danger')
        return redirect(url_for('admin_skills'))
        
    db.execute('DELETE FROM Skill WHERE id = ?', (id,))
    db.commit()
    
    flash('Skill deleted successfully.', 'success')
    return redirect(url_for('admin_skills'))

@app.route('/admin/projects')
@admin_required
def admin_projects():
    """List all projects."""
    db = get_db()
    projects = db.execute('SELECT * FROM Project ORDER BY created_at DESC').fetchall()
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
@admin_required
def admin_add_project():
    """Add a new project."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image = request.form.get('image')
        url = request.form.get('url')
        github_url = request.form.get('github_url')
        technologies = request.form.get('technologies')
        featured = 1 if 'featured' in request.form else 0
        category = request.form.get('category')
        
        if not title:
            flash('Title is required.', 'warning')
            return redirect(url_for('admin_add_project'))
            
        db = get_db()
        db.execute(
            '''INSERT INTO Project 
               (title, description, image, github_link, live_link, categories, category, featured) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (title, description, image, github_url, url, technologies, category, featured)
        )
        db.commit()
        
        flash('Project added successfully.', 'success')
        return redirect(url_for('admin_projects'))
        
    return render_template('admin/project_form.html')

@app.route('/admin/projects/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_project(id):
    """Edit an existing project."""
    db = get_db()
    project = db.execute('SELECT * FROM Project WHERE id = ?', (id,)).fetchone()
    
    if project is None:
        flash('Project not found.', 'danger')
        return redirect(url_for('admin_projects'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image = request.form.get('image')
        url = request.form.get('url')
        github_url = request.form.get('github_url')
        technologies = request.form.get('technologies')
        featured = 1 if 'featured' in request.form else 0
        category = request.form.get('category')
        
        if not title:
            flash('Title is required.', 'warning')
            return redirect(url_for('admin_edit_project', id=id))
            
        db.execute(
            '''UPDATE Project 
               SET title = ?, description = ?, image = ?, github_link = ?, live_link = ?, categories = ?, featured = ?, category = ?
               WHERE id = ?''',
            (title, description, image, github_url, url, technologies, featured, category, id)
        )
        db.commit()
        
        flash('Project updated successfully.', 'success')
        return redirect(url_for('admin_projects'))
        
    return render_template('admin/project_form.html', project=project)

@app.route('/admin/projects/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_project(id):
    """Delete a project."""
    db = get_db()
    project = db.execute('SELECT * FROM Project WHERE id = ?', (id,)).fetchone()
    
    if project is None:
        flash('Project not found.', 'danger')
        return redirect(url_for('admin_projects'))
        
    db.execute('DELETE FROM Project WHERE id = ?', (id,))
    db.commit()
    
    flash('Project deleted successfully.', 'success')
    return redirect(url_for('admin_projects'))

@app.route('/admin/blog')
@admin_required
def admin_blog():
    """List all blog posts."""
    db = get_db()
    try:
        posts = db.execute('SELECT * FROM BlogPost ORDER BY created_at DESC').fetchall()
        
        # Convert posts to a list of dictionaries with properly formatted dates
        formatted_posts = []
        for post in posts:
            post_dict = dict(post)
            # Ensure updated_at is present
            if 'updated_at' not in post_dict or not post_dict['updated_at']:
                post_dict['updated_at'] = post_dict['created_at']
            formatted_posts.append(post_dict)
            
        return render_template('admin/blog.html', posts=formatted_posts)
    except Exception as e:
        flash(f'Error loading blog posts: {str(e)}', 'danger')
        return render_template('admin/blog.html', posts=[])

@app.route('/admin/blog/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_blog_post():
    """Add a new blog post."""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.form.get('image')
        certificate_pdf = request.form.get('certificate_pdf')
        
        if not title or not content:
            flash('Title and content are required!', 'warning')
            return redirect(url_for('admin_add_blog_post'))
        
        # Generate a slug from the title
        slug = title.lower().replace(' ', '-')
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO BlogPost (title, content, image, certificate_pdf, slug) VALUES (?, ?, ?, ?, ?)',
                (title, content, image, certificate_pdf, slug)
            )
            db.commit()
            
            flash('Blog post added successfully!', 'success')
            return redirect(url_for('admin_blog'))
        except Exception as e:
            db.rollback()
            flash(f'Error adding blog post: {str(e)}', 'danger')
            return redirect(url_for('admin_add_blog_post'))
    
    return render_template('admin/blog_form.html')

@app.route('/admin/blog/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_blog_post(id):
    """Edit an existing blog post."""
    db = get_db()
    cursor = db.cursor()
    
    # First check if the blog post exists
    cursor.execute('SELECT * FROM BlogPost WHERE id = ?', (id,))
    blog_post = cursor.fetchone()
    
    if blog_post is None:
        flash('Blog post not found.', 'danger')
        return redirect(url_for('admin_blog'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.form.get('image')
        certificate_pdf = request.form.get('certificate_pdf')
        
        if not title or not content:
            flash('Title and content are required!', 'warning')
            return redirect(url_for('admin_edit_blog_post', id=id))
        
        # Generate a slug from the title
        slug = title.lower().replace(' ', '-')
        
        try:
            cursor.execute(
                'UPDATE BlogPost SET title = ?, content = ?, image = ?, certificate_pdf = ?, slug = ? WHERE id = ?',
                (title, content, image, certificate_pdf, slug, id)
            )
            db.commit()
            
            flash('Blog post updated successfully!', 'success')
            return redirect(url_for('admin_blog'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating blog post: {str(e)}', 'danger')
            return redirect(url_for('admin_edit_blog_post', id=id))
    
    return render_template('admin/blog_form.html', blog_post=blog_post)

@app.route('/admin/blog/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_blog_post(id):
    """Delete a blog post."""
    db = get_db()
    blog_post = db.execute('SELECT * FROM BlogPost WHERE id = ?', (id,)).fetchone()
    
    if blog_post is None:
        flash('Blog post not found.', 'danger')
        return redirect(url_for('admin_blog'))
        
    db.execute('DELETE FROM BlogPost WHERE id = ?', (id,))
    db.commit()
    
    flash('Blog post deleted successfully.', 'success')
    return redirect(url_for('admin_blog'))

@app.route('/admin/achievements')
@admin_required
def admin_achievements():
    """List all achievements."""
    db = get_db()
    try:
        # Use a more specific query to avoid date parsing issues
        achievements = db.execute(
            '''SELECT id, title, description, image, certificate_pdf, 
                  strftime('%Y-%m-%d', date) as formatted_date 
               FROM Achievement ORDER BY date DESC'''
        ).fetchall()
        
        # Convert achievements to a list of dictionaries with properly formatted dates
        formatted_achievements = []
        for achievement in achievements:
            achievement_dict = dict(achievement)
            # Add a 'date' field with the properly formatted date
            achievement_dict['date'] = achievement_dict.get('formatted_date', '')
            formatted_achievements.append(achievement_dict)
            
        return render_template('admin/achievements.html', achievements=formatted_achievements)
    except Exception as e:
        flash(f'Error loading achievements: {str(e)}', 'danger')
        # Fallback to simpler query if there's an error
        achievements = db.execute('SELECT id, title, description, image, certificate_pdf FROM Achievement').fetchall()
        return render_template('admin/achievements.html', achievements=list(achievements))

@app.route('/admin/achievements/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_achievement():
    """Add a new achievement."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        image = request.form.get('image')
        certificate_pdf = request.form.get('certificate_pdf')
        
        if not title or not description:
            flash('Title and description are required!', 'warning')
            return redirect(url_for('admin_add_achievement'))
        
        date = None
        if date_str:
            try:
                # Ensure we're using the standard ISO format YYYY-MM-DD
                date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                flash('Invalid date format! Use YYYY-MM-DD format.', 'danger')
                return redirect(url_for('admin_add_achievement'))
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO Achievement (title, description, date, image, certificate_pdf) VALUES (?, ?, ?, ?, ?)',
                (title, description, date, image, certificate_pdf)
            )
            db.commit()
            
            flash('Achievement added successfully!', 'success')
            return redirect(url_for('admin_achievements'))
        except Exception as e:
            db.rollback()
            flash(f'Error adding achievement: {str(e)}', 'danger')
            return redirect(url_for('admin_add_achievement'))
    
    return render_template('admin/achievement_form.html')

@app.route('/admin/achievements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_achievement(id):
    """Edit an existing achievement."""
    db = get_db()
    cursor = db.cursor()
    
    # First check if the achievement exists
    cursor.execute(
        'SELECT id, title, description, strftime("%Y-%m-%d", date) as date, image, certificate_pdf FROM Achievement WHERE id = ?', 
        (id,)
    )
    achievement = cursor.fetchone()
    
    if achievement is None:
        flash('Achievement not found.', 'danger')
        return redirect(url_for('admin_achievements'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        image = request.form.get('image')
        certificate_pdf = request.form.get('certificate_pdf')
        
        if not title or not description:
            flash('Title and description are required!', 'warning')
            return redirect(url_for('admin_edit_achievement', id=id))
        
        date = None
        if date_str:
            try:
                # Ensure we're using the standard ISO format YYYY-MM-DD
                date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                flash('Invalid date format! Use YYYY-MM-DD format.', 'danger')
                return redirect(url_for('admin_edit_achievement', id=id))
        
        try:
            cursor.execute(
                'UPDATE Achievement SET title = ?, description = ?, date = ?, image = ?, certificate_pdf = ? WHERE id = ?',
                (title, description, date, image, certificate_pdf, id)
            )
            db.commit()
            
            flash('Achievement updated successfully!', 'success')
            return redirect(url_for('admin_achievements'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating achievement: {str(e)}', 'danger')
            return redirect(url_for('admin_edit_achievement', id=id))
    
    # No need for date processing anymore since we're getting it formatted directly from the database
    return render_template('admin/achievement_form.html', achievement=achievement)

@app.route('/admin/achievements/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_achievement(id):
    """Delete an achievement."""
    db = get_db()
    achievement = db.execute('SELECT * FROM Achievement WHERE id = ?', (id,)).fetchone()
    
    if achievement is None:
        flash('Achievement not found.', 'danger')
        return redirect(url_for('admin_achievements'))
        
    db.execute('DELETE FROM Achievement WHERE id = ?', (id,))
    db.commit()
    
    flash('Achievement deleted successfully.', 'success')
    return redirect(url_for('admin_achievements'))

@app.route('/admin/messages')
@admin_required
def admin_messages():
    """List all contact messages."""
    db = get_db()
    messages = db.execute('SELECT * FROM Contact ORDER BY created_at DESC').fetchall()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/messages/<int:id>/read', methods=['POST'])
@admin_required
def admin_mark_message_read(id):
    """Mark a message as read."""
    db = get_db()
    db.execute('UPDATE Contact SET is_read = 1 WHERE id = ?', (id,))
    db.commit()
    
    flash('Message marked as read.', 'success')
    return redirect(url_for('admin_messages'))

@app.route('/admin/logger')
@admin_required
def admin_logger():
    """View application logs."""
    from flask import request
    
    log_files = {
        'app.log': 'Application Logs',
        'gunicorn-access.log': 'Gunicorn Access Logs',
        'gunicorn-error.log': 'Gunicorn Error Logs'
    }
    
    selected_log = request.args.get('log', 'app.log')
    logs = []
    
    if selected_log in log_files:
        log_path = os.path.join('logs', selected_log)
        
        # Create the log file if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                f.write(f"Log file {selected_log} created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
        try:
            with open(log_path, 'r') as f:
                # Read last 1000 lines of logs
                lines = f.readlines()[-1000:]
                
                # Format logs based on the type
                if selected_log == 'gunicorn-access.log':
                    # Format: IP - - [timestamp] "METHOD /path HTTP/1.1" status_code size
                    logs = []
                    for line in lines:
                        try:
                            if ' - - [' in line and '" ' in line:
                                timestamp = line.split('[')[1].split(']')[0]
                                request = line.split('"')[1]
                                status = line.split('" ')[1].split(' ')[0]
                                logs.append(f"{timestamp} - {request} - Status: {status}")
                            else:
                                logs.append(line)
                        except IndexError:
                            logs.append(line)
                elif selected_log == 'gunicorn-error.log':
                    # Keep error logs as is, they're already well formatted
                    logs = lines
                else:
                    # Application logs
                    logs = lines
        except Exception as e:
            error_msg = f"Error reading log file: {str(e)}"
            logs = [error_msg]
    
    return render_template('admin/logger.html', 
                         logs=logs, 
                         log_files=log_files,
                         selected_log=selected_log)

# File upload routes
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/img/<path:subpath>/<path:filename>')
def serve_image(subpath, filename):
    """Serve static images with fallbacks for non-existent files."""
    full_path = os.path.join(app.static_folder, 'img', subpath, filename)
    
    if os.path.exists(full_path):
        return send_from_directory(os.path.join(app.static_folder, 'img', subpath), filename)
    else:
        # Return a fallback image based on the subpath
        if subpath == 'projects':
            return send_from_directory(os.path.join(app.static_folder, 'img'), 'project-placeholder.png')
        elif subpath == 'blog':
            return send_from_directory(os.path.join(app.static_folder, 'img'), 'blog-placeholder.png')
        elif subpath == 'achievements':
            return send_from_directory(os.path.join(app.static_folder, 'img'), 'achievement-placeholder.png')
        else:
            return send_from_directory(os.path.join(app.static_folder, 'img'), 'placeholder.png')

@app.route('/admin/upload', methods=['POST'])
@admin_required
def upload_file():
    """Handle file uploads for projects, blogs, etc."""
    if 'file' not in request.files:
        app.logger.warning('File upload attempted with no file')
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        app.logger.warning('File upload attempted with empty filename')
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        # Secure the filename and add a unique identifier to prevent overwrites
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        app.logger.info(f'File uploaded successfully: {unique_filename}')
        
        # Return the file path to be stored in the database
        relative_path = f"img/uploads/{unique_filename}"
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'filepath': relative_path,
            'url': url_for('uploaded_file', filename=unique_filename)
        })
    
    app.logger.warning(f'Invalid file type attempted: {file.filename}')
    return jsonify({'error': 'File type not allowed'}), 400

# Add a route to view a single achievement
@app.route('/achievement/<int:id>')
def view_achievement(id):
    """View a single achievement in its own page."""
    db = get_db()
    achievement = db.execute('SELECT * FROM Achievement WHERE id = ?', (id,)).fetchone()
    
    if achievement is None:
        flash('Achievement not found', 'danger')
        return redirect(url_for('index'))
    
    # Convert to dictionary to add properties
    achievement_dict = dict(achievement)
    
    # Format date if present
    if achievement_dict.get('date'):
        try:
            achievement_dict['date'] = datetime.strptime(achievement_dict['date'], '%Y-%m-%d')
        except (ValueError, TypeError):
            pass
    
    # Add special flag for competition wins (used for styling)
    if achievement_dict.get('achievement_type') == 'Competition' and ('1st' in achievement_dict.get('title', '') or 'Winner' in achievement_dict.get('title', '')):
        achievement_dict['is_winner'] = True
    else:
        achievement_dict['is_winner'] = False
        
    # Add special flag for certifications (used for styling)
    if achievement_dict.get('achievement_type') == 'Certification':
        achievement_dict['is_certification'] = True
    else:
        achievement_dict['is_certification'] = False
    
    return render_template('achievement_detail.html', achievement=achievement_dict)

# Add a route to serve PDF files for viewing in the browser
@app.route('/view-certificate/<path:filename>')
def view_certificate(filename):
    return send_from_directory(os.path.join('static', 'img', 'uploads'), filename)

def keep_alive():
    """Function to make recursive calls to keep the website alive."""
    # Get local IP address
    local_ip = get_local_ip()
    base_url = f"http://{local_ip}:5000"
    app.logger.info(f"Keep-alive service started, pinging {base_url}/alive every 15 minutes")
    
    while True:
        try:
            response = requests.get(f"{base_url}/alive")
            app.logger.info(f"Keep-alive ping successful: {response.status_code}")
        except Exception as e:
            app.logger.error(f"Keep-alive ping failed: {str(e)}")
        
        # Sleep for 15 minutes
        time.sleep(900)  # 900 seconds = 15 minutes

@app.route('/alive')
def alive():
    """Route to check if the website is alive."""
    app.logger.info("Alive check received")
    return jsonify({"status": "alive", "timestamp": datetime.now().isoformat()})

@app.route('/admin/seed-database', methods=['GET', 'POST'])
@login_required
def admin_seed_database():
    """Seed the database with data from portfolio_data.json."""
    if request.method == 'POST':
        try:
            # Get form data
            clear_existing = request.form.get('clear_existing') == 'on'
            
            # Load the JSON data
            json_path = 'portfolio_data.json'
            if not os.path.exists(json_path):
                flash(f"Error: {json_path} not found.", 'danger')
                return redirect(url_for('admin_seed_database'))
                
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            db = get_db()
            cursor = db.cursor()
            
            # Insert About data
            if 'about' in data and data['about']:
                if clear_existing:
                    cursor.execute('DELETE FROM About')
                cursor.execute(
                    'INSERT INTO About (content) VALUES (?)',
                    (data['about']['content'],)
                )
            
            # Insert Skills
            if 'skills' in data and data['skills']:
                if clear_existing:
                    cursor.execute('DELETE FROM Skill')
                for skill in data['skills']:
                    cursor.execute(
                        'INSERT INTO Skill (name, category, proficiency, icon, display_order) VALUES (?, ?, ?, ?, ?)',
                        (skill['name'], skill['category'], skill['proficiency'], skill['icon'], skill['display_order'])
                    )
            
            # Insert Projects
            if 'projects' in data and data['projects']:
                if clear_existing:
                    cursor.execute('DELETE FROM Project')
                for project in data['projects']:
                    cursor.execute(
                        '''INSERT INTO Project 
                           (title, description, image, github_link, live_link, categories, category, featured) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (project['title'], project['description'], project['image'], 
                         project.get('github_link', ''), project.get('live_link', ''), 
                         project.get('categories', ''), project.get('category', ''), 
                         project.get('featured', 0))
                    )
            
            # Check if Achievement table has linkedin_url column, if not add it
            cursor.execute("PRAGMA table_info(Achievement)")
            achievement_columns = [column[1] for column in cursor.fetchall()]
            
            if 'linkedin_url' not in achievement_columns:
                try:
                    cursor.execute('ALTER TABLE Achievement ADD COLUMN linkedin_url TEXT')
                except:
                    pass  # Column might already exist
            
            # Insert Achievements
            if 'achievements' in data and data['achievements']:
                if clear_existing:
                    cursor.execute('DELETE FROM Achievement')
                for achievement in data['achievements']:
                    cursor.execute(
                        'INSERT INTO Achievement (title, description, date, image, certificate_pdf, linkedin_url, event_type, achievement_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        (achievement['title'], achievement['description'], achievement['date'], 
                         achievement['image'], achievement['certificate_pdf'], achievement.get('linkedin_url', ''), '', 
                         achievement.get('achievement_type', 'Award'))
                    )
            
            # Insert Events
            if 'events' in data and data['events']:
                # Only clear if not already cleared by achievements
                if clear_existing and ('achievements' not in data or not data['achievements']):
                    cursor.execute('DELETE FROM Achievement')
                for event in data['events']:
                    cursor.execute(
                        'INSERT INTO Achievement (title, description, date, image, certificate_pdf, linkedin_url, event_type, achievement_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        (event['title'], event['description'], event['date'], 
                         event['image'], event['certificate_pdf'], event.get('linkedin_url', ''), event.get('event_type', 'Attended'), '')
                    )
            
            # Insert Education
            if 'education' in data and data['education']:
                if clear_existing:
                    cursor.execute('DELETE FROM Education')
                for education in data['education']:
                    cursor.execute(
                        '''INSERT INTO Education 
                           (institution, degree, field, start_date, end_date, description) 
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (education['institution'], education['degree'], education['field'],
                         education['start_date'], education.get('end_date'), education['description'])
                    )
            
            # Insert Blog Posts
            if 'blog_posts' in data and data['blog_posts']:
                if clear_existing:
                    cursor.execute('DELETE FROM BlogPost')
                for post in data['blog_posts']:
                    cursor.execute(
                        '''INSERT INTO BlogPost 
                           (title, content, image, certificate_pdf, created_at, updated_at, slug) 
                           VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), ?)''',
                        (post['title'], post['content'], post.get('image', ''), 
                         post.get('certificate_pdf'), post['slug'])
                    )
            
            # Insert Contacts
            if 'contacts' in data and data['contacts']:
                if clear_existing:
                    cursor.execute('DELETE FROM Contact')
                for contact in data['contacts']:
                    cursor.execute(
                        'INSERT INTO Contact (name, email, subject, message, created_at, is_read) VALUES (?, ?, ?, ?, datetime("now"), ?)',
                        (contact['name'], contact['email'], contact['subject'], 
                         contact['message'], contact.get('is_read', 0))
                    )
            
            # Insert User if not exists
            if 'user' in data and data['user']:
                existing_user = cursor.execute(
                    'SELECT id FROM User WHERE username = ?', 
                    (data['user']['username'],)
                ).fetchone()
                
                if not existing_user:
                    # Hash the password before storing it
                    hashed_password = generate_password_hash(data['user']['password'])
                    cursor.execute(
                        'INSERT INTO User (username, password, is_admin) VALUES (?, ?, ?)',
                        (data['user']['username'], hashed_password, data['user']['is_admin'])
                    )
            
            db.commit()
            flash('Database seeded successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            flash(f'Error seeding database: {str(e)}', 'danger')
            return redirect(url_for('admin_seed_database'))
    
    return render_template('admin/seed_database.html')

@app.route('/admin/education')
@admin_required
def admin_education():
    """List all education entries."""
    db = get_db()
    education_entries = db.execute('SELECT * FROM Education ORDER BY start_date DESC').fetchall()
    return render_template('admin/education.html', education_entries=education_entries)

@app.route('/admin/education/add', methods=['GET', 'POST'])
@admin_required
def admin_add_education():
    """Add a new education entry."""
    if request.method == 'POST':
        institution = request.form.get('institution')
        degree = request.form.get('degree')
        field = request.form.get('field')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date', '')  # Optional
        description = request.form.get('description', '')  # Optional
        
        if not all([institution, degree, field, start_date]):
            flash('Institution, degree, field, and start date are required.', 'warning')
            return redirect(url_for('admin_add_education'))
            
        db = get_db()
        db.execute(
            'INSERT INTO Education (institution, degree, field, start_date, end_date, description) VALUES (?, ?, ?, ?, ?, ?)',
            (institution, degree, field, start_date, end_date, description)
        )
        db.commit()
        
        flash('Education entry added successfully.', 'success')
        return redirect(url_for('admin_education'))
        
    return render_template('admin/education_form.html')

@app.route('/admin/education/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_education(id):
    """Edit an existing education entry."""
    db = get_db()
    education = db.execute('SELECT * FROM Education WHERE id = ?', (id,)).fetchone()
    
    if education is None:
        flash('Education entry not found.', 'danger')
        return redirect(url_for('admin_education'))
    
    if request.method == 'POST':
        institution = request.form.get('institution')
        degree = request.form.get('degree')
        field = request.form.get('field')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date', '')  # Optional
        description = request.form.get('description', '')  # Optional
        
        if not all([institution, degree, field, start_date]):
            flash('Institution, degree, field, and start date are required.', 'warning')
            return redirect(url_for('admin_edit_education', id=id))
            
        db.execute(
            '''UPDATE Education 
               SET institution = ?, degree = ?, field = ?, start_date = ?, end_date = ?, description = ?
               WHERE id = ?''',
            (institution, degree, field, start_date, end_date, description, id)
        )
        db.commit()
        
        flash('Education entry updated successfully.', 'success')
        return redirect(url_for('admin_education'))
        
    return render_template('admin/education_form.html', education=education)

@app.route('/admin/education/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_education(id):
    """Delete an education entry."""
    db = get_db()
    education = db.execute('SELECT * FROM Education WHERE id = ?', (id,)).fetchone()
    
    if education is None:
        flash('Education entry not found.', 'danger')
        return redirect(url_for('admin_education'))
        
    db.execute('DELETE FROM Education WHERE id = ?', (id,))
    db.commit()
    
    flash('Education entry deleted successfully.', 'success')
    return redirect(url_for('admin_education'))

@app.route('/admin/export-data')
@admin_required
def admin_export_data():
    """Export portfolio data as JSON file."""
    db = get_db()
    
    # Build the complete portfolio data dictionary
    portfolio_data = {}
    
    # Get about data
    about = db.execute('SELECT * FROM About ORDER BY id DESC LIMIT 1').fetchone()
    if about:
        portfolio_data['about'] = {
            'content': about['content']
        }
    
    # Get skills data
    skills = db.execute('SELECT * FROM Skill ORDER BY display_order').fetchall()
    portfolio_data['skills'] = []
    for skill in skills:
        portfolio_data['skills'].append({
            'name': skill['name'],
            'category': skill['category'],
            'proficiency': skill['proficiency'],
            'icon': skill['icon'],
            'display_order': skill['display_order']
        })
    
    # Get projects data
    projects = db.execute('SELECT * FROM Project ORDER BY created_at DESC').fetchall()
    portfolio_data['projects'] = []
    for project in projects:
        portfolio_data['projects'].append({
            'title': project['title'],
            'description': project['description'],
            'image': project['image'],
            'github_link': project['github_link'],
            'live_link': project['live_link'],
            'categories': project['categories'],
            'featured': project['featured'] == 1
        })
    
    # Get achievements data
    achievements = db.execute('SELECT * FROM Achievement ORDER BY date DESC').fetchall()
    portfolio_data['achievements'] = []
    for achievement in achievements:
        portfolio_data['achievements'].append({
            'title': achievement['title'],
            'description': achievement['description'],
            'date': achievement['date'].isoformat() if achievement['date'] else None,
            'image': achievement['image'],
            'certificate_pdf': achievement['certificate_pdf'],
            'linkedin_url': achievement['linkedin_url']
        })
    
    # Get education data
    education_items = db.execute('SELECT * FROM Education ORDER BY start_date DESC').fetchall()
    portfolio_data['education'] = []
    for edu in education_items:
        portfolio_data['education'].append({
            'institution': edu['institution'],
            'degree': edu['degree'],
            'field': edu['field'],
            'description': edu['description'],
            'start_date': edu['start_date'].isoformat() if edu['start_date'] else None,
            'end_date': edu['end_date'].isoformat() if edu['end_date'] else None
        })
    
    # Get blog posts data
    blog_posts = db.execute('SELECT * FROM BlogPost ORDER BY created_at DESC').fetchall()
    portfolio_data['blog_posts'] = []
    for post in blog_posts:
        portfolio_data['blog_posts'].append({
            'title': post['title'],
            'slug': post['slug'],
            'content': post['content'],
            'image': post['image'],
            'created_at': post['created_at'].isoformat() if post['created_at'] else None
        })
    
    # Create response with JSON data
    response = jsonify(portfolio_data)
    response.headers.set('Content-Disposition', 'attachment', filename='portfolio_data.json')
    return response

@app.route('/admin/download-log/<filename>')
@admin_required
def admin_download_log(filename):
    """Download a log file."""
    log_files = ['app.log', 'gunicorn-access.log', 'gunicorn-error.log']
    
    if filename not in log_files:
        flash('Invalid log file requested.', 'danger')
        return redirect(url_for('admin_logger'))
    
    log_path = os.path.join('logs', filename)
    if not os.path.exists(log_path):
        flash(f'Log file {filename} does not exist.', 'danger')
        return redirect(url_for('admin_logger'))
    
    return send_from_directory('logs', filename, as_attachment=True)

@app.route('/admin/download-database')
@admin_required
def admin_download_database():
    """Download the database file for backup."""
    # Create a copy of the database to avoid locking issues
    db_path = app.config['DATABASE']
    backup_path = os.path.join('instance', 'portfolio_backup.db')
    
    try:
        # Close the database connection
        if 'db' in g:
            g.db.close()
            g.pop('db', None)
        
        # Copy the database file
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        
        # Set the response headers
        response = send_from_directory('instance', 'portfolio_backup.db', as_attachment=True)
        response.headers['Content-Disposition'] = f'attachment; filename=portfolio_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        
        return response
    except Exception as e:
        flash(f'Error creating database backup: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/download-all-logs')
@admin_required
def admin_download_all_logs():
    """Download all log files as a zip archive."""
    # Create a BytesIO object to store the zip file
    memory_file = BytesIO()
    
    # Define the log files to include
    log_files = ['app.log', 'gunicorn-access.log', 'gunicorn-error.log']
    
    # Create a zip file
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for log_file in log_files:
            log_path = os.path.join('logs', log_file)
            if os.path.exists(log_path):
                # Add the file to the zip
                zf.write(log_path, arcname=log_file)
    
    # Reset the file pointer
    memory_file.seek(0)
    
    # Set the response headers
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response = app.response_class(
        memory_file.getvalue(),
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment;filename=all_logs_{timestamp}.zip'}
    )
    
    return response

# Start the keep-alive thread when the application starts
if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        create_tables()
        
    # Create log directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create empty log files if they don't exist
    log_files = ['app.log', 'gunicorn-access.log', 'gunicorn-error.log']
    for log_file in log_files:
        log_path = os.path.join('logs', log_file)
        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                f.write(f"Log file created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Start the keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True) 