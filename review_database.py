"""
SQLite persistence for email reviews.
"""

import os
import sqlite3
from datetime import datetime
from typing import Iterable, Dict

from config import SQLITE_DB_PATH


class ReviewDatabase:
    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS email_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT,
                    sender TEXT,
                    subject TEXT,
                    category TEXT,
                    confidence REAL,
                    original_body TEXT,
                    suggested_reply TEXT,
                    status TEXT,
                    reviewer_notes TEXT,
                    received_date TEXT,
                    risk_flag TEXT,
                    created_at TEXT
                )
                """
            )
            conn.commit()

    def save_reviews(self, reviews: Iterable[Dict]):
        reviews_list = list(reviews)
        if not reviews_list:
            return
        created_at = datetime.now().isoformat(timespec="seconds")
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO email_reviews (
                    email_id,
                    sender,
                    subject,
                    category,
                    confidence,
                    original_body,
                    suggested_reply,
                    status,
                    reviewer_notes,
                    received_date,
                    risk_flag,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        review.get("id", ""),
                        review.get("from", ""),
                        review.get("subject", ""),
                        review.get("category", ""),
                        review.get("confidence", 0.0),
                        review.get("body", ""),
                        review.get("reply", ""),
                        review.get("status", "pending_review"),
                        review.get("reviewer_notes", ""),
                        review.get("date", ""),
                        review.get("risk_flag", ""),
                        created_at,
                    )
                    for review in reviews_list
                ],
            )
            conn.commit()
