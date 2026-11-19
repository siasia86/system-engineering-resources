# Claude Code 설정 파일 가이드
<!-- reference: _reference/claude_code_official_notes.md -->

Claude Code의 설정 파일(`settings.json`)을 자세히 정리합니다. 설정 파일의 층과 우선순위, 저장소에 공유할 설정과 개인 설정의 구분, 권한 규칙 문법, 실수를 막는 `permissions.deny`·`ask`·`allow` 후보, hook 실패 시 동작과 배포 방식, Codex 대응 설정을 다룹니다. 지침 파일과 확장 기능 전반은 [확장 기능 가이드](claude_code_extensions_guide.md), 권한 모드는 [Linux CLI 가이드](claude_code_cli_linux_guide.md)를 참고합니다.

- 기준: code.claude.com 공식 문서(settings·permissions·hooks·settings-reference, 2026-11-19 확인), 로컬 Claude Code `2.1.311`
- 이 문서는 설명 자료입니다. 규칙 예시는 공식 문법으로 정리한 후보이며, 실제 세션에서 일치 여부를 시험하지는 않았습니다.

## 목차

| 단계 | 섹션                                                                                                                       |
|------|----------------------------------------------------------------------------------------------------------------------------|
| 구조 | [1. 설정 파일 층](#1-설정-파일-층) / [2. 우선순위와 병합](#2-우선순위와-병합) / [3. 공유와 개인 구분](#3-공유와-개인-구분) |
| 규칙 | [4. 권한 규칙 문법](#4-권한-규칙-문법) / [5. deny와 ask 후보](#5-deny와-ask-후보) / [6. allow 후보](#6-allow-후보)         |
| 보호 | [7. 안전 설정](#7-안전-설정) / [8. hook 실패 시 동작](#8-hook-실패-시-동작) / [9. hook 배포 방식](#9-hook-배포-방식)       |
| 운영 | [10. Codex 대응 설정](#10-codex-대응-설정) / [11. 적용과 확인](#11-적용과-확인) / [12. 참고 자료](#12-참고-자료)           |

---

## 1. 설정 파일 층

| 범위          | 파일                                                   | 적용 대상                                    | 넣을 내용                                        |
|---------------|--------------------------------------------------------|----------------------------------------------|--------------------------------------------------|
| 사용자        | `~/.claude/settings.json`                              | 이 PC의 모든 프로젝트에서 나                 | 테마, 기본 모델, 개인 권한 규칙                  |
| 공유 프로젝트 | `.claude/settings.json`                                | 이 폴더에서 일하는 모두 (commit하면 팀 전체) | 팀 권한 규칙, hook, plugin, 필요한 환경 변수     |
| 개인 프로젝트 | `.claude/settings.local.json`                          | 이 프로젝트에서 나                           | 한 프로젝트의 개인 예외, 공유 전 시험            |
| 조직 관리     | `managed-settings.json`, MDM 정책, claude.ai 콘솔 설정 | 조직이 배포한 모든 PC                        | 보안 정책, 준수 요건                             |
| 내부 상태     | `~/.claude.json`                                       | 이 PC의 나                                   | 계정, MCP 서버, 폴더 신뢰 기록 (직접 편집 안 함) |

- 설치만으로는 설정 파일이 생기지 않습니다. `/config`에서 값을 바꾸면 `~/.claude/settings.json`이, 권한 확인 창에서 "Yes, and don't ask again"을 고르면 `.claude/settings.local.json`이 생깁니다.
- Claude Code가 `.claude/settings.local.json`을 처음 쓸 때 전역 git exclude 파일에 `**/.claude/settings.local.json`을 추가합니다. 직접 만든 파일은 `.gitignore`에 직접 추가합니다.
- Git 저장소의 하위 폴더에서 시작해도 `.claude/settings.local.json`은 저장소 루트의 파일을 읽고 씁니다(v2.1.211 이후). worktree에서는 원래 checkout 루트의 파일을 씁니다.
- 공유 파일 `.claude/settings.json`은 세션의 주 작업 폴더에서 읽습니다. 저장소 루트에 commit한 파일을 쓰려면 루트에서 시작합니다.
- 설정 파일은 엄격한 JSON입니다. `//` 주석이나 끝의 쉼표가 있으면 오류가 납니다. 편집기 자동 완성을 쓰려면 첫 키로 `"$schema": "https://json.schemastore.org/claude-code-settings.json"`을 넣습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 우선순위와 병합

같은 키가 여러 곳에 있으면 위쪽 값이 적용됩니다.

| 순위     | 출처                                 | 비고                              |
|----------|--------------------------------------|-----------------------------------|
| 1 (최고) | 조직 관리 설정                       | 아래 어느 것으로도 덮어쓸 수 없음 |
| 2        | 명령행 `--settings <파일 또는 JSON>` | 이번 세션만, 파일에 저장하지 않음 |
| 3        | `.claude/settings.local.json`        | 개인 프로젝트                     |
| 4        | `.claude/settings.json`              | 공유 프로젝트                     |
| 5        | `~/.claude/settings.json`            | 사용자                            |

- **목록은 합쳐집니다.** `permissions.allow`·`deny`·`ask` 같은 목록 키는 위쪽 파일이 아래쪽을 지우지 않고 항목이 더해집니다. hook도 층마다 더해집니다.
- **deny가 먼저입니다.** 규칙은 deny → ask → allow 순서로 평가하고 처음 일치한 것이 결과입니다. 어느 층의 deny든 다른 층의 allow보다 앞서므로, 사용자 설정의 deny는 프로젝트의 allow를 막고 그 반대도 같습니다. 더 구체적인 allow로 deny에 예외를 만들 수 없습니다.
- **환경 변수는 이 순서 밖입니다.** 예를 들어 셸의 `ANTHROPIC_MODEL`은 어느 파일의 `model`보다 앞섭니다. 설정 파일 안의 `env` 블록은 일반 키로 위 순서를 따릅니다.
- **신뢰 전에는 일부만 적용됩니다.** 공유 파일의 `permissions.allow`, `permissions.additionalDirectories`, 대부분의 `env` 값은 각자 그 폴더의 신뢰 확인 창을 수락한 뒤에 적용됩니다. `deny`와 `ask`는 제한만 하므로 바로 적용됩니다.
- **저장소 파일에서 무시되는 값이 있습니다.** `permissions.defaultMode`의 `auto`와 `bypassPermissions`는 공유·개인 프로젝트 파일에서는 적용되지 않습니다(사용자 설정이나 `--permission-mode`로 지정).
- **제한 쪽 값을 존중하는 예외가 있습니다.** `permissions.blockReadsOutsideWorkingDirectories: true`처럼 세션을 제한하는 일부 키는 낮은 층의 `true`도 적용됩니다. 목록은 공식 문서의 "Exceptions to managed settings precedence"에 있습니다.

🟡 클라우드 세션은 이 PC의 `~/.claude/settings.json`을 읽지 않습니다. 저장소 하나로 시작한 클라우드 세션은 commit된 `.claude/settings.json`을 읽지만, 여러 저장소 세션이나 프로젝트 스레드는 권한 규칙·hook·`env`를 읽지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 공유와 개인 구분

공유 파일에는 "이 저장소에서 일하는 누구에게나 같아야 하는 것"만 둡니다. PC·사람마다 다른 값은 사용자 설정이나 개인 프로젝트 파일에 둡니다.

| 공유 파일에 넣음                           | 이유                                           |
|--------------------------------------------|------------------------------------------------|
| 읽기 전용 `permissions.allow`              | 반복 확인 창을 줄임 (신뢰 수락 뒤 적용)        |
| `permissions.disableBypassPermissionsMode` | 확인을 모두 건너뛰는 모드를 이 저장소에서 막음 |
| 저장소 고유 보호 hook                      | 이 저장소 파일 구조에 묶인 검사                |
| `attribution`                              | commit·PR 표기를 저장소 규칙에 맞춤            |

| 공유 파일에 넣지 않음               | 이유                                                                                             |
|-------------------------------------|--------------------------------------------------------------------------------------------------|
| `model`, `autoCompactWindow`        | 사람·요금제마다 다른 선호                                                                        |
| `statusLine`                        | 개인 화면 설정이고, 지정한 명령이 각자 PC에서 실행됨                                             |
| `cleanupPeriodDays`                 | 대화 기록 보존 기간은 개인 판단 (기본 30일, 지나면 알림 없이 삭제)                               |
| `env`의 토큰·개인 경로              | 자격증명과 PC별 경로는 저장소에 두지 않음                                                        |
| `permissions.additionalDirectories` | PC마다 폴더 구조가 다름                                                                          |
| `enableAllProjectMcpServers`        | `.mcp.json` 서버를 모두 확인 없이 승인함. 저장소마다 판단하고, 신뢰 전에는 공유 파일 값이 무시됨 |
| 위험 명령 `permissions.deny`        | 삭제·이력 변경·배포 시험이 잦은 사람의 업무를 막을 수 있음. 공유 deny는 개인 파일로 풀 수 없음   |
| 자격증명 읽기 차단                  | 자격증명 위치는 사람·PC마다 다름                                                                 |

🟡 deny는 층을 넘어 합쳐지고 어느 층에서든 allow보다 앞섭니다. 저장소 공유 파일에 deny를 넣으면 그 저장소에서 일하는 사람은 개인 설정으로 풀 수 없습니다. 위험 명령 차단은 [5절](#5-deny와-ask-후보)처럼 각자 개인 설정에서 선택합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 권한 규칙 문법

규칙은 `도구` 또는 `도구(지정자)` 형식입니다. 도구 이름만 쓴 deny(`Bash`)는 그 도구를 Claude에게서 아예 빼고, 지정자가 있는 deny(`Bash(rm *)`)는 도구를 남긴 채 일치하는 호출만 막습니다.

### Bash 규칙

| 규칙                   | 일치                       | 일치하지 않음           |
|------------------------|----------------------------|-------------------------|
| `Bash(npm run build)`  | `npm run build`            | `npm run build --watch` |
| `Bash(npm run *)`      | `npm run build`, `npm run` | `npm install`           |
| `Bash(ls *)`           | `ls -la`, `ls`             | `lsof`                  |
| `Bash(ls*)`            | `ls -la`, `lsof`           | -                       |
| `Bash(git log * main)` | `git log --oneline main`   | `git log main`          |

- `*`는 공백을 포함한 아무 글자에 일치합니다. 첫 `*` 앞부분은 쓴 그대로 비교하므로 `*`는 하위 명령 뒤에 둡니다. `Bash(git *)`는 모든 git 명령을 허용합니다.
- 끝의 ` *`(공백 + `*`)는 인수 없는 명령에도 일치합니다. 공백도 규칙의 일부라서 `Bash(ls *)`는 `lsof`에 일치하지 않습니다.
- `:*`는 끝에 올 때만 ` *`와 같은 뜻입니다. `Bash(ls:*)`는 `Bash(ls *)`와 같고, 중간의 `:`는 글자 그대로 비교합니다.
- `&&`·`||`·`;`·`|`·`&`·줄바꿈으로 이은 명령은 나눠서 봅니다. allow는 모든 부분이 허용되어야 하고, deny·ask는 하위 셸·명령 치환·`for` 본문 안의 부분까지 하나라도 일치하면 적용됩니다.
- `timeout`·`time`·`nice`·`nohup`·`stdbuf`·`command`·`builtin`과 옵션 없는 `xargs`는 벗기고 비교합니다. deny·ask는 앞의 변수 대입(`FOO=bar rm -rf x`)을 넘어서도 일치합니다.

🟡 Bash 규칙은 Claude가 쓴 명령 글자를 비교할 뿐 프로그램 자체를 막지 않습니다. `Bash(git push *)`는 `git -C . push`, `/usr/bin/git push`, `sh -c 'git push'`를 막지 못합니다. 실수를 막는 난간으로 쓰고, 최종 방어는 원격 branch 보호·CI·sandbox에 둡니다.

### Read와 Edit 규칙

경로는 gitignore 문법을 따르며 시작 모양에 따라 기준이 다릅니다.

| 모양             | 기준                                                                  | 예                   |
|------------------|-----------------------------------------------------------------------|----------------------|
| `//path`         | 파일 시스템 루트 (절대 경로)                                          | `Read(//etc/shadow)` |
| `~/path`         | 홈 디렉토리                                                           | `Read(~/.ssh/**)`    |
| `/path`          | 설정 파일 기준 (프로젝트 파일은 작업 폴더, 사용자 파일은 `~/.claude`) | `Edit(/src/**)`      |
| `path`, `./path` | 현재 폴더                                                             | `Read(./.env)`       |

- `/Users/alice/file`처럼 `/` 하나로 시작하면 절대 경로가 아닙니다. 절대 경로는 `//`로 씁니다. 사용자 설정의 `Read(/secrets/**)`는 `~/.claude/secrets/**`를 뜻합니다.
- 파일 이름만 쓰면 어느 깊이에서나 일치합니다. `Read(.env)`와 `Read(**/.env)`는 같습니다. 폴더 하나짜리 패턴(`secrets/**`)은 deny·ask에서는 모든 깊이, allow에서는 현재 폴더 바로 아래만 일치합니다.
- `Read` deny는 같은 경로의 Edit·Write도 막습니다. 파일을 고치지 못하게만 하려면 `Edit` deny를 씁니다. `Write(...)`·`Grep(...)`·`Glob(...)` 경로 규칙은 받아들여지지만 일치에 쓰이지 않으므로 `Edit`·`Read`로 씁니다.
- Read·Edit deny는 내장 파일 도구, Bash의 `cat`·`head`·`tail`·`sed`·`tee`, 리디렉션 대상에 적용됩니다. `grep -r`처럼 파일 이름을 말하지 않는 명령이나 Python 스크립트가 직접 여는 파일은 막지 못하므로, 운영체제 수준 차단은 sandbox를 씁니다.
- 프로젝트의 `.claudeignore` 파일은 효과가 없습니다. 항목을 `Read` deny로 옮깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. deny와 ask 후보

**deny**는 확인 없이 거부하고, **ask**는 허용 모드에서도 확인 창을 띄웁니다. 이 절의 규칙은 저장소 공유안이 아니라 **개인 설정(`~/.claude/settings.json` 또는 `.claude/settings.local.json`)에서 골라 쓰는 예시**입니다. 아래는 공식 문법으로 정리한 후보이며 세션에서 일치 여부를 시험하지 않았습니다.

### 업무 성격에 맞춰 고르기

시스템 엔지니어처럼 branch 정리, 이력 정리, 파일 삭제, Ansible 시험 같은 위험 작업을 자주 하는 사람은 deny를 넓게 걸면 그때마다 Claude가 작업을 진행하지 못합니다. deny로 막힌 명령은 확인 창도 뜨지 않으므로 사람이 터미널에서 직접 실행하거나 설정을 고쳐야 합니다.

| 방식                         | 동작                                                  | 맞는 경우                                             |
|------------------------------|-------------------------------------------------------|-------------------------------------------------------|
| deny                         | 확인 없이 거부                                        | 한 번도 Claude에게 맡길 일이 없는 명령, 자격증명 읽기 |
| ask                          | 매번 확인 창, 내용을 보고 승인                        | 정당하게 쓰지만 실수하면 되돌리기 어려운 명령         |
| 규칙 없음 (권한 모드에 맡김) | 기본 모드에서는 Bash 실행마다 확인                    | 위험 작업이 일상 업무인 경우                          |
| 세션별 조절                  | `--settings`나 `--disallowedTools`로 이번 세션만 추가 | 운영 저장소처럼 특정 작업에서만 더 엄격하게 할 때     |

- 개인 설정의 사용자 파일은 모든 프로젝트에 적용되고, `.claude/settings.local.json`은 그 프로젝트에만 적용됩니다. 운영 저장소에서만 엄격하게 하고 시험 저장소는 느슨하게 두려면 개인 프로젝트 파일에 넣습니다.
- 처음에는 ask로 시작하고, 확인 창에서 한 번도 승인하지 않는 명령만 deny로 옮기는 방식이 업무 중단이 적습니다.
- 다른 층의 deny는 개인 파일의 allow로 풀리지 않습니다. 막혀서 풀어야 할 때는 deny가 들어 있는 파일을 `/permissions`에서 확인하고 그 파일에서 지웁니다.

### 규칙 후보

| 분류                      | 규칙 후보                                                                                                      | 권장 위치     |
|---------------------------|----------------------------------------------------------------------------------------------------------------|---------------|
| force push                | `Bash(git push --force*)`, `Bash(git push * --force*)`, `Bash(git push -f*)`, `Bash(git push * -f*)`           | deny          |
| 원격 branch·tag 삭제      | `Bash(git push --delete *)`, `Bash(git push * --delete *)`, `Bash(git push -d *)`, `Bash(git push * -d *)`     | deny          |
| 로컬 tag·branch 강제 삭제 | `Bash(git tag -d *)`, `Bash(git tag --delete *)`, `Bash(git branch -D *)`                                      | deny 또는 ask |
| release                   | `Bash(gh release create *)`, `Bash(gh release delete *)`, `Bash(git push --tags*)`, `Bash(git push * --tags*)` | deny 또는 ask |
| 되돌리기 어려운 변경      | `Bash(git reset --hard*)`, `Bash(git clean -f*)`, `Bash(rm -rf *)`, `Bash(rm -fr *)`                           | ask           |
| 이름 없는 stash           | `Bash(git stash)`, `Bash(git stash pop)`, `Bash(git stash drop)`, `Bash(git stash clear)`                      | ask           |
| 자격증명 읽기             | `Read(./.env)`, `Read(./.env.*)`, `Read(~/.ssh/**)`, `Read(~/.aws/**)`, `Read(**/*.pem)`                       | deny          |

- **옵션 위치**: 가운데 `*` 양옆의 공백은 글자 그대로 비교합니다. 그래서 `git push --force origin`과 `git push origin main --force`를 함께 막으려면 바로 뒤에 오는 형태와 중간에 오는 형태 두 규칙이 필요합니다. `--force*`는 `--force-with-lease`도 포함합니다.
- **끝의 `:*` 함정**: `git push origin :branch` 같은 삭제를 막으려고 `Bash(git push origin :*)`를 쓰면, 끝의 `:*`가 와일드카드로 읽혀 `git push origin`으로 시작하는 모든 push에 일치합니다. 콜론 refspec 삭제는 규칙 대신 hook에서 검사합니다.
- **`+` refspec 우회**: `git push origin +main`은 `--force` 없이 강제로 push합니다. `Bash(git push * +*)`로 보완할 수 있지만 다른 표기까지 모두 막지는 못합니다.
- **정확한 명령과 접두어**: `Bash(git stash)`처럼 `*`가 없는 규칙은 그 명령만 일치하므로 `git stash push -m 이름`은 막지 않습니다.
- **자격증명 패턴 범위**: `**/*.pem`처럼 상대 패턴은 현재 폴더 아래에만 적용됩니다. 모든 위치를 막으려면 `//**/*.pem`을 씁니다. `**/*token*`은 `token_guide.md` 같은 일반 문서까지 막을 수 있으므로 대상 이름을 좁혀 씁니다.
- **권장 위치 열**: 위험 작업이 드문 사용자 기준입니다. 삭제·이력 변경이 잦으면 deny 칸의 명령도 ask로 내리거나 빼고 씁니다.

아래는 `~/.claude/settings.json`에 넣는 개인 설정 예시입니다.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "deny": [
      "Bash(git push --force*)",
      "Bash(git push * --force*)",
      "Bash(git push --delete *)",
      "Bash(git push * --delete *)",
      "Read(./.env)",
      "Read(./.env.*)"
    ],
    "ask": [
      "Bash(git reset --hard*)",
      "Bash(git clean -f*)",
      "Bash(rm -rf *)"
    ]
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. allow 후보

allow는 확인 창 없이 실행을 허용합니다. 공유 파일의 allow는 신뢰 수락 뒤에 적용되며, 같은 명령에 일치하는 ask·deny가 있으면 allow보다 앞섭니다.

| 분류      | 규칙 후보                                                                                                                       | 비고                                         |
|-----------|---------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| git 조회  | `Bash(git status*)`, `Bash(git log *)`, `Bash(git diff *)`, `Bash(git show *)`, `Bash(git rev-parse *)`, `Bash(git ls-files *)` | 읽기 전용 git은 대부분 이미 확인 없이 실행됨 |
| git 받기  | `Bash(git fetch *)`                                                                                                             | 원격 추적 ref를 바꾸므로 읽기 전용은 아님    |
| 문서 검사 | `Bash(sia-md-style-check *)`, `Bash(sia-md-heading-check *)`, `Bash(sia-md-link-check *)`                                       | 저장소가 정한 검사 명령으로 바꿔 씀          |
| CI 조회   | `Bash(gh run list *)`, `Bash(gh run view *)`                                                                                    | 네트워크 조회                                |

- `ls`·`cat`·`grep`·`find`·`diff`·`wc`와 읽기 전용 git은 내장 목록으로 이미 확인 없이 실행됩니다. 이 목록은 바꿀 수 없으며, 막으려면 ask·deny를 추가합니다.
- 실행기 뒤의 명령까지 허용되는 형태는 피합니다. `Bash(npx *)`나 `Bash(docker exec *)`는 그 뒤의 어떤 명령이든 허용합니다.
- `find`의 `-exec`·`-delete`나 `watch`·`flock` 같은 실행 래퍼는 접두어 allow로 승인되지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 안전 설정

| 키                                         | 값                                      | 효과                                                                                     |
|--------------------------------------------|-----------------------------------------|------------------------------------------------------------------------------------------|
| `permissions.disableBypassPermissionsMode` | `"disable"`                             | `bypassPermissions` 진입과 `--dangerously-skip-permissions`를 거부. 어느 파일에서나 적용 |
| `permissions.defaultMode`                  | `"default"` 등                          | 새 세션의 기본 모드. `auto`·`bypassPermissions`는 프로젝트 파일에서 무시                 |
| `hooks`                                    | 이벤트별 hook 목록                      | 도구 호출 전후 검사. 층마다 더해지며 공유 파일의 hook은 신뢰 전에도 실행됨               |
| `disableAllHooks`                          | `true`                                  | 조직 관리 hook을 뺀 모든 hook을 끔. 프로젝트 파일의 `false`가 사용자 `true`보다 앞섬     |
| `attribution`                              | `commit`·`pr`·`sessionUrl` 또는 `false` | commit trailer와 PR 문구 지정. `false`는 v2.1.281 이상                                   |
| `includeCoAuthoredBy`                      | (옛 키)                                 | v2.0.62부터 사용 중단 예정. `attribution.commit`·`pr`을 정하면 무시                      |

- `attribution`을 정해도 사용자의 `CLAUDE.md`나 메모리의 표기 규칙이 우선한다고 Claude에게 전달됩니다. 조직 관리 설정에서 정한 경우만 예외입니다.
- 신뢰하지 않은 저장소에서 `claude -p`를 실행하면 신뢰 확인 없이 그 저장소의 hook과 `env`가 쓰입니다. 이때는 `--setting-sources user`나 `--bare`, 또는 `--settings '{"disableAllHooks": true}'`를 씁니다. 사용자 설정에만 `disableAllHooks`를 두면 프로젝트 파일의 `false`가 이깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. hook 실패 시 동작

hook은 종료 코드와 표준 출력으로 결과를 알립니다. 보호용 hook에서 가장 중요한 점은 **hook이 망가지면 기본적으로 작업이 그대로 진행된다**는 것입니다.

| hook 결과                        | `PreToolUse`에서의 동작                                 |
|----------------------------------|---------------------------------------------------------|
| 종료 코드 0, 출력 없음           | 결정 없음. 일반 권한 확인으로 진행 (허용이 아님)        |
| 종료 코드 0, 올바른 JSON         | JSON의 결정 적용                                        |
| 종료 코드 2                      | 차단. 표준 오류가 사유로 Claude에게 전달됨              |
| 그 밖의 종료 코드 (1 포함)       | 차단하지 않는 오류. 작업 진행, 기록에 `hook error` 표시 |
| 실행 실패 (경로 없음, 권한 없음) | 차단하지 않는 오류. 작업 진행                           |
| 시간 초과 (기본 600초)           | 결정 없음. 작업 진행                                    |

- 정책을 강제하는 hook은 `exit 1`이 아니라 `exit 2`로 끝냅니다.
- hook이 실패하거나 시간 초과일 때 막으려면 hook 항목에 `"onFailure": "block"`을 둡니다(v2.1.295 이상, `command`·`http` hook). 이때 실패는 그 이벤트의 종료 코드 2와 같은 효과입니다.
- hook이 `"allow"`를 돌려줘도 deny·ask 규칙은 그대로 평가됩니다. 반대로 종료 코드 2로 막은 호출은 allow 규칙이 있어도 막힙니다.
- 모든 Bash를 허용하고 몇 명령만 막으려면 allow에 `Bash`를 두고 `PreToolUse` hook으로 거부하는 방식이 공식 문서에 안내되어 있습니다.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-command.sh",
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. hook 배포 방식

같은 검사를 여러 저장소·PC에 배포하는 방식은 세 가지가 있습니다.

| 방식             | 위치와 연결                                                         | 장점                                    | 주의                                                    |
|------------------|---------------------------------------------------------------------|-----------------------------------------|---------------------------------------------------------|
| 저장소 직접 포함 | 스크립트를 저장소에 두고 `.claude/settings.json`의 `hooks`에서 호출 | clone만 하면 모두에게 같은 검사 적용    | 저장소마다 사본이 생기고, 수정을 저장소별로 반영해야 함 |
| skill 동봉       | skill 폴더에 스크립트를 넣고, 예시 설정을 각 PC 사용자 설정에 병합  | 개인 도구 묶음으로 여러 저장소에 재사용 | PC마다 수동 병합이 필요하고 적용 여부를 PC별로 확인     |
| Git hook         | PC 공용 hooks 폴더와 저장소별 `core.hooksPath` 연결                 | Claude 밖의 commit·push에도 적용        | Claude 도구 호출 단계가 아니라 Git 단계에서만 검사      |

- Claude Code hook은 Claude의 도구 호출을 검사하고, Git hook은 사람과 도구 모두의 Git 작업을 검사합니다. 둘은 대체가 아니라 층이 다릅니다.
- 공유 파일의 hook은 신뢰 확인 전에도 실행됩니다. 저장소에 hook을 넣으면 그 저장소를 여는 모든 사람의 PC에서 그 명령이 실행된다는 뜻이므로, 스크립트를 검토한 뒤 commit합니다.
- skill의 frontmatter에 둔 hook은 skill을 부른 뒤 세션이 끝날 때까지만 동작합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. Codex 대응 설정

| Claude Code                                    | Codex                                                               | 차이                                                 |
|------------------------------------------------|---------------------------------------------------------------------|------------------------------------------------------|
| `settings.json`의 `permissions.defaultMode`    | `config.toml`의 `approval_policy`·`sandbox_mode`                    | Codex는 승인 정책과 sandbox 경계를 따로 정함         |
| `permissions.deny`·`ask`·`allow` (Bash 규칙)   | `rules/*.rules`의 `prefix_rule()` (`forbidden`·`prompt`·`allow`)    | Codex 규칙은 실험 기능이며 명령을 단어 목록으로 비교 |
| 여러 규칙 일치 시 deny → ask → allow           | 여러 규칙 일치 시 `forbidden` > `prompt` > `allow`                  | 둘 다 가장 엄격한 쪽이 이김                          |
| 공유 `.claude/settings.json` (allow는 신뢰 뒤) | `<저장소>/.codex/rules/` (프로젝트 `.codex/` 층을 신뢰할 때만 읽음) | 둘 다 저장소 제공 허용은 신뢰가 필요                 |
| 규칙 시험 명령 없음                            | `codex execpolicy check --rules <파일> -- <명령>`                   | Codex는 규칙 파일을 명령으로 시험 가능               |

- Codex 사용자 규칙은 `~/.codex/rules/default.rules`이며, TUI에서 허용을 고르면 이 파일에 기록됩니다.
- Codex는 `bash -lc` 안의 단순 연결(`&&`·`||`·`;`·`|`)을 나눠 평가하지만, 리디렉션·치환·변수·와일드카드·제어문이 있으면 나누지 않고 전체를 한 명령으로 봅니다.
- 🟡 미확인: Codex에서 Claude Code `PreToolUse` hook과 같은 도구 호출 전 검사 기능의 범위는 이번에 확인하지 않았습니다. Codex 설정 전반은 [Codex CLI Linux 가이드](../codex/codex_cli_linux_guide.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 적용과 확인

1. 공유할 규칙은 먼저 `.claude/settings.local.json`에 넣어 시험합니다.
2. 저장한 뒤 `/status`의 `Setting sources` 줄에서 읽힌 파일을 확인합니다. 대부분의 키(권한·hook 포함)는 재시작 없이 다시 읽히지만 `model`·`effortLevel`은 세션 시작 때만 읽습니다.
3. `/permissions`에서 각 규칙과 출처 파일을 확인합니다. 시작 때 경고가 나오면 규칙 오타나 하위 명령 앞의 `*` 같은 문제입니다.
4. `claude doctor`로 거부된 항목을 확인합니다. JSON 오류가 있는 파일은 통째로, 잘못된 항목은 그 항목만 건너뜁니다.
5. 확인이 끝나면 `.claude/settings.json`으로 옮겨 commit합니다. 다른 사람은 폴더 신뢰를 수락해야 allow가 적용됩니다.

🟡 `claude -p`(비대화형)는 오류 창을 띄우지 않고 깨진 파일이나 값을 건너뛴 채 진행합니다. 자동화에서 설정을 바꿨다면 `claude doctor`로 따로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 12. 참고 자료

- Settings files and precedence: [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)
- All settings (키 목록): [code.claude.com/docs/en/settings-reference](https://code.claude.com/docs/en/settings-reference)
- Configure permissions: [code.claude.com/docs/en/permissions](https://code.claude.com/docs/en/permissions)
- Hooks reference: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- Codex rules: [developers.openai.com/codex/rules](https://developers.openai.com/codex/rules)
- 관련 문서: [확장 기능 가이드](claude_code_extensions_guide.md), [Linux CLI 가이드](claude_code_cli_linux_guide.md), [공식 참조 노트](../../../_reference/claude_code_official_notes.md)

---

**작성일**: 2026-11-19

**마지막 업데이트**: 2026-11-19

© 2026 siasia86. Licensed under CC BY 4.0.
