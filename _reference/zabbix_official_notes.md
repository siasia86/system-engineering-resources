---
name: zabbix-official-notes
description: Zabbix 공식 문서 기반 버전별 지원 OS, 릴리즈 정책, repo URL 패턴 정리.
last_checked: 2026-05-22
sources:
  - https://www.zabbix.com/life_cycle_and_release_policy
  - https://repo.zabbix.com/zabbix/
---

# Zabbix 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-05-22)

| 버전    | 종류     | 릴리즈일       | 일반 지원 종료          | 전체 지원 종료          |
|---------|----------|----------------|-------------------------|-------------------------|
| 6.0 LTS | LTS      | 2022-02-08     | 2025-02-28              | 2027-02-28              |
| 7.0 LTS | LTS      | 2024-06-04     | 2027-06-30              | 2029-06-30              |
| 7.4     | Standard | 2025-07-01     | until 8.0 LTS (Q4 2026) | until 8.0 LTS (Q4 2026) |
| 8.0 LTS | LTS      | Q3 2026 (예정) | Q3 2029                 | Q3 2031                 |

- LTS: 5년 지원, 18개월 주기 릴리즈
- Standard: 12개월 지원, 6개월 주기 릴리즈

## 2. 버전별 지원 OS

### Zabbix 7.4 (Standard, 현재 최신)

| OS           | 지원 버전                                |
|--------------|------------------------------------------|
| Ubuntu       | 16.04, 18.04, 20.04, 22.04, 24.04, 26.04 |
| Debian       | 9, 10, 11, 12, 13                        |
| RHEL         | 8, 9, 10                                 |
| Rocky Linux  | 9, 10                                    |
| AlmaLinux    | 10                                       |
| Oracle Linux | 10                                       |
| CentOS       | 10                                       |
| Amazon Linux | 2, 2023                                  |
| SLES         | 12, 15, 16                               |

### Zabbix 7.0 LTS

| OS           | 지원 버전                                |
|--------------|------------------------------------------|
| Ubuntu       | 16.04, 18.04, 20.04, 22.04, 24.04, 26.04 |
| Debian       | 9, 10, 11, 12, 13                        |
| RHEL         | 7, 8, 9, 10                              |
| Rocky Linux  | 8, 9, 10                                 |
| AlmaLinux    | 10                                       |
| Oracle Linux | 10                                       |
| CentOS       | 10                                       |
| Amazon Linux | 2, 2023                                  |
| SLES         | 12, 15, 16                               |

### Zabbix 6.0 LTS (일반 지원 종료, 2027-02까지 전체 지원)

| OS           | 지원 버전                                |
|--------------|------------------------------------------|
| Ubuntu       | 14.04, 16.04, 18.04, 20.04, 22.04, 24.04 |
| Debian       | 9, 10, 11, 12, 13                        |
| RHEL         | 6, 7, 8, 9, 10                           |
| Amazon Linux | 2023                                     |
| SLES         | 12, 15                                   |

## 3. repo URL 패턴

### Ubuntu/Debian (deb)

```bash
# Ubuntu — zabbix-release_latest+ubuntu{VERSION_ID}_all.deb
https://repo.zabbix.com/zabbix/{ZABBIX_VER}/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest+ubuntu{VERSION_ID}_all.deb

# 예시 (7.4, Ubuntu 22.04)
https://repo.zabbix.com/zabbix/7.4/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest+ubuntu22.04_all.deb

# Debian — zabbix-release_latest+debian{VERSION}_all.deb
https://repo.zabbix.com/zabbix/7.4/release/debian/pool/main/z/zabbix-release/zabbix-release_latest+debian12_all.deb
```

### RHEL/Rocky/Alma (rpm) — 7.4

```bash
# RHEL/Rocky/Alma — zabbix-release-7.4-1.el{MAJOR}.noarch.rpm
https://repo.zabbix.com/zabbix/7.4/release/rhel/{MAJOR}/noarch/zabbix-release-7.4-1.el{MAJOR}.noarch.rpm

# 예시 (RHEL/Rocky 9)
https://repo.zabbix.com/zabbix/7.4/release/rhel/9/noarch/zabbix-release-7.4-1.el9.noarch.rpm
```

### Amazon Linux (rpm) — 7.4

```bash
# Amazon Linux 2
https://repo.zabbix.com/zabbix/7.4/release/amazonlinux/2/noarch/zabbix-release-7.4-4.amzn2.noarch.rpm

# Amazon Linux 2023
https://repo.zabbix.com/zabbix/7.4/release/amazonlinux/2023/noarch/zabbix-release-7.4-1.amzn2023.noarch.rpm
```

### 7.0 LTS URL 패턴 (release/ 없음)

```bash
# 7.0 LTS는 경로에 release/ 없음
https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/...
https://repo.zabbix.com/zabbix/7.0/rhel/{MAJOR}/noarch/...
```

## 4. 패키지명

| OS                | 패키지명        | 비고          |
|-------------------|-----------------|---------------|
| Ubuntu/Debian     | `zabbix-agent2` | agent2 권장   |
| RHEL/Rocky/Alma   | `zabbix-agent2` |               |
| Amazon Linux 2    | `zabbix-agent`  | agent2 미지원 |
| Amazon Linux 2023 | `zabbix-agent2` |               |

## 5. 주의사항

- Amazon Linux 2는 `zabbix-agent2` 미지원 → `zabbix-agent` 사용
- 6.0 LTS 일반 지원 종료(2025-02) — 신규 구축 시 7.0 LTS 권장
- Ubuntu 18/20에서 `apt` 모듈로 deb 설치 시 python3-apt 충돌 → `raw` 모듈 사용
