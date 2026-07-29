# 버전 관리 시스템 (VCS) 개념
<!-- reference: _reference/svn_official_notes.md -->

## 목차

| 섹션                                                                                                                       |
|----------------------------------------------------------------------------------------------------------------------------|
| [1. VCS란](#1-vcs란) / [2. VCS 분류](#2-vcs-분류) / [3. SVN 아키텍처](#3-svn-아키텍처)                                     |
| [4. 저장소와 Working Copy](#4-저장소와-working-copy) / [5. 리비전 모델](#5-리비전-모델) / [6. 브랜치 전략](#6-브랜치-전략) |
| [7. 병합과 충돌](#7-병합과-충돌) / [8. 잠금 모델](#8-잠금-모델) / [9. SVN vs Git](#9-svn-vs-git)                           |
| [10. 인프라에서의 VCS 활용](#10-인프라에서의-vcs-활용)                                                                     |

---

## 1. VCS란

버전 관리 시스템(Version Control System)은 파일의 변경 이력을 추적하고 관리하는 시스템입니다.

### 핵심 목적

| 목적      | 설명                                     |
|-----------|------------------------------------------|
| 이력 추적 | 누가, 언제, 무엇을, 왜 변경했는지 기록   |
| 협업      | 여러 사람이 동시에 같은 파일을 수정 가능 |
| 롤백      | 이전 상태로 복원                         |
| 분기      | 독립적인 개발 라인(브랜치) 운영          |
| 감사 추적 | 변경 이력 = 자연스러운 감사 로그         |

### VCS 없을 때의 문제

```
myproject_v1/
myproject_v2/
myproject_v2_final/
myproject_v2_final_real/
myproject_v2_final_real_FINAL/   <- 실제 현장에서 자주 발생
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. VCS 분류

### 세대별 분류

| 세대  | 방식       | 대표 도구          | 특징                       |
|-------|------------|--------------------|----------------------------|
| 1세대 | 로컬       | SCCS, RCS          | 단일 파일, 단일 사용자     |
| 2세대 | 중앙집중형 | CVS, **SVN**       | 중앙 서버, 다중 사용자     |
| 3세대 | 분산형     | **Git**, Mercurial | 로컬 저장소, 오프라인 작업 |

### 중앙집중형 vs 분산형

```
Centralized (SVN)                    Distributed (Git)

Developer A   Developer B            Developer A   Developer B
    │               │                Local Repo    Local Repo
    │               │                    │               │
    └───────┬───────┘                    └───────┬───────┘
            v                                    v
      Central Server                    Remote Server (optional)
       Repository                       Remote Repository
```

**중앙집중형 특성:**
- 단일 진실 공급원(Single Source of Truth) — 저장소 = 권위
- 커밋 = 즉시 서버 반영
- 네트워크 단절 시 커밋 불가
- 리비전 번호가 단순하고 직관적 (r1, r2, r3...)
- 권한 관리가 경로 기반으로 세밀함

**분산형 특성:**
- 모든 개발자가 전체 이력 보유
- 오프라인 커밋 가능 → 나중에 push
- 서버 없이도 협업 가능 (peer-to-peer)
- SHA 해시 기반 리비전 (가독성 낮음)

[⬆ 목차로 돌아가기](#목차)

---

## 3. SVN 아키텍처

### 구성 요소

```
┌──────────────┐     ┌─────────────────────────────────┐
│  svn client  │     │          SVN Server             │
│              │     │  svnserve / Apache + mod_dav_svn│
│  Working     │<--->│                                 │
│  Copy        │     │  ┌───────────────────────────┐  │
│  (.svn/)     │     │  │    Repository (FSFS/BDB)  │  │
└──────────────┘     │  └───────────────────────────┘  │
                     └─────────────────────────────────┘
```

### 접근 프로토콜

| 프로토콜     | 서버                 | 인증 방식        | 권장 용도        |
|--------------|----------------------|------------------|------------------|
| `svn://`     | svnserve             | passwd 파일      | 내부망 간단 설정 |
| `svn+ssh://` | svnserve over SSH    | SSH 키/패스워드  | 보안 필요 환경   |
| `https://`   | Apache + mod_dav_svn | LDAP/Active Dir. | 기업 환경 권장   |
| `file://`    | 없음 (로컬 직접)     | OS 파일 권한     | 단일 사용자/백업 |

### 저장소 내부 구조

```
/srv/svn/myrepo/
├── conf/
│   ├── svnserve.conf   # server config
│   ├── passwd          # user/password
│   └── authz           # path-based authorization
├── db/
│   ├── format          # FSFS format version
│   ├── revs/           # revision data (sharding)
│   │   ├── 0/
│   │   └── 1/
│   ├── revprops/       # revision properties (log messages)
│   └── txn-current     # current transaction number
├── hooks/              # hook scripts (pre-commit, etc.)
└── locks/              # file lock info
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 저장소와 Working Copy

### 저장소 (Repository)

저장소는 모든 파일과 디렉토리의 **전체 이력**을 저장합니다. FSFS 형식에서는 리비전 단위로 파일에 저장됩니다.

```
Revision history (repository view)

r1: trunk/  <- initial import
r2: trunk/src/main.py modified
r3: branches/feature-login created (cheap copy of r2 trunk)
r4: branches/feature-login/src/auth.py added
r5: trunk/src/main.py modified again
r6: trunk <- branches/feature-login merged
```

### Working Copy

Working Copy는 저장소의 특정 리비전을 로컬에 체크아웃한 사본입니다.

```
myproject/               <- Working Copy root
├── .svn/                <- metadata (SVN 1.7+: only at root)
│   ├── pristine/        <- BASE revision originals (for diff)
│   ├── wc.db            <- SQLite DB (file status, metadata)
│   └── entries          <- (SVN 1.6 and below, replaced by wc.db in 1.7+)
├── src/
│   └── main.py          <- actual working file
└── README.md
```

### Working Copy 상태 전이

```
Repository
    │
    │ svn checkout
    v
BASE revision state (pristine)
    │
    │ file edit
    v
  Modified (M)
    │
    ├── svn revert  ──────────────────> Back to BASE revision
    │
    └── svn commit  ──────────────────> Repository (new revision created)
                                        BASE = new revision
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 리비전 모델

### 전역 리비전 번호

SVN의 리비전은 저장소 전체의 단일 순번입니다. 파일 하나를 수정해도 저장소 전체 리비전이 증가합니다.

```
r1: initial structure
r2: main.py added          <- main.py First Committed = 2
r3: README.md modified     <- main.py revision is still 2
r4: main.py modified       <- main.py Last Changed Rev = 4
r5: config.py added
```

`svn log main.py`는 r2, r4만 보여줍니다. r3, r5는 main.py와 무관합니다.

### 리비전 키워드 상세

```
Working Copy state (e.g., after "svn up -r 180", HEAD is r185)

HEAD      = r185  (repository latest)
BASE      = r180  (current Working Copy basis)
PREV      = r179  (BASE - 1)
COMMITTED = r175  (last commit of the specific file)
```

### peg revision (페그 리비전)

URL@REV 형식으로 이름이 변경된 파일의 이력을 추적합니다.

```bash
# 현재 이름이 new_name.py이지만, r100 당시 이름으로 이력 추적
svn log new_name.py@HEAD -r 1:100
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 브랜치 전략

### SVN 표준 레이아웃

```
repository/
├── trunk/               <- main development line (keep stable)
├── branches/
│   ├── feature-login/   <- feature development branch
│   ├── hotfix-1.0.1/    <- hotfix branch
│   └── release-2.0/     <- release stabilization branch
└── tags/
    ├── v1.0.0/          <- release tag (do not modify)
    └── v1.1.0/
```

### Cheap Copy 원리

SVN 브랜치/태그 생성은 저장소 내부에서 포인터를 생성하는 것입니다. 실제 파일을 복사하지 않으므로 즉시 완료됩니다.

```
svn copy trunk/ branches/feature-login/

Repository internal:
r50: branches/feature-login/ -> trunk@r49 reference (link)
     (actual file data shared with trunk)

Only subsequent changes are stored separately:
r51: branches/feature-login/src/auth.py (new file)
```

### 브랜치 운영 패턴

| 패턴           | 설명                                               | 적합한 규모    |
|----------------|----------------------------------------------------|----------------|
| Trunk-based    | trunk에서 직접 작업, 태그로 릴리스                 | 소규모 팀      |
| Feature Branch | 기능별 브랜치 → trunk 병합                         | 중소규모       |
| Release Branch | 릴리스마다 브랜치 분리, trunk는 계속 개발          | 여러 버전 유지 |
| Gitflow 유사   | trunk(main) + develop + feature + release + hotfix | 대규모         |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 병합과 충돌

### Copy-Modify-Merge 모델

```
Developer A (from r10)                Developer B (from r10)
    │                                       │
    │ main.py line 10 modified              │ main.py line 25 modified
    │                                       │
    │ svn ci -> r11                         │ svn up (r11 merged)
    │                                       │ -> auto merge (different lines)
    │                                       │ svn ci -> r12
    │
    └── Same line modified simultaneously -> Conflict
```

### 충돌 마커

```python
<<<<<<< .mine
def login(user, pwd):
    return authenticate(user, pwd)   # my change
=======
def login(username, password):
    return auth.verify(username, password)   # server change
>>>>>>> .r211
```

### 3-way merge

SVN은 BASE(공통 조상), 내 변경, 서버 변경을 비교하여 자동 병합합니다.

```
BASE (r10)        My change         Server change (r11)
main.py           main.py           main.py
  line10: A  ->   line10: B   AND    line25: C
  line25: X        line25: X          line10: A

Result: line10=B, line25=C (auto merge success)
```

### svn:mergeinfo

병합 이력을 추적하는 속성입니다. SVN이 자동 관리하므로 직접 편집하지 않습니다.

```bash
svn propget svn:mergeinfo trunk/
# /branches/feature-login:190-205
# -> r190~r205 already merged
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 잠금 모델

### Lock-Modify-Unlock (이진 파일용)

```
Developer A                    Developer B
    │                               │
    │ svn lock design.psd           │
    │ ──> lock acquired             │
    │                               │ svn lock design.psd
    │                               │ ──> FAILED (A holds lock)
    │ edit file                     │
    │ svn ci                        │
    │ svn unlock design.psd         │
    │                               │ svn update
    │                               │ svn lock design.psd
    │                               │ ──> lock acquired
```

### 잠금 모델 선택 기준

| 파일 유형          | 권장 모델          | 이유                                     |
|--------------------|--------------------|------------------------------------------|
| 텍스트 (소스코드)  | Copy-Modify-Merge  | 줄 단위 diff/merge 가능                  |
| 이진 (이미지, PDF) | Lock-Modify-Unlock | diff/merge 불가, 충돌 시 어느 버전 사용? |
| Office 문서        | Lock-Modify-Unlock | 이진 형식, 내용 충돌 해결 어려움         |

[⬆ 목차로 돌아가기](#목차)

---

## 9. SVN vs Git

### 아키텍처 비교

| 항목           | SVN 1.14                   | Git 2.x                      |
|----------------|----------------------------|------------------------------|
| 모델           | 중앙집중형 (CVCS)          | 분산형 (DVCS)                |
| 저장소         | 서버에만 존재              | 모든 클라이언트에 전체 이력  |
| 리비전 식별    | 전역 순번 (r205)           | SHA-1/SHA-256 해시           |
| 브랜치 생성    | 디렉토리 복사 (cheap copy) | 포인터 이동 (O(1), 즉시)     |
| 오프라인 커밋  | 불가                       | 가능 (push는 나중에)         |
| 부분 체크아웃  | 지원 (depth 옵션)          | sparse checkout (별도 설정)  |
| 경로별 권한    | 기본 지원 (authz)          | 기본 미지원 (별도 도구 필요) |
| 이진 파일 잠금 | 기본 지원                  | Git LFS + 별도 잠금 플러그인 |
| 학습 곡선      | 낮음                       | 높음                         |
| 대형 파일 처리 | 보통                       | Git LFS 필요                 |
| 이력 재작성    | 어려움 (서버 관리자 필요)  | 용이 (rebase, amend 등)      |

### SVN이 여전히 유리한 환경

- 레거시 엔터프라이즈 시스템 (이전 비용 > 이득)
- 이진 파일(CAD, 그래픽, Office) 중심 워크플로우
- 경로 기반 세밀한 접근 권한 제어 필수 환경
- Windows 환경에서 TortoiseSVN 활용
- 단순한 선형 이력이 충분한 소규모 팀

### Git 마이그레이션 시 고려사항

```bash
# git svn으로 SVN -> Git 마이그레이션
git svn clone https://svn.example.com/repos/myrepo \
    --trunk=trunk \
    --branches=branches \
    --tags=tags \
    --authors-file=authors.txt \
    ./migrated-repo
```

🟡 `git svn` 은 마이그레이션 용도입니다. 지속적 혼용은 권장하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 인프라에서의 VCS 활용

### 인프라 코드(IaC)와 VCS

| IaC 도구   | VCS 요구사항                              |
|------------|-------------------------------------------|
| Ansible    | Playbook, inventory, vault 파일 버전 관리 |
| Terraform  | `.tf` 파일 버전 관리, `.tfstate` 는 제외  |
| Packer     | 빌드 템플릿 버전 관리                     |
| Kubernetes | YAML 매니페스트 버전 관리 (GitOps)        |

### SVN hooks를 활용한 자동화

```bash
# pre-commit hook: enforce terraform validate on .tf files
# /srv/svn/myrepo/hooks/pre-commit
#!/bin/bash
REPOS="$1"
TXN="$2"

changed=$(svnlook changed -t "$TXN" "$REPOS" | grep '\.tf$')
if [ -n "$changed" ]; then
    echo "Terraform file changed. Run validate before commit." >&2
    # In production: send event to CI server
fi
exit 0
```

훅 종류:

| 훅                   | 실행 시점      | 용도                             |
|----------------------|----------------|----------------------------------|
| `pre-commit`         | 커밋 직전      | 코드 검사, 커밋 메시지 형식 강제 |
| `post-commit`        | 커밋 완료 후   | CI 트리거, 알림 발송             |
| `pre-lock`           | 잠금 획득 직전 | 잠금 권한 검사                   |
| `post-lock`          | 잠금 완료 후   | 알림 발송                        |
| `pre-revprop-change` | 속성 변경 전   | 로그 메시지 수정 제한            |

### 백업 전략

```
Daily incremental dump + Weekly full dump + hotcopy

Every day 00:00   : svnadmin dump --incremental >> /backup/daily.svndump
Every Sunday      : svnadmin hotcopy /srv/svn/myrepo /backup/weekly/
Monthly           : full dump to offsite (S3, tape)
```

```bash
# crontab example
# incremental backup at 2 AM daily
0 2 * * * svnadmin dump /srv/svn/myrepo -r $(cat /var/svn/last_backup_rev):HEAD \
    --incremental >> /backup/svn/myrepo_incr_$(date +\%Y\%m\%d).svndump
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- SVN Book: [svnbook.red-bean.com](https://svnbook.red-bean.com/) — ★★★★☆
- Apache Subversion: [subversion.apache.org](https://subversion.apache.org/) — ★★★☆☆
- Pro Git (Git 비교 참고): [git-scm.com/book](https://git-scm.com/book/ko/v2) — ★★★★☆

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
