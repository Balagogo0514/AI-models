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
> 標記：✅ 本地文件、🔎 官方間接、⚠️ 未驗證（見文首說明）。表格中以標記放在方式名稱後者，表示該列整體的主要來源；單格若與其不同，會另外註記。

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

> TODO：`codex cloud list/status/diff/apply`、`resume` / `fork`、`/agent`、`/goal`、worktree 清理。

---

## 5. 實務建議與陷阱

> TODO：sandbox 與 approval 組合、成本、Git repo 限制、何時用哪種。

---

## 附錄 A　實戰範例：用 Codex 追蹤 fastpath 的 memory / refcount 難題

> TODO：與 `Claude-Agent.md` 附錄 A 同一情境，改用 Codex 分工與範例 prompt；可銜接 `openAI-python-agent.md` 的 coredump 分析架構。
