# 使用说明（连接真实邮箱 & 数据库配置）

本项目支持连接真实邮箱（IMAP 收件 + SMTP 发件），并将审阅记录同时输出为 CSV 与 SQLite 数据库，方便上线前验证与追踪。

## 1) 真实邮箱配置（IMAP/SMTP）

请设置以下环境变量（建议写入 `.env` 或部署环境变量）：

- `IMAP_SERVER`：IMAP 服务器地址（例如 `imap.exmail.qq.com`）
- `IMAP_PORT`：IMAP 端口（默认 993）
- `IMAP_USE_SSL`：是否使用 SSL（`true/false`）
- `SMTP_SERVER`：SMTP 服务器地址（例如 `smtp.exmail.qq.com`）
- `SMTP_PORT`：SMTP 端口（默认 587）
- `SMTP_USE_TLS`：是否使用 TLS（`true/false`）
- `EMAIL_ADDRESS`：邮箱地址
- `EMAIL_APP_PASSWORD`：邮箱应用专用密码/授权码

配置完成后直接运行：

```bash
python main.py
```

## 2) 数据库放在哪里？

默认使用 SQLite，路径为：

```
data/aftersale.db
```

你可以通过 `SQLITE_DB_PATH` 指定其他位置，例如：

```bash
export SQLITE_DB_PATH=/var/lib/aftersale/aftersale.db
```

> 注意：程序会自动创建数据库目录（如果不存在）。

## 3) 售后回复模板 + 语气要求

你可以通过环境变量自定义售后模板与语气：

- `REPLY_TEMPLATE`：售后模板（支持占位符）
- `TONE_GUIDANCE`：语气要求（如 `专业、友好、耐心`）
- `DEFAULT_SIGNATURE`：署名（默认 `Customer Support Team`）

### 模板占位符

模板支持以下占位符：

- `{category}`：分类
- `{subject}`：主题
- `{body}`：原文内容（截取部分）
- `{from}`：发件人
- `{date}`：邮件时间
- `{signature}`：署名

示例（多行模板可用 `\n`）：

```bash
export REPLY_TEMPLATE="您好，感谢您的来信。\n我们已收到您的 {category} 相关问题，并正在处理中。\n如需补充信息，我们会进一步联系您。\n此致\n{signature}"
export TONE_GUIDANCE="温和、专业、简洁"
export DEFAULT_SIGNATURE="售后支持团队"
```

如需启用大模型改写，请配置 `OPENAI_API_KEY`，并可指定：

```bash
export LLM_MODEL=gpt-4o-mini
```

## 4) 审阅输出

- CSV：`review_output/` 目录
- SQLite：`data/aftersale.db`（或自定义路径）

## 5) 我应该怎么测试？

建议按下面 3 步走：

### A. 先做本地冒烟测试（不连真实邮箱）

确保你**没有**配置 `IMAP_SERVER` / `EMAIL_ADDRESS` / `EMAIL_APP_PASSWORD`，程序会自动使用内置 demo 邮件：

```bash
python main.py
```

运行成功后应看到：

- 控制台打印 3 封 demo 邮件的分类与建议回复
- 生成 `review_output/email_review_*.csv`
- 生成 `data/aftersale.db`

可用下面命令验证数据库是否写入：

```bash
python - <<'PY'
import sqlite3
conn = sqlite3.connect('data/aftersale.db')
count = conn.execute('select count(*) from email_reviews').fetchone()[0]
print('email_reviews rows =', count)
conn.close()
PY
```

### B. 再做模板/语气测试

设置你的售后模板和语气后再执行一次：

```bash
export REPLY_TEMPLATE="您好，感谢来信。我们已收到您的 {category} 问题，会尽快处理。\n此致\n{signature}"
export TONE_GUIDANCE="真诚、专业、简洁"
export DEFAULT_SIGNATURE="售后服务团队"
python main.py
```

检查新生成 CSV 的 `suggested_reply` 字段是否符合你的模板和语气预期。

### C. 最后做真实邮箱联调测试

配置 IMAP/SMTP 和应用密码后执行：

