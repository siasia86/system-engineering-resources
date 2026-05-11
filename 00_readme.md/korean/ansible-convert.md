아래 쉘 스크립트를 Ansible Playbook으로 변환해줘:

@${1}

## 변환 규칙
- shell/command 대신 전용 모듈 사용 (apt, yum, copy, template, systemd 등)
- 조건문 → when 절로 변환
- 반복문 → loop로 변환
- 하드코딩 값 → 변수로 추출
- 서비스 재시작 → handler 분리
- 에러 처리 → block/rescue 적용

## 엣지케이스 처리
- 스크립트의 exit code 분기 → failed_when/changed_when
- 파이프라인 명령 → 단계별 task 분리 또는 shell + set -o pipefail
- 임시 파일 사용 → 정리 task 추가 (always 블록)
- OS별 분기 → ansible_os_family when 조건
- 이미 적용된 상태에서 재실행 → idempotent 보장

변환 전/후 비교표도 보여줘.
