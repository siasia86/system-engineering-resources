---
name: zabbix-official-notes
description: Zabbix 공식 문서 기반 버전별 지원 OS, 릴리즈 정책, repo URL 패턴 정리.
tags:
  - zabbix
  - monitoring
  - alerting
  - snmp
last_checked: 2026-11-23
sources:
  - https://www.zabbix.com/life_cycle_and_release_policy
  - https://repo.zabbix.com/zabbix/
  - https://www.zabbix.com/documentation/current/en/manual/installation/containers
  - https://www.zabbix.com/documentation/current/en/manual/installation/requirements
  - https://hub.docker.com/u/zabbix
---

# Zabbix 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-11-09)

| 버전    | 종류     | 릴리즈일   | 일반 지원 종료 | 전체 지원 종료 |
|---------|----------|------------|----------------|----------------|
| 6.0 LTS | LTS      | 2022-02-08 | 2025-02-28     | 2027-02-28     |
| 7.0 LTS | LTS      | 2024-06-04 | 2027-06-30     | 2029-06-30     |
| 7.4     | Standard | 2025-07-01 | 2026-11-12     | 2027-05-31     |
| 8.0 LTS | LTS      | 2026-11-05 | 2029-11-30     | 2031-11-30     |

- LTS: 5년 지원, 18개월 주기 릴리즈
- Standard: 12개월 지원, 6개월 주기 릴리즈

## 2. 버전별 지원 OS

### Zabbix 7.4 (Standard)

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
- 6.0 LTS 일반 지원 종료(2025-02) — 신규 구축 시 7.0 LTS 권장 (2026-11-09 확인: 8.0 LTS가 2026-11-05 출시. 2026-11-23 저장소 경로·요구 사항·컨테이너 확인 결과는 6절, 8.0 지원 OS 표는 아직 기록하지 않음)
- Ubuntu 18/20에서 `apt` 모듈로 deb 설치 시 python3-apt 충돌 → `raw` 모듈 사용

## 6. 8.0 LTS 확인 (2026-11-23)

| 항목          | 내용                                                                                                                                      |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| 수명 주기     | 2026-11-05 출시, 일반 지원 2029-11-30, 전체 지원 2031-11-30 (공식 수명 주기 표)                                                           |
| Docker 이미지 | `zabbix/zabbix-server-pgsql`, `zabbix-web-nginx-pgsql`, `zabbix-agent2` 등. 태그 `ubuntu-8.0.0`, `alpine-8.0-latest` 형식                 |
| PostgreSQL    | 15.0 ~ 18.x, TimescaleDB 2.20 ~ 2.31 (Requirements)                                                                                       |
| PHP           | 8.2.0 ~ 8.5.x (Requirements)                                                                                                              |
| 규모 예       | Small(지표 1,000) 2 vCPU·8 GiB, Medium(10,000) 4 vCPU·16 GiB (Requirements)                                                               |
| deb 저장소    | `https://repo.zabbix.com/zabbix/8.0/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest+ubuntu24.04_all.deb` (debian13도 200) |
| rpm 저장소    | `https://repo.zabbix.com/zabbix/8.0/release/rhel/10/noarch/zabbix-release-latest-8.0.el10.noarch.rpm`                                     |
| API           | `hostinterface.update` 메서드 없음(`Method not found`), 인터페이스 변경은 `host.update`의 `interfaces`                                    |

컨테이너 시험(2026-11-23):

- compose(PostgreSQL 17 + server + web-nginx + agent2, 모두 `ubuntu-8.0.0`)에서 첫 기동 때 서버가 스키마를 만들고 `Starting Zabbix Server. Zabbix 8.0.0`을 남겼습니다. 스키마 생성 전 API는 `table "dbversion" was not found`를 돌려줬습니다.
- 기본 계정 `Admin`/`zabbix`로 API 로그인, `apiinfo.version` = `8.0.0`.
- 기본 `Zabbix server` 호스트 인터페이스는 `127.0.0.1:10050`이라 연결이 거부되고, DNS 이름으로 바꾸면 available=1이 됐습니다.
- agent2 이미지의 기본 `Server=`는 `zabbix-server`이고, 다른 주소에서 오면 `connection from "<주소>" rejected, allowed hosts: "<값>"`을 기록합니다.
- 패키지 agent2 기본값은 `Server=127.0.0.1`, `ServerActive=127.0.0.1`, `Hostname=Zabbix server`입니다(`ubuntu:24.04`에서 설치해 확인, `rockylinux/rockylinux:10`도 8.0.0 설치 확인).
