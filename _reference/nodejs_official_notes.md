---
name: nodejs-official-notes
description: Node.js 26.13.1 판과 LTS 일정, node 이미지 시험 결과(parseArgs·fetch·node:test·npm init type) 정리.
tags:
  - nodejs
  - programming
last_checked: 2026-11-27
sources:
  - https://nodejs.org/dist/index.json
  - https://github.com/nodejs/Release
  - https://nodejs.org/dist/v26.13.1/SHASUMS256.txt
---

# Node.js 공식 자료 참조 노트

## 1. 판과 일정 (2026-11-27 확인)

- dist index: v26.13.1(2026-11-10, LTS Lithium), v26.13.0(10-28), 27.0.0은 alpha(v27.0.0-alpha.0.2.0, 11-25). 24 계열 최신 LTS v24.22.3(Krypton).
- Release 일정: 26.x Active LTS(Active 2026-10-28, Maintenance 2027-10-20, 종료 2029-04-30), 24.x Maintenance LTS(종료 2028-04-30), 22.x Maintenance LTS(종료 2027-04-30).
- `SHASUMS256.txt`에 `node-v26.13.1-linux-x64.tar.xz` sha256 `5c063e46bab0fbc1c17cc445d7ff129cbdcd0471be6ed83b6ab864f8143bc864`.

## 2. 컨테이너 시험 (node:26.13.1)

- `node -v` v26.13.1, `npm -v` 11.20.0. `node --check` 통과.
- 예제(`parseArgs`, `readFile`, `execFile` + timeout, `createServer` + `fetch` + `AbortSignal.timeout`) 정상.
- 없는 파일: `read: ENOENT: no such file or directory, open 'nope.json'`, 종료 코드 1.
- 모르는 옵션: `TypeError [ERR_PARSE_ARGS_UNKNOWN_OPTION]: Unknown option '--bogus'`, 종료 코드 1.
- `node --test`: tests 2, pass 2, fail 0, 종료 코드 0.
- `npm init -y` → `package.json`의 `type`이 `commonjs`.
