Review @${1} Ansible Playbook.

Check: yaml syntax / deprecated modules / become privileges / idempotency(shell creates/removes, lineinfile duplication, repeated changed) / error handling(failed_when, changed_when, ignore_errors followup, block/rescue/always, retries/until) / security(plaintext secrets→vault, no_log missing, file mode 0777) / performance(serial/forks/async, gather_facts, delegate_to/run_once, loop vs with_items) / edge cases(unreachable host, undefined vars→default filter, disk full/permission, handler notify missing, max_fail_percentage, --check compatibility)

Output: Korean, ✅❌⚠️ per item, fixes as code blocks
