# Claude Code 多 Agent 工作與 Code Review 指南

> 本文聚焦「工作流程與選型」：何時用哪種平行工作方式、如何同時審查不同部分、如何追蹤與彙整。
> 指令與參數的完整清單請見 `Claude-Code-CLI.md`（第十四章 Multi-agent 使用方法）。
>
> 狀態：初版完成（五節皆已填）。更新日期：2026-11-02

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

> **一句話定調**：做 code review，重點看 **1.1 Subagents**（同一 session 分工審查）與 **1.2 Agent View**（多個獨立 session 並行追蹤）；另有內建的 **`/code-review ultra`**（雲端多 reviewer，見第 3 節）。**1.4 Workflows** 適合大規模掃描、**1.3 Agent teams** 用於需要協作的複雜任務；**1.5／1.6** 屬於 API 自建 agent，本文其餘章節不深入。

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

平行工作最怕「派出去就看不到了」。依方式不同，追蹤入口也不同。

### 4.1 追蹤入口一覽

| 想看什麼 | 用哪個 |
|------|------|
| session 內執行中的 subagent | `/agents`（Running 分頁） |
| 背景 session（含 Agent View 派發的）| `claude agents` 管理畫面 |
| 背景 task | `/tasks`（別名 `/bashes`） |
| workflow 進度 | `/workflows` 進度檢視器 |
| 完成 / 待回應 | **task 通知**會主動回到 session，不必一直盯 |

### 4.2 Agent View 的狀態與 peek

`claude agents` 是多背景 session 的統一管理台，每列一個 session：

| 狀態 | 意義 |
|------|------|
| Working（動畫 `✽`） | 正在執行工具或生成回應 |
| Needs input（黃） | 等你回應問題或授權 |
| Idle（暗） | 等待下一個指令 |
| Completed（綠 `✻`） | 成功完成 |
| Failed（紅） | 錯誤結束 |
| Stopped（灰） | 被手動停止 |
| `/loop` 睡眠中（`✢`） | 顯示執行次數與下次觸發倒數 |

- 選一列按 `Space` 開 **peek 面板**：看最新輸出、待決問題、已開 PR，可**直接輸入回覆**而不必 attach。
- **PR 狀態顏色**：黃＝等 CI／review 或 CI 失敗；綠＝通過且無阻擋；紫＝已合併；灰＝draft 或已關閉。
- 完整鍵盤快捷鍵、篩選語法（`a:<name>`、`s:<state>`、`#<number>`）見 `Claude-Code-CLI.md` 第十四章。

### 4.3 彙整結果

- **Subagents**：各 subagent 跑完**回報給主 session**，由主 Claude 收攏、去重、排序，形成一份整體結論——適合把「每檔一份 findings」併成一張清單。
- **Agent View**：各 session 結果留在各自的 session；你在管理畫面逐一 peek，或 attach 進去細看。
- **Workflows**：中間結果在腳本變數裡，最後**彙整成一份報告**（例如 `/deep-research` 會附引用、過濾未通過交叉驗證的聲明）。
- **`/code-review ultra`**：findings 以通知回到 session，每個含檔案位置與問題說明，可直接請 Claude 修。

### 4.4 Worktree 清理

當 agent 各自在 worktree 工作，收尾時：

| 狀況 | 行為 |
|------|------|
| 無未提交變更、無新 commit | 自動刪除 worktree 與 branch |
| 有變更或新 commit | 詢問是否保留 |
| 非互動模式（`-p`）| 不自動清理，需手動 `git worktree remove` |

Subagent 建立的 worktree 超過 `cleanupPeriodDays` 天、且無未提交變更或未推送 commit，會自動清除。細節見 `Claude-Code-CLI.md` 第十章（Worktree 使用方法）。

---

## 5. 實務建議與陷阱

### 5.1 一句話選型

- 任務**單一、可快速說清楚** → 不要用多 agent，一個 session 直接做。
- **分工審查 / 改同一個 repo 的不同檔案** → Subagents（必要時各開 worktree）。
- **多個彼此無關的任務並行、要總覽** → Agent View。
- **需要 agent 互相討論、交叉驗證** → Agent teams。
- **大規模、可機械拆解** → Workflows / `/batch`。
- **合併前重大變更深度審查** → `/code-review ultra`。

### 5.2 成本注意

- **token 用量會乘上 agent 數**：workflow、多 subagent、`/code-review ultra` 都是「開很多 agent」，費用遠高於單次對話；大任務先在小範圍試跑。
- **看「每個完成任務」的成本，不是每次請求**：一個便宜但要跑更多回合才完成的做法，未必真的便宜。
- **`/code-review ultra` 免費額度有限**：Pro / Max 各 3 次，用完約 $5–$20／次；**提前停止仍會耗掉一次免費額度**。
- **cache 不跨模型共用**：多模型級聯（例如用便宜模型當 worker）會放棄 cache 重用，有時反而更貴。

