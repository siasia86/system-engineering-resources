Create Ansible Playbook for: ${1}
Target host group: ${2}

Requirements: idempotent / vault for secrets / explicit file mode / handler for service restart
Edge cases: default filter for undefined vars / retries+until+delay for network / block+rescue for rollback / disk+permission pre-check / --check compatible

Output: Korean, directory structure(if roles) + playbook + vars/defaults example + run command
