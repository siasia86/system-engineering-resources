# 개인정보보호위원회 (pipc.go.kr) 파일 다운로드 방법

> pipc.go.kr 은 eGovFrame 기반으로 세션 없이도 직접 API 호출로 다운로드 가능합니다.
> JS 렌더링 없이 curl / Python 으로 자동화할 수 있습니다.

---

## 1. 다운로드 URL 구조

```
https://pipc.go.kr/np/cmm/fms/FileDown.do
  ?atchFileId=FILE_000000000XXXXXX   ← 게시글 고유 파일 묶음 ID
  &fileSn=0                          ← 첨부파일 순번 (0부터 시작)
  &fileExtsn=hwpx                    ← 확장자 (hwpx / pdf / hwp)
```

---

## 2. 게시판 종류 (bbsId / mCode)

동일한 다운로드 방식이 아래 모든 게시판에 적용됩니다.

| 게시판          | bbsId | mCode          | URL 예시                                                                                   |
|-----------------|-------|----------------|--------------------------------------------------------------------------------------------|
| 공지사항        | BS061 | C010010000     | selectBoardList.do?bbsId=BS061&mCode=C010010000                                            |
| 훈령·예규·고시  | BS208 | C010020000     | selectBoardList.do?bbsId=BS208&mCode=C010020000                                            |
| 보도자료        | BS074 | C020010000     | selectBoardList.do?bbsId=BS074&mCode=C020010000                                            |
| 안내서          | BS262 | C010030000     | selectBoardList.do?bbsId=BS262&mCode=C010030000                                            |
| 가이드라인      | BS258 | C010040000     | selectBoardList.do?bbsId=BS258&mCode=C010040000                                            |

> 게시글 상세 URL: `selectBoardArticle.do?bbsId=<bbsId>&mCode=<mCode>&nttId=<nttId>`

---

## 3. atchFileId / fileSn 확인 방법

공지사항 게시글 HTML 소스에서 추출합니다.

```bash
# 게시글 HTML에서 atchFileId / 첨부파일 정보 추출
curl -s "https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do?bbsId=BS061&mCode=C010010000&nttId=12376" \
  -H "User-Agent: Mozilla/5.0" | grep -E "atchFileId|fn_egov_downFile"
```

출력 예시:

```
<input type="hidden" name="atchFileId" value="FILE_000000000561299">
fn_egov_downFile('FILE_000000000561299','0','hwpx')  ← fileSn=0, 첫 번째 파일
fn_egov_downFile('FILE_000000000561299','1','hwpx')  ← fileSn=1, 두 번째 파일
fn_egov_downFile('FILE_000000000561299','2','hwpx')  ← fileSn=2, 세 번째 파일
```

---

## 4. 파일명 확인

첨부파일 `alt` 속성에 실제 파일명이 있습니다.

```bash
# hwpx / hwp / pdf 모두 포함
curl -s "https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do?bbsId=BS061&mCode=C010010000&nttId=12376" \
  -H "User-Agent: Mozilla/5.0" | grep -oP 'alt="[^"]+\.(hwpx|hwp|pdf)"'
```

---

## 5. curl 단일 파일 다운로드

```bash
curl -L -o "파일명.hwpx" \
  "https://pipc.go.kr/np/cmm/fms/FileDown.do?atchFileId=FILE_000000000561299&fileSn=0&fileExtsn=hwpx" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Referer: https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do?bbsId=BS061&mCode=C010010000&nttId=12376"
```

---

## 6. Python 자동화 (전체 첨부파일 일괄 다운로드)

`ntt_id` 하나만 지정하면 해당 게시글의 첨부파일을 모두 다운로드합니다.

