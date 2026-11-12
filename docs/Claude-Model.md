# Claude 模型差異分析：Sonnet / Opus / Fable

> 資料快取時間：2026-10-06（來源：Anthropic `claude-api` skill 模型目錄；目錄未提供的項目標註「未驗證」）

> 2026-11-12 新增 8 張圖示（價格與情境、選型流程、家族 API 能力、思考機制矩陣、Extended 與 Adaptive 差異、refusal 回退流程、Fable 長文優勢、破壞性變更）；圖中內容皆整理自本文既有資料，未更新數值，仍以 2026-10-06 資料為準。

## 1. 總覽表

| 模型 | Model ID | 情境窗口 (Context) | 最大輸出 | 輸入價格 / 1M tokens | 輸出價格 / 1M tokens |
|---|---|---|---|---|---|
| Claude Fable 5.1 | `claude-fable-5-1` | 1M（預設即上限） | 128K | $10.00 | $50.00 |
| Claude Mythos 5.1（僅限 Project Glasswing） | `claude-mythos-5-1` | 1M | 128K | $10.00 | $50.00 |
| Claude Fable 5 | `claude-fable-5` | 1M | 128K | $10.00 | $50.00 |
| Claude Opus 5.5 | `claude-opus-5-5` | 1M | 128K | $4.00 | $20.00 |
| Claude Opus 5 | `claude-opus-5` | 1M | 128K | $5.00 | $25.00 |
| Claude Opus 4.8 | `claude-opus-4-8` | 1M | 128K | $5.00 | $25.00 |
| Claude Opus 4.7 | `claude-opus-4-7` | 1M | 128K | $5.00 | $25.00 |
| Claude Opus 4.6 | `claude-opus-4-6` | 1M | 128K | $5.00 | $25.00 |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 1M | 128K | $2.00 | $10.00 |
| Claude Sonnet 5 | `claude-sonnet-5` | 1M | 128K | $2.00 | $10.00 |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M | 128K | $3.00 | $15.00 |
| Claude Haiku 5.5 | `claude-haiku-5-5` | 1M | 128K | $0.10（prompt 超過 100K 為 $0.50） | $0.50（超過 100K 為 $2.50） |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200K | 64K | $1.00 | $5.00 |

> 註：Fable 系列定價高於 Opus，屬「最高階、最貴」層級；**Opus 5.5（`claude-opus-5-5`）為目前建議的預設模型**；Sonnet 5.5 是性價比選項；Haiku 5.5 價格最低。最大輸出方面，除 Haiku 4.5（64K）外，現行模型皆為 128K。前代的 Claude Mythos 5 未列於目前的模型目錄，已從表中移除。

![圖：現行 Claude 模型的價格與情境窗口。Opus 5.5 為預設推薦；Haiku 4.5 是唯一較小情境的模型](figures/claude-model-lineup.svg)

---

## 2. Claude Fable 5.1（`claude-fable-5-1`）與 Fable 5（`claude-fable-5`）— 目前最強大的公開發行模型

定位：用於最高難度的推理與長時程 (long-horizon) 代理型 (agentic) 工作。1M 情境窗口為預設值也是上限，最大輸出 128K。

**與 Opus 系列的關鍵 API 差異：**

- **思考功能永遠開啟**：`thinking` 參數應完全省略（或明確傳入 `{type: "adaptive"}`）。若明確傳入 `{type: "disabled"}` 或 `{type: "enabled", budget_tokens: N}` 皆會回傳 400 錯誤。可透過 `output_config.effort`（`low` 至 `xhigh`、`max`）控制思考深度。
- **原始思考鏈永不回傳**：回應中會有一般的 `thinking` 區塊（非 `redacted_thinking`）。`display: "summarized"` 會回傳可讀摘要；預設值 `"omitted"` 則會將 `thinking` 欄位留空字串。
  - Replay 規則：同一模型必須原樣傳回 thinking 區塊（包含空文字區塊）——API 只拒絕「被修改」的區塊，讀取後原樣傳回沒問題。
  - 換成**不同模型**時，thinking 區塊會被靜默捨棄（不算入計費，也不會出錯）。
  - 其他模型產生的一般 thinking 區塊，可以自由跨模型重播。
