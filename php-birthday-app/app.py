from flask import Flask, request, jsonify, render_template
from datetime import datetime
import sqlite3
import re
import os


app = Flask(__name__)
DATABASE = os.path.join('/data', 'birthdays.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

def initialize_database():
    """Initialize database with proper error handling"""
    try:
        with app.app_context():
            with get_db() as db:
                db.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        date_of_birth DATE NOT NULL
                    )
                ''')
                db.commit()
                app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Database initialization failed: {str(e)}")
        raise

# Initialize database on startup
initialize_database()

@app.route('/hello/<username>', methods=['PUT'])
def upsert_user(username):
    if not re.match('^[a-zA-Z]+$', username):
        return jsonify({'error': 'Invalid username format'}), 400
    
    data = request.get_json()
    if not data or 'dateOfBirth' not in data:
        return jsonify({'error': 'Missing dateOfBirth'}), 400
    
    try:
        birth_date = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    today = datetime.today().date()
    if birth_date >= today:
        return jsonify({'error': 'Date must be before today'}), 400
    
    try:
        with get_db() as db:
            db.execute('''
                INSERT INTO users (username, date_of_birth)
                VALUES (?, ?)
                ON CONFLICT(username) DO UPDATE SET date_of_birth = excluded.date_of_birth
            ''', (username, birth_date.isoformat()))
            db.commit()
        return '', 204
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/hello/<username>', methods=['GET'])
def get_birthday(username):
    try:
        with get_db() as db:
            user = db.execute(
                'SELECT date_of_birth FROM users WHERE username = ?', 
                (username,)
            ).fetchone()
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database operation failed'}), 500
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        birth_date = datetime.strptime(user['date_of_birth'], '%Y-%m-%d').date()
        today = datetime.today().date()
        next_birthday = birth_date.replace(year=today.year)
        
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        
        days_remaining = (next_birthday - today).days
        message = (f"Hello, {username}! Happy birthday!" if days_remaining == 0
                  else f"Hello, {username}! Your birthday is in {days_remaining} day(s)")
        
        return jsonify({'message': message})
    except Exception as e:
        app.logger.error(f"Date calculation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        with get_db() as db:
            users = db.execute('SELECT * FROM users').fetchall()
            return jsonify([dict(user) for user in users])
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database operation failed'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)