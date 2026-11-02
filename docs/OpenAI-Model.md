# OpenAI 模型比較（API 版）

> 資料日期：2026-07-12  
> 範圍：以 OpenAI 官方 API 文件與定價頁在 2026-07-12 仍可查到的模型為準；不嘗試收錄所有歷史快照。  
> 讀法：如果某模型只出現在定價頁、特定指南或被明確標示為 deprecated / preview，本文會直接標註。

## 1. 先看結論

| 場景 | 建議模型 | 原因 |
|---|---|---|
| 最強通用推理、複雜 coding、代理工作流 | `gpt-5.6-sol` 或 alias `gpt-5.6` | 目前官方主推旗艦；1.05M context、128K max output、完整工具能力。 |
| 智能與成本平衡 | `gpt-5.6-terra` | 價格約是 Sol 的一半，仍屬最新主力。 |
| 大量請求、成本敏感 agent | `gpt-5.6-luna` | 最新便宜版，適合高吞吐量。 |
| 深度研究報告 | `o3-deep-research` | 專門做搜尋、瀏覽、分析與長報告整合。 |
| 便宜版深度研究 | `o4-mini-deep-research` | 與 `o3-deep-research` 同類，但更省。 |
| Coding agent / Codex 生態 | `gpt-5.6`；特殊需求可看 `gpt-5.3-codex` | 官方仍建議大多數程式任務先從 `gpt-5.6` 開始。 |
| 即時語音 agent | `gpt-realtime-2.1` | 原生支援音訊輸入/輸出、推理與工具使用。 |
| 低成本即時語音 | `gpt-realtime-2.1-mini` | 明顯便宜，適合大量語音互動。 |
| 圖像生成 / 編修 | `gpt-image-2` | OpenAI 目前主打的影像模型。 |
| 影片生成 | `sora-2-pro` | 高品質輸出；若重視迭代速度改用 `sora-2`。 |
| 向量檢索 | `text-embedding-3-small` | CP 值高，通常是預設選擇。 |
| 高品質 embedding | `text-embedding-3-large` | 檢索品質最佳，但成本高很多。 |
| 內容審查 | `omni-moderation-latest` | 支援文字與圖片；2026-07-12 的 pricing 頁未單列費率。 |

## 2. 模型分層怎麼看

OpenAI 目前的 API 模型大致分成六層：

1. **最新通用 / 推理模型**：GPT-5.6 家族，是新專案的主力選擇。
2. **較舊但仍列價的 GPT 模型**：GPT-5.5、GPT-5.4 系列，通常是相容性、成本或既有部署考量。
3. **專用模型**：深度研究、Codex、ChatGPT alias、cyber、computer use 之類。
4. **即時與音訊模型**：Realtime、語音轉文字、音訊輸入輸出。
5. **生成式媒體模型**：影像與影片。
6. **基礎設施模型**：Embeddings、Moderation。

另外，官方 Models 首頁已明確把 **GPT-5.6 Sol / Terra / Luna** 放在最前面，代表它們是現在的主力推薦；不是所有列在定價頁的型號都應被當成首選。

## 3. 最新通用 / 推理模型

> 官方 Models 頁寫得很直接：如果你不確定要選哪個，先用 `gpt-5.6`。目前這個 alias 指向 `gpt-5.6-sol`。

| 模型 | 定位 | 標準價（輸入 / 輸出，每 1M tokens） | Context / Max output | 適合什麼 |
|---|---|---:|---|---|
| `gpt-5.6-sol` | 旗艦 | $5 / $30 | 1.05M / 128K | 最難推理、複雜 coding、長鏈工具任務。 |
| `gpt-5.6-terra` | 平衡版 | $2.50 / $15 | 1.05M / 128K | 多數正式產品的預設選擇。 |
| `gpt-5.6-luna` | 成本優先 | $1 / $6 | 1.05M / 128K | 高流量、成本敏感 agent。 |

重點：

- 這三個最新模型都支援文字與圖片輸入、文字輸出、多語與 vision，並可走 `Responses API`。
- 官方列出的內建工具能力包含：Functions、Web search、File search、Computer use。
- 如果你需要 GPT-5.6 家族裡的最高智力配置，官方在 reasoning guide 建議用 `gpt-5.6-sol`，並把 `reasoning.mode` 設成 `pro`。
- `gpt-5.6` 是 alias；若你要固定版本，應直接寫明 `gpt-5.6-sol` / `terra` / `luna`。
- 不要直覺假設「新版一定更貴」：`gpt-5.6-terra` 在官方 pricing 頁上其實**比 `gpt-5.5` 便宜很多**。以 Standard / Short context 為例，`gpt-5.6-terra` 是 `$2.50 in / $15 out`，`gpt-5.5` 是 `$5 in / $30 out`；Long context 也是 Terra 較便宜。

