from email_receiver import fetch_unread_emails
from email_classifier import classify_email
from email_reply_generator import generate_reply
from email_review_manager import append_to_review_csv

def run_daily_pipeline():
    emails = fetch_unread_emails()

    for email in emails:
        category = classify_email(email)
        reply_draft, risk_flag = generate_reply(email, category)

        append_to_review_csv(
            email=email,
            category=category,
            reply_draft=reply_draft,
            risk_flag=risk_flag
        )

if __name__ == "__main__":
    run_daily_pipeline()
