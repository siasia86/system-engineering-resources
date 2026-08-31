# Governance and Tool Mirrors

저장소 운영 정책과 외부 AI 도구 자료 미러를 하나의 네임스페이스에서 관리합니다. 저장소 정책과 각 도구 미러는 하위 디렉토리별로 책임을 분리합니다.

## 목차

| 섹션                                              |
|---------------------------------------------------|
| [1. 목적](#1-목적) / [2. 구성](#2-구성)           |
| [3. 운영 원칙](#3-운영-원칙) / [4. 검증](#4-검증) |

---

## 1. 목적

`00_governance/`는 저장소 운영 기준과 AI 도구별 공개 자료 미러를 함께 탐색하기 위한 상위 디렉토리입니다. 정책 문서와 실행 환경 미러를 같은 파일로 취급하지 않으며, 하위 디렉토리별로 생명주기와 동기화 범위를 분리합니다.

## 2. 구성

| 디렉토리     | 역할                  | 원본·범위            |
|--------------|-----------------------|----------------------|
| `02_kiro/`   | Kiro 공개 미러        | `~/.kiro/` 허용 목록 |
| `03_claude/` | Claude 공개 미러 예정 | 원본·허용 목록 미정  |

- [31 governances Repository Governance](https://github.com/siasia86/31_governances): 저장소 운영 정책·template·동기화 공통 기준의 source of truth입니다 (2026-08-31 이관 완료).
- [Kiro 미러](02_kiro/README.md): `~/.kiro/`에서 허용된 자료만 보존합니다.
- [Claude 미러](03_claude/README.md): Claude 자료 추가를 위한 예약 영역입니다.

## 3. 운영 원칙

- 저장소 정책은 특정 AI 도구의 실행 환경과 분리합니다.
- 도구별 원본 경로와 동기화 허용 목록을 별도로 관리합니다.
- 개인 설정, 세션 상태, 자격증명, 내부 환경 정보는 공개 미러에 포함하지 않습니다.
- 원본에서 공개 미러로의 동기화만 허용하며 자동 역동기화는 수행하지 않습니다.
- 디렉토리 구조를 변경하면 루트 `README.md`, 링크 검사 설정, `CHANGELOG.md`를 함께 갱신합니다.

## 4. 검증

```bash
sia-md-link-check .
sia-md-heading-check .
sia-md-style-check .
sia-readme-inventory-check README.md
git diff --check
sudo gitleaks detect --source . --no-banner
```

`02_kiro/`와 향후 `03_claude/`의 미러 문서는 원본 형식을 보존할 수 있으므로 일반 Markdown 스타일 검사에서 별도 예외로 관리합니다. 정책 문서와 인덱스는 일반 검사 대상입니다.

---

**작성일**: 2026-08-20

**마지막 업데이트**: 2026-08-31

© 2026 siasia86. Licensed under CC BY 4.0.
