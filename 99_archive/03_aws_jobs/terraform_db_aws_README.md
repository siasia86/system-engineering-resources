# 91_resarch_test_20260617

Ubuntu 24.04 EC2 인스턴스에서 MySQL 설치 스크립트를 테스트하는 프로젝트입니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 인프라 구성](#2-인프라-구성) / [3. Security Group](#3-security-group)               |
| [4. 배포 방법](#4-배포-방법) / [5. 디스크 구성](#5-디스크-구성) / [6. 삭제 방법](#6-삭제-방법)             |

## 1. 개요

| 항목      | 값                                |
|-----------|-----------------------------------|
| 목적      | MySQL 설치 스크립트 테스트        |
| OS        | Ubuntu 24.04 LTS                  |
| 리전      | ap-northeast-2 (서울)             |
| 인스턴스  | t3.medium                         |
| VPC       | Default VPC (172.31.0.0/16)       |
| SSH 키    | Terraform으로 신규 생성           |
| EIP       | Terraform으로 신규 생성 (고정 IP) |
| 계정      | 01_re                             |
| Terraform | ~> 5.0 (AWS provider)             |

## 2. 인프라 구성

```
Default VPC (172.31.0.0/16)
└── EC2 (Ubuntu 24.04, t3.medium) -- 서브넷 자동 선택
    ├── EIP (고정 Public IP)
    ├── OS disk     /dev/xvda   20GB  (gp3)
    ├── data1 disk  /dev/xvdb   15GB  (gp3) -> /data1  (user_data 자동 마운트)
    ├── data2 disk  /dev/xvdc   16GB  (gp3) -> /data2  (user_data 자동 마운트)
    └── data3 disk  /dev/xvdd   17GB  (gp3) -> /data3  (user_data 자동 마운트)
```

user_data에서 EBS 디스크를 xfs로 포맷 후 `/data1~3`에 마운트하고 `/etc/fstab`에 등록합니다.

## 3. Security Group

| 방향     | 포트 | 프로토콜 | 허용 대상         | 용도      |
|----------|------|----------|-------------------|-----------|
| inbound  | 22   | TCP      | 112.185.196.55/32 | SSH 접속  |
| inbound  | 80   | TCP      | 0.0.0.0/0         | HTTP      |
| inbound  | 443  | TCP      | 0.0.0.0/0         | HTTPS     |
| outbound | all  | all      | 0.0.0.0/0         | 전체 허용 |

## 4. 배포 방법

```bash
cd /home/sjyun/03_aws/91_resarch_test_20260617

terraform init
terraform plan
terraform apply -auto-approve
```

SSH 접속 (apply 후 출력된 EIP로 접속):

```bash
ssh -i ./sjyun-mysql-test-key.pem ubuntu@<EIP>
```

🟡 `sjyun-mysql-test-key.pem` 은 `terraform apply` 시 로컬에 자동 생성됩니다.

## 5. 디스크 구성

| 장치      | 크기 | 마운트 | 용도                |
|-----------|------|--------|---------------------|
| /dev/xvda | 20GB | /      | OS                  |
| /dev/xvdb | 15GB | /data1 | MySQL 데이터 테스트 |
| /dev/xvdc | 16GB | /data2 | MySQL 데이터 테스트 |
| /dev/xvdd | 17GB | /data3 | MySQL 데이터 테스트 |

🟡 EBS 볼륨은 인스턴스 종료 시 자동 삭제(`delete_on_termination = true`)로 설정합니다.

## 6. 삭제 방법

```bash
terraform destroy -auto-approve
```

---

**작성일**: 2026-06-17

**마지막 업데이트**: 2026-06-17

© 2026 siasia86. Licensed under CC BY 4.0.
