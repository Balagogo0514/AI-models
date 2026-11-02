# Codex CLI 完整參考

> 資料來源：
> - OpenAI 官方文件：https://developers.openai.com/codex/cli 、https://developers.openai.com/codex/cli/reference 、https://developers.openai.com/codex/cli/slash-commands 、https://developers.openai.com/codex/quickstart 、https://developers.openai.com/codex/config-reference 、https://developers.openai.com/codex/permissions 、https://developers.openai.com/codex/environment-variables
> - 本機 CLI help：`codex-cli 0.137.0`
> - 更新日期：2026-06-05

> 說明：
> - 本文件以本機已安裝的 `codex-cli 0.137.0` 實際 `--help` 輸出為主。
> - 官方文件會持續更新；若你本機版本不同，請以 `codex --help` 與 `codex <subcommand> --help` 為準。
> - `Codex` 是 OpenAI 的終端機 coding agent；下文統一使用產品正式名稱 `Codex`。

---

## 零、快速速查

### 最常用指令

| 目的 | 指令 |
|------|------|
| 啟動互動模式 | `codex` |
| 帶 prompt 啟動 | `codex "fix the failing tests"` |
| 指定目錄 | `codex -C ./repo` |
| 非互動執行 | `codex exec "summarize this repository"` |
| 非互動 review | `codex review --uncommitted` |
| 恢復最近 session | `codex resume --last` |
| 從最近 session 分叉 | `codex fork --last` |
| 登入 | `codex login` |
| 檢查健康狀態 | `codex doctor --summary` |
| 列出 MCP servers | `codex mcp list` |
| 列出 plugins | `codex plugin list` |
| 顯示版本 | `codex -V` |

### 建議啟動組合

| 情境 | 指令 |
|------|------|
| 一般本機開發 | `codex -C . -s workspace-write -a on-request` |
| 嚴格安全模式 | `codex -C . -s read-only -a untrusted` |
| 非互動 JSON 輸出 | `codex exec --json "summarize the diff"` |
| 指定模型 | `codex --model gpt-5.5` |
| 啟用 web search | `codex --search` |

### 最常見 slash commands

| 指令 | 用途 |
|------|------|
| `/model` | 切換模型 |
| `/permissions` | 調整 approval / 權限模式 |
| `/status` | 查看目前 session 狀態 |
| `/diff` | 顯示目前變更 |
| `/review` | 對 working tree 做 review |
| `/mcp` | 查看可用 MCP tools |
| `/plugins` | 查看 plugins |
| `/clear` | 開新 chat 並清畫面 |
| `/resume` | 恢復舊 session |
| `/help` 或 `/` | 開啟 slash command 選單 |

### 最短工作流

```bash
codex -C . -s workspace-write -a on-request
codex review --uncommitted
codex resume --last
codex doctor
```

---

## 一、Codex CLI 是什麼

Codex CLI 是 OpenAI 的終端機型 coding agent。它支援：

- 互動式 TUI 工作流
- 非互動式執行
- 程式碼審查
- Sandbox 與 approval 控制
- MCP server 整合
- Plugin / marketplace 擴充
- Codex Cloud 與 Desktop App 整合

官方文件目前建議多數任務優先使用 `GPT-5.5`；若要改模型，可用 `--model` 或 `config.toml` 設定。

---

## 二、快速開始

### 安裝

官方 Quickstart 提供兩種常見安裝方式：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

也可以用：

```bash
npm install -g @openai/codex
brew install --cask codex
```

若已安裝，可檢查版本：

```bash
codex -V
```

本文件驗證版本：

```text
codex-cli 0.137.0
```

### 登入

互動登入：

```bash
codex login
```

用 API key 從 stdin 登入：

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

用 access token 從 stdin 登入：

```bash
printenv CODEX_ACCESS_TOKEN | codex login --with-access-token
```

檢查登入狀態：

```bash
codex login status
```

登出：

```bash
codex logout
```

### 第一個 session

```bash
codex
codex "explain this repository"
codex -C /path/to/repo
codex --model gpt-5.5
```

非互動單次執行：

```bash
codex exec "summarize this repository"
```

---

## 三、CLI 啟動語法

```text
codex [OPTIONS] [PROMPT]
codex [OPTIONS] <COMMAND> [ARGS]
```

如果沒有指定子命令，Codex 會進入互動式 CLI；如果提供 `PROMPT`，會把它當成初始需求。

---

## 四、頂層命令總覽

