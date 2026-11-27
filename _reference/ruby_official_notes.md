---
name: ruby-official-notes
description: Ruby 4.0.10 판과 branches 상태, ruby 이미지 시험 결과(minitest·Bundler·webrick 미포함) 정리.
tags:
  - ruby
  - programming
last_checked: 2026-11-27
sources:
  - https://www.ruby-lang.org/en/downloads/
  - https://www.ruby-lang.org/en/downloads/branches/
---

# Ruby 공식 자료 참조 노트

## 1. 판과 상태 (2026-11-27 확인)

- 다운로드 페이지 판: 4.1.0, 4.0.10, 3.4.13, 3.3.14, 3.2.11.
- branches: 4.1 preview, 4.0 normal maintenance(출시 2025-12-25), 3.4 normal maintenance(2024-12-25), 3.3 legacy maintenance(2023-12-25).

## 2. 컨테이너 시험 (ruby:4.0.10)

- `ruby 4.0.10 (2026-11-19 revision a704b7cd95) +PRISM [x86_64-linux]`, gem·bundle 4.0.20.
- `ruby -c` `Syntax OK`. 예제(optparse, JSON, `Open3.capture2`, TCPServer + `Net::HTTP` 제한 시간) 정상.
- 없는 파일: `read: No such file or directory @ rb_sysopen - nope.json`, 종료 코드 1.
- minitest: `2 runs, 2 assertions, 0 failures, 0 errors, 0 skips`.
- `bundle init`, `bundle add rubocop --skip-install` → `gem "rubocop", "~> 1.93"`.
- `require "webrick"`: `cannot load such file -- webrick (LoadError)`.
