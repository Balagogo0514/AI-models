# Claude Code CLI 完整參考

> 資料來源：https://code.claude.com/docs/en/cli-reference 、https://code.claude.com/docs/en/commands 、`claude --help`（v2.1.208 實測驗證）
> 更新日期：2026-07-14

---

## 一、CLI 啟動指令（`claude <subcommand>`）

| 指令 | 說明 | 範例 |
|------|------|------|
| `claude` | 啟動互動 session | `claude` |
| `claude "query"` | 帶初始 prompt 啟動 | `claude "explain this project"` |
| `claude -p "query"` | Print mode（回應後退出）| `claude -p "explain this"` |
| `cat file \| claude -p "query"` | 處理 pipe 輸入 | `cat logs.txt \| claude -p "explain"` |
| `claude -c` | 繼續最近一次對話 | `claude -c` |
| `claude -r "<name>"` | 以 ID 或名稱恢復對話 | `claude -r "auth-refactor"` |
| `claude update` | 更新至最新版 | `claude update` |
| `claude install [version]` | 安裝指定版本（stable/latest） | `claude install stable` |
| `claude auth login` | 登入帳號 | `claude auth login --console` |
| `claude auth logout` | 登出 | `claude auth logout` |
| `claude auth status` | 顯示登入狀態（JSON） | `claude auth status` |
| `claude agents` | 開啟 Agent View 監控背景 session | `claude agents --json` |
| `claude attach <id>` | 附加到背景 session | `claude attach 7c5dcf5d` |
| `claude auto-mode defaults` | 印出 auto mode 分類規則 | `claude auto-mode defaults > rules.json` |
| `claude daemon status` | 顯示背景 supervisor 狀態 | `claude daemon status` |
| `claude daemon stop --any` | 停止 supervisor 與其管理的 session | `claude daemon stop --any` |
| `claude logs <id>` | 印出背景 session 近期輸出 | `claude logs 7c5dcf5d` |
| `claude mcp` | 設定 MCP server | — |
| `claude plugin` | 管理 plugin（別名：`claude plugins`） | `claude plugin install code-review@...` |
| `claude project purge [path]` | 刪除專案所有本地 Claude 狀態 | `claude project purge ~/work/repo --dry-run` |
| `claude remote-control` | 啟動 Remote Control server | `claude remote-control --name "My Project"` |
| `claude respawn <id>` | 重啟背景 session（保留對話） | `claude respawn 7c5dcf5d` |
| `claude rm <id>` | 從列表移除背景 session | `claude rm 7c5dcf5d` |
| `claude setup-token` | 產生長效 OAuth token（給 CI/script 用）| `claude setup-token` |
| `claude stop <id>` | 停止背景 session | `claude stop 7c5dcf5d` |
| `claude ultrareview [target]` | 非互動式執行 ultrareview | `claude ultrareview 1234 --json` |

---

## 二、CLI 旗標（`--flags`）

| 旗標 | 說明 |
|------|------|
| `--add-dir` | 新增額外工作目錄（授予檔案存取）|
| `--agent` | 指定本次 session 使用的 agent |
| `--agents` | 以 JSON 動態定義 subagent |
| `--allow-dangerously-skip-permissions` | 將 bypassPermissions 加入 Shift+Tab 循環 |
| `--allowedTools` | 指定不需確認的工具白名單 |
| `--append-system-prompt` | 附加文字到預設 system prompt 結尾 |
| `--append-system-prompt-file` | 從檔案附加到 system prompt |
| `--bare` | 最小模式：跳過 hooks/skills/plugins/MCP/memory |
| `--betas` | 啟用 beta headers（僅 API key 用戶）|
| `--bg` | 以背景 agent 啟動，立即返回 |
| `--channels` | 指定 MCP channel 監聽通知（Research preview）|
| `--chrome` | 啟用 Chrome 瀏覽器整合 |
| `--continue`, `-c` | 載入最近一次對話 |
| `--dangerously-skip-permissions` | 跳過所有權限提示 |
| `--debug [categories]` | 啟用 debug mode（可過濾類別）|
| `--debug-file <path>` | 將 debug log 寫入指定檔案 |
| `--disable-slash-commands` | 停用所有 skills 與指令 |
| `--disallowedTools` | 工具黑名單（可 deny 特定 pattern）|
| `--effort` | 設定 effort level（low/medium/high/xhigh/max）|
| `--exclude-dynamic-system-prompt-sections` | 把動態 system prompt 段移至 user message（改善 cache 命中）|
| `--exec` | 以 PTY 背景 job 執行 shell 指令 |
| `--fallback-model` | 主要模型不可用時自動 fallback |
| `--fork-session` | Resume 時建立新 session ID |
| `--from-pr` | 恢復與特定 PR 連結的 session |
| `--ide` | 啟動時自動連接 IDE |
| `--init` | 執行 Setup hooks（print mode）|
| `--init-only` | 執行 Setup 與 SessionStart hooks 後退出 |
| `--include-hook-events` | 輸出 hook 生命週期事件（需 stream-json）|
| `--include-partial-messages` | 包含部分串流事件（需 stream-json）|
| `--input-format` | 指定 print mode 輸入格式（text/stream-json）|
| `--json-schema` | 要求 JSON schema 驗證的結構化輸出 |
| `--maintenance` | 執行 maintenance Setup hooks（print mode）|
| `--max-budget-usd` | 設定 API 費用上限（print mode）|
| `--max-turns` | 限制最大回合數（print mode）；未列於 `claude --help` 輸出，但實測 v2.1.208 仍可正常使用 |
| `--mcp-config` | 從 JSON 檔載入 MCP server |
| `--model` | 設定本次 session 使用的模型 |
| `--name`, `-n` | 為 session 命名 |
| `--no-chrome` | 停用 Chrome 整合 |
| `--no-session-persistence` | 不儲存 session 到磁碟（print mode）|
| `--output-format` | 指定輸出格式（text/json/stream-json）|
| `--permission-mode` | 啟動指定權限模式，實測 v2.1.208 可選值：`acceptEdits`（自動允許檔案編輯）、`auto`（auto mode 分類器判斷）、`bypassPermissions`（跳過所有權限提示）、`manual`（逐次詢問，即一般互動預設）、`dontAsk`（僅允許 `permissions.allow` 規則內的呼叫，其餘一律拒絕不詢問）、`plan`（進入 plan mode）|
| `--permission-prompt-tool` | 指定 MCP 工具處理權限提示（非互動模式）|
| `--plugin-dir` | 從目錄或 zip 載入 plugin（僅本次 session）|
| `--plugin-url` | 從 URL 下載 plugin zip（僅本次 session）|
| `--print`, `-p` | Print mode，不進入互動模式 |
| `--prompt-suggestions` | 每次回應後輸出預測的下一步 prompt |
| `--remote` | 在 claude.ai 建立新 web session |
| `--remote-control`, `--rc` | 啟動可從 claude.ai 遠端控制的 session |
| `--replay-user-messages` | 將 stdin 的 user message 回傳 stdout |
| `--resume`, `-r` | 以 ID 或名稱恢復特定 session |
| `--session-id` | 使用指定 UUID 作為 session ID |
| `--setting-sources` | 指定載入哪些設定來源（user/project/local）|
| `--settings` | 載入指定 settings JSON |
| `--strict-mcp-config` | 只使用 `--mcp-config` 指定的 MCP server |
| `--system-prompt` | 完全取代 system prompt |
| `--system-prompt-file` | 從檔案取代 system prompt |
| `--teleport` | 將 web session 拉到本地終端機繼續 |
| `--teammate-mode` | 設定 agent team 顯示模式（auto/in-process/tmux）|
| `--tmux` | 為 worktree 建立 tmux session |
| `--tools` | 限制可用的內建工具 |
| `--verbose` | 詳細輸出每個 turn |
| `--version`, `-v` | 顯示版本號 |
| `--worktree`, `-w` | 在隔離的 git worktree 啟動 |

### System Prompt 旗標說明

| 旗標 | 行為 |
|------|------|
| `--system-prompt` | 完全取代預設 prompt |
| `--system-prompt-file` | 以檔案內容取代 |
| `--append-system-prompt` | 附加文字到預設 prompt 結尾 |
| `--append-system-prompt-file` | 以檔案內容附加到預設 prompt 結尾 |

`--system-prompt` 與 `--system-prompt-file` 互斥，附加旗標可與任一取代旗標組合使用。

---

## 三、Session 內斜線指令（`/commands`）

> **[S]** = Skill（prompt 交給 Claude 執行）
> **[W]** = Workflow（多 subagent 平行背景執行）

| 指令 | 類型 | 說明 |
|------|------|------|
| `/add-dir <path>` | 內建 | 本次 session 新增工作目錄 |
| `/agents` | 內建 | 管理 subagent 設定 |
| `/autofix-pr [prompt]` | 內建 | 啟動 web session 監控 PR，自動推送修復 |
| `/background [prompt]` | 內建 | 將目前 session 轉為背景 agent，釋放終端機（別名：`/bg`）|
| `/batch <instruction>` | **[S]** | 大規模跨 codebase 平行修改，每個獨立單元各開一個 worktree |
| `/branch [name]` | 內建 | 分支目前對話（別名：`/fork`）|
| `/btw <question>` | 內建 | 不加入 context 的旁白提問 |
| `/chrome` | 內建 | 設定 Claude in Chrome |
| `/claude-api [migrate\|managed-agents-onboard]` | **[S]** | 載入 Claude API 參考資料；`migrate` 升級模型版本 |
| `/clear [name]` | 內建 | 清空 context 開始新對話（別名：`/reset`, `/new`）|
| `/code-review [level] [--fix] [--comment] [target]` | **[S]** | 審查 diff；`ultra` 觸發雲端深度審查；`--fix` 自動套用 |
| `/color [color\|default]` | 內建 | 設定 prompt bar 顏色（red/blue/green/yellow/purple/orange/pink/cyan）|
| `/compact [instructions]` | 內建 | 摘要對話以釋放 context window |
| `/config` | 內建 | 開啟設定介面（別名：`/settings`）|
| `/context [all]` | 內建 | 視覺化 context 使用狀況與優化建議 |
| `/copy [N]` | 內建 | 複製最近第 N 條回應到剪貼簿；有 code block 時顯示選擇器 |
| `/cost` | 內建 | `/usage` 的別名 |
| `/debug [description]` | **[S]** | 啟用 debug log 並分析問題 |
| `/deep-research <question>` | **[W]** | 多 agent 平行網路搜尋，產生引用報告 |
| `/desktop` | 內建 | 在 Desktop app 繼續 session（別名：`/app`）|
| `/diff` | 內建 | 互動式 diff 檢視器（左右切換 git diff 與各 turn 的改動）|
| `/doctor` | 內建 | 診斷 Claude Code 安裝與設定；按 `f` 自動修復 |
| `/effort [level\|auto]` | 內建 | 設定模型 effort level（low/medium/high/xhigh/max/ultracode）|
| `/exit` | 內建 | 退出 CLI（別名：`/quit`）；背景 session 中只是 detach |
| `/export [filename]` | 內建 | 匯出對話為純文字 |
| `/fast [on\|off]` | 內建 | 切換 fast mode |
| `/feedback [report]` | 內建 | 回報 bug（別名：`/bug`, `/share`）|
| `/fewer-permission-prompts` | **[S]** | 掃描 transcript 自動建立工具白名單減少權限提示 |
| `/focus` | 內建 | 切換 focus view（只顯示最後 prompt + 一行 tool 摘要 + 最終回應）|
| `/goal [condition\|clear]` | 內建 | 設定自動完成條件，Claude 持續跨 turn 執行到達成 |
| `/heapdump` | 內建 | 寫入 heap snapshot 用於診斷記憶體問題 |
| `/help` | 內建 | 顯示說明與指令清單 |
| `/hooks` | 內建 | 檢視 hook 設定 |
| `/ide` | 內建 | 管理 IDE 整合狀態 |
| `/init` | 內建 | 初始化專案 CLAUDE.md |
| `/insights` | 內建 | 分析 Claude Code session 使用模式與摩擦點報告 |
| `/install-github-app` | 內建 | 設定 Claude GitHub Actions app |
| `/install-slack-app` | 內建 | 安裝 Claude Slack app |
| `/keybindings` | 內建 | 開啟或建立快捷鍵設定檔 |
| `/login` | 內建 | 登入帳號 |
| `/logout` | 內建 | 登出帳號 |
| `/loop [interval] [prompt]` | **[S]** | 以固定間隔重複執行 prompt（別名：`/proactive`）|
| `/mcp` | 內建 | 管理 MCP server 連線與 OAuth |
| `/memory` | 內建 | 編輯 CLAUDE.md 記憶檔案、管理 auto-memory |
| `/mobile` | 內建 | 顯示手機 app QR Code（別名：`/ios`, `/android`）|
| `/model [model]` | 內建 | 切換 AI 模型並儲存為新 session 預設 |
| `/passes` | 內建 | 分享免費週給朋友（限符合資格帳號）|
| `/permissions` | 內建 | 管理工具權限規則（別名：`/allowed-tools`）|
| `/plan [description]` | 內建 | 進入 plan mode |
| `/plugin` | 內建 | 管理 plugin |
| `/powerup` | 內建 | 互動式功能教學（附動畫展示）|
| `/privacy-settings` | 內建 | 管理隱私設定（Pro/Max 限定）|
| `/radio` | 內建 | 開啟 Claude FM lo-fi 廣播 |
| `/recap` | 內建 | 產生本次 session 單行摘要 |
| `/release-notes` | 內建 | 互動式瀏覽各版本 changelog |
| `/reload-plugins` | 內建 | 重新載入所有 plugin（不需重啟）|
| `/reload-skills` | 內建 | 重新掃描 skill 目錄（不需重啟，v2.1.152+）|
| `/remote-control` | 內建 | 讓此 session 可從 claude.ai 遠端控制（別名：`/rc`）|
| `/remote-env` | 內建 | 設定 web session 預設遠端環境 |
| `/rename [name]` | 內建 | 為目前 session 命名並顯示在 prompt bar |
| `/resume [session]` | 內建 | 以 ID 或名稱恢復對話（別名：`/continue`）|
| `/review [PR]` | 內建 | 在本地 session 審查 PR |
| `/rewind` | 內建 | 回滾對話與程式碼到先前 checkpoint（別名：`/checkpoint`, `/undo`）|
| `/run` | **[S]** | 啟動並驅動 app，驗證改動在 runtime 生效（v2.1.145+）|
| `/run-skill-generator` | **[S]** | 教 `/run` 與 `/verify` 如何啟動你的 app（v2.1.145+）|
| `/sandbox` | 內建 | 切換 sandbox mode（限支援平台）|
| `/schedule [description]` | 內建 | 建立/管理定期執行的 routine（別名：`/routines`）|
| `/scroll-speed` | 內建 | 調整滾輪速度（fullscreen mode 限定）|
| `/security-review` | 內建 | 對目前 branch 的改動做安全漏洞分析 |
| `/setup-bedrock` | 內建 | 設定 Amazon Bedrock（需 `CLAUDE_CODE_USE_BEDROCK=1`）|
| `/setup-vertex` | 內建 | 設定 Google Vertex AI（需 `CLAUDE_CODE_USE_VERTEX=1`）|
| `/simplify [target]` | **[S]** | 找 cleanup 機會並自動套用，不找 correctness bug（v2.1.154+）|
| `/skills` | 內建 | 列出所有可用 skill；按 `t` 依 token 排序 |
| `/stats` | 內建 | `/usage` 別名（開啟 Stats tab）|
| `/status` | 內建 | 顯示版本、模型、帳號、連線狀態（回應中也可開啟）|
| `/statusline` | 內建 | 設定 Claude Code 狀態列 |
| `/stickers` | 內建 | 訂購 Claude Code 貼紙 |
| `/stop` | 內建 | 停止背景 session（附加中才可用）|
| `/tasks` | 內建 | 列出並管理背景 task（別名：`/bashes`）|
| `/team-onboarding` | 內建 | 從 session 歷史產生團隊上手指南 |
| `/teleport` | 內建 | 將 web session 拉入本地終端機（別名：`/tp`）|
| `/terminal-setup` | 內建 | 設定終端機快捷鍵（VS Code/Cursor/Zed 等需要時才顯示）|
| `/theme` | 內建 | 切換色彩主題（含自訂/色盲友好/ANSI 主題）|
| `/tui [default\|fullscreen]` | 內建 | 設定 terminal UI 渲染器並重啟（保留對話）|
| `/ultraplan <prompt>` | 內建 | 在 ultraplan session 草擬計畫，可在瀏覽器審查後遠端執行 |
| `/ultrareview [PR]` | 內建 | 雲端多 agent 深度審查（建議改用 `/code-review ultra`）|
| `/upgrade` | 內建 | 開啟升級方案頁面 |
| `/usage` | 內建 | 顯示費用、用量、活動統計（別名：`/cost`, `/stats`）|
| `/usage-credits` | 內建 | 設定使用額度（前身：`/extra-usage`）|
| `/verify` | **[S]** | 啟動 app 觀察行為，確認改動真正生效（v2.1.145+）|
| `/voice [hold\|tap\|off]` | 內建 | 切換語音聽寫（需 claude.ai 帳號）|
| `/web-setup` | 內建 | 連接 GitHub 帳號到 Claude Code on the web |
| `/workflows` | 內建 | 開啟 workflow 進度檢視器（可暫停/恢復/儲存）|

