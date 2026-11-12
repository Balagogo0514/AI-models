# Python + OpenAI：coredump 自動分析 Agent 設計筆記

## 目標

建立一個由 Python 控制的 coredump 自動分析流程。模型負責規劃、判讀證據及整理結論；受控工具負責執行 debugger、符號解析、程式碼搜尋與保存結果。

```text
coredump / CI 事件
        ↓
案件佇列、artifact storage、fingerprint 去重
        ↓
Python orchestrator（預算、狀態、權限、重試）
        ↓
Agent（規劃、工具選擇、證據判讀）
        ↓
受控 debugger / symbol / source tools
        ↓
結構化報告 + 人工審核或 Issue workflow
```

## 最重要的原則

1. **模型不是 debugger。** `gdb`、`lldb`、symbolication 和 source lookup 是證據來源；模型只能根據工具結果推論。
2. **不可直接暴露任意 shell。** 模型只可呼叫具 allowlist、schema、timeout 與資源限制的 Python 工具。
3. **不可將完整 coredump 直接放進 prompt。** 原始檔留在 artifact storage；只向模型提供經過裁切的結構化證據與 evidence ID。
4. **預算由外部程式強制。** Prompt 中的「節省成本」不等於可執行的成本控制。
5. **結論需區分事實與假設。** 每一個根因判斷都必須連回 debugger、symbols、source 或 log 的證據。

## 使用 Codex 還是 OpenAI Agent SDK？

| 需求 | 建議介面 |
|---|---|
| 人工處理少量未知 crash、驗證分析流程 | 互動式 Codex |
| CI、排程或 webhook 觸發一次分析 | `codex exec` |
| Python 控制本機 Codex thread、workspace、sandbox | Codex Python SDK (`openai-codex`) |
| 正式服務：佇列、去重、預算、稽核、專用工具 | Responses API 或 Agents SDK (`openai-agents`) |

互動式 Codex 並非不能分析 coredump；但它不是事件佇列、案件資料庫、成本帳務或可重試 worker。若有每案成本上限、跨案件快取、CI 觸發、併發、審核與稽核需求，應把模型代理放入 Python orchestrator 的外部控制迴圈。

### 推薦的演進方式

```text
第一階段：互動式 Codex
  驗證 gdb 指令、prompt、報告 schema 與真實案例。

第二階段：codex exec 或 Codex SDK
  將分析接入 CI / job queue，每案使用獨立 sandbox。

第三階段：Python service
  加入去重、artifact、預算、權限、重試、評測與人工核准。
```

## Python 套件選擇與安裝

只需選擇其中一條核心路線，第一版不要混用兩種 agent runtime。

```powershell
# 自行控制 Responses API 工具迴圈
pip install openai

# 使用 OpenAI Agents SDK 的工具迴圈、session、trace、guardrail
pip install openai-agents

# 在 Python 中控制本機 Codex runtime（Python SDK 目前為 beta）
pip install openai-codex
```

- `openai`：適合要精確掌控狀態機、路由、分支與每一步預算的情況。
- `openai-agents`：適合需要現成 agent loop、function tools、sessions、tracing、guardrails 與可恢復的核准流程。
- `openai-codex`：適合要沿用 Codex 的本機工作區、thread 與 sandbox 行為。

`openai` 和 `openai-agents` 通常透過 `OPENAI_API_KEY` 使用 API。`openai-codex` 控制本機 Codex runtime，其身分驗證與一般 API key 設定並非完全相同。

