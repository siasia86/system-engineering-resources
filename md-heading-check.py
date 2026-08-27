#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
md-heading-check.py — Markdown 헤딩 구조 및 목차 앵커 검증
==========================================================

사용법:
    python md-heading-check.py <file_or_dir> [file_or_dir ...]
    python md-heading-check.py README.md
    python md-heading-check.py -v /root/32_system-engineering-resources/
    python md-heading-check.py --no-anchor 01_fundamentals/

검증 대상:
    - anchor    : #앵커 링크가 실제 헤딩과 일치하는지
    - number    : H2 번호가 1부터 연속인지 (## 1., ## 2., ...)
    - level     : 헤딩 레벨이 건너뛰지 않는지 (H2 -> H4 금지)
    - duplicate : 링크가 참조하는 앵커에 중복 헤딩이 있는지

검증 제외:
    - 코드블록 내부 헤딩과 링크
    - http:// https:// 외부 링크
    - 다른 파일을 가리키는 앵커 (path.md#anchor)

md-link-check.py 는 상대경로 링크만 검증하고 #anchor 링크를 의도적으로
제외합니다. 이 스크립트가 그 범위를 담당합니다.

설정:
    대상 경로의 상위 디렉터리에서 .md-heading-check.toml 을 자동 탐색합니다.

    exclude_dirs  = ["99_archive"]          제외할 디렉토리명 또는 상대 경로
    exclude_files = ["vim_airline.md"]      제외할 파일명
    skip_checks   = ["level"]               전역으로 제외할 검사 항목

    [[file_skip]]                           파일별 검사 항목 제외
    path   = "01_fundamentals/linux/vim_airline.md"
    checks = ["level"]
    reason = "외부 프로젝트 README 원본"

종료 코드:
    0 = 이슈 없음
    1 = 이슈 발견
"""

VERSION = "26.08.27.7"

import argparse
import os
import re
import sys
import tomllib

# ── patterns ──────────────────────────────────────────────────────────────────

HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
# 링크 텍스트에 대괄호가 한 겹 중첩될 수 있습니다 (예: `[4. /proc/[pid]/ns/](#...)`).
# 중첩을 처리하지 않으면 해당 링크를 인식하지 못해 앵커 검사에서 누락됩니다.
ANCHOR_LINK_PATTERN = re.compile(r'\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(#([^)]+)\)')
FENCE_PATTERN = re.compile(r'^(\s*)(`{3,}|~{3,})\s*(.*)$')
NUMBERED_H2_PATTERN = re.compile(r'^(\d+)(?:-(\d+))?\.\s+')

# github-slugger 가 제거하는 문자 집합입니다.
# 출처: github.com/Flet/github-slugger (master/regex.js) 의 문자 클래스를 이식했습니다.
# 하이픈(U+002D), 밑줄(U+005F), 공백, 문자, 숫자, 이모지는 유지됩니다.
# 직접 편집하지 않고 원본이 변경되면 다시 이식합니다.
SLUG_REMOVE_PATTERN = re.compile('[' + (
    "\\x00-\\x1F!-,\\.\\/:-@\\[-\\^`\\{-\\xA9\\xAB-\\xB4\\xB6-\\xB9\\xBB-\\xBF\\xD7\\xF7\\u02C2-\\u02C5\\u02D2-\\u02DF\\u02E5-\\u02EB\\u02ED\\u02EF-\\u02FF\\u0375\\u0378\\u0379\\u037E\\u0380-\\u0385\\u0387\\u038B\\u038D\\u03A2\\u03F6\\u0482\\u0530\\u0557\\u0558\\u055A-\\u055F\\u0589-\\u0590\\u05BE\\u05C0\\u05C3\\u05C6\\u05C8-\\u05CF\\u05EB-\\u05EE\\u05F3-\\u060F\\u061B-\\u061F\\u066A-\\u066D\\u06D4\\u06DD\\u06DE\\u06E9\\u06FD\\u06FE\\u0700-\\u070F\\u074B\\u074C\\u07B2-\\u07BF\\u07F6-\\u07F9\\u07FB\\u07FC\\u07FE\\u07FF\\u082E-\\u083F\\u085C-\\u085F\\u086B-\\u089F\\u08B5\\u08C8-\\u08D2\\u08E2\\u0964\\u0965\\u0970\\u0984\\u098D\\u098E\\u0991\\u0992\\u09A9\\u09B1\\u09B3-\\u09B5\\u09BA\\u09BB\\u09C5\\u09C6\\u09C9\\u09CA\\u09CF-\\u09D6\\u09D8-\\u09DB\\u09DE\\u09E4\\u09E5\\u09F2-\\u09FB\\u09FD\\u09FF\\u0A00\\u0A04\\u0A0B-\\u0A0E\\u0A11\\u0A12\\u0A29\\u0A31\\u0A34\\u0A37\\u0A3A\\u0A3B\\u0A3D\\u0A43-\\u0A46\\u0A49\\u0A4A\\u0A4E-\\u0A50\\u0A52-\\u0A58\\u0A5D\\u0A5F-\\u0A65\\u0A76-\\u0A80\\u0A84\\u0A8E\\u0A92\\u0AA9\\u0AB1\\u0AB4\\u0ABA\\u0ABB\\u0AC6\\u0ACA\\u0ACE\\u0ACF\\u0AD1-\\u0ADF\\u0AE4\\u0AE5\\u0AF0-\\u0AF8\\u0B00\\u0B04\\u0B0D\\u0B0E\\u0B11\\u0B12\\u0B29\\u0B31\\u0B34\\u0B3A\\u0B3B\\u0B45\\u0B46\\u0B49\\u0B4A\\u0B4E-\\u0B54\\u0B58-\\u0B5B\\u0B5E\\u0B64\\u0B65\\u0B70\\u0B72-\\u0B81\\u0B84\\u0B8B-\\u0B8D\\u0B91\\u0B96-\\u0B98\\u0B9B\\u0B9D\\u0BA0-\\u0BA2\\u0BA5-\\u0BA7\\u0BAB-\\u0BAD\\u0BBA-\\u0BBD\\u0BC3-\\u0BC5\\u0BC9\\u0BCE\\u0BCF\\u0BD1-\\u0BD6\\u0BD8-\\u0BE5\\u0BF0-\\u0BFF\\u0C0D\\u0C11\\u0C29\\u0C3A-\\u0C3C\\u0C45\\u0C49\\u0C4E-\\u0C54\\u0C57\\u0C5B-\\u0C5F\\u0C64\\u0C65\\u0C70-\\u0C7F\\u0C84\\u0C8D\\u0C91\\u0CA9\\u0CB4\\u0CBA\\u0CBB\\u0CC5\\u0CC9\\u0CCE-\\u0CD4\\u0CD7-\\u0CDD\\u0CDF\\u0CE4\\u0CE5\\u0CF0\\u0CF3-\\u0CFF\\u0D0D\\u0D11\\u0D45\\u0D49\\u0D4F-\\u0D53\\u0D58-\\u0D5E\\u0D64\\u0D65\\u0D70-\\u0D79\\u0D80\\u0D84\\u0D97-\\u0D99\\u0DB2\\u0DBC\\u0DBE\\u0DBF\\u0DC7-\\u0DC9\\u0DCB-\\u0DCE\\u0DD5\\u0DD7\\u0DE0-\\u0DE5\\u0DF0\\u0DF1\\u0DF4-\\u0E00\\u0E3B-\\u0E3F\\u0E4F\\u0E5A-\\u0E80\\u0E83\\u0E85\\u0E8B\\u0EA4\\u0EA6\\u0EBE\\u0EBF\\u0EC5\\u0EC7\\u0ECE\\u0ECF\\u0EDA\\u0EDB\\u0EE0-\\u0EFF\\u0F01-\\u0F17\\u0F1A-\\u0F1F\\u0F2A-\\u0F34\\u0F36\\u0F38\\u0F3A-\\u0F3D\\u0F48\\u0F6D-\\u0F70\\u0F85\\u0F98\\u0FBD-\\u0FC5\\u0FC7-\\u0FFF\\u104A-\\u104F\\u109E\\u109F\\u10C6\\u10C8-\\u10CC\\u10CE\\u10CF\\u10FB\\u1249\\u124E\\u124F\\u1257\\u1259\\u125E\\u125F\\u1289\\u128E\\u128F\\u12B1\\u12B6\\u12B7\\u12BF\\u12C1\\u12C6\\u12C7\\u12D7\\u1311\\u1316\\u1317\\u135B\\u135C\\u1360-\\u137F\\u1390-\\u139F\\u13F6\\u13F7\\u13FE-\\u1400\\u166D\\u166E\\u1680\\u169B-\\u169F\\u16EB-\\u16ED\\u16F9-\\u16FF\\u170D\\u1715-\\u171F\\u1735-\\u173F\\u1754-\\u175F\\u176D\\u1771\\u1774-\\u177F\\u17D4-\\u17D6\\u17D8-\\u17DB\\u17DE\\u17DF\\u17EA-\\u180A\\u180E\\u180F\\u181A-\\u181F\\u1879-\\u187F\\u18AB-\\u18AF\\u18F6-\\u18FF\\u191F\\u192C-\\u192F\\u193C-\\u1945\\u196E\\u196F\\u1975-\\u197F\\u19AC-\\u19AF\\u19CA-\\u19CF\\u19DA-\\u19FF\\u1A1C-\\u1A1F\\u1A5F\\u1A7D\\u1A7E\\u1A8A-\\u1A8F\\u1A9A-\\u1AA6\\u1AA8-\\u1AAF\\u1AC1-\\u1AFF\\u1B4C-\\u1B4F\\u1B5A-\\u1B6A\\u1B74-\\u1B7F\\u1BF4-\\u1BFF\\u1C38-\\u1C3F\\u1C4A-\\u1C4C\\u1C7E\\u1C7F\\u1C89-\\u1C8F\\u1CBB\\u1CBC\\u1CC0-\\u1CCF\\u1CD3\\u1CFB-\\u1CFF\\u1DFA\\u1F16\\u1F17\\u1F1E\\u1F1F\\u1F46\\u1F47\\u1F4E\\u1F4F\\u1F58\\u1F5A\\u1F5C\\u1F5E\\u1F7E\\u1F7F\\u1FB5\\u1FBD\\u1FBF-\\u1FC1\\u1FC5\\u1FCD-\\u1FCF\\u1FD4\\u1FD5\\u1FDC-\\u1FDF\\u1FED-\\u1FF1\\u1FF5\\u1FFD-\\u203E\\u2041-\\u2053\\u2055-\\u2070\\u2072-\\u207E\\u2080-\\u208F\\u209D-\\u20CF\\u20F1-\\u2101\\u2103-\\u2106\\u2108\\u2109\\u2114\\u2116-\\u2118\\u211E-\\u2123\\u2125\\u2127\\u2129\\u212E\\u213A\\u213B\\u2140-\\u2144\\u214A-\\u214D\\u214F-\\u215F\\u2189-\\u24B5\\u24EA-\\u2BFF\\u2C2F\\u2C5F\\u2CE5-\\u2CEA\\u2CF4-\\u2CFF\\u2D26\\u2D28-\\u2D2C\\u2D2E\\u2D2F\\u2D68-\\u2D6E\\u2D70-\\u2D7E\\u2D97-\\u2D9F\\u2DA7\\u2DAF\\u2DB7\\u2DBF\\u2DC7\\u2DCF\\u2DD7\\u2DDF\\u2E00-\\u2E2E\\u2E30-\\u3004\\u3008-\\u3020\\u3030\\u3036\\u3037\\u303D-\\u3040\\u3097\\u3098\\u309B\\u309C\\u30A0\\u30FB\\u3100-\\u3104\\u3130\\u318F-\\u319F\\u31C0-\\u31EF\\u3200-\\u33FF\\u4DC0-\\u4DFF\\u9FFD-\\u9FFF\\uA48D-\\uA4CF\\uA4FE\\uA4FF\\uA60D-\\uA60F\\uA62C-\\uA63F\\uA673\\uA67E\\uA6F2-\\uA716\\uA720\\uA721\\uA789\\uA78A\\uA7C0\\uA7C1\\uA7CB-\\uA7F4\\uA828-\\uA82B\\uA82D-\\uA83F\\uA874-\\uA87F\\uA8C6-\\uA8CF\\uA8DA-\\uA8DF\\uA8F8-\\uA8FA\\uA8FC\\uA92E\\uA92F\\uA954-\\uA95F\\uA97D-\\uA97F\\uA9C1-\\uA9CE\\uA9DA-\\uA9DF\\uA9FF\\uAA37-\\uAA3F\\uAA4E\\uAA4F\\uAA5A-\\uAA5F\\uAA77-\\uAA79\\uAAC3-\\uAADA\\uAADE\\uAADF\\uAAF0\\uAAF1\\uAAF7-\\uAB00\\uAB07\\uAB08\\uAB0F\\uAB10\\uAB17-\\uAB1F\\uAB27\\uAB2F\\uAB5B\\uAB6A-\\uAB6F\\uABEB\\uABEE\\uABEF\\uABFA-\\uABFF\\uD7A4-\\uD7AF\\uD7C7-\\uD7CA\\uD7FC-\\uD7FF\\uE000-\\uF8FF\\uFA6E\\uFA6F\\uFADA-\\uFAFF\\uFB07-\\uFB12\\uFB18-\\uFB1C\\uFB29\\uFB37\\uFB3D\\uFB3F\\uFB42\\uFB45\\uFBB2-\\uFBD2\\uFD3E-\\uFD4F\\uFD90\\uFD91\\uFDC8-\\uFDEF\\uFDFC-\\uFDFF\\uFE10-\\uFE1F\\uFE30-\\uFE32\\uFE35-\\uFE4C\\uFE50-\\uFE6F\\uFE75\\uFEFD-\\uFF0F\\uFF1A-\\uFF20\\uFF3B-\\uFF3E\\uFF40\\uFF5B-\\uFF65\\uFFBF-\\uFFC1\\uFFC8\\uFFC9\\uFFD0\\uFFD1\\uFFD8\\uFFD9\\uFFDD-\\uFFFF]|\\uD800[\\uDC0C\\uDC27\\uDC3B\\uDC3E\\uDC4E\\uDC4F\\uDC5E-\\uDC7F\\uDCFB-\\uDD3F\\uDD75-\\uDDFC\\uDDFE-\\uDE7F\\uDE9D-\\uDE9F\\uDED1-\\uDEDF\\uDEE1-\\uDEFF\\uDF20-\\uDF2C\\uDF4B-\\uDF4F\\uDF7B-\\uDF7F\\uDF9E\\uDF9F\\uDFC4-\\uDFC7\\uDFD0\\uDFD6-\\uDFFF]|\\uD801[\\uDC9E\\uDC9F\\uDCAA-\\uDCAF\\uDCD4-\\uDCD7\\uDCFC-\\uDCFF\\uDD28-\\uDD2F\\uDD64-\\uDDFF\\uDF37-\\uDF3F\\uDF56-\\uDF5F\\uDF68-\\uDFFF]|\\uD802[\\uDC06\\uDC07\\uDC09\\uDC36\\uDC39-\\uDC3B\\uDC3D\\uDC3E\\uDC56-\\uDC5F\\uDC77-\\uDC7F\\uDC9F-\\uDCDF\\uDCF3\\uDCF6-\\uDCFF\\uDD16-\\uDD1F\\uDD3A-\\uDD7F\\uDDB8-\\uDDBD\\uDDC0-\\uDDFF\\uDE04\\uDE07-\\uDE0B\\uDE14\\uDE18\\uDE36\\uDE37\\uDE3B-\\uDE3E\\uDE40-\\uDE5F\\uDE7D-\\uDE7F\\uDE9D-\\uDEBF\\uDEC8\\uDEE7-\\uDEFF\\uDF36-\\uDF3F\\uDF56-\\uDF5F\\uDF73-\\uDF7F\\uDF92-\\uDFFF]|\\uD803[\\uDC49-\\uDC7F\\uDCB3-\\uDCBF\\uDCF3-\\uDCFF\\uDD28-\\uDD2F\\uDD3A-\\uDE7F\\uDEAA\\uDEAD-\\uDEAF\\uDEB2-\\uDEFF\\uDF1D-\\uDF26\\uDF28-\\uDF2F\\uDF51-\\uDFAF\\uDFC5-\\uDFDF\\uDFF7-\\uDFFF]|\\uD804[\\uDC47-\\uDC65\\uDC70-\\uDC7E\\uDCBB-\\uDCCF\\uDCE9-\\uDCEF\\uDCFA-\\uDCFF\\uDD35\\uDD40-\\uDD43\\uDD48-\\uDD4F\\uDD74\\uDD75\\uDD77-\\uDD7F\\uDDC5-\\uDDC8\\uDDCD\\uDDDB\\uDDDD-\\uDDFF\\uDE12\\uDE38-\\uDE3D\\uDE3F-\\uDE7F\\uDE87\\uDE89\\uDE8E\\uDE9E\\uDEA9-\\uDEAF\\uDEEB-\\uDEEF\\uDEFA-\\uDEFF\\uDF04\\uDF0D\\uDF0E\\uDF11\\uDF12\\uDF29\\uDF31\\uDF34\\uDF3A\\uDF45\\uDF46\\uDF49\\uDF4A\\uDF4E\\uDF4F\\uDF51-\\uDF56\\uDF58-\\uDF5C\\uDF64\\uDF65\\uDF6D-\\uDF6F\\uDF75-\\uDFFF]|\\uD805[\\uDC4B-\\uDC4F\\uDC5A-\\uDC5D\\uDC62-\\uDC7F\\uDCC6\\uDCC8-\\uDCCF\\uDCDA-\\uDD7F\\uDDB6\\uDDB7\\uDDC1-\\uDDD7\\uDDDE-\\uDDFF\\uDE41-\\uDE43\\uDE45-\\uDE4F\\uDE5A-\\uDE7F\\uDEB9-\\uDEBF\\uDECA-\\uDEFF\\uDF1B\\uDF1C\\uDF2C-\\uDF2F\\uDF3A-\\uDFFF]|\\uD806[\\uDC3B-\\uDC9F\\uDCEA-\\uDCFE\\uDD07\\uDD08\\uDD0A\\uDD0B\\uDD14\\uDD17\\uDD36\\uDD39\\uDD3A\\uDD44-\\uDD4F\\uDD5A-\\uDD9F\\uDDA8\\uDDA9\\uDDD8\\uDDD9\\uDDE2\\uDDE5-\\uDDFF\\uDE3F-\\uDE46\\uDE48-\\uDE4F\\uDE9A-\\uDE9C\\uDE9E-\\uDEBF\\uDEF9-\\uDFFF]|\\uD807[\\uDC09\\uDC37\\uDC41-\\uDC4F\\uDC5A-\\uDC71\\uDC90\\uDC91\\uDCA8\\uDCB7-\\uDCFF\\uDD07\\uDD0A\\uDD37-\\uDD39\\uDD3B\\uDD3E\\uDD48-\\uDD4F\\uDD5A-\\uDD5F\\uDD66\\uDD69\\uDD8F\\uDD92\\uDD99-\\uDD9F\\uDDAA-\\uDEDF\\uDEF7-\\uDFAF\\uDFB1-\\uDFFF]|\\uD808[\\uDF9A-\\uDFFF]|\\uD809[\\uDC6F-\\uDC7F\\uDD44-\\uDFFF]|[\\uD80A\\uD80B\\uD80E-\\uD810\\uD812-\\uD819\\uD824-\\uD82B\\uD82D\\uD82E\\uD830-\\uD833\\uD837\\uD839\\uD83D\\uD83F\\uD87B-\\uD87D\\uD87F\\uD885-\\uDB3F\\uDB41-\\uDBFF][\\uDC00-\\uDFFF]|\\uD80D[\\uDC2F-\\uDFFF]|\\uD811[\\uDE47-\\uDFFF]|\\uD81A[\\uDE39-\\uDE3F\\uDE5F\\uDE6A-\\uDECF\\uDEEE\\uDEEF\\uDEF5-\\uDEFF\\uDF37-\\uDF3F\\uDF44-\\uDF4F\\uDF5A-\\uDF62\\uDF78-\\uDF7C\\uDF90-\\uDFFF]|\\uD81B[\\uDC00-\\uDE3F\\uDE80-\\uDEFF\\uDF4B-\\uDF4E\\uDF88-\\uDF8E\\uDFA0-\\uDFDF\\uDFE2\\uDFE5-\\uDFEF\\uDFF2-\\uDFFF]|\\uD821[\\uDFF8-\\uDFFF]|\\uD823[\\uDCD6-\\uDCFF\\uDD09-\\uDFFF]|\\uD82C[\\uDD1F-\\uDD4F\\uDD53-\\uDD63\\uDD68-\\uDD6F\\uDEFC-\\uDFFF]|\\uD82F[\\uDC6B-\\uDC6F\\uDC7D-\\uDC7F\\uDC89-\\uDC8F\\uDC9A-\\uDC9C\\uDC9F-\\uDFFF]|\\uD834[\\uDC00-\\uDD64\\uDD6A-\\uDD6C\\uDD73-\\uDD7A\\uDD83\\uDD84\\uDD8C-\\uDDA9\\uDDAE-\\uDE41\\uDE45-\\uDFFF]|\\uD835[\\uDC55\\uDC9D\\uDCA0\\uDCA1\\uDCA3\\uDCA4\\uDCA7\\uDCA8\\uDCAD\\uDCBA\\uDCBC\\uDCC4\\uDD06\\uDD0B\\uDD0C\\uDD15\\uDD1D\\uDD3A\\uDD3F\\uDD45\\uDD47-\\uDD49\\uDD51\\uDEA6\\uDEA7\\uDEC1\\uDEDB\\uDEFB\\uDF15\\uDF35\\uDF4F\\uDF6F\\uDF89\\uDFA9\\uDFC3\\uDFCC\\uDFCD]|\\uD836[\\uDC00-\\uDDFF\\uDE37-\\uDE3A\\uDE6D-\\uDE74\\uDE76-\\uDE83\\uDE85-\\uDE9A\\uDEA0\\uDEB0-\\uDFFF]|\\uD838[\\uDC07\\uDC19\\uDC1A\\uDC22\\uDC25\\uDC2B-\\uDCFF\\uDD2D-\\uDD2F\\uDD3E\\uDD3F\\uDD4A-\\uDD4D\\uDD4F-\\uDEBF\\uDEFA-\\uDFFF]|\\uD83A[\\uDCC5-\\uDCCF\\uDCD7-\\uDCFF\\uDD4C-\\uDD4F\\uDD5A-\\uDFFF]|\\uD83B[\\uDC00-\\uDDFF\\uDE04\\uDE20\\uDE23\\uDE25\\uDE26\\uDE28\\uDE33\\uDE38\\uDE3A\\uDE3C-\\uDE41\\uDE43-\\uDE46\\uDE48\\uDE4A\\uDE4C\\uDE50\\uDE53\\uDE55\\uDE56\\uDE58\\uDE5A\\uDE5C\\uDE5E\\uDE60\\uDE63\\uDE65\\uDE66\\uDE6B\\uDE73\\uDE78\\uDE7D\\uDE7F\\uDE8A\\uDE9C-\\uDEA0\\uDEA4\\uDEAA\\uDEBC-\\uDFFF]|\\uD83C[\\uDC00-\\uDD2F\\uDD4A-\\uDD4F\\uDD6A-\\uDD6F\\uDD8A-\\uDFFF]|\\uD83E[\\uDC00-\\uDFEF\\uDFFA-\\uDFFF]|\\uD869[\\uDEDE-\\uDEFF]|\\uD86D[\\uDF35-\\uDF3F]|\\uD86E[\\uDC1E\\uDC1F]|\\uD873[\\uDEA2-\\uDEAF]|\\uD87A[\\uDFE1-\\uDFFF]|\\uD87E[\\uDE1E-\\uDFFF]|\\uD884[\\uDF4B-\\uDFFF]|\\uDB40[\\uDC00-\\uDCFF\\uDDF0-\\uDFFF"
) + ']')

# 번호를 요구하지 않는 관례적 H2
UNNUMBERED_ALLOWED = {'목차', '참고 자료', '통계', '개요', 'changelog'}

ALL_CHECKS = ('anchor', 'number', 'level', 'duplicate', 'toc')
CONFIG_NAME = '.md-heading-check.toml'
DEFAULT_EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules'}


# ── config ────────────────────────────────────────────────────────────────────

def find_config_path(target):
    """대상 경로에서 상위로 올라가며 설정 파일을 탐색."""
    current = os.path.abspath(target)
    if not os.path.isdir(current):
        current = os.path.dirname(current)
    while True:
        candidate = os.path.join(current, CONFIG_NAME)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def load_config(config_path=None, target=None):
    """TOML 설정을 읽어 정규화된 dict 반환."""
    config = {
        'exclude_dirs': sorted(DEFAULT_EXCLUDE_DIRS),
        'exclude_files': [],
        'skip_checks': [],
        'file_skip': [],
        'path': None,
    }
    selected = config_path or (find_config_path(target) if target else None)
    if not selected:
        if config_path:
            raise FileNotFoundError(f"config not found: {config_path}")
        return config
    selected = os.path.abspath(selected)
    if not os.path.isfile(selected):
        raise FileNotFoundError(f"config not found: {selected}")
    with open(selected, 'rb') as f:
        data = tomllib.load(f)

    allowed = {'exclude_dirs', 'exclude_files', 'skip_checks', 'file_skip'}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unknown config key: {', '.join(sorted(unknown))}")

    for key in ('exclude_dirs', 'exclude_files', 'skip_checks'):
        for value in data.get(key, []):
            if value not in config[key]:
                config[key].append(value)
    for entry in data.get('file_skip', []):
        if 'path' not in entry:
            raise ValueError("file_skip entry requires 'path'")
        config['file_skip'].append({
            'path': os.path.normpath(entry['path']),
            'checks': list(entry.get('checks', ALL_CHECKS)),
            'reason': entry.get('reason', ''),
        })
    config['path'] = selected
    config['root'] = os.path.dirname(selected)
    return config


def enabled_for(filepath, config, base_enabled):
    """파일별 file_skip 설정을 적용한 검사 항목 집합 반환."""
    root = config.get('root')
    if not root:
        return base_enabled, ''
    try:
        rel = os.path.normpath(os.path.relpath(os.path.abspath(filepath), root))
    except ValueError:
        return base_enabled, ''
    for entry in config['file_skip']:
        if entry['path'] == rel:
            return base_enabled - set(entry['checks']), entry['reason']
    return base_enabled, ''


# ── utilities ─────────────────────────────────────────────────────────────────

def make_anchor(heading):
    """헤딩 텍스트를 GitHub 앵커 형식으로 변환.

    github-slugger 규칙을 따릅니다. 소문자로 바꾼 뒤 구두점을 제거하고 공백을
    하이픈으로 치환합니다. 하이픈과 밑줄은 제거하지 않습니다. `TIME_WAIT` 나
    `__init__` 처럼 밑줄이 들어간 헤딩이 있으므로 이 구분이 중요합니다.
    """
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', heading.strip())  # 링크는 텍스트만
    text = text.lower()
    text = SLUG_REMOVE_PATTERN.sub('', text)
    return text.replace(' ', '-')


def strip_code_blocks(content):
    """코드블록 내부를 빈 줄로 치환하여 줄 번호를 보존.

    CommonMark 규칙을 따릅니다.

    - 닫는 펜스는 여는 펜스와 같은 문자이고 개수가 같거나 많아야 합니다.
    - 닫는 펜스에는 정보 문자열(```python 등)이 없어야 합니다.
    - 펜스의 들여쓰기는 최대 3칸입니다. 4칸 이상은 내용으로 취급합니다.

    이 규칙이 없으면 중첩 예시가 있는 문서에서 코드 영역을 잘못 판정합니다.
    """
    result = []
    fence_char = None
    fence_len = 0
    for line in content.split('\n'):
        m = FENCE_PATTERN.match(line)
        # 들여쓰기 4칸 이상은 펜스가 아닙니다 (CommonMark: 최대 3칸)
        if m and len(m.group(1).expandtabs(4)) <= 3:
            marker = m.group(2)
            char, length, info = marker[0], len(marker), m.group(3).strip()
            if fence_char is None:
                fence_char, fence_len = char, length
                result.append('')
                continue
            if char == fence_char and length >= fence_len and not info:
                fence_char, fence_len = None, 0
                result.append('')
                continue
            # 정보 문자열이 있거나 문자가 다르면 닫는 펜스가 아님 (내용으로 취급)
            result.append('')
            continue
        result.append('' if fence_char else line)
    return '\n'.join(result)


def collect_md_files(paths, exclude_dirs=None, exclude_files=None):
    """대상 경로에서 .md 파일 목록 수집. 제외 설정을 적용합니다."""
    skip_dirs = set(exclude_dirs or DEFAULT_EXCLUDE_DIRS) | DEFAULT_EXCLUDE_DIRS
    skip_files = set(exclude_files or [])
    files = []
    for path in paths:
        if os.path.isfile(path) and path.endswith('.md'):
            if os.path.basename(path) not in skip_files:
                files.append(path)
        elif os.path.isdir(path):
            base = os.path.abspath(path)
            for root, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs
                           if d not in skip_dirs
                           and os.path.normpath(
                               os.path.relpath(os.path.join(root, d), base)
                           ) not in skip_dirs]
                files.extend(os.path.join(root, n) for n in sorted(names)
                             if n.endswith('.md') and n not in skip_files)
    return sorted(set(files))


# ── core functions ────────────────────────────────────────────────────────────

def extract_headings(content):
    """(레벨, 텍스트, 줄번호) 목록 반환."""
    headings = []
    for lineno, line in enumerate(content.split('\n'), 1):
        m = HEADING_PATTERN.match(line)
        if m:
            headings.append((len(m.group(1)), m.group(2), lineno))
    return headings


def check_anchors(headings, content):
    """#앵커 링크가 실제 헤딩과 일치하는지 검증."""
    valid = {make_anchor(text) for _, text, _ in headings}
    issues = []
    for lineno, line in enumerate(content.split('\n'), 1):
        for anchor in ANCHOR_LINK_PATTERN.findall(line):
            if anchor not in valid:
                issues.append((lineno, 'anchor', f'앵커 대상 없음: #{anchor}'))
    return issues


def check_numbering(headings):
    """H2 번호가 1부터 연속인지 검증.

    두 가지 확장 표기를 지원합니다.

    - 범위 (`## 5-10. 제목`): 한 섹션이 여러 번호를 포괄합니다. 외부 규칙 번호에
      대응하는 문서에서 사용합니다.
    - 하위 절 (`## 1-1. 제목`): 직전 섹션의 하위 항목이므로 번호를 진행시키지
      않습니다.

    뒤 숫자가 앞 숫자보다 크면 범위, 작거나 같으면 하위 절로 판정합니다.
    """
    issues = []
    numbered = []
    for level, text, lineno in headings:
        if level != 2:
            continue
        m = NUMBERED_H2_PATTERN.match(text)
        if not m:
            continue
        start = int(m.group(1))
        second = int(m.group(2)) if m.group(2) else None
        if second is not None and second > start:
            numbered.append((start, second, False, text, lineno))   # 범위: 5-10.
        elif second is not None:
            numbered.append((start, start, True, text, lineno))     # 하위 절: 1-1.
        else:
            numbered.append((start, start, False, text, lineno))
    if not numbered:
        return issues

    start, _, _, text, lineno = numbered[0]
    if start != 1:
        issues.append((lineno, 'number', f'H2 번호가 1로 시작하지 않음: {text}'))
    for i in range(1, len(numbered)):
        prev_end = numbered[i - 1][1]
        cur_start, _, is_sub, text, lineno = numbered[i]
        expected = prev_end if is_sub else prev_end + 1
        if cur_start != expected:
            issues.append((lineno, 'number',
                           f'H2 번호 불연속: {prev_end} -> {cur_start} ({text})'))
    return issues


def check_levels(headings):
    """헤딩 레벨이 건너뛰지 않는지 검증."""
    issues = []
    prev = 0
    for level, text, lineno in headings:
        if prev and level > prev + 1:
            issues.append((lineno, 'level',
                           f'헤딩 레벨 건너뜀: H{prev} -> H{level} ({text})'))
        prev = level
    return issues


def check_duplicates(headings, content):
    """링크가 참조하는 앵커에 중복 헤딩이 있는지 검증.

    반복 섹션(CHANGELOG의 `### Added` 등)은 정상 형식이므로, 앵커 링크가
    실제로 가리키는 대상만 검사합니다. 중복된 앵커로는 첫 번째 헤딩만
    도달할 수 있어 링크가 의도한 위치로 가지 않습니다.
    """
    referenced = set()
    for line in content.split('\n'):
        referenced.update(ANCHOR_LINK_PATTERN.findall(line))
    if not referenced:
        return []

    issues = []
    seen = {}
    for level, text, lineno in headings:
        anchor = make_anchor(text)
        if anchor in seen:
            if anchor in referenced:
                issues.append((lineno, 'duplicate',
                               f'참조되는 앵커가 중복됨: #{anchor} '
                               f'(L{seen[anchor]}과 동일, 링크는 첫 번째로만 이동)'))
        else:
            seen[anchor] = lineno
    return issues


def check_toc(headings, content):
    """목차가 본문의 번호 있는 H2를 모두 담고 있는지 검증.

    `anchor` 검사는 목차가 없는 섹션을 가리키는 경우(목차 -> 본문)를 잡습니다.
    이 검사는 반대 방향(본문 -> 목차)을 봅니다. 본문에 H2를 추가하고 목차에
    넣지 않으면 어느 검사도 잡지 못했습니다.

    번호 있는 H2만 대상으로 합니다. `목차`, `참고 자료`, `통계` 같은 관례적
    섹션은 목차에 넣지 않는 문서가 많아 제외합니다.
    """
    toc_idx = next((i for i, (lv, text, _) in enumerate(headings)
                    if lv == 2 and text.strip() == '목차'), None)
    if toc_idx is None:
        return []

    # 목차 섹션 범위: '## 목차' 다음 H2 까지
    start = headings[toc_idx][2]
    end = next((ln for lv, _, ln in headings[toc_idx + 1:] if lv == 2), None)
    lines = content.split('\n')
    toc_body = '\n'.join(lines[start:(end - 1) if end else len(lines)])
    listed = set(ANCHOR_LINK_PATTERN.findall(toc_body))

    issues = []
    for lv, text, lineno in headings:
        if lv != 2 or not NUMBERED_H2_PATTERN.match(text):
            continue
        if make_anchor(text) not in listed:
            issues.append((lineno, 'toc', f'목차에 없는 섹션: {text}'))
    return issues


def check_file(filepath, enabled):
    """단일 파일 검증. 이슈 목록과 헤딩 수 반환."""
    try:
        with open(filepath, encoding='utf-8') as f:
            raw = f.read()
    except (OSError, UnicodeError) as exc:
        return [(0, 'read', f'읽기 실패: {exc}')], 0

    content = strip_code_blocks(raw)
    headings = extract_headings(content)

    issues = []
    if 'anchor' in enabled:
        issues += check_anchors(headings, content)
    if 'number' in enabled:
        issues += check_numbering(headings)
    if 'level' in enabled:
        issues += check_levels(headings)
    if 'duplicate' in enabled:
        issues += check_duplicates(headings, content)
    if 'toc' in enabled:
        issues += check_toc(headings, content)
    return sorted(issues), len(headings)


# ── entry point ───────────────────────────────────────────────────────────────

def parse_args():
    """커맨드라인 인자 파싱."""
    parser = argparse.ArgumentParser(
        description='Markdown 헤딩 구조 및 목차 앵커 검증',
        epilog='Examples:\n'
               '  python md-heading-check.py README.md\n'
               '  python md-heading-check.py /root/32_system-engineering-resources/\n'
               '  python md-heading-check.py -v README.md        파일별 헤딩 수 출력\n'
               '  python md-heading-check.py --no-number docs/   번호 검사 제외\n'
               '\nNotes:\n'
               '  - md-link-check.py 는 #anchor 링크를 검증 대상에서 제외합니다.\n'
               '  - 코드블록 내부의 헤딩과 링크는 검사하지 않습니다.\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('paths', nargs='+', help='.md 파일 또는 디렉토리')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='파일별 헤딩 수 출력')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='이슈만 출력')
    parser.add_argument('--no-anchor', action='store_true', help='앵커 검사 제외')
    parser.add_argument('--no-number', action='store_true', help='번호 검사 제외')
    parser.add_argument('--no-level', action='store_true', help='레벨 검사 제외')
    parser.add_argument('--no-duplicate', action='store_true', help='중복 검사 제외')
    parser.add_argument('--no-toc', action='store_true', help='목차 완결성 검사 제외')
    parser.add_argument('-c', '--config', metavar='FILE',
                        help=f'TOML 설정 파일 (미지정 시 {CONFIG_NAME} 자동 탐색)')
    parser.add_argument('-E', '--exclude-dir', action='append', default=[],
                        dest='exclude_dirs', metavar='DIR',
                        help='제외할 디렉토리명 (여러 번 사용 가능)')
    parser.add_argument('-X', '--exclude-file', action='append', default=[],
                        dest='exclude_files', metavar='FILE',
                        help='제외할 파일명 (여러 번 사용 가능)')
    parser.add_argument('-V', '--version', action='version',
                        version=f'%(prog)s {VERSION}')
    return parser.parse_args()


def main():
    """메인 실행."""
    args = parse_args()

    try:
        config = load_config(args.config, args.paths[0])
    except (FileNotFoundError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"설정 오류: {exc}", file=sys.stderr)
        sys.exit(1)

    enabled = set(ALL_CHECKS) - set(config['skip_checks'])
    for name in list(ALL_CHECKS):
        if getattr(args, f'no_{name}'):
            enabled.discard(name)
    if not enabled:
        print("모든 검사가 제외되었습니다")
        sys.exit(0)

    exclude_dirs = list(config['exclude_dirs']) + list(args.exclude_dirs)
    exclude_files = list(config['exclude_files']) + list(args.exclude_files)
    files = collect_md_files(args.paths, exclude_dirs, exclude_files)
    if not files:
        print("대상 .md 파일 없음")
        sys.exit(0)

    if config['path'] and not args.quiet:
        print(f"[설정] {config['path']}")

    total_issues = 0
    total_headings = 0
    failed = []
    skipped = []

    for filepath in files:
        file_enabled, reason = enabled_for(filepath, config, enabled)
        if not file_enabled:
            skipped.append((filepath, reason))
            continue
        if file_enabled != enabled:
            skipped.append((filepath, reason))
        issues, count = check_file(filepath, file_enabled)
        total_headings += count
        if issues:
            total_issues += len(issues)
            failed.append((filepath, issues))
        elif args.verbose and not args.quiet:
            print(f"  ✅ {os.path.relpath(filepath)} ({count} headings)")

    if failed:
        for filepath, issues in failed:
            print(f"\n❌ {os.path.relpath(filepath)}")
            for lineno, kind, message in issues:
                loc = f"L{lineno}" if lineno else "-"
                print(f"   [{kind}] {loc}: {message}")
    elif not args.quiet:
        print("✅ 헤딩 구조 정상")

    if skipped and not args.quiet:
        print(f"\n[예외] {len(skipped)}개 파일에 검사 항목 제외 적용")
        if args.verbose:
            for filepath, reason in skipped:
                note = f" — {reason}" if reason else ""
                print(f"   {os.path.relpath(filepath)}{note}")

    if not args.quiet:
        print(f"\n{'─' * 60}")
        print(f"검사 파일: {len(files)}개 | 헤딩: {total_headings}개 | "
              f"이슈: {total_issues}건")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
