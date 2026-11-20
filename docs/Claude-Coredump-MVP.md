# Claude coredump parser：最小實作計畫（階段 0 到 2）

> 資料日期：2026-11-20  
> 範圍：用 Python 加 Claude SDK 開發 coredump auto parser 時，**第一個要驗證可行性的最小版本**怎麼做：案例集、階段 1（Claude Code 互動驗證）、階段 2（Python ＋ Messages API 最小版本）、評測、驗收與決策。不含佇列、Jira、n8n、去重與深度分析；那些見 [Claude-Coredump-Agent](Claude-Coredump-Agent.md) 第 9–10 節。  
> 讀法：**【官方】** 取自本庫已整理的 Claude 官方資料（[Claude-Code-CLI](Claude-Code-CLI.md)）；**【本庫設計】** 取自 [OpenAI-Python-Agent](OpenAI-Python-Agent.md)（同類系統的設計，寫給 OpenAI，原則與模型廠商無關）；**【建議】** 是我的歸納；**【推論】** 是類推，沒有直接依據。  
> ⚠️ **我沒有實作過這個計畫**；**這次沒有開啟任何官方頁面**；工具名稱、欄位與數字都是設計用的示意。**本文不給準確率門檻的數字**，因為我沒有你們的資料，門檻要由你們與值班人員一起定。

## 先看結論

- **目標**：用兩個階段、小範圍證明「模型根據工具證據判讀 coredump」可行，再決定要不要投入完整系統（【建議】）。
- **階段 1**：用 **Claude Code 互動驗證**，人在迴圈。產出：固定的 `gdb` 指令集、prompt 初稿、報告 schema、失敗模式記錄，並量出每案大約多少 token 與成本。
- **階段 2**：用 **Python ＋ Messages API** 做最小版本：**3 個唯讀工具**、`CaseBudget`、JSON 報告、評測 harness。它是一支**命令列程式，不是服務**。
- **兩個閘門**：閘門 1 決定能不能進階段 2；閘門 2 看評測結果決定怎麼往下走（第 6 節）。
- **不做**：佇列、Jira、n8n、fingerprint 去重、深度分析、多 agent、向量搜尋。
- **最容易出錯的地方**：案例集只收已解決的容易案例，會高估準確率（【推論】）；dump 能不能外送沒先確認；評測沒有「無證據卻高信心」這個指標。

---

## 1. 計畫總覽

![圖：最小實作計畫：階段 0 準備案例集與環境，階段 1 用 Claude Code 互動驗證，閘門 1，階段 2 用 Python 加 Messages API 做最小版本，閘門 2，最後往薄服務與 Jira 整合](figures/claude-coredump-mvp-plan.svg)

| 階段 | 做什麼 | 產出 | 結束條件 |
|---|---|---|---|
| 0 準備 | 收集已知根因的案例、確認資料政策、準備隔離環境 | 案例集（先 10–20 個）、環境 | 案例有標註、dump 能否外送已確認 |
| 1 互動驗證 | 用 Claude Code 對案例逐一分析，人在迴圈 | `gdb` 指令集、prompt 初稿、報告 schema v0、失敗模式 | 閘門 1 |
| 2 最小版本 | Python ＋ Messages API，3 個唯讀工具 | 命令列程式、評測 harness、評測結果 | 閘門 2 |

本計畫**沒有工期估計**：我沒有你們的人力與案例數據，不編數字。

---

## 2. 階段 0：案例集與環境

![圖：案例集中一個案例的內容：core、binary 與 build-id、symbols、對應 commit 的 source、expected.json、notes.md，以及哪些給模型、哪些不能給](figures/claude-coredump-mvp-caseset.svg)

**案例集是整個計畫最重要的資產**：階段 1 用它找失敗模式，階段 2 用它評測，之後每次改 prompt 或模型也用它回歸。【本庫設計】目標是 **50–100 個已知 root cause 的案例**；階段 1 先用 10–20 個。