---

## 四、特殊格式

| 格式 | 說明 |
|------|------|
| `! <command>` | 在目前 session 執行 shell 指令並將輸出帶入對話（互動模式輸入框使用）|
| `/mcp__<server>__<prompt>` | MCP server 動態暴露的 prompt 指令 |

---

## 五、典型工作流程中的指令使用時機

| 時機 | 建議指令 |
|------|---------|
| 第一次進入 repo | `/init` → `/memory` → `/mcp` → `/agents` → `/permissions` |
| 執行任務途中 | `/plan`（大改動前）、`/model`、`/effort`、`/context`、`/compact`、`/btw` |
| 平行工作 | `/agents`、`/tasks`、`/background`、`/batch` |
| 提交前 | `/diff`、`/code-review`、`/review`、`/security-review` |
| 切換任務 | `/clear`、`/resume`、`/branch` |
| 出問題時 | `/rewind`、`/doctor`、`/debug`、`/feedback` |

---

## 六、`/goal` 詳細用法

> 需要 Claude Code v2.1.139+

設定一個**完成條件**，Claude 在每個 turn 結束後由獨立的小模型（Haiku）評估條件是否達成。未達成自動開始下一個 turn，達成後自動停止並清除 goal。

### 基本語法

```text
/goal <條件描述>    # 設定 goal（立即開始執行）
/goal               # 查看目前狀態（turn 數、token、評估原因）
/goal clear         # 提前終止（別名：stop / off / reset / none / cancel）
```

### 使用範例

```text
/goal all tests in test/auth pass and the lint step is clean
```

```text
/goal migrate all API call sites to v2 and npm run build exits 0
```

```bash
# 非互動模式（跑到條件達成才退出）
claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
```

### 寫出有效條件的三個要素

| 要素 | 說明 | 範例 |
|------|------|------|
| **單一可量測終態** | 測試結果、build exit code、檔案數量 | `npm test exits 0` |
| **明確的驗證方式** | Claude 要執行什麼來證明 | `run git status and show clean` |
| **不可破壞的約束** | 過程中不能改變的東西 | `no other test file is modified` |

加入迴圈上限避免無止盡執行：

```text
/goal all linting errors fixed, or stop after 20 turns
```

### `/goal` vs 其他持續執行方式

| 方式 | 下一 turn 觸發時機 | 停止條件 |
|------|------|------|
| `/goal` | 前一 turn 結束後 | 小模型確認條件達成 |
| `/loop` | 固定時間間隔 | 手動停止或 Claude 判斷完成 |
| Stop hook | 前一 turn 結束後 | 自訂 script 或 prompt 判斷 |

> 搭配 `--permission-mode auto` 效果最佳：auto mode 省去 tool 確認提示，`/goal` 省去 turn 確認提示，兩者合用可完全無人看管執行。

### 注意事項

- 評估器**不執行指令也不讀取檔案**，只根據對話 transcript 內容判斷，條件必須是 Claude 輸出能展示的結果
- 每個 session 只能有一個 goal；新設定的會覆蓋舊的
- `--resume` 恢復 session 時，未完成的 goal 會自動還原（但 turn 計數與 token 基準重置）
- 需要已接受 trust dialog 的工作區（底層是 Stop hook，`disableAllHooks` 或 `allowManagedHooksOnly` 時無法使用）

---

## 七、`/loop` 詳細用法

> 需要 Claude Code v2.1.72+

在 session 保持開啟的期間，以固定間隔或自動節奏重複執行一個 prompt。適合用來輪詢部署狀態、監看 PR、追蹤長時間 build，或設定提醒。

### 三種呼叫模式

| 你提供的內容 | 範例 | 行為 |
|------|------|------|
| 間隔 + prompt | `/loop 5m check the deploy` | prompt 以**固定間隔**執行 |
| 只有 prompt | `/loop check the deploy` | prompt 以 **Claude 自動選擇的間隔**執行 |
| 只有間隔，或什麼都不給 | `/loop` 或 `/loop 15m` | 執行**內建 maintenance prompt**（或 `loop.md`）|

### 固定間隔模式

```text
/loop 5m check if the deployment finished and tell me what happened
/loop 2h run the integration test suite and summarize results
```

間隔可放在前面（`30m check...`）或後面（`check... every 2 hours`）。支援單位：`s`（秒）、`m`（分）、`h`（時）、`d`（天）。秒會進位到分鐘（cron 精度限制）；不整除的間隔（如 `7m`、`90m`）會自動捨入並告知實際值。

### 自動節奏模式（省略間隔）

Claude 根據每次觀察到的狀況動態決定下次等待多久（1 分鐘到 1 小時之間）：

```text
/loop check whether CI passed and address any review comments
```

- Build 進行中或 PR 有活動 → 短間隔
- 一切安靜 → 長間隔
- 每次結束都會印出選擇的延遲時間與原因
- Claude 可能直接使用 Monitor 工具串流輸出，比輪詢更省 token

> Bedrock / Vertex AI / Foundry 環境：省略間隔時改用固定 10 分鐘間隔。

### 內建 maintenance prompt（`/loop` 不帶任何引數）

```text
/loop        # 自動節奏執行 maintenance
/loop 15m    # 固定 15 分鐘執行 maintenance
```

每次迭代依序執行：
1. 繼續對話中未完成的工作
2. 照料目前 branch 的 PR（review 留言、CI 失敗、merge conflict）
3. 沒有待辦事項時做 cleanup（找 bug、簡化程式碼）

不會主動發起新工作；push 或刪除等不可逆操作只有在 transcript 已授權時才執行。

### 自訂預設 prompt（`loop.md`）

建立 `loop.md` 可取代內建 maintenance prompt，格式為純 Markdown，直接寫成你想執行的指令：

| 路徑 | 範圍 |
|------|------|
| `.claude/loop.md` | 專案層級（優先）|
| `~/.claude/loop.md` | 使用者層級（全域 fallback）|

```markdown
# .claude/loop.md 範例
Check the `release/next` PR. If CI is red, pull the failing job log,
diagnose, and push a minimal fix. If new review comments have arrived,
address each one and resolve the thread. If everything is green and
quiet, say so in one line.
```

- 執行中修改 `loop.md` 會在下次迭代生效
- 命令列有提供 prompt 時忽略 `loop.md`
- 超過 25,000 bytes 的內容會被截斷

### 也可以重複執行其他指令

```text
/loop 20m /review-pr 1234
```

### 設定一次性提醒（不用 `/loop`）

```text
remind me at 3pm to push the release branch
in 45 minutes, check whether the integration tests passed
```

Claude 會自動建立單次觸發的 cron task，執行後自動刪除。

### 管理排程任務

```text
what scheduled tasks do I have?   # 列出所有任務
cancel the deploy check job        # 取消指定任務
```

底層工具：

| 工具 | 用途 |
|------|------|
| `CronCreate` | 建立新任務（cron 表達式 + prompt + 是否重複）|
| `CronList` | 列出所有任務（含 ID、排程、prompt）|
| `CronDelete` | 以 ID 取消任務 |

每個 session 最多可建立 50 個排程任務。

### 停止 loop

- 按 `Esc`：停止正在等待下次觸發的 `/loop`
- 自動節奏模式：Claude 判斷工作完成時可自行終止
- 固定間隔模式：持續到手動停止或 7 天後自動過期

### Cron 表達式參考

格式：`分 時 日 月 週`

| 範例 | 意義 |
|------|------|
| `*/5 * * * *` | 每 5 分鐘 |
| `0 * * * *` | 每小時整點 |
| `7 * * * *` | 每小時第 7 分鐘 |
| `0 9 * * *` | 每天早上 9 點（本地時間）|
| `0 9 * * 1-5` | 週一到週五早上 9 點 |
| `30 14 15 3 *` | 3 月 15 日下午 2:30 |

### 注意事項

- 任務只有在 Claude Code 執行且閒置時才會觸發；關閉終端機即停止
- 錯過的觸發不會補跑，只在 Claude 閒置後補觸發一次
- 開新對話會清除所有任務；`--resume` / `--continue` 恢復未過期的任務
- 重複任務在建立後 **7 天自動過期**（觸發最後一次後刪除）
- 設定 `CLAUDE_CODE_DISABLE_CRON=1` 可完全停用排程功能
- 需要跨 session 持久的排程請改用 `/schedule`（Routines）或 Desktop scheduled tasks

---

## 八、`/batch` 詳細用法

> `/batch` 是一個 **Bundled Skill**（prompt 交給 Claude 執行），需要 git repository。

### 核心概念

將一個大型改動自動拆分成 **5 到 30 個獨立工作單元**，每個單元在隔離的 git worktree 中由一個獨立的背景 subagent 執行，最終各自開 PR。適合大規模、機械性、可平行化的 codebase 改動。

### 基本語法

```text
/batch <改動指令>
```

### 使用範例

```text
/batch migrate src/ from Solid to React
/batch rename all snake_case function names to camelCase in lib/
/batch add JSDoc comments to every exported function in src/api/
/batch update all fetch() calls to use the new apiClient wrapper
```

### 執行流程（Step-by-step）

1. **研究 codebase**：Claude 先掃描整個 repo，理解改動的範圍
2. **拆解工作**：分解成 5–30 個獨立單元，並呈現計畫等待確認
3. **確認後執行**：你同意後，每個單元各自：
   - 在隔離的 git worktree（`.claude/worktrees/<name>/`）中執行
   - 由一個獨立的背景 subagent 實作
   - 跑測試確認無誤
   - 開一個 PR

