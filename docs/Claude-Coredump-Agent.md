# Claude 開發 coredump 自動分析：工具選型（Claude Code、n8n、LangChain、Claude SDK）

> 資料日期：2026-11-20  
> 範圍：開發「coredump auto parser」時，Claude Code、n8n、LangChain、Claude SDK 與其他工具各適合擔任什麼角色；建議的架構、單案處理流程、成本考量、Jira 事件整合、安全邊界與導入順序。**這是選型與設計筆記，不是實作。**  
> 讀法：**【官方】** 取自本庫已整理的 Claude 官方資料（[Claude-Code-CLI](Claude-Code-CLI.md)、[Claude-Agent](Claude-Agent.md)）；**【本庫設計】** 取自本庫的 [OpenAI-Python-Agent](OpenAI-Python-Agent.md)——那份是同一類系統的設計，寫給 OpenAI，原則與模型廠商無關；**【建議】** 是我的歸納；**【推論】** 是我從已知資料類推，沒有直接依據。  
> ⚠️ **我沒有實作過這個系統**；**這次也沒有開啟任何 Anthropic、n8n、LangChain 的官方頁面**，n8n 與 LangChain 的功能我完全沒查證，相關內容都是【推論】。

## 先看結論

- **建議的組合**（【建議】）：**你們的 Python orchestrator ＋ Claude Messages API ＋ 受控的 debugger／symbol／source 工具**，當正式系統的核心。
- **Claude Code**：拿來**開發**（寫 parser、gdb 腳本、測試）和**人工調查罕見 crash**；CI 裡少量一次性分析可用 `claude -p`。它不是案件佇列、案件資料庫或成本帳務。
- **n8n**：負責**觸發、通知、人工核准、回寫 Jira／Issue**；不要把分析迴圈放進 n8n 節點。
- **LangChain／LangGraph**：**不當起點**。團隊已經熟悉才考慮拿 LangGraph 取代自寫狀態機。
- **Claude Agent SDK**：適合分析完成後的**子流程**（Issue 分流、相似事件查詢）或實驗，不取代控制層。
- **理由只有一個**：coredump 分析需要**每案硬性的成本與工具上限、去重、受控工具、佇列、重試、稽核**，這些要由你們的系統擁有，不要交給框架或互動工具（【本庫設計】）。
- **接 Jira**：**不一定要 n8n**；一個 Python 常駐服務可以直接收 Jira 事件（接收端、jobs 表、隔離 worker）。**只用 Claude Code** 只適合小量原型；折衷是薄服務加 `claude -p` 當 worker（第 9 節）。
- **成本**：模型 token 以本庫價格可估；單次呼叫（輸入 20K、輸出 2K）在 Sonnet 5.5 約 $0.06、Opus 5.5 約 $0.12。**月成本主要取決於「多少案件在不呼叫模型的層解決」與「升級到深度分析的比例」，不是工具選哪個**；基礎設施、人力、平台費用我沒有數據（第 6 節）。
- **先確認一件事**：dump 能不能離開公司。它會影響整個選型（第 11 節）。

**請你確認這五點，結論可能改變**：① 每天大約多少個 core？② 是否已有程式能穩定產出 full backtrace、registers、threads？③ dump 或其中的證據能否送到外部 API？④ 是否已有 job queue 或 n8n？⑤ 每月能接受的模型預算大約多少？

---

## 1. 要解決的問題與整體流程

【本庫設計】這類系統通常有下列要求，也是選型的依據：

- 每個 coredump 必須有成本上限；
- 要 fingerprint 去重與跨案件快取；
- debugger 與 symbol 操作要受 allowlist、timeout 與 sandbox 控制；
- 有「標準分析」與「深度分析」的升級規則；
- 要能接 CI／webhook、job queue、重試、人工核准與可稽核的 artifact。

![圖：coredump 自動分析的整體流程，六個步驟與各自的負責者：n8n 或 CI、你們的 Python 程式、模型與工具、人](figures/claude-coredump-arch.svg)

這張圖也說明了分工：**n8n 與人在頭尾，你們的 Python 在中間掌控，模型與工具只負責「判讀證據」**。【本庫設計】「模型不是 debugger」：`gdb`、`lldb`、symbolication 與 source lookup 是證據來源，模型只能根據工具結果推論。

---

## 2. 各工具的定位

![圖：七種工具的建議角色：Messages API 為正式核心；Claude Code、claude -p、Agent SDK、n8n 為輔助；LangChain 與 Managed Agents 先不選](figures/claude-coredump-roles.svg)