### 5.3 常見陷阱

- **純審查不必開 worktree**：worktree 是為了「改檔案不衝突」。唯讀審查不改檔，開 worktree 只是多餘開銷。
- **Agent teams 預設不隔離**：共用同一個工作目錄，要靠明確分工避免彼此覆蓋；需要隔離時改用 subagent 的 `isolation: worktree` 或 Agent View。
- **分檔派 subagent 時，prompt 要講清楚範圍與準則**：否則每個分身審查口徑不一；用自訂 reviewer subagent（固定 `tools` 與準則）可統一。
- **文件（Markdown）不是程式碼**：`/code-review` 預設審程式邏輯；審文件要在 prompt 明確要求「查事實正確性、連結有效性」等，否則容易文不對題。
- **`/code-review ultra` 的平台限制**：需 claude.ai 帳號登入，**不支援**只用 API key、Bedrock、Vertex AI、Foundry、Zero Data Retention 組織；repo 太大無法打包時改用 PR 模式（先推 branch 開 draft PR，再用 PR 號碼審）。
- **別為了省錢自行降級模型**：模型選擇是使用者的決定；需要省成本時，先調 `effort`、善用 cache，再考慮換模型。

### 5.4 延伸閱讀

- 指令與參數：`Claude-Code-CLI.md` —— 第十章（Worktree）、第十二章（`/code-review ultra`）、第十四章（Multi-agent）。
- 模型選擇與定價：`Claude-Model.md`。
- 實戰範例：本文附錄 A（fastpath memory / refcount 難題的多 Agent 追蹤）。

---

## 附錄 A　實戰範例：用多 Agent 追蹤 fastpath 的 memory / refcount 難題

> **範圍聲明**：本附錄是通用的 DPDK / fastpath 除錯方法論，搭配多 agent 的分工方式。**未針對 6WIND 原始碼或其內部機制逐項驗證**；DPDK 的 debug 選項名稱會隨版本改變，請以實際使用的版本文件為準。

### A.1 問題特徵

- 難以重現：原因（例如 refcount 多減一次）與症狀（幾秒後別的封包踩到已釋放的記憶體）**距離很遠**。
- 常見成因：錯誤處理分支漏 `put` / 多 `put`、跨 core 的 refcount 競態、mbuf / 物件在 slow-path 與 fast-path 交界的所有權不清。
- 核心策略：**不要追事後的崩潰，要讓錯誤在發生當下就爆**，把「原因到症狀」的距離縮成零。

### A.2 先決條件：讓錯誤即時現形（人要先做，agent 才有東西可分析）

多 agent 不能取代這一步，因為 agent 讀程式碼看不到「執行期的真相」。先上這些：

| 手段 | 作用 |
|------|------|
| 釋放時 poison（填毒值）| use-after-free 立刻讀到毒值，不再悄悄沿用 |
| refcount API 統一包一層（debug build）| `refcnt` 為 0 仍被使用時立即 assert；保留最近 N 次 inc/dec 的 backtrace 與 core id（ring buffer）|
| canary / magic | double-free、越界寫入當場爆 |
| mempool census | 穩定流量下 free mbuf 數應回到基準線；漂移即 leak 或 double-free，並可縮小到哪種流量 / 哪個 feature |
| 各類物件 alloc / free 計數 | 差值超標即告警，把「數小時後 OOM」變成「數秒內數字不對」|

### A.3 多 Agent 分工

目標：把「靜態可見的配對錯誤」平行掃完、把「需要執行期證據的問題」交給有資料的 agent，並用**獨立驗證**壓低誤報。

| 角色 | 方式（對應本文章節）| 做什麼 | 是否改檔 |
|------|------|------|------|
| **子系統稽核員 ×N** | Subagents（§3.2），每個認領一個子系統（mbuf / FIB / neighbour / route / ACL…）| 依同一份 checklist（A.4）掃「`get` 無對應 `put`」「錯誤路徑漏 `put`」「跨 core 共享物件的保護」| 否（唯讀）|
| **全樹模式掃描** | Workflows（§1.4）| 全樹找某一類 pattern，例如所有 free 呼叫點是否可能重複釋放；規模大、可機械拆解 | 否 |
| **instrumentation 實作** | Subagent + `isolation: worktree`（§1.1）| 實作 A.2 的 wrapper / poison / census，各自在 worktree 改，避免互相覆蓋 | 是（隔離）|
| **重現 harness 建置** | 獨立 session（Agent View，§1.2）| 寫 pcap replay、固定參數（單核、固定 hash seed）、fault / delay injection 腳本 | 是（隔離）|
| **log / core 分析** | Subagent | 讀 backtrace ring buffer、core dump、census 輸出，依簽章分群、找共同路徑 | 否 |
| **競爭假說調查** | Agent teams（§1.3）| 每個 teammate 追一個不同假說（例如 A：錯誤分支漏 put；B：跨 core race；C：slow-path 所有權），互相質疑證據 | 視情況 |
| **獨立驗證員** | Subagent | 對每個 finding 獨立複核：能否構造出具體交錯 / 呼叫序列？是否與實際程式碼矛盾？ | 否 |