```python
import urllib.request, re, os

def download_attachments(ntt_id, save_dir=".", bbs_id="BS061", m_code="C010010000",
                         skip_existing=True):
    """
    pipc.go.kr 게시글의 첨부파일을 모두 다운로드합니다.

    Args:
        ntt_id       : 게시글 번호 (URL의 nttId 값)
        save_dir     : 저장 디렉토리 경로
        bbs_id       : 게시판 ID (기본값: BS061 공지사항)
        m_code       : 메뉴 코드 (기본값: C010010000)
        skip_existing: True이면 이미 존재하는 파일 건너뜀
    """
    page_url = (
        f"https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do"
        f"?bbsId={bbs_id}&mCode={m_code}&nttId={ntt_id}"
    )
    headers = {"User-Agent": "Mozilla/5.0", "Referer": page_url}

    # 1. 게시글 HTML 가져오기
    req = urllib.request.Request(page_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    # 2. atchFileId 추출
    atch_match = re.search(r'name="atchFileId"\s+value="(FILE_\w+)"', html)
    if not atch_match:
        print(f"[WARN] nttId={ntt_id}: atchFileId 없음 (첨부파일 없는 게시글)")
        return
    atch_id = atch_match.group(1)

    # 3. 첨부파일 목록 추출 (fileSn, 확장자, 파일명)
    # fn_egov_downFile('FILE_xxx','0','hwpx') ... alt="파일명.hwpx"
    pattern = r"fn_egov_downFile\('FILE_\w+','(\d+)','(\w+)'\)[^>]*alt=\"([^\"]+\.\w+)\""
    files = re.findall(pattern, html)
    if not files:
        print(f"[WARN] nttId={ntt_id}: 첨부파일 정보를 찾을 수 없음")
        return

    print(f"[INFO] nttId={ntt_id}: 첨부파일 {len(files)}개 발견 (atchFileId={atch_id})")

    # 4. 순차 다운로드
    base_url = "https://pipc.go.kr/np/cmm/fms/FileDown.do"
    for sn, ext, fname in files:
        save_path = os.path.join(save_dir, fname)

        # 중복 건너뜀
        if skip_existing and os.path.exists(save_path):
            print(f"  [SKIP] 이미 존재: {fname}")
            continue

        url = f"{base_url}?atchFileId={atch_id}&fileSn={sn}&fileExtsn={ext}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()

            # HTML 응답이면 차단 또는 오류
            if data[:20].decode("utf-8", errors="ignore").strip().startswith("<!"):
                print(f"  [FAIL] 차단됨 (세션 만료 가능성): {fname}")
                continue

            with open(save_path, "wb") as f:
                f.write(data)
            print(f"  [OK] {fname} ({len(data):,} bytes)")

        except Exception as e:
            print(f"  [ERR] {fname} — {e}")


# 사용 예시 1 — 공지사항 단일 게시글
download_attachments(
    ntt_id=12376,
    save_dir="/root/32_system-engineering-resources/06_career/legal/_reference/"
)

# 사용 예시 2 — 훈령·예규·고시 게시판
# download_attachments(ntt_id=XXXXX, bbs_id="BS208", m_code="C010020000", save_dir="./")
```

---

## 7. 공지 목록 nttId 확인 방법

```bash
# 공지사항 목록 페이지에서 nttId 전체 추출
curl -s "https://pipc.go.kr/np/cop/bbs/selectBoardList.do?bbsId=BS061&mCode=C010010000" \
  -H "User-Agent: Mozilla/5.0" | grep -o "nttId=[0-9]*" | sort -u

# 제목과 함께 확인 (lynx)
lynx -dump "https://pipc.go.kr/np/cop/bbs/selectBoardList.do?bbsId=BS061&mCode=C010010000" \
  2>/dev/null | grep -E "[0-9]{3} \[|행정예고|입법|개정|고시"
```

---

## 8. 파일 형식별 텍스트 추출

다운로드 후 내용을 확인하는 방법입니다.

| 형식  | 추출 방법                                      | 비고                                    |
|-------|------------------------------------------------|-----------------------------------------|
| PDF   | `pdftotext 파일.pdf -`                         | `poppler-utils` 패키지 필요             |
| HWPX  | Python `zipfile` + XML 파싱                    | HWPX = ZIP 구조, `Contents/section*.xml` |
| HWP   | 직접 추출 불가 (바이너리 압축)                 | 한컴오피스 또는 LibreOffice 필요        |

HWPX 텍스트 추출 예시:

```python
import zipfile, re

def extract_hwpx_text(filepath):
    """HWPX 파일에서 텍스트를 추출합니다."""
    with zipfile.ZipFile(filepath, 'r') as z:
        sections = sorted([n for n in z.namelist()
                           if 'section' in n.lower() and n.endswith('.xml')])
        all_text = ''
        for s in sections:
            xml = z.read(s).decode('utf-8', errors='ignore')
            text = re.sub(r'<[^>]+>', ' ', xml)
            text = re.sub(r'\s+', ' ', text).strip()
            all_text += text + ' '
    return all_text

# 사용 예시
text = extract_hwpx_text("개정 이유서.hwpx")
print(text[:500])
```

---

## 9. 주의사항

| 항목                  | 내용                                                              |
|-----------------------|-------------------------------------------------------------------|
| 세션 불필요           | 로그인 없이 다운로드 가능                                         |
| Referer 헤더          | 없어도 되지만 있으면 안정적 (403 방지)                            |
| HTML 응답 체크        | `data[:20]`이 `<!`로 시작하면 차단 또는 오류                      |
| fileSn                | 0부터 시작, 첨부파일 수만큼 순번 존재                             |
| 파일명                | HTML `alt` 속성에서 추출, 한글·공백·괄호 포함 가능               |
| HWP (구버전)          | 바이너리 압축이라 Python으로 텍스트 추출 불가, 오피스 필요        |
| HWPX (신버전)         | ZIP 구조라 Python zipfile로 XML 파싱 가능                         |
| eGovFrame jsessionid  | URL에 포함되기도 하나 생략해도 정상 동작                          |
| 파일 크기 0           | 다운로드 성공했으나 내용이 없으면 서버 측 오류일 수 있음          |

---

**작성일**: 2026-08-25

**마지막 업데이트**: 2026-08-25

© 2026 siasia86. Licensed under CC BY 4.0.