| 工具 | 建議角色 | 優點 | 不適合當核心的原因 | 依據 |
|---|---|---|---|---|
| **Claude Messages API SDK** | **正式核心** | 控制力最高：可自己計帳、硬性限制每案 token、工具呼叫與時間；容易接 queue、資料庫、artifact 與安全政策 | 工程量最高：狀態機、重試、觀測要自己寫 | 【本庫設計】對 `openai` SDK 的判斷，類推到 Claude（【推論】） |
| **Claude Code（互動）** | 開發與人工調查 | 在專案目錄讀檔、改檔、跑指令，上手快；適合寫 parser、debugger 腳本、測試 | 不是事件佇列、案件資料庫或成本帳務 | 【官方】功能；「不是帳務」是類推（【推論】） |
| **`claude -p`（CI）** | 少量、一次性分析 | 有 `--allowedTools`、`--max-turns`、`--max-budget-usd`、`--output-format json`、`--json-schema` | 回合與費用上限**只在單次執行內生效**，不累積；跨案件要自己加總 | 【官方】 |
| **Claude Agent SDK** | 子流程與實驗 | 把 Claude Code 的核心（agent 迴圈、內建工具、context 管理、hooks、subagents）做成函式庫；Python 套件 `claude-agent-sdk`（3.10+） | 迴圈由 SDK 管；內建工具集含 `Bash`、`Write`、`Edit`，和「不給任意 shell」的原則要小心對齊 | 【官方】；風險是【推論】 |
| **n8n** | 觸發、通知、核准 | 串接 webhook、Jira、通知很方便 | 不是分析迴圈的好位置 | 【推論】；本庫 CodeX-CLI 也把 webhook、重試、併發、timeout、預算與回寫 Jira 交給 n8n、CI 或 queue worker |
| **LangChain／LangGraph** | 不當起點 | 團隊若已熟悉，可用它的狀態機概念 | 多一層抽象與版本風險，而預算與工具層你們本來就要自己寫 | 【推論】；Anthropic 的 *Building effective agents* 建議先用簡單模式，不要一開始就上重型框架（本庫已列此文，我這次沒重新開啟） |
| **Managed Agents** | 先不選 | Anthropic 代跑 agent 迴圈並託管沙箱工作區，適合排程、webhook、長時間執行 | 跑在 Anthropic 雲端；dump 或證據要放進它的工作區，**資料外送要先評估** | 【官方】定位；外送問題是【推論】 |
| **OpenAI／Codex 路線** | 備選 | 若公司已有 OpenAI 合約可沿用 | — | 設計見 [OpenAI-Python-Agent](OpenAI-Python-Agent.md) |

補充：
- **Tool Runner** 是 API SDK 裡幫你跑工具迴圈的小助手，**不是** Agent SDK（【官方】，見 [Claude-Agent 1.6](Claude-Agent.md)）。若用它代跑迴圈，要確認能在每一輪**之前**檢查預算；我沒查證，要精確控制就自己寫迴圈（【建議】）。
- 三種框架可以在同一組織並存，但**不要讓兩個框架同時當同一個案件的主迴圈**，否則容易工具重複執行、成本帳務不一致、狀態分叉（【本庫設計】）。

---

## 3. 怎麼選

![圖：選型決策圖，依五個問題決定用 Messages API、Claude Code、claude -p、Agent SDK 或 n8n](figures/claude-coredump-choose.svg)

---

## 4. 為什麼核心是 Messages API，而不是 Claude Code 或 Agent SDK

| 需求 | Messages API ＋ orchestrator | `claude -p` | Agent SDK |
|---|---|---|---|
| 每案硬性預算 | 自己計帳，可跨案件累積 | `--max-turns`、`--max-budget-usd` **只在單次執行內生效**；長期用量要用 `--output-format json` 自行加總 `total_cost_usd`，或在 Console 設 workspace 層級 spend limit（【官方】） | 迴圈由 SDK 管；能否逐步強制預算我沒查證 |
| 去重、快取、佇列、稽核 | 自己做，本來就要做 | 要用外部腳本包起來 | 同左 |
| 工具範圍 | 只定義你要的幾個唯讀工具 | 用 `--allowedTools`、`--permission-mode` 預先限制；非互動沒人能回應權限提示，不先講清楚會卡住（【官方】） | 內建工具集含 `Bash`、`Write`、`Edit`（【官方】）；怎麼限制我沒查證 |
| 不可信輸入 | 你決定給模型什麼 | 非互動會**跳過 workspace trust 對話框**，只該在信任的目錄執行（【官方】）；**coredump 是不可信輸入**，別在放 dump 的目錄直接跑（【推論】） | 同左 |
| 初期工程量 | **最高** | 低 | 中 |

**取捨**：Messages API 初期最費工，但原因是它**不隱藏必要的系統工程**；對需要可預測成本與安全邊界的 coredump 服務，這些控制本來就該由系統擁有（【本庫設計】）。

若你們**已有**程式能穩定產出 full backtrace、`info registers`、`info threads`，就**不需要讓模型直接操作 `gdb`**：由 deterministic 程式取得證據，模型只解讀已取得的 artifact，更安全、成本更低、更容易重現（【本庫設計】，見 [OpenAI-Python-Agent](OpenAI-Python-Agent.md) 的「精簡架構」）。

---

## 5. 單案處理：成本漏斗與迴圈

### 5.1 成本漏斗

![圖：四層成本漏斗，fingerprint 去重與固定工具初篩不呼叫模型，標準模型分析一次短分析，深度分析需核准；下方是由程式強制的硬性預算](figures/claude-coredump-funnel.svg)

【本庫設計】目標不是讓每案都進入高成本深度推理，而是讓**多數已知案件在第 0 到 2 層結束**。
- **第 0 層**：以 `signal ＋ app build-id ＋ module build-id ＋ normalized top frames` 產生 signature；命中既有分析就直接回傳。
- **第 2 層**只傳案件摘要、verified facts、前 3–10 個關鍵 frames、必要 source 摘錄與問題清單。
- **第 3 層**只有 P0／P1、新 fingerprint、symbols 完整仍無法判斷、疑似安全或資料損壞才升級，要人工核准或 on-call policy。
- **預算耗盡不得無限重試**，要回傳 `needs_human_or_deep_analysis`，並列出已驗證事實與缺少的證據。