| 命令 | 說明 | 備註 |
|------|------|------|
| `codex` | 啟動互動式 TUI session | 可直接帶 prompt |
| `codex exec` | 非互動式執行任務 | 適合 CI / script |
| `codex review` | 非互動式程式碼審查 | 可 review branch / commit / uncommitted |
| `codex login` | 登入管理 | 含 `status` |
| `codex logout` | 移除已儲存憑證 | - |
| `codex mcp` | 管理外部 MCP servers | `list/get/add/remove/login/logout` |
| `codex plugin` | 管理 plugins | `add/list/remove/marketplace` |
| `codex mcp-server` | 以 stdio 啟動 Codex MCP server | 供其他 client 使用 |
| `codex app-server` | 啟動 / 管理 app-server | 實驗性 |
| `codex remote-control` | 管理可遠端控制的 app-server daemon | 實驗性 |
| `codex app` | 啟動 Codex Desktop App | 若未安裝會開啟 installer |
| `codex completion` | 產生 shell completion script | 支援 bash/fish/zsh/powershell 等 |
| `codex update` | 更新到最新版本 | - |
| `codex doctor` | 檢查安裝、設定、認證、執行環境 | 很實用 |
| `codex sandbox` | 在 Codex sandbox 中執行命令 | 偏診斷 / 驗證用途 |
| `codex debug` | Debug 工具 | `models/app-server/prompt-input` |
| `codex apply` | 套用 agent 產出的最新 diff | 適合配合 cloud task |
| `codex resume` | 恢復先前 session | 可用 `--last` |
| `codex archive` | 封存 session | - |
| `codex unarchive` | 解除封存 session | - |
| `codex fork` | 從既有 session 分叉 | 可用 `--last` |
| `codex cloud` | 瀏覽 / 執行 Codex Cloud tasks | 實驗性 |
| `codex exec-server` | 啟動 standalone exec-server | 實驗性 |
| `codex features` | 檢視與切換 feature flags | `list/enable/disable` |
| `codex help` | 顯示 help | - |

---

## 五、全域旗標

下列旗標適用於互動式主程式，很多子命令也會共用其中一部分。

| 旗標 | 說明 |
|------|------|
| `-c, --config <key=value>` | 覆寫 `config.toml` 設定，支援 dotted path，值會先以 TOML 解析 |
| `--enable <FEATURE>` | 啟用 feature flag，可重複 |
| `--disable <FEATURE>` | 停用 feature flag，可重複 |
| `--remote <ADDR>` | 連到遠端 app-server endpoint |
| `--remote-auth-token-env <ENV_VAR>` | 指定遠端連線 bearer token 所在環境變數 |
| `--strict-config` | 若 `config.toml` 有未知欄位就報錯 |
| `-i, --image <FILE>...` | 在初始 prompt 附加圖片 |
| `-m, --model <MODEL>` | 指定模型 |
| `--oss` | 使用 open-source provider |
| `--local-provider <OSS_PROVIDER>` | 搭配 `--oss` 指定 `lmstudio` 或 `ollama` |
| `-p, --profile <CONFIG_PROFILE_V2>` | 疊加 `$CODEX_HOME/<name>.config.toml` profile |
| `-s, --sandbox <SANDBOX_MODE>` | Sandbox 模式：`read-only` / `workspace-write` / `danger-full-access` |
| `--dangerously-bypass-approvals-and-sandbox` | 跳過 approval 與 sandbox，極危險 |
| `--dangerously-bypass-hook-trust` | 跳過 hook trust，極危險 |
| `-C, --cd <DIR>` | 指定工作根目錄 |
| `--add-dir <DIR>` | 增加額外可寫目錄 |
| `-a, --ask-for-approval <POLICY>` | 控制何時需要人工批准 |
| `--search` | 啟用 live web search，讓模型可直接用 web_search |
| `--no-alt-screen` | 關閉 alternate screen，保留終端捲動歷史 |
| `-h, --help` | 顯示 help |
| `-V, --version` | 顯示版本 |

### `--ask-for-approval` 可用值

| 值 | 行為 |
|----|------|
| `untrusted` | 僅 trusted commands 免批准，其他命令會向使用者請求 |
| `on-failure` | 已標示為 deprecated；先執行，失敗後再升級請求 |
| `on-request` | 由模型自行決定何時請求批准 |
| `never` | 永不詢問；失敗直接回傳給模型 |

---

## 六、互動式模式

### 基本用法

```bash
codex
codex "fix failing tests"
codex -C ./repo
codex --search
codex --model gpt-5.5
codex --profile work
```

### 互動模式的重點

- 預設進入 TUI
- 可在 session 中使用 slash commands
- 可掛接圖片、MCP、plugins、AGENTS.md、config profiles
- 可透過 `resume` / `fork` 延續或分叉上下文

---

## 七、`codex exec`

非互動執行模式，適合 shell script、CI、批次任務。

### 語法

```text
codex exec [OPTIONS] [PROMPT]
codex exec [OPTIONS] <COMMAND> [ARGS]
```

### 特有選項

| 旗標 | 說明 |
|------|------|
| `--skip-git-repo-check` | 允許在非 Git repository 執行 |
| `--ephemeral` | 不把 session 檔案持久化到磁碟 |
| `--ignore-user-config` | 不讀取 `$CODEX_HOME/config.toml` |
| `--ignore-rules` | 不讀取 user / project execpolicy `.rules` |
| `--output-schema <FILE>` | 指定最終輸出的 JSON Schema |
| `--color <always\|never\|auto>` | 控制輸出顏色 |
| `--json` | 以 JSONL 輸出事件 |
| `-o, --output-last-message <FILE>` | 將最後一則 agent 訊息寫入檔案 |

### 範例

```bash
codex exec "summarize the repository"
echo "review this diff" | codex exec -
codex exec --json --output-last-message result.txt "generate release notes"
codex exec --skip-git-repo-check -C /tmp "explain these files"
```

### `codex exec resume`

