# CDN, Proxy, Origin IP 정리

## 1. Origin IP란?

Origin IP는 웹사이트나 서비스의 실제 서버 IP 주소를 의미한다. CDN이나 프록시 뒤에 숨겨진 "원본 서버"의 IP이다.

### DNS와 Origin IP의 관계

```
사용자 → DNS 조회 → CDN/프록시 IP (공개) → Origin IP (비공개)
```

### 일반적인 흐름

```
+------------------+        +------------------+        +------------------+
|     사용자        |------->|   CDN/Proxy      |------->|  Origin Server   |
|                  |        | (CloudFront,     |        |  (실제 서버)      |
|                  |        |  Cloudflare 등)  |        |  Origin IP       |
+------------------+        +------------------+        +------------------+
        |                          ^
        |   DNS 조회               |
        v                          |
+------------------+               |
|   DNS Server     |---------------+
| example.com →    |
| CDN IP 반환      |
+------------------+
```

### 핵심 포인트

- **Origin IP**: 실제 애플리케이션이 동작하는 서버의 IP (예: EC2, 온프레미스 서버)
- CDN/프록시 사용 시 DNS는 CDN의 IP를 반환하고, CDN이 내부적으로 Origin IP로 트래픽을 전달
- Origin IP가 외부에 노출되면 CDN을 우회한 직접 공격(DDoS 등)이 가능하므로 보호가 중요

### 예시 (CloudFront + ALB 구성)

```
사용자 → DNS(example.com) → CloudFront(d1234.cloudfront.net)
                                    |
                                    v
                              ALB (공인 IP, 동적으로 변경됨)
                                    |
                                    v
                              EC2 인스턴스 (예: 10.0.1.50)
```

- 사용자에게 보이는 IP: CloudFront의 엣지 IP
- Origin IP: ALB의 DNS 이름 또는 EC2의 실제 IP
- ALB는 여러 AZ에 걸쳐 IP가 동적으로 변경되므로, IP가 아닌 DNS 이름으로 Origin을 지정
- DNS에 Origin IP를 직접 등록하지 않고 CloudFront 도메인을 CNAME으로 설정

### Origin IP 보호 방법

1. Security Group에서 CDN IP 대역만 허용
2. Origin IP를 DNS에 직접 노출하지 않기
3. WAF를 CDN 레벨에서 적용
4. Origin 서버에 커스텀 헤더 검증 설정 (CDN에서 보낸 요청만 수락)

---

## 2. CDN과 Proxy의 차이

둘 다 클라이언트와 Origin 서버 사이에 위치하지만, 목적과 동작 방식이 다르다.

### 핵심 차이

| 구분 | CDN | Proxy |
|------|-----|-------|
| 주 목적 | 콘텐츠 캐싱 및 빠른 전달 | 트래픽 중계 및 제어 |
| 위치 | 전 세계 엣지 서버에 분산 | 보통 단일 또는 소수 지점 |
| 캐싱 | 핵심 기능 (정적 콘텐츠 캐싱) | 선택적 (있을 수도 없을 수도) |
| 대표 서비스 | CloudFront, Cloudflare CDN, Akamai | Nginx, HAProxy, Squid |

### 동작 비교

```
[CDN]
사용자(서울) → 엣지 서버(서울) → 캐시 HIT → 바로 응답 (Origin 안 감)
사용자(서울) → 엣지 서버(서울) → 캐시 MISS → Origin 서버(미국) → 응답 + 캐싱

[Proxy (Reverse Proxy)]
사용자 → Proxy → Origin 서버 → 응답
         (기본적으로 매 요청 전달, 캐싱 설정 시 CDN처럼 동작 가능)
```

### Proxy의 종류

```
+------------------+                              +------------------+
|     사용자        |----> Forward Proxy --------->|   외부 서버       |
| (내부 네트워크)   |     (사용자 측에 위치)         |                  |
+------------------+                              +------------------+

+------------------+                              +------------------+
|     사용자        |----> Reverse Proxy --------->|   Origin 서버    |
| (외부)           |     (서버 측에 위치)           |                  |
+------------------+                              +------------------+
```

- **Forward Proxy**: 클라이언트를 숨김 (사내망에서 외부 접속 시)
- **Reverse Proxy**: 서버를 숨김 (외부에서 내부 서버 접속 시) ← CDN과 비슷한 위치

### CDN과 Proxy의 관계

CDN은 "전 세계에 분산된 Reverse Proxy + 캐싱"이라고 볼 수 있다.

