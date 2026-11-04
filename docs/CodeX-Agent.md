# Codex 多 Agent 工作與 Code Review 指南

> 本文是 `Claude-Agent.md` 的 OpenAI Codex 對應版：聚焦「工作流程與選型」——何時用哪種平行工作方式、如何同時審查不同部分、如何追蹤與彙整。
> 指令與旗標的完整清單請見 `CodeX-CLI.md`；Agents SDK 與 coredump 分析架構請見 `OpenAI-Python-Agent.md`。
>
> 狀態：初版完成（五節與附錄 A 皆已填）。更新日期：2026-11-03

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
- **OpenAI Agents SDK**：用 SDK 自己寫編排邏輯、多個 agent 之間交接。本 repo 的 `OpenAI-Python-Agent.md` 有以 coredump 分析為例的架構與選型。✅
- **與 code review 的關係**：這是**產品整合／自建編排**用的，不是在 Codex CLI 裡做互動式 review 的入口。如果你要的是「審這次改動」，用 1.1–1.3 即可。

> **一句話定調**：做 code review，重點看 **1.1 Subagents**（同一 session 唯讀分工審查）與 **1.2 Codex Cloud**（多個獨立任務並行、可追蹤）；需要精確控制或接 CI 時用 **1.3 多個 `codex exec`**；**1.4／1.5** 屬於桌面或 API 層級，本文其餘章節不深入。另有內建的 review 入口（`/review`、`codex review`、GitHub `@codex review`），見第 3 節。

---

## 2. 平行工作方式的選型

> **釐清框：Sandbox 與 Worktree 不是同一件事（Codex 最常見的混淆）**
>
> 兩者都叫「隔離」，但隔離的東西完全不同，而且**正交、常一起用**：
>
> | | Sandbox（沙箱）＋ approval | Worktree（工作樹）|
> |---|---|---|
> | 本質 | Codex 的**權限邊界**：能讀寫哪裡、能否連網、哪些操作要先問你 | **git 功能**：獨立的工作目錄 + branch，共用同一份 repo 歷史 |
> | 解決什麼 | agent **能做什麼**（防止它碰不該碰的東西）| 平行工作**改哪份檔案**（防止彼此覆蓋）|
> | 層次 | 作業系統／權限層 | 檔案系統／版本控制層 |
> | 怎麼設 | `-s` / `--sandbox`：`read-only`、`workspace-write`、`danger-full-access`；`-a` / `--ask-for-approval`：`untrusted`、`on-request`、`never` ✅ | `git worktree add …`，再用 `codex exec -C <DIR>` 或在該目錄啟動 Codex ✅（`git worktree` 為 git 功能）|
> | 對 subagent | 繼承目前政策，可單一 agent 覆寫 🔎 | **官方未見內建的 per-subagent worktree 機制** ⚠️；多個 agent 寫同一份程式碼會衝突 🔎 |
>
> 比喻：**Sandbox ＝ 每個工人的權限證**（能進哪些房間、能不能動工具）；**Worktree ＝ 每個工人各自的工作檯**（東西不混在一起）。唯讀審查只需要 sandbox 設成 `read-only`，**不需要 worktree**；要多個 agent「同時寫」才需要 worktree。
>
> 常見組合（✅ 取自 `CodeX-CLI.md`）：一般本機開發 `-s workspace-write -a on-request`；嚴格審查 `-s read-only -a untrusted`；CI 非互動 `codex exec -a never --json`。

> **與 Claude Code 對照**：Claude 的 subagent 可設 `isolation: worktree` 自動開 worktree；Codex 沒有已驗證的對應設定，要隔離檔案得**自己建 worktree** 並用 `-C` 指向它。Claude 的 Workflows（腳本編排大量 agent）在 Codex 裡沒有內建對應，同類需求要走 1.3（自己寫腳本）或 1.5（Agents SDK）。

下表把第 1 節的三種 CLI 層級方式，依八個角度整體對照（Desktop App、`mcp-server` ＋ Agents SDK 屬桌面／API 層級，不列入）：

| 方式 | 誰決定下一步 | 中間結果放哪 | 檔案隔離 | 可否重播 | 規模 | 如何追蹤 | 適合情境 |
|------|------|------|------|------|------|------|------|
| **Subagents** 🔎 | 主 session 的 Codex（你明確要求才 spawn）| 各 thread 自己的 context，再回報主 session | 無內建；僅 sandbox 權限可個別覆寫 | 自訂 agent 的 TOML 定義可重用；單次委派不留存 | `max_threads` 預設 6、`max_depth` 預設 1 | `/agent` 切換 thread；可要求 steer／stop／close | 唯讀的分檔／分模組審查、探索、分流 |
| **Codex Cloud** ✅ | 你手動提交每個 task | 雲端 task（不在你的工作樹）| 不碰你的本機檔案；套回前先 `diff` 檢視 | task ID 可隨時 `status`／`diff`／`apply`；`--attempts` 做 best-of-N | 由雲端環境與額度決定（細節未驗證 ⚠️）| `codex cloud list`／`status` | 多個獨立、耗時任務並行，不用盯著電腦 |
| **多個 `codex exec`** ✅ | 你的腳本 | 各程序自己的 session；用 `--json`／`-o` 落地 | 自建 `git worktree` 並用 `-C` 指向 | `codex exec resume`；腳本本身可版控重用 | 自行決定，受機器與額度限制 | 自己的腳本與 log（`--json` 事件流）| CI 批次審查、需精確控制輸入輸出格式 |

