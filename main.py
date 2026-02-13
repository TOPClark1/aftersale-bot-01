import json
from email_receiver import EmailReceiver
from email_classifier import EmailClassifier
from email_reply_generator import ReplyGenerator
from email_review_manager import ReviewManager
from review_database import ReviewDatabase
from feishu_client import FeishuClient
from config import (
    EMAIL_ADDRESS,
    EMAIL_APP_PASSWORD,
    IMAP_SERVER,
    PROCESS_UNSEEN_ONLY,
    MARK_AS_READ_AFTER_PROCESS,
    FEISHU_TABLE_WEBHOOK,
    FEISHU_BOT_WEBHOOK,
    FEISHU_PUSH_ON_RUN,
)
def _has_imap_config() -> bool:
    return bool(EMAIL_ADDRESS and EMAIL_APP_PASSWORD and IMAP_SERVER)
def _demo_emails():
    return [
        {
            "id": "demo-1",
            "from": "customer1@example.com",
            "subject": "Login error",
            "body": "I cannot log in to my account. The app keeps showing an error.",
            "date": "2026-02-06 09:15",
        },
        {
            "id": "demo-2",
            "from": "customer2@example.com",
            "subject": "Invoice request",
            "body": "Could you send me a copy of last month's invoice?",
            "date": "2026-02-06 10:02",
        },
        {
            "id": "demo-3",
            "from": "customer3@example.com",
            "subject": "Feature request: dark mode",
            "body": "It would be great if the app had a dark mode option.",
            "date": "2026-02-06 10:25",
        },
    ]
def _fetch_emails_with_optional_mark_read():
    if not _has_imap_config():
        return _demo_emails(), 0
    receiver = EmailReceiver()
    marked_count = 0
    try:
        receiver.connect()
        emails = receiver.fetch_emails(unread_only=PROCESS_UNSEEN_ONLY)
        if MARK_AS_READ_AFTER_PROCESS:
            for email in emails:
                receiver.mark_as_read(email.get("id", ""))
                marked_count += 1
        return emails, marked_count
    finally:
        receiver.disconnect()
def run_daily_pipeline():
    emails, marked_count = _fetch_emails_with_optional_mark_read()
    if not emails:
        print("No emails to process.")
        return {"total": 0}
    classifier = EmailClassifier(use_llm=True)
    reply_generator = ReplyGenerator()
    review_manager = ReviewManager()
    review_db = ReviewDatabase()
    feishu_client = FeishuClient(bot_webhook=FEISHU_BOT_WEBHOOK, table_webhook=FEISHU_TABLE_WEBHOOK)
    reviews = []
    manual_items = []
    for email in emails:
        category, confidence = classifier.classify(email.get("subject", ""), email.get("body", ""))
        reply_draft = reply_generator.generate_reply(email, category, use_llm=True)
        risk_flag = category == "Other" or confidence < 0.6
        review_row = {
            **email,
            "category": category,
            "confidence": confidence,
            "reply": reply_draft,
            "risk_flag": "high" if risk_flag else "low",
        }
        reviews.append(review_row)
        print("\n" + "=" * 60)
        print(f"From: {email.get('from')}")
        print(f"Subject: {email.get('subject')}")
        print(f"Category: {category} (confidence {confidence:.2f})")
        print("Suggested reply:")
        print(reply_draft)
        if risk_flag:
            manual_items.append(
                {
                    "from": email.get("from", ""),
                    "subject": email.get("subject", ""),
                    "category": category,
                    "confidence": round(confidence, 2),
                }
            )
    csv_path = review_manager.generate_review_csv(reviews)
    if csv_path:
        print(f"\nReview CSV generated: {csv_path}")
    review_db.save_reviews(reviews)
    feishu_rows = [
        {
            "from": r.get("from", ""),
            "subject": r.get("subject", ""),
            "category": r.get("category", ""),
            "confidence": r.get("confidence", 0),
            "risk_flag": r.get("risk_flag", ""),
            "received_date": r.get("date", ""),
        }
        for r in reviews
    ]
    feishu_table_ok = feishu_client.append_table_rows(feishu_rows)
    feishu_bot_ok = False
    if FEISHU_PUSH_ON_RUN and FEISHU_BOT_WEBHOOK:
        msg_lines = [
            "售后处理结果（本次运行）",
            f"总邮件数: {len(reviews)}",
            f"大模型/自动草拟: {len(reviews) - len(manual_items)}",
            f"需要人工处理: {len(manual_items)}",
            f"已取消未读标记: {marked_count}",
            f"CSV: {csv_path or ''}",
        ]
        if manual_items:
            msg_lines.append("需要人工处理列表:")
            for item in manual_items[:10]:
                msg_lines.append(f"- {item.get('from','')} | {item.get('subject','')} | {item.get('category','')}")
        feishu_bot_ok = feishu_client.send_bot_text("\n".join(msg_lines))
    summary = {
        "total": len(reviews),
        "manual_count": len(manual_items),
        "auto_count": len(reviews) - len(manual_items),
        "marked_read_count": marked_count,
        "csv_path": csv_path or "",
        "manual_items": manual_items,
        "feishu_table_pushed": feishu_table_ok,
        "feishu_bot_pushed": feishu_bot_ok,
    }
    print("RUN_SUMMARY_JSON: " + json.dumps(summary, ensure_ascii=False))
    return summary
if __name__ == "__main__":
    run_daily_pipeline()