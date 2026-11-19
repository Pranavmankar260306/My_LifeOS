
import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class PostgresConnection:
    def __init__(self):
        self.conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=DictCursor
        )

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        query = query.replace("?", "%s")
        cursor.execute(query, params)
        return cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_db_connection():

    if DATABASE_URL:
        return PostgresConnection()

    conn = sqlite3.connect("lifeos.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_db_connection()

    if DATABASE_URL:

        queries = [
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT,
                priority TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'Pending'
            )
            """,

            """
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                amount DOUBLE PRECISION NOT NULL,
                category TEXT,
                date TEXT
            )
            """,

            """
            CREATE TABLE IF NOT EXISTS subjects (
                id SERIAL PRIMARY KEY,
                subject_name TEXT NOT NULL,
                total_topics INTEGER DEFAULT 0,
                completed_topics INTEGER DEFAULT 0
            )
            """,

            """
            CREATE TABLE IF NOT EXISTS study_sessions (
                id SERIAL PRIMARY KEY,
                subject_id INTEGER REFERENCES subjects(id),
                duration DOUBLE PRECISION,
                session_date TEXT
            )
            """,

            """
            CREATE TABLE IF NOT EXISTS habits (
                id SERIAL PRIMARY KEY,
                habit_name TEXT NOT NULL,
                frequency TEXT DEFAULT 'Daily'
            )
            """,

            """
            CREATE TABLE IF NOT EXISTS habit_logs (
                id SERIAL PRIMARY KEY,
                habit_id INTEGER REFERENCES habits(id),
                log_date TEXT,
                completed INTEGER DEFAULT 0
            )
            """
        ]

        for query in queries:
            conn.execute(query)

    else:
        # Keep the existing SQLite database structure
        conn.close()

        conn = sqlite3.connect("lifeos.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                priority TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'Pending'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                date TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                total_topics INTEGER DEFAULT 0,
                completed_topics INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                duration REAL,
                session_date TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_name TEXT NOT NULL,
                frequency TEXT DEFAULT 'Daily'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                log_date TEXT,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
        """)

    conn.commit()
    conn.close()