> 概念上等同 `/code-review ultra` 的做法：多個 reviewer 平行找，再由獨立 agent 驗證，只留下站得住腳的。

### A.4 refcount 稽核 checklist（給人或 subagent 共用）

1. 每個取得 reference 的點（`get` / `inc` / 查表後使用）是否有對應釋放？列出配對。
2. **每個 `goto err` / 提前 `return` 路徑**是否釋放了此前取得的所有 reference？
3. 物件放進容器（list / hash / ring）時是由誰持有 reference？取出時誰釋放？
4. 跨 core 傳遞（ring、mbuf 轉送）後，原 core 是否還在使用該物件？
5. 釋放後是否仍有指標被保留（未清空）或被快取？
6. 同一物件是否可能被兩條路徑各釋放一次（例如 timeout 與正常完成並存）？
7. 計數器操作是否為原子？讀改寫之間是否有 race？

### A.5 追蹤帳本（讓平行工作不會「派出去就看不到」）

在 repo 內放一個共用帳本（例如 `debug/ledger.md`），每個 finding 一列，由主 session 或 lead 彙整，欄位建議：

| 欄位 | 說明 |
|------|------|
| ID | 唯一編號 |
| 位置 | 檔案:行、函式 |
| 主張 | 一句話：什麼情況下 refcount 會不平衡 |
| 證據 | 呼叫序列 / 具體交錯 / log 片段；**沒有證據的標「推測」** |
| 信心 | 高 / 中 / 低 |
| 驗證狀態 | 未驗證 / 驗證員確認 / 已在 instrumented build 重現 / 已排除 |
| 負責 agent | 哪個 agent 發現、哪個驗證 |

追蹤入口沿用本文第 4 節：`/agents`、`claude agents`、`/tasks`、通知。

### A.6 能做與做不到的事（務實預期）

**多 agent 擅長：**
- 在大型 codebase 裡**平行**追呼叫路徑、找出配對錯誤與漏掉的錯誤分支。
- 讀 log / backtrace、歸納共同路徑、提出並排序假說。
- 撰寫 instrumentation、重現腳本、單元測試。

**多 agent 做不到或要小心：**
- **時序 race 無法只靠讀程式碼確認**，必須有執行期證據（A.2）。agent 可以提出「可能的交錯」，但不能代替壓測驗證。
- 若 agent **跑不到你的真實環境**（專有 fastpath、特定硬體 / NIC），它只能分析你提供的 log、core、程式碼；成效取決於你餵給它的資料與回饋迴圈。
- 平行 agent 容易**產生看似合理但不成立的推論**；因此要求每個 finding 附證據，並由獨立驗證員複核（A.3）。
- 平行會**乘上 token 用量**；先在單一子系統試跑，再擴大。

> 關於「Claude 似乎已解決很多深度難解的 bug」：它在有明確線索與可驗證回饋時（可重現、有 log / core、能跑測試）通常很有幫助，但並非每個 bug 都能被解開，尤其是缺乏執行期證據的競態。比較可靠的使用方式是把它當成**平行的稽核與假說驗證工具**，而不是單靠它「猜」出根因。

### A.7 建議的實際流程

1. 人 / agent（worktree）上 A.2 的 fail-fast instrumentation。
2. 同時平行：子系統稽核員跑 A.4 checklist（靜態）＋ 重現 harness 建置。
3. 將所有 finding 填入 A.5 帳本，由獨立驗證員複核。
4. 取得穩定重現後，用 `git bisect` 鎖定引入的 commit。
5. 對高信心 finding 先寫會失敗的測試，再修，最後在 instrumented build 跑回歸。

### A.8 範例 prompt

> 下列 prompt 的 `<…>` 為佔位符，請替換成你的實際路徑、子系統與資料。共通原則：**限定範圍、指定輸出格式、要求證據、區分「已確認」與「推測」**。

#### A.8.1 主 session：一次並行派發子系統稽核員

