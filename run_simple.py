from app_sqlite import app

if __name__ == '__main__':
    # Only enable debug mode when running directly with Python
    app.run(debug=True, host='0.0.0.0', port=5000) 