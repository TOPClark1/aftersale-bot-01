"""Auto-trigger app: run pipeline daily and push Feishu report at 09:00 Asia/Shanghai."""

import time
from datetime import datetime
from zoneinfo import ZoneInfo

from config import FEISHU_BOT_WEBHOOK, AUTO_RUN_ON_START
from main import run_daily_pipeline
from feishu_client import FeishuClient
from reporting import build_daily_feishu_message, archive_report, generate_period_report

TZ_SH = ZoneInfo("Asia/Shanghai")


def run_once_with_archives():
    run_daily_pipeline()

    daily = generate_period_report("daily")
    weekly = generate_period_report("weekly")
    monthly = generate_period_report("monthly")
    yearly = generate_period_report("yearly")

    archive_report("daily", daily)
    archive_report("weekly", weekly)
    archive_report("monthly", monthly)
    archive_report("yearly", yearly)

    if FEISHU_BOT_WEBHOOK:
        msg = build_daily_feishu_message()
        FeishuClient(bot_webhook=FEISHU_BOT_WEBHOOK).send_bot_text(msg)


def run_scheduler_forever():
    print("Auto app started. Will run every day at 09:00 (Asia/Shanghai).")
    last_run_day = None

    if AUTO_RUN_ON_START:
        run_once_with_archives()
        last_run_day = datetime.now(TZ_SH).date().isoformat()
        print("Startup run completed and summary pushed (if webhook configured).")
    while True:
        now = datetime.now(TZ_SH)
        if now.hour == 9 and now.minute == 0:
            today = now.date().isoformat()
            if last_run_day != today:
                run_once_with_archives()
                last_run_day = today
        time.sleep(20)


if __name__ == "__main__":
    run_scheduler_forever()
