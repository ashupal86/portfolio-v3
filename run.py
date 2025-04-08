"""
Simple script to run our portfolio application with SQLite.
"""
from app_sqlite import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000) 