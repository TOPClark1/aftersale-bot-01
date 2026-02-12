"""Simple web UI for configuring and running the after-sale pipeline (stdlib only)."""

import html
import imaplib
import os
import re
import smtplib
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = "data/aftersale.db"
PORT = 8000


def _build_env_from_form(form):
    env = os.environ.copy()
    keys = [
        "IMAP_SERVER",
        "IMAP_PORT",
        "IMAP_USE_SSL",
        "SMTP_SERVER",
        "SMTP_PORT",
        "SMTP_USE_TLS",
        "EMAIL_ADDRESS",
        "EMAIL_APP_PASSWORD",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "LLM_MODEL",
        "SQLITE_DB_PATH",
        "REPLY_TEMPLATE",
        "TONE_GUIDANCE",
        "DEFAULT_SIGNATURE",
    ]
    for key in keys:
        value = form.get(key, "").strip()
        if value:
            env[key] = value
        else:
            env.pop(key, None)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def _extract_csv_path(log_text: str):
    match = re.search(r"Review CSV generated:\s*(\S+)", log_text)
    return match.group(1) if match else ""


def _get_env_bool(env: dict, name: str, default: bool = False) -> bool:
    value = env.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _test_mail_connections(env: dict):
    imap_server = env.get("IMAP_SERVER", "")
    imap_port = int(env.get("IMAP_PORT", "993"))
    imap_use_ssl = _get_env_bool(env, "IMAP_USE_SSL", True)
    smtp_server = env.get("SMTP_SERVER", "")
    smtp_port = int(env.get("SMTP_PORT", "587"))
    smtp_use_tls = _get_env_bool(env, "SMTP_USE_TLS", True)
    email_address = env.get("EMAIL_ADDRESS", "")
    app_password = env.get("EMAIL_APP_PASSWORD", "")

    missing = []
    for key, val in {
        "IMAP_SERVER": imap_server,
        "SMTP_SERVER": smtp_server,
        "EMAIL_ADDRESS": email_address,
        "EMAIL_APP_PASSWORD": app_password,
    }.items():
        if not val:
            missing.append(key)
    if missing:
        return False, f"缺少必要配置：{', '.join(missing)}"

    logs = []
    ok = True

    try:
        if imap_use_ssl:
            imap_conn = imaplib.IMAP4_SSL(imap_server, imap_port, timeout=20)
        else:
            imap_conn = imaplib.IMAP4(imap_server, imap_port, timeout=20)
        imap_conn.login(email_address, app_password)
        imap_conn.logout()
        logs.append(f"✅ IMAP 连接成功：{imap_server}:{imap_port}")
    except Exception as exc:
        ok = False
        logs.append(f"❌ IMAP 连接失败：{exc}")

    try:
        smtp_conn = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
        if smtp_use_tls:
            smtp_conn.starttls()
        smtp_conn.login(email_address, app_password)
        smtp_conn.quit()
        logs.append(f"✅ SMTP 连接成功：{smtp_server}:{smtp_port}")
    except Exception as exc:
        ok = False
        logs.append(f"❌ SMTP 连接失败：{exc}")

    return ok, "\n".join(logs)


