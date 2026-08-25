# 개인정보보호위원회 (pipc.go.kr) 파일 다운로드 방법

> pipc.go.kr 은 eGovFrame 기반으로 세션 없이도 직접 API 호출로 다운로드 가능합니다.
> JS 렌더링 없이 curl / python 으로 자동화할 수 있습니다.

---

## 1. 다운로드 URL 구조

```
https://pipc.go.kr/np/cmm/fms/FileDown.do
  ?atchFileId=FILE_000000000XXXXXX   ← 게시글 고유 파일 묶음 ID
  &fileSn=0                          ← 첨부파일 순번 (0부터 시작)
  &fileExtsn=hwpx                    ← 확장자 (hwpx / pdf / hwp)
```

---

## 2. atchFileId / fileSn 확인 방법

공지사항 게시글 HTML 소스에서 추출합니다.

```bash
# 게시글 URL 패턴
# https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do?bbsId=BS061&mCode=C010010000&nttId=<nttId>

# HTML 소스에서 atchFileId / 첨부파일 정보 추출
curl -s "https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do?bbsId=BS061&mCode=C010010000&nttId=12376" \
  -H "User-Agent: Mozilla/5.0" | grep -E "atchFileId|fn_egov_downFile"
```

출력 예시:

```
<input type="hidden" name="atchFileId" value="FILE_000000000561299">
fn_egov_downFile('FILE_000000000561299','0','hwpx')  ← fileSn=0
fn_egov_downFile('FILE_000000000561299','1','hwpx')  ← fileSn=1
fn_egov_downFile('FILE_000000000561299','2','hwpx')  ← fileSn=2
```

---

## 3. 파일명 확인

첨부파일 alt 속성에 실제 파일명이 있습니다.

```bash
curl -s "https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do?bbsId=BS061&mCode=C010010000&nttId=12376" \
  -H "User-Agent: Mozilla/5.0" | grep -o 'alt="[^"]*\.hwpx\|alt="[^"]*\.pdf'
```

---

## 4. curl 다운로드

```bash
# 단일 파일 다운로드
curl -L -o "파일명.hwpx" \
  "https://pipc.go.kr/np/cmm/fms/FileDown.do?atchFileId=FILE_000000000561299&fileSn=0&fileExtsn=hwpx" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Referer: https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do?bbsId=BS061&mCode=C010010000&nttId=12376"
```

---

## 5. Python 자동화 (전체 첨부파일 일괄 다운로드)

```python
import urllib.request, re, os

def download_attachments(ntt_id, save_dir="."):
    """pipc.go.kr 공지사항의 첨부파일을 모두 다운로드합니다."""
    page_url = (
        f"https://pipc.go.kr/np/cop/bbs/selectBoardArticle.do"
        f"?bbsId=BS061&mCode=C010010000&nttId={ntt_id}"
    )
    headers = {"User-Agent": "Mozilla/5.0", "Referer": page_url}

    # 1. 게시글 HTML 가져오기
    req = urllib.request.Request(page_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    # 2. atchFileId 추출
    atch_match = re.search(r'name="atchFileId"\s+value="(FILE_\w+)"', html)
    if not atch_match:
        print("atchFileId를 찾을 수 없습니다.")
        return
    atch_id = atch_match.group(1)

    # 3. 첨부파일 목록 추출 (fileSn, ext, 파일명)
    pattern = r"fn_egov_downFile\('FILE_\w+','(\d+)','(\w+)'\)[^>]*alt=\"([^\"]+)\""
    files = re.findall(pattern, html)
    if not files:
        print("첨부파일 정보를 찾을 수 없습니다.")
        return

    # 4. 순차 다운로드
    base_url = "https://pipc.go.kr/np/cmm/fms/FileDown.do"
    for sn, ext, fname in files:
        url = f"{base_url}?atchFileId={atch_id}&fileSn={sn}&fileExtsn={ext}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            if data[:20].decode("utf-8", errors="ignore").strip().startswith("<!"):
                print(f"[SKIP] 차단됨: {fname}")
                continue
            save_path = os.path.join(save_dir, fname)
            with open(save_path, "wb") as f:
                f.write(data)
            print(f"[OK] 저장: {fname} ({len(data):,} bytes)")
        except Exception as e:
            print(f"[ERR] {fname} — {e}")


# 사용 예시
download_attachments(
    ntt_id=12376,
    save_dir="/root/32_system-engineering-resources/06_career/legal/_reference/"
)
```

---

## 6. 공지 목록 nttId 확인 방법

```bash
# 공지사항 목록에서 nttId 전체 추출
curl -s "https://pipc.go.kr/np/cop/bbs/selectBoardList.do?bbsId=BS061&mCode=C010010000" \
  -H "User-Agent: Mozilla/5.0" | grep -o "nttId=[0-9]*" | sort -u
```

---

## 7. 주의사항

| 항목              | 내용                                                  |
|-------------------|-------------------------------------------------------|
| 세션 불필요       | 로그인 없이 다운로드 가능                             |
| Referer 헤더      | 없어도 되지만 있으면 안정적                           |
| HTML 응답 체크    | `data[:20]`이 `<!`로 시작하면 차단 또는 오류          |
| fileSn            | 0부터 시작, 첨부파일 수만큼 순번 존재                 |
| 파일명            | HTML `alt` 속성에서 추출, 한글 포함 가능              |
| eGovFrame 세션ID  | URL에 포함되기도 하나 생략해도 동작                   |

---

**작성일**: 2026-08-25

**마지막 업데이트**: 2026-08-25

© 2026 siasia86. Licensed under CC BY 4.0.
