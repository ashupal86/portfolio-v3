from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app import db
import models
from datetime import datetime

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    """Main portfolio page with all sections."""
    # Get about content
    about = db.session.query(models.About).first()
    
    # Get skills grouped by category
    skills_by_category = {}
    skills = db.session.query(models.Skill).order_by(models.Skill.display_order).all()
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    # Get featured projects
    featured_projects = db.session.query(models.Project).filter_by(featured=True).all()
    
    # Get other projects
    other_projects = db.session.query(models.Project).filter_by(featured=False).all()
    
    # Get achievements
    achievements = db.session.query(models.Achievement).order_by(models.Achievement.date.desc()).all()
    
    # Get education
    education = db.session.query(models.Education).order_by(models.Education.start_date.desc()).all()
    
    # Get latest blog posts
    blog_posts = db.session.query(models.BlogPost).order_by(models.BlogPost.created_at.desc()).limit(3).all()
    
    return render_template('index.html',
                          about=about,
                          skills_by_category=skills_by_category,
                          featured_projects=featured_projects,
                          other_projects=other_projects,
                          achievements=achievements,
                          education=education,
                          blog_posts=blog_posts)

@main_bp.route('/blog')
def blog():
    """Blog listing page."""
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Number of posts per page
    
    # Get paginated blog posts
    pagination = db.session.query(models.BlogPost).order_by(
        models.BlogPost.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    posts = pagination.items
    
    return render_template('blog.html', posts=posts, pagination=pagination)

@main_bp.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post page."""
    post = db.session.query(models.BlogPost).filter_by(slug=slug).first_or_404()
    
    # Get related posts (simple implementation - can be improved)
    related_posts = db.session.query(models.BlogPost).filter(
        models.BlogPost.id != post.id
    ).order_by(models.BlogPost.created_at.desc()).limit(3).all()
    
    return render_template('blog_post.html', post=post, related_posts=related_posts)

@main_bp.route('/projects')
def projects():
    """Projects listing page."""
    # Get all projects
    all_projects = db.session.query(models.Project).order_by(models.Project.created_at.desc()).all()
    
    return render_template('projects.html', projects=all_projects)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page and submission."""
    if request.method == 'POST':
        # Process contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate inputs
        if not all([name, email, subject, message]):
            flash('All fields are required', 'danger')
            return redirect(url_for('main_bp.contact'))
        
        # Save contact to database
        new_contact = models.Contact(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(new_contact)
        
        try:
            db.session.commit()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('main_bp.contact', _anchor='contact-form'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('contact.html') 