```text
codex exec resume [SESSION_ID]
```

用途是延續非互動 session。

### `codex exec review`

```text
codex exec review
```

等同在 exec 工作流下做 code review。

---

## 八、`codex review`

非互動 code review 模式。

### 語法

```text
codex review [OPTIONS] [PROMPT]
```

### 主要選項

| 旗標 | 說明 |
|------|------|
| `--uncommitted` | review staged、unstaged、untracked 變更 |
| `--base <BRANCH>` | 與指定 base branch 比較 |
| `--commit <SHA>` | review 某個 commit 引入的變更 |
| `--title <TITLE>` | 額外指定 review summary title |

### 範例

```bash
codex review --uncommitted
codex review --base main
codex review --commit abc1234
codex review "focus on security and backward compatibility"
```

---

## 九、session 管理

### `codex resume`

恢復先前互動式 session。

```text
codex resume [SESSION_ID] [PROMPT]
```

| 旗標 | 說明 |
|------|------|
| `--last` | 直接恢復最近一次 session |
| `--all` | 顯示所有 session，不只目前 cwd |
| `--include-non-interactive` | 連非互動 session 也列入 |

範例：

```bash
codex resume --last
codex resume 123e4567-e89b-12d3-a456-426614174000
```

### `codex fork`

從舊 session 分叉成新 session。

```text
codex fork [SESSION_ID] [PROMPT]
```

| 旗標 | 說明 |
|------|------|
| `--last` | 分叉最近一次 session |
| `--all` | 顯示所有 session |

### `codex archive` / `codex unarchive`

```text
codex archive <SESSION>
codex unarchive <SESSION>
```

用途是封存或還原已儲存 session。

---

## 十、認證相關命令

### `codex login`

```text
codex login
codex login status
```

| 旗標 | 說明 |
|------|------|
| `--with-api-key` | 從 stdin 讀 API key |
| `--with-access-token` | 從 stdin 讀 access token |
| `--device-auth` | 使用 device auth |

### `codex logout`

```text
codex logout
```

移除本機已儲存的認證資訊。

---

## 十一、MCP 管理

### `codex mcp`

```text
codex mcp list
codex mcp get <NAME>
codex mcp add <NAME> --url <URL>
codex mcp add <NAME> -- <COMMAND> [ARGS...]
codex mcp remove <NAME>
codex mcp login <NAME>
codex mcp logout <NAME>
```

### 子命令一覽

| 子命令 | 說明 |
|--------|------|
| `list` | 列出目前設定的 MCP servers |
| `get` | 檢視單一 MCP server 設定 |
| `add` | 新增 streamable HTTP 或 stdio MCP server |
| `remove` | 刪除設定 |
| `login` | 執行 MCP OAuth login |
| `logout` | 清除 MCP 認證 |

### `codex mcp add`

#### HTTP MCP server

```bash
codex mcp add my-server --url https://example.com/mcp
```

#### stdio MCP server

```bash
codex mcp add my-server -- node server.js
```

#### 主要選項

| 旗標 | 說明 |
|------|------|
| `--env KEY=VALUE` | 啟動 stdio server 時注入環境變數 |
| `--url <URL>` | 指定 streamable HTTP server |
| `--bearer-token-env-var <ENV_VAR>` | 從指定環境變數讀 bearer token |
| `--oauth-client-id <CLIENT_ID>` | 指定 OAuth client id |
| `--oauth-resource <RESOURCE>` | 指定 OAuth resource |

### 其他 MCP 子命令重點

| 命令 | 重要選項 |
|------|---------|
| `codex mcp list` | `--json` |
| `codex mcp get <NAME>` | `--json` |
| `codex mcp login <NAME>` | `--scopes a,b,c` |

### `codex mcp-server`

```text
codex mcp-server
```

把 Codex 自己啟動成 MCP server，讓其他 client 以 stdio 接入。

---

## 十二、Plugin 與 marketplace

### `codex plugin`

```text
codex plugin add <PLUGIN[@MARKETPLACE]>
codex plugin list
codex plugin remove <PLUGIN[@MARKETPLACE]>
codex plugin marketplace <COMMAND>
```

### 子命令

| 子命令 | 說明 |
|--------|------|
| `add` | 從已設定 marketplace 安裝 plugin |
| `list` | 列出 marketplace 中可用 plugins |
| `remove` | 移除已安裝 plugin |
| `marketplace` | 管理 marketplace 來源 |

### `plugin add`

```bash
codex plugin add sample@debug
codex plugin add sample --marketplace debug
```

### `plugin remove`

```bash
codex plugin remove sample@debug
```

### `plugin marketplace`

```text
codex plugin marketplace add <SOURCE>
codex plugin marketplace list
codex plugin marketplace upgrade [MARKETPLACE_NAME]
codex plugin marketplace remove <MARKETPLACE_NAME>
```

#### `marketplace add` 支援的來源

- 本機路徑
- `owner/repo[@ref]`
- HTTPS Git URL
- SSH Git URL

#### `marketplace add` 主要選項

| 旗標 | 說明 |
|------|------|
| `--ref <REF>` | 指定 Git ref |
| `--sparse <PATH>` | 稀疏 checkout，可重複 |

---

