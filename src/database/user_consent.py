# src/database/user_consent.py
import sqlite3
import os

DB_PATH = "data/users.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_consent (
            id INTEGER PRIMARY KEY,
            consent BOOLEAN NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def has_user_consented():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT consent FROM user_consent WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row is not None and row[0] == 1

def ask_for_consent():
    consent_input = input("Do you agree to share data? (y/n): ").strip().lower()
    consent = 1 if consent_input == "y" else 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_consent (id, consent) VALUES (1, ?)", (consent,))
    conn.commit()
    conn.close()

    print("Consent saved:", "Agreed" if consent else "Declined")