【建議】第 2 層與第 3 層可用不同等級的 Claude 模型；各模型的價格與能力見 [Claude-Model](Claude-Model.md)（資料快取時間 2026-10-06，使用前請重新確認）。

### 5.2 迴圈

![圖：單案處理迴圈的時序圖：orchestrator 讀案件、送證據給 Claude、檢查預算與 allowlist、在 sandbox 執行工具、用 schema 驗證報告](figures/claude-coredump-loop.svg)

這是依本庫設計整理的流程，下面是示意用的偽程式碼（【建議】，**沒有執行過**，函式名稱是假設）：

```python
budget = CaseBudget(            # 初始範例，依真實資料調整（【本庫設計】）
    max_model_calls=2, max_tool_calls=8,
    max_input_tokens=20_000, max_output_tokens=2_000,
    max_debugger_seconds=90,
)
messages = [user_message(load_case_facts(case_id))]   # 裁切後的證據，不是整份 dump

while True:
    if budget.exhausted():
        return needs_human_or_deep_analysis(case_id)   # 不無限重試
    reply = call_claude(messages, tools=TOOLS)          # 預算由這裡的外部程式強制
    budget.charge_model(reply.usage)
    if reply.wants_tool():
        check_allowlist(reply.tool_call)
        budget.charge_tool()
        result = run_tool_in_sandbox(reply.tool_call)   # 回傳 JSON ＋ evidence_id
        messages += [reply, tool_result(result)]
        continue
    return validate_report_schema(reply.text)           # 驗證失敗就不收
```

### 5.3 工具集與報告

【本庫設計】先做**一個 agent 搭配六個工具**，不要一開始就建多代理架構：

| 工具 | 輸入 | 輸出與目的 |
|---|---|---|
| `inspect_core` | artifact path | OS、架構、PID、signal、binary 與 module build-id |
| `resolve_symbols` | build-id 列表 | symbol 是否完整、symbol-set version、缺少項目 |
| `extract_backtrace` | case ID | 各 thread 的標準化 stack frames |
| `inspect_frame` | thread ID、frame index | 受限的區域變數、registers、source location |
| `search_repository` | query、revision | source 摘錄、Git blame、關聯 issue 或變更 |
| `save_analysis` | case ID、report schema | 保存可稽核的分析報告 |

- 工具回傳 **JSON**，不要回傳無限制的純文字。
- 最終報告用 **JSON schema 驗證**，區分 `verified_facts`、`root_cause_hypotheses`（每項要有 `evidence_ids` 與 `counterevidence`）與 `missing_evidence`；**沒有可回查的 evidence ID，不得用「已確認根因」這類字眼**。欄位範例見 [OpenAI-Python-Agent](OpenAI-Python-Agent.md) 的「報告 schema」。
- 快取：以 `(core hash, binary build-id, symbol-set version, analyzer version)` 快取工具輸出（【本庫設計】）。

---

## 6. 成本考量

本節回答「選哪個工具、怎麼設計，成本會怎麼變」。**我只有模型的價格**（[Claude-Model](Claude-Model.md)，資料日期 2026-10-06）；n8n、Claude Code 方案、Managed Agents、LangSmith 等的費用，本庫沒有資料，我也沒有查，**不編數字**。下面的示範數字，凡是比例與 token 數都是**假設**，請換成你們的實際資料。

### 6.1 成本由哪些部分組成

![圖：成本分五塊：模型 token 有價格可估算；基礎設施、人力、平台與授權、誤判成本沒有數據](figures/claude-coredump-cost-model.svg)

| 類別 | 內容 | 本庫有無數據 |
|---|---|---|
| 模型 token | 每次呼叫的輸入與輸出 token | **有價格**，可估算 |
| 基礎設施 | sandbox／microVM 運算、core 與 artifact 儲存、symbol 下載、佇列、資料庫 | 沒有（本庫只有 `max_symbol_download_mb` 這類預算上限的範例） |
| 開發與維運人力 | 建置、觀測、維護案例集 | 沒有；Messages API 最高、Claude Code 最低是【推論】 |
| 平台與授權 | n8n、Claude Code 方案、LangSmith 等 | 沒有，我沒查證 |
| 誤判成本 | 「高信心卻錯」的結論造成的人力與延誤 | 沒有；用評測的「無證據卻高信心」比例追蹤 |

### 6.2 模型 token 成本

![圖：一次呼叫輸入 20K、輸出 2K tokens 的成本：Haiku 5.5 約 0.003 美元、Sonnet 5.5 約 0.06 美元、Opus 5.5 約 0.12 美元、Fable 5.1 約 0.30 美元](figures/claude-coredump-cost-price.svg)

【官方】價格（每 1M tokens，取自 [Claude-Model](Claude-Model.md)）：

| 模型 | 輸入 | 輸出 | 備註 |
|---|---|---|---|
| Haiku 5.5 | $0.10 | $0.50 | prompt 超過 100K 為 $0.50／$2.50 |
| Sonnet 5.5 | $2.00 | $10.00 | cache 讀取 $0.20 |
| Opus 5.5 | $4.00 | $20.00 | cache 讀取 $0.20；目前建議的預設模型 |
| Fable 5.1 | $10.00 | $50.00 | 最高階、最貴 |

