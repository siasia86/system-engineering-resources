# Python 날짜·시간 처리 (datetime, zoneinfo, time)

로그 타임스탬프 파싱, 시간대 변환, 작업 소요 시간 측정처럼 운영 스크립트에서 자주 만나는 날짜·시간 처리를 표준 라이브러리 `datetime`·`zoneinfo`·`time`으로 정리합니다.

## 목차

| 섹션                                                                                                                  |
|-----------------------------------------------------------------------------------------------------------------------|
| [1. 기본 개념](#1-기본-개념) / [2. datetime 객체 만들기](#2-datetime-객체-만들기)                                     |
| [3. 시간대와 zoneinfo](#3-시간대와-zoneinfo) / [4. 문자열 변환](#4-문자열-변환)                                       |
| [5. 날짜 계산과 timedelta](#5-날짜-계산과-timedelta) / [6. time 모듈과 소요 시간 측정](#6-time-모듈과-소요-시간-측정) |
| [7. 실전 예제](#7-실전-예제) / [8. 자주 하는 실수와 점검표](#8-자주-하는-실수와-점검표)                               |

---

## 1. 기본 개념

| 용어              | 뜻                                                                 |
|-------------------|--------------------------------------------------------------------|
| UTC               | 협정 세계시. 서버·로그·DB 저장 기준으로 쓰는 시간                  |
| epoch(Unix time)  | 1970-01-01 00:00:00 UTC부터 지난 초                                |
| UTC offset        | UTC와의 차이. 한국 표준시는 `+09:00`                               |
| 시간대(time zone) | `Asia/Seoul`처럼 지역별 offset 규칙 묶음. 일광 절약 시간(DST) 포함 |
| naive datetime    | 시간대 정보(`tzinfo`)가 없는 값. 어느 시간대인지 알 수 없음        |
| aware datetime    | `utcoffset()`이 `None`이 아닌 값. 절대 시점이 정해짐               |
| ISO 8601          | `2026-11-16T09:30:00+09:00` 같은 국제 표준 날짜·시간 표기          |

원칙은 "저장·계산은 aware UTC, 사람에게 보여 줄 때만 지역 시간"입니다. naive 값과 aware 값을 빼거나 비교하면 `TypeError`가 납니다.

| 모듈       | 주요 클래스·함수                                    | 용도                      |
|------------|-----------------------------------------------------|---------------------------|
| `datetime` | `date`, `time`, `datetime`, `timedelta`, `timezone` | 날짜·시간 값과 계산       |
| `zoneinfo` | `ZoneInfo` (3.9+)                                   | IANA 시간대 데이터베이스  |
| `time`     | `time()`, `monotonic()`, `perf_counter()`           | 시계 읽기, 소요 시간 측정 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. datetime 객체 만들기

```python
import datetime as dt

now_utc = dt.datetime.now(dt.UTC)          # aware, UTC (dt.UTC는 3.11+)
now_local = dt.datetime.now().astimezone() # aware, 시스템 지역 시간대
naive = dt.datetime(2026, 11, 16, 9, 30)   # naive

print(now_utc.isoformat())     # 2026-11-16T00:30:00.123456+00:00 형태
print(naive.tzinfo)            # None
```

`datetime.utcnow()`와 `datetime.utcfromtimestamp()`는 3.12부터 사용 중단(deprecated)되었습니다. 둘 다 UTC 시각을 naive 값으로 돌려줘서 지역 시간과 섞이기 쉽기 때문입니다.

| 사용 중단된 호출                   | 대체 호출                               |
|------------------------------------|-----------------------------------------|
| `dt.datetime.utcnow()`             | `dt.datetime.now(dt.UTC)`               |
| `dt.datetime.utcfromtimestamp(ts)` | `dt.datetime.fromtimestamp(ts, dt.UTC)` |

### epoch와 변환

```python
ts = 1_700_000_000
when = dt.datetime.fromtimestamp(ts, dt.UTC)   # 2023-11-14 22:13:20+00:00
print(when.timestamp())                        # 1700000000.0

# naive 값의 timestamp()는 "시스템 지역 시간"으로 해석되므로 결과가 서버마다 다름
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 시간대와 zoneinfo

`zoneinfo.ZoneInfo`는 IANA 시간대 데이터베이스를 읽는 `tzinfo` 구현입니다(PEP 615). 데이터 자체는 포함하지 않고 아래 순서로 찾습니다.

1. 시스템 데이터베이스: `zoneinfo.TZPATH`의 디렉터리 (Linux는 보통 `/usr/share/zoneinfo`)
2. PyPI의 `tzdata` 패키지

둘 다 없으면 `ZoneInfoNotFoundError`가 납니다. Windows나 최소 컨테이너 이미지처럼 시스템 데이터가 없을 수 있는 환경에서는 `tzdata`를 의존성으로 선언합니다.

```bash
# 시스템 시간대 데이터 확인 (Debian/Ubuntu)
ls /usr/share/zoneinfo/Asia/Seoul
# 없으면 OS 패키지 또는 Python 패키지로 보충
python3 -m pip install tzdata
```

### 변환

```python
from zoneinfo import ZoneInfo
import datetime as dt

SEOUL = ZoneInfo("Asia/Seoul")
NY = ZoneInfo("America/New_York")

t_utc = dt.datetime(2026, 11, 16, 0, 30, tzinfo=dt.UTC)
print(t_utc.astimezone(SEOUL))   # 2026-11-16 09:30:00+09:00
print(t_utc.astimezone(NY))      # 2026-11-15 19:30:00-05:00

# naive 값에 시간대를 "붙이기" (값은 그대로, 의미만 부여)
local = dt.datetime(2026, 11, 16, 9, 30).replace(tzinfo=SEOUL)
```

`replace(tzinfo=...)`는 시각 숫자를 바꾸지 않고 시간대만 붙이고, `astimezone()`은 같은 순간을 다른 시간대 숫자로 바꿉니다. 두 동작을 혼동하면 9시간 차이 같은 오류가 생깁니다.

### 일광 절약 시간과 fold

DST가 끝나는 날에는 같은 지역 시각이 두 번 나옵니다. `fold=0`은 전환 전 offset, `fold=1`은 전환 후 offset을 뜻합니다.

```python
LA = ZoneInfo("America/Los_Angeles")
t = dt.datetime(2020, 11, 1, 1, 0, tzinfo=LA)
print(t)                     # 2020-11-01 01:00:00-07:00
print(t.replace(fold=1))     # 2020-11-01 01:00:00-08:00
```

`Asia/Seoul`은 현재 DST가 없지만, 해외 지역 서버나 사용자 시간을 다룰 때는 이 경우를 고려합니다. 반복 작업 예약은 UTC 기준으로 두는 편이 안전합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 문자열 변환

### ISO 8601

```python
s = "2026-11-16T09:30:00+09:00"
t = dt.datetime.fromisoformat(s)
print(t.isoformat())

# 3.11부터 Z 접미사와 더 넓은 ISO 형식을 받음
dt.datetime.fromisoformat("2026-11-16T00:30:00Z")   # tzinfo=UTC
```

3.10 이하에서는 `fromisoformat()`이 `isoformat()` 출력 형식만 받으므로 `Z`가 붙은 문자열에서 실패합니다. 오래된 서버에서 돌 스크립트라면 `s.replace("Z", "+00:00")`으로 바꾼 뒤 넘깁니다.

### strftime / strptime

| 코드 | 뜻                    | 예       |
|------|-----------------------|----------|
| `%Y` | 4자리 연도            | `2026`   |
| `%m` | 2자리 월              | `11`     |
| `%d` | 2자리 일              | `16`     |
| `%H` | 24시간제 시           | `09`     |
| `%M` | 분                    | `30`     |
| `%S` | 초                    | `00`     |
| `%f` | 마이크로초 (6자리)    | `123456` |
| `%z` | UTC offset            | `+0900`  |
| `%b` | 월 약어 (로캘 영향)   | `Nov`    |
| `%a` | 요일 약어 (로캘 영향) | `Mon`    |

```python
# Apache/Nginx 기본 로그 형식: [16/Nov/2026:09:30:00 +0900]
raw = "16/Nov/2026:09:30:00 +0900"
t = dt.datetime.strptime(raw, "%d/%b/%Y:%H:%M:%S %z")
print(t.astimezone(dt.UTC).isoformat())   # 2026-11-16T00:30:00+00:00

# 파일 이름용 문자열
stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")   # 20261116T003000Z
```

- `%b`·`%a`는 로캘(locale)에 따라 해석이 달라집니다. 영문 로그를 파싱하는 스크립트는 기본 `C` 로캘에서 실행하거나 월 이름을 직접 매핑합니다.
- syslog 전통 형식(`Nov 16 09:30:00`)에는 연도가 없습니다. 3.14부터 `date.strptime()`, 3.15부터 `datetime.strptime()`은 연도 없이 `%d`를 쓰면 `ValueError`를 냅니다. 연도를 문자열에 덧붙여 파싱합니다.

```python
line = "Nov 16 09:30:00 web01 sshd[1234]: Accepted publickey"
stamp = " ".join(line.split()[:3])
t = dt.datetime.strptime(f"2026 {stamp}", "%Y %b %d %H:%M:%S")
```

`date.strptime()`과 `time.strptime()` 클래스 메서드는 3.14에 추가되었습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 날짜 계산과 timedelta

`timedelta`는 두 시점의 차이(기간)입니다. 내부 값은 `days`, `seconds`(0~86399), `microseconds`로 나뉘어 저장됩니다.

```python
d = dt.timedelta(days=1, hours=2, minutes=30)
print(d.total_seconds())      # 95400.0

# 흔한 실수: .seconds는 "일 단위를 뺀 나머지 초"
d = dt.timedelta(seconds=11235813)
print(d.days, d.seconds)      # 130 3813
print(d.total_seconds())      # 11235813.0
```

### 경과 시간·기한 계산

```python
import datetime as dt

cert_not_after = dt.datetime(2027, 1, 10, tzinfo=dt.UTC)
remain = cert_not_after - dt.datetime.now(dt.UTC)
if remain < dt.timedelta(days=30):
    print(f"인증서 만료 {remain.days}일 전")
```

### 월 단위 계산

`timedelta`에는 월·년 단위가 없습니다. 한 달 뒤처럼 달력 기준 계산은 직접 처리합니다.

```python
import calendar

def add_months(d: dt.date, months: int) -> dt.date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    day = min(d.day, calendar.monthrange(year, month)[1])   # 1/31 + 1개월 → 2/28 또는 2/29
    return d.replace(year=year, month=month, day=day)

print(add_months(dt.date(2026, 1, 31), 1))   # 2026-02-28
```

### 지역 시간 기준 덧셈 주의

aware 값에 `timedelta`를 더하면 같은 `tzinfo` 안에서 "벽시계 시각"으로 계산됩니다. DST 전환을 넘어가면 실제 경과 시간은 24시간이 아닐 수 있습니다. 실제 경과 시간이 중요하면 UTC로 바꿔 계산한 뒤 다시 변환합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. time 모듈과 소요 시간 측정

| 함수                  | 시계 종류                     | 시스템 시각 변경 영향  | 용도               |
|-----------------------|-------------------------------|------------------------|--------------------|
| `time.time()`         | 벽시계(epoch 초, float)       | 받음 (뒤로 갈 수 있음) | 타임스탬프 기록    |
| `time.time_ns()`      | 벽시계(정수 나노초)           | 받음                   | 정밀 타임스탬프    |
| `time.monotonic()`    | 단조 시계(뒤로 가지 않음)     | 받지 않음              | timeout·경과 시간  |
| `time.perf_counter()` | 가장 정밀한 단조 시계         | 받지 않음              | 벤치마크·짧은 구간 |
| `time.process_time()` | 프로세스 CPU 시간(sleep 제외) | 해당 없음              | CPU 사용량 측정    |

NTP 동기화나 관리자가 시각을 바꾸면 `time.time()` 차이는 음수가 될 수도 있습니다. 소요 시간·timeout 계산에는 `monotonic()`이나 `perf_counter()`를 씁니다.

```python
import time

start = time.perf_counter()
run_backup()
elapsed = time.perf_counter() - start
print(f"backup took {elapsed:.2f}s")

# 기한 기반 재시도 루프
deadline = time.monotonic() + 60
while time.monotonic() < deadline:
    if service_ready():
        break
    time.sleep(2)
else:
    raise TimeoutError("service not ready in 60s")
```

시계 속성은 `time.get_clock_info("monotonic")`로 확인할 수 있습니다(`adjustable`, `resolution` 등).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실전 예제

### 최근 N분 로그만 골라내기

```python
#!/usr/bin/env python3
"""Nginx access.log에서 최근 10분 요청 수를 셉니다."""
import datetime as dt
import re
import sys

PATTERN = re.compile(r"\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]")

def main(path: str, minutes: int = 10) -> int:
    since = dt.datetime.now(dt.UTC) - dt.timedelta(minutes=minutes)
    count = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = PATTERN.search(line)
            if not m:
                continue
            t = dt.datetime.strptime(m.group(1), "%d/%b/%Y:%H:%M:%S %z")
            if t >= since:          # aware끼리 비교하므로 시간대가 달라도 정확
                count += 1
    print(f"last {minutes}m: {count} requests")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
```

### 날짜별 백업 보존 정리 대상 고르기

```python
from pathlib import Path
import datetime as dt

KEEP_DAYS = 14
cutoff = dt.datetime.now(dt.UTC) - dt.timedelta(days=KEEP_DAYS)

for p in Path("/backup").glob("db_*.sql.gz"):
    mtime = dt.datetime.fromtimestamp(p.stat().st_mtime, dt.UTC)
    if mtime < cutoff:
        print("expired:", p)     # 확인 후에만 p.unlink()로 삭제
```

🟡 주의: 삭제를 자동화할 때는 먼저 목록만 출력해 대상을 확인하고, 시간대·시계 오차로 최신 파일이 지워지지 않는지 검증한 뒤 삭제 코드를 켭니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 자주 하는 실수와 점검표

| 실수                              | 증상                                    | 대응                                |
|-----------------------------------|-----------------------------------------|-------------------------------------|
| `datetime.now()`(naive)로 저장    | 서버 시간대가 다르면 값 의미가 바뀜     | `now(dt.UTC)`로 aware UTC 저장      |
| naive와 aware 비교                | `TypeError: can't compare ...`          | 입력 단계에서 모두 aware로 통일     |
| `replace(tzinfo=)`로 시간대 변환  | 시각 숫자가 그대로라 9시간 어긋남       | 변환은 `astimezone()`               |
| `timedelta.seconds`로 총 초 계산  | 하루 넘는 기간이 작게 나옴              | `total_seconds()`                   |
| `time.time()` 차이로 timeout 계산 | NTP 보정 때 음수·과대 값                | `time.monotonic()`                  |
| 컨테이너에 시간대 데이터 없음     | `ZoneInfoNotFoundError`                 | OS `tzdata` 또는 PyPI `tzdata` 설치 |
| 연도 없는 syslog 시각 파싱        | 3.15에서 `ValueError`, 연말에 연도 오류 | 연도를 명시하고 연말 경계 보정      |

| 점검 항목                                              | 확인 |
|--------------------------------------------------------|------|
| 저장·전송 값은 aware UTC 또는 offset 포함 ISO 8601인가 | [ ]  |
| 화면·보고서 출력 직전에만 지역 시간으로 바꾸는가       | [ ]  |
| 경과 시간·timeout은 단조 시계로 계산하는가             | [ ]  |
| 로그 파싱 형식이 로캘·연도 누락에 영향받지 않는가      | [ ]  |
| 실행 환경에 시간대 데이터가 있는가                     | [ ]  |
| 서버 시각이 NTP로 동기화되어 있는가 (`timedatectl`)    | [ ]  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Python Documentation: [datetime](https://docs.python.org/3/library/datetime.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [zoneinfo](https://docs.python.org/3/library/zoneinfo.html) — ★★★☆☆ (확인일 2026-11-16)
- Python Documentation: [time](https://docs.python.org/3/library/time.html) — ★★★☆☆ (확인일 2026-11-16)
- PEP 615: [Support for the IANA Time Zone Database in the Standard Library](https://peps.python.org/pep-0615/) — ★★★☆☆ (확인일 2026-11-16)
- IANA: [Time Zone Database](https://www.iana.org/time-zones) — ★★★☆☆ (확인일 2026-11-16)
- RFC 3339: [Date and Time on the Internet: Timestamps](https://www.rfc-editor.org/rfc/rfc3339) — ★★★★☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.
