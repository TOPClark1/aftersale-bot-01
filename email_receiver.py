"""
IMAP receiver for Tencent Enterprise Email
Fetches unread emails with full parsing
"""

import imaplib
import email
import email.message
from email.header import decode_header
from typing import List, Dict
from config import (
    IMAP_SERVER, IMAP_PORT, IMAP_USE_SSL,
    EMAIL_ADDRESS, EMAIL_APP_PASSWORD, PROCESS_UNSEEN_ONLY
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _has_imap_config() -> bool:
    return bool(IMAP_SERVER and EMAIL_ADDRESS and EMAIL_APP_PASSWORD)


class EmailReceiver:
    def __init__(self):
        self.server = None
        self.email_address = EMAIL_ADDRESS
        self.app_password = EMAIL_APP_PASSWORD

    def connect(self):
        """Connect to IMAP server"""
        try:
            if not _has_imap_config():
                raise ValueError("Missing IMAP configuration (IMAP_SERVER/EMAIL_ADDRESS/EMAIL_APP_PASSWORD).")
            if IMAP_USE_SSL:
                self.server = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            else:
                self.server = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
            
            self.server.login(self.email_address, self.app_password)
            logger.info(f"✅ Connected to {IMAP_SERVER} as {self.email_address}")
        except imaplib.IMAP4.error as e:
            logger.error(f"❌ IMAP login failed: {e}")
            raise

    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.server:
            self.server.close()
            self.server.logout()
            logger.info("Disconnected from IMAP server")

    def fetch_emails(self, folder: str = "INBOX", unread_only: bool = True) -> List[Dict]:
        """
        Fetch emails from specified folder
        
        Args:
            folder: Mailbox folder name (default: INBOX)
            unread_only: Only fetch unread emails (default: True)
        
        Returns:
            List of dictionaries with email data
        """
        emails = []
        
        try:
            # Select the folder
            self.server.select(folder, readonly=False)
            
            # Search for emails
            if unread_only:
                search_criteria = "UNSEEN"
            else:
                search_criteria = "ALL"
            
            status, message_ids = self.server.search(None, search_criteria)
            
            if status != "OK" or not message_ids[0]:
                logger.info(f"No {search_criteria} emails in {folder}")
                return emails
            
            # Fetch each email
            for msg_id in message_ids[0].split():
                status, msg_data = self.server.fetch(msg_id, "(RFC822)")
                
                if status != "OK":
                    logger.warning(f"Failed to fetch email {msg_id}")
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Parse email
                email_dict = self._parse_email(msg, msg_id.decode())
                emails.append(email_dict)
            
            logger.info(f"✅ Fetched {len(emails)} emails from {folder}")
            return emails
            
        except Exception as e:
            logger.error(f"❌ Error fetching emails: {e}")
            return emails

    def _parse_email(self, msg: email.message.Message, msg_id: str) -> Dict:
        """Parse email message into structured data"""
        
        # Decode subject
        subject, _ = decode_header(msg.get("Subject", ""))[0] if msg.get("Subject") else ("", None)
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8', errors='ignore')
        
        # Get sender
        from_addr = msg.get("From", "")
        
        # Get date
        date = msg.get("Date", "")
        
        # Extract body (plain text preferred, fallback to HTML)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
                elif part.get_content_type() == "text/html" and not body:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = msg.get_payload()
        
        # Clean up body
        body = body.strip()[:1000]  # First 1000 chars
        
        return {
            "id": msg_id,
            "from": from_addr,
            "subject": subject,
            "body": body,
            "date": date,
            "raw_message": msg
        }

    def mark_as_read(self, msg_id: str):
        """Mark email as read"""
        try:
            self.server.store(msg_id, '+FLAGS', '\\Seen')
            logger.info(f"Marked email {msg_id} as read")
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")


def fetch_unread_emails(folder: str = "INBOX") -> List[Dict]:
    """Convenience wrapper to fetch unread emails with automatic connect/disconnect."""
    receiver = EmailReceiver()
    if not _has_imap_config():
        logger.warning("IMAP configuration missing. No emails fetched.")
        return []
    try:
        receiver.connect()
        return receiver.fetch_emails(folder=folder, unread_only=PROCESS_UNSEEN_ONLY)
    finally:
        receiver.disconnect()


# Example usage
if __name__ == "__main__":
    receiver = EmailReceiver()
    receiver.connect()
    
    emails = receiver.fetch_emails(unread_only=True)
    
    for email_obj in emails:
        print(f"\n{'='*60}")
        print(f"From: {email_obj['from']}")
        print(f"Subject: {email_obj['subject']}")
        print(f"Body: {email_obj['body'][:200]}...")
    
    receiver.disconnect()