> 速記：**要同一 session 內唯讀分工審查 → Subagents**；**要多個獨立耗時任務並行、可追蹤 → Codex Cloud**；**要接 CI、精確控制 → 多個 `codex exec`**。要多個 agent **同時寫**程式碼時，一定要自己建 worktree（見上方釐清框）。
>
> 標記：✅ 本地文件、🔎 官方間接、⚠️ 未驗證（見文首說明）。方式名稱後的標記代表該列的主要來源；個別格子若來源不同，會在格內另外標註。

---

## 3. Code Review 的多 Agent 做法

Codex 的 code review 入口比較分散：本機有單次審查指令，「多 agent 同時審不同部分」則要靠 subagent、Cloud 多任務，或自己用 `codex exec` 平行。先給結論，再逐一說明（標記 ✅🔎⚠️ 意義見文首）。

> **速選**：開發途中快速看 → **3.1 本機 `/review`／`codex review`**；同一 session 內分檔唯讀並行審 → **3.2 Subagents**；多個獨立耗時審查要並行追蹤 → **3.3 Codex Cloud**；接 CI、精確控制輸出 → **3.4 多個 `codex exec`**；PR 全自動審 → **3.5 GitHub `@codex review`**。

> **與 Claude Code 的差異**：Codex 沒有已驗證的「一鍵啟動雲端多 reviewer 並獨立驗證每個 finding」指令（對應 Claude 的 `/code-review ultra`）。要多 agent 審查，得自己用 3.2–3.4 組合；若要降低誤報，可仿照 Claude 附錄的做法，另派一個獨立驗證 agent 複核（見附錄 A）。

### 3.1 本機單次審查：`/review`、`codex review`、`codex exec review`

- **做什麼**：對本機改動做一次審查。依文件為**單次審查**，未見多 agent 並行或獨立驗證的說明（此為依文件推論 ⚠️）。
- **怎麼啟動**：
  ```text
  /review                              # 互動式 CLI：對 working tree 做 review ✅
  ```
  ```bash
  codex review --uncommitted           # review staged、unstaged、untracked 變更 ✅
  codex review --base main             # 與指定 base branch 比較 ✅
  codex review --commit abc1234        # review 某個 commit 引入的變更 ✅
  codex review "focus on security and backward compatibility"   # 以 prompt 指定焦點 ✅
  codex exec review                    # 在 exec 工作流下做 review ✅
  ```
  `--title <TITLE>` 可額外指定 review summary title。✅
- **追蹤**：互動模式在畫面上看；非互動用 `--json` 取事件流，或 `-o` 把最後一則訊息寫檔。
- **適合**：開發途中快速回饋；用 prompt 指定焦點（安全、相容性…）取代 Claude 的 `/security-review`。

### 3.2 手動派多個 subagent 分檔／分模組審查 🔎

當你想**明確控制「誰審哪個檔案」**、並在同一個 session 內並行跑時，用這條路。

- **做什麼**：一次要求 Codex spawn 多個 subagent，每個負責一個檔案或模組，各自跑完回報，再由主 Codex 彙整。
- **怎麼啟動**：subagent **只有在你明確要求時才會 spawn**，所以 prompt 要講明白：
  ```text
  請 spawn 三個 subagent，分別審 src/fib/、src/neighbour/、src/route/。
  每個 subagent 只讀、不改檔，依下列準則找 refcount 配對問題，
  各自回報 findings，最後由你彙整去重。
  ```
  先確認功能已啟用（實驗性，`/experimental`；旗標名稱各來源不一 ⚠️）。
- **自訂 reviewer**：可建立 `.codex/agents/<name>.toml`（專案共享）或 `~/.codex/agents/`（個人），每個 agent 一個 TOML 檔，可設描述、developer instructions，並覆寫 model、sandbox 等。**欄位的確切名稱我未驗證，請以官方文件為準。**
- **隔離**：審查要唯讀，把該 agent 的 sandbox 覆寫成 `read-only`；subagent 繼承你目前的政策，所以只要整個 session 本來就是 `read-only` 就不用額外設定。純審查**不需要 worktree**。🔎
- **上限**：同時最多 `max_threads` 個（預設 6）；`max_depth` 預設 1，不要調高。🔎
- **追蹤**：`/agent` 切換 thread；可要求 Codex steer、stop、close。🔎
- **成本**：token 用量高於單 agent，大任務先小範圍試跑。🔎
- **適合**：分工清楚、各檔案相對獨立的審查；或想把結果留在主 session 一起討論。

### 3.3 Codex Cloud 並行提交多個審查任務 ✅

當有**多個彼此獨立、耗時**的審查，想提交後不用一直開著電腦時用。

- **做什麼**：每個審查範圍提交一個 cloud task：
  ```bash
  codex cloud exec --env <ENV_ID> --branch feature-x "審查 src/fib/ 的 refcount 配對問題，只讀不改"
  codex cloud exec --env <ENV_ID> --branch feature-x "審查 src/route/ 的 refcount 配對問題，只讀不改"
  ```
  （`--attempts <N>` 可做 best-of-N；預設 1。）
