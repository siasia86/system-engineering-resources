Convert shell script to Ansible Playbook: @${1}

Rules: dedicated modules over shell/command / conditionals→when / loops→loop / hardcoded→vars / service restart→handler / error→block/rescue
Edge cases: exit code→failed_when/changed_when / pipeline→split tasks or shell+pipefail / temp files→always cleanup / OS branch→ansible_os_family / idempotent on rerun

Output: Korean, include before/after comparison table
