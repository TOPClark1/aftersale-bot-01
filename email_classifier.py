"""
AI-based email classification using LLM.
Supports OpenAI GPT models or rule-based classification.
"""

from typing import Dict, Tuple
from config import EMAIL_CATEGORIES, OPENAI_API_KEY, LLM_MODEL
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailClassifier:
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.categories = EMAIL_CATEGORIES
        
        if use_llm:
            try:
                import openai
                openai.api_key = OPENAI_API_KEY
                self.openai = openai
                logger.info("✅ OpenAI LLM initialized")
            except ImportError:
                logger.warning("⚠️  OpenAI not installed, falling back to rule-based classification")
                self.use_llm = False

    def classify(self, subject: str, body: str) -> Tuple[str, float]:
        """
        Classify email into a category
        
        Args:
            subject: Email subject
            body: Email body
        
        Returns:
            Tuple of (category, confidence_score)
        """
        if self.use_llm:
            return self._classify_with_llm(subject, body)
        else:
            return self._classify_rule_based(subject, body)

    def _classify_with_llm(self, subject: str, body: str) -> Tuple[str, float]:
        """Classify using OpenAI GPT"""
        try:
            prompt = f"""Classify the following customer support email into ONE of these categories:
{', '.join(self.categories)}

Email Subject: {subject}
Email Body: {body}

Respond in JSON format:
{{"category": "CATEGORY_NAME", "confidence": 0.95}}
"""
            
            response = self.openai.ChatCompletion.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a customer support email classifier. Respond only in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            result = json.loads(response.choices[0].message.content)
            category = result.get("category", "Other")
            confidence = result.get("confidence", 0.5)
            
            if category not in self.categories:
                category = "Other"
            
            return category, confidence
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}, falling back to rule-based")
            return self._classify_rule_based(subject, body)

    def _classify_rule_based(self, subject: str, body: str) -> Tuple[str, float]:
        """Simple rule-based classification"""
        combined_text = (subject + " " + body).lower()
        
        rules = {
            "Technical Issue": ["error", "bug", "crash", "not working", "broken", "issue", "problem"],
            "Billing & Payment": ["invoice", "payment", "billing", "subscription", "charge", "refund", "price"],
            "Product Inquiry": ["what is", "how does", "tell me about", "specifications", "features"],
            "Feature Request": ["feature request", "request", "add", "implement", "could you", "would like"],
        }
        
        scores = {}
        for category, keywords in rules.items():
            score = sum(combined_text.count(keyword) for keyword in keywords)
            scores[category] = score
        
        if max(scores.values()) > 0:
            category = max(scores, key=scores.get)
            confidence = min(0.7, max(scores.values()) * 0.1)
        else:
            category = "Other"
            confidence = 0.3
        
        return category, confidence


# Example usage
if __name__ == "__main__":
    classifier = EmailClassifier(use_llm=False)  # Set to True if OpenAI API key available
    
    test_emails = [
        ("Login Error", "I can't log into my account. I get an error message every time I try."),
        ("Invoice Question", "Can you send me a copy of my invoice from last month?"),
        ("New Feature Idea", "Could you add a dark mode to your app?"),
    ]
    
    for subject, body in test_emails:
        category, confidence = classifier.classify(subject, body)
        print(f"Subject: {subject}")
        print(f"  → Category: {category} (confidence: {confidence:.2f})\n")