- **追蹤**：`codex cloud list`（可 `--env`、`--limit`、`--json`）、`codex cloud status <TASK_ID>`。
- **取回結果**：`codex cloud diff <TASK_ID>` 看 unified diff；`codex cloud apply <TASK_ID>` 套回本機。
- **注意**：`codex cloud` 在本機 help 標示為 **experimental**；任務是否以文字 findings（而非 diff）回報、以及每個 task 的隔離與額度，**我未驗證** ⚠️。需要先設定好雲端環境（`--env`）。
- **適合**：多個獨立耗時任務並行；因為不在你的工作樹裡跑，不會覆蓋本機檔案。

### 3.4 多個 `codex exec` 平行（CI／精確控制）✅

編排由你負責，Codex 不會幫你協調。

- **做法**：每個審查範圍開一個唯讀的非互動程序，輸出落地成檔，最後自己彙整。示意如下（**未在實際環境執行**，請依你的目錄與需求調整）：
  ```bash
  mkdir -p out
  printf '%s\n' src/fib src/neighbour src/route |
    xargs -P 3 -I{} sh -c '
      codex exec --sandbox read-only -a never \
        --output-last-message "out/$(echo {} | tr / _).md" \
        "審查 {} 的 refcount 配對問題，只回報有具體呼叫序列的問題，其餘標為推測"'
  ```
- **要點**：`--sandbox read-only` 保證不改檔；`-a never` 讓 CI 不會卡在提示；`-o` 把結果寫檔；要固定輸出格式可加 `--output-schema <FILE>`；要事件流用 `--json`。
- **適合**：CI 批次審查、需要精確控制「每個程序審什麼、輸出什麼格式」。

### 3.5 GitHub 端：`@codex review` 🔎

- **做什麼**：在 PR 頂層留言 `@codex review`，Codex 以 eyes reaction 表示接手，並貼出標準的 GitHub review。
- **前置條件**：需先設定好 Codex cloud，並在 Codex 設定中對該 repo 開啟 Code review。
- **指定焦點**：可附一次性的焦點，例如 `@codex review for security regressions`；常駐規則寫在 repo 的 `AGENTS.md`（用 `/init` 可產生 scaffold ✅）。
- **嚴重度**：GitHub 上只標 **P0／P1**，讓留言聚焦在高優先風險。
- **自動審查**：設定中有開關，可在 PR 開啟時自動審，不必留言。（觸發時機的細節各來源略有出入，以官方最新文件為準 ⚠️。）
- **後續動作**：其他 `@codex` 留言，例如 `@codex fix the P1 issue`，會以 PR 為脈絡啟動雲端任務；有權限時可把修正推到分支。
- **適合**：PR 想全自動、不必人工在本機下指令。

### 3.6 review 相關入口總覽與選擇

| 入口 | 位置 | 用途 | 備註 |
|------|------|------|------|
| `/review` | 互動 CLI | 對 working tree 做 review | ✅ |
| `codex review` | CLI | `--uncommitted`／`--base`／`--commit`／prompt 焦點 | ✅ 單次審查 |
| `codex exec review` | CLI（非互動）| 在 exec 工作流下 review | ✅ |
| `/diff` | 互動 CLI | 顯示 Git diff（含未追蹤檔案），適合自己先看一遍 | ✅ |
| `codex cloud exec …` | CLI → 雲端 | 提交雲端任務 | ✅ experimental |
| `@codex review` | GitHub PR | PR 自動／手動審查 | 🔎 需 Codex cloud 設定 |
| `@codex fix …` | GitHub PR | 以 PR 為脈絡啟動雲端修復任務 | 🔎 |

| 情境 | 建議 |
|------|------|
| 開發途中快速看一下 | `/review` 或 `codex review --uncommitted` |
| 只擔心安全／相容性 | `codex review "focus on security …"`（prompt 指定焦點）|
| 同一 session 分檔並行唯讀審 | 3.2 Subagents |
| 多個耗時審查並行、不盯電腦 | 3.3 Codex Cloud |
| 接 CI、精確控制輸出 | 3.4 多個 `codex exec` |
| PR 全自動審 | 3.5 `@codex review` |
| 要自動修 | `@codex fix …` 或在本機讓 Codex 依 finding 修改 |

> Codex 沒有已驗證的內建對應 Claude 的 `/security-review`（專攻安全）與 `/simplify`（只找 cleanup）；用 prompt 指定焦點即可達到類似效果。

> ⚠️ **文件 vs 程式碼**：`/review` 與 subagent 預設審的是**程式碼 diff**。若審查對象是 Markdown／文件，審查會偏向**內容與事實查核**；此時在 prompt 裡講清楚「查事實正確性、連結有效性」，並用 3.2 分檔派 subagent，會比單次 `/review` 更貼切。

---

## 4. 如何追蹤與彙整

平行工作最怕「派出去就看不到了」。Codex 沒有 Claude 那種統一的 Agent View 畫面（見第 1 節），所以**追蹤入口依做法而分散**，彙整多半要自己動手。標記 ✅🔎⚠️ 意義見文首。

### 4.1 追蹤入口一覽

| 想看什麼 | 用哪個 |
|------|------|
| session 內的 subagent | `/agent` 切換目前的 agent thread ✅；可要求 Codex steer、stop、close 🔎 |
| Cloud 任務 | `codex cloud list`、`codex cloud status <TASK_ID>` ✅ |
| 背景 terminal | `/ps` 檢視、`/stop` 停止 ✅（指**背景 terminals**，不是 subagent 或 cloud task）|
| 自己的 `codex exec` 程序 | 你的腳本與 log；`--json` 事件流、`-o` 寫檔 ✅ |
| 先前的 session | `codex resume`、`codex fork`、`codex archive`／`unarchive` ✅ |
| 目前 session 狀態與用量 | `/status`（設定、token usage 等）✅ |
| 完成通知 | 未見已驗證的「主動通知回 session」機制 ⚠️；非互動程序以 exit code 與輸出檔判斷 |

