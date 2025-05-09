import sqlite3

def init_db():
    conn = sqlite3.connect("news_app.db")
    c = conn.cursor()

    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password_hash TEXT
        )
    ''')

    # User Interests
    c.execute('''
       CREATE TABLE IF NOT EXISTS user_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topics TEXT,  
    countries TEXT, 
    FOREIGN KEY (user_id) REFERENCES users(id)
)
    ''')

    # Saved News
    c.execute('''
        CREATE TABLE IF NOT EXISTS saved_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            url TEXT,
            source TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS user_interests (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         user_id INTEGER NOT NULL,
    #         topics TEXT,
    #         countries TEXT,
    #         FOREIGN KEY (user_id) REFERENCES users(id)
    #     )
    # ''')


    conn.commit()
    conn.close()
