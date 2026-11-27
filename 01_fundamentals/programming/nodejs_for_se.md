# SE를 위한 Node.js 입문
<!-- reference: _reference/nodejs_official_notes.md -->

Node.js는 JavaScript를 서버·명령줄에서 실행하는 런타임입니다. 운영 분야에서는 웹 프런트엔드 빌드(CI), 서버리스 함수, n8n 같은 자동화 도구, VS Code 확장·Claude Code 같은 CLI의 실행 환경으로 만납니다. 이 문서는 Python·Bash에 익숙한 SE가 외부 패키지 없이 표준 모듈만으로 호스트 목록(JSON)을 거르고 외부 명령과 HTTP를 호출하는 스크립트를 쓰고, 내장 테스트 러너로 검사하도록 썼습니다.

- 기준 판: Node.js 26.13.1 (Active LTS, 2026-11-10, npm 11.20.0) (2026-11-27 확인)
- 예제 시험: 2026-11-27 3~6절을 `node:26.13.1` 컨테이너에서 실행해 `node --check`, 실행·오류 종료 코드, 모르는 옵션 오류, `node --test`, `npm init -y`의 `type` 값을 확인

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. SE가 Node.js를 만나는 곳](#1-se가-nodejs를-만나는-곳) / [2. 설치](#2-설치) / [3. 첫 스크립트](#3-첫-스크립트)    |
| [4. 오류와 종료 코드](#4-오류와-종료-코드) / [5. 테스트](#5-테스트) / [6. 패키지와 모듈 형식](#6-패키지와-모듈-형식) |
| [7. 판과 지원](#7-판과-지원) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅) / [함께 보기](#함께-보기)         |

---

## 1. SE가 Node.js를 만나는 곳

| 상황          | 내용                                                                                                                                                |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| CI 빌드       | `npm ci`, `npm run build`로 프런트엔드 빌드                                                                                                         |
| 서버리스      | Lambda·Azure Functions·Cloudflare Workers의 주요 런타임([서버리스 함수 비교](../../02_infrastructure/cloud_aws/serverless_functions_comparison.md)) |
| 자동화·CLI    | n8n, Claude Code 등 npm으로 설치하는 도구                                                                                                           |
| 운영 스크립트 | JSON·HTTP API 다루는 짧은 도구                                                                                                                      |

| Python                   | Node.js                                  |
|--------------------------|------------------------------------------|
| `argparse`               | `node:util`의 `parseArgs`                |
| `json.load`              | `JSON.parse(await readFile(...))`        |
| `subprocess.run`         | `node:child_process`의 `execFile`        |
| `requests`               | 내장 `fetch`                             |
| `pytest`                 | 내장 `node:test`                         |
| `pip`·`requirements.txt` | `npm`·`package.json`·`package-lock.json` |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
NV=v26.13.1
curl -sSLO https://nodejs.org/dist/${NV}/node-${NV}-linux-x64.tar.xz
curl -sSLO https://nodejs.org/dist/${NV}/SHASUMS256.txt
grep " node-${NV}-linux-x64.tar.xz\$" SHASUMS256.txt | sha256sum -c -
sudo tar -C /usr/local --strip-components=1 -xJf node-${NV}-linux-x64.tar.xz
node -v && npm -v

# 시험만 할 때
docker run --rm -it node:26.13.1 bash
```

- 배포판 패키지의 Node.js는 판이 오래된 경우가 많습니다. 여러 판을 쓰면 nvm·fnm·mise 같은 판 관리자를 씁니다(미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 3. 첫 스크립트

[Go 입문](./go_for_se.md)과 같은 `hosts.json`을 씁니다. `hostlist.mjs`(ES 모듈):

```javascript
#!/usr/bin/env node
import { parseArgs, promisify } from "node:util";
import { readFile } from "node:fs/promises";
import { execFile } from "node:child_process";
import { createServer } from "node:http";

export function filterByRole(hosts, role) {
  return role ? hosts.filter((h) => h.role === role) : hosts;
}

async function main() {
  const { values } = parseArgs({
    options: {
      file: { type: "string", default: "hosts.json" },
      role: { type: "string" },
    },
  });

  let hosts;
  try {
    hosts = JSON.parse(await readFile(values.file, "utf8"));
  } catch (err) {
    console.error(err.code === "ENOENT" ? `read: ${err.message}` : `json: ${err.message}`);
    process.exit(err.code === "ENOENT" ? 1 : 2);
  }
  for (const h of filterByRole(hosts, values.role)) {
    console.log(`${h.name.padEnd(6)} ${h.ip.padEnd(12)} ${h.role}`);
  }

  const { stdout } = await promisify(execFile)("uname", ["-s"], { timeout: 5000 });
  console.log(`kernel: ${stdout.trim()}`);

  // 예제용 로컬 HTTP 서버, 제한 시간 있는 fetch
  const server = createServer((req, res) => res.end("ok"));
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const { port } = server.address();
  const res = await fetch(`http://127.0.0.1:${port}/health`, { signal: AbortSignal.timeout(3000) });
  console.log(`health: ${res.status} ${await res.text()}`);
  server.close();
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await main();
}
```

```bash
node --check hostlist.mjs     # 문법만 검사
node hostlist.mjs --role web
```

```text
web01  192.0.2.11   web
web02  192.0.2.12   web
kernel: Linux
health: 200 ok
```

- 외부 패키지 없이 `parseArgs`, `fetch`, `node:test`만으로 됩니다. 운영 서버에 `node_modules`를 두지 않아도 됩니다.
- `execFile`은 셸을 거치지 않습니다. `exec`(셸 경유)에는 입력값을 넣지 않습니다.
- `fetch`는 기본 제한 시간이 없으므로 `AbortSignal.timeout(ms)`을 줍니다.
- 비동기 함수(`await`)가 기본입니다. 결과를 기다리지 않으면 순서가 뒤섞입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 오류와 종료 코드

- 시험에서 없는 파일을 주면 `read: ENOENT: no such file or directory, open 'nope.json'`과 종료 코드 1이었습니다.
- `parseArgs`는 정의하지 않은 옵션을 거부합니다. `--bogus`를 주면 `TypeError [ERR_PARSE_ARGS_UNKNOWN_OPTION]: Unknown option '--bogus'`로 종료 코드 1이었습니다. 사용자에게 보여줄 도구라면 `try`로 잡아 사용법을 출력합니다.
- 잡지 않은 Promise 거부(`await` 없는 실패)는 프로세스를 종료 코드 1로 끝냅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 테스트

`hostlist.test.mjs`:

```javascript
import { test } from "node:test";
import assert from "node:assert/strict";
import { filterByRole } from "./hostlist.mjs";

const hosts = [{ name: "web01", role: "web" }, { name: "db01", role: "db" }];

test("filter by role", () => {
  assert.deepEqual(filterByRole(hosts, "web").map((h) => h.name), ["web01"]);
});

test("empty role returns all", () => {
  assert.equal(filterByRole(hosts, undefined).length, 2);
});
```

```bash
node --test
```

```text
ℹ tests 2
ℹ pass 2
ℹ fail 0
```

- `node --test`는 `*.test.mjs` 같은 이름의 파일을 찾아 실행합니다(시험 결과 종료 코드 0).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 패키지와 모듈 형식

```bash
npm init -y                 # package.json 생성
npm install <패키지>        # node_modules, package-lock.json
npm ci                      # CI·서버: lock 파일 그대로 설치
```

- 시험에서 `npm init -y`가 만든 `package.json`의 `type`은 `"commonjs"`였습니다. 이 경우 `.js`는 CommonJS(`require`)로, `.mjs`는 ES 모듈(`import`)로 읽힙니다. `.js`에서 `import`를 쓰려면 `"type": "module"`로 바꿉니다.
- `package-lock.json`을 커밋하고 서버·CI에서는 `npm install` 대신 `npm ci`를 써 같은 판을 설치합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 판과 지원

| 계열 | 상태(공식 Release 일정, 2026-11-27) | Active LTS 시작 | 유지 보수 시작 | 지원 종료  |
|------|-------------------------------------|-----------------|----------------|------------|
| 26.x | Active LTS                          | 2026-10-28      | 2027-10-20     | 2029-04-30 |
| 24.x | Maintenance LTS                     | 2025-10-28      | 2026-10-20     | 2028-04-30 |
| 22.x | Maintenance LTS                     | 2024-10-29      | 2025-10-21     | 2027-04-30 |

- 짝수 판이 LTS가 됩니다. 운영에는 Active LTS나 Maintenance LTS를 씁니다. 27.x는 2026-11-27 현재 alpha 단계입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용 | 방법                          | 기대 결과              |
|------|-----------|-------------------------------|------------------------|
| 1    | 설치      | `node -v`                     | `v26.13.1`             |
| 2    | 문법      | `node --check hostlist.mjs`   | 출력 없음, 종료 코드 0 |
| 3    | 테스트    | `node --test`                 | `fail 0`               |
| 4    | 오류 처리 | 없는 파일로 실행 뒤 `echo $?` | 1                      |
| 5    | 의존성    | `npm ci`                      | lock 파일 그대로 설치  |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                           | 원인                                | 조치                                   |
|------------------------------------------------|-------------------------------------|----------------------------------------|
| `Cannot use import statement outside a module` | `.js` 파일이 CommonJS로 읽힘        | `.mjs`로 바꾸거나 `"type": "module"`   |
| `ERR_PARSE_ARGS_UNKNOWN_OPTION`                | 정의하지 않은 옵션                  | `options`에 추가, `strict: false` 검토 |
| 요청이 끝나지 않음                             | `fetch` 제한 시간 없음              | `AbortSignal.timeout()`                |
| 서버마다 패키지 판이 다름                      | `npm install`이 범위 안 최신판 설치 | lock 파일 커밋, `npm ci`               |

- 첫 번째 오류 문구는 이번에 재현하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Go 입문](./go_for_se.md) · [Ruby 입문](./ruby_for_se.md) — 같은 예제를 다른 언어로
- [서버리스 함수 비교](../../02_infrastructure/cloud_aws/serverless_functions_comparison.md) — Node.js 런타임을 쓰는 곳
- [REST API 가이드](./rest_api_guide_for_se.md) — HTTP API 기본

---

## 참고 자료

- Node.js: [Downloads](https://nodejs.org/en/download) · [Release schedule](https://github.com/nodejs/Release) · [API docs](https://nodejs.org/docs/latest/api/) · [Test runner](https://nodejs.org/api/test.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
