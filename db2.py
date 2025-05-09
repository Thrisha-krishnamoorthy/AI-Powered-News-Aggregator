import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            user TEXT,
            title TEXT,
            category TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(username, password):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    data = c.fetchone()
    conn.close()
    if data and data[0] == hash_password(password):
        return True
    return False

def log_click(user, title, category):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("INSERT INTO clicks (user, title, category) VALUES (?, ?, ?)", (user, title, category))
    conn.commit()
    conn.close()

def get_user_clicks(user):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("SELECT category FROM clicks WHERE user=?", (user,))
    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return categories
