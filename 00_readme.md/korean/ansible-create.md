${1} 용도의 Ansible Playbook을 작성해줘.
대상 호스트 그룹: ${2}

## 필수 요구사항
- idempotent하게 작성
- 민감 정보는 vault 변수로 분리
- 파일 생성 시 mode 명시
- handler로 서비스 재시작 분리

## 엣지케이스 처리 포함
- 변수 미정의 시 default 필터 적용
- 네트워크 호출은 retries/until/delay 적용
- block/rescue로 실패 시 롤백 또는 알림
- 디스크/권한 사전 검증 task 포함
- check mode (--check) 호환

## 출력 형식
- 디렉토리 구조 (roles 사용 시)
- playbook 본문
- vars/defaults 예시
- 실행 명령어 예시