計算：`輸入 token × 輸入單價 ＋ 輸出 token × 輸出單價`。圖中的 20K／2K 取自 [OpenAI-Python-Agent](OpenAI-Python-Agent.md) 的 `CaseBudget` 範例（【本庫設計】，初始範例），這裡簡化成「一次呼叫」。

要注意：
- **思考 token**：【官方】Fable 系列永遠開啟思考、Opus 5.5 不可關閉、Sonnet 5.5 傳 `disabled` 會回 400，可用 `effort` 調整思考深度。【推論】思考 token 以輸出計費，所以像 `max_output_tokens=2_000` 這種上限可能被思考吃掉，**預算要把思考算進去**，並用 `effort` 控制。我沒有查證計費方式。
- **Haiku 5.5** 的 prompt 超過 100K 單價較高；第 2 層（20K）不受影響，但深度層若送大量證據要注意。
- 價格資料日期是 2026-10-06，**使用前請重新確認**。

### 6.3 漏斗與升級比例，比選工具更影響月成本

![圖：三種假設情境的每案期望成本：不用漏斗 0.060 美元、漏斗且升級 5% 為 0.040 美元、漏斗但升級 15% 為 0.102 美元，反而比不用漏斗貴](figures/claude-coredump-cost-funnel.svg)

【推論】期望成本 ＝ Σ（到達該層的比例 × 該層單價）；第 0、1 層不呼叫模型，視為模型成本 0（但仍有基礎設施成本）。**以下比例是我的假設，不是資料**：標準分析用 Sonnet 5.5（入 20K／出 2K ＝ $0.06）、深度分析用 Opus 5.5（入 100K／出 8K ＝ $0.56）。

| 情境 | 比例 | 每案期望成本 | 每 1,000 案 | 每 10,000 案 |
|---|---|---|---|---|
| A 不用漏斗 | 每案都跑標準分析 | $0.060 | $60 | $600 |
| B 漏斗，升級少 | 60% 去重、20% 初篩解決、20% 到標準分析、5% 升級深度 | $0.040 | $40 | $400 |
| C 漏斗，升級多 | 60% 去重、10% 初篩解決、30% 到標準分析、15% 升級深度 | $0.102 | $102 | $1,020 |

重點：
- **升級比例比去重命中率更影響成本**。深度層單價是標準層的約 9 倍（$0.56 對 $0.06），升級太多時，漏斗反而比「每案都跑標準分析」更貴（情境 C）。
- 所以第 5.1 節說的升級條件（P0／P1、新 fingerprint、符號完整仍無法判斷、疑似安全或資料損壞）要**收緊並由人核准**，不是越寬越安全。
- **每層用哪個模型，要用案例集決定**：Haiku 5.5 與 Sonnet 5.5 單價差約 20 倍（輸入 $0.10 對 $2、輸出 $0.50 對 $10）。若 Haiku 在案例集上的根因 Top-1 準確率夠用，標準層成本可降一個數量級；若 Sonnet 多解決的案件省下的人力超過價差，就用 Sonnet。**我沒有兩者在 coredump 上的準確率資料**。

### 6.4 降低成本的槓桿

![圖：六個降低成本的槓桿，依預期效果排序：去重與初篩、控制升級比例、每層選對模型等級、快取固定前綴、裁切證據、預算硬上限](figures/claude-coredump-cost-levers.svg)

排序是我的判斷（【建議】），效果取決於你們的案件分布。細節：

- **快取固定前綴**：把固定的 system instructions、工具 schema 與分析 taxonomy 放在 prompt 前段，個案資料放後段（【本庫設計】）。【官方】cache 讀取價為 $0.20／1M（Opus 5.5、Sonnet 5.5）。示範（**假設固定前綴 8K tokens**）：Sonnet 5.5 不快取為 8K × $2 ／ 1M ＝ $0.016，命中快取為 8K × $0.20 ／ 1M ＝ $0.0016，**每次呼叫省約 $0.0144，約為一次標準分析（$0.06）的 24%**。cache 寫入價、最短可快取長度與存活時間，本庫沒有資料，我沒查證。
- **Message Batches API**：【官方】本庫提到有此 API（僅提到擴充輸出的 beta）；**折扣幅度與限制本庫沒有資料，我沒查證**。coredump 分析多半不需即時，值得評估；但延遲是否可接受要自己確認（【推論】）。
- **Task Budgets（beta）**：【官方】支援 Opus 5.5、Sonnet 5.5、Haiku 5.5 等，用於限制單次 agentic 任務的 token 上限；細節我沒查證。它**不取代** orchestrator 的 `CaseBudget`，只是多一道保險（【建議】）。
- **Fast Mode**：【官方】價格為標準價 2 倍（Opus 5.5 為 $8／$40）；非即時的 coredump 分析沒有理由開（【建議】）。
- **裁切證據**：輸入 token 與送給模型的案件摘要大小成正比；只傳前 3–10 個關鍵 frames 與必要 source 摘錄（【本庫設計】）。

### 6.5 各工具的成本型態