## 十三、Completion、更新、診斷、功能旗標

### `codex completion`

```text
codex completion [bash|elvish|fish|powershell|zsh]
```

範例：

```bash
codex completion powershell
codex completion zsh
```

### `codex update`

```text
codex update
```

更新到最新版本。

### `codex doctor`

```text
codex doctor
```

#### 常用選項

| 旗標 | 說明 |
|------|------|
| `--json` | 產生機器可讀報告 |
| `--summary` | 只看摘要 |
| `--all` | 展開詳細清單 |
| `--no-color` | 關閉 ANSI 顏色 |
| `--ascii` | 使用 ASCII 標記 |

### `codex features`

```text
codex features list
codex features enable <FEATURE>
codex features disable <FEATURE>
```

用途是檢查 / 切換 feature flags。官方 help 以 `unified_exec` 作為範例 feature key。

### `codex debug`

```text
codex debug models
codex debug app-server
codex debug prompt-input
```

| 子命令 | 說明 |
|--------|------|
| `models` | 輸出原始 model catalog JSON |
| `app-server` | app-server 偵錯工具 |
| `prompt-input` | 將模型可見的 prompt input list 以 JSON 輸出 |

---

## 十四、App / app-server / remote-control / exec-server

這一組偏進階整合與桌面應用。

### `codex app`

```text
codex app [PATH]
```

啟動 Codex Desktop App；若未安裝會改開 installer。

| 旗標 | 說明 |
|------|------|
| `--download-url <URL>` | 覆寫 installer 下載位址 |

### `codex app-server`

```text
codex app-server [COMMAND]
```

子命令：

| 子命令 | 說明 |
|--------|------|
| `daemon` | 管理本機 app-server daemon |
| `proxy` | 將 stdio bytes 代理到 app-server control socket |
| `generate-ts` | 產生 app-server protocol TypeScript bindings |
| `generate-json-schema` | 產生 app-server protocol JSON Schema |

主要選項：

| 旗標 | 說明 |
|------|------|
| `--listen <URL>` | 監聽端點，支援 `stdio://`、`unix://`、`ws://IP:PORT`、`off` |
| `--stdio` | 等同 `--listen stdio://` |
| `--analytics-default-enabled` | 控制 analytics 預設是否啟用 |
| `--ws-auth <MODE>` | 非 loopback listener 的 websocket auth 模式 |
| `--ws-token-file <PATH>` | capability token 檔案 |
| `--ws-token-sha256 <HEX>` | capability token 的 SHA-256 |
| `--ws-shared-secret-file <PATH>` | signed bearer token secret |
| `--ws-issuer <ISSUER>` | JWT issuer |
| `--ws-audience <AUDIENCE>` | JWT audience |
| `--ws-max-clock-skew-seconds <SECONDS>` | JWT 驗證可容忍時差 |

### `codex remote-control`

```text
codex remote-control start
codex remote-control stop
```

用來管理已啟用 remote control 的 app-server daemon。

| 旗標 | 說明 |
|------|------|
| `--json` | 以機器可讀 JSON 輸出 |

### `codex exec-server`

```text
codex exec-server
```

Standalone exec-server，主要選項：

| 旗標 | 說明 |
|------|------|
| `--listen <URL>` | 監聽端點，支援 `ws://IP:PORT`、`stdio`、`stdio://` |
| `--remote <URL>` | 以此 base URL 註冊成 remote environment |
| `--environment-id <ID>` | 綁定既有 environment id |
| `--name <NAME>` | 指定可讀名稱 |
| `--use-agent-identity-auth` | 用 `CODEX_ACCESS_TOKEN` 的 Agent Identity auth |

---

## 十五、Codex Cloud

`codex cloud` 用來瀏覽 cloud task，或把 cloud task 的 diff 套回本機。此功能在本機 help 中標示為 experimental。

### 子命令

| 子命令 | 說明 |
|--------|------|
| `exec` | 不開 TUI，直接提交 cloud task |
| `status` | 查 task 狀態 |
| `list` | 列 task 清單 |
| `apply` | 套用某個 task 的 diff 到本機 |
| `diff` | 顯示某個 task 的 unified diff |

### `cloud exec`

```text
codex cloud exec --env <ENV_ID> [QUERY]
```

| 旗標 | 說明 |
|------|------|
| `--env <ENV_ID>` | 目標環境 id |
| `--attempts <N>` | best-of-N 次數，預設 `1` |
| `--branch <BRANCH>` | 指定 cloud task 要在哪個 Git branch 執行 |

### `cloud list`

```text
codex cloud list
```

| 旗標 | 說明 |
|------|------|
| `--env <ENV_ID>` | 只列某環境的 tasks |
| `--limit <N>` | 回傳數量，1 到 20，預設 `20` |
| `--cursor <CURSOR>` | 分頁 cursor |
| `--json` | JSON 輸出 |

### `cloud status`

```text
codex cloud status <TASK_ID>
```

### `cloud apply`

```text
codex cloud apply <TASK_ID> [--attempt <N>]
```

### `cloud diff`

```text
codex cloud diff <TASK_ID> [--attempt <N>]
```

### `codex apply`

若不是從 `codex cloud apply` 走，也可以直接：

