---
name: svn-official-notes
description: Apache Subversion 공식 문서 기반 핵심 사실, 버전 현황, 아키텍처, 저장소 형식, 주요 명령어 정리. SVN 문서 작성/검토 시 참조.
tags:
  - svn
  - subversion
  - version-control
  - vcs
  - cicd
last_checked: 2026-07-29
sources:
  - https://subversion.apache.org/
  - https://svnbook.red-bean.com/
  - https://subversion.apache.org/docs/release-notes/1.14.html
  - https://svn.apache.org/repos/asf/subversion/trunk/CHANGES
---

# SVN 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-07-29)

| 항목           | 버전   | 비고                             |
|----------------|--------|----------------------------------|
| Stable (LTS)   | 1.14.5 | 출시: 2024-12-08, 현행 권장 버전 |
| 이전 안정 버전 | 1.14.4 | 출시: 2024-10-08                 |
| 개발 중        | 1.15   | in progress (미출시)             |
| EOL            | 1.13   | 이하 모든 버전 지원 종료         |

> 출처: subversion.apache.org 공식 릴리스 공지 (2026-07-29 확인)

## 2. 핵심 개념

| 용어         | 설명                                                            |
|--------------|-----------------------------------------------------------------|
| Repository   | 모든 버전 이력을 저장하는 중앙 저장소 (FSFS 또는 BDB)           |
| Working Copy | 로컬 체크아웃 사본. `.svn/` 디렉토리로 메타데이터 관리          |
| Revision     | 저장소 전체 트리의 상태를 나타내는 전역 순번 (r1, r2, ...)      |
| HEAD         | 저장소의 최신 리비전                                            |
| BASE         | 현재 Working Copy의 기준 리비전 (마지막 체크아웃/업데이트 시점) |
| PREV         | BASE - 1 리비전                                                 |
| COMMITTED    | 파일의 마지막 커밋 리비전                                       |
| trunk        | 메인 개발 라인 (Git의 main에 해당)                              |
| branches/    | 분기 개발 라인                                                  |
| tags/        | 불변 스냅샷 (릴리스 포인트)                                     |

## 3. 저장소 형식

### FSFS (File System File System)

- SVN 1.1+ 기본 포맷. 파일 시스템 기반.
- format 4 (1.6), format 6 (1.8), format 7 (1.9), format 8 (1.10+, LZ4 압축)
- 단순 복사로 백업 가능.

### BDB (Berkeley DB)

- 구버전 포맷. 현재 권장하지 않음.
- 비정상 종료 시 복구 필요 (`svnadmin recover`).

### FSFS format 8 (1.10+)

- LZ4 압축 지원 → 저장 공간 절감.
- sharding: 파일을 1000개 단위로 분산 저장.

> 출처: svnbook.red-bean.com/en/1.7/svn.reposadmin.html

## 4. 아키텍처 — 중앙집중형

```
  Dev A          Dev B          Dev C
  Working Copy   Working Copy   Working Copy
      │               │               │
      └───────────────┼───────────────┘
                      │ svn commit / svn update
                      v
            ┌─────────────────┐
            │   SVN Server    │  (svnserve / Apache httpd + mod_dav_svn)
            │   Repository    │
            │   (FSFS/BDB)    │
            └─────────────────┘
```

- Git과 달리 로컬 저장소 없음. 네트워크 필수.
- 커밋 = 즉시 저장소 반영 (단일 글로벌 리비전 번호 증가).

## 5. 접근 프로토콜

| 프로토콜   | URL 형식               | 비고                                  |
|------------|------------------------|---------------------------------------|
| svn://     | `svn://host/repo`      | svnserve 전용 데몬, 간단 설정         |
| svn+ssh:// | `svn+ssh://host/repo`  | svnserve over SSH, 인증은 SSH 키 사용 |
| http://    | `http://host/repo`     | Apache + mod_dav_svn, WebDAV 기반     |
| https://   | `https://host/repo`    | http의 TLS 버전, 권장                 |
| file://    | `file:///path/to/repo` | 로컬 직접 접근 (단일 사용자)          |

