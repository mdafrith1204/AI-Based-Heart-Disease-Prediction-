import sqlite3
import os

DATABASE = "database/heart.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    os.makedirs("database", exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

  
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prediction TEXT,
        probability REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def create_user(name, email, password):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name,email,password) VALUES (?,?,?)",
        (name, email, password)
    )

    conn.commit()
    conn.close()


def save_prediction(user_id, prediction, probability):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO predictions (user_id,prediction,probability) VALUES (?,?,?)",
        (user_id, prediction, probability)
    )

    conn.commit()
    conn.close()