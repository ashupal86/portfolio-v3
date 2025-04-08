# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/instance /app/static/img/uploads \
    && touch /app/instance/portfolio.db \
    && chmod -R 777 /app/logs /app/instance /app/static/img/uploads

# Set environment variables
ENV FLASK_APP=app_sqlite.py
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app_sqlite.py"] 