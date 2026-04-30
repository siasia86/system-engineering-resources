# Work Rules

## 1. Confirm before action
Print task summary before execution. format: "수행할 작업: - [item]"

## 2. Dangerous operations
terraform apply, infra changes, service restart, deploy → ask "진행할까요?" before execution

## 3. Delete operations
List targets → show impact → confirm before proceeding

## 4. Markdown rules
- diagram: ASCII art (`+`, `-`, `|`)
- tree: use `├──`, `└──`, `│` style
- table: align columns considering Korean character width (vi vertical alignment)
- output language: Korean

## 5. Naming convention
format: `[env]-[category]-[service]-[detail]`
env: dev / qa / stg / prd
ex: prd-app-web-frontend, dev-db-rds-postgresql

## 6. Symbols
Allowed: ✅ ❌ ⚠️ 🟢 🟡 🔴 ★★☆☆☆ 
No other emojis allowed (no decorative emojis)

## 7. sudo
Use sudo for file operations under /root/

## 8. Code changes
- Minimal change principle (modify only requested scope)
- Write test code only when explicitly requested
- Never hardcode secret keys

## 10. Example credentials (placeholder only)
Use the following standard placeholders for example passwords/keys in code and docs:
- username:  `Secureuser123`
- password:  `SecurePassword123`
- key/secret: `SecureKey123`
- token:     `SecureToken123`
- db name:   `SecureDbName123`
- domain:    `example.com` / `db.example.com`
- email:     `user@example.com`
- IP:        `192.0.2.1` (RFC 5737 documentation range)
- S3 bucket: `my-bucket`

## 9. Response style
- Concise and direct answers
- Skip unnecessary praise/agreement
- Politely correct wrong information

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-09

**마지막 업데이트**: 2026-04-09

© 2026 siasia86. Licensed under CC BY 4.0.