### 與其他平行方式的比較

| 方式 | 協調者 | 工作者溝通 | 檔案隔離 | 適用情境 |
|------|------|------|------|------|
| `/batch` | Claude（預設 skill）| 不互相溝通，各自獨立 | 每個 subagent 各一個 worktree | 大規模機械式 codebase 改動 |
| Subagents | Claude（session 內）| 回報給主 session | 可選擇性隔離 | 側邊任務、搜尋、分析 |
| Agent teams | Claude（lead 指派）| 共用 task list + 互傳訊息 | 不隔離（需手動分工）| 複雜協作任務 |
| Agent view | 你（手動派發）| 只向你回報 | 自動各一個 worktree | 多個獨立任務同時進行 |

### Worktree 隔離機制

每個 subagent 在 `.claude/worktrees/<name>/` 下取得獨立的工作目錄與 branch，互不干擾：

- 分支來源：預設從 `origin/HEAD`（遠端預設 branch）
- 若要從當前本地 HEAD 分支，設定 `worktree.baseRef: "head"`（settings.json）
- `.env` 等 gitignore 的本地設定檔需透過 `.worktreeinclude` 自動複製進 worktree

```text
# .worktreeinclude（放在 repo 根目錄）
.env
.env.local
config/secrets.json
```

### 監控執行進度

```text
/tasks        # 列出所有背景任務
/workflows    # 查看 workflow 執行進度
claude agents # 開啟 Agent View 監控所有 session
```

### 完成後清理 worktree

| 狀況 | 行為 |
|------|------|
| 無未提交變更、無新 commit | 自動刪除 worktree 與 branch |
| 有變更或新 commit | Claude 詢問是否保留 |
| 非互動模式（`-p`）| 不自動清理，需手動 `git worktree remove` |

### 注意事項

- 需要 git repository（無 git 則無法使用）
- 每個 subagent 各自開一個 PR，最終需要你自行 review 與合併
- token 用量會乘上 subagent 數量，大型任務請注意費用（`/usage` 查看）
- 適合**機械性、可明確拆解**的改動；需要跨模組協調的複雜重構建議改用 Agent teams
- 建議先在小範圍測試指令效果，確認拆解方式符合預期再跑整個 codebase

---

## 九、`/deep-research` 詳細用法

> `/deep-research` 是一個 **Bundled Workflow**（多 subagent 平行背景執行），需要 Claude Code v2.1.154+，付費方案限定。

### 核心概念

**Dynamic Workflow** 是一段 Claude 撰寫的 JavaScript 腳本，由 runtime 在背景執行，協調大量 subagent 平行工作。`/deep-research` 是內建的 workflow，專為跨多來源的深度研究設計：平行搜尋 → 抓取來源 → 交叉驗證 → 產出引用報告。

Session 保持完全響應，工作全部在背景進行。

### 基本語法

```text
/deep-research <研究問題>
```

### 使用範例

```text
/deep-research What changed in the Node.js permission model between v20 and v22?
/deep-research Compare the trade-offs of CRDT vs OT for collaborative text editing
/deep-research What are the performance implications of React Server Components in Next.js 14?
```

### 執行流程（Step-by-step）

1. **輸入問題**：執行 `/deep-research <問題>`
2. **確認允許**：Claude Code 詢問是否允許執行 workflow（依權限模式有所不同）
3. **背景執行**：多個 subagent 平行展開搜尋，各自從不同角度調查
4. **交叉驗證**：獨立 agent 對各來源的聲明進行投票，過濾掉無法通過交叉驗證的資訊
5. **產出報告**：結果回到 session，報告含有引用來源，未通過驗證的聲明已過濾

### 監控執行進度

```text
/workflows    # 開啟 workflow 進度檢視器
```

進度檢視器鍵盤操作：

| 按鍵 | 功能 |
|------|------|
| `↑` / `↓` | 選擇 phase 或 agent |
| `Enter` / `→` | 深入查看 phase 或 agent 的 prompt、工具呼叫、結果 |
| `Esc` | 返回上一層 |
| `j` / `k` | 在 agent 詳細內容中捲動 |
| `p` | 暫停 / 恢復執行 |
| `x` | 停止選取的 agent，或停止整個 workflow |
| `r` | 重啟選取的 agent |
| `s` | 儲存此次 workflow 腳本為可重用指令 |

### 觸發 Workflow 的其他方式

除了 `/deep-research` 外，任何 prompt 都可觸發 workflow：

```text
# 在 prompt 中加入 "workflow" 關鍵字
Run a workflow to audit every API endpoint under src/routes/ for missing auth checks
```

或切換到 ultracode effort：

```text
/effort ultracode    # 之後每個重要任務都自動使用 workflow 編排
/effort high         # 回到一般模式
```

### 確認提示行為（依權限模式）

| 權限模式 | 提示行為 |
|------|------|
| Default / accept edits | 每次都詢問（選過「不再詢問」除外）|
| Auto mode | 僅第一次詢問；之後自動開始 |
| Bypass permissions / `-p` / Agent SDK | 不詢問，直接執行 |

確認畫面選項：
- **Yes, run it**：立即執行
- **Yes, and don't ask again**：執行並記住（此 workflow × 此專案）
- **View raw script**：先看腳本再決定（`Ctrl+G` 在編輯器開啟）
- **No**：取消

### 儲存為可重用指令

執行完後按 `s` 可儲存此次 workflow 腳本：

| 儲存位置 | 範圍 |
|------|------|
| `.claude/workflows/` | 專案層級（隨 repo 共享）|
| `~/.claude/workflows/` | 使用者層級（所有專案可用）|

儲存後可用 `/<name>` 直接呼叫，支援傳入引數：

```text
/triage-issues on issues 1024, 1025, and 1030
```

### Workflow vs 其他方式比較

| 面向 | Subagents | Skills | Agent teams | Workflows |
|------|------|------|------|------|
| 誰決定下一步 | Claude（逐 turn）| Claude（照 prompt）| Lead agent | 腳本 |
| 中間結果放在 | context window | context window | 共享 task list | 腳本變數 |
| 可重複執行 | Worker 定義 | 指令 | Team 定義 | 編排腳本本身 |
| 規模 | 少數任務 | 同 subagents | 少數長跑 peer | 數十到數百個 agent |
| 中斷後恢復 | 重啟 turn | 重啟 turn | Teammate 繼續跑 | 同 session 內可恢復 |

### 限制與注意事項

- 需要 **WebSearch 工具**可用（`/deep-research` 依賴網路搜尋）
- 需要 **v2.1.154+** 與**付費方案**（Pro、Max、Team、Enterprise）
- 執行中**不接受使用者輸入**，需要分階段確認時請拆成多個 workflow
- 最多同時 **16 個並行 agent**（依機器 CPU 核心數調整）
- 每次執行最多 **1,000 個 agent**（防止無限迴圈）
- token 用量顯著高於一般對話，大型任務建議先跑小範圍測試
- 退出 Claude Code 後重開，workflow 會**重新開始**（不支援跨 session 恢復）
- 設定 `CLAUDE_CODE_DISABLE_WORKFLOWS=1` 或 `/config` 可停用此功能

---

## 十、Worktree 使用方法

> Git worktree 讓每個 Claude Code session 在獨立的工作目錄與 branch 中運作，平行 session 的檔案修改互不干擾。需要 git repository。

### 核心概念

一個 git worktree 是共用同一份 repo 歷史與 remote 的獨立工作目錄，有自己的檔案狀態與 branch。用來讓不同 Claude session 同時修改不同功能，而不會互相衝突。

### 啟動 worktree session

```bash
# 建立名為 feature-auth 的 worktree，分支到 .claude/worktrees/feature-auth/
claude --worktree feature-auth
claude -w feature-auth          # 簡寫

# 省略名稱，自動產生（如 bright-running-fox）
claude --worktree

# 同時開第二個隔離 session
claude --worktree bugfix-123
```

worktree 預設建立在 `.claude/worktrees/<name>/`，branch 名稱為 `worktree-<name>`。

> 建議將 `.claude/worktrees/` 加入 `.gitignore`，避免出現在主 checkout 的未追蹤檔案清單。

### 選擇 branch 基準點

| 設定 | 行為 |
|------|------|
| 預設（`fresh`）| 從 `origin/HEAD`（遠端預設 branch）開分支，取得乾淨的起點 |
| `head` | 從本地當前 `HEAD` 開分支，帶入未推送的 commit |

```json
// settings.json
{
  "worktree": {
    "baseRef": "head"
  }
}
```

從特定 PR 建立 worktree：

```bash
claude --worktree "#1234"
claude --worktree "https://github.com/org/repo/pull/1234"
```

### 複製本地設定檔進 worktree

Worktree 是乾淨的 checkout，`.env` 等 gitignore 的檔案不會自動存在。用 `.worktreeinclude` 指定要複製的檔案：

```text
# .worktreeinclude（放在 repo 根目錄，語法同 .gitignore）
.env
.env.local
config/secrets.json
```

只有「符合 pattern 且已被 gitignore」的檔案才會被複製，已追蹤的檔案不會重複。

### Subagent 使用 worktree 隔離

要讓 `/batch` 或其他 subagent 各自在獨立 worktree 執行：

```text
# 在 prompt 中要求
work in a worktree for your agents
```

或在自訂 subagent 的 frontmatter 中設定：

```yaml
---
isolation: worktree
---
```

完成後無變更的 worktree 會自動刪除。

### 離開 worktree 時的清理行為

| 狀況 | 行為 |
|------|------|
| 無未提交變更、無新 commit | 自動刪除 worktree 與 branch |
| 有變更或新 commit | 詢問是否保留（保留 → 目錄與 branch 留存；移除 → 刪除所有未提交內容）|
| `--worktree` 搭配 `-p`（非互動）| 不自動清理，需手動執行 `git worktree remove` |

Subagent 建立的 worktree 超過 `cleanupPeriodDays` 設定天數後，若無未提交變更或未推送 commit，會自動清除。

### 手動管理 worktree

```bash
# 在新 branch 上建立 worktree
git worktree add ../project-feature-a -b feature-a

# 從現有 branch 建立 worktree
git worktree add ../project-bugfix bugfix-123

# 在該 worktree 啟動 Claude
cd ../project-feature-a && claude

# 列出所有 worktree
git worktree list

# 完成後移除
git worktree remove ../project-feature-a
```

### 與其他平行方式的關係

| 方式 | 檔案隔離 | 工作協調 |
|------|------|------|
| `--worktree` | 每個 session 各一個 worktree | 你自己手動管理 |
| `/batch` | 每個 subagent 各一個 worktree | Claude 自動拆解並協調 |
| Agent view | 每個派發的 session 各一個 worktree | 你監控，Claude 執行 |
| Subagents | 可選擇性隔離（`isolation: worktree`）| Claude 在 session 內協調 |
| Agent teams | 不隔離（需手動分工避免衝突）| Lead agent 協調 |

### 注意事項

- 第一次在某目錄使用 `--worktree` 前，需先執行 `claude` 接受 trust dialog
- 每個新 worktree 需要自行安裝依賴（`npm install`、虛擬環境等）
- 非 git 版本控制（SVN、Perforce 等）可透過 `WorktreeCreate` / `WorktreeRemove` hooks 自訂建立與清理邏輯

---

## 十一、`/schedule` 詳細用法

> `/schedule` 建立的 Routine 跑在 **Anthropic 雲端基礎設施**，與 `/loop`（本地 session 內）完全不同。需要 claude.ai 訂閱帳號（Pro、Max、Team、Enterprise），需要 Claude Code v2.1.81+。

### 核心概念

**Routine** = 一份儲存在雲端的 Claude Code 設定（prompt + repo + connectors），可掛載多種觸發器自動執行。電腦關機時仍持續運作。

每次觸發會在雲端建立一個新 session，Claude 自動執行 prompt、操作 repo、呼叫 connector，完成後你可以在 web 上查看結果、審查變更、開 PR。

### CLI 基本語法

```text
/schedule <描述>                    # 對話式建立排程 routine
/schedule daily PR review at 9am   # 每日定期
/schedule in 2 weeks remove the feature flag   # 單次未來執行
/schedule list                      # 列出所有 routine
/schedule update                    # 修改現有 routine
/schedule run                       # 立即觸發執行一次
```

> `/schedule` 在 CLI 只能建立**排程觸發**（schedule）；API 觸發與 GitHub 事件觸發需到 Web UI 設定。

### 三種觸發器類型

#### 1. Schedule（定期排程）

```text
/schedule daily PR review at 9am
/schedule every weeknight, triage new issues and assign owners
/schedule tomorrow at 9am, summarize yesterday's merged PRs   # 單次
```

- 預設頻率：hourly、daily、weekdays、weekly
- 自訂 cron（如每兩小時）：先用 `/schedule` 建立，再用 `/schedule update` 設定 cron 表達式
- **最小間隔 1 小時**
- 時間以你的本地時區輸入，自動轉換
- 觸發時間可能延遲幾分鐘（固定 offset，每個 routine 一致）

**單次執行（one-off）**：設定後自動停用，Web UI 標示為 **Ran**；不佔每日 routine 執行配額

#### 2. API 觸發

在 Web UI 建立後取得專屬 HTTP endpoint，POST 即可觸發：

