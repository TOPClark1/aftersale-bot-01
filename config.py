import os


def _get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


IMAP_SERVER = os.getenv("IMAP_SERVER", "")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USE_SSL = _get_env_bool("IMAP_USE_SSL", True)
SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USE_TLS = _get_env_bool("SMTP_USE_TLS", True)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
PROCESS_UNSEEN_ONLY = _get_env_bool("PROCESS_UNSEEN_ONLY", True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

EMAIL_CATEGORIES = [
    "Technical Issue",
    "Billing & Payment",
    "Product Inquiry",
    "Feature Request",
    "Other",
]

CSV_OUTPUT_DIR = os.getenv("CSV_OUTPUT_DIR", "review_output")
DATA_DIR = os.getenv("DATA_DIR", "data")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", os.path.join(DATA_DIR, "aftersale.db"))

REPLY_TEMPLATE = os.getenv("REPLY_TEMPLATE", "")
TONE_GUIDANCE = os.getenv("TONE_GUIDANCE", "专业、友好、耐心")
DEFAULT_SIGNATURE = os.getenv("DEFAULT_SIGNATURE", "Customer Support Team")

MARK_AS_READ_AFTER_PROCESS = _get_env_bool("MARK_AS_READ_AFTER_PROCESS", False)

# Prompt knobs (edit these to iterate prompt strategy)
CLASSIFIER_SYSTEM_PROMPT = os.getenv(
    "CLASSIFIER_SYSTEM_PROMPT",
    "You are a customer support email classifier. Respond only with strict JSON.",
)
REPLY_SYSTEM_PROMPT = os.getenv(
    "REPLY_SYSTEM_PROMPT",
    "You are a professional after-sales support agent.",
)
REPLY_LANGUAGE = os.getenv("REPLY_LANGUAGE", "en")

FEISHU_BOT_WEBHOOK = os.getenv("FEISHU_BOT_WEBHOOK", "")
FEISHU_TABLE_WEBHOOK = os.getenv("FEISHU_TABLE_WEBHOOK", "")
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR", "archive_reports")
