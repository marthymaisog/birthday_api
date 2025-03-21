from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3
import re

app = Flask(__name__)

# Initialize SQLite database
DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            date_of_birth TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Validate username and date of birth
def is_valid_username(username):
    return re.match("^[a-zA-Z]+$", username)

def is_valid_date_of_birth(date_of_birth):
    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
        return dob < datetime.now()
    except ValueError:
        return False

@app.route('/hello/<username>', methods=['PUT'])
def save_user(username):
    if not is_valid_username(username):
        return "Invalid username. Only letters are allowed.", 400

    data = request.get_json()
    date_of_birth = data.get("dateOfBirth")

    if not is_valid_date_of_birth(date_of_birth):
        return "Invalid date of birth. Must be in YYYY-MM-DD format and before today's date.", 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, date_of_birth) VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET date_of_birth=excluded.date_of_birth
    ''', (username, date_of_birth))
    conn.commit()
    conn.close()

    return "", 204

@app.route('/hello/<username>', methods=['GET'])
def get_birthday_message(username):
    if not is_valid_username(username):
        return "Invalid username. Only letters are allowed.", 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT date_of_birth FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "User not found.", 404

    date_of_birth = datetime.strptime(row[0], "%Y-%m-%d")
    today = datetime.now()
    next_birthday = date_of_birth.replace(year=today.year)
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=today.year + 1)

    days_until_birthday = (next_birthday - today).days

    if days_until_birthday == 0:
        message = f"Hello, {username}! Happy birthday!"
    else:
        message = f"Hello, {username}! Your birthday is in {days_until_birthday} day(s)."

    return jsonify({"message": message}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
