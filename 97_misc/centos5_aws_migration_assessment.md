# CentOS 5.11 i386 AWS 이전 가능성 평가

CentOS 5.11 i386(32-bit) 서버를 AWS로 이전할 수 있는지 모든 경로를 검토한 결과를 정리합니다.

## 목차

| 섹션                                                                                                                       |
|----------------------------------------------------------------------------------------------------------------------------|
| [1. 결론](#1-결론) / [2. 대상 서버 정보](#2-대상-서버-정보) / [3. 차단 사유 상세](#3-차단-사유-상세)                        |
| [4. 모든 경로 검토](#4-모든-경로-검토) / [5. 실현 가능한 방안](#5-실현-가능한-방안) / [6. 참고 자료](#6-참고-자료)           |

---

## 1. 결론

**CentOS 5.11 i386 상태 그대로는 AWS로 이전할 수 없습니다.**

| 경로                    | 가능 여부 | 차단 사유                              |
|-------------------------|-----------|----------------------------------------|
| VM Import/Export        | ❌        | 2026-04-01부터 i386 지원 종료          |
| AWS Marketplace AMI     | ❌        | CentOS 5 AMI 없음 (7 이상만 존재)     |
| Community AMI           | ❌        | CentOS 5 i386 AMI 없음                |
| 서울 리전 인스턴스 실행 | ❌        | t1/m1(32-bit 지원) 인스턴스 유형 없음  |
| 도쿄/버지니아 우회      | ❌        | t1/m1 존재하나 Import가 i386 거부      |

OS 마이그레이션(x86_64 전환) 선행 후 AWS 이전이 유일한 방법입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 대상 서버 정보

```
Linux Galaxy-Game 2.6.18-419.el5PAE #1 SMP Fri Feb 24 22:09:08 UTC 2017 i686 i686 i386 GNU/Linux
```

| 항목           | 값                         | 문제점                        |
|----------------|----------------------------|-------------------------------|
| OS             | CentOS 5.11                | EOL 2017-03-31                |
| 커널           | 2.6.18-419.el5PAE          | PAE = 32-bit + 확장 메모리    |
| 아키텍처       | i386 / i686                | 32-bit                        |
| 커널 빌드 날짜 | 2017-02-24                 | 마지막 업데이트               |
| 운영 환경      | IDC (Hyper-V 클러스터)     | I/O 경합 이슈 발생 중         |

### PAE 커널의 의미

- PAE(Physical Address Extension): 32-bit OS에서 4GB 이상 메모리 사용을 위한 확장
- OS 자체는 32-bit(i386), 메모리만 확장 접근
- AWS에서는 32-bit OS로 취급 → i386 제한 적용

[⬆ 목차로 돌아가기](#목차)

---

## 3. 차단 사유 상세

### 3.1 VM Import/Export i386 지원 종료

AWS 공식 문서 원문:

> "Starting from April 1, 2026, VM Import Export will stop supporting i386 architecture. Import and Export tasks will stop working for i386 OS versions. These OS versions include ... CentOS 5 (32-bit) ..."

| 항목             | 내용                                                  |
|------------------|-------------------------------------------------------|
| 시행일           | 2026-04-01                                            |
| 현재 상태        | **이미 시행 중** (2026-07-16 기준)                    |
| 영향 범위        | i386 아키텍처의 모든 Import/Export 작업               |
| 대상 OS          | CentOS 5/6, Debian 6/7, RHEL 5/6, Windows 2003/2008 등 |
| 출처             | docs.aws.amazon.com/vm-import/latest/userguide/prerequisites.html |

🟡 VM Import/Export**만** 종료된 것이며, 이미 AWS 위에서 실행 중인 i386 인스턴스를 강제 종료하는 것은 아닙니다. 하지만 새로 가져올 수 없으므로 신규 이전은 불가합니다.

### 3.2 서울 리전(ap-northeast-2) 인스턴스 유형 부재

32-bit OS를 실행할 수 있는 인스턴스 유형(t1.micro, m1.small 등)이 서울 리전에 존재하지 않습니다.

```
# API 확인 결과 (2026-07-16)
$ aws ec2 describe-instance-type-offerings \
    --filters "Name=instance-type,Values=t1.micro,m1.small,m1.medium,m1.large" \
    --region ap-northeast-2

결과: 0건 (빈 응답)
```

| 리전             | t1/m1 존재 | 비고                     |
|------------------|------------|--------------------------|
| ap-northeast-2 (서울) | ❌    | 32-bit 인스턴스 실행 불가 |
| ap-northeast-1 (도쿄) | ✅    | t1.micro, m1.small/medium/large |
| us-east-1 (버지니아)  | ✅    | 동일                     |

도쿄/버지니아에 t1/m1이 있지만, VM Import가 i386을 거부하므로 이미지를 넣을 방법이 없습니다.

### 3.3 AMI 부재

| 검색 대상        | 검색 조건                          | 결과 |
|------------------|------------------------------------|------|
| Marketplace      | `CentOS*5*` + i386                 | 0건  |
| Marketplace      | `CentOS*5*` (모든 아키텍처)        | 0건  |
| Community        | architecture=i386 + CentOS         | 0건  |
| Community        | architecture=i386 (전체)           | 3건 (PV-GRUB, OL6.9, DL AMI 오류) |

AWS Marketplace에 존재하는 CentOS AMI는 **버전 7 이상**만 있으며, 아키텍처는 x86_64 또는 arm64만 존재합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 모든 경로 검토

### 4.1 VM Import/Export (정규 경로)

```
IDC (Hyper-V VHD) → Export → S3 업로드 → VM Import → AMI → EC2 실행
```

- ❌ 2026-04-01부터 i386 Import 거부
- CentOS 5 x86_64라면 여전히 가능하지만, 이 서버는 i386

### 4.2 수동 디스크 복제 (EBS 스냅샷)

```
IDC 디스크 → dd → raw 이미지 → S3 업로드 → EBS 스냅샷 → register-image → AMI
```

- 🟡 이론상 AMI 등록은 가능할 수 있음
- ❌ 실행할 인스턴스 유형이 서울 리전에 없음
- ❌ 도쿄에서 실행하더라도 PV(Paravirtual) 부팅 필요 → 커널 호환 문제

### 4.3 Marketplace / Community AMI 사용

- ❌ CentOS 5 AMI 자체가 존재하지 않음

### 4.4 EC2에서 신규 CentOS 5 설치

- ❌ ISO 부팅 불가 (EC2는 ISO 직접 부팅 미지원)
- ❌ PXE/네트워크 부팅으로 CentOS 5 설치 → 이론상 가능하나 비현실적
- ❌ 설치해도 32-bit 인스턴스 유형 없음

### 4.5 컨테이너로 실행

```
CentOS 5 i386 → Docker 컨테이너 (i386 userspace) → EC2 x86_64 호스트
```

- 🟡 Docker `--platform linux/386`으로 32-bit userspace 실행 가능
- ❌ 커널은 호스트(x86_64)를 사용 → 커널 2.6.18 의존 앱은 호환 문제 가능
- 🟡 단순 앱이라면 가능하지만 게임 서버의 경우 검증 필요

### 4.6 경로 판정 종합

| 경로               | 기술적 가능성 | 현실성 | 판정 |
|--------------------|---------------|--------|------|
| VM Import          | ❌            | —      | 불가 |
| 수동 EBS 등록      | 🟡            | ❌     | 불가 |
| Marketplace AMI    | ❌            | —      | 불가 |
| 신규 설치          | ❌            | —      | 불가 |
| Docker 컨테이너    | 🟡            | 🟡     | 제한적 |
| OS 전환 후 Import  | ✅            | ✅     | **유일한 방법** |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실현 가능한 방안

### 방안 A: OS 마이그레이션 선행 → AWS 이전 (권장)

```
[IDC]                                [AWS]
Galaxy-Game (CentOS 5 i386)
       │
       v  (OS 마이그레이션)
Galaxy-Game (Rocky 9 x86_64)
       │
       v  (VM Import 또는 신규 구축)
                                   EC2 (Rocky 9, t3/m5)
                                   EBS gp3 (I/O 격리)
```

| 단계 | 작업                              | 소요     | 위험도 |
|------|-----------------------------------|----------|--------|
| 1    | 게임 서버 바이너리 아키텍처 확인  | 1일      | 낮음   |
| 2    | 64-bit 호환 테스트 (glibc.i686)   | 1~2주    | 중간   |
| 3    | Rocky 9 x86_64로 OS 교체          | 1~2주    | 높음   |
| 4    | VM Export → S3 → VM Import        | 1~3일    | 낮음   |
| 5    | EC2 검증 및 성능 테스트           | 1주      | 낮음   |
| 6    | DNS/네트워크 전환                 | 1일      | 중간   |

**총 소요: 1~3개월**

#### 바이너리 호환성 확인

```bash
# 게임 서버 바이너리 아키텍처 확인
file /path/to/game_server_binary

# 32-bit ELF라면 x86_64 OS에서 multilib으로 실행 가능
# 출력 예: ELF 32-bit LSB executable, Intel 80386
```

32-bit 바이너리를 x86_64 OS에서 실행하려면:

```bash
# Rocky 9 / AlmaLinux 9
dnf install -y glibc.i686 libstdc++.i686 zlib.i686

# 실행 테스트
./game_server_binary
```

### 방안 B: AWS 신규 구축 + 데이터 이전

OS 전환과 AWS 이전을 동시에 진행합니다.

```
[IDC]                                [AWS]
Galaxy-Game (CentOS 5 i386)          EC2 (Rocky 9 x86_64) 신규 구축
       │                                    ^
       └── rsync 데이터 + 설정 ─────────────┘
```

| 장점                           | 단점                                 |
|--------------------------------|--------------------------------------|
| 깨끗한 환경                    | 게임 서버 재설치/재빌드 필요         |
| 최신 보안 패치 적용            | 32-bit 바이너리 호환 검증 필요       |
| EBS gp3 I/O 격리 보장          | 전환 기간 다운타임 발생 가능         |
| 최신 인스턴스 유형 사용 가능   | 설정 차이로 인한 예기치 못한 문제    |

### 방안 C: IDC 잔류 + I/O 경합 완화 (임시)

AWS 이전 전까지 IDC에서 I/O 경합을 완화하는 임시 조치입니다.

| 우선순위 | 조치                                   | 효과    |
|----------|----------------------------------------|---------|
| 1        | Galaxy-Game VHD를 별도 물리 디스크 분리 | ★★★★★   |
| 2        | Storage QoS Min IOPS 보장              | ★★★★☆   |
| 3        | noisy neighbor VM에 Max IOPS 제한      | ★★★★☆   |
| 4        | I/O timeout 120초 유지 확인            | ★★☆☆☆   |

### 권장 실행 순서

```
[즉시]     IDC I/O 완화 (방안 C: VHD 분리 + QoS)
              │
              v  (1~3개월 병행)
[병행]     OS 마이그레이션 (방안 A 또는 B)
              │  - 바이너리 호환 검증
              │  - Rocky 9 x86_64 전환
              │  - 스테이징 테스트
              v
[완료 후]  AWS 이전 (VM Import 또는 신규 구축)
              │
              v
           EC2 + EBS gp3 (VM별 I/O 완전 격리)
```

### AWS 이전 후 인스턴스 권장

| 항목               | 권장값                              | 이유                         |
|--------------------|-------------------------------------|------------------------------|
| 인스턴스 유형      | t3.medium 이상 또는 m5.large        | 게임 서버 워크로드           |
| EBS 유형           | gp3                                 | IOPS/처리량 독립 설정 가능   |
| EBS IOPS           | 3,000~6,000 (gp3 기본 3,000 포함)   | I/O 격리 보장                |
| EBS 처리량         | 125~250 MB/s                        | 게임 로그 쓰기 대응          |
| 배치 그룹          | 불필요 (단일 인스턴스)              |                              |

🟡 gp3는 VM별 독립 IOPS를 할당하므로 Hyper-V 클러스터에서 발생한 noisy neighbor 문제가 근본적으로 해소됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 참고 자료

- VM Import Prerequisites: [docs.aws.amazon.com](https://docs.aws.amazon.com/vm-import/latest/userguide/prerequisites.html) — ★★★☆☆
- EC2 Instance Types: [docs.aws.amazon.com](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html) — ★★★☆☆
- EC2 Previous Generation: [aws.amazon.com](https://aws.amazon.com/ec2/previous-generation/) — ★★☆☆☆
- EBS Volume Types: [docs.aws.amazon.com](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html) — ★★★☆☆
- [_reference/hyperv_io_contention_notes.md](../_reference/hyperv_io_contention_notes.md)
- [97_misc/hyperv_io_contention_legacy_vm.md](hyperv_io_contention_legacy_vm.md)

---

**작성일**: 2026-07-16

**마지막 업데이트**: 2026-07-16

© 2026 siasia86. Licensed under CC BY 4.0.
