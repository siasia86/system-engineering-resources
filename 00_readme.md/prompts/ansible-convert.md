Convert shell script to Ansible Playbook: @${1}
# ${1} 생략 시: 이 대화에서 가장 최근에 작업한 .sh 파일을 자동으로 대상으로 삼을 것.
# 최근 작업 파일이 불명확하면 "어떤 스크립트를 변환할까요?" 라고 물어볼 것.

Rules: dedicated modules over shell/command / conditionals→when / loops→loop / hardcoded→vars / service restart→handler / error→block/rescue
Edge cases: exit code→failed_when/changed_when / pipeline→split tasks or shell+pipefail / temp files→always cleanup / OS branch→ansible_os_family / idempotent on rerun

Output: Korean, include before/after comparison table