```
+------------------------------------------------------------------+
|                        Reverse Proxy                              |
|   +----------------------------------------------------------+   |
|   |                         CDN                               |   |
|   |   (분산 배치 + 캐싱 + 지리적 라우팅)                        |   |
|   +----------------------------------------------------------+   |
+------------------------------------------------------------------+
```

- 모든 CDN은 Reverse Proxy 역할을 포함
- 모든 Reverse Proxy가 CDN은 아님

### 실무에서의 선택 기준

- 정적 콘텐츠 가속, 글로벌 사용자 대응 → **CDN** (CloudFront, Cloudflare)
- 로드밸런싱, SSL 종료, 라우팅 제어 → **Reverse Proxy** (Nginx, ALB)
- 보통 둘 다 함께 사용: `사용자 → CDN → Reverse Proxy(ALB) → 서버`

---

## 3. Origin IP 노출 확인 방법

Origin IP가 실수로 노출되면 CDN/WAF를 우회한 직접 공격이 가능해진다.

### 흔한 노출 경로

- DNS 변경 히스토리에 과거 A 레코드가 남아있음 (SecurityTrails, ViewDNS 등에서 조회 가능)
- 서브도메인(`mail.example.com`, `dev.example.com`)이 CDN 없이 직접 연결
- 메일 서버 MX 레코드가 같은 서버를 가리킴
- SSL 인증서의 Common Name으로 IP 역추적

### 점검 팁

```bash
# 현재 DNS 레코드 확인 (히스토리는 SecurityTrails, ViewDNS 등 웹 서비스에서 조회)
dig +short example.com
dig +short mail.example.com

# 서브도메인 열거 (노출된 Origin 찾기)
nslookup -type=MX example.com

# SSL 인증서로 IP 역추적 확인
echo | openssl s_client -connect <ORIGIN_IP>:443 2>/dev/null | openssl x509 -noout -subject
```

### 예방 조치

- CDN 적용 전 사용하던 IP는 변경
- 모든 서브도메인도 CDN/프록시 뒤에 배치
- 메일 서버는 별도 IP로 분리

---

## 4. CDN 캐시 디버깅

CDN이 제대로 캐싱하고 있는지 응답 헤더로 확인할 수 있다.

### 주요 응답 헤더

| 헤더 | 설명 | 예시 값 |
|------|------|---------|
| `X-Cache` | 캐시 HIT/MISS 여부 | `Hit from cloudfront` |
| `Age` | 캐시된 후 경과 시간(초) | `3600` |
| `Cache-Control` | 캐시 정책 | `max-age=86400, public` |
| `X-Cache-Hits` | 캐시 적중 횟수 (일부 CDN) | `5` |
| `CF-Cache-Status` | Cloudflare 캐시 상태 | `HIT`, `MISS`, `DYNAMIC` |

### 확인 방법

```bash
# 응답 헤더 확인
curl -I https://example.com/image.png

# 주요 캐시 헤더만 필터링
curl -sI https://example.com/image.png | grep -iE 'x-cache|age|cache-control|cf-cache'
```

### 캐시가 안 되는 흔한 원인

- `Cache-Control: no-store` 설정 (캐시 자체를 하지 않음)
- `Cache-Control: no-cache` 설정 (캐시는 하지만 매번 Origin에 재검증 → 캐시 HIT가 아닌 것처럼 보일 수 있음)
- `Cache-Control: private` 설정 (CDN 캐시 불가, 브라우저만 캐시)
- `Set-Cookie` 헤더가 응답에 포함
- Query String이 매번 다름
- POST 등 캐시 불가 메서드 사용

---

## 5. CDN 우회 문제 사례

### 사례 1: MX 레코드로 Origin 노출

```
example.com      → CloudFront (CDN 적용)
mail.example.com → 203.0.113.10 (같은 서버, CDN 미적용)
MX record        → mail.example.com
```

공격자가 MX 레코드를 조회하면 Origin IP `203.0.113.10`을 알 수 있다.

### 사례 2: 개발 서브도메인 노출

```
www.example.com → CDN 적용
dev.example.com → Origin IP 직접 노출
```

### 사례 3: 서버에서 외부로 나가는 요청

```
사용자 → CDN → Origin 서버 → 외부 Webhook 호출
                              (Origin IP가 요청 소스로 노출)
```

### 대응 방법

- 외부 요청은 NAT Gateway 등 별도 IP로 나가도록 구성
- 모든 서브도메인 DNS 레코드 점검
- 메일 서버는 물리적으로 분리된 서버 사용

---

## 6. Proxy Protocol / X-Forwarded-For

