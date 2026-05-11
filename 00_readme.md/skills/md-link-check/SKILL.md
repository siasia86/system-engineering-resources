# Markdown Link Check Rules

## 목적

`.md` 파일 내 링크가 실제 파일과 일치하는지 검증하고 깨진 링크를 수정

## 검사 대상

- `[텍스트](경로.md)` 형태의 내부 링크
- 앵커 링크 (`#섹션명`) 는 별도 검사
- 외부 URL은 형식만 검사 (접근 가능 여부 제외)

## 검사 방법

```bash
# 특정 README.md 링크 검사
BASE=/path/to/repo
grep -oP '\[.*?\]\(\K[^)#]+\.md' README.md | while read link; do
  [ -f "$BASE/$link" ] && echo "OK  $link" || echo "❌  $link"
done

# 전체 README.md 일괄 검사
find "$BASE" -name "README.md" | while read readme; do
  dir=$(dirname "$readme")
  while IFS= read -r link; do
    full="$dir/$link"
    sudo test -f "$full" || echo "❌  $readme → $link"
  done < <(grep -oP '\[.*?\]\(\K[^)#]+\.md' "$readme")
done
```

## 수정 규칙

1. **파일명 변경 반영** — 파일명이 바뀐 경우 링크 텍스트와 경로 모두 수정
2. **경로 누락** — 서브디렉토리 경로가 빠진 경우 추가 (`04_system_engineer/02_operations/` 등)
3. **접두사 제거** — `01_`, `02_` 등 숫자 접두사가 파일명에서 제거된 경우 링크도 수정
4. **상대 경로** — 서브디렉토리 README에서 상위 디렉토리 참조 시 `../` 사용

## 주의사항

- `05_computer_science/01_data_structures/` 처럼 디렉토리 링크는 `README.md` 존재 여부 확인
- 링크 텍스트(`[텍스트]`)와 경로(`(경로)`)를 모두 수정할 것
- 문서 트리 섹션과 섹션 표 양쪽 모두 수정
