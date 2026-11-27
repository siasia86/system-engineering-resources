---
name: go-official-notes
description: Go 1.27.4 판과 지원 정책, golang 이미지 시험 결과(vet·test·정적 빌드·교차 빌드) 정리.
tags:
  - go
  - programming
last_checked: 2026-11-27
sources:
  - https://go.dev/dl/?mode=json
  - https://go.dev/doc/devel/release
---

# Go 공식 자료 참조 노트

## 1. 판과 지원 (2026-11-27 확인)

- go.dev/dl JSON의 안정 판: go1.27.4, go1.26.11.
- "Each major Go release is supported until there are two newer major releases."

## 2. 컨테이너 시험 (golang:1.27.4)

- `go version go1.27.4 linux/amd64`, `GOPATH=/go`, `GOTOOLCHAIN=local`, `go mod init` 뒤 `go.mod`에 `go 1.27.4`.
- `go vet` 통과, `go test` `ok ... 0.002s`.
- 예제 실행(JSON 필터, `exec.CommandContext`, `httptest` 서버 + `http.Client{Timeout}`) 정상.
- 없는 파일: `read: open nope.json: no such file or directory`, 종료 코드 1, `go run`은 `exit status 1` 추가 출력.
- `CGO_ENABLED=0 go build -ldflags="-s -w"`: 7,237,792바이트, `ldd`는 `not a dynamic executable`. `GOOS=windows`·`GOARCH=arm64` 교차 빌드 성공.
