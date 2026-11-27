# Pulumi
<!-- reference: _reference/pulumi_official_notes.md -->

Python·TypeScript·Go·C#·Java·YAML 같은 일반 언어로 인프라를 정의하는 IaC 도구입니다. Terraform처럼 상태(state)를 두고 미리 보기(preview) → 적용(up)으로 바꾸지만, 반복·조건·함수를 언어 그대로 씁니다. 이 문서만으로 설치 → 로컬 파일 backend → 첫 프로젝트 → 비밀값 → 주요 명령 → 상태 파일 확인 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Pulumi CLI v3.278.0 (2026-11-25), random provider 4.21.6 (2026-11-27 확인)
- 예제 시험: 2026-11-27 2~7절을 Debian 13 컨테이너에서 로컬 파일 backend로 실행해 패스프레이즈 없음·틀림 오류, `config set --secret`, preview·up·output, 상태 파일 안의 비밀값 암호화, 두 번째 stack, export, refresh, 속성 변경 시 교체(replace) 미리 보기, destroy·stack rm, 로그인 안 한 상태의 오류, `--expect-no-changes`를 확인. Pulumi Cloud, S3·Azure Blob·GCS·PostgreSQL backend, 클라우드 provider(AWS 등) 배포, Python·TypeScript 언어 프로젝트는 미실행

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. backend 고르기](#3-backend-고르기)           |
| [4. 첫 프로젝트](#4-첫-프로젝트) / [5. 비밀값과 패스프레이즈](#5-비밀값과-패스프레이즈)    |
| [6. 주요 명령](#6-주요-명령) / [7. 상태 파일 구조](#7-상태-파일-구조) / [8. 검증](#8-검증) |
| [9. 운영 팁](#9-운영-팁) / [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기)      |

---

## 1. 개요

```text
[program: Python / TS / Go / YAML] --> [language host] --> [pulumi engine] --> [provider plugin] --> cloud API
                                                               │
                                                               └── state: Pulumi Cloud or self-managed backend
```

| 항목      | Pulumi                                                 | Terraform                              |
|-----------|--------------------------------------------------------|----------------------------------------|
| 언어      | Python, TypeScript/JavaScript, Go, C#, Java, YAML      | HCL                                    |
| 상태 기본 | Pulumi Cloud(로그인 필요). 자체 backend로 바꿀 수 있음 | 로컬 파일. 원격 backend로 바꿀 수 있음 |
| 비밀값    | 설정·상태의 비밀값을 stack 단위로 암호화               | 상태에 평문(민감 표시는 출력만 가림)   |
| 묶음 단위 | project 안의 stack(dev·prod 등)                        | workspace 또는 디렉터리 분리           |
| 라이선스  | Apache 2.0(CLI·SDK)                                    | BSL 1.1(1.6 이후)                      |

- provider 상당수는 Terraform provider를 감싸 만든 것이라 다루는 리소스 범위가 비슷합니다.
- 다른 형식의 프로그램을 옮길 때는 `pulumi convert`가 있습니다(예: `--from terraform`, 변환 자체는 미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

GitHub 릴리스 압축판과 체크섬 파일을 대조합니다.

```bash
V=3.278.0
curl -sSLO https://github.com/pulumi/pulumi/releases/download/v${V}/pulumi-v${V}-linux-x64.tar.gz
curl -sSLO https://github.com/pulumi/pulumi/releases/download/v${V}/pulumi-${V}-checksums.txt
grep " pulumi-v${V}-linux-x64.tar.gz\$" pulumi-${V}-checksums.txt | sha256sum -c -
tar xzf pulumi-v${V}-linux-x64.tar.gz
sudo cp pulumi/* /usr/local/bin/
pulumi version
```

- 압축판에는 `pulumi`와 언어별 실행기(`pulumi-language-python`, `-nodejs`, `-go`, `-dotnet`, `-yaml`, `-bun` 등)가 함께 들어 있습니다.
- Python·TypeScript 프로젝트는 그 언어 런타임(Python, Node.js)이 따로 필요합니다. YAML 프로젝트는 추가 런타임이 필요 없습니다.
- provider는 처음 쓸 때 플러그인으로 내려받아 `~/.pulumi/plugins`에 둡니다. 시험에서 random provider 하나가 76MB였습니다.
- 공식 설치 스크립트(`curl -fsSL https://get.pulumi.com | sh`)도 있습니다(미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 3. backend 고르기

상태를 어디에 둘지 정합니다. 기본 backend가 Pulumi Cloud라서 로그인하지 않은 채 `pulumi stack init`을 비대화형으로 실행하면 `PULUMI_ACCESS_TOKEN must be set for login during non-interactive CLI sessions`(종료 코드 3)로 실패합니다. 계정 없이 쓰려면 먼저 자체 backend로 로그인합니다.

| backend              | 로그인                                    | 쓰는 곳                        |
|----------------------|-------------------------------------------|--------------------------------|
| Pulumi Cloud         | `pulumi login`                            | 기본값. 잠금·이력 화면·팀 권한 |
| 로컬 파일            | `pulumi login --local` 또는 `file://경로` | 혼자 시험, 오프라인            |
| S3·S3 호환           | `pulumi login s3://버킷`                  | AWS, MinIO·Ceph 등             |
| Azure Blob           | `pulumi login azblob://컨테이너`          | Azure                          |
| Google Cloud Storage | `pulumi login gs://버킷`                  | GCP                            |
| PostgreSQL           | `pulumi login postgres://...`             | DB에 상태 저장                 |

```bash
pulumi login --local          # file://~ 와 같음, ~/.pulumi 아래에 상태 저장
pulumi login file:///srv/pulumi-state
pulumi whoami -v              # 현재 backend 확인
```

- 로그인 정보는 `~/.pulumi/credentials.json`에 남습니다. `--local`로 로그인하면 `"current": "file://~"`가 기록됩니다.
- 자체 backend의 stack은 v3.61.0부터 project 단위로 나뉩니다(같은 이름 `dev`를 project마다 쓸 수 있음).

[⬆ 목차로 돌아가기](#목차)

---

## 4. 첫 프로젝트

언어 런타임 없이 바로 시험할 수 있는 YAML 프로젝트입니다. 무작위 비밀번호와 이름을 만듭니다.

```bash
mkdir demo && cd demo
```

`Pulumi.yaml`:

```yaml
name: demo
runtime: yaml
description: local backend test
config:
  prefix:
    type: string
    default: web
resources:
  pw:
    type: random:RandomPassword
    properties:
      length: 16
  pet:
    type: random:RandomPet
    properties:
      prefix: ${prefix}
outputs:
  petName: ${pet.id}
  password: ${pw.result}
```

```bash
export PULUMI_CONFIG_PASSPHRASE='<PASSPHRASE>'
pulumi stack init dev
pulumi config set prefix api
pulumi up --yes
```

- 언어 프로젝트는 `pulumi new python`·`pulumi new typescript`로 틀을 만듭니다(템플릿을 내려받음, 미시험).
- `RandomPassword.result`는 provider가 비밀값으로 표시하므로 출력에 `[secret]`으로 나옵니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 비밀값과 패스프레이즈

자체 backend는 기본으로 패스프레이즈 방식 비밀값 관리자를 씁니다. stack을 만들 때 패스프레이즈에서 키를 만들고, 그 키로 설정과 상태의 비밀값을 암호화합니다.

| 변수                            | 뜻                          |
|---------------------------------|-----------------------------|
| `PULUMI_CONFIG_PASSPHRASE`      | 패스프레이즈 문자열         |
| `PULUMI_CONFIG_PASSPHRASE_FILE` | 패스프레이즈가 든 파일 경로 |

```bash
pulumi config set --secret dbPassword '<DB_PASSWORD>'
pulumi config                      # dbPassword  [secret]
pulumi stack output password --show-secrets
```

`Pulumi.dev.yaml`은 이렇게 됩니다(값은 줄임).

```yaml
encryptionsalt: v1:...
config:
  demo:dbPassword:
    secure: v1:...
  demo:prefix: api
```

- `Pulumi.<stack>.yaml`은 Git에 커밋해도 비밀값이 암호문입니다. 패스프레이즈는 커밋하지 않습니다.
- 시험에서 상태 파일(`stacks/demo/dev.json`)에 비밀번호 원문은 없고 `"ciphertext"` 항목으로 저장됐습니다.
- 패스프레이즈를 잃으면 그 stack의 비밀값을 풀 수 없습니다. 비밀번호 관리자 등에 따로 보관합니다.
- 클라우드 키로 바꾸려면 `pulumi stack init --secrets-provider="awskms://..."` 또는 `pulumi stack change-secrets-provider`를 씁니다. 지원: `default`(Pulumi Cloud), `passphrase`, `awskms`, `azurekeyvault`, `gcpkms`, `hashivault`.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 주요 명령

| 명령                                     | 하는 일                                                      |
|------------------------------------------|--------------------------------------------------------------|
| `pulumi preview` (`--diff`)              | 바뀔 내용 미리 보기, `--diff`는 속성 단위 차이               |
| `pulumi up --yes`                        | 적용                                                         |
| `pulumi stack output` (`--show-secrets`) | 출력값 보기                                                  |
| `pulumi refresh --yes`                   | 실제 리소스 상태를 읽어 상태 파일 맞추기                     |
| `pulumi destroy --yes`                   | 리소스 삭제(stack 설정·이력은 남음)                          |
| `pulumi stack rm 이름 --yes`             | stack 자체 삭제(리소스가 남아 있으면 거부, `--force`로 무시) |
| `pulumi stack ls` / `select` / `init`    | stack 목록·선택·생성                                         |
| `pulumi stack export --file x.json`      | 상태를 JSON으로 내보내기(`import`로 되돌림)                  |

- 시험에서 `length: 16`을 `20`으로 바꾸면 `--diff`에 `+-... (replace)`와 `~ length : 16 => 20`이 나왔습니다. 교체(replace)는 삭제 후 다시 만드는 것이므로 운영 리소스에서는 미리 보기를 꼭 봅니다.
- 비대화형(CI)에서는 `--yes`와 `--non-interactive`를 함께 줍니다. 버전 확인 요청을 끄려면 `PULUMI_SKIP_UPDATE_CHECK=true`.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 상태 파일 구조

`pulumi login file:///state`로 시험했을 때 생긴 파일입니다(`.attrs` 파일 생략).

```text
/state/.pulumi/
├── meta.yaml
├── stacks/demo/dev.json            # 현재 상태 (project/stack)
├── stacks/demo/dev.json.bak        # 직전 상태
├── history/demo/dev/dev-<n>.history.json      # 실행 기록
├── history/demo/dev/dev-<n>.checkpoint.json
└── backups/demo/dev/dev.<n>.json   # 백업
```

- 상태 디렉터리 전체를 백업합니다. 여러 사람이 같은 파일 backend를 쓰면 동시에 실행하지 않도록 주의합니다.
- 상태를 손으로 고쳐야 할 때는 파일을 직접 고치지 말고 `pulumi stack export` → 수정 → `pulumi stack import`, 또는 `pulumi state delete` 같은 명령을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용 | 방법                                        | 기대 결과                       |
|------|-----------|---------------------------------------------|---------------------------------|
| 1    | 설치      | `pulumi version`                            | v3.278.0                        |
| 2    | backend   | `pulumi whoami -v`                          | 고른 backend 주소               |
| 3    | 미리 보기 | `pulumi preview`                            | `+ 3 to create` 등 예상한 변경  |
| 4    | 적용      | `pulumi up --yes`                           | 종료 코드 0, `created`          |
| 5    | 멱등      | `pulumi preview --expect-no-changes`        | `unchanged`만, 종료 코드 0      |
| 6    | 비밀값    | `pulumi config`, 상태 파일에서 원문 검색    | `[secret]`, 원문 0건            |
| 7    | 정리      | `pulumi destroy --yes` 뒤 `pulumi stack rm` | 리소스 0, stack 목록에서 사라짐 |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영 팁

- 팀에서 자체 backend를 쓸 때는 S3 같은 객체 저장소에 두고 버전 관리를 켜 두면 상태를 되돌리기 쉽습니다.
- stack마다 다른 값은 `Pulumi.<stack>.yaml`에, 공통 기본값은 `Pulumi.yaml`의 `config`에 둡니다.
- 운영 stack은 `pulumi preview`를 CI에서 돌려 결과를 리뷰에 붙이고, 승인 뒤 `pulumi up`을 실행하는 흐름이 흔합니다.
- 비밀값 파일을 따로 관리한다면 [SOPS](./sops.md)로 암호화한 파일을 프로그램에서 읽는 방법도 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                                                                    | 원인                                      | 조치                                                   |
|-----------------------------------------------------------------------------------------|-------------------------------------------|--------------------------------------------------------|
| `passphrase must be set with PULUMI_CONFIG_PASSPHRASE or PULUMI_CONFIG_PASSPHRASE_FILE` | 자체 backend에서 패스프레이즈 변수 없음   | 변수 설정. CI는 비밀 변수로                            |
| `incorrect passphrase`                                                                  | stack을 만들 때와 다른 패스프레이즈       | 원래 패스프레이즈 사용. 잃었으면 비밀값 다시 설정 필요 |
| `PULUMI_ACCESS_TOKEN must be set for login during non-interactive CLI sessions`         | 기본 backend가 Pulumi Cloud, 로그인 안 함 | `pulumi login --local` 또는 원하는 backend로 로그인    |
| `stack rm`이 거부됨                                                                     | 리소스가 남아 있음                        | `pulumi destroy` 먼저                                  |
| 플러그인 내려받기 실패                                                                  | 외부 접속 제한                            | 프록시 설정 또는 `pulumi plugin install`로 미리 설치   |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Terraform](./terraform.md) — HCL 기반 IaC
- [SOPS](./sops.md) — 비밀값 파일 암호화
- [Ansible 기초](./ansible_basic_guide.md) — 서버 안 설정 관리

---

## 참고 자료

- Pulumi Docs: [State and backends](https://www.pulumi.com/docs/iac/concepts/state-and-backends/) · [DIY backend](https://www.pulumi.com/docs/iac/operations/stack-management/using-a-diy-backend/) · [Secrets](https://www.pulumi.com/docs/iac/concepts/secrets/) — ★★★☆☆
- GitHub: [pulumi/pulumi releases](https://github.com/pulumi/pulumi/releases) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.
