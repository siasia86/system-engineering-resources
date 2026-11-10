---
name: trivy-official-notes
description: Trivy 공식 릴리스, 보안 공지, 설치·서명 검증, 필터링·설정 파일, DB·폐쇄망, GitHub Action 확인 노트.
tags:
  - trivy
  - vulnerability-scanning
  - supply-chain
  - security
last_checked: 2026-11-10
sources:
  - https://api.github.com/repos/aquasecurity/trivy/releases
  - https://api.github.com/repos/aquasecurity/trivy/compare/v0.76.1...v0.76.2
  - https://aquasecurity.github.io/trivy-repo/deb/dists/generic/main/binary-amd64/Packages
  - https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23
  - https://github.com/aquasecurity/trivy/security/advisories/GHSA-mcj4-mphf-j9ff
  - https://github.com/aquasecurity/trivy/security/advisories/GHSA-8rc5-4fr6-64pw
  - https://github.com/aquasecurity/trivy/security/advisories/GHSA-q3fv-x8vg-qqm4
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/getting-started/installation.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/getting-started/signature-verification.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/configuration/filtering.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/configuration/others.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/configuration/db.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/configuration/cache.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/references/configuration/config-file.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/scanner/misconfiguration/index.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/target/kubernetes.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/target/rootfs.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/advanced/air-gap.md
  - https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/tutorials/integrations/gitlab-ci.md
  - https://github.com/aquasecurity/trivy-action/blob/v0.36.0/action.yaml
---

# Trivy Official Notes

## 1. 확인 범위

2026-11-05에 GitHub API(릴리스·보안 공지·태그)와 v0.76.1 태그의 `docs/` 원문을 직접 읽었습니다. 작업 서버에서 Trivy 바이너리는 실행하지 않았으므로 명령 출력·종료 코드는 문서 기재 내용이며 로컬 관찰이 아닙니다.

## 2. Version status

- 최신 릴리스: `v0.76.2`(2026-11-05). 직전 `v0.76.1`(2026-10-21), `v0.76.0`(2026-10-14). 저장소 라이선스 Apache-2.0, archive 아님.
- v0.76.1 릴리스는 GitHub immutable release로 표시됩니다.
- 2026-11-10 확인: `v0.76.2`(immutable)는 공식 이미지를 Alpine 3.24.3으로 다시 빌드하고 `golang.org/x/net`·`go-jose` 의존성을 올린 보안 수정판이며, 새 GHSA 공지는 없습니다. 0.77 계열 태그는 없고 v0.76.1과 v0.76.2 사이에 `docs/` 변경은 없습니다. `trivy-action` 최신은 그대로 `v0.36.0`입니다.
- v0.76.2 Linux x64 자산: `trivy_0.76.2_Linux-64bit.tar.gz`, `.deb`, `.rpm`과 각 `.sigstore.json`, `trivy_0.76.2_checksums.txt`와 그 `.sigstore.json`.
- `aquasecurity/trivy-action` 최신 릴리스 `v0.36.0`(2026-04-22, immutable). 태그 객체가 가리키는 commit은 `ed142fd0673e97e23eac54620cfb913e5ce36c25`입니다. `action.yaml`의 `version` 기본값은 `v0.70.0`입니다.

## 3. 보안 공지

| 공지                | 심각도   | 영향 범위                                                   | 수정                                        |
|---------------------|----------|-------------------------------------------------------------|---------------------------------------------|
| GHSA-69fq-xp46-6x23 | critical | 악성 v0.69.4, trivy-action 0.35.0 외 태그, setup-trivy 태그 | 0.69.3 이하·action 0.35.0·setup-trivy 0.2.6 |
| GHSA-mcj4-mphf-j9ff | high     | 조작된 OCI 자산의 파일 이름으로 임의 경로 쓰기              | 0.71.1                                      |
| GHSA-8rc5-4fr6-64pw | medium   | 조작된 플러그인 manifest로 플러그인 폴더 밖 쓰기            | 0.72.0                                      |
| GHSA-q3fv-x8vg-qqm4 | medium   | Helm chart 압축 폭탄으로 메모리 고갈                        | 0.71.0                                      |

- GHSA-69fq-xp46-6x23: 2026-03-19 탈취한 자격증명으로 악성 v0.69.4 배포, trivy-action 77개 태그 중 76개와 setup-trivy 7개 태그를 자격증명 탈취 코드로 교체. 2026-03-22 Docker Hub에 악성 v0.69.5·v0.69.6 이미지. 노출 시간은 v0.69.4 약 3시간, trivy-action 약 12시간, setup-trivy 약 4시간, Docker Hub 이미지 약 10시간. 원인은 2026-02 말 시작된 공격 뒤 자격증명 교체가 한꺼번에 이뤄지지 않은 것입니다. digest 참조 이미지, 소스 빌드, Homebrew 공식 formula는 영향 없음. 권장 조치: 안전 버전 사용, 노출 가능 시크릿 교체, Action 전체 SHA 고정.
- GHSA-mcj4-mphf-j9ff: `--db-repository`·`--java-db-repository`·`--checks-bundle-repository`·`trivy module install`로 공격자 저장소를 지정한 경우만 해당. 기본 Aqua 저장소는 영향 없음.
- GHSA-8rc5-4fr6-64pw: 공격자 플러그인을 설치한 경우만 해당. 공식 플러그인 목록은 영향 없음.
- GHSA-q3fv-x8vg-qqm4: `trivy config`(설정 오류 검사 항상 사용) 또는 `--scanners misconfig` 사용 시 조작된 `.tgz`가 경로에 있을 때.

