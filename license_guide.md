# 라이선스 가이드

## 목차
1. [소프트웨어 라이선스](#소프트웨어-라이선스)
2. [Creative Commons 라이선스](#creative-commons-라이선스)
3. [라이선스 비교](#라이선스-비교)
4. [사용 예시](#사용-예시)
5. [선택 가이드](#선택-가이드)
6. [실전 팁](#실전-팁-tips)
7. [빠른 결정 플로우차트](#빠른-결정-플로우차트)
8. [체크리스트](#체크리스트)
9. [자주 묻는 질문](#자주-묻는-질문-faq)
10. [라이선스 위반 시](#라이선스-위반-시)

---

## 소프트웨어 라이선스

코드, 프로그램, 라이브러리에 사용하는 라이선스

### MIT License (가장 자유로움)

**특징:**
- 가장 간단하고 자유로운 라이선스
- 상업적 사용 가능
- 수정 가능
- 재배포 가능
- 라이선스 변경 가능

**조건:**
- 라이선스 및 저작권 표시만 유지

**사용 예시:**
```markdown
MIT License

Copyright (c) 2026 sj_del

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**유명 프로젝트:** jQuery, Rails, Node.js

---

### Apache License 2.0

**특징:**
- MIT와 유사하지만 특허권 보호 추가
- 상업적 사용 가능
- 수정 가능
- 재배포 가능
- 특허 소송 방지 조항

**조건:**
- 라이선스 및 저작권 표시
- 변경 사항 명시
- NOTICE 파일 포함

**사용 예시:**
```markdown
Apache License 2.0

Copyright 2026 sj_del

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

**유명 프로젝트:** Android, Apache HTTP Server, Kubernetes

---

### GNU GPL (General Public License)

**특징:**
- 강력한 카피레프트 (copyleft)
- 수정본도 같은 라이선스로 공개 필수
- 상업적 사용 가능
- 소스 코드 공개 의무

**버전:**
- **GPL v2** - Linux 커널
- **GPL v3** - 특허권 보호 강화

**조건:**
- 소스 코드 공개
- 같은 라이선스 적용
- 변경 사항 명시

**유명 프로젝트:** Linux, Git, WordPress

---

### BSD License

**특징:**
- MIT와 유사하게 자유로움
- 상업적 사용 가능
- 수정 가능
- 재배포 가능

**버전:**
- **2-Clause BSD** - 매우 간단
- **3-Clause BSD** - 이름 사용 제한 추가

**유명 프로젝트:** FreeBSD, Django

---

## Creative Commons 라이선스

문서, 이미지, 콘텐츠에 사용하는 라이선스

### CC BY (Attribution)

**가장 자유로운 CC 라이선스**

상업적 사용 가능  
수정 가능  
재배포 가능  
라이선스 변경 가능  

조건: 출처 표시

```markdown
이 문서는 CC BY 4.0 라이선스를 따릅니다.
https://creativecommons.org/licenses/by/4.0/

© 2026 sj_del
```

---

### CC BY-SA (Share-Alike)

**동일 조건 변경 허락**

상업적 사용 가능  
수정 가능  
재배포 가능  

조건: 출처 표시 + 같은 라이선스 적용

```markdown
이 문서는 CC BY-SA 4.0 라이선스를 따릅니다.
https://creativecommons.org/licenses/by-sa/4.0/

© 2026 sj_del
```

**사용 사례:** Wikipedia, Stack Overflow

---

### CC BY-NC (Non-Commercial)

**비영리 목적만**

수정 가능  
재배포 가능  
상업적 사용 금지  

조건: 출처 표시 + 비영리 목적

```markdown
이 문서는 CC BY-NC 4.0 라이선스를 따릅니다.
https://creativecommons.org/licenses/by-nc/4.0/

© 2026 sj_del
```

---

### CC BY-ND (No-Derivatives)

**변경 금지**

상업적 사용 가능  
재배포 가능 (원본만)  
수정 금지  

조건: 출처 표시 + 원본 그대로 사용

```markdown
이 문서는 CC BY-ND 4.0 라이선스를 따릅니다.
https://creativecommons.org/licenses/by-nd/4.0/

© 2026 sj_del
```

---

### CC BY-NC-SA

**비영리 + 동일 조건**

수정 가능  
재배포 가능  
상업적 사용 금지  

조건: 출처 표시 + 비영리 + 같은 라이선스

---

### CC BY-NC-ND

**비영리 + 변경 금지 (가장 제한적)**

재배포 가능 (원본만)  
상업적 사용 금지  
수정 금지  

조건: 출처 표시 + 비영리 + 원본 그대로

---

### CC0 (Public Domain)

**모든 권리 포기**

상업적 사용 가능  
수정 가능  
재배포 가능  
출처 표시 불필요  

```markdown
이 문서는 CC0 1.0 (Public Domain)으로 배포됩니다.
https://creativecommons.org/publicdomain/zero/1.0/

누구나 자유롭게 사용할 수 있습니다.
```

---

## 라이선스 비교

### 소프트웨어 라이선스 비교

| 라이선스       | 상업적 사용 | 수정 | 재배포 | 소스 공개 | 특허 보호 |
|----------------|-------------|------|--------|-----------|-----------|
| **MIT**        |             |      |        |           |           |
| **Apache 2.0** |             |      |        |           |           |
| **GPL v3**     |             |      |        | (필수)    |           |
| **BSD**        |             |      |        |           |           |

### Creative Commons 비교

| 라이선스        | 상업적 사용 | 수정 | 재배포 | 조건                          |
|-----------------|-------------|------|--------|-------------------------------|
| **CC BY**       |             |      |        | 출처 표시                     |
| **CC BY-SA**    |             |      |        | 출처 + 동일 라이선스          |
| **CC BY-NC**    |             |      |        | 출처 + 비영리                 |
| **CC BY-ND**    |             |      |        | 출처 + 원본 유지              |
| **CC BY-NC-SA** |             |      |        | 출처 + 비영리 + 동일 라이선스 |
| **CC BY-NC-ND** |             |      |        | 출처 + 비영리 + 원본 유지     |
| **CC0**         |             |      |        | 없음                          |

---

## 사용 예시

### 1. GitHub README.md 하단

```markdown
---

## License

MIT License - Copyright © 2026 sj_del

See [LICENSE](LICENSE) file for details.
```

### 2. 기술 문서 하단

```markdown
---

## 문서 정보

- **작성자**: 홍길동
- **최초 작성**: 2026-03-03
- **라이선스**: CC BY 4.0

이 문서는 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 라이선스를 따릅니다.  
출처를 표시하면 자유롭게 사용할 수 있습니다.

© 2026 홍길동
```

### 3. 간단한 표시

```markdown
---

© 2026 sj_del. Licensed under [MIT License](https://opensource.org/licenses/MIT).
```

### 4. 상세 표시

```markdown
---

## License

**MIT License**

Copyright (c) 2026 sj_del

이 소프트웨어는 MIT 라이선스에 따라 배포됩니다.  
자유롭게 사용, 수정, 배포할 수 있습니다.

전체 라이선스 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
```

### 5. 여러 파일에 적용

**각 소스 파일 상단:**
```python
# Copyright (c) 2026 sj_del
# Licensed under the MIT License
# See LICENSE file in the project root for full license information.
```

---

## 선택 가이드

### 소프트웨어 코드

#### 최대한 자유롭게 공유하고 싶다
→ **MIT License** (추천)

#### 특허 보호가 필요하다
→ **Apache License 2.0**

#### 수정본도 오픈소스로 유지하고 싶다
→ **GPL v3**

#### 간단하고 자유롭게
→ **BSD License**

---

### 문서/콘텐츠

#### 자유롭게 사용하되 출처만 표시
→ **CC BY** (추천)

#### 수정본도 같은 라이선스 유지
→ **CC BY-SA** (Wikipedia 스타일)

#### 상업적 사용 금지
→ **CC BY-NC**

#### 수정 금지 (원본 유지)
→ **CC BY-ND**

#### 완전히 자유롭게 (출처 표시도 불필요)
→ **CC0 (Public Domain)**

---

## 실무 추천

### 오픈소스 프로젝트
```
코드: MIT License
문서: CC BY 4.0
```

### 개인 블로그/기술 문서
```
CC BY 4.0
```

### 회사 공식 문서
```
All Rights Reserved 또는 CC BY-ND
```

### 학습 자료
```
CC BY-SA 4.0
```

### 예제 코드
```
MIT License 또는 CC0
```

---

## 라이선스 파일 생성

### GitHub에서 자동 생성
1. 저장소 생성 시 "Add a license" 선택
2. 또는 "Add file" → "Create new file" → 파일명 `LICENSE` 입력
3. 템플릿 선택

### 수동 생성
```bash
# LICENSE 파일 생성
touch LICENSE

# MIT License 내용 추가
# https://opensource.org/licenses/MIT 에서 복사
```

---

## 주의사항

### 라이선스 변경
- 기존 코드의 라이선스는 변경 불가
- 새 버전부터만 변경 가능
- 기여자 동의 필요

### 라이선스 호환성
- MIT → GPL: 가능
- GPL → MIT: 불가능
- Apache 2.0 → GPL v3: 가능
- GPL v2 → Apache 2.0: 불가능
- CC BY → CC BY-SA: 가능
- CC BY-SA → CC BY: 불가능
- BSD → MIT: 가능

**호환성 규칙:**
- 자유로운 라이선스 → 제한적 라이선스: 가능
- 제한적 라이선스 → 자유로운 라이선스: 불가능

### 여러 라이선스 혼합
```markdown
## License

- 코드: MIT License
- 문서: CC BY 4.0
- 이미지: CC BY-NC 4.0
```

---

---

## 자주 묻는 질문 (FAQ)

### Q1: 라이선스 없이 공개하면?
**A:** 기본적으로 "All Rights Reserved" (모든 권리 보유)로 간주됩니다. 다른 사람이 사용할 수 없습니다.

### Q2: MIT와 Apache 2.0 중 뭘 선택해야 하나?
**A:** 
- 간단하게: **MIT**
- 특허 관련 프로젝트: **Apache 2.0**

### Q3: GPL 코드를 내 프로젝트에 사용하면?
**A:** 내 프로젝트도 GPL로 공개해야 합니다. (카피레프트)

### Q4: MIT 코드를 상업적으로 사용해도 되나?
**A:** 네, 가능합니다. 라이선스 표시만 유지하면 됩니다.

### Q5: CC BY와 MIT의 차이는?
**A:**
- **MIT**: 소프트웨어 코드용
- **CC BY**: 문서/콘텐츠용

### Q6: 여러 라이선스를 섞어 쓸 수 있나?
**A:** 네, 가능합니다.
```markdown
- 코드: MIT License
- 문서: CC BY 4.0
- 이미지: CC BY-NC 4.0
```

### Q7: 라이선스를 나중에 변경할 수 있나?
**A:** 
- 기존 버전: 변경 불가
- 새 버전: 변경 가능 (단, 기여자 동의 필요)

### Q8: 출처 표시는 어떻게 하나?
**A:**
```markdown
Based on [Project Name](URL) by [Author Name]
Licensed under MIT License
```

### Q9: 개인 프로젝트에도 라이선스가 필요한가?
**A:** 공개하려면 필요합니다. 없으면 다른 사람이 사용할 수 없습니다.

### Q10: 가장 무난한 라이선스는?
**A:**
- 코드: **MIT License**
- 문서: **CC BY 4.0**

---

## 라이선스 위반 시

### 위반 사례
- 라이선스 표시 제거
- GPL 코드를 독점 소프트웨어에 사용
- CC BY-NC 콘텐츠를 상업적으로 사용
- 출처 표시 없이 사용

### 대응 방법
1. 위반자에게 연락
2. 라이선스 준수 요청
3. 법적 조치 (최후 수단)

---

## 실전 팁 (Tips)

### Tip 1: 라이선스는 프로젝트 시작 시 결정
나중에 변경하기 어렵습니다. 처음부터 명확히 하세요.

### Tip 2: LICENSE 파일은 프로젝트 루트에
```
project/
├── LICENSE          ← 여기
├── README.md
└── src/
```

### Tip 3: README.md에도 라이선스 명시
```markdown
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

### Tip 4: 소스 파일 헤더에 간단히 표시
```python
# Copyright (c) 2026 Your Name
# SPDX-License-Identifier: MIT
```

### Tip 5: 의존성 라이선스 확인
사용하는 라이브러리의 라이선스도 확인하세요.

```bash
# Python
pip-licenses

# Node.js
npm install -g license-checker
license-checker

# 수동 확인
cat node_modules/package-name/LICENSE
```

### Tip 6: GPL 주의
GPL 라이브러리를 사용하면 내 프로젝트도 GPL이 됩니다.

### Tip 7: 듀얼 라이선스
상업적 사용은 유료, 오픈소스는 무료로 제공 가능
```markdown
## License

- Open Source: GPL v3
- Commercial: Contact us for licensing
```

### Tip 8: 기여자 라이선스 동의 (CLA)
큰 프로젝트는 기여자에게 CLA 서명 요청
```markdown
## Contributing

By contributing, you agree that your contributions will be licensed under the MIT License.
```

### Tip 9: 저작권 연도 업데이트
```markdown
Copyright (c) 2024-2026 Your Name
```

### Tip 10: SPDX 식별자 사용
간단하고 명확한 라이선스 표시
```markdown
SPDX-License-Identifier: MIT
SPDX-License-Identifier: Apache-2.0
SPDX-License-Identifier: GPL-3.0-or-later
```

### Tip 11: 라이선스 배지 추가
README.md에 시각적으로 표시
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
```

### Tip 12: 다국어 라이선스
영어 + 한국어 병기
```markdown
## License / 라이선스

This project is licensed under the MIT License.
이 프로젝트는 MIT 라이선스를 따릅니다.
```

### Tip 13: 예외 조항 추가 가능
```markdown
## License

GPL-3.0 with the following exception:
Linking this library statically or dynamically is permitted without GPL requirements.
```

### Tip 14: 라이선스 자동 체크
GitHub Actions로 자동 검증
```yaml
# .github/workflows/license-check.yml
name: License Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check licenses
        run: |
          npm install -g license-checker
          license-checker --production --onlyAllow 'MIT;Apache-2.0;BSD'
```

### Tip 15: 상업적 사용 문의 연락처
```markdown
## License

MIT License for open source use.

For commercial licensing, please contact: siasia.linux@gmail.com
```

---

## 빠른 결정 플로우차트

```
코드인가? 문서인가?
    │
    ├─ 코드
    │   │
    │   ├─ 최대한 자유롭게? → MIT
    │   ├─ 특허 보호 필요? → Apache 2.0
    │   └─ 오픈소스 유지? → GPL v3
    │
    └─ 문서/콘텐츠
        │
        ├─ 자유롭게 사용? → CC BY
        ├─ 오픈소스 유지? → CC BY-SA
        ├─ 상업적 사용 금지? → CC BY-NC
        └─ 수정 금지? → CC BY-ND
```

---

## 체크리스트

프로젝트 공개 전 확인사항:

- [ ] LICENSE 파일 생성
- [ ] README.md에 라이선스 명시
- [ ] 소스 파일 헤더에 저작권 표시
- [ ] 의존성 라이선스 확인
- [ ] 라이선스 배지 추가 (선택)
- [ ] NOTICE 파일 생성 (Apache 2.0인 경우)
- [ ] 기여 가이드에 라이선스 동의 명시
- [ ] .gitignore에 민감한 정보 제외

---

## 참고 링크

- [Choose a License](https://choosealicense.com/) - 라이선스 선택 도구
- [Creative Commons](https://creativecommons.org/licenses/) - CC 라이선스 공식 사이트
- [Open Source Initiative](https://opensource.org/licenses) - OSI 승인 라이선스 목록
- [TLDRLegal](https://tldrlegal.com/) - 라이선스 요약 정보
- [GitHub Licensing Guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) - GitHub 라이선스 가이드

---

## 요약

| 목적                       | 추천 라이선스 |
|----------------------------|---------------|
| 오픈소스 코드 (자유)       | MIT           |
| 오픈소스 코드 (특허 보호)  | Apache 2.0    |
| 오픈소스 코드 (카피레프트) | GPL v3        |
| 기술 문서 (자유)           | CC BY 4.0     |
| 기술 문서 (동일 조건)      | CC BY-SA 4.0  |
| 공식 문서 (수정 금지)      | CC BY-ND 4.0  |
| 학습 자료                  | CC BY-SA 4.0  |
| 완전 자유                  | CC0           |

**가장 많이 사용되는 조합:**
- 코드: **MIT License**
- 문서: **CC BY 4.0**

---

## GitHub에서 라이선스 사용하기

### 1. 저장소 생성 시 라이선스 추가

```bash
# GitHub 웹에서:
1. New repository 클릭
2. "Add a README file" 체크
3. "Choose a license" 드롭다운에서 선택
   - MIT License
   - Apache License 2.0
   - GNU GPLv3
   - 등등
4. Create repository
```

### 2. 기존 저장소에 라이선스 추가

#### 방법 1: GitHub 웹에서

```bash
1. 저장소 메인 페이지
2. "Add file" → "Create new file"
3. 파일명: LICENSE
4. 오른쪽에 "Choose a license template" 버튼 클릭
5. 라이선스 선택 → Review and submit
6. Commit
```

#### 방법 2: 로컬에서

```bash
# 1. LICENSE 파일 생성
cd your-project
touch LICENSE

# 2. 라이선스 내용 추가 (MIT 예시)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# 3. Git에 추가 및 커밋
git add LICENSE
git commit -m "Add MIT License"
git push origin main
```

### 3. README.md에 라이선스 표시

```markdown
# Project Name

프로젝트 설명...

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

© 2026 Your Name
```

### 4. 라이선스 배지 추가

```markdown
# Project Name

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

프로젝트 설명...
```

**다양한 라이선스 배지:**

```markdown
<!-- MIT -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Apache 2.0 -->
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

<!-- GPL v3 -->
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<!-- BSD 3-Clause -->
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

<!-- CC BY 4.0 -->
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

<!-- CC BY-SA 4.0 -->
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

<!-- CC BY-NC 4.0 -->
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
```

### 5. 소스 파일에 라이선스 헤더 추가

#### Python 예시
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2026 Your Name

This file is part of ProjectName.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

def main():
    pass
```

#### JavaScript 예시
```javascript
/**
 * Copyright (c) 2026 Your Name
 * 
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

function main() {
    // code
}
```

#### Bash 예시
```bash
#!/bin/bash
# Copyright (c) 2026 Your Name
# Licensed under the MIT License
# See LICENSE file in the project root for full license information.

echo "Hello World"
```

### 6. 여러 라이선스 사용 시

```bash
# 프로젝트 구조
project/
├── LICENSE-CODE          # MIT License (코드용)
├── LICENSE-DOCS          # CC BY 4.0 (문서용)
├── README.md
├── src/                  # 코드
└── docs/                 # 문서
```

**README.md에 명시:**
```markdown
## License

This project uses multiple licenses:

- **Source Code**: [MIT License](LICENSE-CODE)
- **Documentation**: [CC BY 4.0](LICENSE-DOCS)
- **Images**: CC BY-NC 4.0

See individual LICENSE files for details.
```

### 7. GitHub 라이선스 자동 인식

GitHub는 다음 파일명을 자동으로 인식합니다:
- `LICENSE`
- `LICENSE.md`
- `LICENSE.txt`
- `COPYING`
- `COPYING.md`

**확인 방법:**
- 저장소 메인 페이지 오른쪽에 라이선스 표시됨
- "View license" 링크 클릭 가능

---

## GitHub 라이선스 실전 가이드

### 시나리오 1: 개인 오픈소스 프로젝트

```bash
# 1. 저장소 생성
git init my-project
cd my-project

# 2. LICENSE 파일 생성 (MIT)
curl -o LICENSE https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt

# 3. 저작권 정보 수정
sed -i 's/\[year\]/2026/g' LICENSE
sed -i 's/\[fullname\]/Your Name/g' LICENSE

# 4. README.md 생성
cat > README.md << 'EOF'
# My Project

## License

MIT License - see [LICENSE](LICENSE) file
EOF

# 5. Git 커밋
git add LICENSE README.md
git commit -m "Initial commit with MIT License"

# 6. GitHub에 푸시
git remote add origin https://github.com/siasia86/my-project.git
git push -u origin main
```

### 시나리오 2: 회사 프로젝트 (Apache 2.0)

```bash
# 1. LICENSE 파일
curl -o LICENSE https://www.apache.org/licenses/LICENSE-2.0.txt

# 2. NOTICE 파일 생성 (Apache 2.0 필수)
cat > NOTICE << 'EOF'
ProjectName
Copyright 2026 Company Name

This product includes software developed at
Company Name (https://company.com/).
EOF

# 3. 각 소스 파일 헤더
cat > src/main.py << 'EOF'
# Copyright 2026 Company Name
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def main():
    pass
EOF

# 4. Git 커밋
git add LICENSE NOTICE src/
git commit -m "Add Apache 2.0 License"
git push
```

### 시나리오 3: 문서 프로젝트 (CC BY 4.0)

```bash
# 1. LICENSE 파일
cat > LICENSE << 'EOF'
Creative Commons Attribution 4.0 International License

This work is licensed under the Creative Commons Attribution 4.0 
International License. To view a copy of this license, visit 
http://creativecommons.org/licenses/by/4.0/ or send a letter to 
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
EOF

# 2. README.md
cat > README.md << 'EOF'
# Documentation Project

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## License

This documentation is licensed under [CC BY 4.0](LICENSE).

You are free to:
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit

© 2026 Your Name
EOF

# 3. 각 문서 하단에 추가
cat >> docs/guide.md << 'EOF'

---

© 2026 Your Name. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
EOF
```

### 시나리오 4: 듀얼 라이선스 (오픈소스 + 상업)

```bash
# 1. LICENSE-OPEN (GPL v3)
curl -o LICENSE-OPEN https://www.gnu.org/licenses/gpl-3.0.txt

# 2. LICENSE-COMMERCIAL
cat > LICENSE-COMMERCIAL << 'EOF'
Commercial License

For commercial use, please contact:
- Email: siasia.linux@gmail.com
- Website: https://company.com/licensing

Pricing and terms available upon request.
EOF

# 3. README.md
cat > README.md << 'EOF'
# Project Name

## Dual Licensing

This project is available under two licenses:

### Open Source (GPL v3)
Free for open source projects. See [LICENSE-OPEN](LICENSE-OPEN).

### Commercial License
For proprietary/commercial use. Contact siasia.linux@gmail.com.

Choose the license that best fits your needs.
EOF
```

---

## GitHub 라이선스 팁

### Tip 1: GitHub 라이선스 템플릿 활용

```bash
# GitHub CLI 사용
gh repo create my-project --public --license mit

# 또는 웹에서 저장소 생성 시 라이선스 선택
```

### Tip 2: 라이선스 변경 시 주의

```bash
# 기존 라이선스 백업
cp LICENSE LICENSE.old

# 새 라이선스 적용
# 주의: 기존 기여자 동의 필요!

# CHANGELOG.md에 기록
cat >> CHANGELOG.md << 'EOF'
## [2.0.0] - 2026-03-11
### Changed
- License changed from MIT to Apache 2.0
EOF
```

### Tip 3: 의존성 라이선스 확인

```bash
# Node.js
npm install -g license-checker
license-checker --summary

# Python
pip install pip-licenses
pip-licenses

# Go
go-licenses report ./... --template=licenses.tpl
```

### Tip 4: GitHub Actions로 라이선스 체크

```yaml
# .github/workflows/license-check.yml
name: License Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check LICENSE file exists
        run: |
          if [ ! -f LICENSE ]; then
            echo "ERROR: LICENSE file not found"
            exit 1
          fi
      
      - name: Check license headers
        run: |
          # Python 파일 체크
          for file in $(find . -name "*.py"); do
            if ! grep -q "Copyright" "$file"; then
              echo "WARNING: No copyright in $file"
            fi
          done
```

### Tip 5: 라이선스 호환성 체크

```bash
# 사용 중인 라이선스 확인
npm ls --depth=0 | grep -i license

# GPL 라이선스 찾기 (주의 필요)
license-checker --onlyAllow 'MIT;Apache-2.0;BSD' --failOn 'GPL'
```

### Tip 6: SPDX 식별자 사용

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Your Name

def main():
    pass
```

**SPDX 식별자 목록:**
- `MIT`
- `Apache-2.0`
- `GPL-3.0-or-later`
- `BSD-3-Clause`
- `CC-BY-4.0`

### Tip 7: 기여자 라이선스 동의 (CLA)

```markdown
# CONTRIBUTING.md

## License Agreement

By contributing to this project, you agree that your contributions 
will be licensed under the MIT License.

All contributions must include:
- Copyright notice
- License header in source files
```

### Tip 8: 라이선스 자동 헤더 추가

```bash
#!/bin/bash
# add-license-header.sh

HEADER="# Copyright (c) 2026 Your Name
# SPDX-License-Identifier: MIT
"

for file in $(find src -name "*.py"); do
    if ! grep -q "Copyright" "$file"; then
        echo "$HEADER" | cat - "$file" > temp && mv temp "$file"
        echo "Added header to $file"
    fi
done
```

### Tip 9: 라이선스 변경 이력 관리

```markdown
# LICENSE-HISTORY.md

## License History

### 2026-03-11: Changed to Apache 2.0
- Reason: Patent protection needed
- Previous: MIT License
- Approved by: All contributors

### 2024-01-01: Initial MIT License
- Reason: Maximum freedom for users
```

### Tip 10: GitHub 저장소 설정 확인

```bash
# GitHub API로 라이선스 확인
curl https://api.github.com/repos/siasia86/system-engineering-resources | jq '.license'

# 출력 예시:
# {
#   "key": "mit",
#   "name": "MIT License",
#   "spdx_id": "MIT",
#   "url": "https://api.github.com/licenses/mit"
# }
```

---

## 빠른 시작 체크리스트

### GitHub에 프로젝트 올리기 전

- [ ] LICENSE 파일 생성
- [ ] README.md에 라이선스 섹션 추가
- [ ] 라이선스 배지 추가 (선택)
- [ ] 소스 파일에 저작권 헤더 추가
- [ ] 의존성 라이선스 확인
- [ ] .gitignore 설정
- [ ] CONTRIBUTING.md 작성 (오픈소스인 경우)
- [ ] 민감 정보 제거 확인

### 명령어 요약

```bash
# 1. LICENSE 파일 생성
touch LICENSE
# (내용 추가)

# 2. README.md 업데이트
echo "## License\n\nMIT License - see [LICENSE](LICENSE)" >> README.md

# 3. Git 커밋
git add LICENSE README.md
git commit -m "Add MIT License"

# 4. GitHub에 푸시
git push origin main
```

---

## 출처 표시를 원할 때 추천 라이선스

### 문서/콘텐츠인 경우

#### CC BY 4.0 (가장 추천)

**특징:**
- 출처 표시 필수
- 상업적 사용 가능
- 수정 가능
- 재배포 가능
- 가장 자유로운 CC 라이선스

**사용 방법:**

```markdown
# 프로젝트 제목

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## License

이 문서는 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 라이선스를 따릅니다.

**출처를 표시하면 자유롭게 사용할 수 있습니다.**

© 2026 sj_del
```

**LICENSE 파일:**
```bash
cat > LICENSE << 'EOF'
Creative Commons Attribution 4.0 International License (CC BY 4.0)

Copyright (c) 2026 sj_del

This work is licensed under the Creative Commons Attribution 4.0 
International License.

To view a copy of this license, visit:
http://creativecommons.org/licenses/by/4.0/

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, 
  even commercially

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the 
  license, and indicate if changes were made. You may do so in any 
  reasonable manner, but not in any way that suggests the licensor 
  endorses you or your use.

No additional restrictions — You may not apply legal terms or technological 
measures that legally restrict others from doing anything the license permits.
EOF
```

**문서 하단 표시:**
```markdown
---

## 문서 정보

- **작성자**: 홍길동
- **최초 작성**: 2026-03-11
- **최종 수정**: 2026-03-11
- **라이선스**: CC BY 4.0

이 문서는 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 라이선스를 따릅니다.  
출처를 표시하면 자유롭게 사용, 수정, 배포할 수 있습니다.

© 2026 홍길동
```

#### CC BY-SA 4.0 (Wikipedia 스타일)

**특징:**
- 출처 표시 필수
- 수정본도 같은 라이선스 유지 (Share-Alike)
- 상업적 사용 가능
- 오픈소스 정신 유지

**사용 방법:**

```markdown
# 프로젝트 제목

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

## License

이 문서는 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 라이선스를 따릅니다.

**수정본도 같은 라이선스로 공유해야 합니다.**

© 2026 sj_del
```

---

### 코드인 경우

#### MIT License (가장 추천)

**특징:**
- 저작권 및 라이선스 표시 필수
- 상업적 사용 가능
- 매우 간단하고 자유로움
- 가장 많이 사용되는 라이선스

**사용 방법:**

```markdown
# 프로젝트 제목

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## License

MIT License

Copyright (c) 2026 sj_del

라이선스 전문은 [LICENSE](LICENSE) 파일을 참조하세요.
```

**LICENSE 파일:**
```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 sj_del

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

**소스 파일 헤더:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2026 sj_del

This file is part of [Project Name].

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""
```

#### Apache License 2.0 (특허 보호)

**특징:**
- 저작권 및 라이선스 표시 필수
- 변경 사항 명시 필수
- 특허 보호 조항 포함
- 기업 친화적

**사용 방법:**

```markdown
# 프로젝트 제목

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## License

Apache License 2.0

Copyright 2026 sj_del

라이선스 전문은 [LICENSE](LICENSE) 파일을 참조하세요.
```

**LICENSE 파일:**
```bash
cat > LICENSE << 'EOF'
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright 2026 sj_del

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
EOF
```

**NOTICE 파일 (Apache 2.0 필수):**
```bash
cat > NOTICE << 'EOF'
[Project Name]
Copyright 2026 sj_del

This product includes software developed by sj_del.
EOF
```

---

## 출처 표시 라이선스 비교

| 라이선스         | 출처 표시 | 상업적 사용 | 수정 | 동일 조건 | 추천 용도            |
|------------------|-----------|-------------|------|-----------|----------------------|
| **CC BY 4.0**    | 필수      |             |      |           | 문서/콘텐츠 (자유)   |
| **CC BY-SA 4.0** | 필수      |             |      | 필수      | 문서 (오픈소스 유지) |
| **MIT**          | 필수      |             |      |           | 코드 (간단)          |
| **Apache 2.0**   | 필수      |             |      |           | 코드 (특허 보호)     |

---

## 실전 예시

### 예시 1: 기술 문서 프로젝트

```bash
# 프로젝트 구조
docs-project/
├── LICENSE              # CC BY 4.0
├── README.md
└── docs/
    ├── guide.md
    └── tutorial.md
```

**README.md:**
```markdown
# 기술 문서 프로젝트

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

이 프로젝트는 [주제]에 대한 기술 문서입니다.

## License

이 문서는 [CC BY 4.0](LICENSE) 라이선스를 따릅니다.

**출처를 표시하면 자유롭게:**
- 복사 및 재배포
- 수정 및 변형
- 상업적 사용

© 2026 홍길동
```

**각 문서 하단:**
```markdown
---

© 2026 홍길동. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
```

### 예시 2: 오픈소스 코드 프로젝트

```bash
# 프로젝트 구조
code-project/
├── LICENSE              # MIT License
├── README.md
├── src/
│   ├── main.py
│   └── utils.py
└── docs/
    └── README.md
```

**README.md:**
```markdown
# 코드 프로젝트

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

\`\`\`bash
pip install my-project
\`\`\`

## License

MIT License

Copyright (c) 2026 홍길동

라이선스 전문은 [LICENSE](LICENSE) 파일을 참조하세요.
```

**src/main.py:**
```python
#!/usr/bin/env python3
# Copyright (c) 2026 홍길동
# SPDX-License-Identifier: MIT

def main():
    print("Hello World")

if __name__ == "__main__":
    main()
```

### 예시 3: 혼합 프로젝트 (코드 + 문서)

```bash
# 프로젝트 구조
mixed-project/
├── LICENSE-CODE         # MIT License
├── LICENSE-DOCS         # CC BY 4.0
├── README.md
├── src/                 # 코드
└── docs/                # 문서
```

**README.md:**
```markdown
# 혼합 프로젝트

## License

이 프로젝트는 여러 라이선스를 사용합니다:

- **소스 코드**: [MIT License](LICENSE-CODE)
  - `src/` 디렉토리의 모든 코드
  
- **문서**: [CC BY 4.0](LICENSE-DOCS)
  - `docs/` 디렉토리의 모든 문서
  - README.md 파일

자세한 내용은 각 LICENSE 파일을 참조하세요.

© 2026 홍길동
```

---

## 빠른 결정 가이드

```
출처 표시를 원한다면?
    │
    ├─ 문서/콘텐츠인가?
    │   │
    │   ├─ 자유롭게 사용 → CC BY 4.0 ⭐
    │   └─ 오픈소스 유지 → CC BY-SA 4.0
    │
    └─ 코드인가?
        │
        ├─ 간단하게 → MIT License ⭐
        └─ 특허 보호 → Apache 2.0
```

---

## 출처 표시 예시

### 다른 사람이 내 작업물을 사용할 때

**CC BY 4.0 출처 표시:**
```markdown
이 문서는 [홍길동의 기술 가이드](https://github.com/user/repo)를 
기반으로 작성되었습니다. (CC BY 4.0)
```

**MIT License 출처 표시:**
```python
# Based on code from https://github.com/user/repo
# Copyright (c) 2026 홍길동
# Licensed under the MIT License
```

---

## 명령어 요약

### CC BY 4.0 적용
```bash
# LICENSE 파일 생성
curl -o LICENSE https://creativecommons.org/licenses/by/4.0/legalcode.txt

# README.md 업데이트
cat >> README.md << 'EOF'

## License

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

© 2026 sj_del. Licensed under CC BY 4.0.
EOF

git add LICENSE README.md
git commit -m "Add CC BY 4.0 License"
git push
```

### MIT License 적용
```bash
# LICENSE 파일 생성 (GitHub에서)
# 또는 로컬에서:
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 sj_del

[MIT License 전문]
EOF

# README.md 업데이트
cat >> README.md << 'EOF'

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MIT License - see [LICENSE](LICENSE) file.
EOF

git add LICENSE README.md
git commit -m "Add MIT License"
git push
```

---
