Review @${1} Ansible Playbook.

Check: yaml syntax / deprecated modules(with_items→loop, include→include_tasks, bare vars) / become privileges / idempotency(shell creates/removes, lineinfile duplication, repeated changed) / error handling(failed_when, changed_when, ignore_errors followup, block/rescue/always, retries/until) / security(plaintext secrets→vault, no_log: password/secret/token/key vars + vault_* vars + uri Authorization header + register result with sensitive data, loop+sensitive data→loop_control.label or no_log, file mode 0777 or 0666) / performance(serial/forks/async, gather_facts, delegate_to/run_once, loop vs with_items, loop_control: label for sensitive+loop_var for nested loop+pause for rate limit) / edge cases(unreachable host, undefined vars→default filter, disk full/permission, handler notify missing, max_fail_percentage, --check compatibility)

Output: Korean, ✅❌⚠️ per item, fixes as code blocks