- **每個案例要有**：core、對應的 binary 與 build-id、符號、對應 commit 的 source，以及 `expected.json`（已知根因、證據、標註者）。
- **`expected.json` 絕對不能進 prompt 或被模型讀到**；評測才用它比對（【建議】）。
- **別只收已解決的容易案例**（【推論】）：真實流入的 crash 有很多符號不全、根因不明的情況；案例集若只有容易案例，準確率會被高估。**請刻意放進幾個困難與符號不全的案例**，並標註難度。
- **多樣性**：不同 signal、不同模組、單 thread 與多 thread、有無優化（`optimized out`）。
- **資料政策先確認**：dump 是記憶體快照，可能含客戶資料或機密。**在把任何案例送進 Claude 之前，先確認哪些可以外送**；階段 1 可以只用脫敏或可外送的案例（【建議】）。
- **環境**：專用 VM 或容器；不放 Jira 或其他系統的憑證；案例目錄以唯讀掛載（【本庫設計】的安全邊界）。階段 1 的 Claude Code 本身要連 Anthropic API，所以這個階段的隔離方式是「專用環境、無憑證、只放可外送的案例」，不是「無網路」；細節我沒查證。

---

## 3. 階段 1：用 Claude Code 互動驗證

**目的**：不寫程式，先弄清楚「模型需要什麼證據、`gdb` 要下哪些指令、輸出長什麼樣、哪些案例會失敗」。這些答案決定階段 2 的工具與 prompt（【本庫設計】的漸進導入第 1 步）。

### 3.1 做法（【建議】）

1. 挑 10–20 個案例，**難易混合**。
2. 在隔離環境的專案目錄開 Claude Code。把分析規則寫進 `CLAUDE.md`：區分事實與假設；每個結論要引用工具輸出；沒有證據不下結論；不要編造 frame 或變數值。`CLAUDE.md` 是文字指示，不保證被遵守（【官方】，見 [Claude-Context](Claude-Context.md)），所以輸出仍要人工核對。
3. 權限收緊到只允許 `gdb` batch 與讀檔。例如在 `permissions.allow` 放 `Bash(gdb -batch*)`；**pattern 的比對細節我沒逐一驗證**，寫好後請實際觸發一次確認有擋到（同 [Claude-React](Claude-React.md) 第 2.3 節的做法）。
4. 每案請它**只用 `gdb -batch` 取** backtrace、threads、registers，再判讀；**記錄它下過的每一個指令與輸出**。
5. 與 `expected.json` 比對，**把每個失敗歸類**（見 3.2）。
6. **量成本**：階段 1 後半，改用非互動模式批次跑案例（【官方】`claude -p` 的旗標）：

```bash
# 示意，沒有實際執行；--allowedTools 的 pattern 與 --json-schema 的參數形式請先驗證
claude -p "Analyze cases/case-001 using only gdb -batch. Return a JSON report." \
  --allowedTools "Read,Bash(gdb -batch*)" \
  --max-turns 8 --max-budget-usd 1 \
  --output-format json --json-schema report.schema.json \
  --no-session-persistence
```

【官方】`--output-format json` 的輸出含 `total_cost_usd`，可用來累加每案成本；`--max-turns` 與 `--max-budget-usd` 只在**單次執行內**生效。注意：**這個成本是 Claude Code 的，不等於階段 2 的成本**（【推論】）：Claude Code 有自己的 system prompt 與工具定義，階段 2 的 prompt 與證據更精簡，成本通常較低，但我沒有數據。

### 3.2 要產出什麼

| 產出 | 內容 |
|---|---|
| `gdb` 指令集（allowlist） | 哪些指令穩定取得 backtrace、threads、registers；各指令的 timeout 與輸出大小 |
| prompt 初稿 | 分析規則、輸出格式、禁用字眼（沒有證據不得說「已確認根因」） |
| 報告 schema v0 | 欄位見 4.4；先能被程式解析即可 |
| 失敗模式記錄 | 例如：符號缺失、`optimized out`、多 thread 競態、stack 被破壞、source 版本不符 |
| 成本範圍 | 每案 token 與成本的中位數與最大值 |

### 3.3 閘門 1：進階段 2 的條件（【建議】）

