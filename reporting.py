"""Archive and reporting utilities for daily/weekly/monthly/yearly aftersale summaries."""

import os
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import SQLITE_DB_PATH, ARCHIVE_DIR

TZ_SH = ZoneInfo("Asia/Shanghai")


def _date_range(period: str):
    now = datetime.now(TZ_SH)
    today = now.date()
    if period == "daily":
        start = today - timedelta(days=1)
        end = today
    elif period == "weekly":
        start = today - timedelta(days=7)
        end = today
    elif period == "monthly":
        start = today - timedelta(days=30)
        end = today
    elif period == "yearly":
        start = today - timedelta(days=365)
        end = today
    else:
        raise ValueError("unknown period")
    return start.isoformat(), end.isoformat()


def generate_period_report(period: str, db_path: str = SQLITE_DB_PATH):
    start, end = _date_range(period)
    with sqlite3.connect(db_path) as conn:
        total = conn.execute(
            """
            SELECT COUNT(1) FROM email_reviews
            WHERE date(created_at) >= ? AND date(created_at) < ?
            """,
            (start, end),
        ).fetchone()[0]

        manual = conn.execute(
            """
            SELECT COUNT(1) FROM email_reviews
            WHERE date(created_at) >= ? AND date(created_at) < ?
              AND lower(risk_flag) IN ('high', 'true', '1')
            """,
            (start, end),
        ).fetchone()[0]

        by_category = conn.execute(
            """
            SELECT category, COUNT(1) c
            FROM email_reviews
            WHERE date(created_at) >= ? AND date(created_at) < ?
            GROUP BY category
            ORDER BY c DESC
            """,
            (start, end),
        ).fetchall()

    auto_count = total - manual
    lines = [
        f"[{period}] {start} ~ {end}",
        f"Total: {total}",
        f"LLM/auto handled: {auto_count}",
        f"Need manual follow-up: {manual}",
        "Category breakdown:",
    ]
    for category, c in by_category:
        lines.append(f"- {category or 'Uncategorized'}: {c}")
    return "\n".join(lines)


def archive_report(period: str, report_text: str, archive_dir: str = ARCHIVE_DIR):
    now = datetime.now(TZ_SH)
    folder = os.path.join(archive_dir, str(now.year), f"{now.month:02d}")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{period}_{now.strftime('%Y%m%d_%H%M%S')}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)
    return path


def build_daily_feishu_message(db_path: str = SQLITE_DB_PATH):
    daily = generate_period_report("daily", db_path=db_path)
    weekly = generate_period_report("weekly", db_path=db_path)
    return f"售后日报（北京时间9点）\n\n{daily}\n\n---\n\n本周趋势\n{weekly}"
