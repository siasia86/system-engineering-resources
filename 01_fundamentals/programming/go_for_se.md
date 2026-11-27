# SE를 위한 Go 입문
<!-- reference: _reference/go_official_notes.md -->

Go는 정적 타입 컴파일 언어로, 의존성 없는 단일 실행 파일을 만들고 여러 OS·CPU용으로 쉽게 교차 빌드할 수 있어 운영 도구·에이전트·CLI에 많이 쓰입니다. Docker, Kubernetes, Terraform, Prometheus가 Go로 만들어졌습니다. 이 문서는 Bash·Python으로 스크립트를 쓰던 SE가 호스트 목록(JSON)을 읽어 거르고, 외부 명령과 HTTP를 호출하는 작은 도구를 만들어 테스트·빌드·배포하는 흐름을 따라 하도록 썼습니다.

- 기준 판: Go 1.27.4 (2026-11-27 확인, 지원 판 1.27·1.26)
- 예제 시험: 2026-11-27 3~6절을 `golang:1.27.4` 컨테이너에서 실행해 `go mod init`, `go vet`, `go test`, 실행·오류 종료 코드, 정적 빌드(7.2MB, 동적 링크 없음), Windows·arm64 교차 빌드를 확인

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 왜 Go인가](#1-왜-go인가) / [2. 설치](#2-설치) / [3. 첫 도구](#3-첫-도구)                                 |
| [4. 오류와 종료 코드](#4-오류와-종료-코드) / [5. 테스트](#5-테스트) / [6. 빌드와 배포](#6-빌드와-배포)       |
| [7. 판과 지원](#7-판과-지원) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅) / [함께 보기](#함께-보기) |

---

## 1. 왜 Go인가

| 상황                                    | Bash·Python                | Go                                |
|-----------------------------------------|----------------------------|-----------------------------------|
| 대상 서버에 런타임·패키지 설치가 어려움 | 인터프리터·라이브러리 필요 | 실행 파일 하나만 복사             |
| 여러 OS·CPU에 같은 도구 배포            | 환경마다 다름              | `GOOS`·`GOARCH`로 교차 빌드       |
| 동시에 수백 대에 요청                   | 스레드·asyncio 설정        | goroutine과 channel이 언어에 포함 |
| 빠르게 고쳐 한 번 돌리는 일             | 맞음                       | 컴파일 단계가 있어 번거로움       |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
GV=1.27.4
curl -sSLO https://go.dev/dl/go${GV}.linux-amd64.tar.gz
sha256sum go${GV}.linux-amd64.tar.gz      # go.dev/dl 페이지의 SHA256과 대조
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go${GV}.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
go version
```

- 컨테이너로 시험만 할 때는 `docker run --rm -it golang:1.27.4 bash`가 간단합니다(이 문서의 시험 방식).
- `go.mod`의 `go` 줄보다 설치된 Go가 낮으면 Go가 필요한 툴체인을 받아 쓰는 기능이 있습니다(`GOTOOLCHAIN`, 공식 이미지 기본값 `local`).

[⬆ 목차로 돌아가기](#목차)

---

## 3. 첫 도구

`hosts.json`:

```json
[
  {"name": "web01", "ip": "192.0.2.11", "role": "web"},
  {"name": "web02", "ip": "192.0.2.12", "role": "web"},
  {"name": "db01",  "ip": "192.0.2.21", "role": "db"}
]
```

`main.go`:

```go
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"os/exec"
	"strings"
	"time"
)

type Host struct {
	Name string `json:"name"`
	IP   string `json:"ip"`
	Role string `json:"role"`
}

func filterByRole(hosts []Host, role string) []Host {
	var out []Host
	for _, h := range hosts {
		if role == "" || h.Role == role {
			out = append(out, h)
		}
	}
	return out
}

func main() {
	file := flag.String("file", "hosts.json", "host list JSON")
	role := flag.String("role", "", "filter by role")
	flag.Parse()

	data, err := os.ReadFile(*file)
	if err != nil {
		fmt.Fprintln(os.Stderr, "read:", err)
		os.Exit(1)
	}
	var hosts []Host
	if err := json.Unmarshal(data, &hosts); err != nil {
		fmt.Fprintln(os.Stderr, "json:", err)
		os.Exit(2)
	}
	for _, h := range filterByRole(hosts, *role) {
		fmt.Printf("%-6s %-12s %s\n", h.Name, h.IP, h.Role)
	}

	// 외부 명령 (제한 시간 5초)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	out, err := exec.CommandContext(ctx, "uname", "-s").Output()
	if err != nil {
		fmt.Fprintln(os.Stderr, "exec:", err)
		os.Exit(3)
	}
	fmt.Println("kernel:", strings.TrimSpace(string(out)))

	// HTTP 요청 (제한 시간 3초, 예제용 로컬 서버)
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, "ok")
	}))
	defer srv.Close()
	client := &http.Client{Timeout: 3 * time.Second}
	resp, err := client.Get(srv.URL + "/health")
	if err != nil {
		fmt.Fprintln(os.Stderr, "http:", err)
		os.Exit(4)
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	fmt.Println("health:", resp.StatusCode, string(body))
}
```

```bash
go mod init example.com/hostlist
go run . -role web
```

```text
web01  192.0.2.11   web
web02  192.0.2.12   web
kernel: Linux
health: 200 ok
```

- JSON 필드는 구조체 태그(`json:"name"`)로 연결합니다. 대문자로 시작하는 필드만 JSON에 들어갑니다.
- 외부 명령은 셸을 거치지 않고 인수 목록으로 넘겨 따옴표·주입 문제를 피합니다. 셸 기능이 필요하면 `exec.Command("sh", "-c", ...)`를 쓰되 입력값을 넣지 않습니다.
- `http.Client`의 기본값은 제한 시간이 없으므로 `Timeout`을 꼭 줍니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 오류와 종료 코드

- Go는 예외 대신 함수가 `error`를 돌려주고, 호출한 쪽이 `if err != nil`로 처리합니다.
- 도구의 종료 코드는 `os.Exit(n)`으로 정합니다. 시험에서 없는 파일을 주면 `read: open nope.json: no such file or directory`와 종료 코드 1이었습니다. `go run`으로 실행하면 `exit status 1` 줄이 덧붙습니다(빌드한 실행 파일은 붙지 않음).
- `os.Exit`는 `defer`를 실행하지 않습니다. 정리할 것이 있으면 `main` 안의 다른 함수에서 오류를 돌려받아 마지막에 종료합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 테스트

`main_test.go`:

```go
package main