```text
codex apply <TASK_ID>
```

用途是把 agent 產出的最新 diff 以 `git apply` 套回工作樹。

---

## 十六、Sandbox 與 approval 模型

Codex CLI 的安全控制是文件中很重要的一塊。常見控制面有三種：

1. sandbox mode
2. approval policy
3. permission profiles

### Sandbox 模式

| 模式 | 說明 |
|------|------|
| `read-only` | 只能讀，不可寫 |
| `workspace-write` | 可寫工作區；日常開發常用 |
| `danger-full-access` | 近乎完全存取；風險最高 |

### Approval policy

| 模式 | 說明 |
|------|------|
| `untrusted` | 僅 trusted commands 直接執行 |
| `on-request` | 由模型決定何時請求 |
| `never` | 永不詢問，失敗直接回傳 |
| `on-failure` | 舊模式，官方 help 已標註 deprecated |

### 常見組合

| 需求 | 建議 |
|------|------|
| 一般本機開發 | `-s workspace-write -a on-request` |
| 嚴格審查 | `-s read-only -a untrusted` |
| CI 非互動 | `codex exec -a never --json` |
| 外部已 sandbox 的自動化環境 | 視情況使用 `--dangerously-bypass-approvals-and-sandbox` |

### `codex sandbox`

```text
codex sandbox [COMMAND]...
```

用途是直接在 Codex 的 sandbox 內跑命令。

| 旗標 | 說明 |
|------|------|
| `--permissions-profile <NAME>` | 使用命名 permission profile |
| `-p, --profile <CONFIG_PROFILE>` | 疊加 profile |
| `-C, --cd <DIR>` | 指定工作目錄 |
| `--include-managed-config` | 額外納入 managed requirements 解析 |

---

## 十七、設定系統

Codex 的設定核心是 `config.toml`。

### 設定來源

依官方文件，常見設定面包括：

- 使用者層 `config.toml`
- profile 檔案
- 專案內規則與 `AGENTS.md`
- CLI `-c key=value` 動態覆寫
- 環境變數

### CLI 動態覆寫

```bash
codex -c model=\"gpt-5.5\"
codex -c 'sandbox_permissions=[\"disk-full-read-access\"]'
codex -c shell_environment_policy.inherit=all
```

規則：

- 使用 dotted path 覆寫巢狀欄位
- `value` 先嘗試以 TOML 解析
- TOML 解析失敗時，會把原字串當 literal

### Profile

```bash
codex --profile work
codex exec --profile ci
```

`--profile <name>` 會把 `$CODEX_HOME/<name>.config.toml` 疊加在基礎設定之上。

### 建議範例

```toml
model = "gpt-5.5"
sandbox_mode = "workspace-write"
approval_policy = "on-request"

[features]
web_search = true
```

若要使用 `--profile work`，請另外建立：

```text
$CODEX_HOME/work.config.toml
```

例如：

```toml
model = "gpt-5.5"
approval_policy = "on-request"
```

> 實際欄位名稱與可用欄位請以你版本的 `config-reference` 與 `codex --help` 為準；不同版本可能調整。

---

## 十八、常用環境變數

官方 Environment Variables 頁面列出的穩定公開環境變數如下。

| 變數 | 用途 |
|------|------|
| `CODEX_HOME` | Codex 狀態根目錄，包含 config、auth、logs、sessions、skills 等 |
| `CODEX_SQLITE_HOME` | SQLite-backed state 位置 |
| `CODEX_NON_INTERACTIVE` | 安裝 script 的非互動模式 |
| `CODEX_INSTALL_DIR` | CLI 安裝位置 |
| `CODEX_API_KEY` | 僅供 `codex exec` 單次非互動執行使用的 API key |
| `CODEX_ACCESS_TOKEN` | CLI、app-server、trusted automation 使用的 access token |
| `CODEX_CA_CERTIFICATE` | 自訂 PEM CA bundle |
| `SSL_CERT_FILE` | 備援 CA bundle 路徑 |
| `RUST_LOG` | CLI 與 app-server 的 Rust log 過濾與 verbosity |

### 相關說明

- 若用 `--with-api-key` 登入，CLI help 範例仍使用 `OPENAI_API_KEY` 經 stdin pipe 進 `codex login`
- 若用 `--with-access-token` 登入，通常會從 stdin 讀取 `CODEX_ACCESS_TOKEN`
- `CODEX_HOME` 也影響 `config.toml` 與 profile 檔案的查找位置
- `CODEX_API_KEY` 是官方文件列出的固定公開變數，但用途是 `codex exec` 單次執行，不是一般互動登入的主要流程

---

## 十九、Slash Commands

互動式 CLI 支援 slash commands。以下清單以官方 `Slash commands in Codex CLI` 頁面明確列出的 built-ins 為準。

