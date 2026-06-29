# 01_cve — CVE 취약점 분석·대응 문서

실제 익스플로잇이 확인되었거나 CVSS HIGH 이상인 취약점의 분석·대응 문서를 관리합니다. 이 문서는 디렉토리 인덱스로서 문서 목록, CVE 간 관계, 등록 기준을 제공합니다.

> 새 CVE 문서 작성 규칙은 [TEMPLATE.md](./TEMPLATE.md)를 참조합니다.

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 문서 목록](#2-문서-목록) / [3. 관계도](#3-관계도-현재-등록-cve-기준) / [4. 문서 작성 규칙](#4-문서-작성-규칙) |

---

## 1. 개요

이 디렉토리는 실제 익스플로잇이 확인되었거나 CVSS HIGH 이상인 취약점의 분석·대응 문서를 관리합니다. 이 문서는 디렉토리 인덱스로서 문서 목록, CVE 간 관계, 등록 기준을 제공합니다.

현재 등록된 취약점은 모두 Linux Kernel skb shared frag in-place 복호화 버그 클래스(page cache write → LPE)에 해당합니다.

### 등록 기준

| 조건                                          | 설명                                     |
|-----------------------------------------------|------------------------------------------|
| CVSS HIGH (7.0) 이상                          | NVD 등재 기준 baseScore 7.0 이상         |
| 실제 익스플로잇 확인 (PoC 공개 또는 CISA KEV) | 이론적 취약점이 아닌 실증된 위협         |
| 운영 환경 영향                                | 관리 중인 서버/컨테이너에 해당 커널 사용 |

### CVSS 심각도 기준

| 등급     | 점수 범위 | 의미                                   |
|----------|-----------|----------------------------------------|
| CRITICAL | 9.0~10.0  | 원격 비인증 공격, 즉시 시스템 장악     |
| HIGH     | 7.0~8.9   | 권한 상승, 인증 우회, 중요 데이터 노출 |
| MEDIUM   | 4.0~6.9   | 제한적 영향, 추가 조건 필요            |
| LOW      | 0.1~3.9   | 최소 영향, 물리 접근 등 특수 조건      |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 문서 목록

| CVE            | 별칭          | CVSS | 컴포넌트                          | 파일                                                                   |
|----------------|---------------|------|-----------------------------------|------------------------------------------------------------------------|
| CVE-2026-31431 | Copy Fail     | 7.8  | `algif_aead`                      | [cve_2026_31431_copy_fail.md](./cve_2026_31431_copy_fail.md)           |
| CVE-2026-43284 | Dirty Frag    | 8.8  | `esp4`, `esp6`                    | [cve_2026_43284_dirty_frag.md](./cve_2026_43284_dirty_frag.md)         |
| CVE-2026-43500 | Dirty Frag    | 7.8  | `rxrpc`                           | [cve_2026_43500_dirty_frag.md](./cve_2026_43500_dirty_frag.md)         |
| CVE-2026-43503 | DirtyClone    | 8.8  | `__pskb_copy_fclone`, `skb_shift` | [cve_2026_43503_dirty_clone.md](./cve_2026_43503_dirty_clone.md)       |
| CVE-2026-46300 | Fragnesia     | —    | `espintcp`                        | [cve_2026_46300_fragnesia.md](./cve_2026_46300_fragnesia.md)           |
| —              | 공격 시나리오 | —    | 종합 분석                         | [cve_2026_lpe_attack_scenarios.md](./cve_2026_lpe_attack_scenarios.md) |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 관계도 (현재 등록 CVE 기준)

```
skb shared frag in-place decrypt → page cache write → LPE
│
├── CVE-2026-31431  algif_aead (Copy Fail) ── CISA KEV, 별도 완화
│   └── /etc/modprobe.d/disable-algif-aead.conf
│
├── CVE-2026-43284  xfrm/ESP (Dirty Frag)      ──┐
├── CVE-2026-43500  rxrpc (Dirty Frag)         ──┤── /etc/modprobe.d/dirtyfrag.conf
├── CVE-2026-46300  espintcp (Fragnesia)       ──┤
└── CVE-2026-43503  frag-transfer (DirtyClone) ──┘

Timeline: 04-22 ──> 05-07 ──> 05-13 ──> 06-25
```

| 완화 파일                                 | 대상                                  |
|-------------------------------------------|---------------------------------------|
| `/etc/modprobe.d/disable-algif-aead.conf` | CVE-2026-31431 단독                   |
| `/etc/modprobe.d/dirtyfrag.conf`          | CVE-2026-43284/43500/46300/43503 공통 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 문서 작성 규칙

새 CVE 문서 추가 시 [TEMPLATE.md](./TEMPLATE.md)를 참조합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-06-29

**마지막 업데이트**: 2026-06-29

© 2026 siasia86. Licensed under CC BY 4.0.
