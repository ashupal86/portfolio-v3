import sqlite3
import os
import shutil
from datetime import datetime

def migrate_db():
    """Migrate data from old table structure to new table structure."""
    print("Starting database migration...")
    
    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)
    
    # Backup existing database
    db_path = os.path.join('instance', 'portfolio.db')
    backup_path = os.path.join('instance', 'portfolio_backup.db')
    
    if os.path.exists(db_path):
        print(f"Creating backup of existing database to {backup_path}")
        shutil.copy2(db_path, backup_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Define table mappings (old_name -> new_name)
    table_mappings = {
        'users': 'User',
        'about': 'About',
        'skills': 'Skill',
        'projects': 'Project',
        'achievements': 'Achievement',
        'education': 'Education',
        'blog_posts': 'BlogPost',
        'contacts': 'Contact'
    }
    
    # Check which tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    # Create schema for new tables
    print("Creating schema for new tables...")
    schema = """
    -- User table
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    );
    
    -- About table
    CREATE TABLE IF NOT EXISTS About (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL
    );
    
    -- Skill table
    CREATE TABLE IF NOT EXISTS Skill (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        proficiency INTEGER NOT NULL
    );
    
    -- Project table
    CREATE TABLE IF NOT EXISTS Project (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        image TEXT,
        github_link TEXT,
        live_link TEXT,
        categories TEXT
    );
    
    -- Achievement table
    CREATE TABLE IF NOT EXISTS Achievement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        date DATE,
        image TEXT,
        certificate_pdf TEXT
    );
    
    -- Education table
    CREATE TABLE IF NOT EXISTS Education (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institution TEXT NOT NULL,
        degree TEXT NOT NULL,
        field TEXT NOT NULL,
        start_date DATE,
        end_date DATE,
        description TEXT
    );
    
    -- BlogPost table
    CREATE TABLE IF NOT EXISTS BlogPost (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        image TEXT,
        certificate_pdf TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        slug TEXT UNIQUE
    );
    
    -- Contact table
    CREATE TABLE IF NOT EXISTS Contact (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0
    );
    """
    cursor.executescript(schema)
    
    # Migrate data from old tables to new tables
    print("Migrating data...")
    
    # Migrate users to User
    if 'users' in existing_tables:
        print("Migrating users table...")
        try:
            cursor.execute("SELECT id, username, password_hash, is_admin FROM users")
            users = cursor.fetchall()
            
            for user in users:
                cursor.execute(
                    "INSERT OR IGNORE INTO User (id, username, password, is_admin) VALUES (?, ?, ?, ?)",
                    (user['id'], user['username'], user['password_hash'], user['is_admin'])
                )
            print(f"Migrated {len(users)} users")
        except sqlite3.Error as e:
            print(f"Error migrating users: {e}")
    
    # Migrate about to About
    if 'about' in existing_tables:
        print("Migrating about table...")
        try:
            cursor.execute("SELECT id, content FROM about")
            about_items = cursor.fetchall()
            
            for item in about_items:
                cursor.execute(
                    "INSERT OR IGNORE INTO About (id, content) VALUES (?, ?)",
                    (item['id'], item['content'])
                )
            print(f"Migrated {len(about_items)} about items")
        except sqlite3.Error as e:
            print(f"Error migrating about: {e}")
    
    # Migrate skills to Skill
    if 'skills' in existing_tables:
        print("Migrating skills table...")
        try:
            cursor.execute("SELECT id, name, category, proficiency FROM skills")
            skills = cursor.fetchall()
            
            for skill in skills:
                cursor.execute(
                    "INSERT OR IGNORE INTO Skill (id, name, category, proficiency) VALUES (?, ?, ?, ?)",
                    (skill['id'], skill['name'], skill['category'], skill['proficiency'])
                )
            print(f"Migrated {len(skills)} skills")
        except sqlite3.Error as e:
            print(f"Error migrating skills: {e}")
    
    # Migrate projects to Project
    if 'projects' in existing_tables:
        print("Migrating projects table...")
        try:
            cursor.execute("SELECT id, title, description, image, github_url, url, technologies FROM projects")
            projects = cursor.fetchall()
            
            for project in projects:
                # Rename fields to match new structure
                cursor.execute(
                    "INSERT OR IGNORE INTO Project (id, title, description, image, github_link, live_link, categories) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (project['id'], project['title'], project['description'], project['image'], 
                     project['github_url'], project['url'], project['technologies'])
                )
            print(f"Migrated {len(projects)} projects")
        except sqlite3.Error as e:
            print(f"Error migrating projects: {e}")
    
    # Migrate achievements to Achievement
    if 'achievements' in existing_tables:
        print("Migrating achievements table...")
        try:
            cursor.execute("SELECT id, title, description, date, image FROM achievements")
            achievements = cursor.fetchall()
            
            for achievement in achievements:
                cursor.execute(
                    "INSERT OR IGNORE INTO Achievement (id, title, description, date, image) VALUES (?, ?, ?, ?, ?)",
                    (achievement['id'], achievement['title'], achievement['description'], 
                     achievement['date'], achievement['image'])
                )
            print(f"Migrated {len(achievements)} achievements")
        except sqlite3.Error as e:
            print(f"Error migrating achievements: {e}")
    
    # Migrate education to Education
    if 'education' in existing_tables:
        print("Migrating education table...")
        try:
            cursor.execute("SELECT id, institution, degree, field, start_date, end_date, description FROM education")
            education_items = cursor.fetchall()
            
            for item in education_items:
                cursor.execute(
                    "INSERT OR IGNORE INTO Education (id, institution, degree, field, start_date, end_date, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (item['id'], item['institution'], item['degree'], item['field'], 
                     item['start_date'], item['end_date'], item['description'])
                )
            print(f"Migrated {len(education_items)} education items")
        except sqlite3.Error as e:
            print(f"Error migrating education: {e}")
    
    # Migrate blog_posts to BlogPost
    if 'blog_posts' in existing_tables:
        print("Migrating blog_posts table...")
        try:
            cursor.execute("SELECT id, title, content, image, slug, created_at FROM blog_posts")
            blog_posts = cursor.fetchall()
            
            for post in blog_posts:
                cursor.execute(
                    "INSERT OR IGNORE INTO BlogPost (id, title, content, image, slug, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (post['id'], post['title'], post['content'], post['image'], post['slug'], post['created_at'])
                )
            print(f"Migrated {len(blog_posts)} blog posts")
        except sqlite3.Error as e:
            print(f"Error migrating blog_posts: {e}")
    
    # Migrate contacts to Contact
    if 'contacts' in existing_tables:
        print("Migrating contacts table...")
        try:
            cursor.execute("SELECT id, name, email, subject, message, created_at, is_read FROM contacts")
            contacts = cursor.fetchall()
            
            for contact in contacts:
                cursor.execute(
                    "INSERT OR IGNORE INTO Contact (id, name, email, subject, message, created_at, is_read) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (contact['id'], contact['name'], contact['email'], contact['subject'], 
                     contact['message'], contact['created_at'], contact['is_read'])
                )
            print(f"Migrated {len(contacts)} contacts")
        except sqlite3.Error as e:
            print(f"Error migrating contacts: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Database migration completed successfully!")

def clean_up_old_tables():
    """Drop old tables after successful migration."""
    print("Cleaning up old tables...")
    
    # Connect to database
    conn = sqlite3.connect(os.path.join('instance', 'portfolio.db'))
    cursor = conn.cursor()
    
    # Old table names to be dropped
    old_tables = ['users', 'about', 'skills', 'projects', 'achievements', 'education', 'blog_posts', 'contacts']
    
    # Check which tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    # Drop old tables if they exist
    for table in old_tables:
        if table in existing_tables:
            try:
                cursor.execute(f"DROP TABLE {table}")
                print(f"Dropped table: {table}")
            except sqlite3.Error as e:
                print(f"Error dropping table {table}: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Clean up completed!")

if __name__ == "__main__":
    # Migrate data from old to new tables
    migrate_db()
    
    # Remove old tables after successful migration
    clean_up_old_tables()
    
    print("All done! Database has been migrated successfully, and old tables have been removed.") 