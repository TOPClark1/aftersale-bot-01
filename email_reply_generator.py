"""
Generate intelligent email replies based on classification and history
"""

from typing import Dict
from config import OPENAI_API_KEY, LLM_MODEL
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReplyGenerator:
    def __init__(self):
        self.use_llm = bool(OPENAI_API_KEY)
        
        # Template replies for each category
        self.templates = {
            "Technical Issue": """Thank you for reporting this issue. Our technical team has received your report and will investigate immediately. 

We typically respond to technical issues within 24 hours. In the meantime, if you have any workarounds or additional details, please reply to this email.

Best regards,
Customer Support Team""",
            
            "Billing & Payment": """Thank you for your inquiry. Our billing department will review your request and respond within 2 business hours.

For urgent billing matters, please contact us directly at [support phone].

Best regards,
Customer Support Team""",
            
            "Product Inquiry": """Thank you for your interest in our product! We're happy to help.

A product specialist will provide detailed information about your inquiry shortly.

Best regards,
Customer Support Team""",
            
            "Feature Request": """Thank you for the feature suggestion! We appreciate your feedback and will review your request with our product team.

We forward valuable user suggestions to our development team.

Best regards,
Customer Support Team""",
            
            "Other": """Thank you for contacting us. Our team will review your message and respond shortly.

Best regards,
Customer Support Team"""
        }

    def generate_reply(self, email_obj: Dict, category: str, use_llm: bool = False) -> str:
        """
        Generate a reply to an email
        
        Args:
            email_obj: Original email data
            category: Classified email category
            use_llm: Use LLM for personalized replies
        
        Returns:
            Reply text
        """
        
        if use_llm and self.use_llm:
            return self._generate_with_llm(email_obj, category)
        else:
            return self._get_template(category)

    def _generate_with_llm(self, email_obj: Dict, category: str) -> str:
        """Generate personalized reply using LLM"""
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            
            prompt = f"""Generate a professional, friendly customer support reply to this email.

Customer Category: {category}
Original Subject: {email_obj['subject']}
Original Message: {email_obj['body'][:500]}

Write a 2-3 sentence response that:
1. Thanks the customer
2. Acknowledges their {category.lower()}
3. Tells them next steps (e.g., "Our team will respond in 24 hours")

Keep it professional and warm."""
            
            response = openai.ChatCompletion.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful customer support agent. Write warm, professional replies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM reply generation failed: {e}")
            return self._get_template(category)

    def _get_template(self, category: str) -> str:
        """Get template reply for category"""
        return self.templates.get(category, self.templates["Other"])


def generate_reply(email_obj: Dict, category: str, confidence: float = None, use_llm: bool = False):
    """Convenience wrapper that returns reply text and a risk flag."""
    generator = ReplyGenerator()
    reply = generator.generate_reply(email_obj, category, use_llm=use_llm)
    risk_flag = category == "Other" or (confidence is not None and confidence < 0.6)
    return reply, risk_flag


# Example usage
if __name__ == "__main__":
    generator = ReplyGenerator()
    
    test_email = {
        "subject": "Cannot log in",
        "body": "I've been trying to log in for an hour but I keep getting an error.",
        "from": "customer@example.com"
    }
    
    reply = generator.generate_reply(test_email, "Technical Issue", use_llm=False)
    print("Generated Reply:")
    print(reply)