- [ ] 固定的 `gdb` 指令集，對案例集都能執行；**失敗的案例都有原因記錄**。
- [ ] 報告格式固定，且能區分事實與假設；schema v0 可被程式解析。
- [ ] 人工審閱過階段 1 的案例後，**主要失敗模式已歸類**。
- [ ] 已量出每案 token 與成本的範圍。
- [ ] dump 能否外送的政策已確認。

**沒過就留在階段 1**：修指令集與 prompt，再跑一輪。

---

## 4. 階段 2：Python ＋ Messages API 最小版本

### 4.1 架構

![圖：階段 2 的模組與資料流：run_case 讀案例，preprocess 產生 case_facts，orchestrator 迴圈受 CaseBudget 限制並呼叫三個唯讀工具與 Claude API，報告驗證 schema 後存檔，由評測 harness 與 expected.json 比對](figures/claude-coredump-mvp-arch.svg)

它是**一支命令列程式**：`run_case <案例目錄>` 讀案例、分析、寫出 `report.json`。**不做佇列、Jira、去重**；先證明分析本身可行。（可執行的範例程式碼，含 Jira 與 Claude 的實際呼叫，見 [Claude-Coredump-Code](Claude-Coredump-Code.md)；那份範例已包含 Jira 與佇列，階段 2 可只取其中的工具、預算、報告驗證與迴圈。）

建議的專案結構（【建議】）：

```text
coredump-parser/
  cases/                 # 案例集（每案一個目錄，見第 2 節）
  prompts/               # system.md、taxonomy.md（固定內容放前段）
  parser/
    preprocess.py        # 確定性程式：產生 case_facts.json
    tools.py             # 3 個唯讀工具（子行程＋timeout）
    budget.py            # CaseBudget
    agent.py             # 工具迴圈：呼叫 Claude、檢查預算與 allowlist
    schema.py            # 報告 schema 與驗證規則
    run_case.py          # 命令列入口
  eval/
    run_eval.py          # 逐案執行並比對 expected.json
    results/             # 每次評測的結果（含模型與 prompt 版本）
```

### 4.2 三個唯讀工具

![圖：六個工具中先做三個：extract_backtrace、resolve_symbols、search_repository；inspect_core 併入 preprocess、inspect_frame 暫不做、save_analysis 由 orchestrator 寫檔](figures/claude-coredump-mvp-tools.svg)

【本庫設計】先做**一個 agent 搭配少數工具**。我建議的取捨（【建議】）：

| 工具 | 輸入 | 輸出（JSON） | 限制（示意） | 失敗時 |
|---|---|---|---|---|
| `extract_backtrace` | case ID、thread ID（可選） | 標準化 frames：function、file、line、`evidence_id` | timeout 30 秒、最多 N 個 frames | 回傳 `{"error": "...", "retryable": false}` |
| `resolve_symbols` | build-id 列表 | 符號是否完整、symbol-set 版本、缺少項目 | timeout、下載量上限 | 回傳缺少項目，不要讓模型猜 |
| `search_repository` | query、revision | source 摘錄、blame、`evidence_id` | 只讀對應 commit、輸出大小上限 | 回傳「找不到」，不要編造 |

- **所有工具都唯讀，輸出一律是 JSON**，不回傳無限制的純文字（【本庫設計】）。
- 每個輸出帶一個 **`evidence_id`**，例如 `artifact://case/482/backtrace/thread-17.json`（格式示意）；模型的結論必須引用它。
- **工具是有 timeout 的子行程**，只允許事先定義的 `gdb`／`lldb` batch 命令，**不提供任意 shell**（【本庫設計】）。
- `inspect_core` 的資訊（signal、build-id、OS、架構）由 `preprocess` 以確定性程式產生，放進 `case_facts.json`；`inspect_frame`（區域變數與 registers）等第一輪證據不夠再加；`save_analysis` 由 orchestrator 直接寫檔。

【本庫設計】**若你們已有程式能穩定產出 full backtrace、registers、threads，就不需要讓模型直接操作 `gdb`**：由它先產生 `case_facts.json`，模型只解讀已取得的 artifact；工具可以更少。

