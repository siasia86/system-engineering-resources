# 라이선스 가이드

## 목차

| 섹션 |
|------|
| [1. 소프트웨어 라이선스](#1-소프트웨어-라이선스) / [2. Creative Commons 라이선스](#2-creative-commons-라이선스) / [3. 라이선스 비교](#3-라이선스-비교) |
| [4. 선택 가이드](#4-선택-가이드) / [5. 실무 적용](#5-실무-적용) / [6. 주의사항 & FAQ](#6-주의사항--faq) |
| [7. 실전 팁](#7-실전-팁) |

---

## 1. 소프트웨어 라이선스

### MIT License

가장 자유로운 라이선스. 출처 표시만 하면 상업적 사용, 수정, 배포 모두 허용.

```
MIT License

Copyright (c) 2026 siasia86

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

| 항목 | 허용 여부 |
|------|-----------|
| 상업적 사용 | ✅ |
| 수정 | ✅ |
| 배포 | ✅ |
| 특허 사용 | ⚠️ 명시 없음 |
| 출처 표시 의무 | ✅ |
| 동일 라이선스 의무 | ❌ |

### Apache License 2.0

MIT와 유사하나 특허 사용 권한 명시. 기업 환경에서 선호.

| 항목 | 허용 여부 |
|------|-----------|
| 상업적 사용 | ✅ |
| 수정 | ✅ |
| 배포 | ✅ |
| 특허 사용 | ✅ |
| 출처 표시 의무 | ✅ |
| 동일 라이선스 의무 | ❌ |

### GNU GPL v3

수정 배포 시 동일 라이선스(GPL) 적용 의무. Copyleft.

| 항목 | 허용 여부 |
|------|-----------|
| 상업적 사용 | ✅ |
| 수정 | ✅ |
| 배포 | ✅ |
| 특허 사용 | ✅ |
| 출처 표시 의무 | ✅ |
| 동일 라이선스 의무 | ✅ (강제) |

### BSD License

MIT와 유사. 2-Clause(Simplified)와 3-Clause(New) 두 종류.

- **2-Clause**: 출처 표시 + 보증 부인
- **3-Clause**: 2-Clause + 프로젝트 이름 광고 금지

[⬆ 목차로 돌아가기](#목차)

---

## 2. Creative Commons 라이선스

문서, 이미지, 콘텐츠에 사용. 코드에는 부적합.

| 라이선스 | 상업적 사용 | 수정 | 동일 라이선스 | 설명 |
|----------|:-----------:|:----:|:-------------:|------|
| **CC BY** | ✅ | ✅ | ❌ | 출처 표시만 |
| **CC BY-SA** | ✅ | ✅ | ✅ | 출처 + 동일 라이선스 |
| **CC BY-NC** | ❌ | ✅ | ❌ | 출처 + 비상업 |
| **CC BY-ND** | ✅ | ❌ | ❌ | 출처 + 수정 금지 |
| **CC BY-NC-SA** | ❌ | ✅ | ✅ | 출처 + 비상업 + 동일 |
| **CC BY-NC-ND** | ❌ | ❌ | ❌ | 출처 + 비상업 + 수정 금지 |
| **CC0** | ✅ | ✅ | ❌ | 퍼블릭 도메인 (출처 불필요) |

이 저장소는 **CC BY 4.0** 적용 — 출처 표시 시 자유롭게 사용 가능.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 라이선스 비교

### 소프트웨어 라이선스

| 라이선스 | 상업적 사용 | 수정 | 특허 | 동일 라이선스 | 난이도 |
|----------|:-----------:|:----:|:----:|:-------------:|--------|
| MIT | ✅ | ✅ | ❌ | ❌ | 쉬움 |
| Apache 2.0 | ✅ | ✅ | ✅ | ❌ | 보통 |
| GPL v3 | ✅ | ✅ | ✅ | ✅ | 복잡 |
| BSD 2-Clause | ✅ | ✅ | ❌ | ❌ | 쉬움 |
| LGPL | ✅ | ✅ | ✅ | 라이브러리만 | 복잡 |

### 라이선스 호환성

```
MIT ──────────────────────────────> GPL v3 (포함 가능)
Apache 2.0 ──────────────────────> GPL v3 (포함 가능)
GPL v2 ──────────────────────────> GPL v3 (불가)
GPL v3 ──────────────────────────> MIT (불가, GPL이 더 제한적)
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 선택 가이드

### 빠른 결정 플로우차트

```
코드인가?
├── YES
│   ├── 최대한 자유롭게 → MIT
│   ├── 특허 보호 필요 → Apache 2.0
│   ├── 파생물도 오픈소스 강제 → GPL v3
│   └── 라이브러리, 파생물 일부만 → LGPL
└── NO (문서/콘텐츠)
    ├── 출처 표시만 → CC BY 4.0
    ├── 비상업 제한 → CC BY-NC 4.0
    └── 제한 없음 → CC0
```

### 상황별 추천

| 상황 | 추천 라이선스 | 이유 |
|------|--------------|------|
| 개인 오픈소스 프로젝트 | MIT | 단순, 광범위한 사용 허용 |
| 기업 오픈소스 프로젝트 | Apache 2.0 | 특허 보호 명시 |
| 커뮤니티 중심 프로젝트 | GPL v3 | 파생물 오픈소스 강제 |
| 기술 문서/학습 자료 | CC BY 4.0 | 출처 표시 후 자유 사용 |
| 개인 블로그 | CC BY-NC 4.0 | 비상업 제한 |
| 예제 코드 | MIT 또는 CC0 | 제약 없이 사용 가능 |
| 회사 내부 문서 | All Rights Reserved | 외부 공개 금지 |

### 체크리스트

```
□ 코드인가, 문서/콘텐츠인가?
□ 상업적 사용을 허용할 것인가?
□ 파생물에도 동일 라이선스를 강제할 것인가?
□ 특허 보호가 필요한가?
□ 기여자들의 동의(CLA)가 필요한가?
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실무 적용

### README.md 하단 표시

```markdown
## License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.

© 2026 siasia86
```

### 기술 문서 하단 표시

```markdown
---

**작성일**: 2026-04-30

**마지막 업데이트**: 2026-04-30

© 2026 siasia86. Licensed under CC BY 4.0.
```

### LICENSE 파일 생성

```bash
# GitHub에서 저장소 생성 시 자동 추가 가능
# 또는 수동 생성

# MIT LICENSE 파일 예시
cat > LICENSE << 'LICEOF'
MIT License

Copyright (c) 2026 siasia86

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software...
LICEOF
```

### GitHub 라이선스 설정

```bash
# 1. 저장소 생성 시: Add a license 선택
# 2. 기존 저장소: 루트에 LICENSE 파일 추가
# 3. GitHub이 자동 인식하는 파일명
#    LICENSE, LICENSE.md, LICENSE.txt, COPYING

# 라이선스 배지 추가 (README.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
```

### 소스 파일 헤더

```python
# Copyright (c) 2026 siasia86
# Licensed under the MIT License.
# See LICENSE file in the project root for details.
```

```bash
#!/bin/bash
# Copyright (c) 2026 siasia86. Licensed under MIT.
```

### Dual Licensing

오픈소스와 상업용 라이선스를 동시에 제공하는 방식.

```
이 소프트웨어는 두 가지 라이선스로 제공됩니다:

1. 오픈소스: GPL v3 (무료, 파생물 오픈소스 의무)
2. 상업용: 별도 계약 (유료, 파생물 비공개 가능)

상업용 라이선스 문의: contact@example.com
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 주의사항 & FAQ

### 주의사항

**라이선스 변경**
- 이미 배포된 버전의 라이선스는 소급 변경 불가
- 모든 기여자의 동의 필요
- 더 제한적인 라이선스로 변경 시 기존 사용자에게 영향

**라이선스 호환성**
- GPL 코드를 MIT 프로젝트에 포함 시 전체가 GPL 적용
- Apache 2.0 + GPL v2 = 비호환 (GPL v3는 호환)
- CC 라이선스는 소프트웨어 코드에 부적합

**라이선스 없음 = All Rights Reserved**
- 라이선스 명시 없으면 저작권법상 모든 권리 보유
- 타인이 사용/수정/배포 불가

### FAQ

**Q. MIT와 Apache 2.0 중 뭘 선택해야 하나?**
특허 분쟁 가능성이 있는 기업 환경이면 Apache 2.0, 단순 개인 프로젝트면 MIT.

**Q. GPL 코드를 내 프로젝트에 사용하면?**
내 프로젝트 전체가 GPL 적용 대상이 됨. 상업 프로젝트라면 LGPL 또는 다른 라이선스 검토.

**Q. 라이선스를 나중에 변경할 수 있나?**
가능하지만 모든 기여자 동의 필요. 초기에 신중하게 선택할 것.

**Q. 출처 표시는 어떻게 하나?**
```
원본 작성자: siasia86
출처: https://github.com/siasia86/system-engineering-resources
라이선스: CC BY 4.0
```

**Q. 라이선스 위반 시 대응 방법**
1. 위반 사실 문서화 (스크린샷, URL)
2. 위반자에게 정정 요청 (이메일)
3. 플랫폼 신고 (GitHub DMCA 등)
4. 법적 조치 (필요 시)

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실전 팁

### Tip 1: 프로젝트 시작 시 라이선스 결정

나중에 변경하면 기여자 동의가 필요해 복잡해진다.

### Tip 2: LICENSE 파일은 프로젝트 루트에

```
my-project/
├── LICENSE          ← 여기
├── README.md
└── src/
```

### Tip 3: 의존성 라이선스 확인

```bash
# Python
pip-licenses --format=table

# Node.js
npx license-checker --summary

# Java (Maven)
mvn license:summary
```

### Tip 4: SPDX 식별자 사용

```python
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: Apache-2.0
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: CC-BY-4.0
```

### Tip 5: GitHub Actions로 라이선스 자동 체크

```yaml
# .github/workflows/license-check.yml
name: License Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npx license-checker --onlyAllow 'MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause'
```

### Tip 6: 저작권 연도

```
# 단일 연도: 최초 작성 연도 고정
© 2026 siasia86

# 범위: 최초~최근 수정 연도
© 2024-2026 siasia86
```

### Tip 7: 기여자 라이선스 동의 (CLA)

대규모 오픈소스 프로젝트에서 라이선스 변경 유연성 확보를 위해 사용.
GitHub CLA Assistant 등 도구로 자동화 가능.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

### 라이선스 선택 도구

- Choose a License: [choosealicense.com](https://choosealicense.com/) — ★★★☆☆
- TLDR Legal: [tldrlegal.com](https://tldrlegal.com/) — ★★☆☆☆
- SPDX License List: [spdx.org/licenses](https://spdx.org/licenses/) — ★★☆☆☆

### 라이선스 원문 & 공식 문서

- GNU Licenses: [gnu.org/licenses](https://www.gnu.org/licenses/) — ★★★☆☆
- FSF 라이선스 호환성: [gnu.org/licenses/license-compatibility](https://www.gnu.org/licenses/license-compatibility.html) — ★★★☆☆
- Apache License 2.0 원문: [apache.org/licenses](https://www.apache.org/licenses/LICENSE-2.0) — ★★★☆☆
- OSI Approved Licenses: [opensource.org/licenses](https://opensource.org/licenses/) — ★★☆☆☆
- Creative Commons: [creativecommons.org](https://creativecommons.org/licenses/) — ★★☆☆☆

### GitHub & 실무

- GitHub Licensing a Repository: [docs.github.com](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) — ★★★☆☆

### 법적 근거

- 한국 저작권법: [law.go.kr](https://www.law.go.kr/법령/저작권법) — ★★☆☆☆

---

## 통계 [choosealicense.com](https://choosealicense.com/)
- Creative Commons: [creativecommons.org](https://creativecommons.org/licenses/)
- SPDX License List: [spdx.org/licenses](https://spdx.org/licenses/)
- OSI Approved Licenses: [opensource.org/licenses](https://opensource.org/licenses/)
- TLDR Legal: [tldrlegal.com](https://tldrlegal.com/)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-25

**마지막 업데이트**: 2026-04-30

© 2026 siasia86. Licensed under CC BY 4.0.
