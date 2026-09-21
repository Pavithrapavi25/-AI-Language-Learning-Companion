import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "history.db"
)


def create_database():
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS translation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_text TEXT NOT NULL,
            source_language TEXT NOT NULL,
            target_language TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()

    print("Database created successfully at:", DB_PATH)


if __name__ == "__main__":
    create_database()