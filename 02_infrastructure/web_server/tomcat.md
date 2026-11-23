# Tomcat
<!-- reference: _reference/tomcat_official_notes.md -->

Java 웹 애플리케이션(WAR)을 실행하는 서블릿 컨테이너입니다. 앞단에는 보통 Nginx·Apache·HAProxy 같은 웹 서버나 로드 밸런서를 두고 Tomcat은 애플리케이션을 실행합니다. 이 문서만으로 판 고르기 → 설치·실행 → 앱 배포 → 운영 설정 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Tomcat 11.0.29, 10.1.62, 9.0.124 (2026-11-23 확인)
- 예제 시험: 2026-11-23, `tomcat:11-jre21` 컨테이너(Server 11.0.29, JVM 21.0.13)에서 3·4절과 6절 1~3번을 실행해 확인

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 개요와 판 고르기](#1-개요와-판-고르기) / [2. 설치](#2-설치) / [3. 실행과 구조](#3-실행과-구조) |
| [4. 앱 배포](#4-앱-배포) / [5. 운영 설정](#5-운영-설정) / [6. 검증](#6-검증)                       |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                 |

---

## 1. 개요와 판 고르기

| 계열 | 최신 판 | 고르는 기준                      |
|------|---------|----------------------------------|
| 11.0 | 11.0.29 | 새 프로젝트 (Jakarta EE 11 계열) |
| 10.1 | 10.1.62 | Jakarta EE 10 기준으로 만든 앱   |
| 9.0  | 9.0.124 | `javax.*` 패키지를 쓰는 옛 앱    |

Tomcat 10부터 패키지 이름이 `javax.*`에서 `jakarta.*`로 바뀌었습니다. `javax.*`로 만든 앱을 10 이상에 올리면 실행되지 않으므로, 앱이 어느 쪽인지 먼저 확인합니다. 계열별로 필요한 Java 판은 공식 Which Version 표를 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
# 컨테이너 (가장 간단)
docker run -d --name tomcat -p 8080:8080 tomcat:11-jre21

# 직접 설치 (Java 설치 후 공식 배포 파일)
sudo apt-get install -y openjdk-21-jre-headless
VER=11.0.29
curl -fsSLO "https://dlcdn.apache.org/tomcat/tomcat-11/v${VER}/bin/apache-tomcat-${VER}.tar.gz"
curl -fsSLO "https://dlcdn.apache.org/tomcat/tomcat-11/v${VER}/bin/apache-tomcat-${VER}.tar.gz.sha512"
sha512sum -c "apache-tomcat-${VER}.tar.gz.sha512"
sudo useradd -r -m -d /opt/tomcat -s /usr/sbin/nologin tomcat
sudo tar -xzf "apache-tomcat-${VER}.tar.gz" -C /opt/tomcat --strip-components=1
sudo chown -R tomcat: /opt/tomcat
```

root로 실행하지 않고 전용 계정을 씁니다. 직접 설치하면 systemd 서비스 파일을 만들어 `bin/startup.sh`·`shutdown.sh` 대신 서비스로 관리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 실행과 구조

| 디렉터리  | 내용                                          |
|-----------|-----------------------------------------------|
| `bin`     | `startup.sh`, `shutdown.sh`, `version.sh`     |
| `conf`    | `server.xml`(포트·커넥터), `tomcat-users.xml` |
| `webapps` | 배포할 앱(WAR·디렉터리)                       |
| `logs`    | `catalina.out`, 접근 로그                     |

```bash
/opt/tomcat/bin/version.sh            # Server number: 11.0.x, JVM Version
curl -sI http://127.0.0.1:8080/        # 응답 확인
```

공식 컨테이너 이미지는 `webapps`가 비어 있어 루트(`/`) 요청이 404입니다. 예제·관리 앱은 `webapps.dist`에 있고, 운영에서는 옮기지 않는 편이 안전합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 앱 배포

```bash
cp myapp.war /opt/tomcat/webapps/      # 자동으로 풀려 /myapp 경로로 배포
cp myapp.war /opt/tomcat/webapps/ROOT.war   # 루트(/)로 배포하려면 ROOT
tail -f /opt/tomcat/logs/catalina.out  # 배포 로그
```

컨테이너는 이미지 안에 WAR를 넣어 새 이미지를 만듭니다.

```dockerfile
FROM tomcat:11-jre21
COPY myapp.war /usr/local/tomcat/webapps/ROOT.war
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 운영 설정

| 항목        | 설정                                                                   |
|-------------|------------------------------------------------------------------------|
| 메모리      | `bin/setenv.sh`에 `JAVA_OPTS="-Xms512m -Xmx1g"` 등                     |
| 관리 앱     | 운영에서는 `manager`·`host-manager`를 배포하지 않거나 접근 주소를 제한 |
| 앞단 프록시 | Nginx·HAProxy가 TLS를 처리하고 Tomcat 8080으로 전달                    |
| 종료 포트   | `server.xml`의 shutdown 포트(기본 8005)는 외부에 열지 않음             |
| 로그        | `catalina.out`이 계속 커지므로 logrotate 등으로 관리                   |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용      | 명령                                                              | 기대 결과                   |
|------|----------------|-------------------------------------------------------------------|-----------------------------|
| 1    | 판과 Java      | `bin/version.sh`                                                  | Server 11.0.x, JVM 판       |
| 2    | 포트 응답      | `curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/` | 앱이 있으면 200, 없으면 404 |
| 3    | 배포 구성      | `ls webapps`                                                      | 의도한 앱만                 |
| 4    | 앱 응답        | `curl http://127.0.0.1:8080/myapp/`                               | 앱 응답                     |
| 5    | 오류 로그      | `grep -i -E 'SEVERE\|Exception' logs/catalina.out`                | 출력 없음                   |
| 6    | 외부 노출 포트 | `ss -tlnp \| grep java`                                           | 8005가 127.0.0.1에만        |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                          | 원인                                | 해결 방법                               |
|-----------------------------------------------|-------------------------------------|-----------------------------------------|
| 앱 배포 뒤 `ClassNotFoundException: javax...` | Tomcat 10+에 `javax.*` 앱           | Tomcat 9 사용 또는 앱을 Jakarta로 이전  |
| 루트(`/`) 404                                 | `webapps`가 비어 있음 (공식 이미지) | 앱을 `ROOT.war`로 배포                  |
| `OutOfMemoryError`                            | 힙 부족                             | `setenv.sh`의 `-Xmx` 조정, 힙 덤프 분석 |
| 포트 8080 충돌                                | 다른 프로세스가 사용                | `server.xml`의 Connector 포트 변경      |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Nginx 설치](./nginx_install.md) · [Apache 설치](./apache_install.md) — 앞단 웹 서버와 리버스 프록시
- [HAProxy 개념](./haproxy_concepts.md) — 여러 Tomcat 앞의 부하 분산
- [journald와 logrotate](../../01_fundamentals/linux/journald_logrotate_guide.md) — `catalina.out` 관리

---

## 참고 자료

- Apache Tomcat: [Which Version Do I Want?](https://tomcat.apache.org/whichversion.html) — ★★★☆☆
- Apache Tomcat: [RUNNING.txt (11.0)](https://tomcat.apache.org/tomcat-11.0-doc/RUNNING.txt) — ★★★☆☆
- Docker Hub: [tomcat official image](https://hub.docker.com/_/tomcat) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
