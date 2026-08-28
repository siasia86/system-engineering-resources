# Neovim 활용 가이드

Neovim은 Vim의 모달 편집 방식을 유지하면서 Lua 설정, 비동기 API, floating window, 내장 LSP client, Tree-sitter 연동, headless 실행을 제공하는 편집기입니다. Vim의 기본 조작은 [Vim 사용법](vim.md)을 참고하고, 이 문서는 Neovim 고유 기능을 중심으로 설명합니다.

## 목차

| 섹션                                                                                    |
|-----------------------------------------------------------------------------------------|
| [1. Neovim 전용 기능](#1-neovim-전용-기능) / [2. 실행과 진단](#2-실행과-진단)           |
| [3. Lua 설정](#3-lua-설정) / [4. Neovim API](#4-neovim-api)                             |
| [5. LSP와 진단](#5-lsp와-진단) / [6. Tree-sitter](#6-tree-sitter)                       |
| [7. Headless 자동화](#7-headless-자동화) / [8. Vim과의 운영 경계](#8-vim과의-운영-경계) |

---

## 1. Neovim 전용 기능

Vim 기본 명령보다 Neovim에서 차이가 큰 영역은 다음과 같습니다.

- `init.lua` 기반 Lua 설정
- `vim.api`를 통한 buffer·window·autocmd 제어
- floating window와 popup UI
- 내장 LSP client와 diagnostic API
- Tree-sitter 기반 구문 트리 연동
- `--headless`를 이용한 CI·자동화 실행
- 외부 UI와 통신할 수 있는 RPC 구조

Neovim의 장점은 단축키 자체보다 편집기 내부 객체를 Lua 코드로 제어할 수 있다는 점에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 실행과 진단

### `nvim` — 실행 옵션

```bash
nvim file.txt
nvim --clean file.txt
nvim --headless -u NONE +'lua print(vim.fn.getcwd())' +qa
nvim --version
```

- `nvim`: 파일을 엽니다.
- `nvim --clean`: 사용자 설정과 플러그인을 제외하고 실행합니다.
- `nvim --headless`: 화면 없이 명령을 실행합니다.
- `nvim --version`: Neovim 버전과 포함 기능을 확인합니다.

### `:checkhealth` — 환경 진단

Neovim 안에서 다음 명령을 실행합니다.

```vim
:checkhealth
:checkhealth vim.lsp
:checkhealth provider
```

플러그인, Python·Node.js provider, LSP 관련 환경 문제를 진단할 때 사용합니다.

`--clean` 실행은 설정 파일이나 플러그인을 변경하지 않으므로 문제 재현의 첫 단계로 적합합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Lua 설정

Neovim의 기본 사용자 설정 파일은 일반적으로 다음 경로입니다.

```text
~/.config/nvim/init.lua
```

### `init.lua` — 기본 옵션과 키 매핑

```lua
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.tabstop = 4
vim.opt.termguicolors = true

vim.g.mapleader = " "

vim.keymap.set("n", "<leader>w", "<cmd>write<cr>", {
  desc = "Save file",
})

vim.keymap.set("n", "<leader>q", "<cmd>quit<cr>", {
  desc = "Quit window",
})
```

`vim.keymap.set()`은 모드, 키, 동작, 설명을 Lua 값으로 표현할 수 있어 기존 `:map` 계열 명령보다 확장하기 쉽습니다.

### Lua 함수 매핑

명령 문자열 대신 Lua 함수를 직접 연결할 수 있습니다.

```lua
vim.keymap.set("n", "<leader>p", function()
  local file = vim.api.nvim_buf_get_name(0)
  vim.notify("current file: " .. file)
end, {
  desc = "Show current file",
})
```

Normal mode에서 `<leader>p`를 누르면 현재 buffer의 경로가 알림 창으로 표시됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Neovim API

`vim.api`는 현재 buffer, window, tabpage, autocmd 등을 직접 제어하는 Neovim API입니다.

### `nvim_create_autocmd()` — 저장 이벤트 처리

Python 파일을 저장한 뒤 알림을 표시합니다.

```lua
vim.api.nvim_create_autocmd("BufWritePost", {
  pattern = "*.py",
  callback = function(args)
    vim.notify("saved: " .. args.file)
  end,
})
```

### `nvim_open_win()` — floating window

다음 코드를 `init.lua`에 추가하면 `<leader>m`으로 임시 floating window를 열 수 있습니다.

```lua
vim.keymap.set("n", "<leader>m", function()
  local buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, {
    "Neovim scratch window",
    "Press q to close",
  })

  local width = 40
  local height = 4
  local ui = vim.api.nvim_list_uis()[1]
  local win = vim.api.nvim_open_win(buf, true, {
    relative = "editor",
    width = width,
    height = height,
    row = math.floor((ui.height - height) / 2),
    col = math.floor((ui.width - width) / 2),
    style = "minimal",
    border = "rounded",
  })

  vim.keymap.set("n", "q", function()
    vim.api.nvim_win_close(win, true)
  end, { buffer = buf })
end, {
  desc = "Open scratch window",
})
```

floating window는 로그 미리보기, 임시 결과, 도움말, 진단 메시지 표시 등에 사용할 수 있습니다.

### 주요 API 범위

| API                                  | 용도                 |
|--------------------------------------|----------------------|
| `vim.api.nvim_get_current_buf()`     | 현재 buffer 식별     |
| `vim.api.nvim_buf_get_lines()`       | buffer 내용 읽기     |
| `vim.api.nvim_buf_set_lines()`       | buffer 내용 쓰기     |
| `vim.api.nvim_get_current_win()`     | 현재 window 식별     |
| `vim.api.nvim_open_win()`            | floating window 열기 |
| `vim.api.nvim_create_autocmd()`      | 이벤트 처리 등록     |
| `vim.api.nvim_create_user_command()` | 사용자 명령 생성     |

[⬆ 목차로 돌아가기](#목차)

---

## 5. LSP와 진단

Neovim에는 LSP(Language Server Protocol) client가 내장되어 있습니다.

> LSP(Language Server Protocol): 편집기와 언어 서버가 정의 이동, 자동완성, 참조 검색, 오류 진단 기능을 통신하는 표준 프로토콜입니다.

언어 서버 실행 파일과 연결 설정은 별도로 필요하지만, client와 진단 결과 표시 API는 Neovim에 포함되어 있습니다.

### `vim.lsp.start()` — 언어 서버 시작

다음 예시는 `pyright-langserver`가 설치되어 있다는 전제의 최소 설정입니다.

```lua
local root = vim.fs.root(0, { "pyproject.toml", ".git" })

if root then
  vim.lsp.start({
    name = "pyright",
    cmd = { "pyright-langserver", "--stdio" },
    root_dir = root,
  })
end
```

### LSP·diagnostic 명령

LSP client가 연결된 buffer에서 다음 명령을 실행할 수 있습니다.

```vim
:lua vim.lsp.buf.definition()
:lua vim.lsp.buf.references()
:lua vim.lsp.buf.hover()
:lua vim.diagnostic.open_float()
:lua vim.diagnostic.setloclist()
```

- `definition()`: 심볼 정의로 이동합니다.
- `references()`: 참조 목록을 표시합니다.
- `hover()`: 심볼 설명을 표시합니다.
- `open_float()`: 현재 줄의 오류·경고를 표시합니다.
- `setloclist()`: 진단 결과를 location list에 등록합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. Tree-sitter

Neovim은 Tree-sitter parser와 연동하여 문서를 토큰이 아닌 구문 트리 단위로 다룰 수 있습니다. 문법 강조, 구조 기반 선택, syntax 분석에 활용됩니다.

Tree-sitter parser가 준비된 파일에서 다음 명령을 실행합니다.

```vim
:Inspect
:InspectTree
```

- `:Inspect`: 커서 위치의 highlight·syntax 정보를 확인합니다.
- `:InspectTree`: 현재 buffer의 구문 트리를 확인합니다.

`:InspectTree` 결과가 표시되지 않으면 해당 파일 형식의 parser가 설치되어 있는지 확인합니다. parser 설치 방식은 사용하는 Neovim 버전과 plugin 구성에 따라 다릅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Headless 자동화

Neovim은 화면 없이 Lua와 Ex 명령을 실행할 수 있습니다. CI, 문서 변환, 파일 일괄 수정에 사용할 수 있습니다.

### 현재 작업 디렉토리 출력

```bash
nvim --headless -u NONE \
  +'lua print(vim.fn.getcwd())' \
  +qa
```

### 파일 치환 후 저장

```bash
nvim --headless -u NONE /tmp/example.txt \
  +'%s/old/new/g' \
  +write \
  +qa
```

쉘에서 `%`를 직접 사용할 때는 Neovim 명령의 `%`가 그대로 전달되어야 합니다. 복잡한 변환은 Lua script로 분리하고, 실행 전 테스트 파일에서 결과를 확인합니다.

### 임시 설정으로 재현

```bash
nvim --clean --headless \
  +'lua print(vim.inspect(vim.api.nvim_list_uis()))' \
  +qa
```

`--clean`과 `--headless`를 함께 사용하면 사용자 설정과 UI 영향을 제외한 최소 동작을 확인할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. Vim과의 운영 경계

개발 PC에서는 Neovim을 주력으로 사용하고, 운영 서버와 장애 복구 환경에서는 Vim 명령을 기본 도구로 유지하는 방식이 실용적입니다.

- `~/.vimrc` 설정은 Neovim의 `~/.config/nvim/init.lua`로 그대로 복사하지 않습니다.
- Vimscript 설정은 Lua 문법으로 옮기거나 호환 설정을 별도로 구성합니다.
- 운영 서버에는 Neovim 설치를 전제하지 않고 `vi` 또는 `vim`으로 복구할 수 있어야 합니다.
- 플러그인에 의존하는 작업은 서버가 아닌 개발 환경이나 CI에서 수행합니다.
- `nvim --clean`으로 설정 문제와 plugin 문제를 분리해 진단합니다.

Neovim의 기본 모달 조작은 Vim과 공유되므로, 두 환경을 병행해도 Normal mode·검색·치환·매크로 사용법은 대부분 재사용할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Neovim Documentation: [neovim.io/doc](https://neovim.io/doc/) — ★★★☆☆
- Neovim API Reference: [neovim.io/doc/user/api.html](https://neovim.io/doc/user/api.html) — ★★★☆☆
- Neovim LSP: [neovim.io/doc/user/lsp.html](https://neovim.io/doc/user/lsp.html) — ★★★☆☆
- [Vim 사용법](vim.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-28

**마지막 업데이트**: 2026-08-28

© 2026 siasia86. Licensed under CC BY 4.0.
