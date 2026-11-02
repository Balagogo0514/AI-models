# Claude Code 多 Agent 工作與 Code Review 指南

> 本文聚焦「工作流程與選型」：何時用哪種平行工作方式、如何同時審查不同部分、如何追蹤與彙整。
> 指令與參數的完整清單請見 `Claude-Code-CLI.md`（第十四章 Multi-agent 使用方法）。
>
> 狀態：骨架草稿，逐節討論中。更新日期：2026-11-02

---

## 1. 概念與定位

「多 agent」在 Claude Code 裡其實有好幾種不同機制，差別在於**誰決定下一步**、**跑在哪裡**、以及**檔案與 context 是否隔離**。以下先逐一介紹，第 2 節再用一張表整體對照。

前四種是 Claude Code 內建、直接可用的平行工作方式；後兩種（Managed Agents、Agent SDK）屬於「用 API 自己蓋 agent」的層級，一般的互動式 code review 用不到，只在你要做產品整合時才需要。

### 1.1 Subagents（session 內委派）

- **是什麼**：在主對話中，Claude 把一個側邊任務（搜尋、分析、審查某個檔案）委派給一個獨立的 subagent 執行。
- **誰控制流程**：主 session 的 Claude，逐 turn 決定要不要派、派給誰。
- **跑在哪裡**：同一個 session 程序內（本機或雲端 session），不是另開一台機器。
- **隔離性**：各 subagent 有**獨立的 context window**，搜尋結果、log 等雜訊不會污染主對話；可選 `isolation: worktree` 讓它在獨立 git worktree 改檔案，避免互相覆蓋。
- **怎麼啟動**：內建的有 `Explore`（唯讀快速搜尋）、`Plan`、`general-purpose` 等；自訂的放 `.claude/agents/*.md`；臨時定義用 `--agents` 旗標。也可在對話裡直接說「用 security-reviewer 審這段」。
- **結果去哪**：回報給主 session，由主 Claude 彙整。
- **追蹤**：`/agents` 看執行中的 subagent。
- **適合**：把一次 code review 拆成「每個 subagent 審一個檔案／模組」，同時跑、再彙整。← 你問的情境主力。

### 1.2 Agent View（背景 session 管理台）

- **是什麼**：`claude agents` 開啟一個管理畫面，同時派發多個**各自獨立的完整 session** 在背景跑。
- **誰控制流程**：你手動派發；每個 session 內部由它自己的 Claude 控制。
- **跑在哪裡**：背景 session（本機），電腦不用一直盯著終端機。
- **隔離性**：每個派發的 session 可自動取得一個 worktree，彼此檔案不干擾。
- **怎麼啟動**：`claude agents` 進畫面後，在輸入框打任務、按 Enter 就建一個新 session。
- **追蹤**：這正是它的強項 —— 統一畫面顯示每個 session 的狀態（Working / Needs input / Completed / Failed…）、PR 狀態顏色，可 peek 看輸出、直接回覆。
- **適合**：多個**彼此無關**的任務同時進行，例如「A 審前端、B 審後端、C 修 flaky test」。

### 1.3 Agent teams（協作團隊）

- **是什麼**：一個 lead agent 帶領多個 teammate，彼此**共用一份 task list、可互傳訊息**協作。
- **誰控制流程**：lead agent 指派與協調。
- **跑在哪裡**：本機 session。
- **隔離性**：預設**不隔離**檔案，需要靠分工避免衝突。
- **怎麼啟動**：由 lead agent 建立 team 並指派 teammates。
- **追蹤**：共享的 task list。
- **適合**：需要 agent 之間互相討論、交叉驗證的**複雜協作**任務；單純平行審檔案反而用不到這種協調。

### 1.4 Workflows（腳本編排大量 agent）

- **是什麼**：一段 Claude 撰寫的 JavaScript 腳本，在背景由 runtime 執行，協調**數十到數百個** subagent 分階段平行工作。
- **誰控制流程**：腳本（而非逐 turn 的 Claude）。中間結果存在腳本變數裡。
- **跑在哪裡**：背景（雲端 workflow runtime）。
- **規模**：最多同時 16 個並行 agent，單次最多 1,000 個。
- **怎麼啟動**：內建的 `/deep-research`；或在 prompt 裡帶 "workflow" 關鍵字；或 `/effort ultracode`。
- **追蹤**：`/workflows` 進度檢視器（可暫停、恢復、停單一 agent、儲存腳本）。
- **適合**：大規模、可明確拆解的平行工作（跨多來源研究、逐檔稽核）。code review 中若要「掃過上百個檔案找某類問題」可用。

### 1.5 Managed Agents（雲端託管，API 層級）