```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/<routine-id>/fire \
  -H "Authorization: Bearer <token>" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sentry alert SEN-4521 fired in prod. Stack trace attached."}'
```

回傳：
```json
{
  "type": "routine_fire",
  "claude_code_session_id": "session_01HJKLMNOPQRSTUVWXYZ",
  "claude_code_session_url": "https://claude.ai/code/session_01HJKLMNOPQRSTUVWXYZ"
}
```

- `text` 欄位為本次執行的額外 context（如 alert body），非必填
- 每個 routine 有獨立 token，只能觸發該 routine
- Token 只顯示一次，請妥善保存；可隨時 Regenerate 或 Revoke

#### 3. GitHub 事件觸發（僅 Web UI）

支援事件：

| 事件 | 觸發時機 |
|------|------|
| Pull request | PR 開啟、關閉、指派、加標籤、同步等 |
| Release | Release 建立、發佈、編輯、刪除 |

PR 過濾條件（全部條件需同時符合）：

| 過濾欄位 | 說明 |
|------|------|
| Author | PR 作者 GitHub username |
| Title | PR 標題 |
| Body | PR 描述內容 |
| Base branch | 目標 branch |
| Head branch | 來源 branch |
| Labels | 標籤 |
| Is draft | 是否為草稿 |
| Is merged | 是否已合併 |

> 每個符合的事件各自啟動獨立 session，不共用。

### 使用情境範例

| 情境 | 觸發器 | 說明 |
|------|------|------|
| Backlog 維護 | Schedule（每個工作日夜間）| 讀取新 issue、加標籤、指派負責人、推播 Slack 摘要 |
| 告警分類 | API | 監控工具觸發，拉 stack trace、比對近期 commit、開草稿 PR |
| 自動 code review | GitHub（PR opened）| 跑自訂 review checklist、留 inline comment |
| 部署驗證 | API（CD pipeline 呼叫）| 跑 smoke test、掃 error log、推播 go/no-go |
| 文件同步 | Schedule（每週）| 掃描合併 PR、找出過時文件、開 PR 更新 |
| SDK 跨語言同步 | GitHub（PR merged）| 自動把變更移植到另一語言的 SDK |

### Routine 設定項目

| 設定 | 說明 |
|------|------|
| **Prompt** | 每次執行的指令（需自包含、明確說明成功條件）|
| **Repositories** | Claude 要操作的 GitHub repo（每次執行都重新 clone）|
| **Environment** | 雲端執行環境（網路存取、環境變數、setup script）|
| **Connectors** | MCP connector（Slack、Linear 等）；預設全部包含，建議移除不需要的 |
| **Branch 權限** | 預設只能推 `claude/` 前綴的 branch；開啟「Allow unrestricted branch pushes」可解鎖 |

### 雲端環境網路存取

| 等級 | 說明 |
|------|------|
| **Trusted**（預設）| 允許 npm/PyPI 等 package registry、常見 cloud API、container registry；封鎖其他 |
| **Custom** | Trusted 清單 + 自訂允許 domain |
| **Full** | 完全不限制 |

### `/schedule` vs `/loop` vs Desktop scheduled tasks

| 面向 | `/schedule`（Routines）| `/loop` | Desktop scheduled tasks |
|------|------|------|------|
| 跑在哪裡 | Anthropic 雲端 | 你的本地機器 | 你的本地機器 |
| 電腦關機能跑 | 可以 | 不行 | 不行 |
| 需要開啟 session | 不需要 | 需要 | 不需要 |
| 最小間隔 | 1 小時 | 1 分鐘 | 1 分鐘 |
| 存取本地檔案 | 不行（fresh clone）| 可以 | 可以 |
| MCP servers | Connector 設定 | 繼承 session | 設定檔 |
| 觸發方式 | 定期 / API / GitHub 事件 | 定期 | 定期 |

### 注意事項

- Routine 屬於你的個人帳號，不與隊友共享；所有操作（commit、PR、Slack 訊息）以你的身份執行
- 每個帳號有**每日執行次數上限**；超過可開啟 usage credits 繼續跑
- 單次執行（one-off）不計入每日配額
- `/schedule` 在以下情況不顯示：使用 Console API key / Bedrock / Vertex / Foundry 登入；設定了 `DISABLE_TELEMETRY` / `DO_NOT_TRACK` 等環境變數；在 Claude Code on the web session 內
- Team/Enterprise 管理員可在 admin settings 停用全組織的 Routine 功能
- 管理介面：[claude.ai/code/routines](https://claude.ai/code/routines)

---

## 十二、`/ultrareview`（`/code-review ultra`）詳細用法

> 需要 Claude Code v2.1.86+，claude.ai 帳號登入（不支援 API key 單獨使用、Bedrock、Vertex AI、Foundry、Zero Data Retention 組織）。

### 核心概念

在 **Claude Code on the web 雲端沙箱**中啟動一批 reviewer agent，平行深度審查你的 branch 或 PR。每個回報的 bug 都經過獨立驗證，只回報真實存在的問題。

> `/ultrareview` 是舊名，現在建議用 `/code-review ultra`，兩者功能相同。

### 基本語法

```text
/code-review ultra           # 審查目前 branch vs 預設 branch（含未提交變更）
/code-review ultra 1234      # 審查 GitHub PR #1234
/ultrareview                 # 同上（alias）
/ultrareview 1234
```

### 非互動模式（CI / Script）

```bash
claude ultrareview                  # 審查目前 branch
claude ultrareview 1234             # 審查 PR #1234
claude ultrareview origin/main      # 審查 vs 指定 base branch
claude ultrareview 1234 --json      # 輸出原始 bugs.json
claude ultrareview --timeout 60     # 設定逾時（分鐘，預設 30）
```

Exit code：`0` = 成功（有無 findings 都算）；`1` = 啟動失敗 / 遠端錯誤 / 逾時；`130` = Ctrl-C 中斷（遠端仍繼續跑）

### 執行流程

1. 執行 `/code-review ultra`
2. 確認對話框顯示：審查範圍（檔案數 / 行數）、剩餘免費次數、預估費用
3. 確認後於背景執行，session 保持可用
4. 約 5–10 分鐘後，findings 以通知方式出現在 session 中
5. 每個 finding 含檔案位置與問題說明，可直接請 Claude 修復

用 `/tasks` 查看執行進度或停止審查（停止後歸檔，部分結果不返回）。

### 兩種審查目標模式

| 模式 | 語法 | 行為 |
|------|------|------|
| Branch 模式 | `/code-review ultra` | 打包本地 repo 狀態上傳（含未提交變更）|
| PR 模式 | `/code-review ultra 1234` | 遠端沙箱直接 clone PR（不依賴本地狀態）|

> repo 太大無法打包時，Claude Code 會提示改用 PR 模式：先推 branch 開 draft PR，再用 PR 號碼執行。

### 費用

| 方案 | 免費次數 | 用完後 |
|------|------|------|
| Pro | 3 次（一次性，不重置）| 以 usage credits 計費，約 $5–$20 / 次 |
| Max | 3 次（一次性，不重置）| 以 usage credits 計費，約 $5–$20 / 次 |
| Team / Enterprise | 無 | 以 usage credits 計費，約 $5–$20 / 次 |

- 費用依變更大小而異；提前停止的審查仍消耗一次免費次數（付費審查只計實際跑完的部分）
- 付費審查需先開啟 usage credits（`/usage-credits` 查看或設定）

### `/review` vs `/code-review ultra` 比較

| 面向 | `/review` | `/code-review ultra` |
|------|------|------|
| 執行位置 | 本地 session | 雲端沙箱 |
| 深度 | 單次審查 | 多 agent 平行 + 獨立驗證 |
| 時間 | 數秒到幾分鐘 | 約 5–10 分鐘 |
| 費用 | 計入一般用量 | 免費 3 次，之後 $5–$20 / 次 |
| 適合時機 | 開發途中快速回饋 | 合併前對重大變更的深度把關 |

### 注意事項

- 需以 claude.ai 帳號登入；若只有 API key 請先執行 `/login`
- 不支援：Bedrock、Vertex AI、Foundry、Zero Data Retention 組織
- 只有你主動呼叫指令時才會執行，Claude 不會自動觸發
- 在 CI 使用 `claude ultrareview` 時，呼叫本身即視為同意計費確認
- 進度與 session URL 輸出到 stderr，findings 輸出到 stdout（方便 script 解析）

---

## 十三、`/ultraplan` 詳細用法

> 需要 Claude Code v2.1.91+，claude.ai 帳號 + GitHub repository。不支援 Bedrock、Vertex AI、Foundry。

### 核心概念

將規劃任務從本地 CLI 交給雲端的 **Claude Code on the web** session（以 plan mode 執行）。Claude 在雲端草擬計畫，你的終端機保持可用；計畫完成後在瀏覽器中逐段評論、要求修改，最後選擇在雲端或本地執行。

### 三種啟動方式

```text
# 1. 指令方式
/ultraplan migrate the auth service from sessions to JWTs

# 2. 關鍵字方式（在一般 prompt 中包含 "ultraplan"）
ultraplan a refactor of the payment module to support multi-currency

# 3. 從本地計畫送出（Claude 完成本地 plan 後，選擇 "No, refine with Ultraplan on Claude Code on the web"）
```

指令與關鍵字方式會先顯示確認對話框；從本地計畫送出則直接啟動（已視為確認）。

### 執行流程（Step-by-step）

1. **啟動**：Claude Code 將任務送至雲端，CLI prompt 顯示狀態指示器
2. **雲端草擬**：遠端 session 研究 codebase、以 plan mode 起草計畫
3. **通知就緒**：狀態變為 `◆ ultraplan ready`，開啟瀏覽器連結審查
4. **瀏覽器審查**：逐段留言、要求修改、反覆迭代
5. **選擇執行位置**：批准後選擇在雲端或本地實作

### CLI 狀態指示器

| 狀態 | 意義 |
|------|------|
| `◇ ultraplan` | Claude 正在研究 codebase 並草擬計畫 |
| `◇ ultraplan needs your input` | Claude 有待確認的問題，開啟 session 連結回答 |
| `◆ ultraplan ready` | 計畫就緒，可在瀏覽器審查 |

用 `/tasks` 選取 ultraplan 項目可查看 session 連結、agent 活動，並執行「Stop ultraplan」（停止後歸檔，不儲存任何內容到終端機）。

### 瀏覽器審查功能

| 功能 | 說明 |
|------|------|
| Inline comments | 反白任意段落留言，Claude 針對留言修改計畫 |
| Emoji reactions | 對段落按 emoji 表示認可或顧慮（不需寫留言）|
| Outline sidebar | 快速跳至計畫各章節 |

可無限次迭代修改，直到計畫符合預期再選擇執行。

### 選擇執行位置

#### 在雲端執行

選「**Approve Claude's plan and start coding**」→ Claude 在同一個雲端 session 實作計畫 → 完成後在 Web UI 審查 diff 並開 PR。

#### 送回本地終端機執行

選「**Approve plan and teleport back to terminal**」→ 雲端 session 歸檔 → 本地終端機出現計畫確認對話框：

| 選項 | 行為 |
|------|------|
| **Implement here** | 將計畫注入目前對話並繼續執行 |
| **Start new session** | 清空目前對話，以計畫為 context 重新開始（會印出 `claude --resume` 指令供日後返回原對話）|
| **Cancel** | 將計畫儲存為檔案（不執行），Claude 印出檔案路徑 |

### `/ultraplan` vs `/plan` vs `/ultrareview` 對照

| 面向 | `/plan` | `/ultraplan` | `/ultrareview` |
|------|------|------|------|
| 目的 | 本地計畫模式 | 雲端草擬計畫 + 瀏覽器審查 | 雲端深度 code review |
| 執行位置 | 本地 session | 雲端 | 雲端 |
| 互動介面 | 終端機 | 瀏覽器（逐段留言）| 終端機通知 |
| 適合時機 | 快速規劃小任務 | 複雜任務需要細部討論計畫 | 合併前驗證 bug |

### 注意事項

- 需要 GitHub repository（雲端 session 需要 clone repo）
- 啟動時若已連接 Remote Control，會自動中斷（兩者共用 claude.ai/code 介面，只能擇一）
- 若尚無雲端環境，ultraplan 首次啟動時會自動建立
- 不支援：Bedrock、Vertex AI、Foundry
- 本地終端機必須保持輪詢（開啟狀態），「送回本地」選項才會出現

---

## 十四、Multi-agent 使用方法

Claude Code 提供四種平行工作方式，分別解決不同問題。

### 方式一：Subagents（session 內委派）

在主對話中，Claude 自動或手動委派側邊任務給獨立 subagent，避免搜尋結果、log 等雜訊污染主 context window。

#### 內建 subagent

| Agent | 模型 | 工具 | 用途 |
|-------|------|------|------|
| Explore | Haiku | 唯讀 | 快速搜尋、分析 codebase |
| Plan | 繼承主對話 | 唯讀 | plan mode 時收集 context |
| general-purpose | 繼承主對話 | 全部 | 複雜多步驟任務 |
| statusline-setup | Sonnet | — | 執行 `/statusline` 時自動啟用 |
| claude-code-guide | Haiku | — | 回答 Claude Code 功能問題時啟用 |

#### 自訂 subagent（建立 Markdown 檔案）

```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Reviews code for security vulnerabilities. Use proactively after any auth, input handling, or crypto changes.
model: sonnet
tools: Read, Glob, Grep
---

You are a security-focused code reviewer. Check for OWASP Top 10 vulnerabilities,
injection risks, improper auth, and data exposure. Report findings with severity level.
```

#### 透過 `--agents` 旗標臨時定義（不儲存）

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on quality and security.",
    "tools": ["Read", "Grep", "Glob"],
    "model": "sonnet"
  }
}'
```

#### Subagent 儲存位置與優先順序

| 位置 | 範圍 | 優先 |
|------|------|------|
| Managed settings | 組織全體 | 最高（1）|
| `--agents` CLI flag | 本次 session | 2 |
| `.claude/agents/` | 當前專案 | 3 |
| `~/.claude/agents/` | 所有專案 | 4 |
| Plugin `agents/` | Plugin 範圍 | 最低（5）|

同名 subagent 以優先順序高者為準。專案層級的 subagent 建議 commit 進 repo，讓團隊共用。

#### Subagent Frontmatter 可用欄位

```yaml
---
name: my-agent           # 唯一識別名稱（必填）
description: ...         # Claude 判斷何時委派的依據（越具體越好）
model: sonnet            # 指定模型（haiku 省錢，opus 強力）
tools: Read, Grep, Glob  # 允許的工具（留空 = 繼承全部）
disallowedTools: Bash    # 明確禁止的工具
permissionMode: plan     # 權限模式（default/plan/acceptEdits/auto）
isolation: worktree      # 在獨立 worktree 執行（避免衝突）
maxTurns: 10             # 最大回合數
background: true         # 背景執行
color: blue              # UI 顯示顏色
memory: user             # 持久記憶（user / project / none）
---
```

#### 在 session 內明確指定 subagent

```text
Use the security-reviewer agent to check the auth changes
@security-reviewer review the latest diff
```

#### Fork 當前對話給 subagent（繼承完整 context）

```text
/branch redis-alternative
Fork this conversation and try the alternative approach with Redis instead
```

#### 管理 subagent

```text
/agents     # 開啟 subagent 管理介面（Running tab + Library tab）
```

Library tab 可建立、編輯、刪除 subagent，Running tab 可查看執行中的 subagent。

---

### 方式二：Agent View（背景 session 管理台）

`claude agents` 開啟統一管理畫面，同時派發多個獨立 session 在背景執行，電腦不需一直看著終端機。

```bash
claude agents                    # 開啟 Agent View
claude agents --cwd ~/my-app     # 只顯示該目錄的 session
claude agents --json             # JSON 輸出（供 script 使用）
```

#### 派發任務

在 Agent View 底部輸入框輸入（每次 `Enter` 建立新的獨立 session）：

```text
fix the flaky auth test in test/auth.spec.ts
review PR #1234 and leave inline comments
investigate why build times doubled this week
```

指定 subagent 執行：

```text
security-reviewer check the payment module
@security-reviewer audit the API routes
```

#### Session 狀態圖示

| 狀態 | 圖示 | 意義 |
|------|------|------|
| Working | 動畫 `✽` | 正在執行工具或生成回應 |
| Needs input | 黃色 | 等待你回應問題或授權 |
| Idle | 暗色 | 等待下一個指令 |
| Completed | 綠色 `✻` | 成功完成 |
| Failed | 紅色 | 錯誤結束 |
| Stopped | 灰色 | 被手動停止 |
| `/loop` 睡眠中 | `✢` | 顯示執行次數與下次觸發倒數 |

圓點 `∙` 表示 process 已退出但仍可 attach（Claude 會從上次中斷處恢復）。

#### Agent View 鍵盤操作

| 快捷鍵 | 功能 |
|--------|------|
| `↑` / `↓` | 移動選取 row |
| `Space` | 開啟 peek 面板（查看最新輸出或問題）|
| `Enter` / `→` | Attach 進入完整 session |
| `Shift+Enter` | 派發並立即 attach |
| `←`（空 prompt）| Detach 返回 Agent View |
| `Ctrl+T` | 釘選 session（保持 process 存活）|
| `Ctrl+R` | 重新命名 |
| `Ctrl+X` | 停止；再按一次（2 秒內）刪除 |
| `Ctrl+S` | 切換依狀態 / 目錄分組 |
| `Shift+↑` / `Shift+↓` | 調整 row 排序 |
| `Ctrl+G` | 在 `$EDITOR` 開啟派發輸入框 |
| `?` | 顯示所有快捷鍵 |
| `Esc` | 關閉 peek / 清空輸入 / 離開 |

#### Peek 面板操作

選取 row 按 `Space` 開啟：

- 查看最新輸出、待決問題、已開 PR
- 直接輸入回覆並按 `Enter` 送出（不需 attach）
- 多選題按數字鍵選擇；按 `Tab` 填入建議回覆
- 輸入前加 `!` 可送出 Bash 指令

#### PR 狀態顏色

| 顏色 | 意義 |
|------|------|
| 黃色 | 等待 CI / review，或 CI 失敗 |
| 綠色 | CI 通過且無 review 阻擋 |
| 紫色 | 已合併 |
| 灰色 | Draft 或已關閉 |

#### 篩選 session

在輸入框輸入篩選條件（不會派發任務）：

| 篩選 | 效果 |
|------|------|
| `a:<name>` | 顯示使用指定 agent 的 session |
| `s:<state>` | 依狀態篩選（如 `s:working`、`s:blocked`）|
| `#<number>` | 顯示與指定 PR 關聯的 session |