## 4. 仍列價的較舊 GPT 模型

這些模型還在官方定價表上，但已不是 Models 首頁的主推選項。新專案除非有成本、回歸測試或既有 prompt 相容需求，否則通常先看 GPT-5.6 家族。

| 模型 | 標準價（輸入 / 輸出，每 1M tokens） | 觀察 |
|---|---:|---|
| `gpt-5.5` | $5 / $30 | 舊一代高階推理模型；仍可用，但已被 GPT-5.6 取代為主力。 |
| `gpt-5.5-pro` | $30 / $180 | 很昂貴；多數情況下會先比較 `gpt-5.6-sol` + `reasoning.mode=pro`。 |
| `gpt-5.4` | $2.50 / $15 | 官方 reasoning guide 仍把它列為較低成本選項。 |
| `gpt-5.4-mini` | $0.75 / $4.50 | 成本與延遲更低，適合輕量推理。 |
| `gpt-5.4-nano` | $0.20 / $1.25 | 超便宜，適合分類、抽取、簡單 agent 任務。 |
| `gpt-5.4-pro` | $30 / $180 | 舊代高價位型號，通常只會出現在既有系統。 |

補充：

- reasoning guide 仍提到 `gpt-5.5` 與 `gpt-5.4` 這類推理模型支援 interleaved thinking。
- 定價頁顯示 `gpt-5.5`、`gpt-5.4` 有 short/long context 定價欄；`gpt-5.4-mini`、`gpt-5.4-nano` 則只出現在 short context 欄位。
- 實務上如果你是在 `gpt-5.6-terra` 和 `gpt-5.5` 之間猶豫，多半會先選 `gpt-5.6-terra`，因為它同時是較新的主力模型，而且價格約是 `gpt-5.5` 的一半。

## 5. 專用模型

| 模型 | 定價 | 定位 | 備註 |
|---|---:|---|---|
| `chat-latest` | $5 / $30 | ChatGPT 對話 alias | 偏 ChatGPT 風格入口，不是新一代旗艦替代品。 |
| `gpt-5.3-codex` | $1.75 / $14 | Codex / coding agent 專用 | Code generation 指南提到它是為 Codex 類 agent 設計，但仍建議大多數 API 程式任務先用 `gpt-5.6`。 |
| `o3-deep-research` | $5 / $20 | 高品質深度研究 | 專長是搜尋、瀏覽、分析與長報告整合。 |
| `o4-mini-deep-research` | $1 / $4 | 便宜版深度研究 | 成本更低，適合大量研究任務。 |
| `gpt-5.4-cyber` | 定價頁列名，但未公開完整價格 | Cyber 類別專用 | 公開文件對此模型細節很少，不建議在未確認權限前直接規劃。 |
| `computer-use-preview` | $1.50 / $6 | 舊 preview 電腦操作模型 | 官方 computer use 指南已把它標成舊 preview 路徑；新實作應改用 GA 的 `gpt-5.5` + `computer` tool。 |

深度研究模型要注意：

- 必須搭配至少一個資料來源：Web search、Remote MCP、或 File search / vector store。
- 可搭配 Code Interpreter 做分析。
- **不支援** 一般 function calling。
- 更像「研究代理模型」，不是通用聊天模型。
- Pricing 頁目前把 deep research 與 `computer-use-preview` 放在 Specialized models 的 Batch 區塊；正式報價前應再核對最新 pricing 頁。

## 6. Realtime / Audio / Speech

### 6.1 最新主力音訊模型

| 模型 | 用途 | 主要價格 |
|---|---|---|
| `gpt-realtime-2.1` | 即時 speech-to-speech、語音 agent、可推理可用工具 | Audio $32 in / $64 out；Text $4 in / $24 out；Image $5 in |
| `gpt-realtime-2.1-mini` | 低成本即時語音 | Audio $10 in / $20 out；Text $0.60 in / $2.40 out；Image $0.80 in |
| `gpt-realtime-translate` | 即時語音翻譯 | $0.034 / 分鐘 |
| `gpt-realtime-whisper` | 即時語音轉文字 | $0.017 / 分鐘 |
| `gpt-4o-transcribe` | 檔案 / request-based 轉錄 | 約 $0.006 / 分鐘 |
| `gpt-4o-mini-transcribe` | 便宜版 request-based 轉錄 | 約 $0.003 / 分鐘 |

### 6.2 其他官方仍提到的音訊模型

- `gpt-audio-1.5`：官方 audio guide 仍把它列為可做 request-based 音訊輸入/輸出與文字轉語音的音訊模型，但 2026-07-12 的 pricing 頁沒有把它單獨列價。
- Models 頁仍可見較舊的 `GPT-Realtime-2`、`GPT-Realtime-1.5`、`GPT-Realtime mini`。
- Models 頁同時把 `GPT-4o mini TTS` 標成 **Deprecated**，新案不應再優先採用。

