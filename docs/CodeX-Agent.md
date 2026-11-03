# Codex 多 Agent 工作與 Code Review 指南

> 本文是 `Claude-Agent.md` 的 OpenAI Codex 對應版：聚焦「工作流程與選型」——何時用哪種平行工作方式、如何同時審查不同部分、如何追蹤與彙整。
> 指令與旗標的完整清單請見 `CodeX-CLI.md`；Agents SDK 與 coredump 分析架構請見 `openAI-python-agent.md`。
>
> 狀態：骨架草稿，逐節討論中。更新日期：2026-11-03

---

## 資料來源與驗證狀態

> **重要**：撰寫本文時，`developers.openai.com` 不在這個雲端 session 的允許網域內，**無法直接讀取 OpenAI 官方頁面**；本機也未安裝 `codex`，**無法用 `--help` 實測**。因此下列內容的來源與可信度分三級，後續每節都會沿用這些標記。

| 標記 | 意義 |
|------|------|
| ✅ 本地文件 | 取自 `CodeX-CLI.md`（codex-cli 0.137.0，2026-06-05 實測 help） |
| 🔎 官方（間接） | 官方頁面經網路搜尋摘要得到，**未直接讀取原頁**；細節以官方最新文件為準 |
| ⚠️ 未驗證 | 只見於第三方文章，或來源互相矛盾 |

**目前已掌握的重點：**

| 項目 | 狀態 | 內容 |
|------|------|------|
| Subagents 存在 | 🔎 | 可平行跑多個 agent 並彙整結果；**只有在你明確要求時才會 spawn** |
| 啟用方式 | ⚠️ | 實驗性功能；來源提到 `/experimental` 或 `config.toml` 的 `[features]` 旗標，**旗標名稱各來源不一致，需以當前版本確認** |
| 自訂 agent | 🔎 | 每個 agent 一個 TOML 檔，放 `~/.codex/agents/`（個人）或 `.codex/agents/`（專案）；可設描述、developer instructions、model、sandbox、MCP |
| 並行與深度上限 | 🔎 | `[agents]` 表：`max_threads` 預設 6、`max_depth` 預設 1（官方建議保持預設，避免 fan-out 暴增）、`job_max_runtime_seconds`（CSV 批次每 worker 逾時，預設 1800 秒）|
| Sandbox | 🔎 | subagent 繼承目前的 sandbox 政策，可針對單一 agent 覆寫（例如設唯讀）|
| 管理 | ✅🔎 | `/agent` 切換 agent thread（本地文件已列）；可要求 Codex steer / stop / close subagent |
| 適用場景與風險 | 🔎 | 適合讀取為主的工作（探索、測試、分流）；多個 agent 同時**寫**同一份程式碼會衝突；token 用量高於單 agent |
| GitHub code review | 🔎 | PR 留言 `@codex review` 觸發；可附焦點（如 `@codex review for security regressions`）；GitHub 上只標 P0 / P1；可設自動審新 PR；常駐規則寫在 repo 的 `AGENTS.md`；`@codex fix …` 可啟動雲端任務 |
| 本機 review 指令 | ✅ | `/review`、`codex review`、`codex exec review`（見 `CodeX-CLI.md` 第七、八章）|
| Codex Cloud | ✅ | `codex cloud exec/list/status/apply/diff`（見 `CodeX-CLI.md` 第十五章）|
| Worktree / 保留數量 | ⚠️ | 只見於第三方，且對保留數量說法不一，**不採用具體數字** |

