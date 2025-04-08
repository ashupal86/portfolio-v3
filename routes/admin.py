import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from slugify import slugify
from app import db, allowed_file
import models

admin_bp = Blueprint('admin_bp', __name__)

# Admin middleware to check for admin privileges
@admin_bp.before_request
def check_admin():
    """Ensure user is logged in and has admin privileges."""
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)  # Forbidden

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard with content statistics."""
    # Count items in each model
    about_count = db.session.query(models.About).count()
    skills_count = db.session.query(models.Skill).count()
    projects_count = db.session.query(models.Project).count()
    achievements_count = db.session.query(models.Achievement).count()
    education_count = db.session.query(models.Education).count()
    blog_posts_count = db.session.query(models.BlogPost).count()
    
    # Get unread messages count
    messages_count = db.session.query(models.Contact).count()
    unread_messages = db.session.query(models.Contact).filter_by(is_read=False).count()
    
    return render_template('admin/dashboard.html',
                          skills_count=skills_count,
                          projects_count=projects_count,
                          achievements_count=achievements_count,
                          education_count=education_count,
                          blog_posts_count=blog_posts_count,
                          messages_count=messages_count,
                          unread_messages=unread_messages)

# About Section CRUD
@admin_bp.route('/about', methods=['GET', 'POST'])
@login_required
def about():
    """Manage About content."""
    about = db.session.query(models.About).first()
    
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not about:
            # Create new About content
            about = models.About(content=content)
            db.session.add(about)
            flash_message = 'About content created successfully!'
        else:
            # Update existing About content
            about.content = content
            about.updated_at = datetime.utcnow()
            flash_message = 'About content updated successfully!'
        
        try:
            db.session.commit()
            flash(flash_message, 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('admin/about.html', about=about)

# Skills CRUD
@admin_bp.route('/skills')
@login_required
def skills():
    """Manage skills."""
    all_skills = db.session.query(models.Skill).order_by(models.Skill.display_order).all()
    return render_template('admin/skills.html', skills=all_skills)

@admin_bp.route('/skills/add', methods=['POST'])
@login_required
def add_skill():
    """Add a new skill."""
    name = request.form.get('name')
    category = request.form.get('category')
    proficiency = request.form.get('proficiency', type=int)
    icon = request.form.get('icon')
    display_order = request.form.get('display_order', type=int, default=0)
    
    # Validate inputs
    if not all([name, category]) or proficiency is None:
        flash('Name, category, and proficiency are required.', 'danger')
        return redirect(url_for('admin_bp.skills'))
    
    # Create new skill
    new_skill = models.Skill(
        name=name,
        category=category,
        proficiency=proficiency,
        icon=icon,
        display_order=display_order
    )
    
    db.session.add(new_skill)
    
    try:
        db.session.commit()
        flash('Skill added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.skills'))

@admin_bp.route('/skills/edit/<int:id>', methods=['POST'])
@login_required
def edit_skill(id):
    """Edit an existing skill."""
    skill = db.session.get(models.Skill, id)
    
    if not skill:
        flash('Skill not found.', 'danger')
        return redirect(url_for('admin_bp.skills'))
    
    # Update skill attributes
    skill.name = request.form.get('name')
    skill.category = request.form.get('category')
    skill.proficiency = request.form.get('proficiency', type=int)
    skill.icon = request.form.get('icon')
    skill.display_order = request.form.get('display_order', type=int, default=0)
    
    try:
        db.session.commit()
        flash('Skill updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.skills'))

@admin_bp.route('/skills/delete/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    """Delete a skill."""
    skill = db.session.get(models.Skill, id)
    
    if not skill:
        flash('Skill not found.', 'danger')
        return redirect(url_for('admin_bp.skills'))
    
    db.session.delete(skill)
    
    try:
        db.session.commit()
        flash('Skill deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.skills'))

# Projects CRUD
@admin_bp.route('/projects')
@login_required
def projects():
    """Manage projects."""
    all_projects = db.session.query(models.Project).order_by(models.Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=all_projects)

@admin_bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    """Add a new project."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        technologies = request.form.get('technologies')
        url = request.form.get('url')
        github_url = request.form.get('github_url')
        featured = request.form.get('featured', type=bool, default=False)
        
        # Validate inputs
        if not all([title, description, technologies]):
            flash('Title, description, and technologies are required.', 'danger')
            return redirect(url_for('admin_bp.add_project'))
        
        # Create new project
        new_project = models.Project(
            title=title,
            description=description,
            technologies=technologies,
            url=url,
            github_url=github_url,
            featured=featured
        )
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_project.image = f'img/uploads/{filename}'
        
        db.session.add(new_project)
        
        try:
            db.session.commit()
            flash('Project added successfully!', 'success')
            return redirect(url_for('admin_bp.projects'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('admin/add_project.html')

@admin_bp.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    """Edit an existing project."""
    project = db.session.get(models.Project, id)
    
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('admin_bp.projects'))
    
    if request.method == 'POST':
        # Update project attributes
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.technologies = request.form.get('technologies')
        project.url = request.form.get('url')
        project.github_url = request.form.get('github_url')
        project.featured = request.form.get('featured', type=bool, default=False)
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                project.image = f'img/uploads/{filename}'
        
        try:
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('admin_bp.projects'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('admin/edit_project.html', project=project)

@admin_bp.route('/projects/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    """Delete a project."""
    project = db.session.get(models.Project, id)
    
    if not project:
        flash('Project not found.', 'danger')
        return redirect(url_for('admin_bp.projects'))
    
    db.session.delete(project)
    
    try:
        db.session.commit()
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.projects'))

# Achievements CRUD
@admin_bp.route('/achievements')
@login_required
def achievements():
    """Manage achievements."""
    all_achievements = db.session.query(models.Achievement).order_by(models.Achievement.date.desc()).all()
    return render_template('admin/achievements.html', achievements=all_achievements)

@admin_bp.route('/achievements/add', methods=['GET', 'POST'])
@login_required
def add_achievement():
    """Add a new achievement."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        
        # Validate inputs
        if not all([title, description]):
            flash('Title and description are required.', 'danger')
            return redirect(url_for('admin_bp.add_achievement'))
        
        # Parse date (if provided)
        date = None
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('admin_bp.add_achievement'))
        
        # Create new achievement
        new_achievement = models.Achievement(
            title=title,
            description=description,
            date=date
        )
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_achievement.image = f'img/uploads/{filename}'
        
        db.session.add(new_achievement)
        
        try:
            db.session.commit()
            flash('Achievement added successfully!', 'success')
            return redirect(url_for('admin_bp.achievements'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('admin/add_achievement.html')

@admin_bp.route('/achievements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_achievement(id):
    """Edit an existing achievement."""
    achievement = db.session.get(models.Achievement, id)
    
    if not achievement:
        flash('Achievement not found.', 'danger')
        return redirect(url_for('admin_bp.achievements'))
    
    if request.method == 'POST':
        # Update achievement attributes
        achievement.title = request.form.get('title')
        achievement.description = request.form.get('description')
        
        date_str = request.form.get('date')
        if date_str:
            try:
                achievement.date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('admin_bp.edit_achievement', id=id))
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                achievement.image = f'img/uploads/{filename}'
        
        try:
            db.session.commit()
            flash('Achievement updated successfully!', 'success')
            return redirect(url_for('admin_bp.achievements'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('admin/edit_achievement.html', achievement=achievement)

@admin_bp.route('/achievements/delete/<int:id>', methods=['POST'])
@login_required
def delete_achievement(id):
    """Delete an achievement."""
    achievement = db.session.get(models.Achievement, id)
    
    if not achievement:
        flash('Achievement not found.', 'danger')
        return redirect(url_for('admin_bp.achievements'))
    
    db.session.delete(achievement)
    
    try:
        db.session.commit()
        flash('Achievement deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.achievements'))

# Education CRUD routes follow the same pattern as above
@admin_bp.route('/education')
@login_required
def education():
    """Manage education."""
    all_education = db.session.query(models.Education).order_by(models.Education.start_date.desc()).all()
    return render_template('admin/education.html', education=all_education)

# Blog CRUD routes
@admin_bp.route('/blog')
@login_required
def blog():
    """Manage blog posts."""
    all_posts = db.session.query(models.BlogPost).order_by(models.BlogPost.created_at.desc()).all()
    return render_template('admin/blog.html', posts=all_posts)

@admin_bp.route('/blog/add', methods=['GET', 'POST'])
@login_required
def add_blog_post():
    """Add a new blog post."""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        slug = request.form.get('slug')
        
        # Validate inputs
        if not all([title, content]):
            flash('Title and content are required.', 'danger')
            return redirect(url_for('admin_bp.add_blog_post'))
        
        # Generate slug from title if not provided
        if not slug:
            slug = slugify(title)
        
        # Check if slug already exists
        existing_post = db.session.query(models.BlogPost).filter_by(slug=slug).first()
        if existing_post:
            flash('A post with this slug already exists. Please choose a different title or slug.', 'danger')
            return redirect(url_for('admin_bp.add_blog_post'))
        
        # Create new blog post
        new_post = models.BlogPost(
            title=title,
            content=content,
            slug=slug
        )
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_post.image = f'img/uploads/{filename}'
        
        db.session.add(new_post)
        
        try:
            db.session.commit()
            flash('Blog post published successfully!', 'success')
            return redirect(url_for('admin_bp.blog'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('admin/add_blog_post.html')

@admin_bp.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog_post(id):
    """Edit an existing blog post."""
    post = db.session.get(models.BlogPost, id)
    
    if not post:
        flash('Blog post not found.', 'danger')
        return redirect(url_for('admin_bp.blog'))
    
    if request.method == 'POST':
        # Update post attributes
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        
        slug = request.form.get('slug')
        if slug and slug != post.slug:
            # Check if new slug already exists
            existing_post = db.session.query(models.BlogPost).filter_by(slug=slug).first()
            if existing_post and existing_post.id != post.id:
                flash('A post with this slug already exists. Please choose a different slug.', 'danger')
                return redirect(url_for('admin_bp.edit_blog_post', id=id))
            post.slug = slug
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                post.image = f'img/uploads/{filename}'
        
        try:
            db.session.commit()
            flash('Blog post updated successfully!', 'success')
            return redirect(url_for('admin_bp.blog'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('admin/edit_blog_post.html', post=post)

@admin_bp.route('/blog/delete/<int:id>', methods=['POST'])
@login_required
def delete_blog_post(id):
    """Delete a blog post."""
    post = db.session.get(models.BlogPost, id)
    
    if not post:
        flash('Blog post not found.', 'danger')
        return redirect(url_for('admin_bp.blog'))
    
    db.session.delete(post)
    
    try:
        db.session.commit()
        flash('Blog post deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.blog'))

# Contact messages management
@admin_bp.route('/messages')
@login_required
def messages():
    """View contact form submissions."""
    all_messages = db.session.query(models.Contact).order_by(models.Contact.created_at.desc()).all()
    return render_template('admin/messages.html', messages=all_messages)

@admin_bp.route('/messages/view/<int:id>')
@login_required
def view_message(id):
    """View a single contact message."""
    message = db.session.get(models.Contact, id)
    
    if not message:
        flash('Message not found.', 'danger')
        return redirect(url_for('admin_bp.messages'))
    
    # Mark message as read
    if not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return render_template('admin/view_message.html', message=message)

@admin_bp.route('/messages/delete/<int:id>', methods=['POST'])
@login_required
def delete_message(id):
    """Delete a contact message."""
    message = db.session.get(models.Contact, id)
    
    if not message:
        flash('Message not found.', 'danger')
        return redirect(url_for('admin_bp.messages'))
    
    db.session.delete(message)
    
    try:
        db.session.commit()
        flash('Message deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('admin_bp.messages')) 