### 4.3 預算

【本庫設計】預算由**外部程式強制**，不是靠 prompt 叫模型節省。初始範例（依真實資料調整）：

```python
CaseBudget(
    max_model_calls=2, max_tool_calls=8,
    max_input_tokens=20_000, max_output_tokens=2_000,
    max_debugger_seconds=90,
)
```

- 預算耗盡**不得無限重試**，回傳 `needs_human_or_deep_analysis`，並列出已驗證事實與缺少的證據。
- **思考 token**（【推論】）：Opus 5.5、Sonnet 5.5 無法關閉思考（【官方】，見 [Claude-Model](Claude-Model.md)），思考 token 預期以輸出計費；`max_output_tokens=2_000` 這種上限可能被思考吃掉，**階段 2 的預算要把思考算進去**，並用 `effort` 控制。成本細節見 [Claude-Coredump-Agent](Claude-Coredump-Agent.md) 第 6 節。
- 階段 2 的目的之一是**用案例集量出真實的每案 token**，再回頭調這些數字。

### 4.4 報告 schema 與驗證規則

【本庫設計】最終輸出用 JSON schema 驗證，至少包含：

```json
{
  "status": "resolved | needs_human_or_deep_analysis",
  "crash_signature": "...",
  "verified_facts": [{"fact": "...", "evidence_id": "..."}],
  "root_cause_hypotheses": [
    {
      "claim": "...",
      "confidence": "low | medium | high",
      "evidence_ids": ["artifact://..."],
      "counterevidence": ["..."]
    }
  ],
  "missing_evidence": ["..."],
  "recommended_next_action": "..."
}
```

**程式強制的驗證規則**（【建議】，用來落實「無證據不下結論」）：

1. `confidence` 為 `medium` 或 `high` 的假設，**至少要有一個 `evidence_id`**。
2. **每個 `evidence_id` 必須真的出現在本案的工具輸出裡**；模型編造的 ID 一律拒收。
3. `status` 為 `resolved` 時，至少要有一個 `medium` 以上且有證據的假設。
4. 不得出現「已確認根因」這類字眼，除非結論有可回查的 evidence ID（【本庫設計】）。
5. **驗證不過就不收**：重試一次（受預算限制），仍不過就回傳 `needs_human_or_deep_analysis`。

### 4.5 評測 harness

![圖：評測流程：案例集、run_eval 逐案呼叫 run_case、每案輸出、與 expected.json 比對，得到根因正確率、無證據高信心比例、成本耗時與失敗分類](figures/claude-coredump-mvp-eval.svg)

【本庫設計】持續評估這些指標：

| 指標 | 怎麼量 | 備註 |
|---|---|---|
| 根因 Top-1／Top-3 正確率 | 與 `expected.json` 比對（規則或人工） | 要分「有符號」與「符號不全」兩組看 |
| **無證據卻高信心的比例** | 驗證規則 1、2 能擋掉多少；漏網的人工抽查 | 目標是 0 |
| 每案成本、耗時、工具呼叫數 | 每案紀錄 | 看中位數與最大值，不只平均 |
| 失敗分類 | 證據不足／工具錯誤／判斷錯 | 決定下一步補工具還是改 prompt |
| 工具與 symbol 成功率 | 工具回傳 error 的比例 | 影響能不能自動化 |

- **每次評測都記錄模型版本、prompt 版本、工具版本**，結果存進 `eval/results/`（【本庫設計】）。換模型或改 prompt 之後，用同一個案例集回歸。
- 判定「正確」由誰做、標準是什麼（例如要寫出正確的函式還是正確的根因類別），**要先與值班人員講好**，否則數字沒有意義（【建議】）。

---

## 5. 驗收：閘門 2

**門檻由你們與值班人員一起定；本文不給數字**，因為我沒有你們的案件資料，任何數字都是編的。建議用下面的方式決定（【建議】）：