### 4.2 Cloud 任務的追蹤與取回 ✅

```bash
codex cloud list --env <ENV_ID> --limit 20 --json   # 列任務（--limit 為 1–20，預設 20；--cursor 分頁）
codex cloud status <TASK_ID>                         # 查單一任務狀態
codex cloud diff <TASK_ID> [--attempt <N>]           # 看 unified diff
codex cloud apply <TASK_ID> [--attempt <N>]          # 把 diff 套回本機工作樹
codex apply <TASK_ID>                                # 不經 cloud 子命令，直接以 git apply 套用最新 diff
```

- 用 `--attempts <N>`（best-of-N）提交時，`diff`／`apply` 用 `--attempt <N>` 指定要看或套用哪一次嘗試。
- **套回前先 `diff` 檢視**：`apply` 會直接改你的工作樹；先確認沒有不該動的檔案，並確保工作樹乾淨，才好 `git diff` 出差異。
- `list --json` 可接腳本做簡易看板（例如定時輪詢、列出尚未完成的 task）。
- 本機 help 標示 `codex cloud` 為 **experimental**，指令行為可能隨版本調整。

### 4.3 Subagent 的追蹤 🔎

- 在主 session 裡用 `/agent` 在各 thread 之間切換，查看各自的進度與輸出。
- 子 agent 跑偏時，直接對 Codex 說要 **steer**（改方向）、**stop**（停止）或 **close**（關閉）。
- `max_threads`（預設 6）決定同時開啟的 thread 上限；超過的要等有空位。
- **沒有跨 session 的總覽**：subagent 活在主 session 裡，關掉主 session 就看不到了；需要長期追蹤的工作，改走 Cloud（4.2）或自己的 `codex exec`（4.5）。

### 4.4 Session 管理：resume、fork、archive ✅

| 指令 | 用途 |
|------|------|
| `codex resume [SESSION_ID] [PROMPT]` | 恢復先前互動式 session；`--last` 取最近一次、`--all` 列出所有 cwd 的 session、`--include-non-interactive` 連非互動 session 也列入 |
| `codex fork [SESSION_ID] [PROMPT]` | 從舊 session **分叉**成新 session（`--last`、`--all`）；適合「同一份 context，試另一種做法」 |
| `codex archive <SESSION>`／`unarchive` | 封存或還原已儲存的 session |
| `/resume`、`/fork`、`/new`、`/clear` | 互動模式內的對應操作 |
| `codex exec resume [SESSION_ID]` | 延續**非互動** session |

- 想把一個調查「分支」成兩條假說各自追，`fork` 是最直接的工具（附錄 A 的競爭假說調查會用到）。
- `resume` 會延續先前 session，所以**不適合當作有嚴格成本、資料隔離或 per-ticket token 預算時的預設機制**；每個獨立事件通常應開新的 `codex exec`，只有明確需要延續同一工作時才 `resume`。✅（本地文件原則）

### 4.5 自己編排時的追蹤（多個 `codex exec`）✅

沒有內建看板，建議自己建立最小的追蹤機制：

- **一個程序一份輸出檔**：`-o out/<範圍>.md`（最後訊息）或 `--json > out/<範圍>.jsonl`（完整事件流）。
- **一個帳本檔**：沿用 `Claude-Agent.md` 附錄 A.5 的格式（ID、位置、主張、證據、信心、驗證狀態、負責 agent），由你或主腳本彙整。
- **exit code**：腳本檢查每個程序是否成功；失敗的範圍重跑。
- **固定輸出格式**：`--output-schema <FILE>` 讓各程序輸出同一個 JSON 結構，彙整時直接合併，不必解析自由文字。

### 4.6 彙整結果

- **Subagents**：各 subagent 回報給主 session，由主 Codex 收攏、去重、排序，形成一份整體結論。🔎
- **Codex Cloud**：每個任務的結果留在各自的 task；你用 `diff` 逐一檢視，再決定要 `apply` 哪些。✅ 若要合併多份審查意見，需自己整理（或開一個本機 session 讀這些 diff 再彙整）。
- **多個 `codex exec`**：輸出檔由你的腳本合併；建議再開一個**獨立驗證**的 `codex exec`，只看彙整清單與程式碼，逐條複核（做法見附錄 A）。
- **GitHub `@codex review`**：結果以 GitHub review／留言呈現在 PR 上，標 P0／P1。🔎

### 4.7 Worktree 與暫存清理

- 本文建議的 worktree 都是**你自己用 `git worktree` 建的**（見第 2 節），因此**清理也由你負責**：

  ```bash
  git worktree list
  git worktree remove ../review-fib          # 無未提交變更時
  git worktree prune                         # 清除已不存在目錄的登記
  ```
- Claude Code 會自動刪除「無變更」的 worktree；Codex 沒有已驗證的對應自動清理行為。桌面 App 若自己管理 worktree，其保留數量與清理規則只見於第三方且互相矛盾 ⚠️，不採用。
- `codex exec --ephemeral` 不把 session 檔案存到磁碟 ✅，適合不需要日後 `resume` 的一次性審查，可減少殘留。