| 工具 | 主要成本 | 怎麼控制 | 本庫有無數據 |
|---|---|---|---|
| Messages API ＋ orchestrator | 按 token（6.2 價格）＋**最高的開發人力** | orchestrator 逐呼叫計帳，可硬性上限、可跨案件累積 | 價格有；人力沒有 |
| `claude -p` | 若用 API 計費則按 token（【推論】；本庫沒有訂閱方案如何計） | `--max-budget-usd` 只在單次內生效；跨次自己加總 `--output-format json` 的 `total_cost_usd`，或在 Console 設 workspace 層級 spend limit（【官方】） | 沒有方案價格 |
| Agent SDK | 按 token；迴圈由 SDK 管，多輪工具呼叫會累積 context（【推論】） | 能否逐步強制預算我沒查證 | 沒有 |
| Claude Code（互動） | 開發階段的工程師使用成本 | 不計入每案成本 | 沒有方案價格 |
| n8n | 平台費用（自架或雲端）我沒查證 | — | 沒有 |
| LangChain／LangGraph | 框架本身費用我沒查證；多一層抽象增加工程與除錯成本（【推論】） | — | 沒有 |
| Managed Agents | 本庫沒有計費資料 | — | 沒有 |

在你們的規模下**哪一項是大頭，需要實際數字**；我不建議憑感覺在工具之間比較授權費，先用 6.6 量測。

### 6.6 怎麼量測與控管（【建議】）

1. **每案記錄**：token、模型呼叫次數、debugger 秒數、估算成本（第 10 節的觀測欄位已涵蓋）。
2. **三層預算**：每案（`CaseBudget`）、每日或每月（Console workspace spend limit，加上自己的加總）、超標告警。
3. **先量再估**：用 50–100 個已知案例，量出「每層命中率、升級率、每層成本」，再把 6.3 的假設換成實測。
4. **成本與準確率一起看**：比較 Haiku 與 Sonnet 當標準層時，同時看每案成本與根因 Top-1／Top-3、「無證據卻高信心」比例。
5. **小規模試跑**後再決定模型等級與升級條件。

---

## 7. 安全邊界與資料外送

![圖：資料流與安全邊界：不信任的 dump 留在隔離環境，只有裁切後的證據送給模型；完整 dump、任意 shell、寫入權限不給模型；建立 Issue、改程式、push、重新部署要人核准](figures/claude-coredump-security.svg)

【本庫設計】coredump 視為**不可信輸入**，每案在隔離容器或 microVM 執行：

- 以**唯讀**掛載 core、binary、symbols、source snapshot；
- 預設**禁止網路**，只有符號服務需要時以 allowlist 開啟；
- 限制 CPU、記憶體、磁碟與 debugger 執行時間；
- 關閉 debugger 自動載入腳本；
- 只允許事先定義的 `gdb`／`lldb` batch 命令，**不提供任意 shell**；
- 建立 issue、修改程式、推送修正、重新部署等動作要**人工核准**。

**資料外送**（【建議】）：dump 是記憶體快照，可能含客戶資料或機密。送到任何外部 API 之前，先確認公司政策；用 Messages API 時，你能決定送出什麼，所以**只送裁切後的結構化證據**，原始 dump 留在 artifact storage。若改用 Managed Agents，工作區在 Anthropic 雲端，這個控制就變弱（【推論】）。

---

## 8. n8n 與 LangChain／LangGraph 怎麼放

**n8n**（【推論】，我沒查 n8n 文件；接 Jira 時是否需要它，見第 9.2 節）：
- 適合做：接收 webhook／CI 事件、丟進佇列、等分析完成後回寫 Jira／Issue、通知、人工核准。
- 不建議做：把分析迴圈拆成多個節點。預算、狀態與工具權限會散落在流程圖裡，難以硬性強制與稽核。
- 邊界：n8n 只呼叫「你們的 orchestrator」的 API，不直接呼叫模型。

**LangChain／LangGraph**（【推論】，我沒評估它目前的版本）：
- 這個系統的價值在**受控工具與預算**，不在串模型呼叫，框架幫不上最關鍵的部分。
- 團隊**已經熟 LangGraph**時，可以用它取代自寫狀態機；但預算與安全限制仍要在你們的工具層強制，不能交給框架。

---

## 9. 接 Jira：事件進來、分析、結果回寫

情境：**Jira 收到帶 coredump 的 ticket → 發事件給 parser → parser 分析 → 結果回寫 Jira**。本節回答三個問題：要串哪些工具？一定要 n8n 嗎？能不能用 Python 常駐服務直接收事件、或只用 Claude Code？

**依據與標記**：【官方】取自本庫整理的 Claude 資料（[Claude-Code-CLI](Claude-Code-CLI.md) 的 Routines 與 `claude -p`）；**【官方\*】**是 Atlassian 官方頁面的內容，但我只看到搜尋結果的摘要，**沒有開啟原文**；**🔎** 是社群或第三方的二手說法；【建議】與【推論】同前。**假設是 Jira Cloud**；Data Center 的 webhook 機制可能不同，我沒查證。⚠️ 我沒有實測任何一條路線，也沒看過你們的 Jira 設定。

### 9.1 要串的工具

