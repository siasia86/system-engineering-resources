# SVN 실무 가이드
<!-- reference: _reference/svn_official_notes.md -->

## 목차

| 섹션                                                                                                                     |
|--------------------------------------------------------------------------------------------------------------------------|
| [1. 기본 개념](#1-기본-개념) / [2. 저장소 초기화](#2-저장소-초기화) / [3. checkout과 update](#3-checkout과-update)       |
| [4. 변경 및 커밋](#4-변경-및-커밋) / [5. diff와 log](#5-diff와-log) / [6. 브랜치와 태그](#6-브랜치와-태그)               |
| [7. 병합 (merge)](#7-병합-merge) / [8. 충돌 해결](#8-충돌-해결) / [9. 속성 관리](#9-속성-관리)                           |
| [10. 잠금 (lock)](#10-잠금-lock) / [11. 외부 참조 (externals)](#11-외부-참조-externals) / [12. 서버 관리](#12-서버-관리) |
| [13. 실무 팁](#13-실무-팁)                                                                                               |

---

## 1. 기본 개념

### 작업 흐름

```
Repository (중앙 서버)
       │
       │ svn checkout (최초 1회)
       v
  Working Copy (로컬)
       │
       │ 파일 편집
       │
       ├── svn add / svn delete / svn move
       │
       │ svn commit ──────────────────────> Repository (즉시 반영)
       │
       └── svn update <────────────────── Repository (최신 반영)
```

### 리비전 키워드

| 키워드      | 의미                           |
|-------------|--------------------------------|
| `HEAD`      | 저장소 최신 리비전             |
| `BASE`      | 현재 Working Copy 기준 리비전  |
| `PREV`      | BASE - 1                       |
| `COMMITTED` | 해당 파일의 마지막 커밋 리비전 |
| `r42`       | 리비전 번호 직접 지정          |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 저장소 초기화

### 저장소 생성 (서버)

```bash
# FSFS 형식 저장소 생성 (권장)
svnadmin create /srv/svn/myrepo

# 디렉토리 구조 확인
ls /srv/svn/myrepo/
# conf/  db/  format  hooks/  locks/  README.txt
```

### 표준 디렉토리 구조 생성

```bash
# trunk / branches / tags 초기 구조 임포트
svn mkdir file:///srv/svn/myrepo/trunk \
          file:///srv/svn/myrepo/branches \
          file:///srv/svn/myrepo/tags \
          -m "초기 디렉토리 구조 생성"
```

### 기존 소스 임포트

```bash
# 소스 디렉토리를 저장소 trunk로 임포트
svn import /path/to/source \
    https://svn.example.com/repos/myrepo/trunk \
    -m "최초 임포트"
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. checkout과 update

### `svn checkout` — 저장소 내려받기

```bash
# trunk 전체 체크아웃
svn checkout https://svn.example.com/repos/myrepo/trunk ./myproject
svn co https://svn.example.com/repos/myrepo/trunk ./myproject   # 축약

# 특정 리비전 체크아웃
svn co -r 150 https://svn.example.com/repos/myrepo/trunk ./myproject

# 특정 디렉토리만 체크아웃 (sparse)
svn co --depth empty https://svn.example.com/repos/myrepo/trunk ./myproject
svn update --set-depth infinity ./myproject/src   # 특정 하위만 확장

# 인증 정보 포함
svn co --username Secureuser123 --password SecurePassword123 \
    https://svn.example.com/repos/myrepo/trunk ./myproject
```

### `svn update` — 최신 반영

```bash
# 전체 업데이트 (HEAD)
svn update
svn up                # 축약

# 특정 리비전으로 업데이트
svn up -r 120

# 특정 파일만 업데이트
svn up src/main.py

# 업데이트 없이 Working Copy 리비전만 변경 (pegrev)
svn up -r BASE        # 로컬 변경 유지하며 서버 정보만 갱신
```

### `svn info` — 현재 상태 확인

```bash
svn info
# URL: https://svn.example.com/repos/myrepo/trunk
# Revision: 203
# Last Changed Rev: 201
# Last Changed Author: sjyun

svn info --show-item revision   # 리비전 번호만 출력
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 변경 및 커밋

### `svn status` — 변경 상태 확인

```bash
svn status
svn st          # 축약
```

상태 코드:

| 코드 | 의미                              |
|------|-----------------------------------|
| `M`  | 수정됨 (Modified)                 |
| `A`  | 추가 예정 (Added)                 |
| `D`  | 삭제 예정 (Deleted)               |
| `?`  | 버전 관리 대상 아님 (Unversioned) |
| `!`  | 누락 (Missing) — 파일 삭제됨      |
| `C`  | 충돌 (Conflict)                   |
| `I`  | 무시됨 (Ignored)                  |
| `~`  | 타입 변경 (파일→디렉토리 등)      |

```bash
# 서버 변경사항도 함께 확인
svn status -u

# 무시 파일 포함 모든 상태 출력
svn status --no-ignore
```

### `svn add` / `svn delete`

```bash
# 파일/디렉토리 추가
svn add newfile.py
svn add newdir/
svn add --force .   # 현재 디렉토리의 Unversioned 파일 전체 추가

# 파일 삭제 (로컬 삭제 + 버전 관리 제거)
svn delete oldfile.py
svn rm oldfile.py   # 축약

# 버전 관리만 제거 (로컬 파일 유지)
svn delete --keep-local config.local
```

### `svn move` / `svn copy`

```bash
# 파일 이동/이름 변경
svn move old_name.py new_name.py
svn mv old_name.py new_name.py   # 축약

# 파일 복사 (이력 유지)
svn copy src.py dst.py
```

### `svn commit` — 저장소에 반영

```bash
# 전체 커밋
svn commit -m "feat: add login feature"
svn ci -m "feat: add login feature"   # 축약

# 특정 파일만 커밋
svn ci src/main.py src/auth.py -m "fix: auth validation"

# 메시지 파일로 커밋
svn ci -F commit_message.txt

# 로그 메시지 없이 커밋 (권장하지 않음)
svn ci --force-log -m ""
```

### `svn revert` — 변경 취소

```bash
# 단일 파일 되돌리기
svn revert main.py

# 전체 Working Copy 되돌리기 (재귀)
svn revert -R .

# 추가 예정(A) 파일 취소 (파일은 유지)
svn revert newfile.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. diff와 log

### `svn diff` — 변경 내용 비교

```bash
# Working Copy vs BASE
svn diff

# 특정 파일
svn diff main.py

# 두 리비전 비교
svn diff -r 100:110

# Working Copy vs 특정 리비전
svn diff -r 100

# 리비전 간 특정 파일 비교
svn diff -r 100:HEAD main.py

# 외부 diff 도구 사용
svn diff --diff-cmd vimdiff
```

### `svn log` — 커밋 이력 조회

```bash
# 전체 로그 (최신순)
svn log

# 최근 N개
svn log -l 10

# 특정 리비전 범위
svn log -r 100:200

# 변경 파일 목록 포함 (verbose)
svn log -v

# 특정 파일의 이력
svn log main.py

# 저장소 URL 직접 지정
svn log https://svn.example.com/repos/myrepo/trunk -l 5

# XML 형식 출력 (스크립트 파싱용)
svn log --xml -l 5
```

### `svn blame` — 라인별 최종 수정자

```bash
svn blame main.py
svn ann main.py   # annotate 축약

# 특정 리비전 기준
svn blame -r 150 main.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 브랜치와 태그

SVN에서 브랜치와 태그는 모두 `svn copy`로 생성합니다. 저장소 내 링크(cheap copy)이므로 즉시 완료됩니다.

### 브랜치 생성

```bash
# trunk에서 브랜치 생성
svn copy https://svn.example.com/repos/myrepo/trunk \
         https://svn.example.com/repos/myrepo/branches/feature-login \
         -m "브랜치 생성: feature-login"

# 특정 리비전에서 브랜치 생성
svn copy -r 180 \
         https://svn.example.com/repos/myrepo/trunk \
         https://svn.example.com/repos/myrepo/branches/hotfix-r180 \
         -m "핫픽스 브랜치 생성 from r180"
```

### 태그 생성

```bash
# trunk HEAD에서 태그 생성
svn copy https://svn.example.com/repos/myrepo/trunk \
         https://svn.example.com/repos/myrepo/tags/v1.0.0 \
         -m "태그: v1.0.0 릴리스"
```

🟡 태그 디렉토리는 관례상 수정하지 않습니다. SVN은 강제 방지 기능이 없으므로 운영 규칙으로 관리합니다.

### 브랜치 전환 (switch)

```bash
# Working Copy를 브랜치로 전환
svn switch https://svn.example.com/repos/myrepo/branches/feature-login

# 전환 후 확인
svn info | grep URL
```

### 브랜치 목록 확인

```bash
svn list https://svn.example.com/repos/myrepo/branches/
svn list https://svn.example.com/repos/myrepo/tags/
```

### 브랜치 삭제

```bash
svn delete https://svn.example.com/repos/myrepo/branches/feature-login \
           -m "브랜치 삭제: feature-login 병합 완료"
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 병합 (merge)

### 브랜치 → trunk 병합

```bash
# trunk Working Copy로 이동
cd /path/to/trunk-workingcopy

# 브랜치의 변경사항 병합
svn merge https://svn.example.com/repos/myrepo/branches/feature-login

# 병합 내용 확인
svn status
svn diff

# 커밋
svn ci -m "merge: feature-login 병합"
```

### 특정 리비전 cherry-pick

```bash
# 리비전 r205 하나만 trunk로 병합
svn merge -c 205 https://svn.example.com/repos/myrepo/trunk

# 리비전 범위 병합
svn merge -r 200:210 https://svn.example.com/repos/myrepo/branches/feature-login

# 리비전 제외 (역방향 병합)
svn merge -c -205 .   # r205를 취소(롤백)
```

### 병합 미리보기 (dry-run)

```bash
svn merge --dry-run \
    https://svn.example.com/repos/myrepo/branches/feature-login
```

### 병합 이력 확인

```bash
# 병합된 리비전 확인
svn mergeinfo --show-revs merged \
    https://svn.example.com/repos/myrepo/branches/feature-login

# 병합 안된 리비전 확인
svn mergeinfo --show-revs eligible \
    https://svn.example.com/repos/myrepo/branches/feature-login
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 충돌 해결

### 충돌 발생 흐름

```bash
svn update
# C  main.py     -- 충돌 발생
# Updated to revision 210.
```

충돌 시 생성 파일:

| 파일           | 내용                |
|----------------|---------------------|
| `main.py`      | 충돌 마커 포함 파일 |
| `main.py.mine` | 내 변경 내용        |
| `main.py.rOLD` | BASE 리비전 원본    |
| `main.py.rNEW` | 서버 최신 리비전    |

### 수동 해결

```bash
# 1. 충돌 파일 직접 편집 (충돌 마커 제거)
vi main.py

# 2. 해결 완료 표시
svn resolve --accept working main.py

# 3. 커밋
svn ci -m "fix: 충돌 해결"
```

### 자동 해결 옵션

```bash
# 내 변경을 우선 (mine-full)
svn resolve --accept mine-full main.py

# 서버 변경을 우선 (theirs-full)
svn resolve --accept theirs-full main.py

# BASE 리비전으로 되돌리기
svn resolve --accept base main.py
```

### 트리 충돌 (tree conflict)

```bash
# 트리 충돌 확인
svn status | grep "^C"

# 상세 확인
svn info main.py | grep -i conflict

# 내 버전 유지
svn resolve --accept working main.py
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 속성 관리

### 속성 설정/조회

```bash
# 속성 설정
svn propset svn:ignore "*.pyc
__pycache__
*.log" .

# 속성 조회
svn propget svn:ignore .

# 모든 속성 조회
svn proplist -v main.py

# 속성 삭제
svn propdel svn:keywords main.py
```

### `svn:ignore` — 무시 패턴

```bash
# 현재 디렉토리 무시 패턴 설정
svn propset svn:ignore "*.pyc
*.log
__pycache__
.env
dist/
build/" .

# 편집기로 설정
svn propedit svn:ignore .

# 커밋
svn ci -m "chore: svn:ignore 패턴 설정"
```

### `svn:eol-style` — 줄바꿈 정규화

```bash
# 텍스트 파일에 native 설정 (OS별 자동)
svn propset svn:eol-style native main.py

# LF 강제 (Linux 서버 배포 파일)
svn propset svn:eol-style LF deploy.sh
```

### `svn:keywords` — 키워드 치환

```bash
# 파일 내 $Rev$, $Date$, $Author$ 자동 치환 활성화
svn propset svn:keywords "Rev Date Author" main.py
```

파일 내에서 사용:

```python
# $Rev: 205 $
# $Date: 2026-07-29 14:30:00 +0900 $
# $Author: sjyun $
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 잠금 (lock)

이진 파일(이미지, Office 문서 등) 동시 편집 방지에 사용합니다.

```bash
# 파일 잠금
svn lock design.psd -m "디자인 작업 중"

# 잠금 확인
svn status -u design.psd
svn info design.psd | grep -i lock

# 잠금 해제 (자신)
svn unlock design.psd

# 잠금 강제 해제 (관리자)
svn unlock --force design.psd

# svn:needs-lock 속성 -- 체크아웃 시 읽기 전용으로 설정
svn propset svn:needs-lock '*' design.psd
svn ci -m "chore: needs-lock 설정"
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 외부 참조 (externals)

다른 저장소 또는 같은 저장소의 경로를 현재 Working Copy에 포함합니다.

```bash
# externals 설정 (lib/ 디렉토리에 외부 저장소 연결)
svn propset svn:externals \
    "lib/common https://svn.example.com/repos/common/trunk" .

# 특정 리비전 고정 (권장 -- 예상치 못한 변경 방지)
svn propset svn:externals \
    "lib/common -r 150 https://svn.example.com/repos/common/trunk" .

# 설정 확인
svn propget svn:externals .

# externals 업데이트
svn update                    # externals 포함 전체 업데이트
svn update --ignore-externals # externals 제외
```

[⬆ 목차로 돌아가기](#목차)

---

## 12. 서버 관리

### `svnadmin` — 저장소 관리

```bash
# 저장소 생성
svnadmin create /srv/svn/myrepo

# 덤프 (백업)
svnadmin dump /srv/svn/myrepo > /backup/myrepo_$(date +%Y%m%d).svndump

# 증분 덤프 (r200 이후만)
svnadmin dump /srv/svn/myrepo -r 200:HEAD --incremental >> /backup/myrepo_incr.svndump

# 복원
svnadmin load /srv/svn/myrepo < /backup/myrepo_20260729.svndump

# 핫카피 (운영 중 백업)
svnadmin hotcopy /srv/svn/myrepo /backup/myrepo_hotcopy

# 무결성 검사
svnadmin verify /srv/svn/myrepo

# 로그 조회 (서버측)
svnlook log /srv/svn/myrepo -r 205
svnlook changed /srv/svn/myrepo    # HEAD 변경 파일
svnlook author /srv/svn/myrepo     # HEAD 커밋 작성자
```

### `svnserve` — 데몬 실행

```bash
# 데몬 모드 실행
svnserve -d -r /srv/svn

# 포트 지정 (기본 3690)
svnserve -d -r /srv/svn --listen-port 3691

# systemd 서비스 등록 확인
systemctl status svnserve
systemctl enable svnserve
```

### `/srv/svn/myrepo/conf/svnserve.conf`

```ini
[general]
anon-access = none
auth-access = write
password-db = passwd
authz-db = authz
realm = My SVN Repository
```

### `/srv/svn/myrepo/conf/passwd`

```ini
[users]
Secureuser123 = SecurePassword123
deploy = SecurePassword123
```

### `/srv/svn/myrepo/conf/authz`

```ini
[groups]
dev = Secureuser123, dev2
ops = deploy

[/]
* = r

[/trunk]
@dev = rw

[/branches]
@dev = rw

[/tags]
@dev = r
@ops = rw
```

[⬆ 목차로 돌아가기](#목차)

---

## 13. 실무 팁

### 자격증명 캐시

```bash
# 캐시된 인증 정보 위치
ls ~/.subversion/auth/

# 인증 정보 초기화 (비밀번호 변경 후)
svn auth --remove '*'

# 캐시 없이 실행
svn up --no-auth-cache --non-interactive \
    --username Secureuser123 --password SecurePassword123
```

### 리비전 롤백

```bash
# 특정 리비전으로 로컬 되돌리기 (커밋 안됨)
svn merge -r HEAD:150 .
svn ci -m "revert: r151~HEAD 롤백"

# 단일 커밋 취소 (r205 롤백)
svn merge -c -205 .
svn ci -m "revert: r205 롤백"
```

### 저장소 URL 변경 (서버 이전)

```bash
# SVN 1.7+: Working Copy URL 재설정
svn relocate https://old-svn.example.com/repos/myrepo \
             https://new-svn.example.com/repos/myrepo
```

### 대용량 파일 처리

```bash
# 이진 파일 MIME 타입 설정 (diff 비교 차단)
svn propset svn:mime-type application/octet-stream large_file.bin

# 디렉토리 내 이진 파일 일괄 설정
find . -name "*.png" | xargs -I{} svn propset svn:mime-type image/png {}
```

### 유용한 alias

```bash
# ~/.bashrc 또는 ~/.bash_profile에 추가
alias svnst='svn status'
alias svnup='svn update'
alias svnci='svn commit'
alias svnlog='svn log -l 10 -v'
alias svndiff='svn diff | colordiff'
```

### CI/CD에서 SVN 사용

```bash
# 비대화형 체크아웃 (Jenkins/CI 환경)
svn checkout \
    --non-interactive \
    --no-auth-cache \
    --username Secureuser123 \
    --password SecurePassword123 \
    https://svn.example.com/repos/myrepo/trunk \
    ./workspace

# 현재 리비전 번호 추출 (빌드 버전 태깅용)
REVISION=$(svn info --show-item revision)
echo "Build revision: ${REVISION}"
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Apache Subversion 공식 사이트: [subversion.apache.org](https://subversion.apache.org/) — ★★★☆☆
- SVN Book (공식 매뉴얼): [svnbook.red-bean.com](https://svnbook.red-bean.com/) — ★★★★☆
- Release Notes 1.14: [subversion.apache.org/docs/release-notes/1.14](https://subversion.apache.org/docs/release-notes/1.14.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-29

**마지막 업데이트**: 2026-07-29

© 2026 siasia86. Licensed under CC BY 4.0.
