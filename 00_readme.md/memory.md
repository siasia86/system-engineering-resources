# Memory

세션 간 유지해야 하는 핵심 정보를 기록합니다.

## 환경

| 항목 | 값 |
|------|------|
| Ansible 서버 | 10.200.90.155 (Linux, Python 3.14, kernel 6.8.0-124) |
| Hyper-V 호스트 | 10.200.101.101 (Windows 10 Pro) |
| Docker | 29.5.3 (cgroup v2) |
| SSH 키 | ~/.ssh/id_ed25519 |
| venv | /home/sjyun/.venv |
| AWS 프로필 | 01_re (980527594869) |

## 프로젝트 경로

| 프로젝트 | 경로 |
|----------|------|
| Ansible 학습 | /opt/00_chobo_ansible/ |
| 기술 문서 | /root/32_system-engineering-resources/ |
| AWS 작업 | /home/sjyun/03_aws/ |
| 로그 | /var/log/sjyun/ansible/ |

## 작업 규칙 요약

- md-style-check 0건 통과 필수
- Python으로 통일 (bash 스크립트 지양)
- 삭제 작업: 출력 → 승인 → 삭제 → 정리
- PLAN.md 이슈: 해결 직후 즉시 기재
- IP 전체 기재 (축약 금지)
- 이모지: ✅ ❌ 🟡 🟢 🔴 ★ 만 허용

## 최근 결정 사항

- 2026-06-19: md-style-check.py 다이어그램 검사 수정 (중첩 박스 지원)
- 2026-06-19: testing-guide skill에 edge case 5축 분석 추가
- 2026-06-19: harness_engineering.md 원문 대조 검증 완료 (13건 수정)
- 2026-06-18: AWS 미사용 리소스 정리 (~$523/월 절감)
- 2026-06-18: template_aws_cleanup.md 템플릿 생성
- 2026-06-17: Docker 컨테이너 15대 SSH 확인 + ssh_test.py 생성
