"""
SMTP sender for Tencent Enterprise Email
Sends emails with proper formatting
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from config import (
    SMTP_SERVER, SMTP_PORT, SMTP_USE_TLS,
    EMAIL_ADDRESS, EMAIL_APP_PASSWORD
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.email_address = EMAIL_ADDRESS
        self.app_password = EMAIL_APP_PASSWORD
        self.server = None

    def connect(self):
        """Connect to SMTP server"""
        try:
            self.server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            if SMTP_USE_TLS:
                self.server.starttls()
            
            self.server.login(self.email_address, self.app_password)
            logger.info(f"✅ Connected to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP connection failed: {e}")
            raise

    def disconnect(self):
        """Disconnect from SMTP server"""
        if self.server:
            self.server.quit()
            logger.info("Disconnected from SMTP server")

    def send_email(self, to_address: str, subject: str, body: str, 
                   is_html: bool = False, cc: List[str] = None,
                   bcc: List[str] = None) -> bool:
        """
        Send an email
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML (default: False)
            cc: CC recipients
            bcc: BCC recipients
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.email_address
            msg["To"] = to_address
            msg["Subject"] = subject
            
            if cc:
                msg["Cc"] = ", ".join(cc)
            
            # Attach body
            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            # Send email
            recipients = [to_address] + (cc or []) + (bcc or [])
            self.server.sendmail(self.email_address, recipients, msg.as_string())
            
            logger.info(f"✅ Email sent to {to_address} with subject: {subject}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"❌ Failed to send email to {to_address}: {e}")
            return False

    def send_reply(self, original_email: Dict, reply_body: str) -> bool:
        """
        Send a reply to an original email
        
        Args:
            original_email: Original email dictionary (from email_receiver.py)
            reply_body: Reply text
        
        Returns:
            True if sent successfully, False otherwise
        """
        # Extract recipient from original email
        from_addr = original_email["from"]
        original_subject = original_email["subject"]
        
        # Create reply subject
        if not original_subject.lower().startswith("re:"):
            reply_subject = f"Re: {original_subject}"
        else:
            reply_subject = original_subject
        
        # Send reply
        return self.send_email(from_addr, reply_subject, reply_body)


# Example usage
if __name__ == "__main__":
    sender = EmailSender()
    sender.connect()
    
    # Test send
    success = sender.send_email(
        to_address="test@example.com",
        subject="Test Email",
        body="This is a test email from Python SMTP."
    )
    
    if success:
        print("✅ Test email sent successfully")
    else:
        print("❌ Failed to send test email")
    
    sender.disconnect()