# CVE-2026-31431 — Linux Kernel algif_aead (Copy Fail)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 취약점 상세](#2-취약점-상세) / [3. 영향 범위 확인](#3-영향-범위-확인) |
| [4. 대처 방안](#4-대처-방안) / [5. 사후 검증](#5-사후-검증) |

---

## 1. 개요

> 🟡 **CISA KEV 등재 (조치 기한 2026-05-15 경과)**. 실제 익스플로잇 확인됨. 즉시 패치 필요.

| 항목 | 내용 |
|------|------|
| CVE | CVE-2026-31431 |
| 별칭 | **Copy Fail** |
| 발견자 | Xint Code (xint.io / copy.fail) |
| CVSS | 7.8 (HIGH) |
| 공격 벡터 | LOCAL / LOW privilege / NO interaction |
| CWE | CWE-669 (Incorrect Resource Transfer Between Spheres) |
| 컴포넌트 | `crypto/algif_aead` |
| 발표일 | 2026-04-22 |
| CISA KEV 등재 | 2026-05-01 |
| 조치 기한 | **2026-05-15** |
| PoC | 공개됨 (copy.fail — 732바이트 Python 스크립트) |
| 영향 | 비권한 로컬 사용자 → root 권한 상승 |

> 동일 버그 클래스(page-cache write): [CVE-2026-43284](./cve_2026_43284_dirty_frag.md) / [CVE-2026-43500](./cve_2026_43500_dirty_frag.md) (**Dirty Frag**, 발견자: Hyunwoo Kim @v4bel) / [CVE-2026-46300](./cve_2026_46300_fragnesia.md) (**Fragnesia**, 발견자: William Bowling)
> Copy Fail과 Dirty Frag는 **별개 연구자가 독립적으로 발견**한 별개 취약점입니다. 임시 완화 모듈도 다릅니다 (`algif_aead` vs `esp4/esp6/rxrpc`).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 취약점 상세

`algif_aead`에서 in-place 복호화 시 `skb_cloned()` 체크만 수행하고 `skb_has_frag_list()` / `skb_has_shared_frag()` 는 체크하지 않습니다. `splice()`로 UDP 소켓에 연결된 shared frag 페이지를 AEAD 복호화 경로에 전달하면 **page cache를 직접 덮어쓸 수 있어 권한 상승**이 가능합니다.

```
splice() → UDP socket → shared frag pages
                              ↓
                    algif_aead 복호화 (in-place)
                              ↓
                    page cache 덮어쓰기 → 권한 상승
```

- **패치 커밋**: `19d43105a97b` (2026-04-22)
- **도입 버전**: kernel 4.14+

**취약 버전:**

| 브랜치 | 취약 범위       | 패치 버전      | RHEL/CentOS          | Ubuntu              | Amazon Linux      |
|--------|-----------------|----------------|----------------------|---------------------|-------------------|
| 5.10.x | 4.14 ~ 5.10.253 | **5.10.254+**  | RHEL 8 (백포트 확인) | 20.04 LTS (HWE)     | AL2 (5.10 kernel) |
| 5.15.x | 5.11 ~ 5.15.203 | **5.15.204+**  | RHEL 9.0~9.2         | 22.04 LTS           | AL2023            |
| 6.1.x  | 5.16 ~ 6.1.169  | **6.1.170+**   | RHEL 9.3~9.4         | 22.04 LTS (HWE)     | AL2023 (6.1)      |
| 6.6.x  | 6.2 ~ 6.6.136   | **6.6.137+**   | RHEL 9.5+            | 24.04 LTS           | AL2023 (6.6)      |
| 6.12.x | 6.7 ~ 6.12.84   | **6.12.85+**   | RHEL 10              | **24.04 LTS** 🟡    | —                 |
| 6.18.x | 6.13 ~ 6.18.21  | **6.18.22+**   | —                    | 25.04               | —                 |
| 6.19.x | 6.19 ~ 6.19.11  | **6.19.12+**   | —                    | 25.10 (예정)        | —                 |

> RHEL/CentOS는 자체 백포트 패치를 적용하므로 upstream 버전과 다릅니다. `rpm -q --changelog kernel | grep CVE-2026-31431` 으로 패치 포함 여부를 직접 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 영향 범위 확인

### Ubuntu 24.04 실제 테스트 결과 (2026-05-13)

테스트 환경: Ubuntu 24.04.4 LTS / kernel `6.8.0-101-generic`

| 항목 | 결과 | 비고 |
|------|------|------|
| 커널 버전 | ❌ 취약 | 6.8.0-101 — 6.12.x 브랜치 취약 범위 |
| CVE-2026-31431 패치 | 🟡 미확인 | `algif_aead` blacklist 적용으로 완화됨 |
| `algif_aead` 모듈 | ✅ 완화 | `/etc/modprobe.d/` blacklist 적용됨 |
| AppArmor | ✅ 활성 | 완전 차단은 아님, 정책 확인 필요 |
| SELinux | ❌ 비활성 | Ubuntu 기본값 |

### 탐지 명령어

```bash
# 커널 버전 확인
uname -r

# 패치 적용 여부 (RHEL/CentOS)
rpm -q --changelog kernel | grep CVE-2026-31431 | head -3

# 패치 적용 여부 (Ubuntu)
apt-get changelog linux-image-$(uname -r) 2>/dev/null | grep CVE-2026-31431 | head -3

# 모듈 로드/blacklist 상태
lsmod | grep "^algif_aead"
grep "algif_aead" /etc/modprobe.d/*.conf 2>/dev/null

# AF_ALG 소켓 사용 여부
ss -A alg 2>/dev/null | head -10
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 대처 방안

### 즉시 패치

```bash
# RHEL / CentOS / Amazon Linux
sudo yum update kernel -y && sudo reboot

# Ubuntu / Debian
sudo apt update && sudo apt dist-upgrade -y && sudo reboot

# 재부팅 후 버전 확인
uname -r
```

### 임시 완화 (패치 적용 전)

**Step 1. AF_ALG 소켓 사용 여부 확인**

```bash
ss -A alg 2>/dev/null | head -10
lsmod | grep "^algif_aead"
```

| 모듈 | 사용 중인 경우 | 언로드 시 영향 |
|------|--------------|----------------|
| `algif_aead` | OpenSSL / GnuTLS AF_ALG 엔진 사용 중 | 암호화 연산 실패, 애플리케이션 오류 |

**Step 2. 언로드 및 blacklist 등록**

```bash
sudo rmmod algif_aead 2>/dev/null || true
echo "install algif_aead /bin/false" | sudo tee /etc/modprobe.d/disable-algif-aead.conf
```

**Step 3. 결과 확인**

```bash
lsmod | grep "^algif_aead"
# 출력 없으면 정상
```

### 배포판별 보안 공지

| 배포판 | 공지 URL |
|--------|---------|
| RHEL/CentOS | https://access.redhat.com/security/cve/CVE-2026-31431 |
| Ubuntu | https://ubuntu.com/security/CVE-2026-31431 |
| Debian | https://security-tracker.debian.org/tracker/CVE-2026-31431 |
| Amazon Linux | https://alas.aws.amazon.com/ |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 사후 검증

```bash
# 패치 적용 후 커널 버전 확인
uname -r

# 모듈 상태 확인
lsmod | grep "^algif_aead"
# 출력 없으면 정상

# CISA KEV 최신 목록 확인
curl -s "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" \
  | python3 -c "
import sys,json
data=json.load(sys.stdin)
linux=[v for v in data['vulnerabilities'] if 'linux' in v.get('product','').lower()]
for v in sorted(linux,key=lambda x:x['dateAdded'],reverse=True)[:5]:
    print(v['cveID'], v['dateAdded'], v['dueDate'])
"
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- NVD CVE-2026-31431: [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-31431) — ★★★☆☆
- Copy Fail PoC: [copy.fail](https://copy.fail/) — ★★☆☆☆
- CISA KEV Catalog: [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) — ★★★☆☆
- Linux Kernel Patch: [git.kernel.org](https://git.kernel.org/stable/c/19d43105a97be0810edbda875f2cd03f30dc130c) — ★★★★☆
- [cve_2026_43284_dirty_frag.md](./cve_2026_43284_dirty_frag.md) — CVE-2026-43284 (Dirty Frag / xfrm ESP)
- [cve_2026_43500_dirty_frag.md](./cve_2026_43500_dirty_frag.md) — CVE-2026-43500 (Dirty Frag / rxrpc)
- [cve_2026_46300_fragnesia.md](./cve_2026_46300_fragnesia.md) — CVE-2026-46300 (Fragnesia)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-13

**마지막 업데이트**: 2026-05-18

© 2026 siasia86. Licensed under CC BY 4.0.