CDN이나 Proxy 뒤에서는 서버가 보는 IP가 클라이언트가 아닌 CDN/Proxy의 IP가 된다.

### 문제 상황

```
실제 클라이언트: 1.2.3.4
        |
        v
CDN/Proxy IP: 10.0.0.1  ← 서버는 이 IP만 보임
        |
        v
Origin 서버: "접속 IP = 10.0.0.1" (잘못된 정보)
```

### 해결 방법 1: X-Forwarded-For 헤더

```
X-Forwarded-For: 1.2.3.4, 10.0.0.1
                 ↑ 실제 클라이언트   ↑ Proxy
```

```nginx
# Nginx에서 실제 클라이언트 IP 사용
set_real_ip_from 10.0.0.0/8;      # CDN/Proxy 대역
real_ip_header X-Forwarded-For;
real_ip_recursive on;
```

### 해결 방법 2: Proxy Protocol (L4)

- TCP 레벨에서 클라이언트 IP를 전달
- NLB + Proxy Protocol v2 조합에서 주로 사용

### 주의사항

- `X-Forwarded-For`는 클라이언트가 위조 가능 → 신뢰할 수 있는 Proxy 대역만 `set_real_ip_from`에 등록
- 여러 Proxy를 거치면 헤더에 IP가 누적됨 → 가장 왼쪽이 원래 클라이언트

---

## 7. 캐시 무효화 (Invalidation)

CDN에 캐싱된 콘텐츠를 강제로 갱신하는 방법이다.

### AWS CloudFront 예시

```bash
# 특정 경로 무효화
aws cloudfront create-invalidation \
  --distribution-id E1234567890 \
  --paths "/index.html" "/css/*"

# 전체 무효화
aws cloudfront create-invalidation \
  --distribution-id E1234567890 \
  --paths "/*"
```

### 무효화 vs 버저닝

| 방식 | 장점 | 단점 |
|------|------|------|
| Invalidation | 즉시 적용 가능 | 비용 발생, 전파 시간 필요 |
| 파일 버저닝 (`app.v2.js`) | 즉시 반영, 비용 없음 | URL 변경 필요 |
| Query String (`app.js?v=2`) | URL 구조 유지 | CDN 설정에 따라 캐시 키 다를 수 있음 |

### 팁

- CloudFront는 월 1,000개 경로(path) 무효화 무료, 이후 경로당 과금
- 가능하면 파일 버저닝을 우선 사용하고, 긴급 시에만 Invalidation 사용
- `/*` 전체 무효화도 1개 경로로 카운트

---

## 8. TTL 설정 가이드

콘텐츠 유형별 권장 캐시 TTL(Time To Live) 설정이다.

### 권장 TTL

| 콘텐츠 유형 | 권장 TTL | Cache-Control 예시 |
|-------------|----------|-------------------|
| 정적 자산 (JS, CSS, 이미지) | 1년 (버저닝 사용 시) | `max-age=31536000, immutable` |
| HTML 페이지 | 짧게 또는 no-cache | `max-age=0, must-revalidate` |
| API 응답 | 캐시 안 함 | `no-store` |
| 폰트 파일 | 1년 | `max-age=31536000` |
| 동영상/대용량 파일 | 1주~1개월 | `max-age=604800` |

### Cache-Control 주요 디렉티브

```
public          → CDN 캐시 허용
private         → 브라우저만 캐시 (CDN 캐시 안 함)
no-cache        → 매번 Origin에 유효성 확인 후 사용
no-store        → 캐시 자체를 하지 않음
max-age=N       → N초 동안 캐시 유효
s-maxage=N      → CDN(공유 캐시)에만 적용되는 TTL
immutable       → 콘텐츠가 변경되지 않음을 명시
must-revalidate → 만료 후 반드시 Origin에 확인
```

### 설정 예시 (Nginx)

```nginx
# 정적 자산 - 장기 캐시
location ~* \.(js|css|png|jpg|gif|ico|woff2)$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
}

# HTML - 항상 최신 확인
location ~* \.html$ {
    add_header Cache-Control "no-cache, must-revalidate";
}

# API - 캐시 안 함
location /api/ {
    add_header Cache-Control "no-store";
}
```

---

## 9. CDN 장애 대응 (Failover)

CDN 자체 또는 Origin 서버 장애 시 서비스 연속성을 확보하는 방법이다.

### CloudFront Origin Failover 구성

```
+------------------+
|   CloudFront     |
+------------------+
        |
        v
+------------------+     장애 시     +------------------+
| Primary Origin   |  ------------> | Secondary Origin  |
| (ALB-A)          |   자동 전환     | (ALB-B / S3)     |
+------------------+                +------------------+
```

