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