| 指令 | 用途 |
|------|------|
| `/permissions` | 檢視或調整權限相關設定 |
| `/ide` | 帶入 IDE 開啟檔案、選取內容等上下文 |
| `/keymap` | 調整 TUI 鍵盤快捷鍵 |
| `/vim` | 切換 Vim 模式 |
| `/sandbox-add-read-dir` | 新增 sandbox 可讀目錄，Windows only |
| `/agent` | 切換目前 agent thread |
| `/apps` | 瀏覽 apps / connectors，並插入 `$app-slug` |
| `/plugins` | 瀏覽 plugins |
| `/hooks` | 查看與管理 lifecycle hooks |
| `/clear` | 清 terminal 並開始新 chat |
| `/compact` | 壓縮 / 摘要目前對話，釋放 context |
| `/copy` | 複製最新完成輸出 |
| `/diff` | 顯示 Git diff，含未追蹤檔案 |
| `/exit`、`/quit` | 離開 CLI |
| `/experimental` | 切換實驗功能 |
| `/approve` | 允許一次 auto review denial 的重試 |
| `/init` | 產生 `AGENTS.md` scaffold |
| `/logout` | 登出 Codex |
| `/mcp` | 列出目前可用 MCP tools |
| `/mention` | 把檔案或資料夾附加到對話 |
| `/model` | 切換模型與可用的 reasoning effort |
| `/fast` | 切換 Fast service tier |
| `/plan` | 切到 plan mode |
| `/goal` | 設定 / 暫停 / 恢復 / 清除目標 |
| `/personality` | 切換回應風格 |
| `/ps` | 檢視背景 terminals |
| `/stop` | 停止背景 terminals |
| `/fork` | 分叉目前對話 |
| `/side`、`/btw` | 開啟臨時側邊對話 |
| `/raw` | 切換 raw scrollback mode |
| `/resume` | 從 session list 恢復對話 |
| `/new` | 在同一 CLI session 開新對話 |
| `/review` | 對 working tree 執行 review |
| `/status` | 顯示 session 設定、token usage 等 |
| `/debug-config` | 印出 config layer 與 requirements 診斷 |
| `/statusline` | 互動設定狀態列欄位 |
| `/title` | 互動設定 terminal title 欄位 |
| `/theme` | 切換語法高亮主題 |
| `/memories` | 調整 memory 使用與產生策略 |
| `/skills` | 瀏覽並套用 skills |

### Slash commands 的用途分組

| 類型 | 常見指令 |
|------|---------|
| session 管理 | `/new`、`/clear`、`/resume`、`/fork`、`/status` |
| 模型與工具 | `/model`、`/fast`、`/mcp`、`/plugins`、`/apps` |
| 開發輔助 | `/review`、`/diff`、`/mention`、`/plan`、`/goal` |
| 安全控制 | `/permissions`、`/approve`、`/sandbox-add-read-dir` |

> 某些 slash commands 會受平台、feature flags、模型能力或目前模式影響而顯示 / 隱藏；實際可見清單請以你當下互動式 `codex` session 為準。

---

## 二十、典型工作流

### 1. 互動式本機開發

```bash
codex -C . --model gpt-5.5 -s workspace-write -a on-request
```

### 2. 嚴格安全模式

```bash
codex -C . -s read-only -a untrusted
```

### 3. 非互動 JSON 輸出

```bash
codex exec --json --output-last-message out.txt "summarize the failing tests"
```

### 4. 對未提交變更做 review

```bash
codex review --uncommitted
```

### 5. 加入 HTTP MCP server

```bash
codex mcp add docs --url https://example.com/mcp
codex mcp login docs
codex mcp list --json
```

### 6. 安裝 marketplace plugin

```bash
codex plugin marketplace add owner/repo --ref main
codex plugin list
codex plugin add sample --marketplace repo
```

### 7. 續接上一個 session

```bash
codex resume --last
codex fork --last
```

### 8. 使用 Codex Cloud

```bash
codex cloud list
codex cloud exec --env env_123 "fix the flaky test"
codex cloud status task_123
codex cloud diff task_123
codex cloud apply task_123
```

---

## 二十一、常見問題與排錯

### PowerShell 執行政策阻擋 `codex`

現象通常像是 `codex.ps1` 無法執行。可改：

- 直接用 `cmd /c codex ...`
- 調整 PowerShell execution policy
- 重新安裝後確認 PATH 與 wrapper

### `config.toml` 有未知欄位

若開了 `--strict-config`，未知欄位會直接報錯。先：

```bash
codex doctor
codex --help
codex <subcommand> --help
```

再比對你的版本與官方文件是否一致。

### MCP / plugin 不生效

優先檢查：

1. `codex mcp list` / `codex plugin list`
2. 是否完成 `mcp login`
3. marketplace / server 名稱是否正確
4. 目前 profile 與 `-c` 覆寫是否把設定蓋掉
5. 目標功能是否受 feature flag 影響

### 想先看健康檢查

```bash
codex doctor --summary
codex doctor --json
```

---

## 二十二、和 Claude Code CLI 的主要差異

若你是從 `docs/claude-code-cli.md` 對照過來，Codex CLI 目前的差異重點大致是：

- 指令體系不同，沒有 Claude 那套大量內建 workflow 指令
- Codex 更明確圍繞 `config.toml`、profiles、sandbox、approval、MCP、plugin marketplace
- `codex exec`、`codex review`、`codex cloud` 是更核心的非互動工作流
- `app-server`、`remote-control`、`exec-server` 是 Codex 生態系特有整合面

---

## 二十三、建議閱讀順序

如果你是第一次完整使用 Codex CLI，建議依序看：