![圖：Jira 收到 coredump ticket 之後要串的九個環節：觸發、接收端、佇列與 worker、取證據、擷取與去重、分析、驗證、回寫為必要，通知與核准為選用](figures/claude-coredump-jira-flow.svg)

| 環節 | 要串的工具 | 必要？ | 備註 |
|---|---|---|---|
| 1 觸發 | Jira webhook，或 Automation 的「Send web request」 | 必要 | 【官方\*】webhook 可選事件（issue 建立、更新、附件建立等），可用 JQL 過濾；🔎 社群回報：由 Automation 觸發的更新事件，可能不含附件與留言的變更，要另外查 |
| 2 接收端 | n8n webhook 節點，或自寫小 API | 必要 | 驗證來源、用 `issue key ＋ attachment id` 去重、立刻回 2xx、丟進佇列 |
| 3 佇列與 worker | 現有的 job queue，或一張 jobs 表 | 必要 | 併發、重試、timeout、每案預算由這層負責（本庫 CodeX-CLI 對 Jira webhook 的分工原則） |
| 4 取證據 | Jira REST API 取附件，或 artifact storage 的連結 | 必要 | 【推論】一般做法是讀 issue 的附件欄位、用認證下載，我沒驗證；coredump 常很大，ticket 可能只放連結，見下方「先確認」 |
| 5 擷取與去重 | `gdb`／`lldb`／`readelf`、symbols、對應 commit 的 source、案件資料庫 | 必要 | 已有程式能產出 backtrace，模型就不必碰 `gdb`（第 4 節） |
| 6 分析 | Claude API ＋ 受控工具（或 `claude -p`） | 必要 | 第 5 節；`claude -p` 見 9.5 |
| 7 驗證 | JSON schema，再轉成 Markdown | 必要 | 不要把模型自由文字直接貼進 Jira |
| 8 回寫 | Jira REST API：comment、label、issue link | 必要 | 重複案件連到既有 issue |
| 9 通知與核准 | n8n、Slack、Teams | 選用 | 修改狀態、指派、建立子 issue 屬高風險動作，要人核准（【本庫設計】） |

**先確認這四點，會改變設計**：① Jira Cloud 還是 Data Center？② coredump 實際放哪：附在 ticket，還是放在別處、ticket 只有連結？（我不確定你們的附件大小上限。）③ 附件權限能否讓 bot 讀取？dump 可能含客戶資料。④ 是否已有 job queue、CI worker，或已在用 n8n？

### 9.2 一定需要 n8n 嗎？不一定

![圖：不用 n8n 與用 n8n 兩條路徑並排，以及各自適合的時機](figures/claude-coredump-jira-n8n.svg)

n8n 在這條流程裡只做三件事，用幾十行程式也能做（【推論】，我沒查 n8n 文件）：**接 Jira 的 webhook**、**回寫 Jira**、**通知與人工核准**。分析本身（取證據、去重、呼叫 Claude、驗證報告）本來就在你們的 Python worker 裡，跟 n8n 無關。

- **建議先不用**（【建議】）：用「Jira Automation → 小 API → 佇列 → worker → Jira REST 回寫」把最小版本跑通。等通知與核准的需求變多、或要讓非工程師調整流程，再把那一段交給 n8n；對分析核心沒有影響，之後加的成本很低。
- **值得用的時機**：沒人想維護接收端與回寫的程式；通知與核准流程常改、由非工程師調整；公司已在用 n8n。
- **不建議的時機**：已有 queue 與 worker 框架（多一個平台要維運）；dump 不能離開公司（n8n 要自架，要計入維運成本）；想把分析迴圈拆進 n8n 節點（預算、狀態、權限會散落在流程圖裡）。
- 費用面見第 6.5 節與下方的未驗證項目：n8n Cloud 按執行次數計，我沒能確認官方價格。

### 9.3 用 Python 常駐服務直接收 Jira 事件

**可以，而且是最單純的做法**：一個 Python 常駐服務收 webhook，用 Claude 的 Python SDK 分析，再呼叫 Jira REST API 回寫（【建議】，沒有實測）。

![圖：Python 常駐服務的架構：接收端、jobs 表與回寫端持有憑證，隔離 worker 無憑證、無對外網路，只回傳精簡證據](figures/claude-coredump-jira-daemon.svg)

1. **不要在收 webhook 的請求裡做分析。** 先寫進 jobs 表、立刻回 2xx，分析交給 worker；分析要幾十秒到幾分鐘，會超過一般 HTTP 逾時。
2. **佇列要持久。** 只用記憶體內的 queue，服務重啟會丟案件；最簡單是一張 jobs 表（待處理、分析中、完成、失敗），worker 輪詢領取。
3. **`gdb` 不要跑在持有憑證的行程裡。** coredump 是不可信輸入；worker 在隔離環境（唯讀掛載、無網路、有 timeout）只產出精簡證據，呼叫 Claude 與回寫 Jira 由有憑證的服務做（第 7 節的安全邊界）。
4. **I/O 用非同步，`gdb` 用子行程**，並限制同時執行的案件數。
5. **Jira 要打得到你的服務**（【推論】）：Jira Cloud 的 webhook 是從外部打你的 HTTPS 網址，內網服務需要公開入口（反向代理、TLS）或轉送；Data Center 在同一內網則沒有這個問題。
6. **來源驗證**：webhook 的驗證方式依版本而異，我沒查證；至少用 HTTPS、不可猜的 secret 路徑或 token，再加 IP 白名單。
7. **維運**：systemd 或容器自動重啟、健康檢查、優雅關閉（收到停止訊號時，把「分析中」的案件放回待處理）、記錄每案 token 與成本。