```bash
export IMAP_SERVER=imap.exmail.qq.com
export IMAP_PORT=993
export IMAP_USE_SSL=true
export SMTP_SERVER=smtp.exmail.qq.com
export SMTP_PORT=587
export SMTP_USE_TLS=true
export EMAIL_ADDRESS=your_email@example.com
export EMAIL_APP_PASSWORD=your_app_password
python main.py
```

联调建议：

1. 先给这个邮箱发 1~2 封测试邮件（不同类型：技术问题、账单问题）。
2. 运行后只检查 CSV/数据库，不要立刻自动发送。
3. 人工确认 `category`、`confidence`、`suggested_reply` 后再接入发送流程。

## 6) 网页方式运行（无需手工敲一堆命令）

如果你希望通过网页输入配置并直接运行：

```bash
python web_app.py
```

打开浏览器访问：

```text
http://127.0.0.1:8000
```

你可以在页面中填写：

- 真实邮箱 IMAP/SMTP 配置
- 数据库路径（`SQLITE_DB_PATH`）
- 售后模板（`REPLY_TEMPLATE`）
- 语气要求（`TONE_GUIDANCE`）
- 模型和 API Key
- 中转 API 地址（`OPENAI_BASE_URL`，例如 `https://poloai.top/v1`）
- 流水线超时时间（`PIPELINE_TIMEOUT_SECONDS`，默认 300 秒）

你可以按这个顺序操作：

1. 点击“先测试邮箱连接”验证 IMAP/SMTP 与账号密码。
2. 点击“测试 API Key / 模型”验证中转 API 地址、Key、模型名是否可用。
3. 最后点击“运行流水线”。

页面会直接显示：

- 运行是否成功
- CSV 输出路径
- 数据库文件是否创建
- 完整运行日志

如果页面显示 `Pipeline execution timed out`，通常不是“没有本地路径”，而是本次运行超过了超时秒数。
可在页面把 `PIPELINE_TIMEOUT_SECONDS` 调大（例如 600）后重试。

## 7) Windows PowerShell 用户注意

你报的这个错：

```text
bash : 无法将“bash”项识别为 cmdlet ...
```

说明你在 **PowerShell** 里输入了 `bash`，但机器上没有安装/启用 bash。
本项目不要求必须用 bash，直接在 PowerShell 执行 Python 命令即可。

PowerShell 示例：

```powershell
$env:IMAP_SERVER = "imap.exmail.qq.com"
$env:IMAP_PORT = "993"
$env:IMAP_USE_SSL = "true"
$env:SMTP_SERVER = "smtp.exmail.qq.com"
$env:SMTP_PORT = "587"
$env:SMTP_USE_TLS = "true"
$env:EMAIL_ADDRESS = "your_email@example.com"
$env:EMAIL_APP_PASSWORD = "your_app_password"
$env:OPENAI_API_KEY = "sk-..."
$env:OPENAI_BASE_URL = "https://poloai.top/v1"
$env:LLM_MODEL = "gpt-4o-mini"
python main.py
```

如果你使用网页方式，也只需要：

```powershell
python web_app.py
```

然后打开 `http://127.0.0.1:8000`。


## 8) 售后情况库（aftersale_situation_library）

系统会在首次初始化数据库时，自动把你提供的售后场景模板写入表 `aftersale_situation_library`。

可用下面命令查看数量与示例：

```bash
python - <<'PY'
import sqlite3
conn = sqlite3.connect('data/aftersale.db')
count = conn.execute('select count(*) from aftersale_situation_library').fetchone()[0]
print('scenario rows =', count)
rows = conn.execute("select scenario_key, title from aftersale_situation_library order by id limit 5").fetchall()
for r in rows:
    print(r)
conn.close()
PY
```

后续你可以继续新增/更新场景（按 `scenario_key` 幂等更新）：

```bash
python - <<'PY'
from review_database import ReviewDatabase

db = ReviewDatabase()
db.add_situation_template(
    scenario_key="custom_case_x",
    tags="#自定义,#测试",
    language="zh",
    title="自定义售后场景",
    reply_template="您好，这是新的售后模板内容。",
)
print("done")
PY
```