#### 將現有 session 送入背景

```text
/background    # session 內執行，轉為背景 agent（別名：/bg）
```

或在任意 session 按 `←`（空 prompt）→ 自動背景化並開啟 Agent View。

#### 從 shell 管理背景 session

```bash
claude attach 7c5dcf5d      # 附加到指定 session
claude stop 7c5dcf5d        # 停止 session
claude rm 7c5dcf5d          # 從列表移除（transcript 保留）
claude logs 7c5dcf5d        # 查看近期輸出
claude respawn 7c5dcf5d     # 重啟（保留對話）
claude respawn --all        # 重啟所有執行中 session（如升級後重載）
```

---

### 方式三：`/batch`（大規模平行改動）

拆分成 5–30 個 subagent，每個在獨立 worktree 執行，各自開 PR。適合機械性大規模改動。詳見「八、`/batch` 詳細用法」。

```text
/batch migrate all fetch() calls to the new apiClient wrapper
/batch add unit tests to every exported function in src/utils/
```

---

### 方式四：Dynamic Workflow（腳本化大規模編排）

Claude 撰寫 JavaScript 腳本協調數十到數百個 subagent，中間結果存在腳本變數而非 context window，支援暫停後繼續。詳見「九、`/deep-research` 詳細用法」。

```text
/deep-research <研究問題>
Run a workflow to audit every API endpoint for missing auth checks
/effort ultracode    # 開啟後每個重要任務都自動使用 workflow
```

---

### 四種方式完整比較

| 面向 | Subagents | Agent View | `/batch` | Workflow |
|------|------|------|------|------|
| 協調者 | Claude（session 內）| 你（手動派發）| Claude（skill）| 腳本（runtime）|
| 同一 session | 是 | 否（各自獨立）| 否 | 否（背景）|
| 工作者溝通 | 回報主 session | 只向你回報 | 不互通，各自獨立 | 不互通 |
| 檔案隔離 | 可選（`isolation: worktree`）| 自動各一個 worktree | 自動各一個 worktree | 無 |
| 結果回到哪裡 | 主 context window | 你查看 / PR | 各自開 PR | 腳本變數 → 最終報告 |
| 規模 | 少數委派任務 | 數個獨立任務 | 5–30 個單元 | 數十到 1000 個 agent |
| 中斷後恢復 | 重啟 turn | 繼續跑（supervisor）| — | 同 session 內可恢復 |
| 適合情境 | 側邊任務、保留 context | 多任務並行監控 | 大規模機械式改動 | 大規模研究 / 稽核 |

---

### 選擇方式的決策流程

```
任務是否可以平行、獨立執行？

│
├─ 否（需要在主對話協調）
│   └─ → Subagents（Claude 自動委派）
│
└─ 是
    ├─ 機械性 codebase 改動（5–30 個單元）
    │   └─ → /batch
    │
    ├─ 多個獨立任務，需要手動監控與介入
    │   └─ → Agent View（claude agents）
    │
    └─ 大規模研究 / 稽核 / 需要可重複腳本
        └─ → Workflow（/deep-research、workflow 關鍵字）

檔案衝突風險？
├─ 有 → 加 isolation: worktree 或改用 /batch（自動隔離）
└─ 無 → 直接用 subagents
```

---

## 十五、`/code-review` 詳細用法

Claude Code 提供三層程式碼審查，適用不同情境：

| 指令 | 執行位置 | 深度 | 費用 | 適合時機 |
|------|------|------|------|------|
| `/code-review` | 本地 session | 單次，可調 effort | 計入一般用量 | 開發途中快速審查 |
| `/code-review ultra` | 雲端沙箱 | 多 agent + 獨立驗證 | 免費 3 次，之後 $5–$20 | 合併前深度把關 |
| Code Review（GitHub App）| Anthropic 雲端 | 多 agent fleet | $15–$25 / 次 | PR 自動化審查（Team/Enterprise）|

---

### A. `/code-review`（本地審查，Skill）

#### 基本語法

```text
/code-review                          # 審查目前 diff，使用 session 當前 effort
/code-review low                      # 低 effort：少量高信心 findings
/code-review medium
/code-review high                     # 高 effort：更廣覆蓋，可能含不確定 findings
/code-review max
/code-review ultra                    # 觸發雲端深度審查（見第十二章）
/code-review --fix                    # 審查後自動套用 findings 到工作目錄
/code-review --comment                # 將 findings 以 inline comment 發佈到 GitHub PR
/code-review --fix --comment          # 同時套用並發 PR comment
/code-review high --fix <path>        # 審查指定路徑
/code-review ultra --fix              # 雲端深度審查後套用 findings
```

#### Effort 等級說明

| Effort | Findings 特性 |
|--------|------|
| `low` / `medium` | 較少、信心高的 findings |
| `high` → `max` | 較廣覆蓋，可能包含不確定的 findings |
| 未指定 | 使用目前 session 的 effort 設定 |

#### 審查目標

```text
/code-review high src/auth/          # 審查指定目錄
/code-review max --comment 1234      # 審查 PR #1234 並發 inline comment
```

#### `/simplify`（v2.1.154+ 獨立的 cleanup 審查）

```text
/simplify                # 只找 cleanup 機會（reuse、簡化、效率）並自動套用，不找 correctness bug
/simplify src/utils/     # 指定路徑
```

> v2.1.154 前 `/simplify` 等同 `/code-review --fix`；之後兩者分離，各有專責。

---

### B. Code Review GitHub App（Team/Enterprise 自動化 PR 審查）

> 需要 Team 或 Enterprise 方案，不支援 Zero Data Retention 組織。

#### 設定流程

1. 前往 [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code)
2. 安裝 Claude GitHub App（需要 Contents / Issues / Pull requests 讀寫權限）
3. 選擇要啟用的 repo
4. 為每個 repo 設定觸發模式

#### 三種觸發模式

| 模式 | 行為 | 成本 |
|------|------|------|
| Once after PR creation | PR 開啟或標記 ready for review 時執行一次 | 最低 |
| After every push | 每次 push 都執行，可自動 resolve 已修復的 thread | 最高 |
| Manual | 只有評論 `@claude review` 才執行 | 按需計費 |

#### 手動觸發指令（在 PR 留言）

| 指令 | 效果 |
|------|------|
| `@claude review` | 立即執行審查，並訂閱後續 push 觸發 |
| `@claude review once` | 只執行一次，不訂閱後續 push |

條件：必須是 PR 頂層留言（非 inline comment），留言者需有 owner/member/collaborator 權限，PR 須為開啟狀態。草稿 PR 僅手動觸發有效。

#### Findings 嚴重程度

| 標記 | 嚴重度 | 意義 |
|------|------|------|
| 🔴 | Important | 應在合併前修復的 bug |
| 🟡 | Nit | 小問題，不阻擋合併 |
| 🟣 | Pre-existing | 存在於 codebase 但非此 PR 引入 |

每個 finding 含可展開的 extended reasoning，說明 Claude 為何標記此問題及驗證方式。

#### 查看結果的三個位置

1. **Inline comments**：直接標在 PR diff 行上
2. **Check run Details**：`Claude Code Review` check → `Details` 連結，含所有 findings 的嚴重度表格
3. **Files changed annotations**：在 Files changed tab 的 diff 行上以 annotation 呈現

#### 用 CLI 解析 check run 結果

```bash
gh api repos/OWNER/REPO/check-runs/CHECK_RUN_ID \
  --jq '.output.text | split("bughunter-severity: ")[1] | split(" -->")[0] | fromjson'
# 回傳如：{"normal": 2, "nit": 1, "pre_existing": 0}
# normal = Important findings 數量
```

#### 自訂審查行為

**`CLAUDE.md`**：通用專案指引，新引入的違規標記為 Nit。

**`REVIEW.md`**（repo 根目錄）：注入所有 review agent 的最高優先指令，可調整：