## 4. 설치와 서명

- 공식 설치: 컨테이너 이미지(`docker.io/aquasec/trivy`, `ghcr.io/aquasecurity/trivy`, `public.ecr.aws/aquasecurity/trivy`), GitHub 릴리스, 설치 스크립트, yum 저장소(`gpgcheck=1`), apt 저장소(`signed-by` 키링, suite `generic main`), Homebrew, Windows zip, FreeBSD pkg. Arch·openSUSE·MacPorts·Nix·asdf/mise는 Community 표기.
- v0.68.1부터 릴리스 자산마다 `.sigstore.json` 묶음이 있으며 `.sig`·`.pem`은 더 이상 배포하지 않습니다. cosign v3.0.0 이상 기준이며 v2(2.4.0 이상)는 `--new-bundle-format`을 추가합니다. `verify-blob`의 identity는 `https://github.com/aquasecurity/trivy/.github/workflows/reusable-release.yaml@refs/tags/<tag>`입니다.
- 이미지 검증은 `cosign verify`에 identity 정규식 `https://github\.com/aquasecurity/trivy/\.github/workflows/.+`를 씁니다. RPM·Deb는 GPG 서명도 있습니다.
- 공식 문서의 이미지 태그 예시는 `v`를 뺀 버전(`0.76.1` 형식)입니다.

## 5. 사용과 설정

- 기본 종료 코드는 탐지가 있어도 0이며 `--exit-code`로 바꿉니다. `--exit-on-eol`은 image·vm·sbom·rootfs에서 EOL OS를 실패 처리합니다.
- `--ignore-unfixed`는 `--ignore-status affected,will_not_fix,fix_deferred,end_of_life`의 줄임입니다.
- `.trivyignore`는 한 줄에 ID 하나이며 `exp:yyyy-mm-dd`로 만료일을 붙입니다. `.trivyignore.yaml`(실험 기능, `--ignorefile`로 지정)은 `vulnerabilities`·`misconfigurations`·`secrets`·`licenses`별로 `id`, `paths`, `purls`(취약점만), `expired_at`, `statement`(필터링에 쓰이지 않음)를 둡니다. `--show-suppressed`로 숨긴 결과를 봅니다. 그 밖에 Rego(`--ignore-policy`)와 VEX가 있습니다.
- 설정 오류 검사는 `image`·`fs`·`repo`에서 기본으로 꺼져 있고 `--scanners misconfig`로 켭니다. 지원 형식은 azure-arm, cloudformation, dockerfile, helm, kubernetes, terraform, terraformplan-json, terraformplan-snapshot, ansible입니다.
- `trivy.yaml` 기본값: `timeout: 5m0s`, `exit-code: 0`, `ignorefile: ".trivyignore"`, `scan.scanners: [vuln, secret]`, `scan.disable-telemetry: false`, `scan.skip-version-check: false`.
- 버전 확인과 사용 통계는 `check.trivy.dev`로 보내며 `--skip-version-check`, `--disable-telemetry`로 끕니다.
- `rootfs`는 호스트·풀린 파일시스템용이고 CI 프로젝트 검사는 `fs`를 권장합니다. `--pkg-types os --scanners vuln`이면 전체 순회를 하지 않습니다.
- `trivy k8s`는 role 또는 cluster role 권한이 필요하며 node collector(기본 사용)는 job 관련 권한이 더 필요합니다. `--exclude-namespaces`는 cluster role에서만 동작합니다.

## 6. DB·캐시·네트워크

- DB는 `trivy-db`, `trivy-java-db`, `trivy-checks` OCI 이미지이며 기본 순서는 `mirror.gcr.io/aquasec`, `ghcr.io/aquasecurity`입니다. `--db-repository` 등을 지정하면 기본값이 대체되고, 여러 값을 주면 429·5xx 오류 시 다음 위치로 넘어갑니다(Checks Bundle 제외).
- `--skip-db-update`, `--skip-java-db-update`, `--skip-check-update`로 내려받기를 끕니다. Checks Bundle을 못 받으면 바이너리 내장 규칙을 씁니다.
- 로컬 캐시 backend는 BoltDB라 한 번에 한 프로세스만 접근합니다. `--cache-backend memory`, Redis backend도 있습니다. `trivy clean`으로 캐시를 지웁니다.
- 외부 자원: OCI DB, VEX Hub(`api.github.com`, `codeload.github.com`), Maven Central(`--offline-scan`으로 차단), 원격 Terraform 모듈, `check.trivy.dev`(선택).

## 7. 적용 범위와 제한

- 이 노트와 가이드의 명령은 공식 문서 기준이며 작업 서버에서 실행하지 않았습니다. 패키지 저장소의 버전 문자열(`trivy=0.76.2`)은 2026-11-10 apt 저장소 `Packages` 목록에서 확인했고, GHCR `0.76.2` 태그는 있으나 이미지 digest 값은 문서에 고정하지 않았습니다.
- 공식 문서의 설정 오류 ID 예시는 `AVD-DS-0002` 형식입니다. 실제 결과의 ID 형식은 사용 버전의 출력으로 확인합니다.