建議在虛擬環境安裝：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install openai-agents
```

## 建議的 Agent 工具

先做一個 agent 搭配以下六個工具；不要一開始就建立多代理架構。

| 工具 | 輸入 | 輸出與目的 |
|---|---|---|
| `inspect_core` | artifact path | OS、架構、PID、signal、binary 與 module build-id |
| `resolve_symbols` | build-id 列表 | symbol 是否完整、使用的 symbol-set version、缺少項目 |
| `extract_backtrace` | case ID | 各 thread 的標準化 stack frames |
| `inspect_frame` | thread ID、frame index | 受限的區域變數、registers、source location |
| `search_repository` | query、revision | source 摘錄、Git blame、關聯的 issue 或變更 |
| `save_analysis` | case ID、report schema | 保存可稽核的分析報告 |

工具結果應為 JSON，不應回傳無限制的純文字輸出：

```json
{
  "thread_id": 17,
  "signal": "SIGSEGV",
  "frames": [
    {"function": "parse_header", "file": "parser.cc", "line": 284}
  ],
  "evidence_id": "artifact://case/482/backtrace/thread-17.json",
  "confidence": "verified"
}
```

## 報告 schema

Agent 的最終輸出應以 JSON schema 驗證，至少包含：

```json
{
  "status": "resolved | needs_human_or_deep_analysis",
  "crash_signature": "...",
  "verified_facts": ["..."],
  "root_cause_hypotheses": [
    {
      "claim": "...",
      "confidence": "low | medium | high",
      "evidence_ids": ["artifact://..."] ,
      "counterevidence": ["..."]
    }
  ],
  "missing_evidence": ["..."],
  "recommended_next_action": "..."
}
```

禁止使用「已確認根因」這類字眼，除非結論具有可回查的 evidence ID。

## 安全邊界

coredump 應視為不可信輸入。建議每個案件在隔離容器或 microVM 中執行：

- 以唯讀方式掛載 core、binary、symbols 與 source snapshot。
- 預設禁止網路；只有符號服務需要時才以 allowlist 開啟。
- 限制 CPU、記憶體、磁碟與 debugger 執行時間。
- 關閉 debugger 自動載入腳本與非必要外部行為。
- 僅允許事先定義的 `gdb` / `lldb` batch 命令，不提供任意 shell。
- 對建立 issue、修改程式、推送修正、重新部署等動作採人工核准。

## 每案成本控制

### 四層漏斗

```text
0. Fingerprint 去重             → 不呼叫模型
1. Deterministic triage         → 不呼叫模型
2. Standard model analysis      → 一次短模型分析
3. Deep analysis                → 僅未知、高風險案件升級
```

### Layer 0：Crash fingerprint

以 `signal + app build-id + module build-id + normalized top frames` 產生 signature。相同 signature 命中既有分析時，直接回傳已知根因與關聯案件，不再呼叫模型。

### Layer 1：固定工具初篩

先執行 `readelf`、symbolication、受限 `gdb -batch`、thread/frame 摘要與已知 issue 搜尋。這些工作成本低、可快取且可重現。

### Layer 2：標準模型分析

僅傳入：

```text
案件摘要
+ verified facts
+ 前 3–10 個關鍵 frames
+ 必要 source 摘錄
+ 已知 crash 相關結果
+ 問題清單
```

輸出必須短且符合 schema。

### Layer 3：深度分析

只有下列情況才升級：

- P1 / P0 事件；
- 新 fingerprint；
- symbols 完整但標準流程仍無法判斷；
- 標準流程發現可能的安全或資料損壞風險。

升級應需要人工核准或明確的 on-call policy。

### 硬性預算

以下數值是初始範例，應根據真實資料調整：

```python
CaseBudget(
    max_model_calls=2,
    max_tool_calls=8,
    max_input_tokens=20_000,
    max_output_tokens=2_000,
    max_debugger_seconds=90,
    max_symbol_download_mb=200,
)
```

預算耗盡時不得無限制重試，應返回 `needs_human_or_deep_analysis`，並列出已驗證事實與缺少的證據。

### 快取策略

- 以 `(core hash, binary build-id, symbol-set version, analyzer version)` 快取工具輸出。
- 固定 system instructions、工具 schema、分析 taxonomy 放在 prompt 前段；個案資料放在後段。
- 對頻繁重複的固定 prompt prefix 使用 `prompt_cache_key` 與明確 cache breakpoint。
- 持續記錄 `cached_tokens`、`cache_write_tokens`、輸入、輸出與 reasoning tokens，依真實命中率調整。
- 原始 artifact 外部保存；對話只保留精簡的 case facts、open questions 與 evidence IDs。

## 觀測與評測

每個案件至少記錄：

```text
case ID、crash signature、binary / symbol version、工具版本
模型與 prompt version、模型呼叫次數、token 用量、cache hit
工具呼叫、debugger 秒數、模型升級原因、最終人工判定
```

建立 50–100 個已知 root cause 的 coredump 案例集，持續評估：

- fingerprint 去重命中率；
- symbol 與 backtrace 成功率；
- 根因 Top-1 / Top-3 正確率；
- 無證據卻高信心下結論的比例；
- 每案成本、耗時、工具呼叫數與人工介入率。

目標不是讓每案進入高成本深度推理，而是讓多數已知案件在 Layer 0–2 完成。

## 已有 full backtrace、registers、threads 時的精簡架構

若既有程式已能穩定產出：

- full backtrace；
- `info registers`；
- `info threads`；

則不需要讓模型直接操作 `gdb`。這是較安全、成本更低且更容易重現的設計：deterministic 程式負責取得 debugger 證據，模型僅負責解讀已取得的 artifact。

```text
既有 debugger 程式
  ├─ full backtrace
  ├─ info registers
  └─ info threads
        ↓