```markdown
# REVIEW.md 範例

## What Important means here
Reserve Important for findings that break behavior, leak data, or block rollback.
Style and naming suggestions are Nit at most.

## Cap the nits
Report at most five Nits per review. Say "plus N similar items" for the rest.

## Do not report
- Anything CI already enforces: lint, formatting, type errors
- Generated files under `src/gen/` and any `*.lock` file

## Always check
- New API routes have an integration test
- Log lines don't include email addresses or user IDs
```

可調整項目：嚴重度定義、Nit 數量上限、略過路徑/分類、repo 專屬規則、驗證門檻、重複審查收斂策略、摘要格式。

#### 費用

- 平均 $15–$25 / 次，依 PR 大小與 codebase 複雜度浮動
- 透過 usage credits 計費，不計入方案包含用量
- 可在 [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage) 設定每月上限
- 查看用量：[claude.ai/analytics/code-review](https://claude.ai/analytics/code-review)

#### 常見問題

| 問題 | 解法 |
|------|------|
| 審查失敗或逾時 | 在 PR 留言 `@claude review once` 重跑 |
| 達到每月上限 | PR 會有提示留言；管理員到 admin settings 提高上限 |
| 有 findings 但看不到 inline comment | 查看 Check run Details 或 Files changed annotations |
| GitHub Checks tab 的 Re-run 無效 | 改用 `@claude review once` 或推新 commit |

---

## 十六、Permission Modes（權限模式）

### 六種模式總覽

| 模式 | 不需確認就能執行 | 適合情境 |
|------|------|------|
| `default`（CLI 旗標值為 `manual`）| 唯讀操作 | 入門、敏感工作 |
| `acceptEdits` | 讀取、檔案編輯、常見 fs 指令 | 迭代開發，事後審查 diff |
| `plan` | 唯讀操作（不執行任何寫入）| 探索 codebase、規劃大改動 |
| `auto` | 幾乎全部（有背景安全分類器）| 長時間任務、減少中斷 |
| `dontAsk` | 只有預先批准的工具 | 鎖定的 CI / script |
| `bypassPermissions` | 全部（無任何檢查）| 隔離容器 / VM 環境 |

除 `bypassPermissions` 外，所有模式都保護特定路徑（`.git`、`.claude` 設定等）不被自動修改。

### 切換方式

**互動模式 — `Shift+Tab` 循環：**

```
default → acceptEdits → plan → (bypassPermissions) → (auto)
```

- `auto` 需帳號符合資格才出現；首次循環到時會詢問是否啟用
- `bypassPermissions` 需啟動時帶旗標才出現
- `dontAsk` 不在循環中，只能用旗標設定

**啟動時指定：**

```bash
claude --permission-mode manual          # 即本節所稱的 default，逐次詢問
claude --permission-mode acceptEdits
claude --permission-mode plan
claude --permission-mode auto
claude --permission-mode bypassPermissions
claude --dangerously-skip-permissions    # bypassPermissions 的別名
```

**設為預設（settings.json）：**

```json
{
  "permissions": {
    "defaultMode": "acceptEdits"
  }
}
```

> `defaultMode: "auto"` 只能放在 `~/.claude/settings.json`；專案層級的 settings 會被忽略（防止 repo 自我授予 auto mode）。

### 各模式詳細說明

#### `acceptEdits`

```bash
claude --permission-mode acceptEdits
```

自動批准：讀取、檔案編輯、常見 Bash fs 指令（`mkdir`、`touch`、`rm`、`rmdir`、`mv`、`cp`、`sed`）。其他 Bash 指令仍需確認。適合想事後用 `git diff` 審查，而非逐步確認的工作流程。

#### `plan`

```bash
claude --permission-mode plan
# 或在 prompt 前綴：
/plan fix the auth bug
```

Claude 只讀取、研究、撰寫計畫，不進行任何編輯。計畫完成後可選擇批准並切換到其他模式執行。按 `Shift+Tab` 可在不批准計畫的情況下離開 plan mode。

計畫批准後的選項：
- 批准並以 auto mode 執行
- 批准並以 acceptEdits 執行
- 批准並逐步手動確認每個編輯
- 繼續修改計畫
- 送至 `/ultraplan` 在瀏覽器深度審查

#### `auto`

```bash
claude --permission-mode auto
```

有背景安全分類器監控每個動作，無需人工確認。**預設封鎖**的操作：

| 類別 | 封鎖的動作 |
|------|------|
| 危險執行 | `curl \| bash` 等下載執行 |
| 資料外洩 | 將敏感資料送往外部 endpoint |
| 生產環境 | deploy、migration |
| 雲端破壞 | 大規模刪除、IAM 變更 |
| Git 危險操作 | force push、直接推送 main |

**預設允許**：本地工作目錄操作、安裝 lock file 宣告的依賴、唯讀 HTTP 請求、推送自己建立的 branch。

若分類器連續封鎖 3 次或累計 20 次，auto mode 暫停並恢復手動確認。用 `/permissions` 的 Recently denied tab 查看並手動批准。

**Auto mode 需求**：
- Claude Code v2.1.83+
- 支援的模型：Opus 4.6+、Sonnet 4.6（Anthropic API）；Opus 4.7+（Bedrock/Vertex/Foundry）
- Team/Enterprise：管理員需在 admin settings 啟用

#### `dontAsk`

```bash
claude --permission-mode dontAsk
```

所有未在 `permissions.allow` 規則中的工具呼叫一律拒絕（不詢問）。完全非互動，適合 CI pipeline 中預定義允許工具集的場景。

#### `bypassPermissions`

```bash
claude --permission-mode bypassPermissions
# 或
claude --dangerously-skip-permissions
```

**所有安全檢查停用**，工具呼叫立即執行。唯一例外：`rm -rf /` 和 `rm -rf ~` 仍會提示。

限制：
- 不能在已啟動的 session 中切換進入，需重啟帶旗標
- Linux/macOS 下以 root 或 sudo 執行時拒絕啟動
- 管理員可在 managed settings 設定 `permissions.disableBypassPermissionsMode: "disable"` 全面封鎖

**只在隔離的容器 / VM 環境使用。**

##### 兩個 `dangerously-skip-permissions` 旗標的差異

| 旗標 | 行為 | 效果 |
|------|------|------|
| `--dangerously-skip-permissions` | 啟動時**立即**以 `bypassPermissions` 模式執行 | 等同 `--permission-mode bypassPermissions`，一啟動就跳過所有權限檢查 |
| `--allow-dangerously-skip-permissions` | 只是**把 `bypassPermissions` 加入 `Shift+Tab` 循環選項**，本身不會立即啟用 | 啟動時仍在 `default`（`manual`）模式，需自己在互動畫面按 `Shift+Tab` 切過去才會真的跳過檢查 |

也就是說，前者是「一開始就全開」，後者只是「允許你之後手動切過去」——`--allow-dangerously-skip-permissions` 本身**不會**讓 Claude 一啟動就跳過權限提示。

### 受保護路徑（所有模式除 bypassPermissions 外）

寫入以下路徑一律不自動批准：

- `.git`、`.config/git`
- `.vscode`、`.idea`、`.husky`、`.cargo`、`.devcontainer`、`.yarn`、`.mvn`
- `.claude`（除 `.claude/commands`、`.claude/agents`、`.claude/skills`、`.claude/worktrees`）
- `.gitconfig`、`.gitmodules`
- Shell 設定檔（`.bashrc`、`.zshrc`、`.profile` 等）
- 套件管理設定（`.npmrc`、`.yarnrc`、`bunfig.toml` 等）

---

## 十七、Hooks（鉤子）

Hooks 讓你在 Claude Code 生命週期的特定時間點自動執行 shell 指令、HTTP 請求、MCP 工具或 LLM prompt。用於自動化、驗證、控制 Claude 的行為。

### Hook 觸發時機

| Event | 觸發時機 | 可阻擋？ |
|-------|------|------|
| `SessionStart` | Session 開始或恢復 | 否 |
| `UserPromptSubmit` | 使用者送出 prompt | 是 |
| `PreToolUse` | 工具執行**前** | 是 |
| `PostToolUse` | 工具執行**成功後** | 否 |
| `PostToolUseFailure` | 工具執行**失敗後** | 否 |
| `PermissionRequest` | Claude 請求工具權限時 | 是（可自動批准/拒絕）|
| `Stop` | Claude 完成回應時 | 是（可繼續下一 turn）|
| `StopFailure` | Claude 回應以錯誤結束 | 否 |
| `Notification` | Claude Code 發送通知 | 否（唯讀）|
| `SessionEnd` | Session 結束 | 否 |

### 設定結構

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/hook.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

三層結構：**Hook event** → **Matcher group**（決定何時觸發）→ **Hook handler**（執行什麼）

### Hook 類型

| 類型 | 說明 |
|------|------|
| `command` | 執行 shell 指令，透過 stdin 收到 JSON 輸入 |
| `http` | POST JSON 到指定 URL |
| `mcp_tool` | 呼叫 MCP server 上的工具 |
| `prompt` | 送 prompt 給 Claude 做 yes/no 評估 |
| `agent` | 派生一個 subagent 進行驗證 |

### Matcher 語法

| Pattern | 效果 |
|---------|------|
| `"*"` 或省略 | 比對全部 |
| `"Bash"` | 精確比對工具名稱 |
| `"Bash\|Edit\|Write"` | 比對任一（OR）|
| `"^Notebook"` | JavaScript regex |
| `"mcp__memory__.*"` | 比對 memory server 所有工具 |
| `"mcp__.*__write.*"` | 比對任何 server 的 write 類工具 |

### Exit code 與輸出

| Exit code | 意義 |
|-----------|------|
| `0` | 成功，解析 stdout 的 JSON 輸出 |
| `2` | 阻擋錯誤，stderr 作為錯誤訊息顯示 |
| 其他 | 非阻擋錯誤，繼續執行 |

Hook 可回傳 JSON 控制行為：

```json
{
  "decision": "block",
  "reason": "說明原因",
  "additionalContext": "給 Claude 的補充 context",
  "systemMessage": "顯示給使用者的警告",
  "suppressOutput": false,
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "原因"
  }
}
```

### 實用範例

#### PreToolUse — 封鎖危險指令

```bash
#!/bin/bash
# .claude/hooks/block-dangerous.sh
COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)

if echo "$COMMAND" | grep -qE 'rm -rf|DROP TABLE|force push'; then
  echo '{"decision":"block","reason":"危險指令已封鎖"}' | jq .
  exit 0
fi
exit 0
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": ".claude/hooks/block-dangerous.sh" }]
      }
    ]
  }
}
```

#### PostToolUse — 編輯後自動執行 lint

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "npm run lint --fix" }]
      }
    ]
  }
}
```

#### Stop — 確保測試通過後才停止

```bash
#!/bin/bash
# 若測試失敗，回傳 block 讓 Claude 繼續修復
npm test > /tmp/test-output.txt 2>&1
if [ $? -ne 0 ]; then
  RESULT=$(cat /tmp/test-output.txt)
  echo "{\"decision\":\"block\",\"reason\":\"測試失敗，請修復後再停止\",\"additionalContext\":\"$RESULT\"}"
fi
exit 0
```

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [{ "type": "command", "command": ".claude/hooks/require-tests-pass.sh" }]
      }
    ]
  }
}
```

#### Notification — 發送桌面通知

```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [{
          "type": "command",
          "command": "osascript -e 'display notification \"Claude 需要你的輸入\" with title \"Claude Code\"'"
        }]
      }
    ]
  }
}
```

### Hook 設定位置

| 位置 | 範圍 | 可共享 |
|------|------|------|
| `~/.claude/settings.json` | 所有專案 | 否（個人）|
| `.claude/settings.json` | 單一專案 | 是（commit 進 repo）|
| `.claude/settings.local.json` | 單一專案（本地）| 否 |
| Plugin `hooks/hooks.json` | Plugin 啟用範圍 | 是 |
| Skill / Agent frontmatter | 該 skill/agent 執行時 | — |

### 共用欄位

所有 hook handler 支援：

| 欄位 | 說明 |
|------|------|
| `type` | 必填：`command`、`http`、`mcp_tool`、`prompt`、`agent` |
| `if` | 可選：Permission rule 過濾，如 `"Bash(git *)"` |
| `timeout` | 可選：逾時秒數（預設 600）|
| `statusMessage` | 可選：自訂 spinner 訊息 |

### 查看與管理 Hooks

```text
/hooks    # 在 session 內查看目前 hook 設定
```

---

## 十八、MCP 使用方法（Model Context Protocol）

MCP 是 Anthropic 推動的開放標準，讓 Claude Code 能連接外部工具、資料庫、API 與服務。連線後，Claude 可直接讀取並操作這些系統，無需手動貼入資料。

### 常見使用情境

| 情境 | 指令範例 |
|------|---------|
| 實作 issue tracker 功能 | "Add the feature described in JIRA-4521 and create a PR on GitHub." |
| 分析監控資料 | "Check Sentry and Statsig for usage of feature ENG-4521." |
| 查詢資料庫 | "Find 10 random users who used feature ENG-4521 in PostgreSQL." |
| 整合設計稿 | "Update email template based on new Figma designs posted in Slack." |
| 自動化工作流程 | "Create Gmail drafts inviting 10 users to a feedback session." |

---

### MCP Server 安裝

#### 方式一：HTTP Server（推薦）

HTTP 是最廣泛支援的遠端傳輸方式。

