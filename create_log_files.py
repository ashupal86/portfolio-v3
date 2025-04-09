import os

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Create empty log files
log_files = ['app.log', 'gunicorn-access.log', 'gunicorn-error.log']
for log_file in log_files:
    file_path = os.path.join('logs', log_file)
    with open(file_path, 'w') as f:
        f.write('')  # Write empty string
    print(f"Created empty log file: {file_path}")

print("Log files created successfully.") 