- Origin Group을 생성하여 Primary/Secondary Origin 지정
- 5xx 에러 또는 타임아웃 시 자동으로 Secondary로 전환

### 설정 포인트

| 항목 | 권장 값 |
|------|---------|
| Origin 응답 타임아웃 | 10~30초 |
| Origin 연결 시도 횟수 | 3회 (같은 Origin에 대한 연결 재시도) |
| Failover 조건 | 500, 502, 503, 504 |

- Primary Origin에서 Failover 조건에 해당하는 상태 코드를 받으면 Secondary Origin으로 1회 전환
- 재시도가 아닌 전환(Failover) 구조

### 정적 페이지 Failover

```
Primary Origin 장애
        |
        v
S3 정적 에러 페이지 반환 (maintenance.html)
```

- S3에 정적 에러 페이지를 미리 배포
- CloudFront Custom Error Response로 특정 에러 코드에 대해 S3 페이지 반환 가능

---

## 10. CORS와 CDN

CDN을 경유하면 CORS 관련 문제가 자주 발생한다.

### 문제 상황

```
1. 브라우저가 Origin 헤더 없이 요청 → CDN이 CORS 헤더 없는 응답을 캐싱
2. 다른 도메인에서 Origin 헤더 포함 요청 → CDN이 캐싱된 (CORS 없는) 응답 반환
3. 브라우저가 CORS 에러 발생
```

### 해결 방법

#### 1. Origin 헤더를 캐시 키에 포함

CloudFront에서 `Origin` 헤더를 Origin으로 전달하고 캐시 키에 포함시킨다.

```
Cache Policy:
  - Header: Origin (캐시 키에 포함)
  
Origin Request Policy:
  - Header: Origin (Origin 서버로 전달)
```

#### 2. Origin 서버에서 CORS 헤더 설정

```nginx
# Nginx
location /api/ {
    add_header Access-Control-Allow-Origin $http_origin;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
    add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    add_header Vary Origin;  # 중요: CDN이 Origin별로 캐시하도록
}
```

### 핵심 팁

- `Vary: Origin` 헤더를 반드시 포함 → CDN이 Origin 헤더 값별로 별도 캐싱
- `Access-Control-Allow-Origin: *`은 간단하지만 인증 요청에는 사용 불가

---

## 11. CDN 비용 최적화

CDN 비용의 대부분은 데이터 전송(Bandwidth)에서 발생한다.

### 비용 절감 방법

#### 1. 압축 활성화

```
압축 전: 1MB JavaScript
압축 후: 200KB (gzip/brotli)
→ 전송 비용 80% 절감
```

CloudFront에서 자동 압축 활성화:
- `Compress Objects Automatically: Yes`
- 파일 크기가 1,000바이트 이상 10MB 이하
- Origin 응답이 이미 압축되지 않은 상태 (`Content-Encoding` 헤더 없음)

#### 2. Origin Shield

```
                    일반 구성                          Origin Shield 사용
엣지(서울)  → Origin                    엣지(서울)  → Origin Shield → Origin
엣지(도쿄)  → Origin                    엣지(도쿄)  → Origin Shield → Origin
엣지(싱가폴) → Origin                   엣지(싱가폴) → Origin Shield → Origin
(Origin 요청 3회)                       (Origin 요청 1회, Shield가 캐싱)
```

- Origin 부하 감소 + 캐시 적중률 향상
- Origin에 가장 가까운 리전을 Shield로 지정

#### 3. 가격 클래스 설정 (CloudFront)

| 가격 클래스 | 포함 리전 | 비용 |
|-------------|----------|------|
| Price Class All | 전체 | 최고 |
| Price Class 200 | 대부분 (남미 포함, 호주·아시아 일부 고비용 리전 제외) | 중간 |
| Price Class 100 | 북미, 유럽만 | 최저 |

- 사용자가 특정 지역에 집중되어 있다면 가격 클래스를 제한하여 비용 절감

#### 4. 캐시 적중률 높이기

- Query String 정규화 (불필요한 파라미터 제거)
- Cookie 전달 최소화
- TTL을 가능한 길게 설정

---

## 12. SSL/TLS 인증서 구성

CDN 사용 시 인증서가 두 구간에 필요하다.

### 두 구간의 인증서

```
사용자 ←── HTTPS ──→ CDN(Edge) ←── HTTPS ──→ Origin
       [인증서 A]                [인증서 B]
```

| 구간 | 인증서 | 설명 |
|------|--------|------|
| 사용자 ↔ CDN | Edge 인증서 | 사용자가 보는 도메인 인증서 (ACM 등) |
| CDN ↔ Origin | Origin 인증서 | Origin 서버에 설치된 인증서 |