**規模**：案件很少時，服務加 SQLite 就夠；案件量大時，把 jobs 表換成正式 queue（Redis、SQS 等）並加多個 worker，架構不變。**SDK**：核心用 Claude 的 Python SDK（Messages API）；Agent SDK 只在分析完成後的子流程才考慮。

### 9.4 事件去重與防迴圈

![圖：事件去重與防迴圈的時序圖：服務驗證並去重後入 jobs 表，立刻回 2xx；分析完成後回寫 Jira，回寫又觸發更新事件，服務判斷是 bot 事件而略過](figures/claude-coredump-jira-loop.svg)

【建議】Jira 特有的坑：

- **回寫會再觸發 webhook。** 你回寫 comment 或 label，會產生 issue 更新事件而造成迴圈；用 JQL 過濾，或略過 bot 帳號的事件。
- **一個 ticket 可能有多個附件、多次更新。** 去重 key 用 `issue key ＋ attachment id`，必要時加檔案 hash；重複事件只處理一次。
- **bot 帳號用最小權限。** 修改狀態、指派、建立子 issue 要人工核准。
- **用 JQL 縮小觸發範圍**，例如只處理帶特定 label 或有附件的 ticket。
- **Jira 的重送次數與逾時行為，我沒查證**，所以接收端要能容忍重複事件。

### 9.5 只用 Claude Code 行不行？

![圖：只用 Claude Code 的四條路線：Routine 的 API 觸發、服務加 claude -p、排程輪詢、Messages API worker，以及各自的限制](figures/claude-coredump-jira-claudeonly.svg)

**純 Claude Code 可以做出能跑的原型，但缺「接事件、佇列、硬性控制」這些系統工程。**

| 需求 | 能不能 | 依據與說明 |
|---|---|---|
| 讀 source、跑 `gdb`、判讀證據、產生報告 | 能 | 這是它的本行，人工調查罕見 crash 最適合 |
| 結構化輸出 | 能 | `claude -p` 有 `--json-schema`（【官方】） |
| 收到 Jira 事件 | 有條件 | 見下 |
| 每案硬性預算 | 部分 | `--max-turns`、`--max-budget-usd` 只在單次執行內生效，不跨案累積（【官方】） |
| fingerprint 去重、跨案快取 | 不能 | 要外部程式與資料庫 |
| 佇列、重試、併發控制 | 不能 | 要外部程式 |
| 隔離不可信的 dump | 不能自己做 | `claude -p` 跳過 workspace trust 對話框，只該在信任的目錄跑（【官方】）；隔離要自己做 |

**純 Claude Code 收 Jira 事件的三條路**：

1. **A：Routine 的 API 觸發**（【官方】）：在 Web UI 建 routine，取得專屬 HTTP endpoint，POST 即可觸發，帶 `text` 欄位當額外 context。理論上 Jira Automation 的「Send web request」可以打它，但**能否帶所需的 Bearer header，我沒查證**。限制：跑在 **Anthropic 雲端**、需要 claude.ai 訂閱帳號；API 觸發目前是 experimental beta（要帶 `anthropic-beta` 標頭）；有每日 routine 執行配額（額度我沒查到）；只能用 `text` 傳文字，**coredump 本身進不去**，dump 與 `gdb` 環境在雲端不一定可用，資料也會離開公司。
2. **B：自己的服務收 webhook，再呼叫 `claude -p`**：仍需要接收端，分析交給 Claude Code。
3. **C：排程輪詢 Jira**：Routine 排程最小間隔 1 小時；`/loop` 在本機 session 內執行，7 天後過期；都不即時。

**判斷**：案件很少、有人看結果、dump 可外送、沒有嚴格成本上限 → A 或 B 就夠；案件多、要每案成本上限、去重、隔離 → B 或自寫 Messages API worker。

**折衷（我的建議）**：保留 9.3 的「薄服務 ＋ jobs 表」，分析 worker 改用 `claude -p`，不自己寫工具迴圈：

```text
Jira webhook → 薄服務（驗證、去重、jobs 表）
   → 隔離環境中跑 claude -p
        --allowedTools／--disallowedTools（限制內建 Bash、Edit 等）
        --max-turns、--max-budget-usd、--json-schema
        --no-session-persistence
   → 服務驗證 schema → 回寫 Jira
```

- **好處**：工程量比自寫工具迴圈低，Claude Code 的讀碼與 `gdb` 能力直接可用。
- **代價**：迴圈內部不能硬性控制「每案總 token」，只有單次上限；工具集預設比六個受控工具寬，要靠白名單收緊；去重與帳務仍要外部做。
- 日後要精確控制成本，再把 worker 換成 Messages API，薄服務不用改。

### 9.6 本節未驗證的項目

- Jira webhook 的簽章或 secret 機制、重送次數與逾時、附件下載的細節，以及你們的 Jira 是 Cloud 還是 Data Center。
- Jira Automation 能否帶 Bearer header 打 Routine 的 endpoint；Routine 的每日配額數字。
- n8n 與 LangChain 的官方價格：我嘗試讀官方定價頁，三個網域（`n8n.io`、`www.langchain.com`、`docs.langchain.com`）被這個環境的網路政策擋住，只有搜尋摘要，且各來源互有出入，所以**沒有寫進文件**。
- 所有路線都**沒有實測**。

