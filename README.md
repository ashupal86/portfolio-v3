# Portfolio Website with Admin Panel

A modern portfolio website built with Flask, featuring a comprehensive admin panel for content management.

## Features

- Responsive design
- Admin panel for content management
- Blog system
- Project showcase
- Skills management
- Achievement tracking
- Contact form
- File uploads
- Logging system

## Project Structure

```
portfolio-v3/
├── app_sqlite.py          # Main application file
├── gunicorn_config.py     # Gunicorn configuration
├── requirements.txt       # Python dependencies
├── static/               # Static files
│   ├── css/
│   ├── js/
│   └── img/
├── templates/            # HTML templates
│   ├── admin/           # Admin panel templates
│   ├── auth/            # Authentication templates
│   └── errors/          # Error pages
├── instance/            # Instance-specific files
│   └── portfolio.db     # SQLite database
└── logs/               # Application logs
    └── app.log         # Log file
```

## Routes

### Public Routes
- `/` - Home page
- `/blog` - Blog listing
- `/blog/<slug>` - Individual blog post
- `/projects` - Projects listing
- `/projects/<id>` - Individual project
- `/contact` - Contact form

### Authentication Routes
- `/auth/login` - Login page
- `/auth/logout` - Logout
- `/auth/create-admin` - Create first admin user

### Admin Routes
- `/admin` - Admin dashboard
- `/admin/about` - Manage about content
- `/admin/skills` - Manage skills
- `/admin/projects` - Manage projects
- `/admin/blog` - Manage blog posts
- `/admin/achievements` - Manage achievements
- `/admin/messages` - View contact messages
- `/admin/logger` - View application logs

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd portfolio-v3
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask init-db
```

5. Create the first admin user:
```bash
flask create-admin
```

## Running the Application

### Development
```bash
flask run
```

### Production with Gunicorn
```bash
gunicorn -c gunicorn_config.py app_sqlite:app
```

## Gunicorn Configuration

The application uses Gunicorn with the following configuration:

```python
# gunicorn_config.py
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# Process naming
proc_name = 'portfolio'

# Server mechanics
daemon = False
pidfile = 'logs/gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
```

## Logging

The application logs are stored in the `logs` directory:
- `app.log` - Application logs
- `access.log` - Gunicorn access logs
- `error.log` - Gunicorn error logs

Logs can be viewed through the admin panel at `/admin/logger`.

## Security Features

- Password hashing
- CSRF protection
- Secure file uploads
- Admin authentication
- Input validation
- XSS protection

## Dependencies

- Flask
- SQLite3
- Gunicorn
- Werkzeug
- Python-slugify
- Other dependencies listed in requirements.txt

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
