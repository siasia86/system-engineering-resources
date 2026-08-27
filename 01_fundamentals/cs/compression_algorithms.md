# 압축 알고리즘

## 목차

| 단계     | 섹션                                                                                                                             |
|----------|----------------------------------------------------------------------------------------------------------------------------------|
| 원리     | [1. 압축의 기본 원리](#1-압축의-기본-원리) / [2. 허프만 코딩](#2-허프만-코딩) / [3. 허프만 구현 (Python)](#3-허프만-구현-python) |
| 알고리즘 | [4. LZ77과 사전 기반 압축](#4-lz77과-사전-기반-압축) / [5. DEFLATE](#5-deflate)                                                  |
| 포맷     | [6. gzip](#6-gzip) / [7. ZIP](#7-zip) / [8. Zstandard](#8-zstandard)                                                             |
| 실무     | [9. 도구 비교 벤치마크](#9-도구-비교-벤치마크) / [10. 실무 선택 기준](#10-실무-선택-기준) / [11. 명령어 요약](#11-명령어-요약)   |

---

## 1. 압축의 기본 원리

무손실 압축은 두 단계로 나뉩니다. 먼저 데이터에서 반복되는 부분을 찾아 짧은 참조로 바꾸고, 그 결과로 남은 심볼을 출현 빈도에 따라 서로 다른 길이의 비트로 바꿉니다.

```
Input bytes
    |
    v
[ Modeling ]         duplicate elimination : LZ77, LZ78, BWT
    |                output = literals + <length, distance> pairs
    v
[ Entropy coding ]   symbol -> variable-length bits : Huffman, FSE/ANS
    |
    v
Compressed bytes
```

1단계는 중복 제거, 2단계는 빈도 편중 활용입니다. gzip, zstd, brotli 모두 이 구조를 따르며 각 단계에 어떤 알고리즘을 쓰는지가 다릅니다.

### 무손실과 손실

| 구분   | 복원                  | 적용 대상               | 예시                |
|--------|-----------------------|-------------------------|---------------------|
| 무손실 | 원본과 비트 단위 동일 | 텍스트, 실행 파일, 백업 | gzip, zstd, xz, ZIP |
| 손실   | 원본과 다름           | 이미지, 음성, 영상      | JPEG, MP3, H.264    |

이 문서는 무손실 압축만 다룹니다.

### 엔트로피 하한

심볼당 평균 비트 수는 정보원의 엔트로피보다 작아질 수 없습니다.

```
H = - sum( p(i) * log2( p(i) ) )     bit/symbol
```

> 엔트로피(Entropy): 정보원이 심볼 하나를 낼 때 담기는 평균 정보량입니다.
> 단위는 bit/symbol 이며 무손실 압축의 이론적 하한을 규정합니다.
> 편중이 심할수록 값이 작아지고 균등 분포일 때 최대가 됩니다.

### 모든 데이터를 압축할 수는 없음

길이 n 비트 입력은 2^n 가지인데 n 비트보다 짧은 출력은 그보다 적습니다. 따라서 모든 입력을 줄이는 무손실 알고리즘은 존재하지 않습니다. DEFLATE 규격도 이 점을 명시합니다.

> A simple counting argument shows that no lossless compression
> algorithm can compress every possible input data set. For the
> format defined here, the worst case expansion is 5 bytes per 32K-
> byte block, i.e., a size increase of 0.015% for large data sets.
>
> — RFC 1951 §1.1

JPEG, MP4, `.zst` 처럼 이미 압축된 데이터를 다시 압축하면 크기가 늘어납니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 허프만 코딩

1952년 David Huffman 이 발표한 최적 접두어 부호 생성 알고리즘입니다. 빈도가 높은 심볼에 짧은 코드를, 낮은 심볼에 긴 코드를 배정합니다.

> 접두어 부호(Prefix-free code): 어떤 코드도 다른 코드의 접두어가 되지 않는 부호입니다.
> 구분자 없이 비트열을 앞에서부터 읽어도 유일하게 복호할 수 있습니다.

### 알고리즘

```
1. 심볼별 출현 빈도 계산
2. 각 심볼을 리프 노드로 만들어 최소 힙에 삽입
3. 빈도가 가장 작은 노드 2개를 꺼내 부모 노드로 합침 (부모 빈도 = 두 자식 합)
4. 부모 노드를 힙에 다시 삽입
5. 노드가 1개 남을 때까지 3~4 반복
6. 루트에서 내려가며 왼쪽 간선에 0, 오른쪽 간선에 1 부여
```

힙 연산이 심볼 수만큼 반복되므로 시간 복잡도는 O(n log n) 입니다. 3단계에서 최소 두 개를 뽑는 데 최소 힙(우선순위 큐)을 쓰는 것이 핵심입니다.

### 예시: `abracadabra`

빈도는 `a` 5, `b` 2, `r` 2, `c` 1, `d` 1 입니다. 트리를 구성하면 다음과 같습니다.

```
root (11)
├── 0 ── a (5)
└── 1 ── node (6)
    ├── 0 ── node (2)
    │   ├── 0 ── c (1)
    │   └── 1 ── d (1)
    └── 1 ── node (4)
        ├── 0 ── b (2)
        └── 1 ── r (2)
```

| 심볼 | 빈도 | 허프만 코드 | 코드 길이 |
|------|------|-------------|-----------|
| `a`  | 5    | `0`         | 1         |
| `b`  | 2    | `110`       | 3         |
| `r`  | 2    | `111`       | 3         |
| `c`  | 1    | `100`       | 3         |
| `d`  | 1    | `101`       | 3         |

가장 빈번한 `a` 가 1비트, 나머지가 3비트를 받습니다. 인코딩 결과는 다음과 같습니다.

```
a b   r   a c   a d   a b   r   a
0 110 111 0 100 0 101 0 110 111 0    -> 23 bit
```

| 항목             | 값                  |
|------------------|---------------------|
| 입력 길이        | 11 심볼             |
| 고정 길이 인코딩 | 88 bit (8 bit × 11) |
| 허프만 인코딩    | 23 bit              |
| 압축률           | 3.83x               |
| 엔트로피 H       | 2.0404 bit/symbol   |
| 평균 코드 길이 L | 2.0909 bit/symbol   |

### 최적성과 한계

허프만 부호는 심볼 단위 부호 중 평균 길이가 최소임이 증명되어 있고, 평균 코드 길이 L 은 다음 범위에 들어갑니다.

```
H <= L < H + 1
```

위 예시에서 H = 2.0404, L = 2.0909 로 이 범위를 만족합니다.

한계는 심볼당 비트 수가 정수라는 점입니다. 출현 확률이 0.9인 심볼의 이론적 정보량은 약 0.152 bit 이지만 허프만은 최소 1비트를 배정합니다. 이 손실을 없애려면 분수 비트를 표현할 수 있는 산술 부호나 ANS 계열이 필요하며, zstd 가 쓰는 FSE 가 후자에 해당합니다.

### Canonical Huffman

트리 구조를 그대로 전송하면 오버헤드가 큽니다. DEFLATE 는 코드 자체가 아니라 심볼별 코드 길이만 보내고, 수신 측이 규칙에 따라 코드를 복원합니다.

> Given this rule, we can define the Huffman code for an alphabet
> just by giving the bit lengths of the codes for each symbol of
> the alphabet in order; this is sufficient to determine the
> actual codes.
>
> — RFC 1951 §3.2.2

[⬆ 목차로 돌아가기](#목차)

---

## 3. 허프만 구현 (Python)

최소 힙 기반 구현입니다. 아래 코드는 실행 검증을 마쳤습니다.

```python
#!/usr/bin/env python3
"""huffman.py - 허프만 코드표 생성 및 인코딩/디코딩"""

import heapq
from collections import Counter


def huffman_codes(text):
    """문자 빈도로 허프만 코드표를 생성합니다."""
    freq = Counter(text)
    if len(freq) == 1:                       # 단일 심볼 예외 처리
        return {next(iter(freq)): "0"}

    # (빈도, 순번, {심볼: 코드}) — 순번은 빈도 동률 시 비교 안정성 확보용
    heap = [(w, i, {c: ""}) for i, (c, w) in enumerate(freq.items())]
    heapq.heapify(heap)
    seq = len(heap)

    while len(heap) > 1:
        w1, _, m1 = heapq.heappop(heap)
        w2, _, m2 = heapq.heappop(heap)
        merged = {c: "0" + b for c, b in m1.items()}
        merged.update({c: "1" + b for c, b in m2.items()})
        heapq.heappush(heap, (w1 + w2, seq, merged))
        seq += 1

    return heap[0][2]


def encode(text, codes):
    """코드표로 비트 문자열을 생성합니다."""
    return "".join(codes[c] for c in text)


def decode(bits, codes):
    """접두어 부호 특성을 이용해 비트 문자열을 복호합니다."""
    rev = {v: k for k, v in codes.items()}
    buf, out = "", []
    for bit in bits:
        buf += bit
        if buf in rev:
            out.append(rev[buf])
            buf = ""
    return "".join(out)


def group(bits, n=4):
    """가독성을 위해 비트 문자열을 n비트 단위로 끊습니다."""
    return " ".join(bits[i:i + n] for i in range(0, len(bits), n))


if __name__ == "__main__":
    text = "abracadabra"
    codes = huffman_codes(text)
    bits = encode(text, codes)
    print("코드표   :", {c: codes[c] for c in sorted(codes)})
    print("인코딩   :", group(bits), f"({len(bits)} bit)")
    print("복호 검증:", decode(bits, codes) == text)
    print("압축률   :", f"{len(text) * 8 / len(bits):.2f}x")
```

실행 결과입니다.

```
코드표   : {'a': '0', 'b': '110', 'c': '100', 'd': '101', 'r': '111'}
인코딩   : 0110 1110 1000 1010 1101 110 (23 bit)
복호 검증: True
압축률   : 3.83x
```

🟡 위 구현은 개념 확인용입니다. 실제 파일 압축에는 비트 패킹, 코드표 직렬화, 스트리밍 처리가 추가로 필요하므로 `zlib`, `zstandard` 같은 검증된 라이브러리를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. LZ77과 사전 기반 압축

허프만이 심볼 빈도를 다루는 반면, LZ 계열은 반복되는 문자열 자체를 제거합니다. 1977년 Jacob Ziv 와 Abraham Lempel 이 발표했습니다.

### 동작 방식

이미 지나간 데이터를 사전으로 삼아, 반복 구간을 `<길이, 뒤로 이동할 거리>` 쌍으로 바꿉니다.

```
Input : a b c a b c a b c d
                    ^ current position
        <-- window -->

Output: a b c <length=6, distance=3> d

  literal a, b, c   : 처음 등장하므로 그대로 출력
  <6, 3>            : 3바이트 앞에서 6바이트를 복사
  literal d         : 처음 등장
```

거리가 길이보다 짧아도 됩니다. 위 예처럼 3바이트 뒤를 참조해 6바이트를 복사하면 복사 중에 방금 쓴 바이트를 다시 읽으므로 반복 패턴이 확장됩니다.

### 계열 비교

| 알고리즘 | 발표 | 핵심 아이디어                               | 대표 구현                  |
|----------|------|---------------------------------------------|----------------------------|
| LZ77     | 1977 | 슬라이딩 윈도우 + `<length, distance>` 참조 | DEFLATE, zstd, LZ4, brotli |
| LZ78     | 1978 | 명시적 사전 구축 + 사전 인덱스 참조         | -                          |
| LZW      | 1984 | LZ78 변형, 사전을 출력에 싣지 않음          | GIF, 구 UNIX `compress`    |
| BWT      | 1994 | 블록 정렬로 같은 문자를 인접 배치           | bzip2                      |

실무 포맷은 대부분 LZ77 계열을 쓰고, 그 출력을 엔트로피 코딩으로 한 번 더 줄입니다.

```
gzip   : LZ77 + Huffman
zstd   : LZ77 + Huffman(literals) + FSE(sequences)
brotli : LZ77 + Huffman + static dictionary
xz     : LZMA (LZ77 + range coder)
bzip2  : BWT + MTF + Huffman
```

> BWT(Burrows-Wheeler Transform): 블록 내 문자열을 회전·정렬해 같은 문자가
> 인접하도록 재배치하는 가역 변환입니다. 변환 자체는 압축이 아니지만
> 후속 엔트로피 코딩의 효율을 높입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. DEFLATE

RFC 1951 (P. Deutsch, 1996-05) 로 규격화된 압축 방식입니다. LZ77 로 중복을 제거하고 그 결과를 허프만 부호로 압축합니다. gzip, ZIP, PNG, HTTP `Content-Encoding: gzip` 이 모두 이 방식을 씁니다.

### 파라미터

| 파라미터        | 값                              | 근거            |
|-----------------|---------------------------------|-----------------|
| 슬라이딩 윈도우 | 32 KB (32,768 byte)             | RFC 1951 §1.1   |
| 최소 일치 길이  | 3 byte                          | RFC 1951 §3.2.5 |
| 최대 일치 길이  | 258 byte                        | RFC 1951 §1.1   |
| 최대 참조 거리  | 32 KB                           | RFC 1951 §1.1   |
| 최악 팽창률     | 32 KB 블록당 5 byte (약 0.015%) | RFC 1951 §1.1   |

윈도우가 32 KB 로 고정되어 있어서 그보다 멀리 떨어진 중복은 찾지 못합니다. 대용량 파일에서 zstd 나 xz 가 유리한 주된 이유입니다.

### 블록 타입

데이터는 블록 단위로 처리되며 각 블록 앞에 `BFINAL` 1비트와 `BTYPE` 2비트가 붙습니다.

| BTYPE | 의미             | 용도                              |
|-------|------------------|-----------------------------------|
| `00`  | 무압축 (stored)  | 이미 압축된 데이터, 팽창 방지     |
| `01`  | 고정 허프만 코드 | 짧은 데이터, 트리 전송 비용 회피  |
| `10`  | 동적 허프만 코드 | 일반적인 경우, 트리를 블록에 포함 |
| `11`  | 예약 (오류)      | 사용 금지                         |

`00` 이 존재하기 때문에 최악의 경우에도 팽창이 블록당 5바이트로 제한됩니다.

### 고정 허프만 코드

`BTYPE=01` 에서 쓰는 코드 길이는 규격에 고정되어 있습니다.

| 리터럴/길이 값 | 코드 비트 수 | 코드 범위                 |
|----------------|--------------|---------------------------|
| 0 - 143        | 8            | `00110000` ~ `10111111`   |
| 144 - 255      | 9            | `110010000` ~ `111111111` |
| 256 - 279      | 7            | `0000000` ~ `0010111`     |
| 280 - 287      | 8            | `11000000` ~ `11000111`   |

값 256 은 블록 종료 표시이며 257 이상은 일치 길이를 나타냅니다.

### 래퍼 비교

DEFLATE 는 압축 데이터 본체만 정의하므로, 실제 파일에는 헤더와 무결성 검사를 추가한 래퍼가 씌워집니다.

| 래퍼        | 규격     | 헤더         | 무결성 검사       | 주 용도                  |
|-------------|----------|--------------|-------------------|--------------------------|
| raw deflate | RFC 1951 | 없음         | 없음              | ZIP 엔트리, PNG `IDAT`   |
| zlib        | RFC 1950 | 2 byte       | Adler-32 (4 byte) | HTTP `deflate`, PNG, PDF |
| gzip        | RFC 1952 | 10 byte 이상 | CRC-32 (4 byte)   | 파일 압축, HTTP `gzip`   |

> Adler-32: CRC-32 보다 계산이 빠른 체크섬입니다. 오류 검출력은 CRC-32 보다
> 낮지만 스트리밍 환경에서 부담이 적어 zlib 래퍼가 채택했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. gzip

RFC 1952 (P. Deutsch, 1996-05) 가 정의하는 파일 포맷입니다. 압축 알고리즘은 DEFLATE 이고, gzip 은 그 위에 헤더와 트레일러를 붙인 컨테이너입니다.

### 파일 구조

```
 0     1     2     3     4  5  6  7     8     9
+-----+-----+-----+-----+-----------+-----+-----+
| ID1 | ID2 | CM  | FLG |   MTIME   | XFL | OS  |   header (10 byte)
+-----+-----+-----+-----+-----------+-----+-----+
| [FEXTRA] [FNAME] [FCOMMENT] [FHCRC]           |   optional fields
+-----------------------------------------------+
|            deflate compressed data            |   RFC 1951
+-----------------------------------------------+
|         CRC32          |         ISIZE        |   trailer (8 byte)
+------------------------+----------------------+
```

### 헤더 및 트레일러 필드

| 필드    | 크기   | 값 / 의미                                         |
|---------|--------|---------------------------------------------------|
| `ID1`   | 1 byte | 고정 `0x1f`                                       |
| `ID2`   | 1 byte | 고정 `0x8b`                                       |
| `CM`    | 1 byte | 압축 방식. `8` = deflate (0~7 예약)               |
| `FLG`   | 1 byte | `FTEXT`/`FHCRC`/`FEXTRA`/`FNAME`/`FCOMMENT` 비트  |
| `MTIME` | 4 byte | 원본 파일 수정 시각 (Unix time)                   |
| `XFL`   | 1 byte | 압축 강도 힌트 (`2` = 압축 우선, `4` = 속도 우선) |
| `OS`    | 1 byte | 생성 OS 종류                                      |
| `CRC32` | 4 byte | 비압축 원본 데이터의 CRC-32                       |
| `ISIZE` | 4 byte | 비압축 원본 크기 modulo 2^32                      |

### 실측 확인

`hello compression` 18바이트를 압축한 결과입니다.

```
$ echo "hello compression" > a.txt && gzip -c a.txt > a.gz

$ xxd -l 8 a.gz
00000000: 1f8b 0808 4e9b 8f6a                      ....N..j
          ^^^^ ^^   ^^   ^^^^^^^^^
          magic CM=8 FLG=8(FNAME)  MTIME

$ tail -c 8 a.gz | xxd
00000000: 9ecb 3eb2 1200 0000                      ..>.....
          ^^^^^^^^^ ^^^^^^^^^
          CRC32     ISIZE = 0x12 = 18
          (little-endian 0xb23ecb9e)

$ stat -c%s a.txt
18
$ python3 -c "import zlib;print(hex(zlib.crc32(open('a.txt','rb').read())))"
0xb23ecb9e
```

`ISIZE` 가 원본 크기 18과, `CRC32` 가 직접 계산한 값과 일치합니다.

### 압축 레벨

`-1` 부터 `-9` 까지이며 기본값은 `-6` 입니다. 벤치마크에서 확인했듯 `-9` 는 압축 속도를 크게 희생하면서 크기는 소폭만 줄입니다.

### 한계

`ISIZE` 가 32비트이므로 원본 크기를 modulo 2^32 로만 기록합니다. 4 GB 이상 파일에서는 `gzip -l` 이 실제와 다른 크기를 보고합니다. 또한 단일 DEFLATE 스트림이라 중간부터 해제할 수 없고 병렬 처리도 불가능합니다. 병렬화가 필요하면 여러 멤버로 나눠 쓰는 `pigz` 를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. ZIP

1989년 PKWARE 가 만든 아카이브 포맷으로, 규격은 APPNOTE.TXT 로 공개되어 있습니다. 이 문서 기준은 버전 6.3.10 (2022-11-01) 입니다.

### 구조

gzip 과 달리 아카이브와 압축이 한 포맷에 통합되어 있고, 파일마다 개별적으로 압축됩니다.

```
+----------------------------------------+
| Local File Header    (50 4b 03 04)     |  file 1
| File Data            (compressed)      |
+----------------------------------------+
| Local File Header    (50 4b 03 04)     |  file 2
| File Data            (compressed)      |
+----------------------------------------+
| Central Directory    (50 4b 01 02)     |  entry list + offsets
+----------------------------------------+
| End of Central Dir   (50 4b 05 06)     |
+----------------------------------------+
```

Central directory 가 파일 말미에 있어서 목록만 필요할 때 전체를 읽지 않아도 됩니다. 특정 파일 하나만 꺼낼 때도 offset 으로 바로 접근합니다.

```
$ xxd -l 8 a.zip
00000000: 504b 0304 0a00 0000                      PK......
          ^^^^^^^^^
          0x04034b50 (little-endian) = "PK" + 0x03 0x04
```

### 압축 방식 코드

각 엔트리 헤더의 2바이트 필드로 방식을 지정합니다.

| 코드 | 압축 방식       | 비고                               |
|------|-----------------|------------------------------------|
| `0`  | Stored (무압축) | 이미 압축된 파일 포함 시           |
| `8`  | Deflated        | 사실상 표준. 지원 범위가 가장 넓음 |
| `12` | BZIP2           | 호환성 제한적                      |
| `14` | LZMA            | 호환성 제한적                      |
| `93` | Zstandard       | 코드 `20` 은 deprecated, `93` 사용 |
| `95` | XZ              | 호환성 제한적                      |

방식을 엔트리별로 다르게 둘 수 있어서, 이미 압축된 파일은 `0`(stored) 으로 넣고 나머지는 `8`(deflated) 로 넣는 조합이 가능합니다.

### `tar.gz` 와의 구조 차이

| 항목             | `tar.gz`                             | ZIP                            |
|------------------|--------------------------------------|--------------------------------|
| 압축 단위        | 아카이브 전체를 단일 스트림으로 압축 | 파일별 개별 압축               |
| 중복 제거 범위   | 파일 경계를 넘어 적용                | 파일 내부로 한정               |
| 개별 파일 추출   | 앞부분부터 순차 해제 필요            | central directory 로 직접 접근 |
| 파일 목록 조회   | 전체 해제 필요                       | 말미 central directory 만 읽음 |
| 부분 손상 영향   | 손상 지점 이후 전체 손실             | 해당 엔트리만 손실             |
| POSIX 메타데이터 | 소유자·권한·심볼릭 링크 보존         | 구현·확장 필드 의존            |

파일이 많고 서로 비슷할 때는 `tar.gz` 가 압축률에서 유리합니다. 파일 경계를 넘어 중복을 찾기 때문입니다. 반대로 특정 파일만 자주 꺼내야 하면 ZIP 이 유리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. Zstandard

Yann Collet 이 개발한 압축 포맷으로, RFC 8478 (2018-10) 로 문서화된 뒤 RFC 8878 (2021-02) 이 이를 대체했습니다. 설계 목표는 gzip 수준의 속도에서 더 높은 압축률, 그리고 압축률과 무관하게 빠른 해제입니다.

### 프레임 구조

```
+--------------------+------------+
| Magic_Number       | 4 bytes    |   0xFD2FB528 (little-endian)
+--------------------+------------+
| Frame_Header       | 2-14 bytes |
+--------------------+------------+
| Data_Block         | n bytes    |
+--------------------+------------+
| [More Data_Blocks] |            |
+--------------------+------------+
| [Content_Checksum] | 0-4 bytes  |   XXH64 lower 32 bits
+--------------------+------------+
```

```
$ xxd -l 8 a.zst
00000000: 28b5 2ffd 2412 9100                      (./.$...
          ^^^^^^^^^
          28 b5 2f fd = 0xFD2FB528 (little-endian)
```

### 엔트로피 코딩

zstd 는 데이터 종류에 따라 두 가지 엔트로피 코더를 나눠 씁니다.

| 구성 요소       | 엔트로피 코딩 | 비고                                                   |
|-----------------|---------------|--------------------------------------------------------|
| Literals        | 허프만 부호   | 이전 블록 트리 재사용 가능 (`Treeless_Literals_Block`) |
| Literals length | FSE           | `Repeat_Mode` 로 테이블 재사용 가능                    |
| Match length    | FSE           | 동일                                                   |
| Offset          | FSE           | 동일                                                   |

> FSE(Finite State Entropy): ANS(Asymmetric Numeral Systems) 기반 엔트로피
> 코더입니다. 심볼당 분수 비트를 표현할 수 있어 허프만보다 이론 한계에
> 가깝고, 상태를 이어가며 인코딩하므로 비트스트림을 역방향으로 읽습니다.

허프만은 리터럴처럼 알파벳이 크고 분포가 완만한 데이터에, FSE 는 길이·오프셋처럼 편중이 심한 데이터에 배정되어 있습니다.

### 윈도우 크기

DEFLATE 의 32 KB 고정 윈도우와 달리 프레임 헤더에서 지정합니다.

```
windowLog   = 10 + Exponent
windowBase  = 1 << windowLog
windowAdd   = (windowBase / 8) * Mantissa
Window_Size = windowBase + windowAdd
```

최소값은 2^10 = 1 KB 이며, 규격은 디코더가 최소 8 MB 까지 지원하도록 권고합니다. 윈도우가 크면 멀리 떨어진 중복까지 찾을 수 있어 대용량 파일 압축률이 올라갑니다. CLI 에서는 `--long[=windowLog]` 로 확장하며 기본값은 27 입니다.

### 압축 레벨

| 레벨    | 지정 방법    | 특성                                 |
|---------|--------------|--------------------------------------|
| 음수    | `--fast=N`   | 속도 우선, 압축률 희생               |
| 1 ~ 19  | `-N`         | 일반 범위. 기본값 `3`                |
| 20 ~ 22 | `--ultra -N` | 메모리 사용량 급증, 별도 플래그 필수 |

### 사전 압축

작은 파일이 많으면 파일마다 LZ77 윈도우를 처음부터 채워야 해서 압축이 잘 되지 않습니다. zstd 는 미리 학습한 사전을 공유해 이 문제를 줄입니다.

```bash
# 샘플에서 사전 학습
zstd --train samples/* -o dict.zdict

# 사전을 사용해 압축·해제
zstd -D dict.zdict -3 input.json -o input.json.zst
zstd -D dict.zdict -d input.json.zst -o input.json
```

🟡 사전은 압축·해제 양쪽에 동일한 파일이 필요합니다. 사전을 분실하면 데이터를 복원할 수 없으므로 사전 자체를 백업 대상에 포함해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 도구 비교 벤치마크

### 측정 환경

| 항목      | 값                                                   |
|-----------|------------------------------------------------------|
| CPU       | Intel Core i5-13500                                  |
| 커널      | 6.8.0-138-generic                                    |
| 코퍼스    | 저장소 내 `*.md` 421개를 tar 로 묶은 5,314,560 byte  |
| 측정 방식 | 각 조합 3회 실행 후 최소 소요 시간 채택, 단일 스레드 |
| 도구 버전 | gzip 1.12 / zstd 1.5.5 / xz 5.4.5 / bzip2 1.0.8      |

### 재현 명령

```bash
# 코퍼스 생성
find . -name '*.md' -not -path './.git/*' -print0 | sort -z \
    | tar --null -cf corpus.tar --files-from=-

# 개별 측정 예
zstd -3 -c -q < corpus.tar > out.zst
zstd -dc -q   < out.zst > /dev/null

# zstd 내장 벤치마크로 레벨별 일괄 비교
zstd -b1 -e19 corpus.tar
```

### 결과

| 도구       | 결과 크기      | 압축률 | 압축 속도  | 해제 속도  |
|------------|----------------|--------|------------|------------|
| `gzip -6`  | 1,394,451 byte | 3.81x  | 44.0 MB/s  | 180.0 MB/s |
| `gzip -9`  | 1,384,077 byte | 3.84x  | 13.3 MB/s  | 186.2 MB/s |
| `zstd -3`  | 1,346,357 byte | 3.95x  | 184.2 MB/s | 664.3 MB/s |
| `zstd -12` | 1,150,714 byte | 4.62x  | 30.5 MB/s  | 650.6 MB/s |
| `zstd -19` | 1,035,035 byte | 5.13x  | 3.8 MB/s   | 670.5 MB/s |
| `xz -6`    | 1,016,084 byte | 5.23x  | 3.8 MB/s   | 104.7 MB/s |
| `bzip2 -9` | 1,056,323 byte | 5.03x  | 20.9 MB/s  | 46.6 MB/s  |

### 해석

`zstd -3` 은 `gzip -6` 보다 압축률이 높으면서 압축이 약 4배, 해제가 약 3.7배 빠릅니다. 기본값끼리 비교하면 gzip 을 계속 쓸 기술적 이유는 호환성 외에 크지 않습니다.

`xz -6` 이 압축률 5.23x 로 가장 높지만 압축 속도가 3.8 MB/s 로 `zstd -3` 의 약 1/48 입니다. 해제 속도도 104.7 MB/s 로 zstd 의 약 1/6 수준입니다.

zstd 의 특징은 레벨을 올려도 해제 속도가 거의 변하지 않는 점입니다. `-3` 에서 `-19` 로 올리면 압축 속도는 약 48배 느려지지만 해제 속도는 664 MB/s 에서 670 MB/s 로 사실상 동일합니다. 한 번 압축해 여러 번 배포하는 아티팩트에 유리한 특성입니다.

`bzip2 -9` 는 압축률이 `zstd -19` 와 비슷한데 해제 속도가 46.6 MB/s 로 가장 느립니다. 신규 도입 이유를 찾기 어렵습니다.

🟡 위 수치는 텍스트 코퍼스 기준입니다. 바이너리, 이미지, 로그 등 데이터 특성에 따라 순위가 달라질 수 있으므로 실제 데이터로 재측정해야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 실무 선택 기준

### 용도별 권장

| 상황               | 권장                  | 이유                                                |
|--------------------|-----------------------|-----------------------------------------------------|
| 로그 실시간 압축   | `zstd -3`             | 압축 속도 184 MB/s 로 수집 지연 최소화              |
| 일일 백업 전송     | `zstd -12` ~ `-19`    | 해제 속도를 유지하며 압축률 확보                    |
| 장기 보관 아카이브 | `xz -6`               | 측정 중 압축률 1위. 해제 빈도가 낮아 속도 불리 감수 |
| 배포 아티팩트      | `zstd`                | 해제 속도 650 MB/s 이상으로 배포 시간 단축          |
| 외부 배포 파일     | ZIP (method 8)        | OS 기본 지원. 수신자 환경 제약 없음                 |
| HTTP 응답 본문     | `gzip` 또는 `br`      | `Accept-Encoding` 협상 호환성                       |
| 이미 압축된 데이터 | 무압축 (`0` / stored) | 재압축 시 크기 증가                                 |

### 판단 순서

```
1. 수신 측 환경을 통제할 수 있는가?
   No  -> ZIP (method 8) 또는 gzip
   Yes -> 2

2. 해제 빈도가 압축 빈도보다 높은가?
   Yes -> zstd (레벨은 압축 시간 예산에 맞춰 결정)
   No  -> 3

3. 보관 기간이 길고 용량 비용이 지배적인가?
   Yes -> xz
   No  -> zstd -3
```

### 주의사항

| 주의 항목            | 내용                                                             |
|----------------------|------------------------------------------------------------------|
| `tar.gz` 랜덤 액세스 | 단일 스트림이므로 특정 파일만 뽑아도 앞부분 전체 해제 필요       |
| `gzip` 병렬화        | 포맷상 단일 스트림. 병렬 압축은 `pigz` 등 다중 멤버 방식 필요    |
| `zstd --ultra`       | 레벨 20 이상은 압축·해제 양쪽 메모리 사용량 급증                 |
| ZIP 비표준 method    | `93`(zstd), `95`(XZ) 는 수신 측 도구가 지원하지 않을 수 있음     |
| 재압축               | JPEG, MP4, `.zst` 등은 이미 엔트로피 한계에 근접해 크기가 늘어남 |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 명령어 요약

| 목적                   | 명령                                         |
|------------------------|----------------------------------------------|
| 레벨별 압축률 비교     | `zstd -b1 -e19 <file>`                       |
| gzip 헤더 확인         | `xxd -l 16 <file>.gz`                        |
| gzip 원본 크기 확인    | `gzip -l <file>.gz`                          |
| zstd 프레임 정보       | `zstd -l <file>.zst`                         |
| ZIP 엔트리 목록·method | `unzip -v <file>.zip`                        |
| 무결성 검사            | `gzip -t` / `zstd -t` / `xz -t` / `unzip -t` |

### 자주 쓰는 조합

```bash
# 디렉토리를 zstd 로 아카이브 (tar 내장 옵션)
tar --zstd -cf backup.tar.zst /data
tar --zstd -xf backup.tar.zst

# 레벨 지정이 필요할 때
tar -cf - /data | zstd -12 -o backup.tar.zst

# gzip 아카이브 (호환성 우선)
tar -czf backup.tar.gz /data

# 병렬 gzip 압축
tar -cf - /data | pigz -6 > backup.tar.gz

# 스트림 재압축 (gzip -> zstd)
gzip -dc old.gz | zstd -3 -o new.zst

# 압축 상태로 내용 검색
zstdgrep 'pattern' file.zst
zgrep    'pattern' file.gz
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- RFC 1951: DEFLATE Compressed Data Format Specification version 1.3
- RFC 1952: GZIP file format specification version 4.3
- RFC 1950: ZLIB Compressed Data Format Specification version 3.3
- RFC 8878: Zstandard Compression and the 'application/zstd' Media Type
- RFC 7932: Brotli Compressed Data Format
- Huffman, David A. "A Method for the Construction of Minimum-Redundancy Codes". Proceedings of the IRE, vol. 40, no. 9, pp. 1098-1101, 1952
- Ziv, Jacob and Lempel, Abraham. "A universal algorithm for sequential data compression". IEEE Transactions on Information Theory, vol. 23, no. 3, pp. 337-343, 1977
- PKWARE APPNOTE.TXT: [.ZIP File Format Specification 6.3.10](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT) — ★★★☆☆
- Zstandard: [github.com/facebook/zstd](https://github.com/facebook/zstd) — ★★★☆☆
- zlib Manual: [zlib.net/manual.html](https://zlib.net/manual.html) — ★★★☆☆
- [이진 트리](data_structures/binary_tree.md)
- [힙](data_structures/heap.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-27

© 2026 siasia86. Licensed under CC BY 4.0.
