---
name: acl-setfacl-official-notes
description: POSIX ACL과 setfacl·getfacl·gpasswd의 공식 동작 및 파일·디렉토리 권한 상속 참조 노트
tags:
  - linux
  - acl
  - posix-acl
  - setfacl
  - getfacl
  - permissions
last_checked: 2026-09-16
sources:
  - https://savannah.nongnu.org/projects/acl/
  - https://savannah.nongnu.org/files/?group=acl
  - https://man7.org/linux/man-pages/man1/setfacl.1.html
  - https://man7.org/linux/man-pages/man1/getfacl.1.html
  - https://man7.org/linux/man-pages/man5/acl.5.html
  - https://man7.org/linux/man-pages/man2/umask.2.html
  - https://man7.org/linux/man-pages/man1/gpasswd.1.html
---

# POSIX ACL·setfacl 공식 참조 노트

## 1. 확인 범위

2026-09-16 기준으로 POSIX Access Control List(ACL), `setfacl`, `getfacl`, 파일·디렉토리 Default ACL 상속, ACL mask, `gpasswd`의 공식 동작을 확인했습니다.

실제 사용자명·그룹명·운영 경로는 reference note에 포함하지 않습니다. 예시는 `example_user`, `example_read_only_group`, `/srv/example_data` 같은 비민감 placeholder만 사용합니다.

## 2. 버전 및 공식 프로젝트

| 항목                | 확인 결과               | 출처                   |
|---------------------|-------------------------|------------------------|
| 공식 프로젝트       | Savannah `acl` 프로젝트 | Savannah project       |
| 최신 공식 배포 버전 | `acl-2.4.0`             | Savannah release files |
| 최신 릴리스 날짜    | 2026-06-29              | Savannah release files |
| 확인 환경의 버전    | `setfacl 2.3.2`         | local command          |
| 라이선스            | GNU GPL v2 or later     | Savannah project       |
| 개발 상태           | Production/Stable       | Savannah project       |

`setfacl`·`getfacl`가 설치된 운영체제의 패키지 버전은 공식 최신 릴리스와 다를 수 있습니다. 문서에서 기능을 설명할 때는 배포판의 실제 버전과 `setfacl --version` 결과를 함께 확인합니다.

> ACL(Access Control List): 파일의 소유자·소유 그룹·기타 사용자라는 기본 권한 외에 특정 사용자나 그룹별 권한을 추가로 지정하는 제어 목록입니다.

## 3. Access ACL과 Default ACL

`acl(5)`은 두 종류의 ACL을 구분합니다.

| 종류        | 적용 대상     | 역할                                            |
|-------------|---------------|-------------------------------------------------|
| Access ACL  | 파일·디렉토리 | 현재 객체에 대한 접근 권한                      |
| Default ACL | 디렉토리만    | 해당 디렉토리에서 생성되는 객체의 초기 ACL 기준 |

파일에는 Default ACL을 설정할 수 없습니다. Default ACL은 디렉토리에 설정하며, 새 파일 또는 새 디렉토리가 생성될 때 새 객체의 Access ACL을 초기화하는 데 사용됩니다.

```bash
# 현재 Access ACL과 디렉토리의 Default ACL을 함께 확인
getfacl -p /srv/example_data
```

## 4. ACL entry 형식

`setfacl`은 다음과 같은 ACL entry 형식을 사용합니다.

| 형식                              | 의미                        |
|-----------------------------------|-----------------------------|
| `u::rwx`                          | 파일 소유자 권한            |
| `u:example_user:r--`              | 지정 사용자 권한            |
| `g::r-x`                          | 파일 소유 그룹 권한         |
| `g:example_read_only_group:r-x`   | 지정 그룹 권한              |
| `m::r-x`                          | Access ACL mask             |
| `o::---`                          | 그 밖의 사용자 권한         |
| `d:u::rwx`                        | Default 소유자 권한         |
| `d:g:example_read_only_group:r-x` | Default 지정 그룹 권한      |
| `d:m::r-x`                        | Default ACL mask            |
| `d:o::---`                        | Default 그 밖의 사용자 권한 |

`d:` 접두사는 Default ACL을 뜻합니다. `setfacl -d -m` 방식으로도 Default ACL을 설정할 수 있습니다.

```bash
# 두 표현은 같은 목적의 Default ACL 설정 방식
setfacl -d -m g:example_read_only_group:r-x,m:r-x /srv/example_data
setfacl -m d:g:example_read_only_group:r-x,d:m:r-x /srv/example_data
```

## 5. ACL mask와 effective 권한

ACL mask는 소유자와 `other`를 제외한 다음 ACL entry의 최대 유효 권한을 제한합니다.

- owning group entry
- named user entry
- named group entry

```text
group:example_read_only_group:rwx
mask::r-x
```

위 예시에서 그룹 entry가 `rwx`를 요청해도 mask가 `r-x`이므로 실제 유효 권한은 `r-x`입니다. `getfacl`은 필요한 경우 다음처럼 표시합니다.

```text
group:example_read_only_group:rwx    #effective:r-x
mask::r-x
```