- **Tokenizer**：與 Opus 4.8 相同（自 Opus 4.7 起沿用）。從 Opus 4.7/4.8 遷移時 token 數大致不變，但單位價格不同；若從 Opus 4.6、Sonnet 或 Haiku 等舊模型遷移，需重新用 `count_tokens` 校準。
- **`refusal` stop reason（拒絕原因）— 必須處理，且預設應啟用容錯回退**：
  - 安全分類器可能拒絕請求（HTTP 200，`stop_reason: "refusal"`，並附帶 `stop_details` 分類）。
  - 輸出前即被拒絕：`content` 為空陣列，完全不計費。
  - 串流中途被拒絕：已串流輸出部分會計費，需捨棄該部分內容。
  - 務必在讀取 `content` 前先檢查 `stop_reason`。
  - 復原機制屬於**選擇加入 (opt-in)**：多數 Claude 消費端介面內建 Opus 4.8 回退機制，但直接呼叫 API 若未主動啟用，遇到拒絕就會直接停止——而安全性工具、生命科學等敏感但合法的任務，確實會出現誤判 (false positive)。
  - **撰寫 `claude-fable-5` 程式碼時，建議預設加入伺服器端 `fallbacks` 參數**：`betas: ["server-side-fallback-2026-06-01"]` + `fallbacks: [{"model": "claude-opus-4-8"}]`（適用於 Claude API 與 Claude Platform on AWS）。被拒絕的請求會在同一次呼叫中，透明地由回退模型重新產生結果，並自動套用類似退款的重新計費規則（輸出前拒絕不計費；由回退模型產生的內容按回退模型自身費率計費）。
  - 在 Amazon Bedrock、Vertex AI、Microsoft Foundry 等不支援伺服器端回退的平台，可改用 GA SDK 內建的用戶端 `BetaRefusalFallbackMiddleware` + `BetaFallbackState` 進行重試。
  - 較新的簡化寫法：`betas: ["server-side-fallback-2026-07-01"]` + `fallbacks: "default"`，依拒絕類別自動路由，不必維護模型清單（上方陣列形式仍可用）。

![圖：Fable 請求被安全分類器拒絕後的處理流程與三種回退路徑](figures/claude-model-refusal-flow.svg)

**使用時機**：需要最頂尖推理能力、長時程自主代理任務，且能接受較高成本與需要處理 `refusal` 邏輯時。

**Fable 5.1（`claude-fable-5-1`）相對 Fable 5 的變更**（同價位；Fable 5 仍可使用）：

- **強制 `tool_choice` 會回 400**：`{type:"any"}` 與 `{type:"tool", name:...}` 皆不可用。改用 `auto` 加 prompt 指示、`strict: true`，或用 structured outputs。`none` 不受影響。
- **thinking block 綁定產生它的模型**：其他模型會（不計費地）捨棄這些區塊。
- **編輯歷史會使先前 thinking block 失效（preserved thinking）**：2026-08-31 起建立的新帳號，送出編輯過的歷史在所有平台回 400；Mythos 5.1 則任何帳號預設如此。harness 需改為 append-only。
- **新增 beta 功能**：每則訊息可調 `effort`（`mid-conversation-output-config-2026-07-01`，Opus 5 / 5.5 也支援）、`clear_at: "next_user_message"` 系統訊息（`mid-conversation-system-clear-at-2026-08-21`）、`thinking.display: "updates"` 進度摘要（`thinking-display-updates-2026-08-18`）。Cache 讀取價 $0.25 / MTok。
- **Covered Model**：與 Fable 5 相同，ZDR 組織會回 400；不支援 Priority Tier。

**官方安全機制（來源：Anthropic 官方發佈頁與 System Card）：**

- Fable 5 專屬三種分類器安全防護：**網路安全**（攻擊性網路任務會被封鎖並可回退至 Opus 4.8）、**生物/化學**（涵蓋雙用途生物研究相關查詢）、**蒸餾防護**（防止他人藉由大量查詢萃取模型能力）。
- 官方數據：**95% 以上的 Fable 5 對話完全不會觸發任何回退機制**（即誤判率很低）。
- 外部紅隊測試與抓漏懸賞（bug bounty）超過 1000 小時測試，**未發現長時程代理任務上的通用型 jailbreak**。
- Mythos-class 模型（Fable 5 / Mythos 5）強制 30 天資料保留，且資料僅用於安全目的。

