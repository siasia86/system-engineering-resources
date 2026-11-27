# SE를 위한 Ruby 입문
<!-- reference: _reference/ruby_official_notes.md -->

Ruby는 문법이 간결한 인터프리터 언어로, 운영 분야에서는 Chef·Vagrant·Fluentd·Homebrew·GitLab 같은 도구의 설정과 확장을 읽고 고칠 때 주로 만납니다. 이 문서는 Python·Bash에 익숙한 SE가 호스트 목록(JSON)을 읽어 거르고 외부 명령과 HTTP를 호출하는 작은 스크립트를 쓰고, 테스트와 의존성 관리(Bundler)까지 따라 하도록 썼습니다.

- 기준 판: Ruby 4.0.10 (2026-11-19, RubyGems·Bundler 4.0.20) (2026-11-27 확인, 4.1은 preview)
- 예제 시험: 2026-11-27 3~6절을 `ruby:4.0.10` 컨테이너에서 실행해 문법 검사, 실행·오류 종료 코드, minitest, `bundle init`·`bundle add`, 기본 설치에 webrick이 없는 점을 확인

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. SE가 Ruby를 만나는 곳](#1-se가-ruby를-만나는-곳) / [2. 설치](#2-설치) / [3. 첫 스크립트](#3-첫-스크립트) |
| [4. 오류와 종료 코드](#4-오류와-종료-코드) / [5. 테스트](#5-테스트) / [6. 의존성 관리](#6-의존성-관리)       |
| [7. 판과 지원](#7-판과-지원) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅) / [함께 보기](#함께-보기) |

---

## 1. SE가 Ruby를 만나는 곳

| 도구             | Ruby가 나오는 곳                                                                                          |
|------------------|-----------------------------------------------------------------------------------------------------------|
| Chef             | recipe·cookbook이 Ruby DSL([설정 관리 비교](../../02_infrastructure/iac/config_management_comparison.md)) |
| Vagrant          | `Vagrantfile`이 Ruby 코드([Vagrant](../../02_infrastructure/iac/vagrant.md))                              |
| Fluentd          | 플러그인이 Ruby gem                                                                                       |
| Homebrew, GitLab | formula·애플리케이션 코드                                                                                 |

| Python                   | Ruby                       |
|--------------------------|----------------------------|
| `import json`            | `require "json"`           |
| `argparse`               | `optparse`                 |
| `subprocess.run`         | `Open3.capture2`, `system` |
| `try`/`except`           | `begin`/`rescue`           |
| `pip`·`requirements.txt` | `gem`·Bundler `Gemfile`    |
| `pytest`                 | minitest(기본 포함), RSpec |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
# Debian·Ubuntu 배포판 패키지 (판은 배포판에 따라 다름)
sudo apt install ruby-full
ruby -v

# 시험만 할 때
docker run --rm -it ruby:4.0.10 bash
```

- 여러 판을 함께 쓰려면 rbenv·asdf·mise 같은 판 관리자를 씁니다(미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 3. 첫 스크립트

[Go 입문](./go_for_se.md)과 같은 `hosts.json`을 씁니다. `hostlist.rb`:

```ruby
#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "optparse"
require "open3"
require "net/http"
require "socket"

def filter_by_role(hosts, role)
  role.nil? || role.empty? ? hosts : hosts.select { |h| h["role"] == role }
end

if $PROGRAM_NAME == __FILE__
  opts = { file: "hosts.json", role: nil }
  OptionParser.new do |o|
    o.on("--file PATH", "host list JSON") { |v| opts[:file] = v }
    o.on("--role ROLE", "filter by role") { |v| opts[:role] = v }
  end.parse!

  begin
    hosts = JSON.parse(File.read(opts[:file]))
  rescue Errno::ENOENT => e
    warn "read: #{e.message}"
    exit 1
  rescue JSON::ParserError => e
    warn "json: #{e.message}"
    exit 2
  end

  filter_by_role(hosts, opts[:role]).each do |h|
    puts format("%-6s %-12s %s", h["name"], h["ip"], h["role"])
  end

  out, status = Open3.capture2("uname", "-s")
  abort "exec failed" unless status.success?
  puts "kernel: #{out.strip}"

  # 예제용 로컬 HTTP 서버 (표준 라이브러리 socket만 사용)
  server = TCPServer.new("127.0.0.1", 0)
  port = server.addr[1]
  Thread.new do
    c = server.accept
    c.gets
    c.print "HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok"
    c.close
  end
  http = Net::HTTP.new("127.0.0.1", port)
  http.open_timeout = 3
  http.read_timeout = 3
  res = http.get("/health")
  puts "health: #{res.code} #{res.body}"
end
```

```bash
ruby -c hostlist.rb          # Syntax OK
ruby hostlist.rb --role web
```

```text
web01  192.0.2.11   web
web02  192.0.2.12   web
kernel: Linux
health: 200 ok
```

- `Open3.capture2("uname", "-s")`처럼 인수를 나눠 넘기면 셸을 거치지 않습니다. 백틱(`` `cmd` ``)은 셸을 거치므로 입력값을 넣지 않습니다.
- `if $PROGRAM_NAME == __FILE__`은 Python의 `if __name__ == "__main__"`과 같은 역할로, 테스트에서 파일을 불러와도 본문이 실행되지 않게 합니다.
- `Net::HTTP`의 `open_timeout`·`read_timeout`을 정해 두면 응답 없는 서버에서 멈추지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 오류와 종료 코드

- 예외는 `begin`/`rescue`로 잡고, `exit n`으로 종료 코드를 정합니다. `warn`은 표준 오류로 씁니다.
- 시험에서 없는 파일을 주면 `read: No such file or directory @ rb_sysopen - nope.json`과 종료 코드 1이었습니다.
- `abort "메시지"`는 메시지를 표준 오류로 쓰고 종료 코드 1로 끝냅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 테스트

`hostlist_test.rb`:

```ruby
# frozen_string_literal: true

require "minitest/autorun"
require_relative "hostlist"

class HostlistTest < Minitest::Test
  HOSTS = [{ "name" => "web01", "role" => "web" }, { "name" => "db01", "role" => "db" }].freeze

  def test_filter_by_role
    assert_equal ["web01"], filter_by_role(HOSTS, "web").map { |h| h["name"] }
  end

  def test_empty_role_returns_all
    assert_equal 2, filter_by_role(HOSTS, nil).size
  end
end
```

```bash
ruby hostlist_test.rb      # 2 runs, 2 assertions, 0 failures, 0 errors, 0 skips
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 의존성 관리

```bash
bundle init                          # Gemfile 생성
bundle add rubocop --skip-install    # Gemfile에 gem "rubocop", "~> 1.93" 추가
bundle install                       # Gemfile.lock 생성 (설치)
bundle exec rubocop hostlist.rb      # 프로젝트에 고정된 판으로 실행
```

- `Gemfile`과 `Gemfile.lock`을 함께 커밋하면 다른 서버에서도 같은 판을 설치합니다(Python의 lock 파일과 같은 역할).
- Ruby 4.0.10 기본 설치에서 `require "webrick"`은 `cannot load such file -- webrick`로 실패했습니다. 예전 자료의 `ruby -run -e httpd` 같은 간이 웹 서버 예시는 webrick gem을 따로 설치해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 판과 지원

| 판  | 상태(공식 branches 페이지, 2026-11-27) |
|-----|----------------------------------------|
| 4.1 | preview                                |
| 4.0 | normal maintenance(2025-12-25 출시)    |
| 3.4 | normal maintenance                     |
| 3.3 | legacy maintenance                     |

- 새 판은 대체로 매년 12월 25일에 나옵니다(4.0·3.4·3.3 출시일 기준). 운영 스크립트는 normal maintenance 판을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용 | 방법                          | 기대 결과              |
|------|-----------|-------------------------------|------------------------|
| 1    | 설치      | `ruby -v`                     | `ruby 4.0.10`          |
| 2    | 문법      | `ruby -c hostlist.rb`         | `Syntax OK`            |
| 3    | 테스트    | `ruby hostlist_test.rb`       | `0 failures, 0 errors` |
| 4    | 오류 처리 | 없는 파일로 실행 뒤 `echo $?` | 1                      |
| 5    | 의존성    | `bundle exec rubocop -v`      | Gemfile에 고정된 판    |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                                     | 원인                                    | 조치                                     |
|----------------------------------------------------------|-----------------------------------------|------------------------------------------|
| `cannot load such file -- webrick`                       | 3.0부터 기본 포함 gem이 아님            | `bundle add webrick` 또는 다른 서버 사용 |
| `can't modify frozen String`                             | `# frozen_string_literal: true` 사용 중 | `+""`나 `dup`으로 새 문자열 만들기       |
| 서버마다 gem 판이 다름                                   | `Gemfile.lock` 없음                     | lock 파일 커밋, `bundle exec`로 실행     |
| `invalid option: --bogus`(`OptionParser::InvalidOption`) | 정의하지 않은 옵션                      | `o.on`으로 정의, 예외를 잡아 사용법 출력 |

- webrick 오류 외의 문구는 이번에 재현하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Go 입문](./go_for_se.md) · [Node.js 입문](./nodejs_for_se.md) — 같은 예제를 다른 언어로
- [설정 관리 도구 비교](../../02_infrastructure/iac/config_management_comparison.md) — Chef recipe
- [Vagrant](../../02_infrastructure/iac/vagrant.md) — Ruby로 쓰는 Vagrantfile

---

## 참고 자료

- Ruby: [Downloads](https://www.ruby-lang.org/en/downloads/) · [Branches](https://www.ruby-lang.org/en/downloads/branches/) · [Documentation](https://docs.ruby-lang.org/en/) — ★★★☆☆
- Bundler: [bundler.io](https://bundler.io/) — ★★★☆☆

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
