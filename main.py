from email_receiver import fetch_unread_emails
from email_classifier import EmailClassifier
from email_reply_generator import ReplyGenerator
from email_review_manager import ReviewManager
from config import EMAIL_ADDRESS, EMAIL_APP_PASSWORD, IMAP_SERVER


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

def run_daily_pipeline():
    if _has_imap_config():
        emails = fetch_unread_emails()
    else:
        emails = _demo_emails()

    if not emails:
        print("No emails to process.")
        return

    classifier = EmailClassifier(use_llm=True)
    reply_generator = ReplyGenerator()
    review_manager = ReviewManager()
    reviews = []

    for email in emails:
        category, confidence = classifier.classify(email.get("subject", ""), email.get("body", ""))
        reply_draft = reply_generator.generate_reply(email, category, use_llm=True)
        risk_flag = category == "Other" or confidence < 0.6

        reviews.append({
            **email,
            "category": category,
            "confidence": confidence,
            "reply": reply_draft,
            "risk_flag": "high" if risk_flag else "low",
        })

        print("\n" + "=" * 60)
        print(f"From: {email.get('from')}")
        print(f"Subject: {email.get('subject')}")
        print(f"Category: {category} (confidence {confidence:.2f})")
        print("Suggested reply:")
        print(reply_draft)

    csv_path = review_manager.generate_review_csv(reviews)
    if csv_path:
        print(f"\n✅ Review CSV generated: {csv_path}")

if __name__ == "__main__":
    run_daily_pipeline()
