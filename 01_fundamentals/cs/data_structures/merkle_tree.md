# 머클 트리와 Git 적용 원리
<!-- reference: _reference/merkle_tree_official_notes.md, _reference/git_official_notes.md -->

머클 트리(Merkle Tree)의 구조와 검증 원리를 설명하고, Git이 파일·디렉터리·커밋을 해시로 연결하여 무결성을 추적하는 방식을 정리합니다.

## 목차

| 섹션                                                                                                                               |
|------------------------------------------------------------------------------------------------------------------------------------|
| [1. 머클 트리 개요](#1-머클-트리-개요) / [2. 구조와 루트 계산](#2-구조와-루트-계산) / [3. 검증 증명](#3-검증-증명)                 |
| [4. 복잡도와 장점](#4-복잡도와-장점) / [5. 유사 구조 비교](#5-유사-구조-비교) / [6. Git의 적용 방식](#6-git의-적용-방식)           |
| [7. Git 변경 전파 사례](#7-git-변경-전파-사례) / [8. Git 객체 실습](#8-git-객체-실습) / [9. 보안 범위와 한계](#9-보안-범위와-한계) |

## 1. 머클 트리 개요

머클 트리는 데이터 블록의 해시를 리프로 두고, 하위 노드의 해시를 결합하여 상위 노드를 반복 계산하는 해시 기반 트리입니다. 최상위 머클 루트(Merkle Root)는 전체 데이터 집합과 순서를 대표하는 짧은 값입니다.

> 커밋먼트(Commitment): 큰 데이터 전체를 공개하지 않고도 특정 시점의 데이터에
> 대응하는 짧은 값을 고정하는 방식입니다. 이후 데이터와 계산 규칙을 제시하면
> 같은 값이 나오는지 검증할 수 있습니다.

### 핵심 성질

- 같은 데이터·순서·인코딩·트리 구성 규칙·해시 알고리즘은 같은 루트를 생성합니다.
- 하나의 리프가 바뀌면 해당 리프에서 루트까지의 해시가 바뀝니다.
- 전체 데이터를 보내지 않고 형제 해시만으로 특정 데이터의 포함 여부를 검증할 수 있습니다.
- 변경되지 않은 subtree 해시는 다시 계산하거나 전송하지 않고 재사용할 수 있습니다.
- 루트 해시만으로 원본 데이터 복원은 불가능하며, 데이터의 비밀성도 제공하지 않습니다.

### 일반 트리와의 차이

일반 트리는 탐색·계층 표현이 목적입니다. 머클 트리는 각 부모가 자식의 내용을 해시로 커밋하므로 데이터 변경 탐지와 부분 검증이 핵심 목적입니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 구조와 루트 계산

RFC 9162의 이진 머클 트리는 리프와 내부 노드의 입력 영역을 구분하기 위해 접두사를 사용합니다.

```text
Leaf(D)        = H(0x00 || D)
Node(L, R)     = H(0x01 || L || R)
Merkle Root    = Node(left_subtree, right_subtree)
```

`H`는 해시 함수이고 `||`는 바이트열 결합입니다. 리프와 내부 노드에 다른 접두사를 사용하는 domain separation은 서로 다른 구조가 같은 해시 입력으로 해석되는 위험을 줄입니다.

> Domain separation: 같은 해시 함수를 여러 용도로 사용할 때 입력 앞에 서로 다른
> 식별값을 붙여 각 용도의 입력 공간을 분리하는 기법입니다.

### 리프 4개의 계산 예시

```text
                         Root
                    H(0x01 || AB || CD)
                         /          \
                        /            \
              AB = H(0x01||A||B)  CD = H(0x01||C||D)
                    /      \           /      \
                   A        B         C        D
              H(0x00||d0) H(...d1) H(...d2) H(...d3)
                   |        |         |        |
                  d0       d1        d2       d3
```

계산 순서는 다음과 같습니다.

1. 각 데이터 `d0`~`d3`의 리프 해시를 계산합니다.
2. 인접한 리프 해시를 왼쪽·오른쪽 순서로 결합하여 `AB`, `CD`를 계산합니다.
3. `AB`, `CD`를 결합하여 루트를 계산합니다.
4. `d2`가 바뀌면 `C`, `CD`, `Root`만 다시 계산합니다.

### 구현별 규칙 차이

머클 트리라는 이름만 같아도 다음 규칙이 다르면 루트가 달라집니다.

| 항목              | 확인할 내용                                     |
|-------------------|-------------------------------------------------|
| 리프 순서         | 입력 정렬 여부와 인덱스 기준                    |
| 리프 인코딩       | 길이·타입·구분자·문자 인코딩                    |
| 노드 결합 순서    | `left || right` 순서 유지 여부                  |
| 홀수 리프 처리    | 마지막 노드 복제, 승격 또는 불균형 subtree 처리 |
| domain separation | 리프·내부 노드 접두사 사용 여부                 |
| 해시 알고리즘     | SHA-256, SHA-512, BLAKE 계열 등                 |

RFC 9162는 입력 개수가 2의 거듭제곱이 아니어도 트리 모양이 유일하게 정해지는 재귀 규칙을 사용합니다. 다른 시스템이 마지막 리프를 복제하는 규칙을 사용하면 같은 데이터라도 루트가 다릅니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 검증 증명

### 포함 증명

포함 증명(Inclusion Proof)은 특정 리프에서 루트까지 올라갈 때 필요한 형제 노드 해시 목록입니다. 리프가 `n`개인 균형 트리에서는 대략 `log2(n)`개의 해시로 검증할 수 있습니다.

앞의 트리에서 `d2`를 검증하려면 다음 값이 필요합니다.

```text
Given:
  d2
  sibling D
  sibling AB
  trusted Root

Verify:
  C      = H(0x00 || d2)
  CD     = H(0x01 || C || D)
  Root'  = H(0x01 || AB || CD)
  accept if Root' == trusted Root
```

검증자는 `d0`, `d1`, `d3`의 원문을 받을 필요가 없습니다. 다만 형제 해시의 좌우 위치와 신뢰할 수 있는 루트가 필요합니다.

### 일관성 증명

일관성 증명(Consistency Proof)은 이전 트리가 현재 트리의 접두 부분이며 기존 항목이 변경·삭제되지 않았음을 검증합니다. RFC 9162의 Certificate Transparency는 append-only 로그가 과거 기록을 바꾸지 않았는지 확인하는 데 사용합니다.

### 증명이 보장하지 않는 것

- 포함 증명은 해당 데이터가 루트에 포함됐음을 보이지만 데이터가 사실이라는 의미는 아닙니다.
- 일반적인 포함 증명만으로 특정 데이터가 없다는 사실을 증명할 수는 없습니다.
- 루트 출처를 인증하지 않으면 공격자가 가짜 데이터로 새 루트를 만들 수 있습니다.
- 서로 다른 사용자에게 다른 루트를 보여 주는 split-view 공격은 루트 서명만으로 막을 수 없습니다. 독립적인 tree head 교환, witness·monitor, 일관성 증명으로 상충하는 관측값을 탐지해야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 복잡도와 장점

리프가 `n`개인 균형 이진 머클 트리를 기준으로 한 일반적인 복잡도입니다.

| 연산           | 시간·크기 복잡도 | 설명                                  |
|----------------|------------------|---------------------------------------|
| 전체 트리 생성 | O(n)             | 모든 리프와 내부 노드 계산            |
| 단일 리프 갱신 | O(log n)         | 리프에서 루트까지 경로 재계산         |
| 포함 증명 생성 | O(log n)         | 내부 노드를 저장한 트리에서 경로 수집 |
| 포함 증명 검증 | O(log n)         | 리프에서 루트까지 해시 재계산         |
| 전체 저장 공간 | O(n)             | 리프·내부 노드 저장                   |

### 실무 장점

- 대규모 데이터에서 일부 항목만 효율적으로 검증합니다.
- 분산 노드가 루트 또는 subtree 해시를 비교해 다른 구간만 찾을 수 있습니다.
- 변경되지 않은 객체와 subtree를 재사용할 수 있습니다.
- 전체 파일 대신 해시를 교환하여 동기화 대상 범위를 좁힐 수 있습니다.
- 서명할 데이터를 전체 데이터가 아닌 루트 해시로 축약할 수 있습니다.

### 비용

- 트리 노드 저장과 해시 계산 비용이 추가됩니다.
- 작은 데이터 집합에서는 전체 해시 목록보다 구현이 복잡할 수 있습니다.
- 갱신 방식에 따라 균형 유지, 캐시 무효화, 동시성 제어가 필요합니다.
- 해시 알고리즘과 직렬화 형식을 변경하면 기존 루트와 호환되지 않을 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 유사 구조 비교

| 구조           | 상위 노드 계산             | 공유 구조 | 대표 목적                     |
|----------------|----------------------------|-----------|-------------------------------|
| 일반 트리      | 해시 연결 없음             | 선택적    | 계층 표현·탐색                |
| 해시 목록      | 항목별 해시 나열           | 없음      | 전체 목록 단순 비교           |
| 이진 머클 트리 | 두 자식 해시 결합          | 보통 없음 | 포함 증명·일관성 검증         |
| Merkle DAG     | 여러 하위 객체 ID 포함     | 있음      | content-addressed 객체 그래프 |
| 해시 체인      | 현재 항목이 이전 해시 포함 | 없음      | 순차 이력 연결                |

Git은 디렉터리 tree가 여러 자식을 가질 수 있고 여러 commit이 동일 객체를 공유하므로 이진 머클 트리보다는 Merkle DAG에 해당합니다. 블록체인의 블록 연결은 해시 체인이고, 각 블록 내부 거래 검증에는 별도의 머클 트리를 사용할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 6. Git의 적용 방식

Git은 content-addressable filesystem으로 동작합니다. 객체 ID는 순번이나 객체 파일의 저장 위치가 아니라 객체 타입·크기·Git 객체 데이터베이스에 저장되는 바이트열을 해시한 값입니다. `blob` 내용에는 파일명이 없지만, `tree` 내용에는 하위 항목의 파일명과 객체 ID가 포함됩니다.

```text
object_id = HASH(type || " " || size || NUL || content)
```

### Git 객체 관계

```text
refs/heads/main
       |
       v
  commit C2 --------------------> parent commit C1
       |
       v
  root tree T2
       |-------------------------|
       v                         v
  blob README                tree src
                                  |
                                  v
                              blob app.py
```

| 객체     | 포함 내용                                           | 머클 구조 역할                   |
|----------|-----------------------------------------------------|----------------------------------|
| `blob`   | 객체 데이터베이스에 저장되는 파일 내용, 파일명 제외 | 데이터 리프                      |
| `tree`   | mode·파일명·하위 blob/tree 객체 ID                  | 디렉터리와 내부 노드             |
| `commit` | 루트 tree ID·parent ID·작성자·시간·메시지           | 스냅샷과 과거 이력의 상위 노드   |
| `tag`    | 대상 객체 ID·tagger·메시지·선택적 서명              | 객체에 이름·메타데이터·서명 부여 |
| `ref`    | Git 객체 ID를 가리키는 변경 가능한 이름             | 해시 객체 그래프 외부의 진입점   |

### Git이 이진 머클 트리가 아닌 이유

- tree 객체는 항목 수만큼 자식을 가집니다.
- merge commit은 parent commit을 두 개 이상 가질 수 있습니다.
- 여러 스냅샷이 동일한 blob과 tree를 공유합니다.
- branch와 `HEAD`는 해시 계산에 포함되지 않는 변경 가능한 ref입니다.

따라서 “Git은 머클 트리를 사용합니다”라는 표현은 핵심 원리를 설명할 때는 유효하지만, 자료구조를 정확히 부를 때는 “Git 객체 저장소는 Merkle DAG입니다”라고 구분하는 편이 적절합니다. 이는 Git이 RFC 9162의 compact inclusion proof나 consistency proof 형식을 제공한다는 의미는 아닙니다.

### 객체 형식

기존 Git 저장소는 일반적으로 SHA-1 객체 형식을 사용하며, 최신 Git은 SHA-256 객체 형식도 지원합니다. 저장소마다 실제 형식을 확인해야 합니다.

```bash
git rev-parse --show-object-format
```

SHA-256 저장소에서는 객체 ID뿐 아니라 tree·commit·tag 내부의 하위 객체 참조도 SHA-256 ID를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. Git 변경 전파 사례

다음 스냅샷에서 `src/app.py`만 변경되는 상황을 가정합니다.

```text
Before commit C1                 After commit C2

C1                               C2
|                                |-- parent: C1
v                                v
T1                               T2
|-- README -> B_readme           |-- README -> B_readme   (reuse)
`-- src -> T_src1                `-- src -> T_src2
           `-- app.py -> B_app1             `-- app.py -> B_app2
```

변경 전파 순서는 다음과 같습니다.

1. `app.py` 내용이 바뀌어 `B_app1`과 다른 `B_app2`가 생성됩니다.
2. `src` tree의 하위 객체 ID가 바뀌어 `T_src2`가 생성됩니다.
3. 루트 tree가 `T_src2`를 참조하므로 `T2`가 생성됩니다.
4. 새 commit은 `T2`와 parent `C1`을 참조하므로 `C2`가 생성됩니다.
5. 변경되지 않은 `README`의 `B_readme` 객체는 그대로 재사용됩니다.

### 변경 유형별 결과

| 변경                  | blob ID      | tree ID      | commit ID    | 이유                                 |
|-----------------------|--------------|--------------|--------------|--------------------------------------|
| 파일 내용 변경        | 변경         | 변경         | 변경         | 새 blob을 tree가 참조                |
| 파일명만 변경         | 유지 가능    | 변경         | 변경         | 파일명은 blob이 아니라 tree에 저장   |
| 권한 mode 변경        | 유지 가능    | 변경         | 변경         | mode는 tree 항목에 저장              |
| commit 메시지만 수정  | 유지         | 유지         | 변경         | 메시지는 commit 객체 내용            |
| 작성 시간·작성자 변경 | 유지         | 유지         | 변경         | 메타데이터는 commit 객체 내용        |
| branch 이름 변경      | 유지         | 유지         | 유지         | ref 이름만 변경, 기존 객체 내용 불변 |
| branch 포인터 이동    | 새 객체 없음 | 새 객체 없음 | 새 객체 없음 | ref 대상만 다른 기존 commit으로 변경 |

`git commit --amend`가 파일 스냅샷을 바꾸지 않아도 commit ID를 바꾸는 이유는 작성 시각·메시지·parent 같은 commit 객체 내용이 달라질 수 있기 때문입니다.

### 저장 효율과 packfile

Git은 변경되지 않은 객체를 객체 ID로 재사용합니다. 이후 `git gc`가 packfile에서 유사 객체를 delta compression할 수 있지만, 이는 저장 방식의 최적화입니다. 객체 ID는 packfile의 delta 표현이 아니라 논리적인 Git 객체 내용으로 계산합니다.

[⬆ 목차로 돌아가기](#목차)

## 8. Git 객체 실습

다음 명령은 현재 저장소를 수정하지 않고 객체 그래프를 조회합니다.

### 객체 형식과 진입점 확인

```bash
git rev-parse --show-object-format
git rev-parse --verify 'HEAD^{commit}'
git rev-parse 'HEAD^{tree}'
```

### commit 객체 확인

```bash
git cat-file -t HEAD
git cat-file -s HEAD
git cat-file -p HEAD
```

`git cat-file -p HEAD` 출력에서 루트 `tree` ID, parent commit ID, 작성자, committer, 메시지를 확인할 수 있습니다.

### tree와 blob 연결 확인

```bash
git cat-file -p 'HEAD^{tree}'
git ls-tree HEAD
git ls-tree -r HEAD
git rev-parse 'HEAD:README.md'
git cat-file -t 'HEAD:README.md'
```

`git ls-tree -r HEAD`는 mode, 객체 타입, 객체 ID, 경로를 출력합니다. 파일명은 tree에 있고 `HEAD:README.md`가 가리키는 객체 타입은 일반 파일이면 `blob`입니다.

### 객체 무결성 검사

```bash
git fsck --full
```

`git fsck --full`은 객체 데이터베이스의 연결성과 객체 유효성을 검사합니다. dangling object는 ref에서 도달할 수 없는 객체를 의미하며, 메시지가 존재한다는 이유만으로 현재 이력이 손상됐다고 단정하지 않습니다.

### 변경 전후 객체 비교

현재 commit과 첫 번째 parent가 모두 존재할 때 다음 명령으로 루트 tree를 비교할 수 있습니다.

```bash
git rev-parse 'HEAD^{tree}'
git rev-parse 'HEAD^1^{tree}'
git diff-tree --no-commit-id --name-status -r 'HEAD^1' HEAD
```

루트 tree ID가 같아도 commit 메시지나 메타데이터가 다르면 commit ID는 달라질 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 9. 보안 범위와 한계

### 무결성과 인증의 구분

머클 구조와 Git 객체 ID는 내용 변경을 연결된 해시 변화로 드러냅니다. 그러나 해시가 일치한다는 사실만으로 작성자, 승인 여부, 원격 서버의 신뢰성을 보장하지 않습니다.

| 요구사항                | 객체 해시만으로 충족 | 추가 수단                                |
|-------------------------|----------------------|------------------------------------------|
| 우발적 손상 탐지        | 가능                 | `git fsck`, 전송 재시도                  |
| 객체 간 연결 검증       | 가능                 | 신뢰하는 commit 또는 root ID             |
| 작성자 신원 확인        | 불가                 | signed commit, signed tag                |
| 승인된 배포 확인        | 불가                 | 보호 브랜치, CI 정책, 서명 검증          |
| 데이터 기밀성           | 불가                 | 저장·전송 암호화, 접근 제어              |
| 악의적 이력 재작성 탐지 | 조건부               | 외부에 고정한 commit ID, 서명, 감사 로그 |

### 신뢰 기준점

공격자가 객체와 branch ref를 함께 바꿀 수 있으면 새로운 객체 ID로 일관된 가짜 이력을 만들 수 있습니다. 검증자는 다음 중 하나 이상의 신뢰 기준점을 별도로 가져야 합니다.

- 서명된 commit 또는 annotated tag
- 보호된 원격 branch와 강제 push 제한
- CI/CD가 기록한 승인 commit ID
- 독립 시스템에 보관한 release manifest
- append-only 감사 로그 또는 transparency log

### 운영 주의사항

- 짧게 축약한 객체 ID는 저장소가 커질수록 모호해질 수 있으므로 자동화에서는 전체 ID 또는 `git rev-parse --verify`를 사용합니다.
- SHA-1과 SHA-256 저장소의 객체 ID 길이와 내부 참조 형식이 다르므로 40자리로 고정한 파서를 사용하지 않습니다.
- `git fsck` 성공은 코드가 안전하거나 승인됐음을 의미하지 않습니다.
- Git 객체 해시는 파일 권한 전체가 아니라 Git이 지원하는 제한된 mode만 반영합니다.
- 파일의 mtime과 일반적인 파일시스템 소유자는 commit 객체에 저장되지 않습니다.
- 비밀정보를 커밋하면 객체가 content-addressed 형태로 이력에 남으므로 해시 구조가 삭제나 접근 통제를 대신하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- [머클 트리 공식 참조 노트](../../../_reference/merkle_tree_official_notes.md)
- [Git 공식 참조 노트](../../../_reference/git_official_notes.md)
- [Git 개념](../git_concepts.md)
- [이진 트리](binary_tree.md)
- [해시 테이블](hash_table.md)
- RFC 9162: [Certificate Transparency Version 2.0](https://www.rfc-editor.org/rfc/rfc9162.html) — ★★★★☆
- Pro Git: [Git Internals - Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) — ★★★☆☆
- Git Documentation: [hash-function-transition](https://git-scm.com/docs/hash-function-transition) — ★★★☆☆
- Git Documentation: [git-cat-file](https://git-scm.com/docs/git-cat-file) — ★★★☆☆
- Git Documentation: [git-ls-tree](https://git-scm.com/docs/git-ls-tree) — ★★★☆☆
- Git Documentation: [git-fsck](https://git-scm.com/docs/git-fsck) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-14

**마지막 업데이트**: 2026-09-14

© 2026 siasia86. Licensed under CC BY 4.0.