```bash
# 基本語法
claude mcp add --transport http <name> <url>

# 範例：連接 Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# 帶 Bearer token 認證
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

> `.mcp.json` 中 `type` 欄位可用 `streamable-http` 作為 `http` 的別名（符合 MCP 規格書命名）。

#### 方式二：SSE Server（已棄用）

```bash
claude mcp add --transport sse asana https://mcp.asana.com/sse \
  --header "X-API-Key: your-key-here"
```

> SSE 傳輸已棄用，有 HTTP 選項時請優先使用 HTTP。

#### 方式三：stdio Server（本地程序）

本地 stdio server 以子程序執行，適合需要直接存取系統或自訂腳本的工具。

```bash
# 基本語法（選項必須在 server name 之前，-- 之後是要執行的指令）
claude mcp add [options] <name> -- <command> [args...]

# 範例：新增 Airtable server
claude mcp add --transport stdio --env AIRTABLE_API_KEY=YOUR_KEY airtable \
  -- npx -y airtable-mcp-server

# 範例：PostgreSQL 資料庫
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"
```

> Claude Code 啟動 stdio server 時，會自動設置 `CLAUDE_PROJECT_DIR` 環境變數為專案根目錄。

#### 方式四：WebSocket Server

WebSocket 適合需要持久雙向連線、伺服器主動推送事件的情境。不支援 OAuth。

```bash
claude mcp add-json events-server \
  '{"type":"ws","url":"wss://mcp.example.com/socket","headers":{"Authorization":"Bearer YOUR_TOKEN"}}'
```

---

### 管理已設定的 Server

```bash
# 列出所有已設定的 server
claude mcp list

# 查看單一 server 詳情
claude mcp get github

# 移除 server
claude mcp remove github

# 重置 project-scope 的核准選擇
claude mcp reset-project-choices
```

```text
# 在 Claude Code session 內查看 server 狀態
/mcp
```

`/mcp` 面板顯示每個 server 的工具數量，並標記需要 OAuth 認證的 server。

---

### MCP 安裝範圍（Scope）

| Scope | 載入範圍 | 共享給團隊 | 儲存位置 |
|-------|---------|-----------|---------|
| `local`（預設）| 僅目前專案 | 否 | `~/.claude.json` |
| `project` | 僅目前專案 | 是（commit 進 repo）| `.mcp.json`（專案根目錄）|
| `user` | 所有專案 | 否 | `~/.claude.json`（global）|

```bash
# local（預設）
claude mcp add --transport http stripe https://mcp.stripe.com

# project scope（寫入 .mcp.json，適合 commit 共享）
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp

# user scope（跨所有專案可用）
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

#### Scope 優先順序

當同名 server 出現在多個位置時，依以下優先順序選用（高→低）：

1. Local scope
2. Project scope
3. User scope
4. Plugin 提供的 server
5. claude.ai connectors

#### `.mcp.json` 環境變數展開

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

支援 `${VAR}` 和 `${VAR:-default}` 語法，可用於 `command`、`args`、`env`、`url`、`headers` 欄位。

---

### OAuth 2.0 認證

當遠端 MCP server 回傳 `401 Unauthorized` 或 `403 Forbidden` 時，`/mcp` 面板會標記需要認證。

```bash
# 1. 新增需認證的 server
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# 2. 在 Claude Code session 內執行 /mcp，依提示在瀏覽器完成登入
```

```bash
# 固定 OAuth callback port（server 需預先註冊 redirect URI 時使用）
claude mcp add --transport http --callback-port 8080 my-server https://mcp.example.com/mcp

# 使用預設的 OAuth 憑證（手動申請 client_id/secret 時）
claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp

# 透過環境變數傳入 secret（適合 CI）
MCP_CLIENT_SECRET=your-secret claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

OAuth 認證 token 安全儲存於系統鑰匙圈（macOS）或憑證檔案，並自動更新。在 `/mcp` 選擇「Clear authentication」可撤銷授權。

#### 限制 OAuth Scopes

```json
{
  "mcpServers": {
    "slack": {
      "type": "http",
      "url": "https://mcp.slack.com/mcp",
      "oauth": {
        "scopes": "channels:read chat:write search:read"
      }
    }
  }
}
```

#### 動態 Header 認證（`headersHelper`）

適合 Kerberos、短效 token、內部 SSO 等非 OAuth 認證方式：

```json
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "/opt/bin/get-mcp-auth-headers.sh"
    }
  }
}
```

`headersHelper` 指令需將 JSON 物件寫入 stdout，每次連線時執行一次（無快取）。

---

### 從 JSON 設定新增 Server

```bash
# HTTP server
claude mcp add-json weather-api \
  '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'

# stdio server
claude mcp add-json local-tool \
  '{"type":"stdio","command":"/path/to/tool","args":["--verbose"],"env":{"CACHE_DIR":"/tmp"}}'

# WebSocket server
claude mcp add-json events-server \
  '{"type":"ws","url":"wss://mcp.example.com/socket"}'
```

---

### 從 Claude Desktop 匯入

```bash
# 互動式選擇要匯入哪些 server（僅限 macOS / WSL）
claude mcp add-from-claude-desktop

# 匯入到 user scope
claude mcp add-from-claude-desktop --scope user

# 確認匯入結果
claude mcp list
```

同名 server 會自動加上數字後綴（如 `server_1`）。

---

### 使用 Claude.ai Connectors

以 Claude.ai 帳號登入後，在 [claude.ai/customize/connectors](https://claude.ai/customize/connectors) 設定的 MCP server 會自動在 Claude Code 中可用。

在 session 內執行 `/mcp` 查看，connector 旁會有來源標記。

```bash
# 停用 claude.ai MCP servers
ENABLE_CLAUDEAI_MCP_SERVERS=false claude
```

> 僅在以 Claude.ai 訂閱為認證方式時有效；使用 `ANTHROPIC_API_KEY` 或第三方 provider（Bedrock、Vertex）時不會載入。

---

### 將 Claude Code 本身作為 MCP Server

```bash
# 以 stdio MCP server 模式啟動
claude mcp serve
```

在 Claude Desktop 的 `claude_desktop_config.json` 中加入：

```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "/full/path/to/claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

> 用 `which claude` 取得完整路徑。此模式下，Claude Code 的工具（View、Edit、LS 等）會暴露給連接的 MCP client 使用，工具呼叫的使用者確認由 client 端自行實作。

---

### MCP Resources（@提及）

MCP server 可暴露 resources，以 `@` 提及方式引用，和引用本地檔案相同。

```text
# 列出可用 resources（輸入 @ 觸發自動完成）
@

# 引用特定 resource
Can you analyze @github:issue://123 and suggest a fix?

# 引用多個 resources
Compare @postgres:schema://users with @docs:file://database/user-model
```

---

### MCP Prompts 作為指令

MCP server 可暴露 prompts，在 Claude Code 中以 `/mcp__<server>__<prompt>` 格式使用：

```text
# 列出所有 MCP prompt 指令（輸入 / 觸發）
/

# 執行 prompt（無參數）
/mcp__github__list_prs

# 執行 prompt（帶參數，空格分隔）
/mcp__github__pr_review 456
/mcp__jira__create_issue "Bug in login flow" high
```

---

### Tool Search（工具搜尋）

Tool Search 預設啟用，將 MCP 工具的定義延遲載入，降低 context 消耗。Claude 只有在需要時才搜尋並載入相關工具。

```bash
# 控制 Tool Search 行為（環境變數）
ENABLE_TOOL_SEARCH=true claude      # 全部延遲載入（強制啟用）
ENABLE_TOOL_SEARCH=auto claude      # 自動：工具佔用 <10% context 時預載，否則延遲
ENABLE_TOOL_SEARCH=auto:5 claude    # 自動：自訂門檻 5%
ENABLE_TOOL_SEARCH=false claude     # 停用：全部預載
```

| 值 | 行為 |
|----|------|
| (未設定) | 全部延遲，Vertex AI / 自訂 base URL 時回退為預載 |
| `true` | 強制全部延遲（即使在 Vertex AI）|
| `auto` | 門檻模式：<10% context 則預載，否則延遲 |
| `auto:N` | 門檻模式：自訂 N% 門檻 |
| `false` | 停用：全部預載 |

#### 永遠預載特定 Server（`alwaysLoad`）

```json
{
  "mcpServers": {
    "core-tools": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "alwaysLoad": true
    }
  }
}
```

設為 `true` 後，該 server 的工具會在 session 啟動時立即載入，不受 `ENABLE_TOOL_SEARCH` 影響。

---

### 輸出大小限制

| 設定 | 說明 |
|------|------|
| 警告門檻 | 工具輸出超過 10,000 tokens 時顯示警告 |
| 預設上限 | 25,000 tokens |
| 調整方式 | `MAX_MCP_OUTPUT_TOKENS=50000 claude` |

```bash
# 增加輸出上限
export MAX_MCP_OUTPUT_TOKENS=50000
claude
```

MCP server 開發者可在 `tools/list` 回應的 `_meta` 欄位中為特定工具設定個別上限（最高 500,000 字元）：

```json
{
  "name": "get_schema",
  "description": "Returns the full database schema",
  "_meta": {
    "anthropic/maxResultSizeChars": 200000
  }
}
```

---

### 環境變數彙整

| 環境變數 | 說明 | 範例 |
|---------|------|------|
| `MCP_TIMEOUT` | Server 啟動逾時（毫秒）| `MCP_TIMEOUT=10000 claude` |
| `MAX_MCP_OUTPUT_TOKENS` | 工具輸出 token 上限 | `MAX_MCP_OUTPUT_TOKENS=50000` |
| `ENABLE_TOOL_SEARCH` | Tool Search 行為 | `ENABLE_TOOL_SEARCH=auto` |
| `ENABLE_CLAUDEAI_MCP_SERVERS` | 是否載入 claude.ai connectors | `ENABLE_CLAUDEAI_MCP_SERVERS=false` |
| `MCP_CLIENT_SECRET` | OAuth client secret（CI 用）| `MCP_CLIENT_SECRET=secret` |
| `CLAUDE_PROJECT_DIR` | 專案根目錄（stdio server 內部使用）| 自動設定 |

---

### 快速範例

```bash
# Sentry 錯誤監控
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# GitHub（用 Personal Access Token）
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"

# PostgreSQL 資料庫（stdio）
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"

# 查看所有已設定 server
claude mcp list

# 在 session 內管理 / 認證
/mcp
```

---

## 十九、Plugin 使用方法

Plugin 是可自行安裝的擴充包，可為 Claude Code 新增 Skills（斜線指令）、Agents（子代理）、Hooks（事件處理）、MCP servers、LSP servers、Monitors（背景監控）以及 Themes（色彩主題）。

---

### Plugin 管理 CLI 指令

#### 安裝 / 移除

```bash
# 從 marketplace 安裝（預設 user scope）
claude plugin install formatter@my-marketplace

# 安裝到 project scope（寫入 .claude/settings.json，共享給團隊）
claude plugin install formatter@my-marketplace --scope project

# 安裝到 local scope（gitignored）
claude plugin install formatter@my-marketplace --scope local

# 移除（別名：remove、rm）
claude plugin uninstall formatter@my-marketplace

# 移除並保留 plugin 持久資料目錄
claude plugin uninstall formatter@my-marketplace --keep-data

# 移除並一併清除無用的相依 plugins
claude plugin uninstall formatter@my-marketplace --prune
```

#### 啟用 / 停用

```bash
# 啟用（不移除情況下重新啟動）
claude plugin enable my-plugin

# 停用（不移除）
claude plugin disable my-plugin
```

#### 查看清單 / 詳情

```bash
# 列出已安裝的 plugins（含版本、來源、啟用狀態）
claude plugin list

# 以 JSON 輸出（可加 --available 顯示 marketplace 可安裝項目）
claude plugin list --json --available

# 查看單一 plugin 的元件清單與預估 token 成本
claude plugin details my-plugin
```

#### 更新 / 清理

```bash
# 更新 plugin 到最新版
claude plugin update my-plugin@my-marketplace

# 清除已無 plugin 依賴的自動安裝相依項
claude plugin prune

# 預覽要清除什麼（不實際執行）
claude plugin prune --dry-run
```

#### 建立新 Plugin

```bash
# 在 ~/.claude/skills/<name>/ 建立骨架（即時載入，無需安裝步驟）
claude plugin init my-helper

# 同時建立指定元件資料夾
claude plugin init my-helper --with skills agents hooks mcp lsp

# 覆蓋既有骨架
claude plugin init my-helper --force
```

#### 驗證與發佈

```bash
# 驗證 plugin 的 plugin.json、frontmatter、hooks.json 語法
claude plugin validate ./my-plugin

# 嚴格模式（warning 也視為 error，適合 CI）
claude plugin validate ./my-plugin --strict

# 建立版本 git tag（在 plugin 目錄內執行）
claude plugin tag
claude plugin tag --push   # 同時推到遠端
```

---

### Session 內 Plugin 管理（`/plugin`）

```text
/plugin              # 開啟 plugin 管理介面（Discover / Installed / Errors 分頁）
/reload-plugins      # 重新載入 plugins（修改 hooks/MCP/agents 後需執行）
```

在 `/plugin` 介面中可：
- **Discover**：瀏覽 marketplace 可安裝的 plugins
- **Installed**：查看 / 啟用 / 停用 / 更新已安裝的 plugins
- **Errors**：查看載入錯誤（含 LSP 找不到執行檔等問題）

---

### Plugin 安裝範圍（Scope）

