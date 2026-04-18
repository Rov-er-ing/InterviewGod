import sqlite3
import json
import os
from datetime import datetime
from utils.logger import logger

class Storage:
    """
    Handles persistence of detected signals using SQLite and JSON.
    """

    def __init__(self, db_path="data/signals.db", json_path="outputs/signals.json"):
        self.db_path = db_path
        self.json_path = json_path
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    title TEXT,
                    url TEXT UNIQUE,
                    published_at TEXT,
                    score REAL,
                    confidence TEXT,
                    max_volume INTEGER,
                    detected_at TEXT,
                    raw_data TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def save_signals(self, signals):
        """Saves a list of signal dictionaries to both SQLite and JSON."""
        if not signals:
            return

        # 1. Save to SQLite (with deduplication based on URL)
        self._save_to_sqlite(signals)

        # 2. Save to JSON (overwrites with current batch)
        self._save_to_json(signals)

    def _save_to_sqlite(self, signals):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            new_count = 0
            for s in signals:
                parsed = s.get("parsed_data", {})
                try:
                    cursor.execute('''
                        INSERT INTO signals (
                            company_name, title, url, published_at, score, 
                            confidence, max_volume, detected_at, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        s.get("company_name"),
                        s.get("title"),
                        s.get("url"),
                        s.get("published_at"),
                        s.get("score"),
                        s.get("confidence"),
                        parsed.get("max_volume", 0),
                        datetime.now().isoformat(),
                        json.dumps(s)
                    ))
                    new_count += 1
                except sqlite3.IntegrityError:
                    # Signal already exists (unique URL)
                    continue
            
            conn.commit()
            conn.close()
            logger.info(f"Saved {new_count} new signals to SQLite database.")
        except Exception as e:
            logger.error(f"Error saving to SQLite: {e}")

    def _save_to_json(self, signals):
        try:
            os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
            with open(self.json_path, 'w') as f:
                json.dump(signals, f, indent=4)
            logger.info(f"Exported {len(signals)} signals to JSON: {self.json_path}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")

    def get_all_signals(self):
        """Retrieves all stored signals from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM signals ORDER BY score DESC')
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving signals: {e}")
            return []
