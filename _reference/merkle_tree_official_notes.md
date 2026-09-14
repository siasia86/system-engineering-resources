---
name: merkle-tree-official-notes
description: RFC 9162와 Git 공식 문서 기반 머클 트리, 증명, Git 객체 그래프 참조 노트.
tags:
  - merkle-tree
  - hash-tree
  - git
  - integrity
  - data-structure
last_checked: 2026-09-14
sources:
  - https://www.rfc-editor.org/rfc/rfc9162.html
  - https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
  - https://git-scm.com/docs/hash-function-transition
  - https://git-scm.com/docs/git-cat-file
  - https://git-scm.com/docs/git-ls-tree
  - https://git-scm.com/docs/git-rev-parse
  - https://git-scm.com/docs/git-fsck
---

# 머클 트리와 Git 객체 그래프 공식 참조 노트

## 목차

| 섹션                                                   |
|--------------------------------------------------------|
| [1. 머클 트리 정의](#1-머클-트리-정의)                 |
| [2. 증명과 복잡도](#2-증명과-복잡도)                   |
| [3. Git 객체 모델](#3-git-객체-모델)                   |
| [4. Git과 머클 트리의 관계](#4-git과-머클-트리의-관계) |
| [5. 무결성 보장의 범위](#5-무결성-보장의-범위)         |
| [6. 공식 검증 명령](#6-공식-검증-명령)                 |

## 1. 머클 트리 정의

RFC 9162의 Certificate Transparency v2는 append-only 로그를 효율적으로 감사하기 위해 이진 머클 트리를 사용합니다.

- 리프 노드는 데이터 항목의 해시입니다.
- 내부 노드는 자식 노드 해시를 결합한 값의 해시입니다.
- 최상위 루트 해시는 전체 데이터 집합과 순서에 대한 단일 커밋먼트입니다.
- RFC 9162는 리프와 내부 노드를 구분하기 위해 각각 `0x00`, `0x01` 접두사를 사용합니다.

```text
MTH({}) = HASH()
MTH({d[0]}) = HASH(0x00 || d[0])
MTH(D_n) = HASH(0x01 || MTH(D[0:k]) || MTH(D[k:n]))
```

`k`는 `n`보다 작은 가장 큰 2의 거듭제곱이며, 입력 개수가 2의 거듭제곱일 필요는 없습니다. 구현마다 홀수 리프 처리와 직렬화 규칙이 다를 수 있으므로 동일한 루트를 비교하려면 알고리즘·순서·인코딩이 같아야 합니다.

## 2. 증명과 복잡도

### 포함 증명

RFC 9162의 Merkle inclusion proof는 특정 리프에서 루트까지 계산하는 데 필요한 형제 노드 해시의 최소 목록입니다. 계산한 루트가 신뢰하는 루트와 같으면 해당 리프가 트리에 포함됐음을 검증할 수 있습니다.

### 일관성 증명

Merkle consistency proof는 이전 트리의 처음 `m`개 입력이 확장된 현재 트리의 처음 `m`개 입력과 같음을 보입니다. Certificate Transparency에서는 append-only 속성을 검증하는 데 사용합니다.

### 일반적인 복잡도

균형 잡힌 이진 머클 트리에서 리프가 `n`개일 때 다음 성질을 가집니다.

| 연산           | 일반적인 복잡도 | 비고                              |
|----------------|-----------------|-----------------------------------|
| 전체 트리 생성 | O(n)            | 모든 리프·내부 노드 계산          |
| 단일 리프 갱신 | O(log n)        | 루트까지의 경로 재계산            |
| 포함 증명 크기 | O(log n)        | 형제 해시 목록                    |
| 포함 증명 검증 | O(log n)        | 경로상의 해시 재계산              |
| 전체 노드 저장 | O(n)            | 구현의 캐시·저장 정책에 따라 차이 |

RFC 9162의 consistency proof 노드 수는 `ceil(log2(n)) + 1` 이하입니다.

## 3. Git 객체 모델

Git 공식 문서는 Git의 핵심을 content-addressable filesystem으로 설명합니다. Git 객체는 객체 타입, 크기, NUL 문자, 객체 내용을 결합한 바이트열을 해시하여 식별합니다.

```text
object_id = HASH(type || " " || size || NUL || content)
```

| 객체     | 공식 객체 내용                                      |
|----------|-----------------------------------------------------|
| `blob`   | 객체 데이터베이스에 저장되는 파일 내용, 파일명 제외 |
| `tree`   | mode·이름·하위 `blob` 또는 `tree` 객체 ID 목록      |
| `commit` | 루트 `tree`, parent commit, 작성자·시간·메시지      |
| `tag`    | 대상 객체, tagger·메시지·선택적 서명                |

Git 공식 문서 기준으로 tree 객체는 UNIX 디렉터리와 비슷하며, 각 항목에 mode, type, filename, 하위 객체 ID를 저장합니다. commit 객체는 프로젝트 스냅샷의 최상위 tree와 0개 이상의 parent commit을 참조합니다.

Git의 기본 객체 형식은 역사적으로 SHA-1을 사용합니다. Git은 hardened SHA-1 구현을 사용하며 SHA-256 객체 형식으로의 전환 기능도 제공합니다. 저장소의 객체 형식은 `git rev-parse --show-object-format`으로 확인합니다.

## 4. Git과 머클 트리의 관계

Git 객체 그래프는 머클 트리의 핵심 성질인 해시 기반 상위 참조를 사용합니다.

1. 파일 내용이 바뀌면 `blob` 객체 ID가 바뀝니다.
2. 해당 `blob`을 포함한 `tree` 객체 내용과 ID가 바뀝니다.
3. 상위 디렉터리 `tree`의 ID가 루트까지 연쇄적으로 바뀝니다.
4. 루트 `tree`를 참조하는 `commit` 객체 ID가 바뀝니다.
5. 변경되지 않은 `blob`과 subtree는 기존 객체 ID를 재사용합니다.

다만 Git 전체는 엄밀한 이진 머클 트리보다 Merkle DAG(Directed Acyclic Graph)로 보는 것이 정확합니다.

- tree 객체는 자식이 두 개로 제한되지 않습니다.
- 여러 tree와 commit이 동일한 객체를 공유할 수 있습니다.
- merge commit은 parent commit을 여러 개 가질 수 있습니다.
- branch와 `HEAD`는 해시 객체가 아니라 객체를 가리키는 변경 가능한 ref입니다.

Git은 Certificate Transparency의 포함 증명·일관성 증명 프로토콜을 그대로 구현하지 않습니다. 두 시스템은 해시로 하위 데이터를 커밋한다는 원리를 공유하지만 목적과 증명 형식은 다릅니다.

## 5. 무결성 보장의 범위

- 객체 ID와 실제 내용의 해시가 다르면 손상이나 잘못된 객체를 탐지할 수 있습니다.
- 하나의 객체가 변경되면 해당 객체를 참조하는 상위 객체 ID도 달라집니다.
- 루트 해시를 신뢰할 수 있어야 검증 결과에 의미가 있습니다.
- 해시만으로 작성자 신원이나 데이터의 정당성을 보장하지 않습니다.
- 공격자가 객체와 ref를 모두 다시 작성할 수 있으면 일관된 새 이력을 만들 수 있습니다.
- 신원과 배포 기준점은 signed commit, signed tag, 보호된 원격 ref 같은 별도 신뢰 수단으로 보완합니다.
- `git fsck`는 객체 연결성과 유효성을 검사하지만, 커밋 내용이 조직 정책상 승인됐는지는 판단하지 않습니다.
- packfile의 delta compression은 저장 최적화이며 객체 ID 계산 원리와 별개입니다.

## 6. 공식 검증 명령

```bash
git rev-parse --show-object-format
git rev-parse --verify 'HEAD^{commit}'
git rev-parse 'HEAD^{tree}'
git cat-file -t HEAD
git cat-file -p HEAD
git cat-file -p 'HEAD^{tree}'
git ls-tree -r HEAD
git fsck --full
```

- `git cat-file -t`: 객체 타입 출력
- `git cat-file -p`: 객체 타입에 맞게 내용 출력
- `git ls-tree -r`: tree의 하위 항목을 재귀적으로 출력
- `git rev-parse --show-object-format`: 저장소의 객체 해시 형식 출력
- `git fsck --full`: 객체 데이터베이스의 연결성과 유효성 검사

## 참고 자료

- RFC 9162: [Certificate Transparency Version 2.0](https://www.rfc-editor.org/rfc/rfc9162.html) — ★★★★☆
- Pro Git: [Git Internals - Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) — ★★★☆☆
- Git Documentation: [hash-function-transition](https://git-scm.com/docs/hash-function-transition) — ★★★☆☆
- Git Documentation: [git-cat-file](https://git-scm.com/docs/git-cat-file) — ★★★☆☆
- Git Documentation: [git-ls-tree](https://git-scm.com/docs/git-ls-tree) — ★★★☆☆
- Git Documentation: [git-rev-parse](https://git-scm.com/docs/git-rev-parse) — ★★★☆☆
- Git Documentation: [git-fsck](https://git-scm.com/docs/git-fsck) — ★★★☆☆