---

## 5. 實務建議與陷阱

標記 ✅🔎⚠️ 意義見文首。

### 5.1 一句話選型

- 任務**單一、可快速說清楚** → 不要用多 agent，一個 session 直接做。
- **同一 session 內分檔唯讀審查** → Subagents（要明確要求才會 spawn）。
- **多個獨立、耗時的審查並行、不想盯電腦** → Codex Cloud。
- **接 CI、需精確控制輸入輸出** → 多個 `codex exec`。
- **多個 agent 同時寫程式碼** → 一定要自己建 worktree（Codex 沒有已驗證的內建隔離）。
- **PR 想全自動審** → GitHub `@codex review`。
- **需要自訂編排邏輯、agent 之間交接** → 才考慮 `codex mcp-server` ＋ Agents SDK（API 層級）。

### 5.2 Sandbox 與 approval 怎麼配 ✅

| 需求 | 建議 | 說明 |
|------|------|------|
| 一般本機開發 | `-s workspace-write -a on-request` | 可寫工作區，由模型決定何時請你批准 |
| 嚴格審查／唯讀分析 | `-s read-only -a untrusted` | 只能讀；只有 trusted commands 直接執行 |
| CI 非互動 | `codex exec -a never --json` | 永不詢問，失敗直接回傳；不會卡在提示 |
| 外部已隔離的自動化環境 | 視情況用 `--dangerously-bypass-approvals-and-sandbox` | 近乎完全存取，風險最高，**只在已有外部隔離（容器／microVM）時才考慮** |

- 審查類工作建議**預設 `read-only`**，只有明確要產生修復檔或分析檔時才用 `workspace-write`，且限定在隔離的 worktree。
- `on-failure` 已標示 deprecated，不要用在新腳本。✅

### 5.3 成本注意

- **token 用量會乘上 agent 數**：多 subagent、多個 cloud task、多個 `codex exec` 都是「開很多次」，費用遠高於單次；Subagents 官方也提醒 token 用量高於同樣工作的單 agent 流程。🔎 大任務先在單一子系統試跑，再擴大。
- **看「每個完成任務」的成本，不是每次請求**：一個便宜但要多跑幾輪才完成的做法，未必真的便宜。
- **用漏斗降成本**：先做不呼叫模型的去重與確定性分流，再用標準模型，最後才用深度分析；參考 `OpenAI-Python-Agent.md`「每案成本控制」的四層漏斗。✅
- **為每個獨立事件開新的 `codex exec`**，不要預設 `resume`：`resume` 會延續先前 session，不利於成本、資料隔離與 per-ticket token 預算。✅
- **`--attempts <N>`（best-of-N）會乘上次數**：預設 1，調高前先想清楚值不值得。✅

### 5.4 常見陷阱

- **Subagent 不會自己 spawn**：你不明講，Codex 就單 agent 做完；prompt 要寫「請 spawn N 個 subagent，分別審…」。🔎
- **權限隔離 ≠ 檔案隔離**：subagent 繼承 sandbox，但多個 agent 同時**寫**同一份程式碼仍會衝突；要寫就各自建 worktree（見第 2 節）。🔎
- **別調高 `max_depth`**：預設 1 已夠；調高會讓 fan-out、token 與延遲倍增。🔎
- **純審查不必開 worktree**：把 sandbox 設成 `read-only` 即可，開 worktree 只是多餘開銷。
- **`codex exec` 預設要求在 Git repository 中執行**：非 Git 目錄需 `--skip-git-repo-check`，且只應在安全的隔離目錄使用。✅ 平行跑多個程序時，也別讓它們共用同一個會被寫入的目錄。
- **`codex cloud` 是 experimental**：指令行為可能隨版本調整；套用 `apply` 前先 `diff`，並確認工作樹乾淨。✅
- **分檔派 agent 時 prompt 要講清楚範圍與準則**：否則每個分身審查口徑不一；用自訂 reviewer agent（固定準則）或把準則寫進 `AGENTS.md` 可統一。🔎
- **文件（Markdown）不是程式碼**：`/review` 預設審程式邏輯；審文件要在 prompt 明確要求「查事實正確性、連結有效性」。
- **設定檔欄位與版本不符**：開了 `--strict-config` 時，`config.toml` 的未知欄位會直接報錯；先跑 `codex doctor`、`codex --help`、`codex <subcommand> --help`，再比對版本與官方文件。✅ 這也適用於 `[agents]` 的上限設定：不同版本欄位可能有差異。
- **不可信輸入要隔離**：審查或分析來自外部的內容（例如 coredump、第三方 PR）時，用容器或 microVM、預設禁止網路、唯讀掛載來源；建立 issue、改程式、推送、重新部署等動作保留人工核准。✅（見 `OpenAI-Python-Agent.md`「安全邊界」）
- **啟用旗標與官方文件不一致時，以你本機版本為準**：subagents 的啟用方式各來源說法不一，先用 `/experimental` 看實際清單。⚠️
- **別為了省錢自行降級模型**：模型選擇是使用者的決定；要省成本，先調整 reasoning effort、善用漏斗，再考慮換模型。（可用 `/model` 切換模型與 reasoning effort ✅）

### 5.5 與 Claude Code 的主要差異（做多 agent 審查時）