**為何說 Fable 5 提升「長文/長時程推理能力」？（重點：不是 context window 變大）**

Fable 5 的 1M context window 與 Opus/Sonnet **完全相同**，並沒有變大。官方說法明確指出，提升來自「有效使用 context 的能力」，而非「視窗尺寸」：

- **有效檢索深度優於原始長度**：Anthropic 官方表示 Mythos-class 模型的優化目標是「能否從很深的 context 裡準確檢索到需要的資訊」，這比單純的 token 上限更關鍵——避免舊模型在長 context 中出現「context rot」（愈後面的內容愈容易被忽略或誤用）。
- **長時程自主性 (long-horizon autonomy) 實測提升**：可維持多天、目標導向的連續執行，且對初始指令的記憶/遵循度更強；在 SWE-bench Verified 上，**需理解多個互相關聯檔案**的題目分數明顯優於 Opus 4.8——這類題目的瓶頸正是 context 管理能力，不是單題推理難度。
- **長步驟鏈的穩定度更高**：在需連續執行 20–50 步、且中途不能靠人工糾正的任務鏈上，完成率更高、需要回滾（rollback）的中途錯誤更少。
- **首發支援的長 context 管理工具**（讓「有限視窗」用得更久、更有效率，而非視窗本身變大）：
  - **Memory tool**：可跨 session 持久化重點資訊
  - **Compaction**：自動壓縮過長的對話歷史
  - **Context editing / tool result clearing**：主動清除不再需要的工具呼叫結果，釋放空間給新資訊

![圖：Fable 與 Opus、Sonnet 的視窗尺寸相同，差別在有效使用 context 的能力](figures/claude-model-fable-longctx.svg)

**結論**：Fable 5 的長文優勢是「使用 1M window 的效率與穩定度」提升，不是「視窗本身變大」——這也解釋了為何前面提到 Fable 5 的最大輸出（128K）跟 Opus/Sonnet 一樣，並沒有因為「長文能力強」而有更大的輸出上限。

---

## 3. Claude Opus 系列（4.6 / 4.7 / 4.8 / 5 / 5.5）— 目前建議的預設模型為 Opus 5.5

`claude-opus-5-5`、`claude-opus-5`、`claude-opus-4-8`、`claude-opus-4-7`、`claude-opus-4-6`，情境窗口皆為 1M。Opus 5.5 定價 $4 / $20，其餘為 $5 / $25（每 1M tokens）。

**關鍵特性：**

- **Opus 5.5（`claude-opus-5-5`）— 目前的 Opus 與預設模型**：Opus 5 的後繼，$4 / $20（cache 讀取 $0.20），1M 情境 / 128K 輸出，tokenizer 與功能集同 Opus 5。相對 Opus 5 的破壞性變更：
  - **thinking 不能關閉**：`{type:"disabled"}` 與 `budget_tokens` 在任何 effort 都回 400；`effort` 預設為 **`medium`**（Opus 5 為 `high`），建議明確設定。
  - **強制 `tool_choice` 回 400**（改用 `auto` + `strict: true` 或 structured outputs）。
  - **thinking block 綁定模型與對話**（preserved thinking）；2026-08-31 起建立的帳號會檢查歷史編輯。
  - **computer use 在 Claude API 與 Google Cloud 只能用 `computer_toolset_20260801`**（`computer_20251124` 會 400；Amazon Bedrock 仍接受舊版）。
  - 工具呼叫之間的文字以 progress-update `thinking` 區塊回傳（預設為空，需設 `display: "updates"`）。
  - Fast Mode 僅限 Claude API，$8 / $40。
