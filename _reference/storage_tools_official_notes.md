---
name: storage-tools-official-notes
last_checked: 2026-08-18
sources:
  - https://man7.org/linux/man-pages/man8/lsblk.8.html
  - https://man7.org/linux/man-pages/man8/findmnt.8.html
  - https://man7.org/linux/man-pages/man8/blkid.8.html
  - https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html
  - https://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html
  - https://dev.yorhel.nl/ncdu/man
  - https://github.com/sysstat/sysstat
  - https://github.com/dstat-real/dstat
  - https://github.com/Atoptool/atop
  - https://nmon.sourceforge.net/pmwiki.php
  - https://github.com/axboe/fio
  - https://man7.org/linux/man-pages/man8/hdparm.8.html
  - https://github.com/smartmontools/smartmontools
  - https://github.com/linux-nvme/nvme-cli
---

# 저장장치 도구 공식 참조 노트

기존 참고 문서인 `iotop_official_notes.md`와 `ioping_official_notes.md`를 제외한 저장장치 도구의 공식 출처와 검증된 핵심 기능을 기록합니다.

## 1. 장치·마운트 확인

### `lsblk`

- 공식 매뉴얼: https://man7.org/linux/man-pages/man8/lsblk.8.html
- 블록 장치에 대한 정보를 목록 형태로 표시합니다.
- 장치와 파티션의 계층 구조, 파일시스템, UUID, 마운트 지점을 확인할 수 있습니다.
- `-f`는 파일시스템 관련 정보를 표시하고, `-o`는 출력 열을 선택합니다.

### `findmnt`

- 공식 매뉴얼: https://man7.org/linux/man-pages/man8/findmnt.8.html
- `/proc/self/mountinfo`, `/etc/mtab`, `/etc/fstab`의 마운트 정보를 표시하거나 검색합니다.
- 파일시스템 유형, 소스 장치, 마운트 지점과 옵션을 확인할 수 있습니다.
- `-t`는 파일시스템 유형, `-o`는 출력 열을 선택합니다.

### `blkid`

- 공식 매뉴얼: https://man7.org/linux/man-pages/man8/blkid.8.html
- 블록 장치의 콘텐츠와 메타데이터를 식별합니다.
- 파일시스템 유형, LABEL, UUID 같은 식별 정보를 조회할 수 있습니다.
- `-o`는 출력 형식을 선택하며, 장치 스캔은 권한에 따라 제한될 수 있습니다.

## 2. 공간 사용량 확인

### `df`

- 공식 매뉴얼: https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html
- 파일시스템별 사용 중인 공간과 사용 가능한 공간을 표시합니다.
- 인수를 지정하지 않으면 마운트된 모든 파일시스템의 정보를 표시합니다.
- `-h`는 사람이 읽기 쉬운 단위, `-T`는 파일시스템 유형을 표시합니다.

### `du`

- 공식 매뉴얼: https://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html
- 지정한 파일과 각 하위 디렉토리가 사용하는 파일시스템 공간을 추정합니다.
- `-h`는 사람이 읽기 쉬운 단위, `--max-depth`는 출력 깊이를 제한합니다.
- `-x`는 명령행 인수로 지정한 파일시스템 외부의 파일시스템을 건너뜁니다.

### `ncdu`

- 공식 프로젝트: https://dev.yorhel.nl/ncdu
- 공식 매뉴얼: https://dev.yorhel.nl/ncdu/man
- `du`와 유사한 디스크 사용량 정보를 curses 기반 대화형 화면으로 제공합니다.
- `-x`는 다른 파일시스템 경계를 넘지 않도록 합니다.
- 실제 파일시스템을 스캔할 때 브라우저에서 삭제 기능이 제공될 수 있으므로 삭제 옵션은 주의해서 사용합니다.

## 3. 프로세스·디바이스 I/O

### `pidstat`

- 공식 프로젝트: https://github.com/sysstat/sysstat
- 공식 매뉴얼: https://man7.org/linux/man-pages/man1/pidstat.1.html
- Linux task의 CPU·메모리·디바이스 I/O 통계를 보고합니다.
- `-d`는 task별 디바이스 I/O 통계를 표시하고, 간격과 횟수 인수로 샘플링을 제어합니다.

### `iostat`

- 공식 프로젝트: https://github.com/sysstat/sysstat
- 공식 매뉴얼: https://man7.org/linux/man-pages/man1/iostat.1.html
- 디바이스와 파티션의 CPU 및 I/O 통계를 보고합니다.
- `-x`는 확장 통계, `-z`는 활동이 없는 디바이스를 생략하며, 간격과 횟수 인수로 반복 측정을 수행합니다.
- `await`, `avgqu-sz`, `%util` 등은 확장 디바이스 통계에서 확인할 수 있습니다.