- **是什麼**：透過 REST API 建立**持久化、有版本**的 agent 設定，再開 session 執行；Anthropic 代跑 agent 迴圈並託管一個沙箱工作區（bash、檔案、程式執行都在那裡）。
- **跟 code review 的關係**：這是**產品整合**用的（例如把 agent 排程、接 webhook、長時間執行），不是在 Claude Code 裡做互動式 review 的工具。
- **跑在哪裡**：Anthropic 雲端基礎設施。
- **劃清界線**：如果你要的是「在這個 session 裡審這次改動」，用 1.1–1.4，不需要 Managed Agents。

### 1.6 Claude Agent SDK（函式庫，API 層級）

- **是什麼**：把 Claude Code 的核心（agent 迴圈、內建工具、context 管理、hooks、subagents）包成函式庫，讓你在**自己的程式／基礎設施**裡跑一個 coding/檔案 agent。
- **跟 code review 的關係**：同樣是拿來**自建應用**的，不是互動式 review 的入口。
- **與 Tool Runner 的區別**：Agent SDK 是「整套 Claude Code 當函式庫」；Tool Runner 只是 API SDK 裡幫你跑工具迴圈的小助手，兩者不同套件。

> **一句話定調**：做 code review，重點看 **1.1 Subagents**（同一 session 分工審查）、**1.2 Agent View**（多個獨立 session 並行追蹤）、**1.4 Workflows**（`/code-review ultra` 背後就是雲端多 agent）。1.3 用於需要協作的複雜任務；1.5／1.6 屬於 API 自建 agent，本文其餘章節不深入。

---

## 2. 四種平行工作方式的選型

> **釐清框：Workflow 與 Worktree 不是同一件事（常見混淆）**
>
> 兩者層次完全不同，而且**正交、常一起用**：
>
> | | Workflow（工作流） | Worktree（工作樹） |
> |---|---|---|
> | 本質 | Claude 寫的**編排腳本**，協調多個 agent 分階段平行跑 | **git 功能**：獨立的工作目錄 + branch，共用同一份 repo 歷史 |
> | 解決什麼 | 誰做什麼、什麼順序、結果怎麼彙整（**協調**） | 平行工作各改各的、不互相覆蓋（**檔案隔離**） |
> | 層次 | 工作協調層 | 檔案系統 / 版本控制層 |
> | 誰在用 | `/deep-research`、`/batch`、ultracode effort | `claude --worktree`、subagent 的 `isolation: worktree`、`/batch` 每個單元 |
> | 產物 | 彙整後的結果（報告、多個 PR） | 一個 `.claude/worktrees/<name>/` 目錄與一條 branch |
>
> 比喻：**Workflow = 工頭**（分派任務、收攏結果）；**Worktree = 每個工人的工作檯**（東西不混在一起）。一個 workflow 編排的多個 agent，可以各自在一個 worktree 裡改檔案——workflow 負責協調，worktree 負責隔離。

下表把第 1 節的四種內建方式，依八個角度整體對照（Managed Agents / Agent SDK 屬 API 自建層級，不列入）：

| 方式 | 誰決定下一步 | 中間結果放哪 | 檔案隔離 | 可否重播 | 規模 | 如何追蹤 | 適合情境 |
|------|------|------|------|------|------|------|------|
| **Subagents** | 主 session 的 Claude（逐 turn 委派） | 各自的 context window，再回報主 session | 可選（`isolation: worktree`），預設不隔離 | worker 定義可重用；單次委派不留存 | 少數任務 | `/agents` | 側邊搜尋／分析；**分檔／分模組審查** |
| **Agent View** | 你手動派發；各 session 內部各自的 Claude | 各 session 自己的 context | 每個派發的 session 各一個 worktree | 任務各自獨立，可重新派 | 多個獨立任務 | `claude agents` 管理畫面（狀態圖示、peek、PR 顏色） | 多個**彼此無關**的任務並行 |
| **Agent teams** | lead agent 指派 | 共享 task list | 預設不隔離（需手動分工） | team 定義可重用 | 少數長跑 peer | 共享 task list + 互傳訊息 | 需**協作／交叉驗證**的複雜任務 |
| **Workflows** | 編排腳本（非逐 turn） | 腳本變數 | 各 agent 可選 worktree | 腳本本身可存成指令重用 | 數十到數百 agent（同時最多 16、單次最多 1,000） | `/workflows` 進度檢視器 | 大規模、可明確拆解的平行工作 |

> 速記：**要分工審查 → Subagents**；**要並行多個無關任務 → Agent View**；**要協作討論 → Agent teams**；**要大規模掃描 → Workflows**。四者都可搭配 worktree 做檔案隔離（見上方釐清框）。

---

## 3. Code Review 的多 Agent 做法