- **Opus 5（`claude-opus-5`）**：$5 / $25，thinking 預設為 adaptive；`{type:"disabled"}` 僅在 effort 為 `high` 以下時接受（`xhigh` / `max` 回 400）；`budget_tokens` 與 sampling 參數回 400；`effort` 預設 `high`。
- **建議一律使用 `claude-opus-5-5`**，除非使用者明確指定其他模型（例如明確說「用 sonnet」或「用 haiku」）。不應為了省成本而自行降級，這是使用者的決定權。
- **Extended Thinking vs Adaptive Thinking（官方文件明確區分兩者，非同一機制）**：
  - **Opus 4.8**：只支援 Adaptive Thinking（`thinking: {type: "adaptive"}`），**不支援**舊式 Extended Thinking／`budget_tokens`（會被 400 拒絕）。`effort` 參數在所有介面（API、Claude Code、claude.ai）**預設值為 `high`**。
  - **Opus 4.7**：同樣只支援 Adaptive Thinking，不支援 Extended Thinking。
  - **Opus 4.6**：**兩者都支援**——Extended Thinking（`budget_tokens`，已標示 deprecated 但仍可用）與 Adaptive Thinking 皆可用。
- **`output_config.effort`**：可設定 `low` / `medium` / `high` / `xhigh` / `max`，控制推理深度與延遲/成本的取捨。
- **Fast Mode**：僅 Opus 5.5 / 5 / 4.8 支援，且僅限 Claude API（Opus 4.7 的 fast mode 已移除，傳 `speed: "fast"` 會報錯）。價格為標準價的 2 倍（Opus 5 為 $10 / $50，Opus 5.5 為 $8 / $40）；模型本身不降級，只是加速輸出。
- **對話中途系統訊息 (mid-conversation system message)**：Opus 5.5 / 5 / 4.8、Fable 5 / 5.1、Sonnet 5.5、Haiku 5.5 支援（Sonnet 5 不支援），無需 beta header，可在對話進行中插入系統層級指令而不破壞 cache 前綴。
- **Task Budgets（beta）**：支援 Opus 5.5 / 5 / 4.8 / 4.7、Fable 5 / 5.1、Sonnet 5.5、Haiku 5.5（Sonnet 5 不支援）；用於限制單次 agentic 任務的 token 上限。
- **Batch API 擴充輸出（beta）**：Opus 4.8 / 4.7 / 4.6 與 Sonnet 5 / 4.6 在 Message Batches API 上，加上 `output-300k-2026-03-24` beta header 後，最大輸出可提升至 **300K tokens**（同步 Messages API 仍是 128K 上限）。
- **知識截止日期**：Opus 4.8 可靠知識截止於 **2026 年 1 月**，訓練資料截止同為 2026 年 1 月。

**使用時機**：絕大多數程式開發、複雜推理、代理型工作的預設選擇；除非使用者特別要求，否則應優先使用。

---

## 4. Claude Sonnet 系列（4.6 / 5 / 5.5）— 性價比選項

`claude-sonnet-5-5`、`claude-sonnet-5`、`claude-sonnet-4-6`，情境窗口 1M。

- **Sonnet 5**：定價 $2 / $10（每 1M tokens 輸入/輸出）。採用新版 tokenizer（與舊版 Sonnet/Haiku 不同，遷移時需重新校準 token 計數）。只支援 Adaptive Thinking，**不支援**舊式 Extended Thinking；`effort` 在 API 與 Claude Code 上預設值為 `high`。可靠知識截止於 2026 年 1 月。不支援對話中途系統訊息與 Task Budgets。
- **Sonnet 5.5（`claude-sonnet-5-5`）— 目前的 Sonnet**：同價 $2 / $10（cache 讀取 $0.20）、同 tokenizer、1M 情境 / 128K 輸出。相對 Sonnet 5 的破壞性變更：
  - `thinking: {type:"disabled"}` 回 400；要關閉思考請改傳 `{type:"between_tools"}`（僅限 effort `high` 以下、不可附帶其他欄位、不能中途變更 effort）。
  - 強制 `tool_choice`（`any` / 指定工具）回 400。
  - thinking block 綁定模型與對話（preserved thinking）。
  - computer use 在 Claude API 與 Google Cloud 只能用 `computer_toolset_20260801`。
  - advisor tool 不接受 Opus 4.8、Opus 4.7、Sonnet 5 作為 advisor。
  - `effort` 預設仍為 `high`，但各級別已重新校準，建議重跑 effort 比較（agentic coding 與多步驟工具使用從 `medium` 起，一般聊天從 `low` 起）。