```text
請平行派出 4 個唯讀 subagent，各自稽核一個子系統的 refcount 配對：
1. <src/mbuf/>   2. <src/fib/>   3. <src/neighbour/>   4. <src/route/>

每個 subagent 都使用相同的稽核準則（見下方 checklist），只讀不改檔，
不要開 worktree。每個 subagent 完成後回報 findings，格式見下。
你（主 session）負責彙整、去重，並寫入 <debug/ledger.md>。

[稽核準則]
<貼上 A.4 的七條 checklist>

[回報格式]
每個 finding 一列：ID｜檔案:行｜一句話主張｜證據（呼叫序列或程式碼片段）｜信心（高/中/低）｜
是否為推測。沒有具體證據者一律標「推測」，不要省略但不要寫成確定。
```

#### A.8.2 子系統稽核員（單一 subagent 的 prompt）

```text
你是 refcount 稽核員，只讀、不改檔。範圍：<src/fib/> 底下所有檔案。

任務：找出 reference 取得與釋放不配對的地方。
1. 先列出此子系統中所有「取得 reference」的 API 與「釋放」的 API（含 wrapper）。
2. 逐一檢查每個取得點：是否在所有出口都有對應釋放？特別檢查每個 goto err、
   提前 return、錯誤處理分支。
3. 檢查物件放入容器／取出時，reference 的持有者是否一致。
4. 檢查跨 core 傳遞後，原 core 是否仍使用該物件。

規則：
- 只回報你能指出「具體呼叫序列」的問題；無法指出序列的，標為「推測」並說明缺什麼證據。
- 不要回報風格問題或與 refcount 無關的缺陷。
- 看不懂的巨集或 wrapper，先追到定義再下結論，不要猜。
- 輸出格式：ID｜檔案:行｜主張｜證據｜信心｜推測與否。無發現時回報「未發現」並列出已檢查的函式。
```

#### A.8.3 獨立驗證員（對單一 finding 複核）

```text
你是獨立驗證員，只讀、不改檔，且你不知道原稽核員的推理過程，只看下列主張：

[主張] <F-012：在 fib_entry_add() 的 err_nomem 分支，nexthop 的 reference 未釋放>
[位置] <src/fib/fib_entry.c:218>

請依序做：
1. 到該位置讀實際程式碼（含呼叫者與被呼叫者），確認主張描述的程式碼確實存在。
2. 構造一條會觸發該路徑的具體呼叫序列，逐步追蹤 refcount 的變化。
3. 檢查是否有其他機制補償（例如外層 cleanup、destructor、其他分支的補釋放）。

結論只能是三種之一：
- 成立：附上呼叫序列與逐步 refcount 數值。
- 不成立：指出哪一行／哪個機制使其不成立。
- 無法判定：說明缺少什麼資訊（例如需要執行期資料）。
不要為了附和原主張而勉強成立。
```

#### A.8.4 競爭假說調查員（Agent teams）

```text
我們有一個難重現的問題：<穩定流量下運行數小時後，free mbuf 數緩慢下降，偶發 crash>。
已知：<crash 的 backtrace 位於 …；census 顯示 …；僅在啟用 <feature X> 時出現>。

請建立 3 位 teammate，各自調查一個不同假說，並互相挑戰證據：
- 假說 A：錯誤處理分支漏釋放（leak）
- 假說 B：跨 core 的 refcount 競態（double-free / use-after-free）
- 假說 C：slow-path 與 fast-path 交界的所有權不清

每位 teammate：
1. 說明該假說應該留下什麼可觀察的痕跡（log、census 曲線、backtrace 型態）。
2. 對照我們已有的資料，判斷是支持還是矛盾。
3. 提出能區分各假說的最小實驗（例如只開 feature X 並加上某個計數器）。

lead 最後彙整：哪些假說被資料排除、哪些仍成立、建議的下一個實驗。
共用 task list 追蹤，不要改檔。
```

#### A.8.5 log / core 分析員

```text
請分析 <logs/crash-*/> 內的 backtrace ring buffer 與 core 摘要，只讀不改。

1. 依 crash 簽章（最頂的 frame ＋ 觸發的物件類型）分群，統計每群次數。
2. 對每一群，列出物件「最後 N 次 inc/dec」的 backtrace 與 core id，
   找出多減／漏減的那一次，以及是否跨 core。
3. 找出各群共同的前置事件（例如特定 feature、特定封包類型、特定 timer）。
4. 輸出：群組表（簽章｜次數｜疑似肇因路徑｜證據）＋ 建議下一步要加什麼 instrumentation。
資料不足的地方明說，不要補猜。
```