1. 快速開始
2. 頂層命令總覽
3. 全域旗標
4. `exec` / `review`
5. Sandbox 與 approval 模型
6. MCP / Plugin
7. 設定系統與環境變數

---

## 二十四、最短速查

```bash
codex
codex exec "..."
codex review --uncommitted
codex resume --last
codex fork --last
codex login
codex doctor
codex mcp list
codex plugin list
codex completion powershell
codex -V
```

---

## Codex 非互動模式：`codex exec`

`codex exec`（別名：`codex e`）讓 Codex 在 shell script、CI、排程或 webhook worker 中執行，不開啟互動式 TUI。一次執行會由 Codex 自行完成內部推理、讀檔、工具呼叫與最終回覆；呼叫端只需要接收退出碼與輸出。

它適合「給定工作目錄與任務，讓 agent 自行完成分析或工程工作」；不適合需要硬性限制每個 ticket 的總 token、模型回合或工具呼叫數的服務。後一種情境應使用 Responses API，由應用程式實作固定步數的 workflow。

### 執行模型

```text
Webhook / CI / 排程
  -> 準備工作目錄、輸入檔與權限
  -> codex exec <prompt>
       -> Codex 自行多輪推理與工具操作
       -> stdout: 最終訊息或 JSONL
  -> 呼叫端檢查退出碼、保存結果、更新外部系統
```

`codex exec` 不是常駐 event listener。Jira webhook、重試、併發、timeout、成本預算與回寫 Jira 都應由 n8n、CI、queue worker 或其他外部服務負責。

### 基本語法

```text
codex exec [OPTIONS] "PROMPT"
codex exec resume [SESSION_ID] "PROMPT"
```

最小範例：

```powershell
codex exec "Read this repository and list the three highest-risk areas. Do not modify files."
```

預設情況下，進度輸出寫到 `stderr`，最終 agent 訊息寫到 `stdout`。可直接 pipe 最終結果：

```powershell
codex exec "Summarize the latest test failures." | Set-Content -Encoding utf8 test-summary.md
```

### 工作目錄與 Git 檢查

Codex 預設要求在 Git repository 中執行，以降低自動化誤操作風險。使用 `-C` 指定分析用 worktree：

```powershell
codex exec -C 'D:\workers\CORE-123\repo' `
  "Inspect the source code relevant to reports\coredump-summary.json. Do not modify files."
```

只有在已隔離且確認安全的非 Git 目錄中，才使用 `--skip-git-repo-check`：

```powershell
codex exec --skip-git-repo-check -C 'D:\workers\scratch' `
  "Summarize the files in this directory."
```

### 重要選項

| 選項 | 用途 |
|---|---|
| `-C <DIR>` | 在指定工作目錄執行。 |
| `-m <MODEL>` / `--model <MODEL>` | 單次指定模型。 |
| `--profile <NAME>` | 套用 `config.toml` 的命名設定檔。 |
| `--sandbox read-only` | 僅分析，不允許檔案修改；自動分析的預設選擇。 |
| `--sandbox workspace-write` | 只允許修改 workspace；用於修復或產生檔案。 |
| `--json` | 將 `stdout` 輸出為 JSON Lines，包含 lifecycle、工具與最終訊息事件。 |
| `-o <FILE>` / `--output-last-message <FILE>` | 額外將最終 agent 訊息寫入檔案。 |
| `--output-schema <FILE>` | 要求最終訊息符合指定 JSON Schema。 |
| `--ephemeral` | 不保存本次 session rollout 檔。 |
| `--ignore-user-config` | 不讀取使用者層級 `config.toml`；適合需要可重現 CI 設定時使用。 |
| `--ignore-rules` | 略過 execpolicy rules；除非在受控測試環境，否則不要使用。 |

### Sandbox 與自動化安全

非互動模式預設為 `read-only` sandbox。依最小權限原則選擇權限：

```powershell
# coredump 初步分析：只讀取報告、source worktree 與功能文件
codex exec --sandbox read-only `
  "Analyze reports\CORE-123.json and the matching source code. Do not modify files."

# 僅在隔離的 CI worktree 中，才允許寫入分析檔或修復檔
codex exec --sandbox workspace-write `
  "Create analysis\CORE-123.md from reports\CORE-123.json. Do not modify source files."
```

避免在未隔離的 runner 使用 `danger-full-access`。自動工作需要外網或外部工具時，也應先在 container / VM 與允許清單中限制可用命令與網路範圍。

### API Key 認證

`CODEX_API_KEY` 只支援 `codex exec`，可用於 CI/CD 或其他非互動自動化。應將 secret 注入單次 job / process，不要設定成可被 repository-controlled build script、測試或 dependency hook 讀取的 job-level 環境變數。

```powershell
# 在 CI secret store 或受控 worker 中提供 CODEX_API_KEY 後執行
codex exec --json "Triage the open bug report and return a concise result."
```

若使用保存的 CLI 登入狀態，`codex exec` 會重用它。CI 的一般預設仍是 API key；只有在受信任 runner 且確實需要 ChatGPT / Codex 帳號配額時，才考慮使用帳號 access token。

### JSONL 與結構化輸出

