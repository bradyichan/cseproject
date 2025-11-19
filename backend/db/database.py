"""Database connection and initialization utilities for Marketplace."""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "marketplace.db")


def get_connection():
    """Return a SQLite3 connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # --- CREATE TABLES ---
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            joined TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            price REAL,
            location TEXT,
            seller_id INTEGER,
            created_at TEXT,
            image_filename TEXT,  -- <<<< NEW COLUMN FOR IMAGE STORAGE
            FOREIGN KEY (seller_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            bidder_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'pending',
            timestamp TEXT,
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (bidder_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            buyer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'unshipped',
            purchased_at TEXT,
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (buyer_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payment_method_id TEXT NOT NULL,
            card_last4 TEXT,
            expiry_date TEXT,
            verified INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            sender_id INTEGER,
            receiver_id INTEGER,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        );
        """
    )

    # --- FORCE ADD COLUMN IF DATABASE ALREADY EXISTS ---
    try:
        cursor.execute("ALTER TABLE items ADD COLUMN image_filename TEXT;")
        print("Added missing image_filename column to items table.")
    except sqlite3.OperationalError:
        # Column already exists → do nothing
        pass

    conn.commit()
    conn.close()
