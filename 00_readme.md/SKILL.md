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

## 9. Response style
- Concise and direct answers
- Skip unnecessary praise/agreement
- Politely correct wrong information