| 項目 | 怎麼定門檻 |
|---|---|
| 根因 Top-1／Top-3 | 與目前值班人員人工 triage 的準確率比較；也可以用「階段 1 人工加 Claude Code」當基準 |
| 無證據卻高信心 | **0**：由驗證規則強制，不是靠運氣 |
| 每案成本 | 不超過 `CaseBudget` 上限；低於人工 triage 一案的成本（你們自己的數字） |
| 耗時 | 與人工回應時間比較；不一定要即時 |
| 失敗案例 | 每個失敗都有歸類與原因，沒有「不知道為什麼」 |

---

## 6. 閘門 2 之後怎麼走

![圖：閘門 2 之後：準確率與成本不達標就查失敗模式並修正重跑；達標則看每日案件量，量小用薄服務加現有 worker，量大加去重、佇列與深度升級](figures/claude-coredump-mvp-gate.svg)

- **不達標**：先看失敗模式，**多半是證據或 prompt 的問題，不代表不可行**。證據不足就補工具（例如 `inspect_frame`）；判斷錯就改 prompt 或模型等級；案例本身不可行（符號缺失、dump 損毀）就記錄並排除。修正後用同一個案例集重跑。
- **達標、量小**：用薄服務加現有 worker 即可（[Claude-Coredump-Agent](Claude-Coredump-Agent.md) 第 9.3 節）。
- **達標、量大**：加 fingerprint 去重、佇列、深度升級（同文件第 10 節的階段 3–4）。「量大」沒有固定門檻，請用每日 core 數與值班負擔判斷。

---

## 7. 風險與注意事項（【建議】）

1. **案例集偏誤**：只收已解決的容易案例會高估準確率（【推論】）；請刻意放進困難案例。
2. **dump 外送**：沒確認政策就送案例，是最大的合規風險。
3. **符號不全**：符號不全時模型更容易「編」；用驗證規則 2 擋 evidence ID，並在報告中明確列出 `missing_evidence`。
4. **版本漂移**：模型、價格與 API 行為會更新（價格資料日期見 [Claude-Model](Claude-Model.md)）；每次評測都記錄版本，換版本前先回歸。
5. **階段 1 的成本不等於階段 2**：兩者 prompt 與工具定義不同，別直接拿階段 1 的數字做預算。
6. **評測標準不一致**：「正確」的定義要先講好，否則兩個人評同一案可能不同結果。
7. **不要為了過閘門而放寬規則**：例如為了提高「resolved」比例而允許無證據的結論，會讓系統看起來準、實際上不可信。

---

## 8. 驗證說明與限制

- 資料日期 2026-11-20。**我沒有實作過這個計畫**，程式碼與指令都沒有執行過。
- 內容取自本庫已整理的文件：[OpenAI-Python-Agent](OpenAI-Python-Agent.md)（工具集、報告 schema、預算、安全邊界、評測；寫給 OpenAI，我把原則類推到 Claude，類推部分是【推論】）、[Claude-Code-CLI](Claude-Code-CLI.md)（`claude -p` 的旗標與 `total_cost_usd`）、[Claude-Model](Claude-Model.md)、[Claude-Coredump-Agent](Claude-Coredump-Agent.md)。
- **這次沒有開啟任何官方頁面**。Claude Messages API 的工具呼叫格式、結構化輸出與 SDK 用法，我沒有查證；實作時請以 Anthropic 官方文件為準。
- **`--allowedTools` 的 pattern 比對、`--json-schema` 的參數形式、Claude Code 的 `permissions.allow` 寫法細節**，我沒逐一驗證。
- 工具名稱、欄位、`evidence_id` 格式、timeout 與數字都是示意，請依你們的環境調整。
- **沒有給準確率門檻、工期或人力估計**：我沒有你們的資料。

---

## 9. 參考

- 本庫：[Claude-Coredump-Agent](Claude-Coredump-Agent.md)（工具選型、成本、Jira 整合、導入順序）、[OpenAI-Python-Agent](OpenAI-Python-Agent.md)（同類系統的完整設計，含工具集、報告 schema、預算、安全邊界、評測）、[Claude-Code-CLI](Claude-Code-CLI.md)、[Claude-Model](Claude-Model.md)、[Claude-Context](Claude-Context.md)。
