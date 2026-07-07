# CVE 문서 작성 템플릿

> 🟡 이 파일은 새 CVE 문서 추가 시 참조하는 작성 규칙·테스트 방법을 정의합니다.

## 목차

| 섹션                                                                                           |
|------------------------------------------------------------------------------------------------|
| [1. 파일명 규칙](#1-파일명-규칙) / [2. 섹션 구조](#2-섹션-구조) / [3. 필수 검증](#3-필수-검증) |
| [4. 테스트 방법](#4-테스트-방법) / [5. 취약점 존재 확인](#5-취약점-존재-확인-서버-점검)         |

---

## 1. 파일명 규칙

`cve_YYYY_NNNNN_별칭.md` (소문자, 언더스코어)

[⬆ 목차로 돌아가기](#목차)

---

## 2. 섹션 구조

```
# CVE-YYYY-NNNNN — 영향 소프트웨어 컴포넌트 (별칭)
## 목차
## 1. 개요          ← 표: CVE, CVSS, 벡터, 컴포넌트, 발견자, 일자
## 2. 취약점 상세   ← > 출처: [NVD](...) / [패치 커밋](...) / [PoC](...)
## 3. 영향 범위 확인 ← 탐지 명령어, 테스트 결과
## 4. 대처 방안     ← 즉시 패치 + 임시 완화 (출처 인용 필수)
## 5. 사후 검증     ← 패치 확인 명령어
## 참고 자료        ← 별점 포함 링크 목록
## 통계 + 푸터
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 필수 검증

- NVD API로 CVE 존재, CVSS, 영향 버전 확인
- git.kernel.org에서 패치 커밋 확인
- 배포판 보안 공지 HTTP 200 확인

공식 소스 상세: [`_reference/cve_security_official_notes.md`](../../_reference/cve_security_official_notes.md)

[⬆ 목차로 돌아가기](#목차)

---

## 4. 테스트 방법

문서 작성 완료 후 아래 순서로 검증합니다.

```bash
# 1. 스타일 검사 (0건 통과 필수)
python3 md-style-check.py 06_security/01_cve/cve_YYYY_NNNNN_alias.md

# 2. NVD API 존재 확인 (출력: 1 이상)
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-YYYY-NNNNN" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['totalResults'])"

# 3. 패치 커밋 접근 확인 (출력: 200 또는 301)
curl -s -o /dev/null -w "%{http_code}" "https://git.kernel.org/stable/c/{commit_hash}"

# 4. 배포판 보안 공지 접근 확인 (출력: 200)
curl -s -o /dev/null -w "%{http_code}" "https://ubuntu.com/security/CVE-YYYY-NNNNN"
curl -s -o /dev/null -w "%{http_code}" "https://access.redhat.com/security/cve/CVE-YYYY-NNNNN"

# 5. 내부 링크 검증
python3 md-link-check.py 06_security/01_cve/cve_YYYY_NNNNN_alias.md
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 취약점 존재 확인 (서버 점검)

대상 서버에서 해당 CVE에 실제로 취약한지 확인하는 방법입니다. 아래는 현재 등록된 DirtyFrag 계열 기준 예시이며, 새 CVE 추가 시 해당 CVE의 컴포넌트에 맞게 수정합니다.

```bash
# 1. 커널 버전 확인
uname -r

# 2. 패치 적용 여부 (Ubuntu)
apt-get changelog linux-image-$(uname -r) 2>/dev/null | grep CVE-YYYY-NNNNN

# 3. 패치 적용 여부 (RHEL/CentOS)
rpm -q --changelog kernel | grep CVE-YYYY-NNNNN

# 4. 관련 모듈 로드 상태 (로드됨 = 공격 경로 활성)
lsmod | grep -E "^algif_aead|^esp4|^esp6|^rxrpc"

# 5. blacklist 적용 여부
cat /etc/modprobe.d/disable-algif-aead.conf 2>/dev/null
cat /etc/modprobe.d/dirtyfrag.conf 2>/dev/null

# 6. 비권한 userns 활성 여부 (활성 = 익스플로잇 조건 충족)
sysctl kernel.unprivileged_userns_clone 2>/dev/null

# 7. DirtyFrag-Detector (자동 진단)
curl -sO https://raw.githubusercontent.com/liamromanis101/DirtyFrag-Detector/main/dirty_frag_detect.py
python3 dirty_frag_detect.py
rm -f dirty_frag_detect.py
```

| 결과                         | 판정      | 조치                          |
|------------------------------|-----------|-------------------------------|
| 패치 미적용 + 모듈 로드됨    | ❌ 취약   | 즉시 패치 또는 blacklist 적용 |
| 패치 미적용 + 모듈 blacklist | 🟡 완화됨 | 커널 업데이트 예정 확인       |
| 패치 적용됨                  | ✅ 안전   | blacklist 해제 가능           |

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