- **Sonnet 4.6**：定價 $3 / $15，Extended Thinking 與 Adaptive Thinking **兩者皆支援**（`budget_tokens` 已標示 deprecated 但仍可用）。可靠知識截止於 2025 年 8 月。

![圖：Fable 5.1、Opus 5.5、Sonnet 5.5 相對前一版的破壞性變更對照](figures/claude-model-breaking-changes.svg)

**使用時機**：當使用者明確要求「用 sonnet」，或在成本敏感、任務複雜度中等的情境下，作為 Opus 的平價替代方案。

> 補充：**Haiku 5.5**（`claude-haiku-5-5`，1M 情境、128K 輸出，$0.10 / $0.50，prompt 超過 100K 為 $0.50 / $2.50）支援 Adaptive Thinking（預設開啟，`effort` 預設 `medium`；`disabled` 僅在 `high` 以下接受），`budget_tokens` 與非預設 sampling 值皆回 400，且沒有 server-side refusal fallback。**Haiku 4.5** 則仍是現行模型中唯一保留 `budget_tokens` 傳統思考、且不支援 Adaptive Thinking 的模型，可靠知識截止於 2025 年 2 月。

**Opus 4.8 對比 Sonnet 5，推理優勢具體強在哪？（官方說法 + 第三方基準彙整）**

> ⚠️ 以下為 Opus 4.8 對 Sonnet 5 的舊世代比較（資料日期 2026-06），**不適用於 Opus 5.5 / Sonnet 5.5**；目前的模型目錄沒有新世代的對應數據（未驗證）。

差距集中在「困難／開放式」任務，而非全面壓制；結構清楚、有工具輔助的日常任務兩者已非常接近。

- **規劃與工具呼叫準確度（官方明確指出）**：Opus 讀取參數 schema 更準確、更懂得「該不該呼叫工具」而非硬套，規劃多步驟任務時更能抓出步驟間依賴、減少多餘動作。Sonnet 5 在結構清楚、文件完整的任務上表現穩定，但遇到需要自行規劃、從錯誤中恢復的開放式任務容易卡住。
- **不靠工具的純推理，Opus 領先較明顯；給工具後差距幾乎消失**（第三方基準彙整，非官方數字）：Humanity's Last Exam 不用工具時 Opus 4.8 約 49.8% vs Sonnet 5 約 43.2%；給工具後 Sonnet 5 追到約 57.4%，與 Opus 4.8 的 57.9% 幾乎打平。
- **困難、多檔案的程式碼理解，Opus 仍明顯領先**：SWE-bench Pro 上 Opus 4.8 約 69.2% vs Sonnet 5 約 63.2%，差距在需要理解多個互相關聯檔案的困難題上更明顯（與 Fable 5 的「長 context 有效檢索」屬同一類能力）。
- **網路安全（cybersecurity）任務，官方明確承認差距大**：Anthropic 官方原話：Sonnet 5「執行網路安全任務的能力明顯低於目前的 Opus 系列模型」；Firefox 漏洞開發測試中，Sonnet 系列未能做出可用 exploit，Opus 4.8 明顯更強。
- **反例——知識型工作 Sonnet 5 已小贏**：GDPval-AA v2（知識工作基準）Sonnet 5 約 1618 分、Opus 4.8 約 1615 分，官方稱這是「Sonnet 級模型首次在任一基準上超越同期 Opus 旗艦」。
- **成本考量的反直覺點**：Sonnet 5 當時單價便宜約 40%（現價 $2 對 Opus 4.8 的 $5，價差已擴大為約 60%），但因「更努力」（在高 effort 下輸出 token 更多、agentic 任務所需回合數更多），實際單次任務總花費有時反而比 Opus 4.8 更高——不能只看每 token 單價判斷成本。

**結論**：Opus 的推理優勢集中在開放式規劃、多檔案長程程式碼、無工具純推理、網路安全深度技術這幾類困難/高風險任務；一般結構清楚、有工具輔助的日常任務，Sonnet 5 已非常接近，甚至偶爾反超。

---

## 5. 三大模型家族快速比較