Python preprocess / normalize
        ↓
case_facts.json + crash fingerprint + artifact IDs
        ↓
去重／命中既有 root cause？
  ├─ 是：回傳既有分析與關聯案件，不呼叫模型
  └─ 否：單次模型判讀
              ↓
         不確定時才搜尋 source / Git / issue
```

此設計把正式系統的模型成本壓縮到多數新案件只需一次判讀；只有未知、高優先或證據不足的案件才進入第二次深度分析。

### 流程圖

![圖：已有 backtrace 時的精簡流程——fingerprint 命中就不呼叫模型，未命中才進入預算控管的分析](figures/openai-python-agent-lean-flow.svg)

正式 production 控制層為：

```text
Python orchestrator + openai SDK + Responses API
```

### `case_facts.json` 建議 schema

不要把原始 `gdb` 全部輸出直接放入 prompt。先由 Python 產生小而穩定的事實摘要，原始資料則留在 artifact storage：

```json
{
  "signal": "SIGSEGV",
  "faulting_thread": 17,
  "pc": "0x...",
  "sp": "0x...",
  "crash_signature": "sha256:...",
  "top_frames": [
    {"function": "parse_header", "file": "parser.cc", "line": 284}
  ],
  "thread_summary": [
    {"thread_id": 17, "state": "crashed", "top_function": "parse_header"}
  ],
  "register_summary": {
    "instruction_pointer": "0x...",
    "stack_pointer": "0x...",
    "fault_address": "0x..."
  },
  "artifacts": {
    "full_backtrace": "artifact://case/482/backtrace.txt",
    "all_registers": "artifact://case/482/registers.txt",
    "all_threads": "artifact://case/482/threads.txt"
  }
}
```

依 CPU 架構調整 register summary 欄位。例如 x86_64 應至少保留 instruction pointer、stack pointer、frame pointer、fault address 與 signal；ARM 則保留相對應的 PC、SP、FP 與 fault address。

### 第一輪模型可見的最小證據集

第一輪僅傳入：

- signal、crashed thread、fault address；
- 前 5–10 個標準化 stack frames；
- 所有 thread 的頂層 frame 摘要；
- 必要的 PC、SP、FP 與架構相關 registers；
- binary build-id、版本與 crash fingerprint；
- 相同 fingerprint 的歷史案件或已知根因。

完整 backtrace、完整 registers 與全量 threads 應保留為 artifact。若模型真的需要細節，使用受控的按需工具取得單一 thread、frame 或 source 範圍，而非重新傳送整份輸出。

### 依此架構調整的工具集

既有 debugger 輸出已取代 `extract_backtrace` 與大部分 `inspect_frame` 工作，因此正式 agent 最小工具可縮減為：

| 工具 | 用途 |
|---|---|
| `get_case_facts` | 讀取已驗證、經正規化的 `case_facts.json` |
| `lookup_signature` | 查詢相同 crash fingerprint、已知根因與關聯 Issue |
| `get_artifact_excerpt` | 以 evidence ID 按需讀取指定 thread、frame 或 register 範圍 |
| `search_repository` | 搜尋 source、Git blame、變更與既有 issue |
| `save_analysis` | 保存符合 schema 的結論、證據與後續動作 |

這些工具仍應使用嚴格 schema、最大輸出長度和 timeout。原始 core 不應直接提供給模型，也不必暴露任意 debugger 或 shell。

### 建議的下一步

1. 固定 `case_facts.json` schema 並為 schema 設定版本號。
2. 建立 normalized crash fingerprint，作為去重與快取主鍵。
3. 建立 `signature → root cause / issue / fix version` 的資料表。
4. 為 `search_repository` 與 `get_artifact_excerpt` 設計最小、可稽核的 tool schema。
5. 以固定案例集測試「一次模型判讀」的根因 Top-1 / Top-3 正確率，再決定何時升級深度分析。

## SDK 角色分工：依 coredump 需求選型

三種 SDK 可以在同一組織中並存，但不應同時擔任同一個案件的主要 agent runtime。對 coredump 自動分析而言，建議的角色分工如下：

| SDK | 在 coredump 系統的建議角色 | 優點 | 不適合作為核心的原因 |
|---|---|---|---|
| `openai` | **正式 production worker 的核心**：使用 Responses API，管理案件狀態、工具迴圈、預算、快取與審核 | 控制力最高；可硬性限制每案 token、tool calls、時間與支出；容易整合 queue、database、artifact 與自訂安全政策 | 初期工程量最高，必須自行實作 state machine、retry、觀測與部分工具迴圈 |
| `openai-agents` | **研發／原型環境**：驗證工具定義、trace、session、guardrail 或較標準化子流程 | 內建 agent loop、tracing、sessions、guardrails、handoffs 與可恢復核准流程 | SDK 管理部分迴圈，對每案的細緻預算、特製分支與案件狀態控制不如自建 orchestrator 直接 |
| `openai-codex` | **工程師與 CI 輔助**：探索未知 crash、協助撰寫 debugger 腳本、一次性 repo／dump 分析 | 可延用 Codex 的本機 workspace、thread 與 sandbox 能力；上手快 | 非事件佇列、案件資料庫或成本帳務系統；不宜把 Codex thread 當正式 case state 或自動重試機制 |

### 正式推薦

針對下列已提出的要求：

- 每個 coredump 必須有成本上限；
- 需 fingerprint 去重與跨案件快取；
- debugger 與 symbol 操作要受到 allowlist、timeout 和 sandbox 控制；
- 有 standard analysis 與 deep analysis 的升級規則；
- 需要 CI / webhook、job queue、重試、人工核准與可稽核 artifact；

正式系統應選擇：

```text
Python orchestrator
  + openai SDK
  + Responses API
  + 受控的 debugger / symbol / source Python tools
