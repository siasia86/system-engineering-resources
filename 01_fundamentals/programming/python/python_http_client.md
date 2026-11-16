# Python HTTP 클라이언트 (urllib.request, requests)

헬스 체크, REST API 호출, 파일 다운로드처럼 운영 스크립트에서 HTTP 요청을 보낼 때 쓰는 표준 라이브러리 `urllib.request`와 외부 패키지 `requests`를 timeout·재시도·TLS·프록시 관점에서 정리합니다. HTTP 자체와 API 설계는 [REST API 가이드](../rest_api_guide_for_se.md)를 함께 봅니다.

## 목차

| 섹션                                                                                      |
|-------------------------------------------------------------------------------------------|
| [1. 도구 선택](#1-도구-선택) / [2. urllib.request 기본](#2-urllibrequest-기본)            |
| [3. requests 기본](#3-requests-기본) / [4. timeout](#4-timeout)                           |
| [5. 재시도와 백오프](#5-재시도와-백오프) / [6. TLS 인증서 검증](#6-tls-인증서-검증)       |
| [7. 프록시와 환경 변수](#7-프록시와-환경-변수) / [8. 대용량 다운로드](#8-대용량-다운로드) |
| [9. 실전 예제](#9-실전-예제) / [10. 점검표](#10-점검표)                                   |

---

## 1. 도구 선택

| 항목           | `urllib.request` (표준)              | `requests` (PyPI)                         |
|----------------|--------------------------------------|-------------------------------------------|
| 설치           | 필요 없음                            | `pip install requests`                    |
| 연결 재사용    | 요청마다 `Connection: close`         | `Session`이 연결 풀로 재사용              |
| HTTP 오류 처리 | 4xx·5xx에서 `HTTPError` 발생         | 예외 없음, `raise_for_status()`로 확인    |
| 재시도         | 직접 구현                            | `HTTPAdapter(max_retries=Retry(...))`     |
| JSON           | `json.loads(resp.read())`            | `resp.json()`                             |
| 적합한 곳      | 패키지 설치가 어려운 서버, 단발 호출 | 반복 호출, 인증·세션·재시도가 필요한 도구 |

- `requests` 판: 2.34.2, Python 3.10 이상 필요 (PyPI, 2026-11-16 확인).
- Python 공식 문서도 고수준 HTTP 클라이언트로 `requests`를 권합니다.
- 두 도구 모두 동기(blocking) 방식입니다. 많은 연결을 동시에 다루려면 [동시성](python_concurrency.md)의 스레드 풀이나 [비동기 프로그래밍](python_async.md)을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. urllib.request 기본

```python
import json
import urllib.error
import urllib.request

req = urllib.request.Request(
    "https://api.example.com/v1/status",
    headers={"Accept": "application/json", "User-Agent": "ops-check/1.0"},
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.status, resp.headers.get("Content-Type"))
        data = json.loads(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:        # 서버가 4xx·5xx로 응답
    print("HTTP", e.code, e.read()[:200])
except urllib.error.URLError as e:         # DNS 실패, 연결 거부, timeout 등
    print("connection error:", e.reason)
```

- `HTTPError`는 `URLError`의 하위 클래스이므로 `HTTPError`를 먼저 잡습니다.
- 응답을 읽는 중에 나는 `TimeoutError`, `http.client.RemoteDisconnected` 같은 예외는 `URLError`로 감싸지지 않습니다. 넓게 잡으려면 `OSError`도 함께 처리합니다.
- `timeout`을 생략하면 전역 소켓 기본값(설정하지 않았다면 무제한 대기)을 씁니다.

### POST(JSON)

```python
payload = json.dumps({"host": "web01", "state": "ok"}).encode("utf-8")
req = urllib.request.Request(
    "https://api.example.com/v1/report",
    data=payload,
    method="POST",
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=10) as resp:
    print(resp.status)
```

`data`를 주면 기본 메서드는 POST, 없으면 GET입니다. `Content-Type`을 지정하지 않으면 `application/x-www-form-urlencoded`가 붙습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. requests 기본

```python
import requests

resp = requests.get(
    "https://api.example.com/v1/hosts",
    params={"env": "prod", "limit": 100},      # 쿼리 문자열 자동 인코딩
    headers={"Accept": "application/json"},
    timeout=(3.05, 10),
)
resp.raise_for_status()                        # 4xx·5xx면 HTTPError 발생
for host in resp.json()["items"]:
    print(host["name"])
```

### Session

`Session`은 헤더·인증·쿠키를 유지하고 urllib3 연결 풀로 같은 호스트의 TCP·TLS 연결을 재사용합니다. 같은 API를 여러 번 부르면 `Session`을 씁니다.

```python
import os
import requests

with requests.Session() as s:
    s.headers.update({"Authorization": f"Bearer {os.environ['API_TOKEN']}"})
    for page in range(1, 4):
        r = s.get("https://api.example.com/v1/events",
                  params={"page": page}, timeout=10)
        r.raise_for_status()
        print(len(r.json()["items"]))
```

토큰·비밀번호는 코드에 쓰지 않고 환경 변수나 비밀 관리 도구에서 읽습니다. 예외 메시지나 로그에 `Authorization` 헤더가 찍히지 않는지도 확인합니다.

### 예외 계층

| 예외                                   | 발생 상황                           |
|----------------------------------------|-------------------------------------|
| `requests.exceptions.ConnectTimeout`   | 연결 수립 시간 초과                 |
| `requests.exceptions.ReadTimeout`      | 응답 바이트 사이 대기 시간 초과     |
| `requests.exceptions.ConnectionError`  | DNS 실패, 연결 거부, 연결 끊김      |
| `requests.exceptions.SSLError`         | 인증서 검증 실패                    |
| `requests.exceptions.HTTPError`        | `raise_for_status()`가 4xx·5xx 감지 |
| `requests.exceptions.RequestException` | 위 예외 전체의 상위 클래스          |

[⬆ 목차로 돌아가기](#목차)

---

## 4. timeout

`requests`는 timeout을 지정하지 않으면 시간 제한 없이 기다립니다. 응답 없는 서버 하나 때문에 cron 작업 전체가 멈출 수 있으므로 모든 호출에 timeout을 줍니다.

| 값                   | 의미                                        |
|----------------------|---------------------------------------------|
| `timeout=5`          | 연결 timeout과 읽기 timeout 모두 5초        |
| `timeout=(3.05, 27)` | 연결 3.05초, 읽기 27초                      |
| `timeout=None`       | 무제한 대기 (운영 스크립트에서는 쓰지 않음) |

- 연결(connect) timeout은 TCP 연결 시도 한 번에 적용됩니다. 도메인에 IPv4·IPv6 주소가 여러 개면 차례로 시도하므로 실제 대기는 몇 배가 될 수 있습니다.
- 읽기(read) timeout은 "전체 응답 시간"이 아니라 서버가 보내는 바이트 사이의 최대 대기입니다. 느리게 조금씩 오는 응답은 오래 걸려도 timeout이 나지 않습니다.
- 전체 시간 상한이 필요하면 호출 바깥에서 `time.monotonic()` 기한을 확인하거나, 스트리밍으로 읽으며 경과 시간을 직접 검사합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 재시도와 백오프

`requests`는 기본적으로 재시도하지 않습니다. urllib3의 `Retry`를 `HTTPAdapter`에 연결하면 연결 오류·지정 상태 코드에서 자동으로 다시 시도합니다.

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

retry = Retry(
    total=5,
    connect=3,
    read=2,
    status=3,
    backoff_factor=0.5,
    status_forcelist=[429, 502, 503, 504],
    allowed_methods={"GET", "HEAD", "PUT", "DELETE", "OPTIONS"},
    respect_retry_after_header=True,
)
s = requests.Session()
adapter = HTTPAdapter(max_retries=retry)
s.mount("https://", adapter)
s.mount("http://", adapter)

resp = s.get("https://api.example.com/v1/health", timeout=(3.05, 10))
```

| 매개변수                     | 의미 (urllib3 문서 기준)                                               |
|------------------------------|------------------------------------------------------------------------|
| `total`                      | 전체 재시도 상한. 다른 횟수보다 우선                                   |
| `connect`, `read`, `status`  | 오류 종류별 재시도 상한                                                |
| `backoff_factor`             | 대기 = `backoff_factor * 2 ** (이전 재시도 횟수)`, 기본 0(대기 없음)   |
| `backoff_max`                | 대기 상한, 기본 120초                                                  |
| `status_forcelist`           | 재시도할 응답 상태 코드                                                |
| `allowed_methods`            | 재시도할 메서드. 기본은 멱등 메서드(DELETE·GET·HEAD·OPTIONS·PUT·TRACE) |
| `respect_retry_after_header` | 413·429·503의 `Retry-After` 헤더를 따름, 기본 True                     |

판단 기준은 다음과 같습니다.

- 멱등(idempotent)은 같은 요청을 여러 번 보내도 결과가 같다는 뜻입니다. POST처럼 멱등이 아닌 요청은 서버가 처리했는데 응답만 잃은 경우 중복 생성이 생기므로 기본적으로 재시도하지 않습니다. 서버가 멱등 키(idempotency key)를 지원할 때만 POST 재시도를 켭니다.
- 400·401·403·404는 다시 보내도 결과가 같으므로 재시도 목록에 넣지 않습니다.
- 백오프(backoff)는 실패할수록 대기를 늘리는 방식입니다. 여러 클라이언트가 동시에 재시도해 서버를 다시 넘어뜨리지 않도록 `backoff_jitter`(무작위 추가 대기)도 고려합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. TLS 인증서 검증

두 도구 모두 기본으로 HTTPS 인증서를 검증합니다.

| 상황                    | `requests`                                           | `urllib.request`                                        |
|-------------------------|------------------------------------------------------|---------------------------------------------------------|
| 기본 CA 묶음            | `certifi` 패키지                                     | 시스템 CA (`ssl.create_default_context()`)              |
| 사내 CA 사용            | `verify="/etc/pki/ca.pem"` 또는 `REQUESTS_CA_BUNDLE` | `ssl.create_default_context(cafile=...)`를 `context=`로 |
| 클라이언트 인증서(mTLS) | `cert=("client.crt", "client.key")`                  | `context.load_cert_chain(...)`                          |

```python
import ssl
import urllib.request

ctx = ssl.create_default_context(cafile="/etc/pki/tls/certs/internal-ca.pem")
with urllib.request.urlopen("https://internal.example.com/health",
                            context=ctx, timeout=5) as resp:
    print(resp.status)
```

- `requests`는 사내 CA를 시스템 저장소에 넣어도 기본적으로 `certifi` 묶음을 쓰므로 검증에 실패할 수 있습니다. `REQUESTS_CA_BUNDLE`로 시스템 묶음(예: Debian 계열 `/etc/ssl/certs/ca-certificates.crt`)을 지정합니다.
- `urllib.request.urlopen()`의 `cafile`·`capath`·`cadefault` 인자는 3.13에서 제거되었습니다. `context=`를 씁니다.
- 🟡 주의: `verify=False`는 중간자 공격(MitM)에 노출됩니다. 임시 시험 외에는 쓰지 말고, 쓰더라도 사내 CA를 지정하는 방식으로 바꿉니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 프록시와 환경 변수

두 도구 모두 `http_proxy`, `https_proxy`, `no_proxy`(대문자도 인식)를 읽습니다.

```bash
export https_proxy="http://proxy.example.com:3128"
export no_proxy="localhost,127.0.0.1,.internal.example.com"
```

```python
import urllib.request
print(urllib.request.getproxies())   # 현재 인식된 프록시 확인

# requests에서 이 요청만 프록시 지정
requests.get("https://example.com", timeout=10,
             proxies={"https": "http://proxy.example.com:3128"})

# urllib에서 환경 변수 프록시를 무시
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
```

- `requests`의 `Session.proxies` 값은 환경 변수 프록시에 덮어써질 수 있습니다. 확실히 지정하려면 요청마다 `proxies=`를 넘깁니다.
- `urllib.request`는 CGI 환경(`REQUEST_METHOD`가 설정됨)에서 `HTTP_PROXY`를 무시합니다. 클라이언트가 `Proxy:` 헤더로 값을 주입할 수 있기 때문입니다.
- SOCKS 프록시는 `pip install 'requests[socks]'` 후 `socks5h://`(DNS를 프록시에서 해석) 또는 `socks5://`(로컬에서 해석)를 씁니다.
- 프록시 URL에 계정·비밀번호를 넣으면 환경 변수 목록·프로세스 정보로 노출될 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 대용량 다운로드

`stream=True`를 쓰면 헤더만 먼저 받고 본문은 나눠 읽습니다. 메모리에 파일 전체를 올리지 않습니다.

```python
import hashlib
import os
import requests

def download(url: str, dest: str, sha256: str | None = None) -> None:
    tmp = dest + ".part"
    h = hashlib.sha256()
    with requests.get(url, stream=True, timeout=(3.05, 30)) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):   # 1 MiB
                f.write(chunk)
                h.update(chunk)
    if sha256 and h.hexdigest() != sha256:
        os.remove(tmp)
        raise ValueError("checksum mismatch")
    os.replace(tmp, dest)          # 검증 후 원자적으로 교체
```

- `with` 문을 쓰지 않고 본문을 다 읽지 않으면 연결이 풀로 돌아가지 않습니다.
- 임시 파일에 받은 뒤 체크섬을 확인하고 `os.replace()`로 바꾸면 중간에 끊겨도 반쯤 받은 파일이 정상 파일처럼 남지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 실전 예제

### 여러 엔드포인트 헬스 체크 (표준 라이브러리만)

```python
#!/usr/bin/env python3
"""URL 목록의 HTTP 상태와 응답 시간을 점검합니다. 실패가 있으면 종료 코드 1."""
from concurrent.futures import ThreadPoolExecutor
import time
import urllib.error
import urllib.request

URLS = [
    "https://www.example.com/",
    "https://api.example.com/healthz",
]

def check(url: str) -> tuple[str, int | None, float, str]:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "healthcheck/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read(1024)
            return url, resp.status, time.perf_counter() - start, ""
    except urllib.error.HTTPError as e:
        return url, e.code, time.perf_counter() - start, ""
    except (urllib.error.URLError, OSError) as e:
        return url, None, time.perf_counter() - start, str(getattr(e, "reason", e))

def main() -> int:
    bad = 0
    with ThreadPoolExecutor(max_workers=10) as pool:
        for url, status, sec, err in pool.map(check, URLS):
            ok = status is not None and 200 <= status < 400
            bad += not ok
            print(f"{'OK  ' if ok else 'FAIL'} {status or '-':>3} {sec*1000:7.1f}ms {url} {err}")
    return 1 if bad else 0

if __name__ == "__main__":
    raise SystemExit(main())
```

### curl과 대응 표

| curl                                                       | requests                                    |
|------------------------------------------------------------|---------------------------------------------|
| `curl -sS URL`                                             | `requests.get(URL, timeout=10)`             |
| `-H 'Accept: application/json'`                            | `headers={"Accept": "application/json"}`    |
| `--data-raw '{"a":1}' -H 'Content-Type: application/json'` | `json={"a": 1}`                             |
| `--connect-timeout 3 --max-time 30`                        | `timeout=(3, 30)` (읽기는 바이트 간격 기준) |
| `--cacert ca.pem`                                          | `verify="ca.pem"`                           |
| `-x http://proxy:3128`                                     | `proxies={"https": "http://proxy:3128"}`    |
| `-f` (4xx·5xx를 실패로)                                    | `resp.raise_for_status()`                   |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 점검표

| 점검 항목                                                        | 확인 |
|------------------------------------------------------------------|------|
| 모든 요청에 timeout이 있는가                                     | [ ]  |
| 4xx·5xx를 성공으로 처리하지 않는가 (`raise_for_status()` 등)     | [ ]  |
| 재시도는 멱등 메서드와 일시적 오류(429·502·503·504)로 한정했는가 | [ ]  |
| 재시도 사이에 백오프가 있는가                                    | [ ]  |
| `verify=False`나 검증 끈 SSL 컨텍스트가 남아 있지 않은가         | [ ]  |
| 토큰·비밀번호가 코드·로그·프록시 URL에 노출되지 않는가           | [ ]  |
| 반복 호출에 `Session`을 재사용하는가                             | [ ]  |
| 큰 응답은 `stream=True`로 나눠 받고 체크섬을 확인하는가          | [ ]  |
| 스크립트 종료 코드가 실패를 반영하는가 (cron·모니터링 연동)      | [ ]  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Python Documentation: [urllib.request](https://docs.python.org/3/library/urllib.request.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [urllib.error](https://docs.python.org/3/library/urllib.error.html) — ★★★☆☆ (확인일 2026-11-16)
- Requests Documentation: [Advanced Usage](https://requests.readthedocs.io/en/latest/user/advanced/) — ★★★☆☆ (확인일 2026-11-16)
- PyPI: [requests](https://pypi.org/project/requests/) — ★★★☆☆ (확인일 2026-11-16)
- urllib3 Documentation: [Retry](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html) — ★★★☆☆ (확인일 2026-11-16)
- RFC 9110: [HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) — ★★★★☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
