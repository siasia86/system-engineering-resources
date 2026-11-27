# SOPS
<!-- reference: _reference/sops_official_notes.md -->

YAML·JSON·ENV·INI 파일에서 값만 암호화하고 키 이름과 구조는 그대로 두는 비밀값 파일 편집 도구입니다. 암호화한 파일을 Git에 그대로 커밋할 수 있고, diff에서 어느 키가 바뀌었는지 보입니다. 이 문서만으로 설치 → age 키 만들기 → `.sops.yaml` 규칙 → 암호화·복호화·수정 → 명령에 값 넘기기 → 키 추가·교체 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: SOPS v3.13.3 (2026-07-23), age v1.3.2 (2026-08-29) (2026-11-27 확인)
- 예제 시험: 2026-11-27 2~7절을 Debian 13 컨테이너에서 실행해 선택한 키만 암호화, 추출·값 변경·편집, 규칙 불일치 오류, `exec-env`·`exec-file`, 받는 사람 추가(`updatekeys`), 데이터 키 교체(`rotate`), 키 없음·MAC 불일치 오류를 확인. PGP와 클라우드 KMS(AWS·GCP·Azure·HashiCorp Vault) 연동, 키 그룹(`key_groups`)·`shamir_threshold`, Git `textconv` 연동은 미실행

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. age 키 만들기](#3-age-키-만들기)                                   |
| [4. .sops.yaml 규칙](#4-sopsyaml-규칙) / [5. 암호화·복호화·수정](#5-암호화복호화수정)                            |
| [6. 명령에 값 넘기기](#6-명령에-값-넘기기) / [7. 키 추가와 교체](#7-키-추가와-교체) / [8. Git과 CI](#8-git과-ci) |
| [9. 검증](#9-검증) / [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기)                                  |

---

## 1. 개요

```text
plain file ──sops encrypt──> file with ENC[...] values + sops metadata ──git commit
                 │                                   │
                 │ data key (random, per file)       │ data key wrapped for each recipient
                 └── values encrypted (AES256-GCM)   └── age / PGP / AWS KMS / GCP KMS / Azure / Vault
```

| 항목      | 내용                                                                                   |
|-----------|----------------------------------------------------------------------------------------|
| 하는 일   | 값만 암호화, 키 이름·주석·구조는 평문으로 둠. 파일 전체에 MAC을 붙여 변조를 막음       |
| 파일 형식 | YAML, JSON, ENV(dotenv), INI, 그 밖의 파일은 통째로(binary)                            |
| 키 방식   | age, PGP, AWS KMS, GCP KMS, Azure Key Vault, HuaweiCloud KMS, HashiCorp Vault(OpenBao) |
| 라이선스  | MPL 2.0, CNCF Sandbox 프로젝트                                                         |

- 파일마다 무작위 데이터 키를 만들어 값을 암호화하고, 그 데이터 키를 받는 사람(age 공개키 등)마다 따로 감싸 파일 끝 `sops:` 블록에 둡니다. 받는 사람 중 한 명의 비밀키만 있으면 풀 수 있습니다.
- 비슷한 도구와의 차이:

| 도구                                | 다른 점                                                                       |
|-------------------------------------|-------------------------------------------------------------------------------|
| [Ansible Vault](./ansible_vault.md) | Ansible 안에서 쓰고 파일 전체를 암호화(키 이름도 안 보임), 비밀번호 하나로 풂 |
| HashiCorp Vault                     | 비밀값을 서버에 두고 API로 꺼냄. SOPS는 서버 없이 파일로 둠                   |
| Kubernetes Sealed Secrets           | 클러스터 컨트롤러만 풀 수 있음. SOPS는 사람·CI·도구 어디서나 풂               |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

GitHub 릴리스의 단일 실행 파일과 체크섬 파일을 받아 대조합니다.

```bash
SV=3.13.3
curl -sSLO https://github.com/getsops/sops/releases/download/v${SV}/sops-v${SV}.linux.amd64
curl -sSLO https://github.com/getsops/sops/releases/download/v${SV}/sops-v${SV}.checksums.txt
grep " sops-v${SV}.linux.amd64\$" sops-v${SV}.checksums.txt | sha256sum -c -
sudo install -m 755 sops-v${SV}.linux.amd64 /usr/local/bin/sops
sops --version
```

age는 압축판에 `age`와 `age-keygen`이 들어 있습니다. 체크섬은 GitHub 릴리스 페이지의 자산 digest와 대조합니다.

```bash
AV=1.3.2
curl -sSLO https://github.com/FiloSottile/age/releases/download/v${AV}/age-v${AV}-linux-amd64.tar.gz
sha256sum age-v${AV}-linux-amd64.tar.gz
tar xzf age-v${AV}-linux-amd64.tar.gz
sudo install -m 755 age/age age/age-keygen /usr/local/bin/
```

- 시험한 체크섬: `sops-v3.13.3.linux.amd64`는 체크섬 파일과 일치, `age-v1.3.2-linux-amd64.tar.gz`는 `cbe24006683f8eb669266162894b9a522a1af52f2665fbc63a4bb032ed26ac10`(릴리스 digest와 일치)
- macOS는 `brew install sops age`로도 설치할 수 있습니다(미시험).

[⬆ 목차로 돌아가기](#목차)

---

## 3. age 키 만들기

SOPS는 Linux에서 `$XDG_CONFIG_HOME/sops/age/keys.txt`, 없으면 `~/.config/sops/age/keys.txt`의 age 비밀키를 읽습니다.

```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
chmod 600 ~/.config/sops/age/keys.txt
age-keygen -y ~/.config/sops/age/keys.txt      # 공개키(age1...) 출력
```

| 위치·변수           | 쓰임                                                 |
|---------------------|------------------------------------------------------|
| 기본 위치           | 위 `keys.txt`. 여러 줄에 비밀키를 여러 개 둘 수 있음 |
| `SOPS_AGE_KEY_FILE` | 다른 키 파일 경로                                    |
| `SOPS_AGE_KEY`      | 비밀키 문자열 자체(CI 비밀 변수에 넣을 때)           |

- 공개키(`age1...`)는 `.sops.yaml`에 적어 공유하고, 비밀키(`AGE-SECRET-KEY-1...`)는 사람마다·CI마다 따로 보관합니다.
- 시험(v3.13.3)에서 `SOPS_AGE_KEY_FILE`로 틀린 키 파일을 줘도 기본 위치의 키로 복호화가 성공했습니다. 변수는 기본 위치를 대신하지 않고 함께 읽힙니다. 키 하나만으로 되는지 확인할 때는 기본 위치에 키가 없는 환경에서 시험합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. .sops.yaml 규칙

저장소 루트에 `.sops.yaml`을 두면 파일 경로에 맞는 규칙으로 받는 사람과 암호화 범위가 정해집니다. 이름은 `.sops.yaml`이어야 하고 `.sops.yml`은 자동으로 찾지 않습니다.

```yaml
creation_rules:
  - path_regex: secrets/.*\.yaml$
    encrypted_regex: ^(password|token)$
    age: age1aaa...,age1bbb...
  - path_regex: secrets/.*\.env$
    age: age1aaa...,age1bbb...
```

| 키                                                                         | 뜻                                                              |
|----------------------------------------------------------------------------|-----------------------------------------------------------------|
| `path_regex`                                                               | 대상 파일 경로 정규식. 규칙은 위에서부터 보고 처음 맞는 것을 씀 |
| `age`                                                                      | 받는 사람 공개키. 쉼표로 여러 명                                |
| `encrypted_regex`                                                          | 이 정규식에 맞는 키의 값만 암호화. 없으면 모든 값을 암호화      |
| `unencrypted_suffix`                                                       | 이 접미사로 끝나는 키는 암호화하지 않음(기본 `_unencrypted`)    |
| `pgp`, `kms`, `gcp_kms`, `azure_keyvault`, `hckms`, `hc_vault_transit_uri` | 다른 키 방식                                                    |

- 이 밖에 `unencrypted_regex`, `encrypted_suffix`, `key_groups`·`shamir_threshold`(여러 키 묶음 중 몇 개가 있어야 풀지)도 있습니다(v3.13.3 소스의 설정 키 이름 기준, 미시험).

- `encrypted_regex: ^(password|token)$`로 시험하면 `host`·`user`는 평문, `password`·`token`만 `ENC[AES256_GCM,...]`이 됐습니다.
- `.sops.yaml`이 있는데 맞는 규칙이 없으면 명령행에 `--age`를 줘도 `error loading config: no matching creation rules found`로 실패합니다(시험 결과). 규칙을 추가하거나, 규칙 없이 한 번만 쓸 때는 `sops --config /dev/null encrypt --age age1... 파일`을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 암호화·복호화·수정

```bash
# 암호화 (-i: 제자리에 덮어씀, 없으면 표준 출력)
sops encrypt -i secrets/app.yaml

# 복호화 (표준 출력, 파일은 그대로)
sops decrypt secrets/app.yaml
sops decrypt --output-type json secrets/app.yaml

# 값 하나만 꺼내기
sops decrypt --extract '["db"]["password"]' secrets/app.yaml

# 값 하나만 바꾸기 (값은 JSON 형식, 문자열은 따옴표 포함)
sops set secrets/app.yaml '["api"]["token"]' '"new-token"'

# 편집기에서 평문으로 열고 저장하면 다시 암호화
sops edit secrets/app.yaml

# 암호화 여부 확인
sops filestatus secrets/app.yaml        # {"encrypted":true}
```

암호화 뒤 파일은 이런 모양입니다(값은 줄임). `<ENCRYPTED>` 자리에는 실제로 `ENC[AES256_GCM,data:...,iv:...,tag:...,type:str]` 형식의 암호문이 들어갑니다.

```yaml
db:
    host: db.example.com
    user: app
    password: <ENCRYPTED>
sops:
    age:
        - recipient: age1...
          enc: |
            -----BEGIN AGE ENCRYPTED FILE-----
            ...
    lastmodified: "..."
    mac: ENC[AES256_GCM,data:...]
    encrypted_regex: ^(password|token)$
    version: 3.13.3
```

- `sops edit`은 `EDITOR` 환경 변수의 편집기를 씁니다. 평문 임시 파일이 편집하는 동안 디스크에 생기므로 공유 서버에서는 주의합니다.
- 평문으로 남긴 값(`host` 등)도 MAC 계산에 들어갑니다. 손으로 고치면 복호화가 MAC 불일치로 실패합니다(10절). 평문 값도 `sops edit`이나 `sops set`으로 고칩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 명령에 값 넘기기

복호화한 값을 파일로 남기지 않고 명령에 넘깁니다.

```bash
# 환경 변수로 넘기기 (최상위 키만, 값이 평평해야 함)
sops exec-env secrets/app.enc.env 'echo mode=$MODE'

# 임시 파일로 넘기기 ({}가 임시 파일 경로로 바뀜)
sops exec-file secrets/app.yaml 'grep -c password {}'
```

- `exec-env`는 중첩된 YAML을 받지 못합니다. 시험에서 `db:` 아래에 값이 있는 파일은 `cannot use complex value in environment; offending key db`로 실패했습니다. 환경 변수용은 dotenv 파일(`KEY=value`)로 따로 둡니다.
- dotenv 파일도 `.sops.yaml`에 맞는 규칙이 있어야 암호화됩니다(4절 예시의 `.env` 규칙).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 키 추가와 교체

| 상황                           | 명령                                           | 하는 일                                                         |
|--------------------------------|------------------------------------------------|-----------------------------------------------------------------|
| 받는 사람 추가·삭제            | `.sops.yaml` 수정 뒤 `sops updatekeys -y 파일` | 데이터 키를 새 받는 사람 목록으로 다시 감쌈. 값 암호문은 그대로 |
| 데이터 키 교체(사람이 나갈 때) | `sops rotate -i 파일`                          | 새 데이터 키를 만들어 모든 값을 다시 암호화                     |

```bash
# 받는 사람 B를 추가한 뒤
sops updatekeys -y secrets/app.yaml
SOPS_AGE_KEY_FILE=b_keys.txt sops decrypt secrets/app.yaml   # B도 풀 수 있음

# 사람을 뺐다면: 받는 사람에서 지운 뒤 updatekeys → rotate
sops rotate -i secrets/app.yaml
```

- 시험에서 `updatekeys` 뒤 `recipient` 2개가 됐고 두 번째 키로 복호화됐습니다. `rotate` 뒤에는 값의 암호문과 감싼 데이터 키가 모두 바뀌었고 값은 그대로였습니다.
- 받는 사람에서 빼기만 하면 그 사람은 예전 데이터 키를 알고 있을 수 있습니다. 빠진 사람이 알던 비밀값 자체(DB 비밀번호 등)도 바꾸는 것이 안전합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. Git과 CI

- 커밋할 것: `.sops.yaml`, 암호화된 파일. 커밋하지 않을 것: `keys.txt`, 복호화한 평문 파일(`.gitignore`에 추가).
- 암호화 전 평문을 한 번이라도 커밋했다면 이력에 남습니다. 그 비밀값은 바꾸고 이력 검사 도구로 확인합니다([gitleaks](../../04_security/hardening/gitleaks_guide.md)).
- CI에서는 비밀키 문자열을 CI의 비밀 변수에 넣고 `SOPS_AGE_KEY`로 넘깁니다.

```yaml
# GitHub Actions 예시 (단계 일부)
- name: decrypt and deploy
  env:
    SOPS_AGE_KEY: ${{ secrets.SOPS_AGE_KEY }}
  run: sops exec-env deploy/prod.enc.env './deploy.sh'
```

- CI용 키는 사람 키와 따로 만들어 받는 사람에 추가하면, CI 키만 교체하거나 빼기 쉽습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

| 순서 | 확인 내용   | 방법                                     | 기대 결과                            |
|------|-------------|------------------------------------------|--------------------------------------|
| 1    | 설치        | `sops --version`, `age --version`        | 3.13.3, v1.3.2                       |
| 2    | 암호화 범위 | `sops encrypt -i` 뒤 파일 보기           | 정한 키만 `ENC[...]`                 |
| 3    | 복호화      | `sops decrypt`                           | 원래 값                              |
| 4    | 상태        | `sops filestatus 파일`                   | `{"encrypted":true}`                 |
| 5    | 다른 사람   | 받는 사람 추가 뒤 그 키로 `decrypt`      | 성공                                 |
| 6    | 키 없음     | 기본 위치에 키가 없는 환경에서 `decrypt` | 종료 코드 128, `Recovery failed ...` |
| 7    | 변조 탐지   | 평문 값을 손으로 바꾼 뒤 `decrypt`       | 종료 코드 51, `MAC mismatch`         |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                                        | 원인                                             | 조치                                                       |
|-------------------------------------------------------------|--------------------------------------------------|------------------------------------------------------------|
| `error loading config: no matching creation rules found`    | `.sops.yaml`에 경로가 맞는 규칙 없음             | `path_regex` 확인·규칙 추가, 일회성은 `--config /dev/null` |
| `Recovery failed because no master key was able to decrypt` | 받는 사람 중 누구의 비밀키도 없음                | 키 파일 위치·`SOPS_AGE_KEY` 확인, 받는 사람 목록 확인      |
| `MAC mismatch`, 종료 코드 51                                | 파일을 sops 밖에서 고침(평문 값 포함), 병합 충돌 | Git에서 되돌린 뒤 `sops edit`으로 다시 수정                |
| `cannot use complex value in environment`                   | `exec-env`에 중첩 구조 파일                      | dotenv 파일로 분리하거나 `exec-file` 사용                  |
| 틀린 키 파일을 줬는데 복호화됨                              | 기본 위치의 키도 함께 읽음                       | 3절 참고. 시험은 기본 위치가 빈 환경에서                   |
| `.sops.yml`을 만들었는데 규칙이 안 먹음                     | 자동 탐색은 `.sops.yaml`만                       | 이름 변경 또는 `--config` 지정                             |

- `--ignore-mac`을 주면 MAC 불일치를 무시하고 복호화합니다(시험에서 종료 코드 0). 복구용으로만 쓰고, 왜 바뀌었는지 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Ansible Vault](./ansible_vault.md) — Ansible 안의 파일 암호화
- [HashiCorp Vault 개념](../../04_security/hardening/hashicorp_vault_concepts.md) — 서버형 비밀값 관리
- [Terraform](./terraform.md) — 상태 파일의 비밀값 다루기
- [Pulumi](./pulumi.md) — stack 설정의 비밀값 암호화

---

## 참고 자료

- SOPS Docs: [Introduction](https://getsops.io/docs/) · [age](https://getsops.io/docs/usage/identities/age/) · [.sops.yaml](https://getsops.io/docs/usage/identities/config-file/) · [Key management](https://getsops.io/docs/usage/key-management/) — ★★★☆☆
- GitHub: [getsops/sops releases](https://github.com/getsops/sops/releases) · [FiloSottile/age releases](https://github.com/FiloSottile/age/releases) — ★★★☆☆

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
