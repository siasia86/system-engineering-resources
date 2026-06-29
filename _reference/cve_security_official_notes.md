name: cve-security-official-notes
description: CVE/보안 취약점 문서 작성 시 참조할 공식 소스, API 엔드포인트, 검증 방법 정리. 06_security/01_cve/ 문서 생성/검토 시 참조.
tags:
  - cve
  - security
  - reference
last_checked: 2026-06-29
sources:
  - https://nvd.nist.gov/developers/vulnerabilities
  - https://www.cve.org/
  - https://www.cisa.gov/known-exploited-vulnerabilities-catalog
  - https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
  - https://access.redhat.com/security/security-updates/
  - https://ubuntu.com/security/cves
  - https://security-tracker.debian.org/tracker/
  - https://alas.aws.amazon.com/

# CVE/보안 취약점 공식 참조 노트

## 1. 공식 소스 목록

### 1차 소스 (CVE 등록 및 메타데이터)

| 소스           | URL                                                          | 용도                       | 신뢰도 |
|----------------|--------------------------------------------------------------|----------------------------|--------|
| NVD            | https://nvd.nist.gov/vuln/detail/CVE-YYYY-NNNNN              | CVSS, CWE, 영향 버전, 참조 | ★★★★★  |
| CVE.org        | https://www.cve.org/CVERecord?id=CVE-YYYY-NNNNN              | CVE 레코드 원본            | ★★★★★  |
| CISA KEV       | https://www.cisa.gov/known-exploited-vulnerabilities-catalog | 실제 악용 확인, 조치 기한  | ★★★★★  |
| git.kernel.org | https://git.kernel.org/stable/c/{commit_hash}                | 커널 패치 원본, Fixes 태그 | ★★★★★  |

### 배포판 보안 공지 (백포트 패치 확인)

| 배포판       | URL                                                        | API/검색        |
|--------------|------------------------------------------------------------|-----------------|
| RHEL/CentOS  | https://access.redhat.com/security/cve/CVE-YYYY-NNNNN      | 개별 CVE 페이지 |
| Ubuntu       | https://ubuntu.com/security/CVE-YYYY-NNNNN                 | 개별 CVE 페이지 |
| Debian       | https://security-tracker.debian.org/tracker/CVE-YYYY-NNNNN | 패키지별 상태   |
| Amazon Linux | https://alas.aws.amazon.com/                               | ALAS 공지 목록  |
| SUSE         | https://www.suse.com/security/cve/CVE-YYYY-NNNNN           | 개별 CVE 페이지 |

### 보안 연구 기업/개인 (PoC, 기술 분석)

| 소스                | URL 패턴                           | 비고               | 별점 기준   |
|---------------------|------------------------------------|--------------------|-------------|
| 발견자 GitHub       | github.com/{researcher}/{cve-repo} | PoC, 완화 가이드   | ★★☆☆☆~★★★☆☆ |
| JFrog Research      | research.jfrog.com/post/{slug}     | 상세 기술 문서     | ★★★☆☆       |
| Google Project Zero | googleprojectzero.blogspot.com     | 익스플로잇 분석    | ★★★★☆       |
| Qualys              | blog.qualys.com                    | 대규모 취약점 분석 | ★★★☆☆       |

### 뉴스/미디어 (2차 자료)

| 소스             | URL                  | 별점 기준 | 비고                        |
|------------------|----------------------|-----------|-----------------------------|
| 데일리시큐       | dailysecu.com        | ★★☆☆☆     | 국내 보안 뉴스, 기사 발견용 |
| BleepingComputer | bleepingcomputer.com | ★★☆☆☆     | 영문 보안 뉴스              |
| The Hacker News  | thehackernews.com    | ★★☆☆☆     | 영문 보안 뉴스              |

## 2. API 엔드포인트

### NVD API 2.0

```bash
# 단일 CVE 조회
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-43503"

# 응답에서 핵심 정보 추출
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-YYYY-NNNNN" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d['totalResults']==0: print('NOT FOUND'); sys.exit(1)
v=d['vulnerabilities'][0]['cve']
print('ID:', v['id'])
print('Published:', v['published'])
print('Status:', v['vulnStatus'])
metrics=v.get('metrics',{})
if 'cvssMetricV31' in metrics:
    m=metrics['cvssMetricV31'][0]['cvssData']
    print(f\"CVSS 3.1: {m['baseScore']} {m['baseSeverity']}\")
    print(f\"Vector: {m['vectorString']}\")
"
```

