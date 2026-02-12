"""Feishu integrations: bot webhook and optional table webhook."""

import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class FeishuClient:
    def __init__(self, bot_webhook: str = "", table_webhook: str = ""):
        self.bot_webhook = (bot_webhook or "").strip()
        self.table_webhook = (table_webhook or "").strip()

    def send_bot_text(self, text: str) -> bool:
        if not self.bot_webhook:
            return False
        payload = {"msg_type": "text", "content": {"text": text}}
        return self._post_json(self.bot_webhook, payload)

    def append_table_rows(self, rows):
        if not self.table_webhook:
            return False
        payload = {"rows": rows}
        return self._post_json(self.table_webhook, payload)

    def _post_json(self, url: str, payload: dict) -> bool:
        req = Request(
            url=url,
            method="POST",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        )
        try:
            with urlopen(req, timeout=20) as resp:
                _ = resp.read()
            return True
        except (HTTPError, URLError, Exception):
            return False
