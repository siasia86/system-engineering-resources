# Python argparse - CLI 도구 제작

명령줄 인터페이스(CLI) 도구 제작을 위한 argparse 가이드입니다.

## 목차
- [기본 사용법](#기본-사용법)
- [인자 타입](#인자-타입)
- [고급 옵션](#고급-옵션)
- [서브커맨드](#서브커맨드)
- [실전 예제](#실전-예제)
- [요약](#요약)

---

## 기본 사용법

### 최소 구조

```python
import argparse

parser = argparse.ArgumentParser(description='서버 관리 도구')
parser.add_argument('hostname', help='대상 호스트명')
parser.add_argument('-p', '--port', type=int, default=22, help='포트 번호')
parser.add_argument('-v', '--verbose', action='store_true', help='상세 출력')

args = parser.parse_args()
print(f"호스트: {args.hostname}, 포트: {args.port}")
```

```bash
$ python tool.py web-01 -p 8080 -v
호스트: web-01, 포트: 8080
```

### 위치 인자 vs 옵션 인자

```python
# 위치 인자 (필수)
parser.add_argument('filename')           # 이름으로 접근

# 옵션 인자 (선택)
parser.add_argument('-o', '--output')     # 짧은/긴 형태
parser.add_argument('--dry-run')          # 긴 형태만
```

---

## 인자 타입

### type

```python
parser.add_argument('--count', type=int)
parser.add_argument('--ratio', type=float)
parser.add_argument('--config', type=argparse.FileType('r'))
```

### choices

```python
parser.add_argument('--env', choices=['dev', 'stg', 'prd'], required=True)
parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
```

### nargs

```python
parser.add_argument('files', nargs='+')          # 1개 이상
parser.add_argument('--targets', nargs='*')       # 0개 이상
parser.add_argument('--range', nargs=2, type=int) # 정확히 2개
parser.add_argument('--config', nargs='?', const='default.yml')  # 0 또는 1개
```

### action

```python
parser.add_argument('-v', '--verbose', action='store_true')   # 플래그
parser.add_argument('--no-cache', action='store_false', dest='cache')
parser.add_argument('-d', '--debug', action='count', default=0)  # -ddd → 3
parser.add_argument('--version', action='version', version='1.0.0')
```

### default / required

```python
parser.add_argument('--timeout', type=int, default=30)
parser.add_argument('--token', required=True)
```

---

## 고급 옵션

### 상호 배타 그룹

```python
group = parser.add_mutually_exclusive_group()
group.add_argument('--start', action='store_true')
group.add_argument('--stop', action='store_true')
group.add_argument('--restart', action='store_true')
```

### 인자 그룹

```python
db_group = parser.add_argument_group('데이터베이스 옵션')
db_group.add_argument('--db-host', default='localhost')
db_group.add_argument('--db-port', type=int, default=5432)
db_group.add_argument('--db-name', required=True)
```

### epilog (도움말 하단)

```python
parser = argparse.ArgumentParser(
    description='서버 관리 도구',
    epilog='예시: %(prog)s web-01 --env prd --restart',
    formatter_class=argparse.RawDescriptionHelpFormatter
)
```

---

## 서브커맨드

```python
parser = argparse.ArgumentParser(description='서버 관리 도구')
subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령')

# deploy 서브커맨드
deploy_parser = subparsers.add_parser('deploy', help='배포')
deploy_parser.add_argument('service', help='서비스명')
deploy_parser.add_argument('--env', choices=['dev', 'stg', 'prd'], required=True)

# status 서브커맨드
status_parser = subparsers.add_parser('status', help='상태 확인')
status_parser.add_argument('--all', action='store_true', help='전체 서비스')

# logs 서브커맨드
logs_parser = subparsers.add_parser('logs', help='로그 조회')
logs_parser.add_argument('service', help='서비스명')
logs_parser.add_argument('-n', '--lines', type=int, default=100)

args = parser.parse_args()

if args.command == 'deploy':
    print(f"{args.service}를 {args.env}에 배포")
elif args.command == 'status':
    print("상태 확인")
elif args.command == 'logs':
    print(f"{args.service} 로그 {args.lines}줄")
```

```bash
$ python tool.py deploy nginx --env prd
$ python tool.py status --all
$ python tool.py logs nginx -n 50
```

### 환경변수 fallback

```python
import os

parser.add_argument(
    '--token',
    default=os.environ.get('API_TOKEN'),
    help='API 토큰 (환경변수 API_TOKEN으로도 설정 가능)'
)
```

### 인자 유효성 검사

```python
def valid_port(value):
    port = int(value)
    if not (1 <= port <= 65535):
        raise argparse.ArgumentTypeError(f"유효하지 않은 포트: {value}")
    return port

parser.add_argument('--port', type=valid_port, default=8080)
```

---

## 실전 예제

### 서버 관리 CLI

```python
#!/usr/bin/env python3
import argparse
import subprocess
import sys

def cmd_ping(args):
    for host in args.hosts:
        result = subprocess.run(
            ['ping', '-c', str(args.count), '-W', '2', host],
            capture_output=True, text=True
        )
        status = "🟢" if result.returncode == 0 else "🔴"
        print(f"{status} {host}")

def cmd_disk(args):
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        if args.threshold:
            parts = line.split()
            if len(parts) >= 5 and parts[4].endswith('%'):
                usage = int(parts[4].replace('%', ''))
                if usage >= args.threshold:
                    print(line)
        else:
            print(line)

def main():
    parser = argparse.ArgumentParser(description='서버 관리 도구')
    subparsers = parser.add_subparsers(dest='command')

    # ping
    ping_parser = subparsers.add_parser('ping', help='호스트 연결 확인')
    ping_parser.add_argument('hosts', nargs='+', help='대상 호스트')
    ping_parser.add_argument('-c', '--count', type=int, default=3)
    ping_parser.set_defaults(func=cmd_ping)

    # disk
    disk_parser = subparsers.add_parser('disk', help='디스크 사용량')
    disk_parser.add_argument('-t', '--threshold', type=int, help='임계값 (%)')
    disk_parser.set_defaults(func=cmd_disk)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

```bash
$ python sysadmin.py ping 8.8.8.8 1.1.1.1
$ python sysadmin.py disk -t 80
```

---

## 요약

| 항목 | 설명 | 예시 |
|------|------|------|
| 위치 인자 | 필수, 순서대로 | `add_argument('host')` |
| 옵션 인자 | 선택, 이름 지정 | `add_argument('--port')` |
| type | 타입 변환 | `type=int` |
| choices | 허용 값 제한 | `choices=['a','b']` |
| action | 동작 방식 | `action='store_true'` |
| nargs | 인자 개수 | `nargs='+'` |
| subparsers | 서브커맨드 | `add_subparsers()` |

**관련 문서:**
- [subprocess](./python_subprocess.md) - 외부 명령 실행
- [함수](./python_functions.md) - 함수 정의
- [패키지](./python_packages.md) - 모듈 구조화
