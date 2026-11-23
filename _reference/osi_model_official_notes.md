---
name: osi-model-official-notes
description: OSI 기본 참조 모델(ITU-T X.200)과 인터넷 프로토콜 계층(RFC 1122)의 대응 정리.
tags:
  - networking
  - osi
  - tcp-ip
  - rfc
last_checked: 2026-11-23
sources:
  - https://www.itu.int/rec/T-REC-X.200-199407-I/en
  - https://www.rfc-editor.org/rfc/rfc1122
---

# OSI 모델 공식 자료 참조 노트

## 1. 기준 문서

| 문서                | 내용                                                                                                                       |
|---------------------|----------------------------------------------------------------------------------------------------------------------------|
| ITU-T X.200 (07/94) | Information technology - Open Systems Interconnection - Basic Reference Model: The basic model. ISO/IEC 7498-1과 같은 내용 |
| RFC 1122 (1989-10)  | Requirements for Internet Hosts -- Communication Layers. 인터넷 프로토콜 계층 정의                                         |

## 2. OSI 7계층 (X.200)

| 번호 | 계층         |
|------|--------------|
| 7    | Application  |
| 6    | Presentation |
| 5    | Session      |
| 4    | Transport    |
| 3    | Network      |
| 2    | Data Link    |
| 1    | Physical     |

## 3. 인터넷 프로토콜 계층 (RFC 1122 1.1.3)

- 계층은 Application, Transport, Internet, Link 넷이며, 호스트는 각 계층에서 적어도 하나의 프로토콜을 구현해야 합니다.
- 원문 요지: 인터넷의 애플리케이션 계층은 OSI 참조 모델의 위 두 계층(Presentation, Application)의 기능을 합친 것이고, 인터넷 계열은 애플리케이션 계층을 더 나누지 않습니다. 일부 프로토콜은 내부에 하위 계층을 둡니다.
- Link 계층은 직접 연결된 네트워크와 통신하는 프로토콜(media-access layer)이며 네트워크 종류만큼 다양합니다.

## 4. 정리할 때 주의

- OSI는 참조 모델이고, 실제 인터넷 프로토콜은 RFC 1122의 4계층을 따릅니다. TLS처럼 어느 한 OSI 계층에 정확히 들어맞지 않는 프로토콜이 있어, 계층 배치는 "대응"으로 설명합니다.
- X.200 본문 PDF는 ITU 사이트에서 받을 수 있으며, 이 노트는 표제·계층 이름만 인용했습니다.
