---
name: tomcat-official-notes
description: Apache Tomcat의 지원 계열·판, Java 요구 판, 디렉터리 구조, 공식 컨테이너 이미지의 공식 출처 기준 사실 정리.
tags:
  - tomcat
  - java
  - web-server
last_checked: 2026-11-23
sources:
  - https://tomcat.apache.org/whichversion.html
  - https://tomcat.apache.org/
  - https://tomcat.apache.org/tomcat-11.0-doc/RUNNING.txt
  - https://hub.docker.com/_/tomcat
---

# Tomcat 공식 참조 노트

## 1. 공식 소스

| 소스               | URL                                                   | 용도                        |
|--------------------|-------------------------------------------------------|-----------------------------|
| Which version      | https://tomcat.apache.org/whichversion.html           | 계열별 사양·최신 판·Java 판 |
| Tomcat 홈          | https://tomcat.apache.org/                            | 출시 공지                   |
| RUNNING.txt (11.0) | https://tomcat.apache.org/tomcat-11.0-doc/RUNNING.txt | 설치·실행, CATALINA_HOME    |
| Docker 공식 이미지 | https://hub.docker.com/_/tomcat                       | 컨테이너 이미지             |

## 2. 검증된 사실 (2026-11-23)

| 항목              | 값                                                                    | 출처                        |
|-------------------|-----------------------------------------------------------------------|-----------------------------|
| 지원 계열 최신 판 | 11.0.29, 10.1.62, 9.0.124                                             | whichversion, 홈            |
| 디렉터리          | `bin`(시작·종료), `conf`(`server.xml` 등), `webapps`(앱 배포), `logs` | RUNNING.txt                 |
| 기본 포트         | HTTP 커넥터 8080                                                      | 기본 `server.xml`, 컨테이너 |
| 공식 이미지       | `tomcat:11-jre21` 등. `webapps`는 비어 있고 기본 앱은 `webapps.dist`  | Docker Hub, 컨테이너        |
| 판 확인           | `bin/version.sh`                                                      | 컨테이너 실행               |

## 3. 검증 기록

- 1차: tomcat.apache.org(whichversion, 출시 공지, RUNNING.txt)와 Docker Hub에서 확인했습니다.
- 2차: `tomcat:11-jre21` 컨테이너를 띄워 `version.sh`(Server 11.0.29, JVM 21.0.13), 8080 응답, `webapps.dist` 구성을 대조했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.