### CISA KEV JSON

```bash
# 전체 카탈로그 다운로드
curl -s "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" \
  | python3 -c "
import sys,json
data=json.load(sys.stdin)
target='CVE-YYYY-NNNNN'
matches=[v for v in data['vulnerabilities'] if v['cveID']==target]
for v in matches:
    print(v['cveID'], v['dateAdded'], v['dueDate'], v['shortDescription'])
"
```

### 커널 커밋 확인

```bash
# 패치 커밋 내용 확인
lynx -dump -nolist "https://git.kernel.org/stable/c/{commit_hash}" | head -30

# Fixes 태그 확인 (도입 커밋 추적)
lynx -dump -nolist "https://git.kernel.org/stable/c/{commit_hash}" | grep "Fixes:"
```

## 3. CVE 문서 작성 워크플로우

### 검증 순서

```
1. NVD API → CVE 존재, CVSS, 영향 버전 확인
2. git.kernel.org → 패치 커밋, 도입 커밋, 영향 코드 확인
3. 배포판 보안 공지 → 백포트 상태, 패치 버전 확인
4. 발견자 GitHub/블로그 → PoC, 기술 상세, 완화 방법 확인
5. CISA KEV → 실제 악용 여부, 조치 기한 확인
```

### 필수 검증 항목

| 항목               | 검증 소스          | 방법                                            |
|--------------------|--------------------|-------------------------------------------------|
| CVE 존재 여부      | NVD API            | `totalResults >= 1`                             |
| CVSS 점수          | NVD API            | `cvssMetricV31[0].cvssData.baseScore`           |
| 취약 버전 범위     | NVD configurations | `versionStartIncluding` ~ `versionEndExcluding` |
| 패치 커밋          | git.kernel.org     | 커밋 메시지 + diff 존재 확인                    |
| 패치 버전 (배포판) | 배포판 보안 공지   | HTTP 200 + 페이지 내용                          |
| PoC 존재 여부      | 발견자 GitHub      | 저장소 + README 확인                            |
| CISA KEV 등재      | CISA JSON          | `cveID` 매치 여부                               |

### 문서 신뢰도 규칙

| 규칙                                                                   |
|------------------------------------------------------------------------|
| 1차 소스(NVD, git.kernel.org)에서 확인 불가한 정보는 기재하지 않습니다 |
| 뉴스 기사는 발견 트리거로만 사용, 기술 정보의 근거로 사용하지 않습니다 |
| PoC 링크는 발견자 원본 저장소 우선, fork/mirror는 원본 병기합니다      |
| 배포판 패치 버전은 반드시 해당 배포판 공식 공지에서 확인합니다         |
| CVSS 점수는 NVD 등재 값만 사용, 자체 산정하지 않습니다                 |

## 4. 임시 완화 검증 규칙

| 규칙                                                                     |
|--------------------------------------------------------------------------|
| 완화 명령어는 반드시 출처 URL을 `>` 인용으로 표기합니다                  |
| 커널 모듈 blacklist 시 해당 모듈 의존 서비스(IPsec, AFS 등)를 명시합니다 |
| sysctl 변경 시 영향받는 애플리케이션을 명시합니다                        |
| 패치 후 완화 해제 명령어를 반드시 포함합니다                             |

## 5. DirtyFrag 계열 공통 참조

현재 `06_security/01_cve/` 에 등록된 동일 버그 클래스:

| CVE            | 별칭       | 컴포넌트                          | 완화 모듈               |
|----------------|------------|-----------------------------------|-------------------------|
| CVE-2026-31431 | Copy Fail  | `algif_aead`                      | `algif_aead`            |
| CVE-2026-43284 | Dirty Frag | `esp4`, `esp6`                    | `esp4`, `esp6`, `rxrpc` |
| CVE-2026-43500 | Dirty Frag | `rxrpc`                           | `esp4`, `esp6`, `rxrpc` |
| CVE-2026-46300 | Fragnesia  | `espintcp`                        | `esp4`, `esp6`, `rxrpc` |
| CVE-2026-43503 | DirtyClone | `__pskb_copy_fclone`, `skb_shift` | `esp4`, `esp6`, `rxrpc` |

공통 blacklist 파일: `/etc/modprobe.d/dirtyfrag.conf`

```bash
install esp4 /bin/false
install esp6 /bin/false
install rxrpc /bin/false
```

공통 탐지 도구: [DirtyFrag-Detector](https://github.com/liamromanis101/DirtyFrag-Detector)