| 面向 | Claude Code | Codex |
|------|------|------|
| 一鍵雲端多 reviewer ＋ 獨立驗證 | `/code-review ultra` | 無已驗證的對應指令 ⚠️ |
| 多背景 session 總覽 | Agent View（`claude agents`）| 無內建；用 `codex cloud list` 或自己的腳本 |
| subagent 檔案隔離 | `isolation: worktree` | 無已驗證的內建設定；自建 worktree ＋ `-C` |
| 腳本編排大量 agent | Workflows | 無內建；用 `codex exec` 腳本或 Agents SDK |
| 完成通知 | 主動回到 session | 未見已驗證機制 |
| 工作區無變更時自動清 worktree | 有 | 無已驗證的對應行為 |
| 設定中心 | `settings.json`、hooks | `config.toml`、profiles、sandbox／approval、MCP、plugin marketplace ✅ |

### 5.6 延伸閱讀

- 指令與旗標：`CodeX-CLI.md` —— 第七章（`codex exec`）、第八章（`codex review`）、第九章（session 管理）、第十五章（Codex Cloud）、第十六章（Sandbox 與 approval）、第十九章（Slash Commands）。
- 模型選擇與定價：`OpenAI-Model.md`。
- Agents SDK、coredump 分析架構、成本漏斗與安全邊界：`OpenAI-Python-Agent.md`。
- 實戰範例：本文附錄 A（fastpath memory／refcount 難題的 Codex 追蹤）。
- Claude Code 對應版：`Claude-Agent.md`。

---

## 附錄 A　實戰範例：用 Codex 追蹤 fastpath 的 memory / refcount 難題

> **範圍聲明**：本附錄是通用的 DPDK／fastpath 除錯方法論，搭配 Codex 的分工方式；與 `Claude-Agent.md` 附錄 A 是同一情境的 Codex 版。**未針對 6WIND 原始碼逐項驗證**；DPDK 的 debug 選項名稱隨版本而異，請以實際版本文件為準。範例指令與腳本**未在實際環境執行**（本環境未安裝 `codex`）。標記 ✅🔎⚠️ 意義見文首。

### A.1 問題特徵

- 難以重現：原因（例如 refcount 多減一次）與症狀（幾秒後別的封包踩到已釋放的記憶體）**距離很遠**。
- 常見成因：錯誤處理分支漏 `put`／多 `put`、跨 core 的 refcount 競態、mbuf／物件在 slow-path 與 fast-path 交界的所有權不清。
- 核心策略：**不要追事後的崩潰，要讓錯誤在發生當下就爆**，把「原因到症狀」的距離縮成零。

### A.2 先決條件：讓錯誤即時現形（人要先做，agent 才有東西可分析）

多 agent 不能取代這一步，agent 讀程式碼看不到「執行期的真相」。

| 手段 | 作用 |
|------|------|
| 釋放時 poison（填毒值）| use-after-free 立刻讀到毒值，不再悄悄沿用 |
| refcount API 統一包一層（debug build）| `refcnt` 為 0 仍被使用時立即 assert；保留最近 N 次 inc／dec 的 backtrace 與 core id（ring buffer）|
| canary／magic | double-free、越界寫入當場爆 |
| mempool census | 穩定流量下 free mbuf 數應回到基準線；漂移即 leak 或 double-free |
| 各類物件 alloc／free 計數 | 差值超標即告警 |

### A.3 Codex 的多 Agent 分工

目標：把「靜態可見的配對錯誤」平行掃完，把「需要執行期證據的問題」交給有資料的 agent，並用**獨立驗證**壓低誤報。

| 角色 | 用哪種機制（對應本文章節）| 做什麼 | 是否改檔 |
|------|------|------|------|
| **子系統稽核員 ×N** | Subagents（3.2）或多個 `codex exec`（3.4），每個認領一個子系統（mbuf／FIB／neighbour／route／ACL…）| 依同一份 checklist（A.4）掃「`get` 無對應 `put`」「錯誤路徑漏 `put`」「跨 core 共享物件的保護」| 否（`read-only`）|
| **耗時的獨立審查** | Codex Cloud（3.3）| 每個子系統提交一個 cloud task，提交後不用盯著電腦 | 否 |
| **instrumentation 實作** | 自建 worktree ＋ `codex exec -C <worktree> --sandbox workspace-write` | 實作 A.2 的 wrapper／poison／census，各自在獨立 worktree 改，避免互相覆蓋 | 是（隔離）|
| **重現 harness 建置** | 同上，另一個 worktree 或獨立 session | 寫 pcap replay、固定參數（單核、固定 hash seed）、fault／delay injection 腳本 | 是（隔離）|
| **log／core 分析** | `codex exec --sandbox read-only` | 讀 backtrace ring buffer、core 摘要、census 輸出，依簽章分群、找共同路徑 | 否 |
| **競爭假說調查** | 方案一：主 session 同時 spawn 數個 subagent，每個追一個假說；方案二：`codex fork` 從同一份 context 分叉出多條調查線 | 每條線追一個不同假說（漏釋放／跨 core 競態／所有權不清），各自提出證據與最小實驗 | 視情況 |
| **獨立驗證員** | 另開一個**全新的** `codex exec`（不要 `resume`）| 對每個 finding 獨立複核：能否構造出具體交錯／呼叫序列？是否與實際程式碼矛盾？ | 否 |