import "testing"

func TestFilterByRole(t *testing.T) {
	hosts := []Host{{"web01", "192.0.2.11", "web"}, {"db01", "192.0.2.21", "db"}}
	if got := filterByRole(hosts, "web"); len(got) != 1 || got[0].Name != "web01" {
		t.Fatalf("got %v", got)
	}
	if got := filterByRole(hosts, ""); len(got) != 2 {
		t.Fatalf("empty role should return all, got %d", len(got))
	}
}
```

```bash
go vet ./...      # 흔한 실수 정적 검사
go test ./...     # ok  example.com/hostlist  0.002s
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 빌드와 배포

```bash
# 정적 실행 파일 (C 라이브러리 의존 없음), 디버그 정보 제거
CGO_ENABLED=0 go build -ldflags="-s -w" -o hostlist .

# 교차 빌드
GOOS=windows GOARCH=amd64 go build -o hostlist.exe .
GOOS=linux   GOARCH=arm64 go build -o hostlist-arm64 .
```

- 시험에서 정적 빌드 결과는 7,237,792바이트이고 `ldd`는 `not a dynamic executable`이었습니다. 대상 서버에 이 파일 하나만 복사하면 됩니다.
- 컨테이너 이미지는 빌드 단계와 실행 단계를 나눠, 실행 이미지에는 실행 파일만 넣습니다([Dockerfile](../../02_infrastructure/containers/dockerfile_best_practices.md)의 멀티 스테이지).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 판과 지원

- 공식 정책: "Each major Go release is supported until there are two newer major releases." 2026-11-27 기준 1.27·1.26이 지원 판입니다.
- 메이저 판은 대체로 1년에 두 번 나옵니다. 운영 도구는 지원 판으로 다시 빌드해 보안 수정을 받습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용 | 방법                          | 기대 결과                  |
|------|-----------|-------------------------------|----------------------------|
| 1    | 설치      | `go version`                  | `go1.27.4`                 |
| 2    | 정적 검사 | `go vet ./...`                | 출력 없음                  |
| 3    | 테스트    | `go test ./...`               | `ok`                       |
| 4    | 정적 빌드 | `ldd hostlist`                | `not a dynamic executable` |
| 5    | 오류 처리 | 없는 파일로 실행 뒤 `echo $?` | 1                          |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                | 원인                                | 조치                      |
|-------------------------------------|-------------------------------------|---------------------------|
| `go: cannot find main module`       | `go.mod` 없음                       | `go mod init <모듈 경로>` |
| `go mod init` 뒤 `go mod tidy` 안내 | 외부 패키지 의존 정리 필요          | `go mod tidy`             |
| 다른 서버에서 `GLIBC_... not found` | cgo로 동적 링크됨                   | `CGO_ENABLED=0`으로 빌드  |
| `declared and not used`             | 쓰지 않는 변수·import는 컴파일 오류 | 지우거나 `_`로 받기       |
| HTTP 요청이 끝나지 않음             | `http.Client` 기본 제한 시간 없음   | `Timeout` 지정            |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [언어 비교(C·C++·C#·Go·Python·Bash)](./c_cpp_csharp_go_python_bash_comparison.md) — 언어 선택
- [Rust 로드맵](./rust_roadmap_for_se.md) — 또 다른 컴파일 언어
- [Node.js 입문](./nodejs_for_se.md) · [Ruby 입문](./ruby_for_se.md) — 같은 예제를 다른 언어로

---

## 참고 자료

- Go: [Downloads](https://go.dev/dl/) · [Release history](https://go.dev/doc/devel/release) · [Tutorial: Get started](https://go.dev/doc/tutorial/getting-started) · [Effective Go](https://go.dev/doc/effective_go) — ★★★☆☆

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