```

這條路線的初期開發難度最高，但原因是它不會隱藏必要的系統工程。對需要可預測成本與安全邊界的 coredump 服務而言，這些控制本來就應由系統擁有。

### 建議部署隔離

即使三種 SDK 都需要使用，也應在不同環境中分隔相依與職責：

```text
venv-prod
  └─ openai
     正式 coredump worker

venv-agent-lab
  └─ openai + openai-agents
     agent workflow 實驗、工具 trace 與評測

venv-codex
  └─ openai-codex
     工程師輔助、互動式 investigation、CI 一次性工作
```

避免同一個 case 同時讓 Responses API 與 Agents SDK 各自執行工具迴圈，也避免把 Codex thread 當作 production case database。否則容易造成工具重複執行、成本帳務不一致、狀態分叉與稽核困難。

### 各 SDK 的使用時機

| SDK | 適合引入的時機 | coredump 情境範例 | 不適合引入的時機 |
|---|---|---|---|
| `openai` + Responses API | 系統需要精確掌控每一步工具、成本、狀態、分支、retry 與人工核准 | 正式 coredump 根因分析、fingerprint 去重、預算升級、artifact 查詢與結構化分析報告 | 不適合只為了快速做一次手動 investigation 而建立完整服務 |
| `openai-agents` | 工作流已是可重複的多步驟流程，且需要 sessions、traces、guardrails、handoffs 或可恢復核准 | 根因分析完成後，將結果分流至 Issue 建立、相似事件搜尋、修復建議、通知與文件整理等子流程 | 每案需要極嚴格的 token / tool / 時間上限，或必須由自訂 state machine 精確決定每一分支時 |
| `openai-codex` | 工程師需在 repo 或 workspace 中探索、修改程式、執行測試或研究未知問題，且有人監督 | 研究罕見 crash、改善 backtrace parser、撰寫 symbol 工具測試、尋找可能引入 regression 的 commit；也可用 `codex exec` 作一次性 CI investigation | 高量自動化 coredump worker、跨案件去重與成本帳務、將不可信 dump 作為長期服務輸入時 |

可用下列判斷規則選擇：

```text
需要由系統精確決定下一步、成本與案件狀態？
  → openai + Responses API

