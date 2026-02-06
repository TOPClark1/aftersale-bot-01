"""
Generate daily CSV for human review before sending replies
"""

import csv
import os
from datetime import datetime
from typing import List, Dict
from config import CSV_OUTPUT_DIR
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewManager:
    def __init__(self):
        self.output_dir = CSV_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_review_csv(self, email_reviews: List[Dict]) -> str:
        """
        Generate CSV file for daily email review
        
        Args:
            email_reviews: List of email review dictionaries
        
        Returns:
            Path to generated CSV file
        """
        
        if not email_reviews:
            logger.warning("No emails to review")
            return None
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"email_review_{timestamp}.csv")
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'email_id',
                    'from',
                    'subject',
                    'category',
                    'confidence',
                    'original_body',
                    'suggested_reply',
                    'status',  # pending_review, approved, rejected
                    'reviewer_notes',
                    'received_date'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for review in email_reviews:
                    writer.writerow({
                        'email_id': review.get('id', ''),
                        'from': review.get('from', ''),
                        'subject': review.get('subject', ''),
                        'category': review.get('category', ''),
                        'confidence': review.get('confidence', ''),
                        'original_body': review.get('body', '')[:500],  # First 500 chars
                        'suggested_reply': review.get('reply', ''),
                        'status': 'pending_review',
                        'reviewer_notes': '',
                        'received_date': review.get('date', '')
                    })
            
            logger.info(f"✅ Review CSV generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Failed to generate CSV: {e}")
            return None

    def read_review_csv(self, filepath: str) -> List[Dict]:
        """
        Read review CSV and return parsed data
        
        Args:
            filepath: Path to CSV file
        
        Returns:
            List of review dictionaries
        """
        reviews = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    reviews.append(row)
            
            logger.info(f"✅ Read {len(reviews)} reviews from {filepath}")
            return reviews
            
        except Exception as e:
            logger.error(f"❌ Failed to read CSV: {e}")
            return reviews

    def get_approved_replies(self, filepath: str) -> List[Dict]:
        """
        Get only approved emails from review CSV
        
        Args:
            filepath: Path to CSV file
        
        Returns:
            List of approved review dictionaries
        """
        all_reviews = self.read_review_csv(filepath)
        approved = [r for r in all_reviews if r.get('status').lower() == 'approved']
        
        logger.info(f"✅ Found {len(approved)} approved replies out of {len(all_reviews)}")
        return approved


# Example usage
if __name__ == "__main__":
    manager = ReviewManager()
    
    # Sample reviews
    sample_reviews = [
        {
            'id': '1',
            'from': 'customer1@example.com',
            'subject': 'Login Error',
            'body': 'I cannot log in to my account...',
            'category': 'Technical Issue',
            'confidence': 0.95,
            'reply': 'Thank you for reporting this. Our team will investigate...',
            'date': '2026-02-06 10:30'
        },
        {
            'id': '2',
            'from': 'customer2@example.com',
            'subject': 'Invoice Question',
            'body': 'Can I get a copy of my invoice?',
            'category': 'Billing & Payment',
            'confidence': 0.88,
            'reply': 'Of course! I will send your invoice shortly...',
            'date': '2026-02-06 11:00'
        }
    ]
    
    # Generate CSV
    csv_path = manager.generate_review_csv(sample_reviews)
    
    if csv_path:
        print(f"✅ CSV generated at: {csv_path}")
        # View content
        reviews = manager.read_review_csv(csv_path)
        for r in reviews:
            print(f"\n{r['subject']} - {r['category']}")