怎麼選：

- 即時對話 agent：先看 `gpt-realtime-2.1`。
- 低成本客服或大量語音 session：`gpt-realtime-2.1-mini`。
- 單純做檔案轉錄：`gpt-4o-transcribe` / `gpt-4o-mini-transcribe`。
- 既有 chat 系統只想加音訊 I/O：可研究 `gpt-audio-1.5`，但先確認最新價格與支援狀態。

## 7. 圖像生成模型

### 7.1 目前主力

| 模型 | 定位 | 1024x1024 參考成本 | 觀察 |
|---|---|---|---|
| `gpt-image-2` | 現行主力影像模型 | Low $0.006 / Medium $0.053 / High $0.211 | 支援更大尺寸，最高邊長可到 3840px；目前**不支援透明背景**。 |
| `gpt-image-1.5` | 較舊但仍列價 | Low $0.009 / Medium $0.034 / High $0.133 | 如果你有既有流程或需要延續舊模型結果，可保留比較。 |
| `gpt-image-1` | 舊代影像模型 | Low $0.011 / Medium $0.042 / High $0.167 | 官方 image guide 仍有列出，但已不是首頁主推。 |
| `gpt-image-1-mini` | 便宜版 | Low $0.005 / Medium $0.011 / High $0.036 | 成本最低，適合大量生成或草圖。 |

其他觀察：

- `gpt-image-2` 是目前 OpenAI 明確主打的影像模型。
- `gpt-image-2` 支援大量尺寸，而不只傳統 1024 方圖。
- 編修時如果帶 reference image，`gpt-image-2` 會以高保真處理圖片輸入，因此圖片輸入 token 成本可能上升。
- 圖像家族文件中仍提到 `gpt-image-1`，但 Models 首頁目前主推的是 `gpt-image-2`。

## 8. 影片生成模型

| 模型 | 定位 | 標準價 | 適合什麼 |
|---|---|---:|---|
| `sora-2` | 速度與靈活性優先 | 720p 約 $0.10 / 秒 | 概念驗證、快速迭代、社群內容、rough cut。 |
| `sora-2-pro` | 品質優先 | 720p $0.30 / 秒；1024p $0.50 / 秒；1080p $0.70 / 秒 | 廣告、行銷素材、較高穩定度與視覺精度。 |

補充：

- Batch 價格約是 standard 的一半。
- 官方明確說 `sora-2-pro` 更適合 `1920x1080` / `1080x1920` 的 1080p 輸出。
- 文件指出兩者都支援較長片段生成，並建議依 production 需求選最小可用尺寸。

## 9. Embeddings

| 模型 | Pages per dollar | MTEB | 向量長度 | Max input | 建議 |
|---|---:|---:|---:|---:|---|
| `text-embedding-3-small` | 62,500 | 62.3% | 1536 | 8192 | 預設首選；CP 值最好。 |
| `text-embedding-3-large` | 9,615 | 64.6% | 3072 | 8192 | 品質最高，但明顯更貴。 |
| `text-embedding-ada-002` | 12,500 | 61.0% | 1536 | 8192 | 舊基準模型；新案通常不會再從它開始。 |

補充：

- 官方支援用 `dimensions` 參數縮短 embedding 長度。
- 文件特別提到：就算把 `text-embedding-3-large` 壓到 256 維，仍可能優於完整 1536 維的 `text-embedding-ada-002`。

## 10. Moderation

| 模型 | 支援輸入 | 價格 | 備註 |
|---|---|---|---|
| `omni-moderation-latest` | 文字、圖片 | Pricing 頁未單列 | 不支援音訊；單張圖片上限 20 MB。 |

這個模型不是用來產生內容，而是做安全分類。若你的系統需要審核使用者輸入、檔案上傳或模型輸出，這是幾乎必備的配套模型。

## 11. 實務選型建議

### 新專案

- 通用產品：先用 `gpt-5.6-terra`。
- 最難任務、最重 reasoning：`gpt-5.6-sol`。
- 大量低成本：`gpt-5.6-luna`。
- 不要一開始就選 `gpt-5.5` / `gpt-5.4`，除非你有相容性需求。

### GPT-5.6 的 reasoning effort

`reasoning.effort` 是模型內部推理量的調整鈕，不是回覆長度設定。提高 effort 通常能提升複雜任務的品質與穩定性，但也會提高延遲、輸出 token 用量與成本。GPT-5.6 支援 `none`、`low`、`medium`、`high`、`xhigh`；未指定時預設為 `medium`。模型仍會依任務難度自適應，因此 effort 不是固定 token 額度保證。

