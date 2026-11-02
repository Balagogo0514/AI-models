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

> TODO：比較表 —— 誰決定下一步、中間結果放哪、檔案隔離方式、可否重播、規模、如何追蹤。

---

## 3. Code Review 的多 Agent 做法

> TODO：
> - `/code-review ultra`（雲端多 reviewer + 每個 finding 獨立驗證）
> - 手動派多個 subagent 分檔／分模組審查
> - 各自的追蹤方式與適用時機

---

## 4. 如何追蹤與彙整

> TODO：狀態圖示、peek 面板、task 通知、`/tasks` 與 Agent View、worktree 清理。

---

## 5. 實務建議與陷阱

> TODO：何時用哪種、token 成本、文件 vs 程式碼審查的差異、常見誤用。