def _render_page(values=None, result=None, log_output=""):
    values = values or {}

    def field(name, default=""):
        return html.escape(values.get(name, default), quote=True)

    status_html = ""
    if result:
        cls = "ok" if result["ok"] else "fail"
        status = "成功" if result["ok"] else "失败"
        action_name = "运行流水线" if result.get("action") == "run_pipeline" else "连接测试"
        status_html = f"""
        <div class="result {cls}">
          <strong>{action_name}{status}</strong><br>
          return_code: {result['return_code']}<br>
          CSV: {html.escape(result['csv_path'] or '未识别到输出路径')}<br>
          DB: {html.escape(result['db_path'])}（{'存在' if result['db_exists'] else '未创建'}）
        </div>
        <h3>运行日志</h3>
        <pre>{html.escape(log_output)}</pre>
        """

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>售后邮件助手配置页</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f7fb; color: #1f2937; }}
    .container {{ max-width: 980px; margin: 24px auto; padding: 0 16px 40px; }}
    h1 {{ font-size: 26px; margin-bottom: 8px; }}
    .desc {{ color: #4b5563; margin-bottom: 20px; }}
    form {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px 16px; }}
    .full {{ grid-column: 1 / -1; }}
    label {{ display: block; font-weight: 600; margin-bottom: 6px; font-size: 14px; }}
    input, textarea, select {{ width: 100%; border: 1px solid #d1d5db; border-radius: 8px; padding: 10px; font-size: 14px; box-sizing: border-box; }}
    textarea {{ min-height: 90px; resize: vertical; }}
    .btn {{ margin-top: 16px; background: #2563eb; color: #fff; border: none; border-radius: 8px; padding: 12px 16px; cursor: pointer; font-size: 15px; margin-right: 8px; }}
    .btn:hover {{ background: #1d4ed8; }}
    .result {{ margin-top: 18px; padding: 14px; border-radius: 8px; }}
    .ok {{ background: #ecfdf5; border: 1px solid #10b981; }}
    .fail {{ background: #fef2f2; border: 1px solid #ef4444; }}
    pre {{ background: #0b1020; color: #dbeafe; border-radius: 8px; padding: 12px; overflow: auto; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>售后邮件助手 - 网页配置与运行</h1>
    <p class="desc">在这里填写邮箱、数据库、模板和语气要求。建议先测试邮箱连接，再运行流水线。</p>

    <form method="post">
      <div class="grid">
        <div><label>IMAP_SERVER</label><input name="IMAP_SERVER" value="{field('IMAP_SERVER')}" placeholder="imap.exmail.qq.com"></div>
        <div><label>IMAP_PORT</label><input name="IMAP_PORT" value="{field('IMAP_PORT', '993')}"></div>
        <div><label>IMAP_USE_SSL</label><select name="IMAP_USE_SSL"><option value="true">true</option><option value="false" {'selected' if field('IMAP_USE_SSL','true')=='false' else ''}>false</option></select></div>
        <div><label>SMTP_SERVER</label><input name="SMTP_SERVER" value="{field('SMTP_SERVER')}" placeholder="smtp.exmail.qq.com"></div>
        <div><label>SMTP_PORT</label><input name="SMTP_PORT" value="{field('SMTP_PORT', '587')}"></div>
        <div><label>SMTP_USE_TLS</label><select name="SMTP_USE_TLS"><option value="true">true</option><option value="false" {'selected' if field('SMTP_USE_TLS','true')=='false' else ''}>false</option></select></div>
        <div><label>EMAIL_ADDRESS</label><input name="EMAIL_ADDRESS" value="{field('EMAIL_ADDRESS')}" placeholder="your@email.com"></div>
        <div><label>EMAIL_APP_PASSWORD</label><input type="password" name="EMAIL_APP_PASSWORD" value="{field('EMAIL_APP_PASSWORD')}"></div>
        <div><label>OPENAI_API_KEY (可选)</label><input type="password" name="OPENAI_API_KEY" value="{field('OPENAI_API_KEY')}"></div>
        <div><label>OPENAI_BASE_URL (可选)</label><input name="OPENAI_BASE_URL" value="{field('OPENAI_BASE_URL')}" placeholder="https://poloai.top/v1"></div>
        <div><label>LLM_MODEL</label><input name="LLM_MODEL" value="{field('LLM_MODEL', 'gpt-4o-mini')}"></div>
        <div class="full"><label>SQLITE_DB_PATH</label><input name="SQLITE_DB_PATH" value="{field('SQLITE_DB_PATH', DEFAULT_DB_PATH)}"></div>
        <div class="full"><label>TONE_GUIDANCE</label><input name="TONE_GUIDANCE" value="{field('TONE_GUIDANCE', '专业、友好、耐心')}"></div>
        <div class="full"><label>DEFAULT_SIGNATURE</label><input name="DEFAULT_SIGNATURE" value="{field('DEFAULT_SIGNATURE', 'Customer Support Team')}"></div>
        <div class="full">
          <label>REPLY_TEMPLATE (可选，支持 {html.escape('{category}/{subject}/{body}/{from}/{date}/{signature}')}</label>
          <textarea name="REPLY_TEMPLATE">{html.escape(values.get('REPLY_TEMPLATE', ''))}</textarea>
        </div>
      </div>
      <button class="btn" type="submit" name="action" value="test_connection">先测试邮箱连接</button>
      <button class="btn" type="submit" name="action" value="run_pipeline">运行流水线</button>
    </form>
    {status_html}
  </div>
</body>
</html>"""


class AppHandler(BaseHTTPRequestHandler):
    def _send_html(self, body: str):
        content = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        self._send_html(_render_page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        data = {k: v[0] for k, v in parse_qs(raw).items()}

        action = data.get("action", "run_pipeline")
        env = _build_env_from_form(data)
        db_path = env.get("SQLITE_DB_PATH", DEFAULT_DB_PATH)

        if action == "test_connection":
            ok, log_output = _test_mail_connections(env)
            result = {
                "ok": ok,
                "return_code": 0 if ok else 1,
                "csv_path": "",
                "db_path": db_path,
                "db_exists": (ROOT_DIR / db_path).exists(),
                "action": action,
            }
        else:
            try:
                completed = subprocess.run(
                    [sys.executable, "main.py"],
                    cwd=ROOT_DIR,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
                log_output = (completed.stdout + "\n" + completed.stderr).strip()
                result = {
                    "ok": completed.returncode == 0,
                    "return_code": completed.returncode,
                    "csv_path": _extract_csv_path(log_output),
                    "db_path": db_path,
                    "db_exists": (ROOT_DIR / db_path).exists(),
                    "action": action,
                }
            except subprocess.TimeoutExpired:
                log_output = "Pipeline execution timed out (120s)."
                result = {
                    "ok": False,
                    "return_code": -1,
                    "csv_path": "",
                    "db_path": db_path,
                    "db_exists": False,
                    "action": action,
                }

        self._send_html(_render_page(values=data, result=result, log_output=log_output))


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), AppHandler)
    print(f"Web UI running at http://127.0.0.1:{PORT}")
    server.serve_forever()
