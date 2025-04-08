from datetime import datetime
from flask_login import UserMixin
from slugify import slugify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from typing import Optional, List

# This will be populated by the create_app function
db = None

class Base(DeclarativeBase):
    pass

class User(UserMixin):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(sa.String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(sa.String(256))
    is_admin: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
    
    def set_password(self, password: str) -> None:
        """Hash and set the user password."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'


class About:
    """About section content."""
    __tablename__ = 'about'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(sa.Text)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<About {self.id}>'


class Skill:
    """User skills with categories and proficiency levels."""
    __tablename__ = 'skills'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(64))
    category: Mapped[str] = mapped_column(sa.String(64))
    proficiency: Mapped[int] = mapped_column(sa.Integer)  # 0-100
    icon: Mapped[Optional[str]] = mapped_column(sa.String(128))
    display_order: Mapped[int] = mapped_column(sa.Integer, default=0)
    
    def __repr__(self) -> str:
        return f'<Skill {self.name}>'


class Project:
    """Portfolio projects."""
    __tablename__ = 'projects'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(128))
    description: Mapped[str] = mapped_column(sa.Text)
    image: Mapped[Optional[str]] = mapped_column(sa.String(256))
    url: Mapped[Optional[str]] = mapped_column(sa.String(256))
    github_url: Mapped[Optional[str]] = mapped_column(sa.String(256))
    technologies: Mapped[str] = mapped_column(sa.String(256))
    featured: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<Project {self.title}>'


class Achievement:
    """Professional achievements and certifications."""
    __tablename__ = 'achievements'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(128))
    description: Mapped[str] = mapped_column(sa.Text)
    date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime)
    image: Mapped[Optional[str]] = mapped_column(sa.String(256))
    
    def __repr__(self) -> str:
        return f'<Achievement {self.title}>'


class Education:
    """Educational background."""
    __tablename__ = 'education'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    institution: Mapped[str] = mapped_column(sa.String(128))
    degree: Mapped[str] = mapped_column(sa.String(128))
    field: Mapped[str] = mapped_column(sa.String(128))
    start_date: Mapped[datetime] = mapped_column(sa.DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime)
    description: Mapped[Optional[str]] = mapped_column(sa.Text)
    
    def __repr__(self) -> str:
        return f'<Education {self.institution} - {self.degree}>'


class BlogPost:
    """Blog posts."""
    __tablename__ = 'blog_posts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(128))
    slug: Mapped[str] = mapped_column(sa.String(128), unique=True, index=True)
    content: Mapped[str] = mapped_column(sa.Text)
    image: Mapped[Optional[str]] = mapped_column(sa.String(256))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(BlogPost, self).__init__(**kwargs)
        if self.title and not self.slug:
            self.slug = slugify(self.title)
    
    def __repr__(self) -> str:
        return f'<BlogPost {self.title}>'


class Contact:
    """Contact form submissions."""
    __tablename__ = 'contacts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(64))
    email: Mapped[str] = mapped_column(sa.String(120))
    subject: Mapped[str] = mapped_column(sa.String(128))
    message: Mapped[str] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
    is_read: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    
    def __repr__(self) -> str:
        return f'<Contact {self.name} - {self.email}>' 