> **獨立驗證的關鍵**：驗證員要在**全新的 context** 裡，只看「主張」與程式碼，不看原稽核員的推理。所以用新的 `codex exec`（不 `resume` 先前的 session）最乾淨。這是仿照 Claude `/code-review ultra`「多 reviewer 平行找、再由獨立 agent 驗證」的做法，Codex 沒有一鍵版，需自己組。
>
> **與 Claude 附錄的差異**：Claude 用 Agent teams 讓 teammate 互相挑戰證據；Codex 沒有已驗證的對應功能 ⚠️，改用「多個假說各一條線＋最後由主 session 或另一個全新 `codex exec` 裁決」。

### A.4 refcount 稽核 checklist（給人或 agent 共用）

建議把它放進 repo 的 `AGENTS.md`（`/init` 可產生 scaffold ✅），讓所有 agent 都套用同一份準則；官方也說明常駐審查規則寫在 `AGENTS.md`。🔎

1. 每個取得 reference 的點（`get`／`inc`／查表後使用）是否有對應釋放？列出配對。
2. **每個 `goto err`／提前 `return` 路徑**是否釋放了此前取得的所有 reference？
3. 物件放進容器（list／hash／ring）時是由誰持有 reference？取出時誰釋放？
4. 跨 core 傳遞（ring、mbuf 轉送）後，原 core 是否還在使用該物件？
5. 釋放後是否仍有指標被保留（未清空）或被快取？
6. 同一物件是否可能被兩條路徑各釋放一次（例如 timeout 與正常完成並存）？
7. 計數器操作是否為原子？讀改寫之間是否有 race？

### A.5 追蹤帳本

Codex 沒有統一看板（見第 4 節），所以**帳本是必要的**。在 repo 內放一個共用檔（例如 `debug/ledger.md`），每個 finding 一列，由主 session 或你的腳本彙整：

| 欄位 | 說明 |
|------|------|
| ID | 唯一編號 |
| 位置 | 檔案:行、函式 |
| 主張 | 一句話：什麼情況下 refcount 會不平衡 |
| 證據 | 呼叫序列／具體交錯／log 片段；**沒有證據的標「推測」** |
| 信心 | 高／中／低 |
| 驗證狀態 | 未驗證／驗證員確認／已在 instrumented build 重現／已排除 |
| 負責 agent | 哪個程序／thread 發現、哪個驗證 |

用 `--output-schema` 讓各 `codex exec` 輸出同一個 JSON 結構，彙整時直接合併。把下面的範例 schema 存成 `debug/finding.schema.json`（A.8.2 的指令會引用這個路徑；欄位對應上表，嚴格度要求以官方為準 ⚠️）：

```json
{
  "type": "object",
  "properties": {
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "location": { "type": "string" },
          "claim": { "type": "string" },
          "evidence": { "type": "string" },
          "confidence": { "type": "string", "enum": ["high", "medium", "low"] },
          "is_speculation": { "type": "boolean" }
        },
        "required": ["id", "location", "claim", "evidence", "confidence", "is_speculation"],
        "additionalProperties": false
      }
    }
  },
  "required": ["findings"],
  "additionalProperties": false
}
```

若問題是從 coredump 起手，案件事實檔（`case_facts.json`）、第一輪模型可見的最小證據集與工具集，見 `OpenAI-Python-Agent.md`。✅

### A.6 能做與做不到的事（務實預期）

**多 agent 擅長：**
- 在大型 codebase 裡**平行**追呼叫路徑、找出配對錯誤與漏掉的錯誤分支。
- 讀 log／backtrace、歸納共同路徑、提出並排序假說。
- 撰寫 instrumentation、重現腳本、單元測試。

**做不到或要小心：**
- **時序 race 無法只靠讀程式碼確認**，必須有執行期證據（A.2）。agent 可以提出「可能的交錯」，但不能代替壓測驗證。
- 若 agent **跑不到你的真實環境**（專有 fastpath、特定硬體／NIC），它只能分析你提供的 log、core、程式碼；成效取決於你餵給它的資料與回饋迴圈。
- 平行 agent 容易**產生看似合理但不成立的推論**；因此每個 finding 都要附證據，並由獨立驗證員複核（A.3）。
- 平行會**乘上 token 用量**；先在單一子系統試跑，再擴大。
- Subagents 需明確要求才會 spawn、且同時最多 `max_threads` 個（預設 6）。🔎

### A.7 建議的實際流程

1. 人／agent（獨立 worktree）上 A.2 的 fail-fast instrumentation。
2. 同時平行：子系統稽核員跑 A.4 checklist（靜態）＋ 重現 harness 建置。
3. 將所有 finding 填入 A.5 帳本，由全新 `codex exec` 的獨立驗證員複核。
4. 取得穩定重現後，用 `git bisect` 鎖定引入的 commit。
5. 對高信心 finding 先寫會失敗的測試，再修，最後在 instrumented build 跑回歸。

### A.8 範例 prompt 與指令

> `<…>` 為佔位符，請替換成你的實際路徑、子系統與資料。共通原則：**限定範圍、指定輸出格式、要求證據、區分「已確認」與「推測」**。指令中的旗標均取自 `CodeX-CLI.md` ✅，但**整體腳本未實際執行**。

#### A.8.1 主 session：一次要求 spawn 多個唯讀 subagent 🔎

