Ansible 실행 중 아래 에러가 발생했어:

- Playbook: ${1}
- 에러 내용: ${2}

## 분석해줘
1. 에러 원인 (root cause)
2. 재현 조건
3. 수정 방법 (코드 블록)
4. 엣지케이스 확인
   - 호스트 unreachable / SSH 타임아웃
   - 변수 undefined / 타입 불일치
   - 권한 부족 (become 누락)
   - 모듈 버전 호환성
   - 이전 task 실패로 인한 연쇄 에러
5. 재발 방지 대책
