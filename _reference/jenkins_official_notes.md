---
name: jenkins-official-notes
description: Jenkins LTS 판·Java 지원 정책·Docker 이미지·JCasC·백업 공식 자료와 2.580.3 컨테이너 시험 결과(플러그인 설치, JCasC, REST 빌드, master.key 복원) 정리.
tags:
  - jenkins
  - ci
  - jcasc
  - backup
  - docker
last_checked: 2026-11-26
sources:
  - https://www.jenkins.io/changelog-stable/
  - https://www.jenkins.io/doc/book/platform-information/support-policy-java/
  - https://www.jenkins.io/doc/book/installing/docker/
  - https://github.com/jenkinsci/docker/blob/master/README.md
  - https://www.jenkins.io/doc/book/system-administration/backing-up/
  - https://www.jenkins.io/doc/book/managing/casc/
  - https://github.com/jenkinsci/configuration-as-code-plugin/blob/master/README.md
  - https://pkg.jenkins.io/debian-stable/
---

# Jenkins 공식 자료 참조 노트

## 1. 판 (2026-11-26)

| 항목          | 내용                                                                                     | 근거                         |
|---------------|------------------------------------------------------------------------------------------|------------------------------|
| 최신 LTS      | 2.580.3 (2026-11-25), 2.580.2 (10-28), 2.580.1 (09-30), 2.568.3 (09-02), 2.568.2 (08-05) | changelog-stable             |
| Java 요구     | 2.555.1(2026-04-15)부터 Java 21 이상, Java 17 미지원                                     | changelog-stable             |
| Java 지원 표  | 25: 2.541.1부터, 2029-09까지 예정. 21: 2.479.1부터, 2027-09까지 예정. 17: 마지막 2.541.3 | support-policy-java          |
| apt 키        | `jenkins.io-2026.key`, 지문 `5E386EADB55F01504CAE8BCF7198F4B714ABFC68`, 만료 2028-12-21  | pkg.jenkins.io/debian-stable |
| Docker 이미지 | `jenkins/jenkins`. `latest`는 주간판, `lts-jdk21`은 LTS. Docker CLI 없음                 | installing/docker            |
| 포트          | 8080 웹, 50000 인바운드 에이전트(WebSocket 에이전트는 불필요)                            | installing/docker            |

- debian-stable 페이지의 문장 하나가 "Weekly Release Line"이라고 적혀 있지만 경로는 stable입니다(페이지 표기 오류로 보임).

## 2. Docker·JCasC·백업 (공식 문서)

- 플러그인 미리 설치: Dockerfile에서 `jenkins-plugin-cli --plugins ...` 또는 `/usr/share/jenkins/ref/plugins.txt`를 복사한 뒤 `jenkins-plugin-cli -f`.
- JVM 옵션: README는 컨트롤러 전용 옵션을 `JENKINS_JAVA_OPTS`로 주라고 하고, `JAVA_OPTS`도 받습니다. 실행 인수는 `JENKINS_OPTS`.
- 설정 마법사 끄기 속성 `jenkins.install.runSetupWizard=false`는 이번에 읽은 공식 페이지에서 찾지 못했고 시험으로 동작을 확인했습니다.
- JCasC: `CASC_JENKINS_CONFIG`(쉼표로 여러 개, 폴더·파일·URL), 기본 `$JENKINS_HOME/jenkins.yaml`. 문서의 최소 예는 `jenkins: systemMessage:`.
- Docker 안에서 Docker를 쓰는 공식 예는 `docker:dind` 사이드카(privileged, TLS)입니다. docker.sock 공유는 설치 문서에 없습니다.
- 백업: `$JENKINS_HOME` 전체가 가장 간단. `war`·`cache`·`tools`·풀린 `plugins/<이름>/`·`workspace`는 보통 제외. 원문 "Never include the controller key in your Jenkins backup!" — `master.key`는 따로 안전한 곳에 보관.

## 3. 컨테이너 시험 (2026-11-26)

구성: `jenkins/jenkins:2.580.3-jdk21` 기반 이미지(플러그인 4개 지정, JCasC, 마법사 끔), 메모리 제한 2GB, 힙 1GB, 같은 네트워크의 curl 컨테이너로 REST 호출. 비밀번호는 env 파일로만 전달.

| 확인                    | 결과                                                                                                                                                                                                                    |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기동                    | `Starting version 2.580.3` 후 수 초 만에 "fully up and running", Java 21.0.13.1                                                                                                                                         |
| 플러그인                | workflow-aggregator·configuration-as-code·job-dsl·git 지정 → 63개 설치                                                                                                                                                  |
| 플러그인 판             | configuration-as-code 2150.v9cb_6a_756737e, git 5.11.0, job-dsl 3752.vb_199526b_20c3, workflow-aggregator 608.v67378e9d3db_1, workflow-cps 4403.4405.va_b_cdb_b_d0b_89f, pipeline-model-definition 2.2293.v6e7193cec599 |
| 마법사                  | `initialAdminPassword` 없음                                                                                                                                                                                             |
| 인증                    | 익명 403, 관리자 200, 틀린 비밀번호 401, 응답 헤더 `X-Jenkins: 2.580.3`                                                                                                                                                 |
| crumb                   | 필드 `Jenkins-Crumb`. 비밀번호 인증 POST는 crumb 없으면 403, 있으면 201                                                                                                                                                 |
| API 토큰                | crumb 없이 POST 201                                                                                                                                                                                                     |
| 매개변수                | 첫 실행 전 `buildWithParameters` 400, `/build` 201 뒤 등록, 이후 201                                                                                                                                                    |
| Pipeline                | parallel 단계·`archiveArtifacts` 포함 3회 SUCCESS(약 1.9~3.7초)                                                                                                                                                         |
| JCasC `${}`             | Pipeline 스크립트 안 `${BUILD_NUMBER}` 등이 빈 값으로 치환. `^${...}`로 이스케이프하면 유지                                                                                                                             |
| JCasC reload            | `POST /configuration-as-code/reload` 302, 작업 재생성으로 매개변수 등록 초기화                                                                                                                                          |
| JCasC export            | `POST /configuration-as-code/export`로 YAML 출력                                                                                                                                                                        |
| `JENKINS_HOME`          | 약 211MB, `war`·`workspace`·`caches`·`master.key` 제외 tar.gz 약 111MB                                                                                                                                                  |
| 복원(`master.key` 없음) | 기동·빌드 기록 4개 복원, `identity.key.enc is corrupted` SEVERE·`BadPaddingException`                                                                                                                                   |
| 복원(`master.key` 포함) | 오류 없이 기동, 빌드 기록 4개                                                                                                                                                                                           |

- 패키지 설치(apt·dnf), 에이전트 연결, 업그레이드, DinD는 시험하지 않았습니다.