## 4. 종합 시스템 모니터링

### `dstat`

- 공식 저장소: https://github.com/dstat-real/dstat
- 공식 저장소의 최신 릴리스 API 확인 결과: `v0.7.4` (2019-05-22), 저장소는 archived 상태입니다.
- CPU, 디스크, 네트워크, 페이징, 시스템 통계를 함께 표시하는 자원 통계 도구입니다.
- 배포판별 패키지와 플러그인 제공 범위가 다를 수 있으므로 실제 설치 버전의 도움말을 확인해야 합니다.

### `atop`

- 공식 저장소: https://github.com/Atoptool/atop
- 공식 저장소의 최신 릴리스 API 확인 결과: `v2.13.0` (2026-07-19).
- CPU, 메모리, 스왑, 디스크, 네트워크와 프로세스 상태를 실시간으로 표시합니다.
- 장기 관찰을 위해 시스템 활동을 로그 파일에 기록하고 나중에 재생할 수 있습니다.

### `nmon`

- 공식 프로젝트: https://nmon.sourceforge.net/pmwiki.php
- CPU, 메모리, 디스크, 네트워크, 파일시스템 및 프로세스 관련 시스템 통계를 표시합니다.
- 인터랙티브 화면과 파일 기반 성능 기록 모드를 제공하며, 배포판·빌드에 따라 키와 기능이 다를 수 있습니다.
- 실제 사용 전 설치된 버전의 도움말과 화면 키를 확인합니다.

## 5. 성능 테스트

### `fio`

- 공식 저장소: https://github.com/axboe/fio
- 공식 저장소의 최신 릴리스 API 확인 결과: `fio-3.42` (2026-04-07).
- Flexible I/O Tester로 블록 I/O 부하를 생성하고 성능을 측정합니다.
- 블록 크기, 읽기·쓰기 방식, 큐 깊이, 작업자 수, 접근 패턴과 런타임을 작업 파일 또는 명령행 옵션으로 제어합니다.
- 블록 장치에 직접 쓰는 작업은 기존 데이터를 덮어쓸 수 있으므로 테스트 대상과 `--readonly` 여부를 먼저 확인합니다.

## 6. ATA/SATA 장치 정보와 테스트

### `hdparm`

- 공식 매뉴얼: https://man7.org/linux/man-pages/man8/hdparm.8.html
- ATA/SATA 장치의 커널 인터페이스를 조회하거나 설정하는 유틸리티입니다.
- `-I`는 장치 식별 정보를 표시하고, `-t`는 장치 읽기 타이밍, `-T`는 캐시 읽기 타이밍을 수행합니다.
- 설정 변경 옵션 중 일부는 데이터 손실 또는 장치·파일시스템 장애를 일으킬 수 있으므로 읽기 전용 조회와 변경 작업을 구분해야 합니다.

## 7. 저장장치 상태 확인

### `smartctl`

- 공식 저장소: https://github.com/smartmontools/smartmontools
- 공식 프로젝트: https://www.smartmontools.org/
- 공식 저장소의 최신 릴리스 API 확인 결과: `RELEASE_7_5` (2025-05-12).
- ATA/SATA, SCSI/SAS, NVMe 장치의 SMART 정보와 상태를 조회·모니터링합니다.
- `-H`는 건강 상태, `-a`는 장치의 지원 정보와 SMART 정보를 표시합니다.

### `nvme-cli`

- 공식 저장소: https://github.com/linux-nvme/nvme-cli
- 공식 저장소의 최신 릴리스 API 확인 결과: `v2.16` (2025-11-04).
- NVMe 장치를 관리하고 컨트롤러·네임스페이스 정보와 로그를 조회합니다.
- `nvme list`는 NVMe 장치 목록, `nvme smart-log`는 SMART 로그를 조회합니다.
- 세부 명령어 문서는 공식 저장소의 `Documentation/` 아래에 제공됩니다.

## 8. 검증 원칙

- 명령어와 옵션은 해당 도구의 공식 매뉴얼 또는 공식 저장소 문서에서 확인한 내용만 사용합니다.
- 설치 여부와 기능 지원 여부를 혼동하지 않습니다.
- 버전이나 배포판에 따라 출력 열·키·옵션이 달라질 수 있는 도구는 실제 설치 버전의 `--help`와 매뉴얼을 함께 확인합니다.
- 쓰기 테스트, 장치 설정 변경, 삭제 기능은 데이터 손실 또는 서비스 영향 가능성을 본문에 명시합니다.