| Scope | 設定檔 | 適用情境 |
|-------|--------|---------|
| `user`（預設）| `~/.claude/settings.json` | 個人跨專案使用 |
| `project` | `.claude/settings.json` | 團隊共享（commit 進 repo）|
| `local` | `.claude/settings.local.json` | 個人專案專用（gitignored）|
| `managed` | 管理員部署（唯讀）| 企業統一部署 |

---

### Plugin 元件總覽

| 元件 | 目錄位置 | 功能 |
|------|---------|------|
| Skills | `skills/<name>/SKILL.md` | 建立 `/<name>` 斜線指令 |
| Commands | `commands/*.md` | 簡單的斜線指令（flat 格式）|
| Agents | `agents/*.md` | 專門用途子代理 |
| Hooks | `hooks/hooks.json` | 事件自動化處理 |
| MCP servers | `.mcp.json` | 連接外部工具 / API |
| LSP servers | `.lsp.json` | 程式碼智能（診斷、跳轉定義）|
| Monitors | `monitors/monitors.json` | 背景監控（輸出每行作為通知）|
| Themes | `themes/*.json` | 色彩主題 |
| Executables | `bin/` | 加入 Bash PATH 的執行檔 |

#### 官方 LSP Plugins

| Plugin | Language Server | 安裝方式 |
|--------|----------------|---------|
| `pyright-lsp` | Pyright (Python) | `pip install pyright` |
| `typescript-lsp` | TypeScript Language Server | `npm install -g typescript-language-server typescript` |
| `rust-analyzer-lsp` | rust-analyzer | 參考官方安裝指南 |

```text
# 先安裝 language server binary，再從 marketplace 安裝 plugin
/plugin install typescript-lsp@...
```

---

### Plugin 目錄結構

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json          ← 只有 manifest 放這裡
├── skills/
│   └── my-skill/
│       └── SKILL.md
├── commands/
│   └── status.md
├── agents/
│   └── reviewer.md
├── hooks/
│   └── hooks.json
├── .mcp.json
├── .lsp.json
├── monitors/
│   └── monitors.json
├── themes/
│   └── dark.json
├── bin/
│   └── my-tool              ← 在 Bash 工具中可直接呼叫
└── scripts/
    └── format.sh
```

> 注意：`skills/`、`agents/`、`hooks/` 等元件目錄必須在 plugin 根目錄，不能放在 `.claude-plugin/` 內。

---

### Plugin Manifest（`plugin.json`）

```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "version": "1.2.0",
  "description": "簡短說明",
  "author": { "name": "作者名稱", "email": "author@example.com" },
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "defaultEnabled": true,
  "skills": "./custom/skills/",
  "agents": ["./custom/agents/reviewer.md"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json",
  "lspServers": "./.lsp.json",
  "experimental": {
    "monitors": "./monitors/monitors.json",
    "themes": "./themes/"
  },
  "userConfig": {
    "api_token": {
      "type": "string",
      "title": "API Token",
      "description": "認證 token",
      "sensitive": true,
      "required": true
    }
  },
  "dependencies": [
    { "name": "helper-lib", "version": "~2.1.0" }
  ]
}
```

`name` 是唯一必填欄位（若省略整個 manifest，Claude Code 會自動從目錄名稱推斷）。

---

### Plugin 環境變數

| 變數 | 說明 |
|------|------|
| `${CLAUDE_PLUGIN_ROOT}` | Plugin 安裝目錄的絕對路徑（可能隨更新改變）|
| `${CLAUDE_PLUGIN_DATA}` | Plugin 持久資料目錄（`~/.claude/plugins/data/<id>/`，跨版本保留）|
| `${CLAUDE_PROJECT_DIR}` | 目前專案根目錄 |
| `${user_config.KEY}` | Plugin 啟用時使用者填寫的設定值 |

```json
{
  "mcpServers": {
    "my-server": {
      "command": "${CLAUDE_PLUGIN_ROOT}/bin/server",
      "env": { "DATA_DIR": "${CLAUDE_PLUGIN_DATA}" }
    }
  }
}
```

---

### Skills-directory Plugin（免安裝）

在 `~/.claude/skills/<name>/` 或 `<cwd>/.claude/skills/<name>/` 中放置含 `.claude-plugin/plugin.json` 的資料夾，下次 session 自動載入為 `<name>@skills-dir`，無需 marketplace / 安裝步驟。

```bash
# 建立 skills-dir plugin 骨架
claude plugin init my-helper  # 建立在 ~/.claude/skills/my-helper/

# 停用（不需 uninstall）
claude plugin disable my-tool@skills-dir

# 修改 SKILL.md 後立即生效；修改 hooks/MCP/agents 需執行：
/reload-plugins
```

---

### 版本管理

| 方式 | 設定 | 更新行為 | 適用情境 |
|------|------|---------|---------|
| 明確版本號 | `"version": "1.2.0"` in plugin.json | 只在 bump version 時更新 | 穩定發布週期 |
| Commit SHA 版本 | 省略 `version` 欄位 | 每次 commit 都是新版本 | 內部 / 快速迭代 |

---

### 常見問題排查

| 問題 | 原因 | 解決方式 |
|------|------|---------|
| Plugin 未載入 | plugin.json 語法錯誤 | `claude plugin validate` |
| Skills 不出現 | 目錄結構錯誤 | 確認 `skills/` 在 plugin 根目錄 |
| Hooks 未觸發 | 腳本無執行權限 | `chmod +x script.sh` |
| MCP server 失敗 | 路徑問題 | 使用 `${CLAUDE_PLUGIN_ROOT}` |
| LSP 找不到執行檔 | binary 未安裝 | 安裝對應 language server |
| 元件更新後未生效 | 需重載 | `/reload-plugins` |

```bash
# 開啟 debug 模式查看 plugin 載入詳情
claude --debug
```

---

## 二十、非互動模式（Headless / Print Mode）詳細用法

> 以下旗標行為已用本機安裝的 Claude Code v2.1.208（`claude --help` / 實際執行）驗證。

### 核心概念

`-p` / `--print` 讓 Claude Code 執行一次任務、印出結果後立即結束，不進入互動 REPL。適合 shell script、CI/CD pipeline、cron 排程、或作為其他程式的子行程呼叫。非互動模式下會跳過 workspace trust 對話框（stdout 非 TTY，如被 pipe 或導向檔案時也視同非互動）。

### 基本語法

```bash
claude -p "explain this project"
claude --print "find and fix the bug in auth.py" --allowedTools "Read,Edit,Bash"
```

### stdin / stdout pipe

```bash
# 從檔案 pipe 內容進去
cat build-error.txt | claude -p "explain this error"

# 導向輸出到檔案
git diff main | claude -p "check for typos" > review.txt

# 串接指令
claude -p "list TODO comments in src/" --output-format json | jq -r '.result'
```

stdin 輸入上限 10MB，超過會直接失敗。

### 輸出格式（`--output-format`）

僅在 `--print` 下生效，三種選項：

| 格式 | 說明 |
|------|------|
| `text`（預設）| 純文字回應 |
| `json` | 單一 JSON 物件，含完整結果與用量統計 |
| `stream-json` | 逐段串流 JSON 事件；**在 print mode 下必須搭配 `--verbose`**，否則報錯 |

```bash
claude -p "say hi" --output-format json
```

回傳範例（實測欄位）：

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 1937,
  "duration_api_ms": 1829,
  "num_turns": 1,
  "result": "Hi! What can I help you with today?",
  "stop_reason": "end_turn",
  "session_id": "e891d26f-...",
  "total_cost_usd": 0.0748,
  "usage": {
    "input_tokens": 2,
    "output_tokens": 14,
    "cache_read_input_tokens": 20815,
    "cache_creation_input_tokens": 11394
  },
  "permission_denials": [],
  "terminal_reason": "completed"
}
```

常用欄位：

| 欄位 | 用途 |
|------|------|
| `result` | Claude 的最終文字回應 |
| `total_cost_usd` | 本次執行花費（美元），可用來做累加預算監控 |
| `usage.input_tokens` / `output_tokens` | Token 用量細項（含 cache read/creation）|
| `num_turns` | 本次執行用了幾個回合 |
| `session_id` | 可用 `-r <id>` 之後接續此對話 |
| `is_error` / `terminal_reason` | 判斷是否成功結束（`completed` 為正常）|

```bash
# 從 script 取出費用累加、超過門檻就中止
cost=$(claude -p "$TASK" --output-format json | jq '.total_cost_usd')
```

`--json-schema` 可強制結構化輸出（搭配 `--output-format json` 使用）：

```bash
claude -p "extract the title and author from README.md" \
  --json-schema '{"type":"object","properties":{"title":{"type":"string"},"author":{"type":"string"}},"required":["title"]}'
```

### 限制執行範圍

| 旗標 | 行為 |
|------|------|
| `--max-turns <n>` | 限制最大回合（工具呼叫）數，超過即停止 |
| `--max-budget-usd <amount>` | 設定本次執行 API 花費上限（僅 print mode），達到上限即停止 |
| `--allowedTools "Read,Edit,Bash"` | 白名單，僅允許列出的工具，其餘不詢問直接拒絕 |
| `--disallowedTools "Bash(rm *)"` | 黑名單，禁止特定工具或 pattern |
| `--tools "Read,Grep"` | 直接限制本次 session 可用的內建工具集合（`""` = 全部停用）|
| `--permission-mode bypassPermissions` | 跳過所有權限提示，全自動執行（僅建議在無網路存取的沙箱使用）|
| `--permission-mode dontAsk` | 未在 `permissions.allow` 規則內的工具呼叫一律拒絕，不詢問（適合預先定義好白名單的 CI）|
| `--no-session-persistence` | 不將 session 存到磁碟（print mode 專用，適合一次性、不需要之後 `-r` 恢復的呼叫）|

```bash
# CI 中安全跑一次性任務：限制回合數、限制費用、限制工具
claude -p "run tests and report failures" \
  --max-turns 8 \
  --max-budget-usd 2 \
  --allowedTools "Read,Bash(npm test)" \
  --output-format json
```

### `--bare`：最小化啟動模式

跳過 hooks、LSP、plugin sync、auto-memory、CLAUDE.md 自動載入等，啟動更快、行為更可預期，適合 CI：

```bash
claude --bare -p "summarize this file" --allowedTools "Read"
```

`--bare` 下驗證身份僅接受 `ANTHROPIC_API_KEY` 或 `apiKeyHelper`（不讀 OAuth / keychain）。需要 context 時要明確傳入：`--system-prompt[-file]`、`--append-system-prompt[-file]`、`--add-dir`、`--mcp-config`、`--settings`、`--agents`、`--plugin-dir`。

### 恢復與命名

```bash
claude -p "continue the refactor" --resume e891d26f-af48-4798-a239-ea8f12cc8f09
claude -p "..." --session-id <uuid>       # 指定固定 session ID，方便日後追蹤
claude -p "..." --fork-session -r <id>    # 從既有對話分支出新 session，不覆蓋原本
```

### Claude Agent SDK（程式化嵌入）

若要在自己的應用程式/服務中嵌入 Claude Code 的能力（而不是呼叫 CLI 子行程），可用官方 Agent SDK：

| 語言 | 套件 |
|------|------|
| Python（3.10+） | `claude-agent-sdk` |
| TypeScript | `@anthropic-ai/claude-agent-sdk` |

內建與 CLI 相同的工具集（Read/Write/Edit/Bash/Glob/Grep/WebSearch/WebFetch），也支援 Hooks、Subagents、MCP、Sessions。適合需要在生產服務中重複呼叫、需要更細緻程式控制（而非純 shell 呼叫）的情境。

### CI/CD 整合

- **GitHub Actions**：官方 action，可用 `@claude` 於 PR/Issue 留言觸發，或設定自動化 workflow；底層即為此 headless 模式
- **GitLab CI/CD**：官方文件另有對應整合方式
- 兩者本質上都是在 runner 上呼叫 `claude -p ...`，搭配 `--allowedTools`、`--max-turns`、`--output-format json` 做好邊界與可觀測性

### 與互動模式的差異

| 面向 | 互動模式 | 非互動模式（`-p`）|
|------|------|------|
| Workspace trust 對話框 | 顯示 | 跳過（僅在你信任的目錄使用）|
| 設定檔驗證失敗 | 顯示錯誤對話框 | 靜默忽略 |
| Session 預設持久化 | 是 | 是（可用 `--no-session-persistence` 關閉）|
| 權限提示 | 逐次詢問 | 需靠 `--allowedTools` / `--permission-mode` 預先定義，否則卡住等不到輸入 |
| `/loop`、`/goal` 等 REPL 專屬指令 | 可用 | 部分可透過把指令當作 prompt 傳入（如 `claude -p "/goal ..."`），但沒有畫面互動 |

### 注意事項

- 非互動模式下沒有人能回應權限提示，務必用 `--allowedTools` / `--dangerously-skip-permissions` / `--permission-mode` 先講清楚邊界，否則行程會卡住直到 timeout
- `--max-turns` 與 `--max-budget-usd` 都只在單次執行內生效，不會記憶跨呼叫的累積用量；長期用量監控請搭配 `--output-format json` 自行在 script 中累加 `total_cost_usd`，或在 Anthropic Console 設定 workspace 層級 spend limit
- `stream-json` 輸出在 print mode 下必須加 `--verbose`，否則直接報錯拒絕啟動
- 只有你在自己信任的目錄下執行非互動模式才安全，因為 trust dialog 被跳過
