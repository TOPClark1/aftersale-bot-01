"""
Generate intelligent email replies based on classification and history
"""

from typing import Dict
from config import OPENAI_API_KEY, LLM_MODEL, REPLY_TEMPLATE, TONE_GUIDANCE, DEFAULT_SIGNATURE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReplyGenerator:
    def __init__(self):
        self.use_llm = bool(OPENAI_API_KEY)
        self.custom_template = REPLY_TEMPLATE.strip()
        self.client = None
        self.legacy_openai = None
        self._init_openai_client()

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
Customer Support Team""",
        }

    def _init_openai_client(self):
        if not self.use_llm:
            return
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✅ OpenAI reply generator initialized (v1 client)")
            return
        except Exception:
            pass
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            self.legacy_openai = openai
            logger.info("✅ OpenAI reply generator initialized (legacy client)")
        except ImportError:
            logger.warning("⚠️ OpenAI not installed, fallback to template reply")
            self.use_llm = False

    def generate_reply(self, email_obj: Dict, category: str, use_llm: bool = False) -> str:
        if use_llm and self.use_llm:
            return self._generate_with_llm(email_obj, category)
        return self._get_template(category, email_obj)

    def _generate_with_llm(self, email_obj: Dict, category: str) -> str:
        try:
            template_hint = ""
            if self.custom_template:
                template_hint = (
                    "\n请遵循以下售后模板（可根据内容微调，但保持结构与关键措辞）：\n"
                    f"{self.custom_template}\n"
                )

            prompt = (
                "请生成一封专业、友好且贴合语气要求的售后回复邮件。\n"
                f"客户分类：{category}\n"
                f"原始主题：{email_obj.get('subject', '')}\n"
                f"原始内容：{email_obj.get('body', '')[:500]}\n"
                f"{template_hint}"
                "要求：\n"
                "1. 简洁清晰，2-4 句为宜\n"
                "2. 表达感谢并确认问题\n"
                "3. 告知下一步处理（例如处理时效或需要的补充信息）\n"
                f"4. 语气要求：{TONE_GUIDANCE}\n"
                f"5. 署名使用：{DEFAULT_SIGNATURE}\n"
            )

            if self.client is not None:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "你是专业的售后客服，写作风格稳重、友好、可信。"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=200,
                )
                return response.choices[0].message.content or self._get_template(category, email_obj)

            if self.legacy_openai is not None:
                response = self.legacy_openai.ChatCompletion.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "你是专业的售后客服，写作风格稳重、友好、可信。"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=200,
                )
                return response.choices[0].message.content

            raise RuntimeError("OpenAI client not initialized")

        except Exception as e:
            logger.error(f"LLM reply generation failed: {e}")
            return self._get_template(category, email_obj)

    def _get_template(self, category: str, email_obj: Dict) -> str:
        if self.custom_template:
            return self._render_template(self.custom_template, email_obj, category)
        return self.templates.get(category, self.templates["Other"])

    def _render_template(self, template: str, email_obj: Dict, category: str) -> str:
        safe_values = {
            "category": category,
            "subject": email_obj.get("subject", ""),
            "body": email_obj.get("body", ""),
            "from": email_obj.get("from", ""),
            "date": email_obj.get("date", ""),
            "signature": DEFAULT_SIGNATURE,
        }
        return template.format_map(_SafeDict(safe_values))


class _SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def generate_reply(email_obj: Dict, category: str, confidence: float = None, use_llm: bool = False):
    generator = ReplyGenerator()
    reply = generator.generate_reply(email_obj, category, use_llm=use_llm)
    risk_flag = category == "Other" or (confidence is not None and confidence < 0.6)
    return reply, risk_flag


if __name__ == "__main__":
    generator = ReplyGenerator()

    test_email = {
        "subject": "Cannot log in",
        "body": "I've been trying to log in for an hour but I keep getting an error.",
        "from": "customer@example.com",
    }

    reply = generator.generate_reply(test_email, "Technical Issue", use_llm=False)
    print("Generated Reply:")
    print(reply)
