# Git 이력 민감 파일 제거 런북

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 사전 판단](#2-사전-판단) / [3. 노출 범위 진단](#3-노출-범위-진단)                         |
| [4. 백업](#4-백업) / [5. 이력 재작성](#5-이력-재작성) / [6. 로컬 검증](#6-로컬-검증)                               |
| [7. Force push](#7-force-push) / [8. 잔존 노출 처리](#8-잔존-노출-처리) / [9. 재발 방지](#9-재발-방지)             |
| [10. 예상하지 못한 상황](#10-예상하지-못한-상황) / [11. 전체 흐름](#11-전체-흐름) / [12. 참고 자료](#12-참고-자료) |

---

## 1. 개요

공개 저장소에 개인정보나 저작권 제한 자료를 커밋한 뒤 이를 제거하는 절차입니다.

핵심 전제는 다음 세 가지입니다.

- 최신 커밋에서 파일을 지워도 **과거 커밋의 blob은 그대로 남습니다.**
- `.gitignore`는 **이미 추적 중인 파일에 작용하지 않습니다.**
- Force push 후에도 원격 호스팅은 **unreachable 객체를 일정 기간 보유합니다.**

즉 조치는 3단으로 나뉩니다.

| 단계 | 목적                | 도구                    |
|------|---------------------|-------------------------|
| 1단  | 현재 추적 중단      | `git rm --cached`       |
| 2단  | 과거 이력 제거      | `git filter-repo`       |
| 3단  | 원격 잔존 객체 제거 | 호스팅 서비스 지원 요청 |

1단만 수행하고 완료로 판단하는 것이 가장 흔한 실수입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 사전 판단

이력 재작성은 되돌리기 어렵습니다. 먼저 정말 필요한지 판단합니다.

| 유형                          | 조치 수준                       |
|-------------------------------|---------------------------------|
| 개인정보 (실명·연락처·식별자) | 이력 제거 + 지원 요청           |
| 자격증명 (키·토큰·패스워드)   | **즉시 폐기·교체** 후 이력 제거 |
| 저작권 제한 자료              | 이력 제거 + 지원 요청           |
| 대용량 바이너리 (용량 문제)   | 이력 제거 (긴급도 낮음)         |
| 단순 오커밋 (민감성 없음)     | 최신 커밋 정리만                |

🟡 자격증명이 유출된 경우 이력 제거보다 **키 교체가 우선**입니다. 이력을 지워도 이미 취득된 키는 유효합니다.

### 판단 기준

- 저장소가 public인지 private인지 확인합니다.
- 노출 기간이 얼마인지 확인합니다.
- 협업자·CI·다른 클론이 존재하는지 확인합니다.
- 파일에 실제로 민감 정보가 있는지 **내용을 열어** 확인합니다.

파일명만 보고 판단하면 오판합니다. 행정문서로 보이는 PDF에 실명 목록이 들어 있는 사례가 있습니다.

```bash
pdftotext -layout target.pdf - | grep -n -E '성\s*명|이름|연락처|주민|이메일' | head
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 노출 범위 진단

무엇을 어디까지 지울지 먼저 확정합니다.

### 추적 상태 확인

```bash
REPO=/path/to/repo
TARGET='path/to/sensitive.pdf'

git -C "${REPO}" ls-files --error-unmatch "${TARGET}"
git -C "${REPO}" check-ignore -v --no-index "${TARGET}"
```

### 이력 존재 확인

```bash
git -C "${REPO}" log --all --oneline -- "${TARGET}"
git -C "${REPO}" branch -a --contains <commit>
```

### 이력 내 동종 파일 전수 조사

한 건만 지우면 나머지가 남습니다. 확장자 단위로 훑습니다.

```bash
git -C "${REPO}" rev-list --all --objects \
  | git -C "${REPO}" cat-file --batch-check='%(objecttype) %(objectname) %(rest)' \
  | grep '^blob' | grep -iE '\.(pdf|xlsx|zip|pem|key)$' \
  | sed 's/^blob [0-9a-f]* //' | sort -u
```

### 원격 반영 여부

```bash
git -C "${REPO}" remote -v
git -C "${REPO}" ls-remote origin
```

저장소 공개 여부는 API로 확인합니다.

```bash
curl -sS -H 'Accept: application/vnd.github+json' \
  https://api.github.com/repos/<owner>/<repo> \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["visibility"])'
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 백업

이력 재작성의 유일한 복구 수단입니다. 생략하면 안 됩니다.

```bash
REPO=/path/to/repo
TS=$(date +%Y%m%d_%H%M%S)
BK=/root/backup_git/${TS}
mkdir -p "${BK}"

git clone --mirror "${REPO}" "${BK}/repo.git"

git -C "${BK}/repo.git" fsck --no-progress
git -C "${BK}/repo.git" show-ref | wc -l
git -C "${BK}/repo.git" ls-tree -r <commit> --name-only -- path/to/dir/
```

### 워킹트리 전용 파일도 백업

`git rm --cached`로 추적만 해제한 파일은 Git에 없습니다. 이력 재작성 도구가 워킹트리를 리셋하므로 별도 보관합니다.

```bash
mkdir -p "${BK}/local_only"
cp -a "${REPO}/path/to/dir/"*.pdf "${BK}/local_only/"

cd "${REPO}/path/to/dir"
for f in *.pdf; do
  a=$(sha256sum "$f" | cut -c1-12)
  b=$(sha256sum "${BK}/local_only/$f" | cut -c1-12)
  [ "$a" = "$b" ] && echo "OK   $f" || echo "FAIL $f"
done
```

🟡 `cp`나 `ls`의 종료 코드만 믿지 말고 **해시로 대조**합니다. 권한 문제로 글로브가 확장되지 않아 조용히 실패하는 경우가 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 이력 재작성

`git filter-repo`를 사용합니다. `filter-branch`는 느리고 오류가 잦아 권장되지 않습니다.

### 대상 경로 파일 작성

파일명에 공백·괄호·한글이 있으면 `--path` 인자 전달에서 깨질 수 있습니다. `--paths-from-file`을 사용합니다.

```bash
cat > /tmp/remove_paths.txt <<'EOF'
path/to/sensitive one.pdf
path/to/(attachment) report.pdf
path/to/personal data.xlsx
EOF

cat -A /tmp/remove_paths.txt
```

### 사전 확인

```bash
cd "${REPO}"
while IFS= read -r p; do
  printf '%s commits : %s\n' "$(git log --all --oneline -- "$p" | wc -l)" "$p"
done < /tmp/remove_paths.txt
```

0으로 나오면 경로가 틀린 것입니다. 재작성해도 아무것도 지워지지 않습니다.

### 실행

```bash
cd "${REPO}"
git filter-repo --invert-paths --paths-from-file /tmp/remove_paths.txt --force
```

출력에서 확인할 것들입니다.

```
Parsed N commits
NOTICE: Removing 'origin' remote
New history written in ...
Completely finished after ...
```

🟡 `filter-repo`는 실행 후 **`origin` 원격을 자동 제거**합니다. 의도된 안전장치이며 나중에 다시 등록해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 로컬 검증

Force push 전에 반드시 로컬에서 확인합니다. push 후에는 되돌리기 비용이 급증합니다.

### 대상 경로 제거 확인

```bash
cd "${REPO}"
while IFS= read -r p; do
  printf 'main=%s dev=%s : %s\n' \
    "$(git log --oneline main -- "$p" | wc -l)" \
    "$(git log --oneline <branch> -- "$p" | wc -l)" "$p"
done < /tmp/remove_paths.txt
```

🟡 `git log --all`은 `refs/remotes/*`를 포함합니다. `fetch`를 한 상태라면 원격 추적 ref에 옛 이력이 남아 **제거 실패로 오판**합니다. 로컬 브랜치를 명시해 확인합니다.

어떤 ref가 옛 이력을 보유하는지 분리해 봅니다.

```bash
git for-each-ref --format='%(refname)' | while read -r r; do
  n=$(git log --oneline "$r" -- 'path/to/sensitive.pdf' 2>/dev/null | wc -l)
  [ "$n" -gt 0 ] && echo "HAS OLD: $r ($n)"
done
```

`refs/remotes/origin/*`만 나오면 정상입니다. Force push로 정리됩니다.

### 손실 여부 확인

| 확인 항목     | 명령                            | 기대                  |
|---------------|---------------------------------|-----------------------|
| 커밋 총수     | `git rev-list --all --count`    | 재작성 전과 동일      |
| 태그          | `git tag`                       | 보존                  |
| 브랜치        | `git branch -vv`                | 전부 존재, SHA만 변경 |
| 워킹트리 파일 | `ls path/to/dir/`               | 로컬 전용 파일 보존   |
| 문서 내용     | `grep -c '<수정 문구>' file.md` | 최근 변경분 보존      |

커밋 수가 줄었다면 경로 지정이 과했다는 뜻입니다. 백업에서 다시 시작합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Force push

### 원격 재등록

```bash
git -C "${REPO}" remote add origin <remote-url>
git -C "${REPO}" remote -v
```

### 원격 현재값 확인

push 직전에 반드시 원격 SHA를 확인합니다.

```bash
git -C "${REPO}" ls-remote origin refs/heads/main refs/heads/<branch>
```

기억하던 값과 다르면 **누군가 또는 CI가 새 커밋을 올린 것**입니다. 그대로 force push하면 유실됩니다.

### `--force-with-lease` 사용

```bash
git -C "${REPO}" push \
  --force-with-lease=refs/heads/<branch>:<expected-remote-sha> \
  origin <branch>
```

`--force`는 조건 없이 덮어씁니다. `--force-with-lease`는 원격이 예상값일 때만 진행하므로 동시 변경을 잡아냅니다.

### 새 커밋이 있었다면

재작성된 이력 위로 옮겨 담습니다.

```bash
git -C "${REPO}" fetch origin
git -C "${REPO}" log -1 --format='%an <%ae> %s' <new-remote-sha>
git -C "${REPO}" cherry-pick <new-remote-sha>
```

`cherry-pick`은 부모가 사라진 커밋도 diff 기준으로 적용되며 작성자 정보를 유지합니다.

### 사후 정리

```bash
git -C "${REPO}" fetch origin --prune
git -C "${REPO}" branch --set-upstream-to=origin/<branch> <branch>

git -C "${REPO}" reflog expire --expire=now --expire-unreachable=now --all
git -C "${REPO}" gc --prune=now
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 잔존 노출 처리

Force push는 **참조만 끊습니다.** 객체는 원격에 남습니다.

### 실제 잔존 여부 확인

```bash
API=https://api.github.com/repos/<owner>/<repo>

curl -sS -o /dev/null -w '%{http_code}\n' \
  "https://raw.githubusercontent.com/<owner>/<repo>/<old-commit>/<path>"

curl -sS -o /dev/null -w '%{http_code}\n' "${API}/commits/<old-commit>"
curl -sS -o /dev/null -w '%{http_code}\n' "${API}/git/blobs/<blob-sha>"
```

전형적인 결과입니다.

| 접근 경로              | 결과    | 의미               |
|------------------------|---------|--------------------|
| raw (경로 기반)        | 404     | 경로 조회는 차단   |
| API `/commits/<sha>`   | 200     | 커밋 객체 잔존     |
| API `/git/trees/<sha>` | 200     | 파일 목록 노출     |
| API `/git/blobs/<sha>` | **200** | **내용 취득 가능** |

즉 SHA를 아는 사람은 여전히 파일을 받을 수 있습니다.

### 지원 요청

호스팅 서비스가 GC를 수행해야 완결됩니다. 사용자가 강제할 수단은 없습니다.

```
접수: https://support.github.com/contact
```

요청에 포함할 항목입니다.

- 저장소 식별자
- 요청 내용: force push 이후 남은 unreachable objects의 GC 및 캐시 무효화
- 사유: 개인정보 또는 저작권 제한 자료 포함
- 대상 커밋 SHA와 blob SHA
- 조치 완료 회신 요청

🟡 blob SHA를 공개 문서나 이슈에 적으면 오히려 노출을 확대합니다. 비공개 지원 채널로만 전달합니다.

### 회수 불가 영역

- 공개 기간 중 클론·크롤링된 사본
- 검색 엔진·아카이브 서비스 캐시
- 포크된 저장소 (포크는 별도 GC 대상)

개인정보라면 이 한계를 전제로 후속 대응을 판단해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 재발 방지

### 화이트리스트 방식 `.gitignore`

파일명을 하나씩 등록하는 방식은 누락됩니다. 확장자 단위로 막고 예외만 허용합니다.

```gitignore
path/to/reference/*.pdf
path/to/reference/*.hwp
path/to/reference/*.hwpx
!path/to/reference/public_document.pdf
```

동작을 실제로 테스트합니다.

```bash
WORK=$(mktemp -d); cd "${WORK}"; git init -q .
mkdir -p path/to/reference
cp /path/to/.gitignore .
: > 'path/to/reference/new file.pdf'
git status --porcelain --untracked-files=all
```

`status`에 나타나지 않으면 차단 성공입니다.

### 제약 사항

| 제약                  | 내용                                       |
|-----------------------|--------------------------------------------|
| 추적 중 파일          | `.gitignore` 무효 — `git rm --cached` 필요 |
| 부모 디렉터리 제외 시 | 하위 `!` 부정 패턴이 동작하지 않음         |
| 파일명 변경           | 파일명 기반 화이트리스트가 깨짐            |
| 후행 공백             | 무시됨 — 필요 시 `\ `로 이스케이프         |
| 인용부호              | `"..."`는 문자로 취급되어 매칭 실패        |

### 디렉터리 분리 (권장)

파일이 늘어날 예정이면 정책을 디렉터리로 표현합니다.

```
_reference/
├── public/    공개 가능 — 추적
└── local/     저작권·개인정보 — 제외
```

```gitignore
path/to/_reference/local/
```

### 커밋 전 자동 점검

```bash
gitleaks protect --staged --redact --no-banner || exit 1
```

바이너리 첨부는 `gitleaks`로 잡히지 않습니다. 확장자 차단과 병행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 예상하지 못한 상황

실제 작업에서 발생한 함정들입니다. 대부분 **검증 방법 자체가 틀려서** 잘못된 안심으로 이어집니다.

### 10.1 최신 커밋 삭제를 완료로 착각

```
증상: git rm --cached 후 .gitignore 등록까지 마쳐 조치 완료로 판단
원인: 과거 커밋의 blob 은 그대로 존재
확인: git log --all --oneline -- <path>
대응: 이력 재작성 필요
```

### 10.2 `check-ignore` 종료 코드 오해

```
증상: 부정 패턴(!) 대상인데 IGNORED 로 판정
원인: -v 옵션은 부정 패턴 매칭에도 종료 코드 0 반환
확인: 출력 패턴의 ! 접두사로 판단
대응: 별도 저장소에서 status --porcelain -uall 로 확정
```

종료 코드가 아니라 출력 내용을 읽어야 합니다.

### 10.3 `sudo` 아래 글로브 미확장

```
증상: cp 가 성공한 듯 보이나 백업 디렉터리가 비어 있음
원인: 글로브가 호출 사용자 권한으로 확장되어 경로 접근 실패
확인: 해시 대조
대응: sudo bash -c '...' 로 root 셸에서 확장
```

`2>/dev/null`과 결합되면 실패가 완전히 은폐됩니다.

### 10.4 `--all`에 원격 추적 ref 포함

```
증상: filter-repo 후에도 제거 대상이 이력에 남아 있다고 표시
원인: git log --all 이 refs/remotes/* 를 포함
확인: 로컬 브랜치 명시 후 재확인
대응: for-each-ref 로 보유 ref 를 분리 확인
```

### 10.5 `filter-repo`가 origin 제거

```
증상: 재작성 후 git push 가 원격을 찾지 못함
원인: 실수 push 방지를 위한 의도된 동작
대응: git remote add origin <url> 로 재등록
```

### 10.6 `already_ran` 마커

```
증상: The previous run is older than a day 경고
원인: 과거에 filter-repo 를 실행한 저장소
대응: 연속 실행 여부를 판단하고 --force 로 진행
```

과거 재작성 이력이 있다는 신호이므로 백업 중요도가 더 높습니다.

### 10.7 push 직전 CI 봇 커밋 유입

```
증상: 원격 SHA 가 기억하던 값과 다름
원인: GitHub Actions 등이 날짜 갱신 커밋을 push
확인: git log -1 --format='%an <%ae> %s' <remote-sha>
대응: cherry-pick 으로 재작성 이력 위에 재적용
```

`--force`만 썼다면 조용히 유실됩니다. `--force-with-lease`가 이를 잡아냅니다.

### 10.8 Force push 후에도 원격에서 취득 가능

```
증상: 이력 제거·force push 완료 후에도 API blob 조회가 200
원인: unreachable 객체는 호스팅 GC 까지 잔존
확인: API /git/blobs/<sha>
대응: 지원 요청 (사용자가 GC 강제 불가)
```

가장 오해가 큰 지점입니다. **force push는 완결이 아닙니다.**

### 10.9 커밋 분리 실패

```
증상: 문서 수정 커밋에 파일 삭제가 함께 포함
원인: 앞선 git rm --cached 결과가 인덱스에 남아 있었음
확인: git diff --cached --name-status 로 스테이징 사전 확인
대응: push 전이면 git reset --soft HEAD~1 후 재구성
```

`reset --soft`는 인덱스를 보존하므로 안전하고 reflog로 복구 가능합니다.

### 10.10 무해해 보이는 파일에 개인정보

```
증상: 행정문서 PDF 에 실명·소속 목록 포함
원인: 파일명만으로 판단
확인: pdftotext 로 내용 점검
대응: 개인정보 기준으로 우선순위 상향
```

### 10.11 문서 본문 오염 여부

원문 파일을 제거해도 Markdown 본문에 내용이 옮겨져 있으면 의미가 없습니다.

```bash
python3 - <<'PY'
import re
doc = open('target.md', encoding='utf-8').read()
src = open('extracted.txt', encoding='utf-8').read()
names = set(re.findall(r'^([가-힣]{3})\s{2,}', src, re.M))
hit = sorted(n for n in names if n in doc)
print(f'후보 {len(names)}건 / 문서 유입 {len(hit)}건')
PY
```

### 10.12 로컬 파일 참조가 깨짐

원문을 추적 해제하면 문서의 로컬 경로 참조가 무효가 됩니다. 공식 출처 링크로 대체합니다.

```markdown
- 기관명. 「문서명」: [도메인](https://example.com/article?id=123) — ★★★☆☆
```

대체 전에 원격 파일과 로컬 파일의 해시를 대조해 **동일 자료임을 확인**합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 전체 흐름

```
          Sensitive file committed
                     │
                     v
          ┌────────────────────┐
          │ 1. Assess          │  content check, not filename
          └────────────────────┘
                     │
                     v
          ┌────────────────────┐
          │ 2. Scope           │  tracked / history / remote / public
          └────────────────────┘
                     │
                     v
          ┌────────────────────┐
          │ 3. Backup          │  mirror + local-only, verify by hash
          └────────────────────┘
                     │
                     v
          ┌────────────────────┐
          │ 4. Untrack         │  git rm --cached + gitignore
          └────────────────────┘
                     │
                     v
          ┌────────────────────┐
          │ 5. Rewrite         │  git filter-repo
          └────────────────────┘
                     │
                     v
          ┌────────────────────┐
          │ 6. Verify locally  │  local branches only
          └────────────────────┘
                     │
                     v
          ┌────────────────────┐
          │ 7. Force push      │  --force-with-lease
          └────────────────────┘
                     │
                     v
          ┌────────────────────┐
          │ 8. Support ticket  │  remote GC request
          └────────────────────┘
                     │
                     v
          ┌────────────────────┐
          │ 9. Prevent         │  whitelist gitignore + hooks
          └────────────────────┘
```

각 단계 앞에서 검증을 통과하지 못하면 다음 단계로 넘어가지 않습니다.

### 체크리스트

| 순서 | 항목                                 | 완료 기준                |
|------|--------------------------------------|--------------------------|
| 1    | 파일 내용 확인                       | 민감 정보 유형 확정      |
| 2    | 자격증명 포함 시 키 교체             | 폐기·재발급 완료         |
| 3    | 미러 백업 + 해시 대조                | `fsck` 통과, 해시 일치   |
| 4    | 워킹트리 전용 파일 백업              | 해시 일치                |
| 5    | 대상 경로 사전 확인                  | commits 수 > 0           |
| 6    | `filter-repo` 실행                   | `Completely finished`    |
| 7    | 로컬 브랜치 기준 제거 확인           | 전부 0                   |
| 8    | 커밋 수·태그·브랜치 보존 확인        | 재작성 전과 동일         |
| 9    | 원격 SHA 사전 확인                   | 기억값과 일치            |
| 10   | 신규 커밋 있으면 cherry-pick         | 작성자 보존              |
| 11   | `--force-with-lease` push            | `forced update`          |
| 12   | 로컬 `gc --prune=now`                | blob `cat-file -e` 실패  |
| 13   | 원격 잔존 확인                       | API 응답 기록            |
| 14   | 지원 요청 접수                       | 티켓 번호 확보           |
| 15   | `.gitignore` 화이트리스트화 + 테스트 | 신규 파일 차단 확인      |
| 16   | 백업 보관 정책 결정                  | 보관 기간·삭제 시점 명시 |

🟡 백업 미러에는 민감 파일이 그대로 있습니다. 복구 목적이 끝나면 삭제 시점을 정해 관리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 12. 참고 자료

- git-filter-repo: [github.com/newren/git-filter-repo](https://github.com/newren/git-filter-repo) — ★★★☆☆
- GitHub Docs 민감 데이터 제거: [docs.github.com](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) — ★★★☆☆
- Git gitignore 명세: [git-scm.com/docs/gitignore](https://git-scm.com/docs/gitignore) — ★★★☆☆
- Git push 옵션: [git-scm.com/docs/git-push](https://git-scm.com/docs/git-push) — ★★★☆☆
- GitHub Support: [support.github.com/contact](https://support.github.com/contact) — ★★☆☆☆
- [.gitignore 패턴 정리](gitignore_patterns.md)
- [Git 명령어 레퍼런스](git_command_reference.md)

[⬆ 목차로 돌아가기](#목차)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-26

**마지막 업데이트**: 2026-08-26

© 2026 siasia86. Licensed under CC BY 4.0.
