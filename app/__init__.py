import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()

# Global models dict to store model classes
models = {}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config['default'].ALLOWED_EXTENSIONS


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Initialize models
    from app.models import init_models
    global models
    models = init_models(db)
    
    # Fix for proper IP handling with reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load a user by ID for Flask-Login."""
        return models['User'].query.get(int(user_id))
    
    @app.context_processor
    def inject_now():
        """Inject current datetime into templates."""
        return {'now': datetime.utcnow()}
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors with custom template."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle 500 errors with custom template."""
        return render_template('errors/500.html'), 500
    
    # Create DB tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Database tables created.')
        except Exception as e:
            app.logger.error(f'Error creating database tables: {e}')
    
    return app 