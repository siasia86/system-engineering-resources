@${1} Ansible Playbook을 리뷰해줘.

## 필수 점검 항목

### 기본
- YAML 문법 오류
- 모듈 deprecated 여부
- become/권한 설정 적절성

### Idempotent (멱등성)
- shell/command 모듈 사용 시 creates/removes 조건 있는지
- lineinfile 중복 실행 시 문제 없는지
- 파일 생성/수정이 changed 반복하지 않는지

### 에러 핸들링
- failed_when / changed_when 조건 적절성
- ignore_errors 사용 시 후속 처리 있는지
- block/rescue/always 구조 필요한 곳 누락 여부
- retries/until 필요한 네트워크/API 호출 여부

### 보안
- 평문 비밀번호/키 하드코딩 여부 (vault 사용 권장)
- no_log: true 누락된 민감 task
- 파일 권한 (mode) 과도하게 열려있는지 (0777 등)

### 성능
- serial / forks / async+poll 적절성
- 불필요한 gather_facts 여부
- delegate_to / run_once 최적화 가능 여부
- with_items 대신 loop 사용 권장

### 엣지케이스
- 대상 호스트 unreachable 시 동작
- 빈 변수/undefined 변수 처리 (default 필터)
- 디스크 풀/권한 부족 시 실패 처리
- handler notify 누락 (서비스 restart 필요한 설정 변경)
- 롤링 업데이트 시 max_fail_percentage 설정 여부
- check mode (--check) 호환 여부

결과를 항목별 ✅ ❌ ⚠️ 로 표시하고, 수정 제안은 코드 블록으로 보여줘.
