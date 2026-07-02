Fact-check markdown @${1}
# ${1} 생략 시: 이 대화에서 가장 최근에 수정/생성/읽은 .md 파일을 자동으로 대상으로 삼을 것.
# 최근 작업 파일이 불명확하면 "어떤 파일을 검증할까요?" 라고 물어볼 것.

## 목적

기술 문서의 **내용 정확성**을 공식 출처와 대조하여 검증합니다.
형식/스타일 검사는 `@md-review`에서, 사실 검증은 이 프롬프트에서 수행합니다.

## 검증 항목

1. **rfc-port-protocol**: RFC 번호, 포트, 프로토콜 번호가 IANA/IETF 원문과 일치하는지
2. **version-date**: 소프트웨어 버전, RFC 발행일, 출시연도가 정확한지
3. **algorithm-crypto**: 암호화 알고리즘, 키 길이, MUST/SHOULD 등급이 해당 RFC와 일치하는지
4. **feature-claim**: "기본", "필수", "항상", "지원" 등 단정 표현이 공식 문서와 일치하는지
5. **unverified-numbers**: 출처 없는 수치(%, 줄 수, 성능 비교, 배수)가 있으면 출처 명시 또는 제거
6. **hallucination**: 실제로 존재하지 않는 기능, 옵션, 명령어, 파라미터가 기술되어 있는지
7. **timeline-order**: 연도/세대 순서가 실제 발표/릴리즈 순서와 일치하는지
8. **cross-reference**: 동일 레포 내 _reference/ 파일과 수치/사실이 모순되지 않는지

## 검증 방법

- 공식 출처만 사용: IETF datatracker, IANA registry, 프로젝트 공식 사이트, GitHub releases
- 블로그, Wikipedia, Stack Overflow는 검증 출처로 사용 금지 (단서 발견용으로만 허용)
- `lynx -dump` 또는 `curl` + API로 직접 확인
- 확인 불가한 항목: 제거하거나 "검증 불가 — 출처 필요" 표시

## 검증 절차

```
1. 문서에서 핵심 사실 추출 (RFC, 포트, 버전, 알고리즘, 수치, 연도)
2. 각 사실을 공식 출처에서 lynx/curl로 대조
3. 불일치/미검증 항목 목록 작성
4. 수정 (최소 변경 — 내용 추가 금지, 오류만 수정/제거)
5. 재검증
```

## 금지 사항

- 검증 과정에서 새로운 내용을 추가하는 행위 ❌
- "더 정확하게"를 이유로 표현을 확장/수식하는 행위 ❌
- 출처 없이 수치를 다른 수치로 교체하는 행위 ❌
- 검증 불가 항목을 추론으로 채우는 행위 ❌

## Output

Korean, ✅❌🟡 per item

```
=== Fact Check: {filename} ===
✅ PPTP TCP 1723 — RFC 2637 확인
❌ OpenVPN "TLS 1.3 기본" — openvpn.net: tls-version-max=highest (기본 아님)
🟡 코드 규모 ~120,000줄 — 출처 없음, 검증 불가
```

수정 시: 오류 항목만 최소 변경, diff 표시

## Loop (max 2 iterations)

1. 핵심 사실 추출 + 공식 출처 대조 → ❌/🟡 목록
2. 오류만 수정 (추가 금지)
3. 재검증 → 잔여 이슈 확인
4. Final summary: 검증 항목 수, 정확 수, 수정 수, 잔여 이슈
