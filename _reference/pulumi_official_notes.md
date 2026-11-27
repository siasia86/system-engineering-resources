---
name: pulumi-official-notes
description: Pulumi CLI v3.278.0 판, 자체 backend 종류와 로컬 로그인, 패스프레이즈 비밀값, 상태 파일 구조와 컨테이너 시험 결과 정리.
tags:
  - pulumi
  - iac
last_checked: 2026-11-27
sources:
  - https://github.com/pulumi/pulumi/releases
  - https://www.pulumi.com/docs/iac/concepts/state-and-backends/
  - https://www.pulumi.com/docs/iac/operations/stack-management/using-a-diy-backend/
  - https://www.pulumi.com/docs/iac/concepts/secrets/
---

# Pulumi 공식 자료 참조 노트

## 1. 판 (2026-11-27 확인)

- 최신 v3.278.0(2026-11-25). 이전 v3.277.0(11-18), v3.276.0·v3.275.0(11-12). 대체로 매주 릴리스.
- 릴리스 자산 `pulumi-v<판>-linux-x64.tar.gz`와 `pulumi-<판>-checksums.txt`. 시험한 압축판은 체크섬 일치.
- 압축판 구성: `pulumi`, `pulumi-language-{bun,dotnet,go,nodejs,pcl,python,python-exec,yaml}`, `pulumi-resource-pulumi-{nodejs,python}`.
- 라이선스: GitHub 저장소 Apache-2.0.

## 2. backend

- 자체 backend: S3, Azure Blob Storage, Google Cloud Storage, S3 호환(MinIO, Ceph, SeaweedFS), PostgreSQL, 로컬 파일.
- DIY 문서: "`pulumi login --local` is syntactic sugar for `pulumi login file://~`", 기본 디렉터리 `~/.pulumi`.
- 로그인 정보 `~/.pulumi/credentials.json`.
- v3.61.0부터 새 DIY backend의 stack은 project 단위로 나뉨.

## 3. 비밀값

- `pulumi config set --secret 키 값` → `pulumi config`에 `[secret]`, `Pulumi.<stack>.yaml`에 `secure:` 암호문.
- `stack change-secrets-provider`: `default`, `passphrase`, `awskms`, `azurekeyvault`, `gcpkms`, `hashivault`. `stack init --secrets-provider="<provider>://<settings>"`.
- 문서 두 쪽에서 `PULUMI_CONFIG_PASSPHRASE` 설명은 찾지 못함. CLI 오류 문구로 확인: "passphrase must be set with PULUMI_CONFIG_PASSPHRASE or PULUMI_CONFIG_PASSPHRASE_FILE environment variables".

## 4. 컨테이너 시험 (2026-11-27, Debian 13, YAML 런타임, random provider 4.21.6)

- 로그인 없이 비대화형 `stack init`: `PULUMI_ACCESS_TOKEN must be set for login during non-interactive CLI sessions`(종료 코드 3). `whoami`: `this command requires logging in`.
- 패스프레이즈 없이 `stack init`: 위 passphrase 오류. 틀린 패스프레이즈로 preview: `incorrect passphrase`.
- `up`: 3개 생성(Stack, RandomPassword, RandomPet). `RandomPassword.result`는 출력에 `[secret]`.
- 상태 파일에 설정 비밀값 원문 0건, `"ciphertext"` 항목 있음.
- 파일 구조: `.pulumi/meta.yaml`, `stacks/<project>/<stack>.json`(+`.bak`), `history/<project>/<stack>/*.history.json`·`*.checkpoint.json`, `backups/<project>/<stack>/*.json`, 각 파일의 `.attrs`.
- 다시 preview: `2 unchanged`, `--expect-no-changes` 종료 코드 0.
- `length` 16→20: `--diff`에 replace와 `~ length : 16 => 20`.
- 리소스가 남은 `stack rm`: 거부(종료 코드 1), `--force` 안내.
- `destroy` 뒤 stack 설정·이력은 남고 `stack rm`으로 삭제.
- random 플러그인 76MB.
- 미실행: Pulumi Cloud, 객체 저장소·PostgreSQL backend, 클라우드 provider, 언어 프로젝트, `convert` 변환.
