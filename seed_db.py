import os
import json
import sqlite3
import uuid
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join('instance', 'portfolio.db')

def get_db():
    """Connect to the database and return a connection object."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables."""
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
        certificate_pdf TEXT,
        linkedin_url TEXT,
        event_type TEXT,
        achievement_type TEXT
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
    print("Database tables created successfully.")

def clean_old_db_files():
    """Clean up old database files."""
    print("Cleaning up old database files...")
    
    # Ensure the instance directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Remove all .db files in instance directory except portfolio.db
    for file in os.listdir(os.path.dirname(DB_PATH)):
        if file.endswith('.db') and file != os.path.basename(DB_PATH):
            file_path = os.path.join(os.path.dirname(DB_PATH), file)
            try:
                os.remove(file_path)
                print(f"Removed old database file: {file}")
            except Exception as e:
                print(f"Error removing {file}: {str(e)}")

def seed_database():
    """Seed the database with data from portfolio_data.json."""
    try:
        # Load the JSON data
        json_path = 'portfolio_data.json'
        if not os.path.exists(json_path):
            print(f"Error: {json_path} not found.")
            return
            
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print("Loading data from portfolio_data.json...")
        
        db = get_db()
        cursor = db.cursor()
        
        # Insert About data
        if 'about' in data and data['about']:
            cursor.execute('DELETE FROM About')
            cursor.execute(
                'INSERT INTO About (content) VALUES (?)',
                (data['about']['content'],)
            )
            print("About data loaded.")
        
        # Insert Skills
        if 'skills' in data and data['skills']:
            cursor.execute('DELETE FROM Skill')
            for skill in data['skills']:
                cursor.execute(
                    'INSERT INTO Skill (name, category, proficiency, icon, display_order) VALUES (?, ?, ?, ?, ?)',
                    (skill['name'], skill['category'], skill['proficiency'], skill['icon'], skill['display_order'])
                )
            print(f"Loaded {len(data['skills'])} skills.")
        
        # Insert Projects
        if 'projects' in data and data['projects']:
            cursor.execute('DELETE FROM Project')
            for project in data['projects']:
                cursor.execute(
                    '''INSERT INTO Project 
                       (title, description, image, github_link, live_link, categories, category, featured) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (project['title'], project['description'], project['image'], 
                     project.get('github_link', ''), project.get('live_link', ''), project.get('categories', ''), 
                     project.get('category', ''), project.get('featured', 0))
                )
            print(f"Loaded {len(data['projects'])} projects.")
        
        # Check if Achievement table has linkedin_url column, if not add it
        cursor.execute("PRAGMA table_info(Achievement)")
        achievement_columns = [column[1] for column in cursor.fetchall()]
        
        if 'linkedin_url' not in achievement_columns:
            print("Adding linkedin_url column to Achievement table...")
            cursor.execute('ALTER TABLE Achievement ADD COLUMN linkedin_url TEXT')
        
        # Insert Achievements
        if 'achievements' in data and data['achievements']:
            cursor.execute('DELETE FROM Achievement')
            for achievement in data['achievements']:
                cursor.execute(
                    'INSERT INTO Achievement (title, description, date, image, certificate_pdf, linkedin_url, achievement_type) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (achievement['title'], achievement['description'], achievement['date'], 
                     achievement['image'], achievement['certificate_pdf'], achievement.get('linkedin_url', ''),
                     achievement.get('achievement_type', 'Award'))
                )
            print(f"Loaded {len(data['achievements'])} achievements.")
        
        # Insert Events
        if 'events' in data and data['events']:
            # Only clear if not already cleared by achievements
            if 'achievements' not in data or not data['achievements']:
                cursor.execute('DELETE FROM Achievement')
            for event in data['events']:
                cursor.execute(
                    'INSERT INTO Achievement (title, description, date, image, certificate_pdf, linkedin_url, event_type, achievement_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (event['title'], event['description'], event['date'], 
                     event['image'], event.get('certificate_pdf'), event.get('linkedin_url', ''), 
                     event.get('event_type', 'Attended'), event.get('achievement_type', ''))
                )
            print(f"Loaded {len(data['events'])} events.")
        
        # Insert Education
        if 'education' in data and data['education']:
            cursor.execute('DELETE FROM Education')
            for education in data['education']:
                cursor.execute(
                    '''INSERT INTO Education 
                       (institution, degree, field, start_date, end_date, description) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (education['institution'], education['degree'], education['field'],
                     education['start_date'], education.get('end_date'), education['description'])
                )
            print(f"Loaded {len(data['education'])} education entries.")
        
        # Insert Blog Posts
        if 'blog_posts' in data and data['blog_posts']:
            cursor.execute('DELETE FROM BlogPost')
            for post in data['blog_posts']:
                # Generate created_at and updated_at timestamps
                now = 'datetime("now")'
                cursor.execute(
                    '''INSERT INTO BlogPost 
                       (title, content, image, certificate_pdf, created_at, updated_at, slug) 
                       VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), ?)''',
                    (post['title'], post['content'], post.get('image', ''), post.get('certificate_pdf'), post['slug'])
                )
            print(f"Loaded {len(data['blog_posts'])} blog posts.")
        
        # Insert Contacts
        if 'contacts' in data and data['contacts']:
            cursor.execute('DELETE FROM Contact')
            for contact in data['contacts']:
                cursor.execute(
                    'INSERT INTO Contact (name, email, subject, message, created_at, is_read) VALUES (?, ?, ?, ?, datetime("now"), ?)',
                    (contact['name'], contact['email'], contact['subject'], contact['message'], contact.get('is_read', 0))
                )
            print(f"Loaded {len(data['contacts'])} contact messages.")
        
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
                print("Admin user created.")
            else:
                print("Admin user already exists.")
        
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        raise e

if __name__ == "__main__":
    clean_old_db_files()
    init_db()
    seed_database() 