需要標準化多步驟 agent、trace、session、handoff 或人工核准？
  → openai-agents

需要工程師在 repo 中探索、跑測試、修改工具或處理罕見事件？
  → openai-codex
```

對本系統的建議分工：

```text
正式 coredump 根因分析
  → openai + Responses API

分析完成後的協作流程
  → openai-agents
     - Issue 建立或更新
     - 相似事件與既有知識查詢
     - 修復建議、測試清單、通知與文件整理

罕見 crash 與分析工具研發
  → openai-codex
     - 人工引導的 investigation
     - parser / symbol 工具 / 測試改善
     - 大型 repo 的變更與 regression 研究
```

一個實用門檻是：當系統出現兩個以上職責明確的 agent，且該流程不要求逐 token、逐工具呼叫的硬性成本控制，例如「分析完成後的 Issue 分流與知識整理」，才適合加入 `openai-agents`。需要讀取 repo、操作開發工具並由工程師審視結果時，才適合使用 `openai-codex`。

### 漸進導入順序

```text
1. 用互動式 Codex 驗證 gdb 指令、prompt 與報告格式。
2. 以 openai SDK 完成最小 production loop：3 個唯讀工具、單次模型呼叫、JSON 報告。
3. 加入 fingerprint 去重、artifact cache 與 CaseBudget。
4. 加入 queue、深度分析升級、人類核准、trace 與固定案例評測。
5. 在需要時以 openai-agents 建立實驗性或標準化的子流程；不取代正式控制層。
```

## 官方參考資料

1. OpenAI Agents SDK quickstart: <https://developers.openai.com/api/docs/guides/agents/quickstart>
2. OpenAI Agents SDK overview: <https://developers.openai.com/api/docs/guides/agents>
3. OpenAI tools and function calling: <https://developers.openai.com/api/docs/guides/tools>
4. OpenAI prompt caching: <https://developers.openai.com/api/docs/guides/prompt-caching>
5. OpenAI agent evaluations: <https://developers.openai.com/api/docs/guides/agent-evals>
6. Codex Python SDK: <https://github.com/openai/codex/tree/main/sdk/python>
7. Codex non-interactive mode: <https://learn.chatgpt.com/docs/non-interactive-mode.md>