| 面向 | Fable 5 / 5.1 | Opus 系列 (4.6–5.5) | Sonnet 系列 (4.6 / 5 / 5.5) |
|---|---|---|---|
| 定位 | 最強推理 + 長時程代理 | 目前預設推薦模型（Opus 5.5） | 性價比選項（Sonnet 5.5） |
| 價格層級 | 最高（$10/$50） | 中高（5.5 為 $4/$20，其餘 $5/$25） | 中低（5 / 5.5 為 $2/$10，4.6 為 $3/$15） |
| 思考模式 | 永遠開啟，僅可調 effort，不可關閉 | Adaptive Thinking；Opus 5.5 不可關閉（effort 預設 `medium`）；`budget_tokens` 僅 4.6 仍可用 | Sonnet 5 / 5.5 只支援 adaptive；5.5 以 `between_tools` 取代 `disabled` |
| 思考鏈可見性 | 一般 thinking 區塊，可摘要或省略 | 依模型版本而定 | 依模型版本而定 |
| 特殊錯誤處理 | 需處理 `refusal` stop reason，建議啟用 server-side fallback | Opus 5.5 / 5 同樣建議啟用 fallback；4.x 未列此機制 | Sonnet 5.5 同樣建議啟用（僅 `"default"` 形式、僅 Claude API）；其餘未列 |
| 資料保留要求 | 需 30 天資料保留，與 ZDR（零資料保留）不相容 | 依方案彈性設定 | 依方案彈性設定 |
| Fast Mode | 不支援 | Opus 5.5 / 5 / 4.8 支援（僅 Claude API） | 不支援 |
| 對話中途系統訊息 | 支援 | Opus 5.5 / 5 / 4.8 支援 | 僅 Sonnet 5.5 支援（Sonnet 5 不支援） |
| 強制 `tool_choice`（`any` / 指定工具） | Fable 5.1 回 400 | Opus 5.5 回 400 | Sonnet 5.5 回 400 |
| Priority Tier | Fable 5 支援；Fable 5.1 不支援 | Opus 5.5 / 5 不支援；4.8 支援 | Sonnet 5 / 5.5 不支援 |
| 建議使用情境 | 使用者明確要求 Fable / 最高難度任務 | 預設選擇（`claude-opus-5-5`），除非使用者另有指示 | 使用者明確要求 sonnet（現行為 5.5），或成本敏感場景 |

![圖：Fable 5.1、Opus 5.5、Sonnet 5.5 的 API 能力比較](figures/claude-model-family.svg)

---

## 6. 推理階段（Inference）差異總覽

訓練規模與資料決定「模型能力上限」（Anthropic 未公開參數量、算力等細節），但實際呼叫 API 時，**下列推理層的機制差異才是真正影響程式碼寫法、成本與延遲的部分**——這些是產品設計上的開關，不完全跟著模型大小走。

**Context Window 並非全部一樣：**

| 面向 | Fable 5 / 5.1 | Opus 5.5/5/4.8/4.7/4.6 | Sonnet 5.5/5/4.6 | Haiku 5.5 | Haiku 4.5 |
|---|---|---|---|---|---|
| Context Window | 1M | 1M | 1M | 1M | **200K**（唯一較小者） |
| 最大輸出（同步 API） | 128K | 128K | 128K | 128K | **64K**（唯一較小者） |
| 最大輸出（Batch API + beta header） | 不支援此 beta | **300K**（Opus 5.5 / 5 未驗證） | **300K**（Sonnet 5.5 未驗證） | 未驗證 | 不適用（本身較小） |

**思考機制種類（Extended Thinking vs Adaptive Thinking，官方視為兩種不同機制，非升級關係）：**

| 模型 | Extended Thinking（舊式 `budget_tokens`） | Adaptive Thinking（`{type:"adaptive"}`） |
|---|---|---|
| Fable 5 / 5.1 | ❌ 明確禁止，會 400 | ✅ 永遠開啟，無法關閉 |
| Opus 5.5 | ❌ | ✅（不可關閉；`effort` 預設 `medium`） |
| Opus 5 | ❌ | ✅（預設開啟；`disabled` 僅 effort `high` 以下） |
| Opus 4.8 | ❌ | ✅（`effort` 預設 `high`） |
| Opus 4.7 | ❌ | ✅ |
| Opus 4.6 | ✅（deprecated 但可用） | ✅ |
| Sonnet 5.5 | ❌ | ✅（`effort` 預設 `high`；`disabled` 回 400，改用 `between_tools`） |
| Sonnet 5 | ❌ | ✅（`effort` 預設 `high`） |
| Sonnet 4.6 | ✅（deprecated 但可用） | ✅ |
| Haiku 5.5 | ❌ | ✅（預設開啟，`effort` 預設 `medium`） |
| Haiku 4.5 | ✅（現行模型中唯一僅靠此機制） | ❌ 不支援 |

