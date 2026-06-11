Cross-file consistency review (Ansible/Vagrant project) for @${1:directory}
# ${1} 생략 시: /opt/00_chobo_ansible 를 대상으로 삼을 것.

Extends `doc-consistency-review` with Ansible/Vagrant/Hyper-V specific checks.
Run base checks (version, path, date, status, links, cross-doc) first, then add:

Additional check items:
1. ip-consistency: IP in code constants (VMS dict) vs inventory.ini vs PLAN.md VM table vs README IP table
2. inventory-match: inventory.ini host entries vs VMS dict keys (vm-{name} pattern)
3. box-existence: PLAN status "✅ 빌드 완료" → verify .box file exists (SSH to Windows if needed)
4. issue-code-sync: PLAN.md issues with `수정 파일:` field — verify fix is present in that file
5. vm-state-match: PLAN status "✅ ping pong" → verify VM is Running (SSH to Windows: Get-VM)
6. python-script-syntax: all .py files in scripts/ pass `ast.parse()`

Edge case handling:
- SSH to Windows host 불가: checks 3, 5 → 🟡 skip (접근 불가 명시)
- 여러 PLAN.md 존재 시: 각각 독립 검증
- inventory.ini 없는 서브디렉토리: check 1, 2 skip
- 코드블록/인용구 내부 IP·경로: 검증 제외

Method:
- inventory.ini: grep ansible_host= lines → extract IP map
- VMS dict: grep pattern `"ip": "..."` in provision_vms.py
- box files: SSH to Windows → `Test-Path D:\Masang\VHD\boxes\*.box`
- VM state: SSH to Windows → `Get-VM | Select Name,State`

Output: Korean, ✅❌🟡 per item, show specific mismatches with file:line

Loop (max 3 iterations):
1. Run base doc-consistency-review checks
2. Run additional Ansible-specific checks
3. Fix all ❌/🟡 issues
4. Re-review
5. Repeat until clean or 3 iterations completed
6. Final summary: iterations run, issues fixed, remaining issues