## 6. Working Copy 메타데이터

- `.svn/` 디렉토리: 체크아웃 정보, BASE 리비전 사본, 변경 추적
- SVN 1.7+: `.svn/` 이 최상위 Working Copy 루트 하나만 존재 (1.6 이하는 각 서브디렉토리마다 존재)
- `pristine/`: BASE 리비전의 원본 파일 사본 (diff 계산용)

## 7. 잠금 모델 — Copy-Modify-Merge

| 모델               | 설명                                | SVN 기본값 |
|--------------------|-------------------------------------|------------|
| Copy-Modify-Merge  | 동시 편집 허용, 커밋 시 충돌 해결   | ✅ 기본    |
| Lock-Modify-Unlock | 편집 전 잠금 획득, 이진 파일에 적합 | 선택 사항  |

- `svn:needs-lock` 속성으로 잠금 강제 가능.
- 이진 파일(이미지, Office 문서 등)은 Lock-Modify-Unlock 권장.

## 8. 주요 속성 (svn:*)

| 속성             | 설명                                   |
|------------------|----------------------------------------|
| `svn:ignore`     | 무시할 파일 패턴 (.gitignore 역할)     |
| `svn:externals`  | 외부 저장소 참조 (서브모듈 유사)       |
| `svn:keywords`   | $Rev$, $Date$, $Author$ 등 키워드 치환 |
| `svn:eol-style`  | 줄바꿈 정규화 (native / LF / CRLF)     |
| `svn:mime-type`  | MIME 타입 지정 (이진 판별에 영향)      |
| `svn:needs-lock` | 체크아웃 시 읽기 전용 → 잠금 후 편집   |
| `svn:mergeinfo`  | 병합 이력 추적 (자동 관리)             |

## 9. 관리 명령어 (서버측)

| 명령어                           | 설명                        |
|----------------------------------|-----------------------------|
| `svnadmin create /path/to/repo`  | 저장소 생성 (FSFS 기본)     |
| `svnadmin dump /path/to/repo`    | 저장소 덤프 (백업)          |
| `svnadmin load /path/to/repo`    | 덤프 파일 복원              |
| `svnadmin hotcopy /src /dst`     | 온라인 백업 (운영 중 가능)  |
| `svnadmin verify /path/to/repo`  | 저장소 무결성 검사          |
| `svnadmin recover /path/to/repo` | BDB 저장소 복구             |
| `svnlook log /path/to/repo -r N` | 리비전 N의 로그 메시지 확인 |
| `svnlook changed /path/to/repo`  | HEAD에서 변경된 파일 목록   |

## 10. Git과의 주요 차이

| 항목           | SVN                        | Git                         |
|----------------|----------------------------|-----------------------------|
| 모델           | 중앙집중형                 | 분산형                      |
| 리비전         | 전역 순번 (r1, r2, ...)    | SHA-1/SHA-256 해시          |
| 브랜치         | 디렉토리 복사 (cheap copy) | 포인터 (O(1))               |
| 오프라인 작업  | 제한적 (log, diff 일부)    | 완전 지원                   |
| 커밋 단위      | 저장소 전체 트리           | 변경셋(changeset)           |
| 부분 체크아웃  | 지원 (sparse checkout)     | 미지원 (partial clone 별도) |
| 이진 파일 잠금 | 지원 (svn:needs-lock)      | LFS + 별도 잠금 플러그인    |
| 학습 곡선      | 낮음                       | 높음                        |

## 11. 주의사항

- `svn commit` 은 즉시 저장소에 반영. Git의 `git commit`(로컬)과 다름.
- 병합 이력은 `svn:mergeinfo` 속성으로 관리 → 수동 편집 금지.
- `svn cp` (브랜치/태그 생성)는 cheap copy — 저장소 내 링크이므로 빠름.
- Working Copy 포맷은 SVN 서버 버전보다 최신일 수 없음.
- SVN 1.7+ Working Copy는 SVN 1.6 이하 클라이언트로 열 수 없음.