![圖：各模型支援 Extended Thinking 與 Adaptive Thinking 的矩陣](figures/claude-model-thinking-matrix.svg)

> 可以看出：新一代（Opus 5.5 / 5 / 4.8 / 4.7、Sonnet 5.5 / 5、Haiku 5.5）都已拿掉舊式 `budget_tokens`，只留 Adaptive；4.6 世代是新舊並存的過渡期；Haiku 4.5 是現行模型中唯一仍停留在舊機制的。另外，自 2026-10-21 起，任何模型的 Messages 請求只要帶 `temperature`、`top_p` 或 `top_k` 都會回 400。

**Adaptive Thinking 與 Extended Thinking 的機制本身差在哪（不只是支援名單不同）：**

| 面向 | Extended Thinking（`type:"enabled"` + `budget_tokens`） | Adaptive Thinking（`type:"adaptive"`） |
|---|---|---|
| 控制方式 | 你手動指定思考 token 的**硬性上限**（`budget_tokens`），且必須 `< max_tokens` | 模型自己判斷「要不要思考」「思考多少」，你只用 `effort` 做**軟性引導**，非硬上限 |
| 調節旋鈕 | 單一數字（token 數） | 5 段 `effort`：`low`／`medium`／`high`（預設）／`xhigh`／`max` |
| 簡單問題的行為 | 即使問題很簡單，仍會依你設定的 budget 硬性思考 | `effort` 較低時可直接跳過思考；`high`/`max` 幾乎必思考 |
| 交錯思考（工具呼叫間思考） | Sonnet 4.6 需額外加 `interleaved-thinking-2025-05-14` beta header 才有；Opus 4.6 **完全不支援**（若需要工具呼叫間思考只能改用 adaptive） | **自動啟用**，工具呼叫之間可以插入思考，天生適合 agentic 工作流 |
| 多輪對話驗證規則 | API 強制規定：有思考的 assistant 回合**必須**以 thinking 區塊開頭 | 較寬鬆：前面的 assistant 回合不需要以 thinking 區塊開頭 |
| `tool_choice` 限制 | 思考開啟時只能用 `auto` 或 `none`，**不能**指定特定工具（`any` 或 `{type:"tool", name:...}` 皆不可） | 官方文件未列出此限制 |
| 思考模式中途切換 | 同一個 assistant 回合內**不能**切換思考開/關 | 同上規則仍適用，但因模型自行決定深度，實務上較少遇到需要中途切換的情境 |
| Prompt Cache 影響 | 與 adaptive 互相切換會打斷 cache breakpoint | 連續使用 adaptive 可維持 cache breakpoint；但切去 `enabled`/`disabled` 一樣會打斷 |
| 計費方式 | 依實際產生的思考 token 計費（不管 `budget_tokens` 設多少，只計真正用掉的量，但不能超過上限） | 依實際產生的思考 token 計費——**計費機制完全相同**，差異只在「誰決定要不要思考」 |
| 目前支援模型 | 僅 Opus 4.6 / Sonnet 4.6（deprecated，仍可用）、Haiku 4.5、更舊的 Opus/Sonnet | Fable 5 / 5.1 / Mythos 5 / 5.1（永遠開啟）、Opus 5.5 / 5 / 4.8 / 4.7 / 4.6、Sonnet 5.5 / 5 / 4.6、Haiku 5.5 |

![圖：Extended Thinking 與 Adaptive Thinking 的機制差異](figures/claude-model-ext-vs-adaptive.svg)

