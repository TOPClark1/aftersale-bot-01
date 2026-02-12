"""
SQLite persistence for email reviews.
"""

import os
import sqlite3
from datetime import datetime
from typing import Iterable, Dict

from config import SQLITE_DB_PATH
from aftersale_scenario_seed import SCENARIO_SEEDS


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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS aftersale_situation_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_key TEXT UNIQUE,
                    tags TEXT,
                    language TEXT,
                    title TEXT,
                    reply_template TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.commit()
        self.seed_situation_library_if_empty()


    def seed_situation_library_if_empty(self):
        now = datetime.now().isoformat(timespec="seconds")
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute("SELECT COUNT(1) FROM aftersale_situation_library").fetchone()[0]
            if existing > 0:
                return
            conn.executemany(
                """
                INSERT INTO aftersale_situation_library (
                    scenario_key, tags, language, title, reply_template, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item["scenario_key"],
                        item.get("tags", ""),
                        item.get("language", "en"),
                        item.get("title", ""),
                        item.get("reply_template", ""),
                        now,
                        now,
                    )
                    for item in SCENARIO_SEEDS
                ],
            )
            conn.commit()

    def add_situation_template(self, scenario_key: str, tags: str, language: str, title: str, reply_template: str):
        now = datetime.now().isoformat(timespec="seconds")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO aftersale_situation_library (
                    scenario_key, tags, language, title, reply_template, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(scenario_key) DO UPDATE SET
                    tags=excluded.tags,
                    language=excluded.language,
                    title=excluded.title,
                    reply_template=excluded.reply_template,
                    updated_at=excluded.updated_at
                """,
                (scenario_key, tags, language, title, reply_template, now, now),
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
