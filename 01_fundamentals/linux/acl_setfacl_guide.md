# POSIX ACL·setfacl 가이드
<!-- reference: _reference/acl_setfacl_official_notes.md -->

Linux 파일과 디렉토리에 사용자·그룹별 세분화된 접근 권한을 설정하고, 신규 파일·디렉토리에 권한을 상속시키는 방법을 정리합니다. 모든 예시는 실제 사용자명·그룹명·운영 경로가 아닌 placeholder를 사용합니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. ACL 구조](#2-acl-구조) / [3. ACL 확인](#3-acl-확인)                                 |
| [4. 기존 권한 적용](#4-기존-권한-적용) / [5. 신규 항목 상속](#5-신규-항목-상속) / [6. ACL mask](#6-acl-mask) |
| [7. 백업·복구](#7-백업복구) / [8. 그룹 구성원 관리](#8-그룹-구성원-관리) / [9. 적용 절차](#9-적용-절차)      |

---

## 1. 개요

기본 Unix 권한은 파일 소유자, 소유 그룹, 그 밖의 사용자(`user::`, `group::`, `other::`)를 기준으로 합니다. 특정 그룹이나 사용자에게 별도 권한을 부여해야 할 때 POSIX ACL을 사용합니다.

> ACL(Access Control List): 기본 소유자·소유 그룹·기타 사용자 권한에 더해 특정 사용자와 그룹별 접근 권한을 기록하는 목록입니다.

`setfacl`은 ACL을 설정하고, `getfacl`은 현재 ACL을 확인합니다.

| 명령어    | 역할                                  |
|-----------|---------------------------------------|
| `setfacl` | Access ACL·Default ACL 수정·삭제·복구 |
| `getfacl` | ACL·소유자·소유 그룹·mask 확인        |
| `gpasswd` | 로컬 그룹의 구성원 추가·삭제          |

ACL은 그룹 구성원 관리와 별개입니다. 그룹에 사용자를 추가해야 해당 사용자가 그룹 ACL의 대상이 됩니다.

### 적용 범위

| 목표                                  | 필요한 설정                                |
|---------------------------------------|--------------------------------------------|
| 기존 파일·디렉토리에 권한 적용        | Access ACL                                 |
| 앞으로 생성되는 파일·디렉토리에 상속  | 부모 디렉토리의 Default ACL                |
| 기존 하위 디렉토리까지 신규 파일 상속 | 모든 기존 디렉토리에 Default ACL 설정      |
| 그룹 구성원 추가·삭제                 | 로컬 또는 중앙 디렉토리 서비스의 그룹 관리 |

## 2. ACL 구조

### 2.1 Access ACL과 Default ACL

**Access ACL**은 현재 파일 또는 디렉토리에 적용되는 권한입니다. **Default ACL**은 디렉토리에만 설정할 수 있으며, 해당 디렉토리에서 새로 생성되는 객체의 초기 Access ACL 기준이 됩니다.

```text
/srv/example_data/              ← Access ACL + Default ACL
├── existing.txt                ← Access ACL
└── new.txt                     ← 부모 Default ACL을 기준으로 생성
```

파일에는 Default ACL을 설정할 수 없습니다.

```bash
# 디렉토리: Access ACL과 Default ACL을 함께 표시
getfacl -p /srv/example_data

# 파일: Access ACL만 표시
getfacl -p /srv/example_data/existing.txt
```

### 2.2 ACL entry 형식

| 형식                              | 의미                        |
|-----------------------------------|-----------------------------|
| `u::rwx`                          | 파일 소유자 권한            |
| `u:example_user:r--`              | 지정 사용자 권한            |
| `g::r-x`                          | 파일 소유 그룹 권한         |
| `g:example_read_only_group:r-x`   | 지정 그룹 권한              |
| `m::r-x`                          | 현재 Access ACL mask        |
| `o::---`                          | 그 밖의 사용자 권한         |
| `d:u::rwx`                        | Default 소유자 권한         |
| `d:g:example_read_only_group:r-x` | Default 지정 그룹 권한      |
| `d:m::r-x`                        | Default ACL mask            |
| `d:o::---`                        | Default 그 밖의 사용자 권한 |

`d:` 접두사는 Default ACL을 의미합니다. 다음 두 표현은 같은 목적의 Default ACL 설정입니다.

```bash
setfacl -d -m g:example_read_only_group:r-x,m:r-x /srv/example_data
setfacl -m d:g:example_read_only_group:r-x,d:m:r-x /srv/example_data
```

> Default ACL: 디렉토리에 저장되어 새 파일·디렉토리의 초기 Access ACL로 사용되는 ACL입니다. 파일 자체에는 Default ACL을 저장할 수 없습니다.

## 3. ACL 확인

### 3.1 단일 경로 확인

```bash
getfacl -p /srv/example_data
```

`-p`는 절대 경로를 출력에 유지합니다. 디렉토리에 Default ACL이 있으면 출력에 `default:` 항목이 추가됩니다.

```text
# file: /srv/example_data
# owner: root
# group: root
user::rwx
group::r-x
group:example_read_only_group:r-x
mask::r-x
other::---
default:user::rwx
default:group::r-x
default:group:example_read_only_group:r-x
default:mask::r-x
default:other::---
```

파일에는 `default:` 항목이 없어야 정상입니다.

```bash
getfacl -p /srv/example_data/example_file
```

### 3.2 하위 트리 확인

```bash
# 모든 파일·디렉토리의 ACL 출력
getfacl -R -p /srv/example_data

# ACL이 추가된 객체만 출력
getfacl -R -s -p /srv/example_data
```

많은 파일을 한 번에 출력하면 검토가 어려우므로, 운영 변경 전에는 대표 디렉토리·하위 디렉토리·파일을 분리해서 확인합니다.

### 3.3 상위 경로 탐색 권한 확인

대상 디렉토리에 ACL이 있어도 상위 디렉토리를 통과할 `x` 권한이 없으면 접근할 수 없습니다.

```bash
namei -l /srv/example_data/example_file
```

다음 경로의 탐색 권한을 함께 확인합니다.

```text
/
/srv
/srv/example_data
/srv/example_data/example_file
```

## 4. 기존 권한 적용

### 4.1 전체 트리에 재귀 적용

```bash
BASE=/srv/example_data

setfacl -R -m g:example_read_only_group:r-X "$BASE"
```

`-R`은 기존 파일·디렉토리 전체에 Access ACL을 재귀 적용합니다. `r-X`의 대문자 `X`는 대상이 디렉토리이거나 기존에 실행 권한이 있는 파일일 때만 `x`를 적용합니다.

| 기존 대상                  | `r-X`의 일반적인 결과 |
|----------------------------|-----------------------|
| 디렉토리                   | `r-x`                 |
| 실행 권한이 없는 일반 파일 | `r--`                 |
| 기존 실행 파일             | `r-x` 가능            |

소문자 `x`를 사용하면 일반 파일에도 실행 권한을 적용할 수 있으므로, 읽기 전용 파일 트리에는 `X`의 조건부 동작을 검토합니다.

### 4.2 파일·디렉토리 정책을 분리

디렉토리와 파일에 서로 다른 Access ACL을 적용하려면 `find`로 대상을 분리합니다.

```bash
BASE=/srv/example_data

# 기존 디렉토리
find "$BASE" -type d \
  -exec setfacl -m g:example_group:rwx {} +

# 기존 일반 파일
find "$BASE" -type f \
  -exec setfacl -m g:example_group:rw- {} +
```

| `find` 조건 | 대상             |
|-------------|------------------|
| `-type d`   | 디렉토리         |
| `-type f`   | 일반 파일        |
| `{}`        | 검색된 경로      |
| `+`         | 경로를 묶어 실행 |

`setfacl -R`은 기존 전체 객체에 같은 ACL 작업을 적용할 때 간결하고, `find -type d`·`find -type f`는 대상별 정책을 명확하게 표현할 때 적합합니다.

## 5. 신규 항목 상속

### 5.1 최상위 디렉토리 하나에 설정

```bash
setfacl -m \
  d:g:example_read_only_group:r-x, \
  d:m:r-x \
  /srv/example_data
```

이 설정은 `/srv/example_data`에서 직접 생성되는 새 항목의 상속 기준이 됩니다. 이미 존재하는 하위 디렉토리에 Default ACL이 없다면 그 하위 디렉토리 안에서 생성되는 파일은 별도 상속 기준을 갖지 않을 수 있습니다.

### 5.2 기존 모든 디렉토리에 설정

기존 하위 디렉토리까지 신규 파일 상속을 보장하려면 모든 디렉토리에 Default ACL을 설정합니다.

```bash
BASE=/srv/example_data

find "$BASE" -type d \
  -exec setfacl -m \
  d:g:example_read_only_group:r-x, \
  d:m:r-x {} +
```

기존 Access ACL과 신규 Default ACL을 함께 설정하는 전체 예시는 다음과 같습니다.

```bash
BASE=/srv/example_data

# 기존 파일·디렉토리
setfacl -R -m g:example_read_only_group:r-X "$BASE"

# 기존 모든 디렉토리의 신규 항목 상속 정책
find "$BASE" -type d \
  -exec setfacl -m \
  d:g:example_read_only_group:r-x, \
  d:m:r-x {} +
```

### 5.3 생성 mode와 최종 권한

새 객체의 Access ACL은 부모 디렉토리의 Default ACL과 생성 호출의 mode parameter로 결정됩니다. Default ACL에 `x`가 있어도 생성 mode에 execute 권한이 없으면 새 객체의 해당 권한이 제거될 수 있습니다.

```text
Default ACL: group:example_read_only_group:r-x
새 일반 파일 생성 mode: 0666
최종 파일 권한: execute 권한이 제외될 수 있음
```

따라서 Default ACL 문자열만 보고 새 파일의 최종 권한을 단정하지 않고 실제 생성 결과를 `getfacl`로 확인합니다.

## 6. ACL mask

ACL mask는 소유자와 `other`를 제외한 ACL entry의 최대 유효 권한입니다.

```text
group:example_read_only_group:rwx
mask::r-x
```

위 상태에서 `example_read_only_group`의 실제 유효 권한은 `r-x`입니다.

```text
group:example_read_only_group:rwx    #effective:r-x
mask::r-x
```

ACL mask가 적용되는 대상:

- 소유 그룹 entry
- named user entry
- named group entry

ACL mask가 적용되지 않는 대상:

- 파일 소유자 entry
- `other` entry

Default ACL에서도 같은 구조를 사용합니다.

```text
default:group:example_read_only_group:rwx
default:mask::r-x
```

이 경우 새 항목에 상속되는 해당 그룹 권한의 최대 유효 권한은 `r-x`입니다.

`setfacl`은 기본적으로 mask를 재계산합니다. `-n`은 자동 재계산을 억제하고, `--mask`는 mask를 다시 계산하도록 지정합니다.

```bash
# Default ACL에서 그룹 관련 유효 권한의 상한을 r-x로 제한
setfacl -m d:g:example_read_only_group:r-x,d:m:r-x /srv/example_data
```

## 7. 백업·복구

### 7.1 ACL 백업

운영 경로를 변경하기 전에 ACL을 별도 파일로 저장합니다.

```bash
BASE=/srv/example_data
BACKUP="/var/tmp/example_data_acl_$(date +%Y%m%d_%H%M%S).acl"

umask 077
getfacl -R -p "$BASE" > "$BACKUP" || {
    rm -f "$BACKUP"
    echo "ACL backup failed" >&2
    exit 1
}

echo "ACL backup: $BACKUP"
```

백업 파일에는 경로·소유자·그룹·ACL 정보가 포함될 수 있으므로 접근 권한을 제한합니다.

### 7.2 ACL 복구

`getfacl -R` 출력은 `setfacl --restore`의 입력으로 사용할 수 있습니다.

```bash
setfacl --restore=/var/tmp/example_data_acl_YYYYMMDD_HHMMSS.acl
```

`--restore`는 전체 디렉토리 트리의 권한을 복구하며, 백업의 소유자·소유 그룹·setuid·setgid·sticky bit 주석이 포함된 경우 이를 복구하려고 시도합니다. 복구 전에 백업 파일과 대상 경로를 다시 확인합니다.

### 7.3 테스트 모드

실제 변경 없이 결과 ACL을 확인하려면 `--test`를 사용합니다.

```bash
setfacl --test -m g:example_read_only_group:r-X /srv/example_data/example_file
```

## 8. 그룹 구성원 관리

로컬 `/etc/group`·`/etc/gshadow`의 그룹 구성원은 `gpasswd`로 관리할 수 있습니다.

```bash
# 로컬 그룹에 사용자 추가
gpasswd -a example_user example_read_only_group

# 로컬 그룹에서 사용자 제거
gpasswd -d example_user example_read_only_group
```

이 작업은 ACL entry를 추가하거나 삭제하지 않습니다.

```text
그룹 구성원 변경
≠
파일·디렉토리 ACL entry 변경
```

사용자를 그룹에서 제거해도 다음 ACL entry 자체는 남아 있습니다.

```text
group:example_read_only_group:r-x
```

NIS·LDAP 그룹은 `gpasswd`로 변경하지 않습니다. 중앙 디렉토리 서비스를 사용하는 환경에서는 해당 서비스에서 그룹 구성원을 관리합니다.

구성원 변경 후에는 다음으로 실제 그룹 membership을 확인합니다.

```bash
id example_user
getent group example_read_only_group
```

## 9. 적용 절차

운영 경로에 ACL을 적용할 때는 다음 순서를 사용합니다.

1. 대상 경로를 절대 경로로 확정합니다.
2. 대상 파일시스템이 ACL을 지원하는지 확인합니다.
3. 기존 ACL을 백업합니다.
4. 대표 디렉토리·하위 디렉토리·파일의 현재 ACL을 확인합니다.
5. 기존 Access ACL을 적용합니다.
6. 기존 모든 디렉토리에 Default ACL을 적용합니다.
7. 테스트 디렉토리에서 신규 파일·디렉토리를 생성합니다.
8. `getfacl`로 신규 항목의 상속 결과를 확인합니다.
9. 그룹 구성원과 상위 경로의 탐색 권한을 확인합니다.
10. 결과와 백업 경로를 운영 기록에 남깁니다.

### 점검 명령

```bash
BASE=/srv/example_data

# 대상 경로 확인
readlink -f "$BASE"

# 그룹 확인
getent group example_read_only_group

# ACL 확인
getfacl -p "$BASE"

# 상위 경로 탐색 권한 확인
namei -l "$BASE"
```

### 적용 전후 체크리스트

| 점검 항목                 | 확인 방법                             |
|---------------------------|---------------------------------------|
| 대상 경로                 | `readlink -f "$BASE"`                 |
| ACL 지원 여부             | `getfacl -p "$BASE"`                  |
| 기존 ACL 백업             | `getfacl -R -p "$BASE" > backup.acl`  |
| 기존 디렉토리 Access ACL  | `getfacl -p directory`                |
| 기존 디렉토리 Default ACL | `getfacl -p directory`                |
| 기존 파일 Access ACL      | `getfacl -p file`                     |
| 신규 파일 상속 결과       | 테스트 후 `getfacl -p file`           |
| ACL mask effective 권한   | `getfacl`의 `#effective:` 확인        |
| 상위 경로 탐색 권한       | `namei -l "$BASE"`                    |
| 그룹 membership           | `id example_user`, `getent group ...` |

## 참고 자료

- ACL project: [savannah.nongnu.org/projects/acl](https://savannah.nongnu.org/projects/acl/) — ★★★☆☆
- `setfacl(1)`: [man7.org](https://man7.org/linux/man-pages/man1/setfacl.1.html) — ★★★★☆
- `getfacl(1)`: [man7.org](https://man7.org/linux/man-pages/man1/getfacl.1.html) — ★★★★☆
- `acl(5)`: [man7.org](https://man7.org/linux/man-pages/man5/acl.5.html) — ★★★★☆
- `umask(2)`: [man7.org](https://man7.org/linux/man-pages/man2/umask.2.html) — ★★★★☆
- `gpasswd(1)`: [man7.org](https://man7.org/linux/man-pages/man1/gpasswd.1.html) — ★★★☆☆
- [_reference/acl_setfacl_official_notes.md](../../_reference/acl_setfacl_official_notes.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-16

**마지막 업데이트**: 2026-09-16

© 2026 siasia86. Licensed under CC BY 4.0.
