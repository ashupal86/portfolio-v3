# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p instance
RUN mkdir -p logs
RUN mkdir -p static/img/uploads

# Set permissions
RUN chmod -R 755 .

# Run the seed script to initialize the database
RUN python seed_db.py

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app_sqlite.py
ENV FLASK_ENV=production

# Run using gunicorn
CMD ["gunicorn", "app_sqlite:app", "--bind", "0.0.0.0:5000", "--access-logfile", "logs/gunicorn-access.log", "--error-logfile", "logs/gunicorn-error.log"] 