---

## 10. 導入順序

![圖：導入順序的五個階段與完成條件：Claude Code 互動驗證、Messages API 最小版本、去重快取預算、佇列 n8n 核准評測、選配 Agent SDK 子流程](figures/claude-coredump-roadmap.svg)

【本庫設計】順序取自 OpenAI 版並改為 Claude；「完成條件」是我的建議。

**評測**（【本庫設計】）：建立 50–100 個已知 root cause 的 coredump 案例集，持續評估：
- fingerprint 去重命中率；
- symbol 與 backtrace 成功率；
- 根因 Top-1／Top-3 正確率；
- **無證據卻高信心下結論**的比例；
- 每案成本、耗時、工具呼叫數與人工介入率；
- **每一層用哪個模型的「成本對準確率」**（第 6.3 節）。

每個案件至少記錄：crash signature、binary／symbol 版本、工具版本、模型與 prompt 版本、模型呼叫次數與 token、工具呼叫與 debugger 秒數、升級原因、最終人工判定。

---

## 11. 什麼情況下，結論會改變

![圖：五種情況與對應的結論改變：core 很少改用 claude -p；已熟 LangGraph 可取代自寫狀態機；dump 不能出公司要先決定模型來源；需要託管再評估 Managed Agents；子流程變多加入 Agent SDK](figures/claude-coredump-change.svg)

---

## 12. 驗證說明與限制

- 資料日期 2026-11-20。**我沒有實作過**，偽程式碼沒有執行過，函式與欄位名稱是假設。
- 內容取自本庫已整理的文件：[Claude-Code-CLI](Claude-Code-CLI.md)（`claude -p` 旗標、Agent SDK、非互動注意事項）、[Claude-Agent](Claude-Agent.md)（Managed Agents、Agent SDK、Tool Runner）、[Claude-Model](Claude-Model.md)、[OpenAI-Python-Agent](OpenAI-Python-Agent.md)（設計原則、漏斗、工具集、安全、評測）、[CodeX-CLI](CodeX-CLI.md)（n8n 的分工）。
- **這次沒有開啟任何官方頁面**，所以 Claude 部分只和本庫已整理的內容一致，沒有重新驗證。**n8n 與 LangChain／LangGraph 的功能我完全沒有查證**，標【推論】的都是類推。
- 【本庫設計】來自 OpenAI 版：把 `openai` SDK 的判斷類推到 Claude Messages API 是【推論】；兩家 API 的細節（工具呼叫格式、快取、結構化輸出）不同，實作時請以 Claude 官方文件為準。
- **Claude Agent SDK** 的細節（如何限制內建工具、能否逐步強制預算、hooks）我沒有查證。
- **成本（第 6 節）**：價格取自 [Claude-Model](Claude-Model.md)（2026-10-06，我這次沒有重新確認）；示範用的 token 數、去重與升級比例、固定前綴大小**都是假設**，不是你們的資料；算式我用程式驗算過，但沒有實際呼叫 API 量測。cache 寫入價、Batch 折扣、Task Budgets 細節、思考 token 的計費方式，以及 n8n、Claude Code 方案、Managed Agents、LangSmith 的費用，我都沒有查證。
- **Jira 整合（第 9 節）**：Jira webhook、JQL 過濾、Automation 行為來自搜尋結果對 Atlassian 官方頁面的摘要（標【官方\*】），**我沒有開啟原文**；社群說法標 🔎。Routines 與 `claude -p` 的內容取自本庫的 Claude-Code-CLI。n8n 與 LangChain 的官方價格頁我讀不到（網路被擋），所以沒有寫進文件。這一節是通用架構，不是針對你們 Jira 的設計，也沒有實測。
- 我沒有你們的環境資訊（每日 core 量、平台、是否已有擷取程式、資料政策），所以結論有條件，見「請你確認」與第 11 節。

---

## 13. 參考

- 本庫：[OpenAI-Python-Agent](OpenAI-Python-Agent.md)（同一類系統的完整設計）、[Claude-Agent](Claude-Agent.md)、[Claude-Code-CLI](Claude-Code-CLI.md)、[Claude-Model](Claude-Model.md)、[CodeX-CLI](CodeX-CLI.md)、[Agentic-Engineering](Agentic-Engineering.md)。
- Atlassian（第 9 節，網址來自搜尋結果，**我沒有開啟原文**）：Jira Cloud webhooks <https://developer.atlassian.com/cloud/jira/platform/webhooks/>、Automation webhooks <https://developer.atlassian.com/cloud/jira/service-desk/automation-webhooks>；二手：社群討論〈更新事件下載附件〉<https://community.developer.atlassian.com/t/download-attachment-in-jira-cloud-using-rest-api-for-issue-update-events/3224/2>（🔎）。
- Anthropic：*Building effective agents*：<https://www.anthropic.com/engineering/building-effective-agents>（區分 workflow 與 agent，建議先用簡單模式；本庫 [AI-Learning-Resources](AI-Learning-Resources.md) 已列，我這次沒重新開啟）。