| effort | 適用工作 | 實務建議 |
|---|---|---|
| `none` | 分類、快速查詢、極低延遲流程 | 不適合多步推理、複雜工具呼叫或 agent。 |
| `low` | 簡單程式修改、初步 log 判讀、一般工具呼叫 | 速度與成本優先；適合大量日常小任務。 |
| `medium` | 功能開發、單元測試、一般 issue 分析 | GPT-5.6 預設值；品質、延遲與成本的平衡起點。 |
| `high` | 複雜除錯、跨模組根因分析、重構規劃 | 品質優先；適合較難的 coding 與 agent 任務。 |
| `xhigh` | 安全／程式碼審查、長時間 agent、困難研究 | 僅在 eval 證實有明顯收益時使用，因延遲與成本最高。 |

`reasoning.mode` 與 effort 是兩個獨立設定：`standard` 是預設模式；`pro` 會讓模型進行更多運算，適合非常困難且能容忍更高延遲與 token 成本的工作。若使用 GPT-5.6 家族的最高能力組合，選 `gpt-5.6-sol` + `reasoning.mode=pro`，再從 `medium` 或 `high` 開始評測。不要把提高 effort 當成修復品質的唯一方法，prompt 仍應明確寫出完成條件與驗證方式。

### 程式專案開發

- 日常開發、功能實作、重構、補測試：先用 `gpt-5.6-terra`。
- 跨模組設計、較大範圍重構、複雜 code review：升到 `gpt-5.6-sol`。
- 大量樣板程式、批次小改動、低成本輔助：用 `gpt-5.6-luna`。
- 若比較的是 `gpt-5.6-terra` 與 `gpt-5.5`：優先考慮 `gpt-5.6-terra`，因為它是更新主力，且 2026-07-12 官方 pricing 顯示它更便宜。

### Issue 分析

- 一般 bug triage、讀 stack trace、初步定位問題：先用 `gpt-5.6-terra`。
- 困難 issue、跨模組除錯、根因分析、flaky 問題、效能瓶頸排查：升到 `gpt-5.6-sol`。
- 大量 ticket triage、log 摘要、分類與優先級整理：用 `gpt-5.6-luna`。
- 如果 issue 分析需要大量查外部文件、搜尋資料、整理研究報告：改用 `o3-deep-research`，便宜版可用 `o4-mini-deep-research`。

### 測試程式

- 單元測試、整合測試、mock/stub、測試資料生成：先用 `gpt-5.6-terra`。
- 複雜測試策略、端對端測試設計、難重現 bug 的回歸測試、flaky test 分析：升到 `gpt-5.6-sol`。
- 大量產生測試案例、補 coverage、整理測試輸出與失敗摘要：用 `gpt-5.6-luna`。
- 如果是要分析 CI 失敗、比對多次測試結果、找出不穩定測試的共同模式，`gpt-5.6-sol` 通常比 `terra` 更穩。

### Agent / tool-heavy workflow

- 一般 agent：GPT-5.6 家族優先。
- 深度研究 agent：`o3-deep-research` 或 `o4-mini-deep-research`。
- 電腦操作：不要再從 `computer-use-preview` 開始，直接走 GA 的 `gpt-5.5` + `computer` tool。

### 多媒體

- 圖像品質優先：`gpt-image-2`。
- 圖像成本優先：`gpt-image-1-mini`。
- 影片品質優先：`sora-2-pro`。
- 影片迭代速度優先：`sora-2`。
- 即時語音：`gpt-realtime-2.1`。

### 檢索與安全

- RAG / 搜尋：`text-embedding-3-small` 是預設值。
- 高精度語義檢索：`text-embedding-3-large`。
- 內容審核：一定接 `omni-moderation-latest`。

## 12. 一句話總結

如果你只想記一件事：**2026-07-12 這個時間點，OpenAI 的主力不是「所有列價模型平均分布」，而是 GPT-5.6 家族做通用任務，Deep Research 做研究，Realtime 做語音，GPT Image / Sora 做生成式媒體，Embedding / Moderation 做底層能力。**

## 13. 官方來源

- Models: https://developers.openai.com/api/docs/models
- Pricing: https://developers.openai.com/api/docs/pricing
- Reasoning models: https://developers.openai.com/api/docs/guides/reasoning
- Code generation: https://developers.openai.com/api/docs/guides/code-generation
- Deep research: https://developers.openai.com/api/docs/guides/deep-research
- Audio and speech: https://developers.openai.com/api/docs/guides/audio
- Image generation: https://developers.openai.com/api/docs/guides/image-generation
- Video generation: https://developers.openai.com/api/docs/guides/video-generation
- Embeddings: https://developers.openai.com/api/docs/guides/embeddings
- Moderation: https://developers.openai.com/api/docs/guides/moderation
- Computer use: https://developers.openai.com/api/docs/guides/tools-computer-use
- Cybersecurity checks: https://developers.openai.com/api/docs/guides/safety-checks/cybersecurity