> 一句話總結：Extended Thinking 是「你告訴模型能想多久」；Adaptive Thinking 是「你告訴模型想深入到什麼程度，模型自己決定要不要想、想多久」。兩者計費邏輯相同，差別在**控制權在誰手上**，以及 adaptive 額外自帶「工具呼叫間思考」與較寬鬆的多輪驗證規則。

**其他推理層差異：**

- **官方延遲分級（comparative latency，同一家族內設計取向，不是同顆模型跑法不同）**：Fable 5（最慢）→ Opus 4.8（中等）→ Sonnet 5（快）→ Haiku 4.5（最快）。（此排名為舊資料；Fable 5.1 / Opus 5.5 / Sonnet 5.5 / Haiku 5.5 的延遲排名目錄未提供，未驗證。）
- **Tokenizer 版本不同**：Fable 5 / 5.1 與 Opus 4.7/4.8 共用同一版，比舊模型多產生約 30% token；Sonnet 5 / 5.5 共用另一套新版；Opus 5.5 與 Opus 5 相同；跨版本遷移都需要用 `count_tokens` 重新校準，而非直接假設 token 數不變。
- **`refusal` 安全回退機制**：Fable 5 / 5.1 與 Mythos 5 / 5.1 有安全分類器與伺服器端 fallback；Opus 5.5 / 5 與 Sonnet 5.5 也可能回 `refusal`（`stop_details` 類別如 `cyber`、`bio`、`reasoning_extraction`、`frontier_llm`、`general_harms`），建議同樣啟用 `fallbacks`；Haiku 5.5 沒有 server-side fallback；舊世代模型未列此機制。
- **Fast Mode**：僅 Opus 5.5 / 5 / 4.8（Claude API），其他模型不支援；Opus 4.7 已移除。
- **對話中途系統訊息**：Opus 5.5 / 5 / 4.8、Fable 5 / 5.1、Sonnet 5.5、Haiku 5.5 支援；Sonnet 5 不支援。
- **強制資料保留**：Fable 5 / 5.1 與 Mythos 5 / 5.1 要求 30 天保留，與 ZDR 不相容；其他模型依方案彈性設定。
- **知識截止日期**（推理時模型「知道多少」，也是訓練面但直接影響推理輸出正確性）：Fable 5/Opus 4.8/Sonnet 5 都是 2026 年 1 月；Opus 4.6 為 2025 年 5 月；Sonnet 4.6 為 2025 年 8 月；Haiku 4.5 最舊，2025 年 2 月。Fable 5.1、Opus 5.5 / 5、Sonnet 5.5、Haiku 5.5 的知識截止日期目錄未提供，未驗證。
- **Priority Tier**：Opus 5.5 / 5、Sonnet 5.5 / 5、Fable 5.1、Mythos 5.1 / 5 不支援；Fable 5、Opus 4.8 與較舊的現行模型支援。
- **Sampling 參數**：自 2026-10-21 起，`temperature`、`top_p`、`top_k` 在所有模型都回 400；Opus 5.5 / 5、Sonnet 5.5 / 5、Fable 系列與 Haiku 5.5 更早就已移除或拒絕非預設值。

---

## 7. 選型建議

![圖：選型流程——先看使用者有沒有明確指定，沒有就用 Opus 5.5](figures/claude-model-choose.svg)

1. **預設情況下使用 Opus（`claude-opus-5-5`）**——這是目前建議的通用預設模型，適合絕大多數程式開發與推理任務。注意其 `effort` 預設為 `medium`，並且不能關閉 thinking。
2. **僅在使用者明確要求「Fable」、「最強模型」時，才使用 `claude-fable-5-1`**——需處理 `refusal` 與強制 `tool_choice` 回 400 的限制，並注意其資料保留政策（30 天，與 ZDR 不相容）與較高的計費成本。
3. **僅在使用者明確要求「Sonnet」或有明確成本考量時，才降級使用 Sonnet（現行為 `claude-sonnet-5-5`）**——不應自行為了省錢而降級，這是使用者的決定權。
4. **Haiku 5.5**（`claude-haiku-5-5`，1M 情境、$0.10 / $0.50）適合高吞吐量、低複雜度的任務；**Haiku 4.5**（200K、$1 / $5）僅在需要舊機制時使用。兩者同樣需使用者明確指定才使用。