다음 entry는 ACL mask의 영향을 받지 않습니다.

- 파일 소유자 `user::...`
- `other::...`

`setfacl`은 기본적으로 mask를 다시 계산합니다. `-n`을 사용하면 effective rights mask를 다시 계산하지 않습니다. `--mask`는 명시된 mask가 있어도 다시 계산합니다.

```bash
# Default ACL mask를 명시적으로 r-x로 제한
setfacl -m d:g:example_read_only_group:r-x,d:m:r-x /srv/example_data
```

## 6. `setfacl` 핵심 옵션

| 옵션                     | 공식 동작                               |
|--------------------------|-----------------------------------------|
| `-m`, `--modify`         | 기존 ACL entry를 수정하거나 추가        |
| `-x`, `--remove`         | ACL entry를 제거                        |
| `-d`, `--default`        | 모든 작업을 Default ACL에 적용          |
| `-R`, `--recursive`      | 파일·디렉토리 트리 전체에 재귀 적용     |
| `-n`, `--no-mask`        | effective rights mask 자동 재계산 억제  |
| `--mask`                 | mask를 다시 계산                        |
| `-k`, `--remove-default` | Default ACL 제거                        |
| `--restore=FILE`         | `getfacl -R`로 저장한 ACL 백업을 복원   |
| `--test`                 | 실제 변경 없이 결과 ACL을 출력          |
| `-P`, `--physical`       | 심볼릭 링크를 따라가지 않는 물리적 순회 |
| `-L`, `--logical`        | 심볼릭 링크를 따라가는 논리적 순회      |

`-R`은 기존 객체에 작업을 재귀 적용하는 옵션입니다. 앞으로 생성되는 객체의 권한 상속을 설정하려면 디렉토리에 Default ACL을 별도로 설정해야 합니다.

## 7. 파일·디렉토리 권한에 `X` 사용

권한 문자열의 대문자 `X`는 다음 조건에서만 execute/search 권한으로 해석됩니다.

- 대상이 디렉토리인 경우
- 대상 파일에 기존 execute 권한이 하나라도 있는 경우

```bash
setfacl -R -m g:example_read_only_group:r-X /srv/example_data
```

일반적인 결과는 다음과 같습니다.

| 대상                       | `r-X`의 일반적 결과 |
|----------------------------|---------------------|
| 디렉토리                   | `r-x`               |
| 실행 권한이 없는 일반 파일 | `r--`               |
| 기존 실행 파일             | `r-x` 가능          |

따라서 읽기 전용 파일 트리에 디렉토리 탐색 권한을 함께 부여할 때 소문자 `x`보다 대문자 `X`가 파일별 실행 권한 변화를 줄일 수 있습니다.

## 8. 기존 객체와 신규 객체를 함께 설정하는 패턴

기존 파일·디렉토리와 신규 파일·디렉토리를 모두 대상으로 하려면 Access ACL과 Default ACL을 나누어 설정합니다.

```bash
BASE=/srv/example_data

# 기존 파일·디렉토리의 Access ACL
setfacl -R -m g:example_read_only_group:r-X "$BASE"

# 기존 모든 디렉토리의 Default ACL
find "$BASE" -type d \
  -exec setfacl -m \
  d:g:example_read_only_group:r-x, \
  d:m:r-x {} +
```

첫 번째 명령만 사용하면 기존 객체만 변경되고 신규 객체의 상속 정책은 설정되지 않습니다. 두 번째 명령을 최상위 디렉토리에만 실행하면 이미 존재하는 하위 디렉토리에는 Default ACL이 없을 수 있으므로, 기존 하위 디렉토리까지 대상으로 하려면 `find -type d`를 사용합니다.

새 객체의 Access ACL은 부모 디렉토리의 Default ACL과 생성 시스템 호출의 mode parameter를 사용하여 결정됩니다. Default ACL이 있어도 생성 mode에 없는 권한은 새 객체에 포함되지 않습니다.

## 9. Default ACL과 `umask`

부모 디렉토리에 Default ACL이 있으면 Linux는 새 객체의 ACL을 Default ACL과 생성 mode parameter로 결정합니다. 이 경우 일반적인 ACL 초기화 규칙이 적용되며, mode parameter에 없는 권한은 제거됩니다.

`umask(2)`는 부모 디렉토리에 Default ACL이 없는 경우의 파일 생성 권한 결정과 구분해야 합니다. Default ACL이 있으면 `umask` 대신 Default ACL이 사용되며, mode parameter에 없는 권한은 여전히 제거됩니다.

```text
Default ACL: group:example_read_only_group:r-x
파일 생성 mode: 0666
일반 파일 결과: execute 권한이 mode에 없으므로 x가 유지되지 않을 수 있음
```

실제 결과는 `getfacl`로 확인합니다. Default ACL의 예상 문자열만으로 새 파일의 최종 Access ACL을 단정하지 않습니다.

## 10. `getfacl` 확인과 ACL 백업

`getfacl`은 파일명·소유자·소유 그룹·Access ACL을 표시하며, 디렉토리에 Default ACL이 있으면 함께 표시합니다. `-p`는 절대 경로를 보존하고, `-R`은 하위 트리를 재귀적으로 표시합니다.

