import sqlite3
import bcrypt

DB = "news_app.db"  # Correct database name

def get_connection():
    return sqlite3.connect(DB)

def create_user(username, email, password):
    conn = get_connection()
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
              (username, email, hashed.decode()))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user[3].encode()):
        return {"id": user[0], "username": user[1], "email": user[2]}
    return None

def save_user_interests(user_id, topics, countries):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM user_interests WHERE user_id = ?", (user_id,))
    for topic in topics:
        for country in countries:
            c.execute("INSERT INTO user_interests (user_id, topic, country) VALUES (?, ?, ?)",
                      (user_id, topic, country))
    conn.commit()
    conn.close()

# Fix: Corrected database connection and logic for fetching user interests
def get_user_interests(user_id):
    conn = get_connection()  # Correct database connection
    cursor = conn.cursor()
    cursor.execute("SELECT topic, country FROM user_interests WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()  # Fetch all rows for the user (topics and countries)
    conn.close()

    if rows:
        topics = [row[0] for row in rows]  # Extract topics from rows
        countries = [row[1] for row in rows]  # Extract countries from rows
        return {"topics": topics, "countries": countries}
    return None

# def get_user_interests(user_id):
#     conn = sqlite3.connect("news_app.db")
#     c = conn.cursor()
#     c.execute("SELECT topic, country FROM user_interests WHERE user_id = ?", (user_id,))
#     interests = c.fetchone()  # Only one row should exist for each user
#     conn.close()

#     topics = interests[0].split(",") if interests else []
#     countries = interests[1].split(",") if interests else []
#     return {"topics": topics, "countries": countries}