```text
請 spawn 4 個唯讀 subagent，各自稽核一個子系統的 refcount 配對：
1. <src/mbuf/>   2. <src/fib/>   3. <src/neighbour/>   4. <src/route/>

每個 subagent 都使用 AGENTS.md 裡的 refcount 稽核準則，只讀不改檔。
每個 subagent 完成後回報 findings，格式如下；你（主 session）負責彙整、去重，
並寫入 <debug/ledger.md>。

[回報格式]
每個 finding 一列：ID｜檔案:行｜一句話主張｜證據（呼叫序列或程式碼片段）｜信心（高/中/低）｜
是否為推測。沒有具體證據者一律標「推測」，不要省略但不要寫成確定。
```

#### A.8.2 子系統稽核員（單一 `codex exec`，唯讀、固定輸出格式）✅

```bash
mkdir -p out
codex exec --sandbox read-only -a never \
  --output-schema debug/finding.schema.json \
  --output-last-message out/fib.json \
  "你是 refcount 稽核員，只讀、不改檔。範圍：<src/fib/> 底下所有檔案。
   1) 先列出此子系統中所有『取得 reference』與『釋放』的 API（含 wrapper）。
   2) 逐一檢查每個取得點在所有出口是否有對應釋放，特別檢查每個 goto err、提前 return。
   3) 檢查物件放入容器／取出時 reference 持有者是否一致；跨 core 傳遞後原 core 是否仍使用。
   規則：只回報你能指出『具體呼叫序列』的問題；無法指出序列的標為推測並說明缺什麼證據；
   不回報風格問題；看不懂的巨集或 wrapper 先追到定義再下結論，不要猜。
   無發現時回報空的 findings，並在 evidence 說明已檢查的函式。"
```

平行跑多個子系統：

```bash
printf '%s\n' src/mbuf src/fib src/neighbour src/route |
  xargs -P 4 -I{} sh -c '
    n=$(echo {} | tr / _)
    codex exec --sandbox read-only -a never \
      --output-schema debug/finding.schema.json \
      -o "out/$n.json" \
      "你是 refcount 稽核員，只讀不改檔。範圍：{}。依 AGENTS.md 的 refcount 稽核準則審查，只回報有具體呼叫序列的問題。"'
```

#### A.8.3 獨立驗證員（全新 `codex exec`，只看單一主張）✅

```bash
codex exec --sandbox read-only -a never -o out/verify-F012.md \
  "你是獨立驗證員，只讀、不改檔，且你不知道原稽核員的推理，只看下列主張：
   [主張] <F-012：在 fib_entry_add() 的 err_nomem 分支，nexthop 的 reference 未釋放>
   [位置] <src/fib/fib_entry.c:218>
   請依序：
   1) 到該位置讀實際程式碼（含呼叫者與被呼叫者），確認主張描述的程式碼確實存在。
   2) 構造一條會觸發該路徑的具體呼叫序列，逐步追蹤 refcount 的變化。
   3) 檢查是否有其他機制補償（外層 cleanup、destructor、其他分支補釋放）。
   結論只能是三種之一：成立（附呼叫序列與逐步 refcount 數值）／不成立（指出哪一行或機制使其不成立）／
   無法判定（說明缺什麼資訊，例如需要執行期資料）。不要為了附和原主張而勉強成立。"
```

#### A.8.4 競爭假說調查員 🔎

**方案一（同一 session 內，需明確要求 spawn）：**

```text
我們有一個難重現的問題：<穩定流量下運行數小時後，free mbuf 數緩慢下降，偶發 crash>。
已知：<crash 的 backtrace 位於 …；census 顯示 …；僅在啟用 feature X 時出現>。

請 spawn 3 個 subagent，各自調查一個不同假說（皆只讀）：
- 假說 A：錯誤處理分支漏釋放（leak）
- 假說 B：跨 core 的 refcount 競態（double-free／use-after-free）
- 假說 C：slow-path 與 fast-path 交界的所有權不清

每個 subagent：
1) 說明該假說應該留下什麼可觀察的痕跡（log、census 曲線、backtrace 型態）。
2) 對照我們已有的資料，判斷是支持還是矛盾。
3) 提出能區分各假說的最小實驗（例如只開 feature X 並加上某個計數器）。
最後由你彙整：哪些假說被資料排除、哪些仍成立、建議的下一個實驗。
```

**方案二（`codex fork`）**：在已讀完相關資料的 session 上 `codex fork`，分叉成三條調查線，各自帶入一個假說的 prompt；之後把三條線的結論貼回主 session 或帳本，由一個全新的 `codex exec` 裁決。✅（`codex fork [SESSION_ID] [PROMPT]`）

#### A.8.5 log／core 分析員 ✅

```bash
codex exec --sandbox read-only -a never -o out/log-analysis.md \
  "請分析 <logs/crash-*/> 內的 backtrace ring buffer 與 core 摘要，只讀不改。
   1) 依 crash 簽章（最頂的 frame ＋ 觸發的物件類型）分群，統計每群次數。
   2) 對每一群，列出物件『最後 N 次 inc/dec』的 backtrace 與 core id，找出多減／漏減的那一次，以及是否跨 core。
   3) 找出各群共同的前置事件（特定 feature、封包類型、timer…）。
   4) 輸出：群組表（簽章｜次數｜疑似肇因路徑｜證據）＋ 建議下一步要加什麼 instrumentation。
   資料不足的地方明說，不要補猜。"
```

> 實務提醒：審查不可信輸入（coredump、第三方資料）時，在容器或 microVM 中執行、預設禁網路、唯讀掛載來源，並對建立 issue、改程式、推送等動作保留人工核准。✅（見 `OpenAI-Python-Agent.md`「安全邊界」）