`--json` 讓呼叫端取得 JSONL event stream；可用於記錄執行狀態、工具動作、最終訊息與 usage。若下游要回寫 Jira 或寫 Markdown，應同時使用 JSON Schema 約束最終結果。

`coredump-result.schema.json`：

```json
{
  "type": "object",
  "properties": {
    "triage": { "type": "string" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "evidence": { "type": "array", "items": { "type": "string" } },
    "recommended_next_steps": { "type": "array", "items": { "type": "string" } },
    "needs_human_investigation": { "type": "boolean" }
  },
  "required": ["triage", "confidence", "evidence", "recommended_next_steps", "needs_human_investigation"],
  "additionalProperties": false
}
```

PowerShell 範例：

```powershell
codex exec --json --sandbox read-only `
  --output-schema .\coredump-result.schema.json `
  -o .\result.json `
  "Analyze reports\CORE-123.json. Use only matching-commit source code and docs\features\payment-refund.md. Return preliminary triage, evidence, confidence, next steps, and whether human investigation is needed." `
  2> .\codex-progress.log | Set-Content -Encoding utf8 .\codex-events.jsonl

if ($LASTEXITCODE -ne 0) {
  throw "Codex analysis failed with exit code $LASTEXITCODE"
}
```

注意：`-o` 寫入的是最終 agent 訊息；採用 `--output-schema` 時，將它視為 JSON 輸入並由後續程式套用 Markdown template。不要直接把模型自由文字當成唯一的 Jira 報告格式。

### 透過 stdin 傳遞短暫資料

prompt 是指令，stdin 是額外 context。適合傳送已脫敏、已截斷的 log 或 debugger 摘要：

```powershell
Get-Content -Raw .\reports\stacktrace.txt |
  codex exec --sandbox read-only `
    "Identify the likely crash category, cite the most important frames, and propose the next three debugging steps. Do not claim a root cause without evidence."
```

不要將 raw coredump binary、完整 repository、完整 memory map 或無限制 `gdb` 輸出 pipe 給 Codex。應先用 `gdb` / `lldb` 萃取 signal、build ID、crash thread、top application frames、matching source ranges 與必要 logs。

### 指定模型與 reasoning effort

可在命令列指定模型，或透過 profile 統一管理模型、reasoning effort、sandbox 與 MCP。

```powershell
codex exec -m gpt-5.6-terra --sandbox read-only `
  "Perform preliminary coredump triage only; do not perform broad repository exploration."
```

`reasoning effort` 較高會提升複雜任務品質，但也會增加延遲與 token 使用量。對初步 coredump 分流，先使用低至中等 effort；只有人工確認需要深度追查時，再升級模型或 effort。

### Session continuation

通常每個 webhook / Jira ticket 都應啟動獨立的 `codex exec`，避免不同事故混用 context。只有明確需要延續同一工作時，才使用 `resume`：

```powershell
codex exec "Inspect the failing test and record the evidence."
codex exec resume --last "Based on the evidence, propose the smallest safe fix."
```

`resume` 會延續先前 session，因此不適合作為有嚴格成本、資料隔離或 per-ticket token 預算的預設機制。

### CI / Jira coredump 整合範本

```text
Jira webhook / CI failure
  -> 建立每 ticket 專用且唯讀的 matching-commit worktree
  -> gdb / lldb 產生精簡且脫敏的 coredump-summary.json
  -> 由外部 workflow 限制 timeout、重試、併發與每 ticket 執行次數
  -> codex exec --json --sandbox read-only --output-schema ...
  -> 驗證退出碼與結構化結果
  -> 程式產生 Markdown，回寫 Jira
```

Codex 可以自行讀取 frame 相關 source、功能 Markdown 與必要測試資訊，因此比手動實作 tool-calling loop 快速。但它的內部模型回合、工具呼叫與 token 用量不是 `codex exec` 可硬性限制的參數。若需求是「每張 ticket 最多 N tokens、最多 M 次模型來回」，應改由 n8n / worker 直接呼叫 Responses API，做固定步數的 Context Pack pipeline。

### 常見問題

| 問題 | 處理方式 |
|---|---|
| CLI 要求 Git repository | 優先在 matching-commit worktree 中執行；僅在安全的隔離目錄使用 `--skip-git-repo-check`。 |
| 自動化卡在 approval | 使用最小 sandbox；確認組織政策允許後，才在受控 runner 使用適當 approval policy。 |
| 結果格式不穩定 | 使用 `--output-schema`，再由程式將 JSON 渲染成 Markdown。 |
| 輸出難以被程式消費 | 使用 `--json` 記錄事件，並用 `-o` 保存最終結果。 |
| 成本過高 | 縮小 source / docs context、降低 reasoning effort、避免 `resume`，或改用 Responses API 固定回合數。 |
| 需要完整自動化 | 以 webhook / queue / CI 觸發 `codex exec`；不要把 `codex exec` 當成常駐服務。 |

### 官方文件

- Codex non-interactive mode: https://learn.chatgpt.com/docs/non-interactive-mode
- Codex CLI command reference: https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-exec
- Codex sandboxing: https://learn.chatgpt.com/docs/sandboxing
- Codex authentication for CI/CD: https://learn.chatgpt.com/docs/auth/ci-cd-auth