### CloudFront 인증서 설정

```
Edge 인증서:
  - ACM (us-east-1 리전에서 발급 필수)
  - 도메인: example.com, *.example.com

Origin 인증서:
  - ACM, Let's Encrypt, 또는 자체 인증서
  - CloudFront Origin SSL Protocol: TLSv1.2 권장
```

### Origin Protocol Policy

| 설정 | 동작 |
|------|------|
| HTTPS Only | CDN → Origin 항상 HTTPS (권장) |
| Match Viewer | 사용자 요청과 동일 프로토콜 사용 |
| HTTP Only | CDN → Origin HTTP (내부망에서만) |

### 주의사항

- CloudFront용 ACM 인증서는 반드시 `us-east-1`에서 발급
- Origin 인증서가 만료되면 CDN → Origin 통신이 끊김 → 모니터링 필수
- Self-signed 인증서 사용 시 CloudFront에서 검증 비활성화 가능하나 비권장

---

## 13. CDN 로그 분석

CDN 접속 로그를 통해 캐시 효율, 트래픽 패턴, 이상 접근을 파악할 수 있다.

### CloudFront 로그 활성화

```
로그 저장 위치: S3 버킷
로그 형식: 탭 구분 텍스트 (TSV)
주요 필드: 날짜, 시간, 엣지 위치, 클라이언트 IP, URI, 상태 코드, 캐시 결과
```

### 주요 분석 항목

#### 1. 캐시 적중률

```bash
# S3에서 로그 다운로드 후 분석
# 캐시 HIT/MISS 비율 확인 (x-edge-result-type: 14번째 필드)
# 주석 행(#으로 시작) 제외
awk '!/^#/ {print $14}' cloudfront-log.tsv | sort | uniq -c | sort -rn

# 결과 예시:
# 85000 Hit
# 10000 Miss
# 5000  RefreshHit
# → 캐시 적중률: 약 85%
```

#### 2. 상태 코드 분포

```bash
# 4xx, 5xx 에러 비율 확인 (sc-status: 9번째 필드)
awk '!/^#/ {print $9}' cloudfront-log.tsv | sort | uniq -c | sort -rn
```

#### 3. 대량 요청 IP 탐지 (DDoS/봇 의심)

```bash
# 요청 수 기준 상위 IP (주석 행 제외)
awk '!/^#/ {print $5}' cloudfront-log.tsv | sort | uniq -c | sort -rn | head -20
```

### Athena를 활용한 분석

대량 로그는 S3 + Athena 조합으로 SQL 쿼리가 효율적이다.

```sql
-- 캐시 적중률 일별 추이
SELECT date,
       COUNT(CASE WHEN result_type = 'Hit' THEN 1 END) * 100.0 / COUNT(*) AS hit_rate
FROM cloudfront_logs
GROUP BY date
ORDER BY date;

-- 5xx 에러가 많은 URI
SELECT uri, COUNT(*) AS error_count
FROM cloudfront_logs
WHERE status >= 500
GROUP BY uri
ORDER BY error_count DESC
LIMIT 20;
```

---

## 14. Multi-CDN 전략

단일 CDN에 의존하면 해당 CDN 장애 시 전체 서비스가 영향을 받는다.

### 구성 방식

```
                    +------------------+
                    |   DNS (Route53)  |
                    | 가중치/지연시간   |
                    | 기반 라우팅       |
                    +------------------+
                     /        |        \
                    v         v         v
            +---------+ +---------+ +---------+
            |CloudFront| |Cloudflare| | Akamai  |
            +---------+ +---------+ +---------+
                    \         |        /
                     v        v       v
                    +------------------+
                    |  Origin Server   |
                    +------------------+
```

### 라우팅 전략

| 방식 | 설명 | 사용 사례 |
|------|------|----------|
| Active-Passive | 평소 1개 CDN, 장애 시 전환 | 비용 절감 우선 |
| Active-Active (가중치) | 트래픽을 비율로 분산 | 고가용성 |
| 지연시간 기반 | 사용자에게 가장 빠른 CDN으로 | 글로벌 서비스 |

### 고려사항

- 각 CDN마다 캐시 설정, SSL 인증서를 별도 관리해야 함
- 캐시 무효화를 모든 CDN에 동시 수행 필요
- 모니터링/로그 형식이 CDN마다 다름 → 통합 대시보드 필요
- 비용이 증가하므로 서비스 규모와 가용성 요구사항에 따라 판단