**參考來源（官方頁面，間接）：**
[Subagents](https://developers.openai.com/codex/subagents)、
[Subagents 概念](https://developers.openai.com/codex/concepts/subagents)、
[GitHub integration](https://developers.openai.com/codex/integrations/github)、
[Cloud code review](https://developers.openai.com/codex/cloud/code-review)。

---

## 1. 概念與定位

「多 agent」在 Codex 裡不是單一功能，而是幾種不同層次的機制，差別在於**誰決定下一步**、**跑在哪裡**、以及**檔案是否隔離**。以下逐一介紹（標記意義見上方「資料來源與驗證狀態」），第 2 節再用一張表整體對照。

與 Claude Code 的重要差異先說在前：**Codex 沒有「Agent View」那種統一管理多個背景 session 的內建畫面**（本地文件與官方摘要中都找不到對應功能）；要並行追蹤多個獨立任務，主要靠 Codex Cloud 的 task 清單，或自己用 shell 管理多個 `codex exec` 程序。

前三者（1.1–1.3）是 CLI 直接可用的平行工作方式；1.4 偏桌面 App；1.5 屬於「用 API / SDK 自己蓋編排」的層級，一般的互動式 code review 用不到。

### 1.1 Subagents（agent thread，session 內委派）

- **是什麼**：在主對話中，Codex 把任務交給多個 subagent 平行執行，再彙整結果。🔎
- **誰控制流程**：主 session 的 Codex。**只有在你明確要求時才會 spawn**，不會自動展開。🔎
- **啟用**：實驗性功能。可用 `/experimental` 切換（本地文件已列此指令 ✅）；另有 `config.toml` 旗標的說法，**但旗標名稱各來源不一致 ⚠️**，請以你所用版本的 `/experimental` 清單為準。
- **跑在哪裡**：同一個 CLI session 內，以多個 thread 並行。🔎
- **自訂 agent**：每個 agent 一個 TOML 檔，放 `~/.codex/agents/`（個人）或 `.codex/agents/`（專案，可隨 repo 共享）；可設描述、developer instructions，並覆寫 model、sandbox、MCP 等設定；內建有通用的 `default` agent。🔎
- **上限**：`[agents]` 表的 `max_threads`（同時開啟的 thread 數，預設 6）、`max_depth`（巢狀深度，預設 1：直接子 agent 可 spawn，更深則不行）、`job_max_runtime_seconds`（CSV 批次每個 worker 的逾時，預設 1800 秒）。官方建議保持 `max_depth` 預設，因為調高會讓 fan-out、token 與延遲倍增。🔎
- **隔離性**：subagent **繼承**目前的 sandbox 政策，可針對單一 agent 覆寫（例如某個 reviewer 設成唯讀）。🔎 這是**權限**的隔離，不是**檔案**的隔離——多個 agent 若同時寫同一份程式碼會衝突，官方建議把平行用在讀取為主的工作（探索、測試、分流）。🔎
- **管理**：`/agent` 切換目前的 agent thread ✅；也可要求 Codex steer、stop 或 close 某個 subagent。🔎
- **成本**：token 用量高於同樣工作的單 agent 流程。🔎
- **適合**：把一次 code review 拆成「每個 subagent 審一個檔案／模組」，唯讀、同時跑、再彙整。← 你的主力情境。

### 1.2 Codex Cloud（雲端任務，可平行提交多個）

- **是什麼**：`codex cloud` 把任務提交到雲端執行，再用指令瀏覽結果、把 diff 套回本機。本機 help 標示為 **experimental**。✅
- **誰控制流程**：你。每個 task 是獨立提交的；task 內部由它自己的 agent 處理。
- **指令**：✅
  - `codex cloud exec --env <ENV_ID> [QUERY]`：不開 TUI 直接提交；`--attempts <N>` 做 best-of-N（預設 1）；`--branch <BRANCH>` 指定要在哪個 Git branch 上執行。
  - `codex cloud list`：列 task（`--env`、`--limit` 1–20、`--cursor`、`--json`）。
  - `codex cloud status <TASK_ID>`：查狀態。
  - `codex cloud diff <TASK_ID> [--attempt <N>]`：看 unified diff。
  - `codex cloud apply <TASK_ID> [--attempt <N>]`：把 diff 套回本機工作樹。
- **隔離性**：task 不在你的本機工作樹裡跑，所以彼此不會覆蓋你的檔案；是否每個 task 各用獨立容器，目前只見於第三方文章 ⚠️，不採用。
- **追蹤**：`list` / `status` 就是追蹤入口（見第 4 節）。
- **適合**：多個彼此獨立、耗時的任務同時進行（例如「A 審前端、B 審後端」各提交一個 task），電腦不必一直開著盯。
- **限制**：需要先設定好雲端環境（`--env`）；是否支援你的 repo 與 plan 請以官方設定為準。

### 1.3 多個獨立的 `codex exec` 程序（非互動，自行並行）

- **是什麼**：`codex exec` 是非互動模式，適合 shell script、CI、批次任務。✅ 把它當成積木，你自己用 shell 開多個程序，就得到「多 agent 並行」——但**編排完全由你負責**，Codex 不會幫你協調。
- **誰控制流程**：你的腳本。
- **相關旗標**：✅
  - `--json`：以 JSONL 輸出事件；`-o, --output-last-message <FILE>`：把最後一則訊息寫入檔案，方便彙整。
  - `--output-schema <FILE>`：指定最終輸出的 JSON Schema，讓各程序輸出格式一致。
  - `--ephemeral`：不把 session 檔案存到磁碟。
  - `-C <DIR>`：指定工作目錄；搭配每個程序一個 `git worktree`，即可做到檔案隔離。
  - `codex exec resume [SESSION_ID]`：延續非互動 session。
  - `codex exec review`：在 exec 工作流下做 code review。
- **注意**：`codex exec` 預設要求在 Git repository 中執行；非 Git 目錄要加 `--skip-git-repo-check`，並只在安全的隔離目錄使用。✅
- **適合**：CI 裡的批次審查、需要精確控制「每個程序審什麼、輸出什麼格式」的情境，或要把 Codex 嵌進既有 pipeline。

### 1.4 Codex Desktop App 與 app-server（偏桌面／整合）

- **是什麼**：`codex app [PATH]` 啟動 Codex Desktop App（未安裝則開 installer）；`codex app-server` 等屬於進階整合入口。✅
- **與多 agent 的關係**：桌面 App 是否提供「多個 thread ＋ 各自 worktree」的並行介面，目前只見於第三方文章 ⚠️，本文不展開；若你實際在用，請以 App 內說明為準。
- **適合**：偏好圖形介面的使用者；本文其餘章節以 CLI 為主。

### 1.5 `codex mcp-server` 與 Agents SDK（API 層級）

- **`codex mcp-server`**：把 Codex 自己啟動成 MCP server，讓其他 client 以 stdio 接入。✅ 也就是說，別的程式（例如用 Agents SDK 寫的編排器）可以把 Codex 當成一個工具來呼叫。
- **OpenAI Agents SDK**：用 SDK 自己寫編排邏輯、多個 agent 之間交接。本 repo 的 `openAI-python-agent.md` 有以 coredump 分析為例的架構與選型。✅
- **與 code review 的關係**：這是**產品整合／自建編排**用的，不是在 Codex CLI 裡做互動式 review 的入口。如果你要的是「審這次改動」，用 1.1–1.3 即可。

> **一句話定調**：做 code review，重點看 **1.1 Subagents**（同一 session 唯讀分工審查）與 **1.2 Codex Cloud**（多個獨立任務並行、可追蹤）；需要精確控制或接 CI 時用 **1.3 多個 `codex exec`**；**1.4／1.5** 屬於桌面或 API 層級，本文其餘章節不深入。另有內建的 review 入口（`/review`、`codex review`、GitHub `@codex review`），見第 3 節。

---

## 2. 平行工作方式的選型

> TODO：Workflow vs Worktree 釐清框（Codex 的隔離：git worktree vs sandbox 模式，兩件事）＋八欄選型對照表。

---

## 3. Code Review 的多 Agent 做法

> TODO：`/review`、`codex review`、`codex exec review`、Cloud 並行、手動分檔、GitHub `@codex review`，以及 review 相關指令總覽。

---

## 4. 如何追蹤與彙整

> TODO：`codex cloud list/status/diff/apply`、`resume` / `fork`、`/agent`、`/goal`、worktree 清理。

---

## 5. 實務建議與陷阱

> TODO：sandbox 與 approval 組合、成本、Git repo 限制、何時用哪種。

---

## 附錄 A　實戰範例：用 Codex 追蹤 fastpath 的 memory / refcount 難題

> TODO：與 `Claude-Agent.md` 附錄 A 同一情境，改用 Codex 分工與範例 prompt；可銜接 `openAI-python-agent.md` 的 coredump 分析架構。