```bash
BASE=/srv/example_data
BACKUP="/var/tmp/example_data_acl_$(date +%Y%m%d_%H%M%S).acl"

umask 077
getfacl -R -p "$BASE" > "$BACKUP"
```

`getfacl` 출력은 `setfacl --restore` 입력으로 사용할 수 있습니다.

```bash
setfacl --restore="$BACKUP"
```

백업 전에 대상 경로가 맞는지 확인하고, 출력 파일이 비어 있거나 명령이 실패한 경우 권한 변경을 진행하지 않습니다. 백업에는 실제 경로·소유자·그룹 정보가 포함될 수 있으므로 접근 권한을 제한합니다.

```bash
# 단일 디렉토리의 Access ACL과 Default ACL 확인
getfacl -p /srv/example_data

# 특정 파일은 Access ACL만 확인
getfacl -p /srv/example_data/example_file
```

일반 파일에는 Default ACL이 존재하지 않습니다. `getfacl` 출력에서 `default:` 항목은 디렉토리에서만 확인할 수 있습니다.

## 11. `find`로 디렉토리와 파일을 분리하는 이유

다음 두 명령은 파일과 디렉토리에 서로 다른 정책을 적용하는 패턴입니다.

```bash
find "$BASE" -type d \
  -exec setfacl -m \
  g:example_group:rwx, \
  d:g:example_group:rwx, \
  d:m:rwx {} +

find "$BASE" -type f \
  -exec setfacl -m g:example_group:rw- {} +
```

- `-type d`: 디렉토리만 선택
- `-type f`: 일반 파일만 선택
- `g:...`: 현재 객체의 Access ACL
- `d:g:...`: 신규 객체에 상속할 Default ACL
- `d:m:...`: 신규 객체의 Default ACL mask
- `{}`: 검색된 경로 대체
- `+`: 여러 경로를 묶어 명령 실행

`setfacl -R`은 기존 파일·디렉토리 전체에 같은 ACL 작업을 적용할 때 편리합니다. `find -type d`와 `find -type f`는 파일·디렉토리별 정책을 명확하게 분리할 때 사용합니다.

## 12. 그룹 구성원 관리와 ACL의 관계

`gpasswd`는 로컬 `/etc/group` 및 `/etc/gshadow`의 그룹 구성원을 관리합니다.

```bash
gpasswd -a example_user example_read_only_group
gpasswd -d example_user example_read_only_group
```

- `-a`: 로컬 그룹에 사용자 추가
- `-d`: 로컬 그룹에서 사용자 제거

이 작업은 ACL entry를 추가하거나 삭제하지 않습니다. 사용자를 그룹에서 제거해도 다른 그룹 구성원에게 적용되는 `group:example_read_only_group:...` ACL은 그대로 남습니다.

`gpasswd`는 NIS·LDAP 그룹을 변경하지 않습니다. 중앙 디렉토리 그룹을 사용하는 환경에서는 해당 디렉토리 서비스에서 그룹 구성원을 관리합니다.

## 13. 권한 변경 전후 점검 항목

| 점검 항목                    | 확인 방법                                  |
|------------------------------|--------------------------------------------|
| 대상 경로 확인               | `readlink -f /srv/example_data`            |
| 상위 디렉토리 탐색 권한      | `namei -l /srv/example_data/example_file`  |
| 그룹 존재 여부               | `getent group example_read_only_group`     |
| 현재 ACL 백업                | `getfacl -R -p ... > backup.acl`           |
| 디렉토리 Access ACL          | `getfacl -p directory`                     |
| 디렉토리 Default ACL         | `getfacl -p directory`                     |
| 파일 Access ACL              | `getfacl -p file`                          |
| 신규 파일 상속 결과          | 테스트 디렉토리에서 생성 후 `getfacl` 확인 |
| 적용 대상의 심볼릭 링크 정책 | `setfacl -P` 또는 `setfacl -L` 선택 확인   |
| ACL mask의 effective 권한    | `getfacl`의 `#effective:` 확인             |

## 14. 공식 출처

- ACL project: [savannah.nongnu.org/projects/acl](https://savannah.nongnu.org/projects/acl/) — ★★★☆☆
- ACL releases: [savannah.nongnu.org/files/?group=acl](https://savannah.nongnu.org/files/?group=acl) — ★★★☆☆
- `setfacl(1)`: [man7.org](https://man7.org/linux/man-pages/man1/setfacl.1.html) — ★★★★☆
- `getfacl(1)`: [man7.org](https://man7.org/linux/man-pages/man1/getfacl.1.html) — ★★★★☆
- `acl(5)`: [man7.org](https://man7.org/linux/man-pages/man5/acl.5.html) — ★★★★☆
- `umask(2)`: [man7.org](https://man7.org/linux/man-pages/man2/umask.2.html) — ★★★★☆
- `gpasswd(1)`: [man7.org](https://man7.org/linux/man-pages/man1/gpasswd.1.html) — ★★★☆☆
