"""
AI-based email classification using LLM.
Supports OpenAI GPT models or rule-based classification.
"""

from typing import Tuple
from config import (
    EMAIL_CATEGORIES,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    LLM_MODEL,
    CLASSIFIER_SYSTEM_PROMPT,
)
import logging
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailClassifier:
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.categories = EMAIL_CATEGORIES
        self.client = None
        self.legacy_openai = None

        if use_llm:
            self._init_openai_client()

    def _init_openai_client(self):
        if not OPENAI_API_KEY:
            logger.warning("⚠️  OPENAI_API_KEY missing, falling back to rule-based classification")
            self.use_llm = False
            return

        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL or None)
            logger.info("✅ OpenAI LLM initialized (v1 client)")
            return
        except Exception:
            pass

        try:
            import openai

            openai.api_key = OPENAI_API_KEY
            self.legacy_openai = openai
            logger.info("✅ OpenAI LLM initialized (legacy client)")
        except ImportError:
            logger.warning("⚠️  OpenAI not installed, falling back to rule-based classification")
            self.use_llm = False

    def classify(self, subject: str, body: str) -> Tuple[str, float]:
        if self.use_llm:
            return self._classify_with_llm(subject, body)
        return self._classify_rule_based(subject, body)

    def _extract_json(self, raw_text: str):
        if not raw_text:
            raise ValueError("empty response")
        text = raw_text.strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, flags=re.IGNORECASE)
        if fenced:
            return json.loads(fenced.group(1))

        brace = re.search(r"(\{[\s\S]*\})", text)
        if brace:
            return json.loads(brace.group(1))

        raise ValueError(f"No JSON object found in model response: {text[:160]}")

    def _classify_with_llm(self, subject: str, body: str) -> Tuple[str, float]:
        try:
            prompt = f"""Classify the following customer support email into ONE of these categories:
{', '.join(self.categories)}

Email Subject: {subject}
Email Body: {body}

Return strict JSON only:
{{"category": "CATEGORY_NAME", "confidence": 0.95}}
"""

            if self.client is not None:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=120,
                )
                content = response.choices[0].message.content
            elif self.legacy_openai is not None:
                response = self.legacy_openai.ChatCompletion.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=120,
                )
                content = response.choices[0].message.content
            else:
                raise RuntimeError("OpenAI client not initialized")

            result = self._extract_json(content)
            category = str(result.get("category", "Other"))
            confidence = float(result.get("confidence", 0.5))

            if category not in self.categories:
                category = "Other"

            return category, confidence

        except Exception as e:
            logger.error(f"LLM classification failed: {e}, falling back to rule-based")
            return self._classify_rule_based(subject, body)

    def _classify_rule_based(self, subject: str, body: str) -> Tuple[str, float]:
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
