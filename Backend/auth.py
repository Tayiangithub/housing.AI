import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB = 'database.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Updated table schema with 5 columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            second_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Default admin user with full fields
    c.execute('''
        INSERT OR IGNORE INTO users (first_name, second_name, username, password, role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Admin', 'User', 'admin', generate_password_hash('admin123'), 'admin'))

    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and check_password_hash(result[0], password):
        return result[1]  # Return role
    return None
