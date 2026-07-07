Create Ansible Playbook for: ${1}
Target host group: ${2}
Target OS: ${3}
# ${3} 예시: ubuntu22/rocky9/windows/mixed(OS별 분기 필요)
# mixed 지정 시 ansible_os_family 기반 when 조건 자동 생성

Requirements: idempotent / vault for secrets / explicit file mode / handler for service restart
Edge cases: default filter for undefined vars / retries+until+delay for network / block+rescue for rollback / disk+permission pre-check / --check compatible
OS branch: if ${3}=mixed → when: ansible_os_family / apt+dnf+yum 분기 / service name diff(ssh vs sshd)
OS branch: if ${3}=windows → ansible_connection=ssh+shell_type=powershell or winrm / win_shell+win_command+win_package+win_service+win_file / chcp 65001 for UTF-8 / administrators_authorized_keys for SSH auth

Output: Korean, directory structure(if roles) + playbook + vars/defaults example + run command
