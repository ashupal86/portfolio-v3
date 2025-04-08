# This file marks the models directory as a Python package 

# Import the models
from datetime import datetime
from flask_login import UserMixin
from slugify import slugify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

# This function will be called by create_app
def init_models(db):
    """Initialize models with SQLAlchemy db instance."""
    
    class User(db.Model, UserMixin):
        """User model for authentication."""
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(64), unique=True, index=True)
        email = db.Column(db.String(120), unique=True, index=True)
        password_hash = db.Column(db.String(256))
        is_admin = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def set_password(self, password):
            """Hash and set the user password."""
            self.password_hash = generate_password_hash(password)
            
        def check_password(self, password):
            """Check if the provided password matches the hashed password."""
            return check_password_hash(self.password_hash, password)
        
        def __repr__(self):
            return f'<User {self.username}>'

    class About(db.Model):
        """About section content."""
        __tablename__ = 'about'
        
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.Text)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f'<About {self.id}>'

    class Skill(db.Model):
        """User skills with categories and proficiency levels."""
        __tablename__ = 'skills'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64))
        category = db.Column(db.String(64))
        proficiency = db.Column(db.Integer)  # 0-100
        icon = db.Column(db.String(128))
        display_order = db.Column(db.Integer, default=0)
        
        def __repr__(self):
            return f'<Skill {self.name}>'

    class Project(db.Model):
        """Portfolio projects."""
        __tablename__ = 'projects'
        
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(128))
        description = db.Column(db.Text)
        image = db.Column(db.String(256))
        url = db.Column(db.String(256))
        github_url = db.Column(db.String(256))
        technologies = db.Column(db.String(256))
        featured = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Project {self.title}>'

    class Achievement(db.Model):
        """Professional achievements and certifications."""
        __tablename__ = 'achievements'
        
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(128))
        description = db.Column(db.Text)
        date = db.Column(db.DateTime)
        image = db.Column(db.String(256))
        
        def __repr__(self):
            return f'<Achievement {self.title}>'

    class Education(db.Model):
        """Educational background."""
        __tablename__ = 'education'
        
        id = db.Column(db.Integer, primary_key=True)
        institution = db.Column(db.String(128))
        degree = db.Column(db.String(128))
        field = db.Column(db.String(128))
        start_date = db.Column(db.DateTime)
        end_date = db.Column(db.DateTime)
        description = db.Column(db.Text)
        
        def __repr__(self):
            return f'<Education {self.institution} - {self.degree}>'

    class BlogPost(db.Model):
        """Blog posts."""
        __tablename__ = 'blog_posts'
        
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(128))
        slug = db.Column(db.String(128), unique=True, index=True)
        content = db.Column(db.Text)
        image = db.Column(db.String(256))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __init__(self, **kwargs):
            super(BlogPost, self).__init__(**kwargs)
            if self.title and not self.slug:
                self.slug = slugify(self.title)
        
        def __repr__(self):
            return f'<BlogPost {self.title}>'

    class Contact(db.Model):
        """Contact form submissions."""
        __tablename__ = 'contacts'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(64))
        email = db.Column(db.String(120))
        subject = db.Column(db.String(128))
        message = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_read = db.Column(db.Boolean, default=False)
        
        def __repr__(self):
            return f'<Contact {self.name} - {self.email}>'
    
    # Return all models
    return {
        'User': User,
        'About': About,
        'Skill': Skill,
        'Project': Project,
        'Achievement': Achievement,
        'Education': Education,
        'BlogPost': BlogPost,
        'Contact': Contact
    } 