「多個 agent 同時審查不同部分、而且能追蹤」有三條路：內建的雲端深度審查、手動分檔派 subagent、以及搭配 Agent View 做並行追蹤。先給結論，再逐一說明。

> **速選**：合併前對重大變更深度把關 → **3.1 `/code-review ultra`**；想自己控制「誰審哪個檔案」並行跑 → **3.2 手動派 subagent**；多個獨立審查任務要用統一畫面盯著 → **3.3 Agent View**。

### 3.1 `/code-review ultra`（雲端多 reviewer，內建首選）

- **做什麼**：在 Claude Code on the web 的雲端沙箱裡，啟動**一批 reviewer agent 平行審查**你的 branch 或 PR，每個回報的問題都經**獨立 agent 驗證**，只回報真實存在的（降低誤報）。
- **怎麼啟動**：
  ```text
  /code-review ultra           # 審目前 branch vs 預設 branch（含未提交變更）
  /code-review ultra 1234      # 審 PR #1234
  ```
  非互動（CI / script）：`claude ultrareview 1234 --json`。
- **追蹤**：findings 以**通知**回到 session；用 `/tasks` 看進度或停止。
- **成本 / 條件**：需 claude.ai 帳號；約 5–10 分鐘；Pro / Max 各有 3 次免費，用完以 usage credits 計費（約 $5–$20／次）。
- **適合**：合併前對**重大變更**的深度把關。這是「多 agent code review」最省事、最對味的選擇——你不用自己分工。

### 3.2 手動派多個 subagent 分檔／分模組審查

當你想**明確控制「誰審哪個檔案」**、repo 太大不好一次打包、或想在本機 session 內並行跑時，用這條路。

- **做什麼**：一次派出多個背景 subagent，每個負責一個檔案或模組，各自跑完回報，再由主 Claude 彙整。
- **怎麼啟動**：
  - 在 session 內直接要求：「平行派三個 subagent，分別審 `a.ts`、`b.ts`、`c.ts`，各自回報問題」。主 Claude 會在**同一回合並行啟動**，而不是排隊。
  - 或寫一個自訂 reviewer subagent（`.claude/agents/security-reviewer.md`，`tools: Read, Grep, Glob`），讓每個分身都用同一套審查準則。
- **隔離**：純審查是**唯讀**，通常**不需要** worktree；只有當你要 agent 同時「審完順手改／修」時，才讓每個 agent 各開一個 `isolation: worktree` 避免改檔衝突。
- **追蹤**：`/agents` 看執行中的 subagent；背景任務完成會通知；也可用 `/tasks`。
- **適合**：分工清楚、各檔案相對獨立的審查；或想把審查結果**留在主 session** 一起討論。

### 3.3 搭配 Agent View 做並行追蹤

如果同時有**多個彼此無關**的審查／修復任務（例如「A 審前端、B 審後端、C 查 CI 失敗」），用 `claude agents` 把它們派成各自獨立的背景 session。

- **做什麼**：每個任務一個完整 session，各自可取得 worktree。
- **追蹤**：統一管理畫面顯示每個 session 的狀態（Working / Needs input / Completed / Failed）、PR 狀態顏色；按 `Space` peek 看輸出、直接回覆。
- **適合**：任務多且互不相關，需要一個**總覽畫面**盯進度。

### 3.4 對照：本機單次 vs 雲端多 agent

| 面向 | `/code-review`（本機單次） | `/code-review ultra`（雲端多 agent） |
|------|------|------|
| 執行位置 | 本機 session | 雲端沙箱 |
| 深度 | 單次審查 | 多 agent 平行 + 獨立驗證 |
| 時間 | 數秒到幾分鐘 | 約 5–10 分鐘 |
| 費用 | 計入一般用量 | 免費 3 次，之後約 $5–$20／次 |
| 適合時機 | 開發途中快速回饋 | 合併前對重大變更深度把關 |

> 補充：`/code-review` 可帶 level（`low`…`max`）與 `--fix`（自動套用）、`--comment`（貼成 PR inline 留言）；`/simplify` 只找 cleanup、不找 bug；`/security-review` 專做安全漏洞分析。

> ⚠️ **文件 vs 程式碼**：`/code-review` 與 subagent 預設審的是**程式碼 diff**。若審查對象是 Markdown／文件，審查會偏向**內容與事實查核**，而非程式邏輯；此時手動派 subagent 分檔、在 prompt 裡講清楚「查事實正確性」會比 `/code-review` 更貼切。

---

## 4. 如何追蹤與彙整

> TODO：狀態圖示、peek 面板、task 通知、`/tasks` 與 Agent View、worktree 清理。

---

## 5. 實務建議與陷阱

> TODO：何時用哪種、token 成本、文件 vs 程式碼審查的差異、常見誤用。
