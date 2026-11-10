# Trivy 가이드
<!-- reference: _reference/trivy_official_notes.md -->

## 목차

| 섹션                                                                           |
|--------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치와 무결성 검증](#2-설치와-무결성-검증)            |
| [3. 기본 사용법](#3-기본-사용법) / [4. 설정 파일과 예외](#4-설정-파일과-예외)  |
| [5. 인프라 대상별 적용](#5-인프라-대상별-적용) / [6. CI/CD 연동](#6-cicd-연동) |
| [7. 운영](#7-운영) / [8. 탐지 후 대응](#8-탐지-후-대응)                        |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

Trivy는 컨테이너 이미지, 파일시스템, IaC 설정, Kubernetes 클러스터에서 취약점(CVE)·설정 오류·시크릿·라이선스를 찾는 오픈소스 보안 스캐너입니다. 운영 인프라에서는 이미지 배포 전 검사, IaC 변경 검토, 호스트 패키지 점검, 클러스터 정기 점검에 사용합니다.

| 항목      | 내용                                       |
|-----------|--------------------------------------------|
| 언어      | Go                                         |
| 라이선스  | Apache-2.0                                 |
| 최신 버전 | v0.76.2 (2026-11-05 배포, 2026-11-10 확인) |
| GitHub    | https://github.com/aquasecurity/trivy      |
| 공식 문서 | https://trivy.dev/                         |

### 스캐너와 대상

| 스캐너    | `--scanners` 값 | 찾는 것                                      |
|-----------|-----------------|----------------------------------------------|
| 취약점    | `vuln`          | OS 패키지·언어 라이브러리의 알려진 CVE       |
| 설정 오류 | `misconfig`     | Dockerfile·Terraform·Kubernetes 등 위험 설정 |
| 시크릿    | `secret`        | 키·토큰·패스워드                             |
| 라이선스  | `license`       | 사용 제한이 있는 라이선스                    |

| 대상 명령      | 대상                             | 기본 스캐너               |
|----------------|----------------------------------|---------------------------|
| `trivy image`  | 컨테이너 이미지(레지스트리·로컬) | `vuln`, `secret`          |
| `trivy fs`     | 소스 디렉토리(lock 파일 기준)    | `vuln`, `secret`          |
| `trivy config` | IaC·설정 파일                    | `misconfig`(항상 사용)    |
| `trivy rootfs` | 호스트나 풀린 루트 파일시스템    | `vuln`, `secret`          |
| `trivy k8s`    | Kubernetes 클러스터              | 리소스 설정·이미지 취약점 |
| `trivy sbom`   | 기존 SBOM 파일(CycloneDX·SPDX)   | `vuln`                    |

🟡 이 문서의 명령과 설정은 공식 문서 v0.76.1 태그 원문을 기준으로 정리했으며 작성 시 실제로 실행하지 않았습니다. 확인 범위는 [Trivy 참조 노트](../../_reference/trivy_official_notes.md)에 기록했습니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치와 무결성 검증

### 공급망 사고와 버전 기준

2026-03-19에 공격자가 탈취한 자격증명으로 악성 Trivy v0.69.4를 배포하고, `aquasecurity/trivy-action` 태그 77개 중 76개와 `aquasecurity/setup-trivy` 태그 7개를 자격증명 탈취 코드로 바꿨습니다. 2026-03-22에는 Docker Hub에 악성 v0.69.5·v0.69.6 이미지가 올라왔습니다(공식 공지 GHSA-69fq-xp46-6x23).

| 구성 요소                  | 노출 시간(UTC)                       | 영향받은 사용                                   |
|----------------------------|--------------------------------------|-------------------------------------------------|
| trivy v0.69.4              | 2026-03-19 18:22 ~ 약 21:42          | 바이너리·이미지 v0.69.4 또는 그 시간의 `latest` |
| trivy-action               | 2026-03-19 약 17:43 ~ 03-20 약 05:40 | 0.35.0을 제외한 태그 참조                       |
| setup-trivy                | 2026-03-19 약 17:43 ~ 약 21:44       | SHA로 고정하지 않은 참조                        |
| Docker Hub v0.69.5·v0.69.6 | 2026-03-22 15:43 ~ 03-23 약 01:40    | 해당 태그 또는 그 시간의 `latest`               |

이 사고와 이후 보안 공지에서 다음 기준을 정합니다.

- `latest` 태그나 버전 없는 설치 스크립트를 쓰지 않고 버전을 고정합니다.
- 바이너리는 서명이나 체크섬을 확인한 뒤 설치하고, 이미지는 digest로 참조합니다.
- GitHub Action은 태그가 아니라 전체 commit SHA로 고정합니다.
- 운영 기준 버전은 v0.72.0 이상으로 둡니다. v0.71.0(Helm chart 압축 폭탄으로 메모리 고갈), v0.71.1(DB 내려받기 경로 조작), v0.72.0(플러그인 경로 조작)에서 보안 수정이 있었습니다.

### 바이너리 설치 (권장)

v0.68.1부터 모든 릴리스 파일에 sigstore 서명 묶음(`.sigstore.json`)이 함께 올라옵니다. [cosign](https://github.com/sigstore/cosign) v3.0.0 이상으로 서명을 확인합니다. cosign v2(2.4.0 이상)는 `--new-bundle-format` 옵션을 추가합니다.

```bash
VERSION="v0.76.2"
BASE="https://github.com/aquasecurity/trivy/releases/download/${VERSION}"
ASSET="trivy_${VERSION#v}_Linux-64bit.tar.gz"
WORK=$(mktemp -d)
curl -fsSL -o "${WORK}/${ASSET}" "${BASE}/${ASSET}"
curl -fsSL -o "${WORK}/${ASSET}.sigstore.json" "${BASE}/${ASSET}.sigstore.json"

# 서명 확인 (Verified OK가 나와야 다음 단계 진행)
cosign verify-blob "${WORK}/${ASSET}" \
  --bundle "${WORK}/${ASSET}.sigstore.json" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  --certificate-identity "https://github.com/aquasecurity/trivy/.github/workflows/reusable-release.yaml@refs/tags/${VERSION}"

# 설치
sudo tar -xzf "${WORK}/${ASSET}" -C /usr/local/bin trivy
rm -rf "${WORK}"
trivy --version
```

cosign을 쓸 수 없는 환경에서는 최소한 체크섬을 확인합니다. 체크섬 파일은 릴리스와 같은 곳에서 받으므로 서명 확인보다 보장이 약합니다.

```bash
curl -fsSL -o "${WORK}/checksums.txt" "${BASE}/trivy_${VERSION#v}_checksums.txt"
(cd "${WORK}" && grep " ${ASSET}\$" checksums.txt | sha256sum -c -)
```

### 패키지 저장소

| 배포판        | 방법                                                                  |
|---------------|-----------------------------------------------------------------------|
| Debian/Ubuntu | 공식 apt 저장소(`signed-by` 키링, suite `generic`) 또는 릴리스 `.deb` |
| RHEL 계열     | 공식 yum 저장소(`gpgcheck=1`) 또는 릴리스 `.rpm`                      |
| macOS·Linux   | `brew install trivy` (공식 formula는 소스에서 빌드)                   |
| Windows       | 릴리스의 `trivy_<버전>_windows-64bit.zip`                             |

```bash
# Debian/Ubuntu: apt-key 대신 전용 키링 사용
sudo apt-get install wget gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key \
  | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" \
  | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy=0.76.2
```

🟡 패키지 저장소는 갱신할 때 새 버전이 바로 설치될 수 있습니다. 운영 서버는 버전을 지정해 설치하고 `apt-mark hold trivy`처럼 자동 갱신을 막은 뒤, 검토한 버전만 올립니다.

### 컨테이너 이미지

| 레지스트리 | 이미지                              |
|------------|-------------------------------------|
| Docker Hub | `docker.io/aquasec/trivy`           |
| GHCR       | `ghcr.io/aquasecurity/trivy`        |
| AWS ECR    | `public.ecr.aws/aquasecurity/trivy` |

```bash
# 이미지 서명 확인 후 digest 확인
cosign verify ghcr.io/aquasecurity/trivy:0.76.2 \
  --certificate-identity-regexp 'https://github\.com/aquasecurity/trivy/\.github/workflows/.+' \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"

# 실행은 digest로 고정 (<digest>는 위 확인 결과의 sha256 값)
docker run --rm \
  -v trivy-cache:/root/.cache/ \
  ghcr.io/aquasecurity/trivy@sha256:<digest> image alpine:3.20
```

[⬆ 목차로 돌아가기](#목차)

## 3. 기본 사용법

### 대상별 실행

```bash
# 컨테이너 이미지
trivy image registry.example.com/app/api:1.4.2

# 소스 디렉토리 (lock 파일 기준 의존성 + 시크릿)
trivy fs ./app

# IaC 설정 (Terraform, Dockerfile, Kubernetes, Helm, CloudFormation 등)
trivy config ./infra

# 호스트 OS 패키지 (전체 순회를 피하려면 os 패키지만)
sudo trivy rootfs --pkg-types os --scanners vuln /

# Kubernetes 클러스터 요약
trivy k8s --report summary

# 기존 SBOM 파일 검사
trivy sbom ./app.cdx.json
```

`fs`는 CI에서 프로젝트를 검사하는 용도이고, `rootfs`는 호스트나 풀린 루트 파일시스템처럼 설치된 패키지를 검사하는 용도입니다. 검사 방식이 다르므로 목적에 맞게 고릅니다.

### 주요 옵션

| 옵션                          | 설명                                                                                                  |
|-------------------------------|-------------------------------------------------------------------------------------------------------|
| `--scanners`                  | 사용할 스캐너 (`vuln`, `misconfig`, `secret`, `license`)                                              |
| `--severity`                  | 표시할 심각도 (`UNKNOWN`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)                                        |
| `--ignore-unfixed`            | 수정 버전이 없는 취약점 제외(`--ignore-status affected,will_not_fix,fix_deferred,end_of_life`의 줄임) |
| `--exit-code`                 | 탐지 시 종료 코드 (기본 0)                                                                            |
| `--exit-on-eol`               | 지원 종료(EOL) OS면 지정한 코드로 종료                                                                |
| `--format`, `-f`              | 출력 형식 (`table`, `json`, `sarif`, `cyclonedx`, `spdx-json`, `template` 등)                         |
| `--output`, `-o`              | 결과 파일 경로                                                                                        |
| `--ignorefile`                | 예외 파일 경로 (기본 `.trivyignore`)                                                                  |
| `--skip-dirs`, `--skip-files` | 검사에서 뺄 디렉토리·파일                                                                             |
| `--show-suppressed`           | 예외로 숨긴 결과도 함께 표시                                                                          |
| `--offline-scan`              | 외부 저장소(Maven Central 등) 조회 없이 검사                                                          |
| `--timeout`                   | 제한 시간 (기본 5분)                                                                                  |

### 종료 코드

🟡 Trivy는 기본 설정에서 취약점을 찾아도 종료 코드 0을 반환합니다. CI에서 차단하려면 `--exit-code`를 반드시 지정합니다.

```bash
# HIGH는 보고만, CRITICAL이면 실패
trivy image --exit-code 0 --severity HIGH app:1.4.2
trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed app:1.4.2

# 지원이 끝난 OS 이미지는 실패 처리
trivy image --exit-on-eol 1 app:1.4.2
```

`--ignore-unfixed`를 쓰면 수정 버전이 없는 취약점이 빠지므로 오래된 OS에서 결과가 0건으로 보일 수 있습니다. `--exit-on-eol`을 함께 써서 지원이 끝난 OS를 놓치지 않습니다.

### 보고서

```bash
# JSON 보고서 (후처리·보관용)
trivy image -f json -o trivy-report.json app:1.4.2

# SARIF (GitHub code scanning 업로드용)
trivy fs -f sarif -o trivy.sarif .

# SBOM 생성
trivy image -f cyclonedx -o app.cdx.json app:1.4.2
trivy fs -f spdx-json -o app.spdx.json ./app
```

[⬆ 목차로 돌아가기](#목차)

## 4. 설정 파일과 예외

### trivy.yaml

명령행 옵션은 `trivy.yaml`에 같은 이름으로 적을 수 있습니다. 현재 디렉토리의 `trivy.yaml`을 읽으며 `--config`로 다른 경로를 지정합니다. 팀 공통 기준은 이 파일로 저장소에 두고 검토를 거쳐 바꿉니다.

```yaml
# trivy.yaml
timeout: 10m0s

# 탐지 시 실패, 지원이 끝난 OS도 실패
exit-code: 1
exit-on-eol: 1

severity:
  - HIGH
  - CRITICAL

ignorefile: ".trivyignore.yaml"

scan:
  scanners:
    - vuln
    - secret
    - misconfig
  skip-dirs:
    - "tests/fixtures"
  # 사내 기준: 버전 확인·사용 통계 전송 끄기
  skip-version-check: true
  disable-telemetry: true

vulnerability:
  ignore-unfixed: true

misconfiguration:
  scanners:
    - dockerfile
    - kubernetes
    - helm
    - terraform
```

🟡 Trivy는 기본적으로 `check.trivy.dev`에 버전 확인과 사용 통계를 보냅니다. 외부 전송을 제한하는 환경에서는 `skip-version-check`와 `disable-telemetry`를 모두 켭니다.

### 예외 처리

| 방법                | 형식                  | 사용 시점                                                                       |
|---------------------|-----------------------|---------------------------------------------------------------------------------|
| `.trivyignore`      | 한 줄에 ID 하나       | 간단한 예외. `CVE-2024-0001 exp:2026-12-31`처럼 만료일 지정 가능                |
| `.trivyignore.yaml` | 스캐너별 ID·경로·사유 | 경로·패키지 단위 예외와 사유 기록이 필요할 때(실험 기능, `--ignorefile`로 지정) |
| `--ignore-policy`   | Rego 정책 파일        | 조건이 복잡한 일괄 예외                                                         |
| VEX 문서            | CSAF·OpenVEX 등       | 공급자가 "영향 없음"을 공식 판정한 취약점                                       |

```yaml
# .trivyignore.yaml
vulnerabilities:
  - id: CVE-2024-0001
    purls:
      - "pkg:deb/debian/libexample1"
    expired_at: 2026-12-31
    statement: "취약 함수를 쓰지 않음. 패키지 업데이트 배포 후 제거(담당: 플랫폼팀)"
misconfigurations:
  - id: AVD-DS-0002
    paths:
      - "build/legacy/Dockerfile"
    expired_at: 2027-03-31
    statement: "레거시 빌드 이미지는 root 권한 필요. 이전 완료 후 제거"
secrets:
  - id: generic-unwanted-rule
    paths:
      - "docs/examples/sample.env"
```

- 예외에는 만료일(`expired_at` 또는 `exp:`)과 사유(`statement`)를 반드시 남깁니다. 만료일이 지나면 다시 탐지되어 재검토가 강제됩니다.
- 예외 파일은 코드 리뷰를 거쳐 바꾸고, 정기 점검 때 `--show-suppressed`로 숨긴 결과를 함께 확인합니다.
- `statement`는 기록용이며 필터링에는 쓰이지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 인프라 대상별 적용

### 적용 지점

| 지점                   | 명령                          | 실패 기준 예                      | 주기               |
|------------------------|-------------------------------|-----------------------------------|--------------------|
| 이미지 빌드 직후       | `trivy image`                 | CRITICAL(수정 버전 있음), EOL OS  | 빌드마다           |
| IaC 변경 검토(PR)      | `trivy config`                | HIGH 이상 설정 오류               | PR마다             |
| 애플리케이션 의존성    | `trivy fs`                    | CRITICAL(수정 버전 있음), 시크릿  | PR마다             |
| 레지스트리 보관 이미지 | `trivy image`                 | 보고만, 신규 CRITICAL 알림        | 매일(DB 갱신 반영) |
| 운영 호스트            | `trivy rootfs --pkg-types os` | 보고만, 패치 계획에 반영          | 매주               |
| Kubernetes 클러스터    | `trivy k8s --report summary`  | 보고만, 설정 오류·이미지 CVE 추적 | 매주               |

빌드 시점에 통과한 이미지도 이후 새 CVE가 공개되면 취약해집니다. 배포된 이미지는 레지스트리나 클러스터 단위로 정기 재검사합니다.

### IaC

```bash
# Terraform 변수 파일을 함께 반영
trivy config --tf-vars prod.tfvars ./terraform

# 내려받은 원격 모듈은 제외하고 자체 코드만
trivy config --tf-exclude-downloaded-modules ./terraform

# Helm chart 값 반영
trivy config --helm-values values-prod.yaml ./charts/api
```

- 지원 형식: Dockerfile, Kubernetes, Helm, Terraform(plan JSON 포함), CloudFormation, Azure ARM, Ansible.
- `image`·`fs`·`repo`에서는 설정 오류 검사가 기본으로 꺼져 있으므로 `--scanners misconfig`를 추가해야 합니다.
- 신뢰할 수 없는 기여자가 PR을 올리는 저장소는 `trivy config` 실행 환경에 메모리 제한을 둡니다(v0.71.0 미만은 조작된 Helm 압축 파일로 메모리 고갈 가능).

### 운영 호스트

```bash
# OS 패키지만 빠르게
sudo trivy rootfs --pkg-types os --scanners vuln \
  --skip-version-check --disable-telemetry \
  -f json -o "/var/lib/trivy/$(hostname)-$(date +%Y%m%d).json" /
```

- 호스트 전체 순회는 디스크 부하가 크므로 `--pkg-types os`로 범위를 줄이거나 `--skip-dirs`로 데이터 디렉토리를 뺍니다.
- 결과에는 호스트 이름·패키지 목록이 들어가므로 접근이 제한된 저장소에 보관합니다.

### Kubernetes

```bash
trivy k8s --report summary
trivy k8s --include-namespaces prod-app --report all
trivy k8s --report summary --disable-node-collector
```

- `trivy k8s`는 리소스를 읽을 수 있는 role 또는 cluster role이 필요합니다. node collector(기본 사용)를 쓰면 job을 만들고 추적하는 권한이 더 필요합니다.
- 운영 클러스터에서는 읽기 전용 전용 계정을 만들고, node collector가 job을 만드는 것이 허용되지 않으면 `--disable-node-collector`를 씁니다.
- `--exclude-namespaces`는 cluster role에서만 동작합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. CI/CD 연동

### GitHub Actions

```yaml
# .github/workflows/trivy.yml
name: trivy

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6.1.0

      # 태그 대신 전체 commit SHA로 고정 (v0.36.0)
      - uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25
        with:
          version: v0.76.2
          scan-type: fs
          scan-ref: .
          scanners: vuln,secret,misconfig
          severity: CRITICAL
          ignore-unfixed: true
          exit-code: "1"
          trivyignores: .trivyignore.yaml
```

- `trivy-action` v0.36.0의 기본 Trivy 버전은 v0.70.0이라 이후 보안 수정이 빠집니다. `version` 입력으로 검토한 버전을 지정합니다.
- 이미지 검사는 `scan-type: image`, `image-ref: <이미지>`를 씁니다. 저장소 기준 설정은 `trivy-config: trivy.yaml`로 넘길 수 있습니다.
- `version: latest`는 사고 당시 악성 바이너리를 받은 경로였으므로 쓰지 않습니다.

### GitLab CI

```yaml
# .gitlab-ci.yml
trivy:
  stage: test
  image:
    name: ghcr.io/aquasecurity/trivy@sha256:<digest>
    entrypoint: [""]
  variables:
    TRIVY_NO_PROGRESS: "true"
    TRIVY_CACHE_DIR: ".trivycache/"
  script:
    - trivy fs --exit-code 0 --severity HIGH .
    - trivy fs --exit-code 1 --severity CRITICAL --ignore-unfixed .
  cache:
    paths:
      - .trivycache/
```

GitLab의 Container Scanning 템플릿(`Security/Container-Scanning.gitlab-ci.yml`)도 내부적으로 Trivy를 씁니다. 템플릿을 쓰면 버전은 GitLab이 관리합니다.

### 실패 기준 정하기

| 단계      | 차단                                          | 보고만                   |
|-----------|-----------------------------------------------|--------------------------|
| 도입 초기 | 시크릿, CRITICAL(수정 버전 있음)              | HIGH, 설정 오류          |
| 안정화    | 시크릿, CRITICAL·HIGH(수정 버전 있음), EOL OS | MEDIUM, 설정 오류 MEDIUM |
| 성숙      | 위 항목 + HIGH 설정 오류                      | 나머지                   |

처음부터 모두 차단하면 기존 결과 때문에 배포가 멈춥니다. 기존 결과는 만료일이 있는 예외로 등록해 두고 신규 결과부터 차단합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 운영

### 데이터베이스와 캐시

Trivy 바이너리에는 검사 엔진만 들어 있고 검사 자료는 실행 시 내려받습니다.

| DB            | 이름            | 용도                |
|---------------|-----------------|---------------------|
| 취약점 DB     | `trivy-db`      | 취약점 검사         |
| Java DB       | `trivy-java-db` | JAR 파일 식별       |
| Checks Bundle | `trivy-checks`  | 설정 오류 검사 규칙 |

- 기본 내려받기 순서는 `mirror.gcr.io/aquasec`, `ghcr.io/aquasecurity`입니다.
- CI에서는 캐시 디렉토리(`--cache-dir`, 기본 `~/.cache/trivy`)를 재사용해 매번 DB를 받지 않게 합니다.
- 로컬 파일 캐시(BoltDB)는 한 번에 한 프로세스만 쓸 수 있습니다. 같은 캐시로 병렬 실행하면 잠금 대기가 생기므로 작업별 캐시를 나누거나 `--cache-backend memory`를 씁니다.
- 캐시 정리는 `trivy clean --scan-cache`처럼 `trivy clean` 하위 명령으로 합니다.

### 폐쇄망·제한 네트워크

| 외부 자원                          | 필요한 기능           | 대안                                                |
|------------------------------------|-----------------------|-----------------------------------------------------|
| OCI DB(`mirror.gcr.io`, `ghcr.io`) | 취약점·설정 오류 검사 | 사내 레지스트리에 DB 복제 후 `--db-repository` 지정 |
| Maven Central                      | Java 패키지 식별      | `--offline-scan`                                    |
| 원격 Terraform 모듈                | Terraform 검사        | 모듈을 미리 내려받아 둠                             |
| `check.trivy.dev`                  | 버전 확인·통계(선택)  | `--skip-version-check --disable-telemetry`          |

- `--db-repository`를 지정하면 기본 위치가 대체됩니다. 공식 위치를 예비로 두려면 함께 나열합니다.
- DB 위치는 사내에서 운영하거나 신뢰하는 레지스트리만 지정합니다. v0.71.1 미만은 조작된 DB 이미지로 임의 경로에 파일을 쓸 수 있었습니다.
- Checks Bundle을 받지 못하면 바이너리에 내장된 규칙(릴리스 시점 기준)으로 검사합니다.
- 내려받기를 막으려면 `--skip-db-update`, `--skip-java-db-update`, `--skip-check-update`를 씁니다. DB가 오래되면 새 CVE를 놓치므로 갱신 주기를 따로 관리합니다.

### 플러그인

플러그인은 Trivy가 내려받아 실행하는 외부 바이너리입니다. 공식 플러그인 목록이나 검토한 출처만 설치합니다. v0.72.0 미만은 조작된 플러그인이 플러그인 폴더 밖에 파일을 쓸 수 있었습니다.

### 결과 보관

- 결과 JSON과 SBOM은 이미지 digest·검사 일시·Trivy 버전·DB 갱신 시각과 함께 보관해야 나중에 비교할 수 있습니다.
- 보고서에는 이미지 이름, 내부 레지스트리 주소, 호스트 이름, 패키지 목록이 들어가므로 공개 저장소에 올리지 않습니다.
- 시크릿 탐지 결과는 값이 그대로 들어갈 수 있으므로 공유 전에 값을 가립니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 탐지 후 대응

### 취약점

1. 실제 사용 여부를 확인합니다. 런타임 이미지에 들어 있는지, 빌드 단계에만 쓰는지 구분합니다.
2. 수정 버전이 있으면 패키지나 기반 이미지를 올려 다시 빌드합니다. 기반 이미지 교체가 가장 많은 결과를 한 번에 줄입니다.
3. 수정 버전이 없거나 바로 올릴 수 없으면 영향을 줄이는 조치(기능 비활성, 네트워크 차단)를 하고 만료일이 있는 예외로 등록합니다.
4. EOL OS는 예외 대상이 아니라 교체 대상으로 계획합니다.

### 설정 오류

- 결과의 규칙 ID로 공식 설명을 확인하고 IaC 원본을 고칩니다. 운영 리소스를 콘솔에서 직접 고치면 코드와 달라지므로 코드에서 고쳐 배포합니다.
- 의도한 설정이면 해당 경로만 예외로 등록하고 사유를 남깁니다.

### 시크릿

시크릿은 [Gitleaks 가이드](./gitleaks_guide.md#8-탐지-후-대응)의 대응 순서를 따릅니다. 발급처에서 폐기·교체하는 것이 먼저이고, 이력 제거나 예외 등록이 그 뒤입니다.

### 공급망 사고 점검

신뢰한 배포 경로가 오염된 사고(2절)가 다시 생기면 다음을 확인합니다.

- 노출 시간 동안 해당 버전이나 `latest`를 받은 CI 작업과 서버가 있는지 실행 기록을 확인합니다.
- 그 작업에서 쓸 수 있던 CI 시크릿·클라우드 자격증명을 모두 교체합니다.
- Action 참조를 전체 SHA로 바꾸고, 바이너리·이미지 서명을 다시 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- Trivy: [github.com/aquasecurity/trivy](https://github.com/aquasecurity/trivy) — ★★★☆☆
- Trivy 공식 문서: [trivy.dev](https://trivy.dev/) — ★★★☆☆
- 공급망 사고 공지: [GHSA-69fq-xp46-6x23](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23) — ★★★☆☆
- Trivy GitHub Action: [github.com/aquasecurity/trivy-action](https://github.com/aquasecurity/trivy-action) — ★★★☆☆
- Trivy v0.76.2 릴리스(보안 수정): [github.com/aquasecurity/trivy/releases](https://github.com/aquasecurity/trivy/releases/tag/v0.76.2) — ★★★☆☆
- 확인 기록: [Trivy 참조 노트](../../_reference/trivy_official_notes.md)
- 관련 문서: [취약점 스캔 개요](./vulnerability_scanning.md), [Gitleaks 가이드](./gitleaks_guide.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-05

**마지막 업데이트**: 2026-11-10

© 2026 siasia86. Licensed under CC BY 4.0.
