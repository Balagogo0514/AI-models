# Transformer Attention 強化機制

> 範圍：本文件整理 Transformer 中常見的 attention 強化方法、解決的瓶頸與公開可驗證的代表模型。內容分為「改變模型架構」與「不改變模型數學結果的系統最佳化」兩類；兩者都常被稱作 attention optimization，但取捨不同。
>
> 更新日期：2026-07-19

## 先看結論

- 短到中等 context、追求通用品質：仍以 dense multi-head self-attention（MHA）為基準，搭配 RoPE 與 FlashAttention 類 kernel。
- 自回歸 LLM 的主要推論瓶頸是 KV cache，不是單純的 `QK^T` 計算；MQA、GQA、MLA 的核心目標都是降低 KV 頭數或壓縮 KV cache。
- 長文件預訓練：sliding-window / sparse attention 直接降低序列長度的二次成本，但會限制部分 token 的直接互看能力。
- 超長 context：位置編碼延展（RoPE scaling、ALiBi）、KV cache 管理與分散式 attention 要一起考量；單一技術通常不足。
- FlashAttention、PagedAttention 不會改變模型的 attention 語義或權重。前者降低 GPU 記憶體 I/O，後者改善 KV cache 配置與 serving；它們可套在許多既有模型上。
- 未公開架構的閉源模型不應根據傳聞宣稱使用某種 attention。本文只列公開論文、技術報告或模型卡可確認的案例。

---

## 1. 基準：Scaled Dot-Product Attention 與 MHA

Transformer 的 self-attention 為：

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

Multi-Head Attention（MHA）用多組投影平行計算 attention，再將各 head 合併。它讓不同 head 學到不同的關聯型態，但 dense attention 的 prefill 計算與 attention matrix 記憶體都隨序列長度 `n` 呈 `O(n^2)` 成長；在 decoder-only LLM 的逐 token decode 中，KV cache 也會隨 `n`、layer 數與 KV head 數線性增加。

| 機制 | 作用 | 代表模型 |
|---|---|---|
| Scaled dot-product attention | 以 query 與 key 相似度加權 value；縮放避免 softmax 過度飽和。 | 原始 Transformer、BERT、GPT 系列等。 |
| Multi-Head Attention（MHA） | 多個 attention 子空間並行，提升表徵能力。 | Transformer、BERT、GPT-2、LLaMA 1 等。 |
| Causal mask | decoder 只能注意目前與過去 token，維持自回歸生成。 | GPT 類、LLaMA 類、Mistral 類。 |

**原始來源：** [Attention Is All You Need](https://arxiv.org/abs/1706.03762)

---

## 2. 位置與相對距離：讓 attention 知道「在哪裡」

純 attention 對 token 順序不敏感，因此必須注入位置訊息。此類方法通常不降低主要複雜度，但直接影響長 context 泛化、外插能力與訓練穩定性。

| 機制 | 如何強化 attention | 主要作用 | 公開代表模型 |
|---|---|---|---|
| Relative Position Bias | 在 attention score 加入 query-key 相對距離的 learned bias / embedding。 | 讓模型直接表示相對距離；適合 encoder-decoder 與長序列。 | Transformer-XL、T5。 |
| RoPE（Rotary Position Embedding） | 對 Q、K 的成對維度做隨位置變化的旋轉，使內積自然帶入相對位置。 | 兼具絕對位置與相對距離訊號；已成 decoder LLM 常見選擇。 | RoFormer、LLaMA 1/2/3、Mistral、Qwen。 |
| RoPE scaling / Position Interpolation / YaRN | 對 RoPE 頻率或位置索引重縮放，通常搭配長 context fine-tuning。 | 將既有 RoPE 模型延展到較長 context；須驗證長距離 retrieval 與品質退化。 | LongChat（position interpolation）、多個 LLaMA 衍生長 context 模型。 |
| ALiBi | 對 attention score 加入每個 head 不同斜率的線性距離懲罰。 | 以很少的額外參數支援 train-short / test-long 外插。 | BLOOM、MPT。 |

### 選型提醒

- RoPE / ALiBi 解的是「位置表示」問題，不會消除 dense attention 的 `O(n^2)` prefill 成本。
- context window 宣稱可用，不等於模型能在整段內容穩定檢索與推理；應以 needle retrieval、長文件 QA 與實際工作負載評估。
- RoPE scaling 通常需要針對目標長度重新訓練或微調；只在推論時任意拉伸位置，可能使品質明顯下降。

**來源：** [Transformer-XL](https://arxiv.org/abs/1901.02860)、[T5](https://arxiv.org/abs/1910.10683)、[RoFormer / RoPE](https://arxiv.org/abs/2104.09864)、[ALiBi](https://arxiv.org/abs/2108.12409)、[Position Interpolation](https://arxiv.org/abs/2306.15595)、[YaRN](https://arxiv.org/abs/2309.00071)

---

## 3. 降低 KV Cache：MQA、GQA 與 MLA

對 decoder LLM，生成第 `t` 個 token 時，所有過去 token 的 K、V 會保留在 KV cache。MHA 中每個 query head 都有自己的 K/V head；因此長 context、多併發 serving 時，記憶體頻寬與容量常成為瓶頸。

| 機制 | 核心改動 | 效果與取捨 | 公開代表模型 |
|---|---|---|---|
| MQA（Multi-Query Attention） | 所有 query heads 共用單一 K head 與單一 V head。 | 大幅縮小 KV cache、加快 autoregressive decode；可能比 MHA 有較明顯品質損失。 | PaLM、Falcon 40B。 |
| GQA（Grouped-Query Attention） | 多個 query heads 共用一組 K/V heads；KV head 數介於 MHA 與 MQA。 | 在品質、KV cache 與 decode throughput 間折衷；目前公開 LLM 的常見方案。 | Llama 2 34B/70B、Mistral 7B、Mixtral。 |
| MLA（Multi-head Latent Attention） | 將 KV 壓縮為低維 latent cache，使用上投影與位置處理重建每個 head 所需資訊。 | 比 GQA 更激進壓縮 KV cache，降低 decode 記憶體頻寬；架構與 kernel 實作較複雜。 | DeepSeek-V2、DeepSeek-V3、DeepSeek-R1。 |

### 關係圖

```text
MHA:  h 個 Q heads -> h 個 K/V heads        品質基準，KV cache 最大
GQA:  h 個 Q heads -> g 個 K/V heads         g < h；常見折衷
MQA:  h 個 Q heads -> 1 個 K/V head           KV cache 最小，品質取捨較大
MLA:  h 個 Q heads -> 壓縮 latent KV cache    以投影換取更高壓縮率
```

### 實務判斷

- 新建高併發 decoder-only LLM：GQA 是成熟、相對低風險的預設。
- 目標是非常長 context 或 decode throughput：評估 MLA，但不要只看 cache 壓縮率，也要量測 kernel、量化、tensor parallel 與實際 batch size。
- MQA 適合極端 decode 記憶體壓力情境；若品質敏感，通常先比較 GQA。

**來源：** [Multi-Query Attention](https://arxiv.org/abs/1911.02150)、[GQA](https://arxiv.org/abs/2305.13245)、[PaLM](https://arxiv.org/abs/2204.02311)、[Llama 2](https://arxiv.org/abs/2307.09288)、[Mistral 7B](https://arxiv.org/abs/2310.06825)、[DeepSeek-V2 / MLA](https://arxiv.org/abs/2405.04434)

---

## 4. 稀疏與局部 Attention：直接降低長序列成本

Dense attention 讓每個 token 都可看全部 token，成本為二次成長。Sparse attention 只保留某些連線，常見組合是 local window、少量 global token、random / block pattern。代價是某些遠距 token 不再能在單一 layer 直接互相注意。

| 機制 | 連線模式 | 作用 | 公開代表模型 |
|---|---|---|---|
| Sliding Window Attention（SWA） | 每個 token 只看附近固定 window；多層後有效 receptive field 擴大。 | prefill 成本近似 `O(nw)`，`w` 為 window；適合局部語言與長 context。 | Mistral 7B、Mixtral。 |
| Longformer attention | local window 加上任務指定的 global attention。 | 長文件 classification、QA、summarization；讓關鍵 token 保持全域連線。 | Longformer、LED（Longformer Encoder-Decoder）。 |
| BigBird block sparse attention | random + window + global token。 | 以近線性成本處理長序列，同時保留全域資訊路徑與理論性質。 | BigBird、BigBird-Pegasus。 |
| Dilated / block sparse attention | 以固定或擴張間隔保留 blocks。 | 用較少連線擴大 receptive field；常用於特定長序列研究與架構。 | LongNet（dilated attention）。 |

### 何時使用

- 文件任務重點多在局部段落：SWA 或 Longformer 類模式可顯著降低成本。
- 需要任意兩個 token 精確直接比對：sparse pattern 可能漏掉關聯，需額外 global token、retrieval 或多層傳遞。
- 自回歸 decoder 的長 context 服務：Mistral 類 SWA 通常仍須考慮 KV cache；window 限制可讓舊 KV 不再參與部分計算，但實際記憶體策略依實作而異。

**來源：** [Longformer](https://arxiv.org/abs/2004.05150)、[BigBird](https://arxiv.org/abs/2007.14062)、[Mistral 7B](https://arxiv.org/abs/2310.06825)、[LongNet](https://arxiv.org/abs/2307.02486)

---

## 5. 線性與近似 Attention：以近似換取序列長度可擴展性

這一類方法避免顯式建立 `n x n` attention matrix，將 softmax / kernel attention 改寫或近似為可結合的形式。理論複雜度可對序列長度近線性，但常有近似誤差、數值穩定性或硬體實際吞吐不如 dense kernel 的問題。

| 機制 | 核心想法 | 作用與限制 | 公開代表模型 |
|---|---|---|---|
| Linear Transformer | 以可分解的 kernel feature map，利用矩陣乘法結合律改寫 attention。 | 對序列長度近線性；與 softmax dense attention 的行為不同。 | Linear Transformer 論文模型。 |
| Performer / FAVOR+ | 以正交 random features 近似 softmax kernel。 | 線性時間與空間，並提供近似誤差理論；效果取決於 random feature 維度與任務。 | Performer 模型；用於文字、影像與 protein sequence 實驗。 |
| Low-rank / Nyström attention | 對 attention matrix 使用 landmark 或低秩近似。 | 降低長序列成本；適合某些 encoder 類任務，對因果 LLM 要額外注意。 | Nyströmformer。 |

**重要區別：** FlashAttention 不是 linear / approximate attention。FlashAttention 仍計算 exact softmax attention，主要降低 I/O 與中間矩陣儲存。

**來源：** [Linear Transformers](https://arxiv.org/abs/2006.16236)、[Performer](https://arxiv.org/abs/2009.14794)、[Nyströmformer](https://arxiv.org/abs/2102.03902)

---

## 6. 跨模態與 Encoder-Decoder Attention

這些機制不一定是為了加速，而是改變「誰能注意誰」，使 Transformer 能融合不同來源或在生成時查閱 encoder memory。

| 機制 | 作用 | 公開代表模型 |
|---|---|---|
| Cross-attention | decoder 的 Q 注意 encoder 或外部 memory 的 K/V；把輸入理解與輸出生成分開。 | 原始 Transformer、T5、BART。 |
| Gated cross-attention | 將視覺 / 音訊等模態作為 cross-attention memory，並用 gate 控制注入幅度。 | Flamingo。 |
| Perceiver latent cross-attention | 用固定數量 latent queries 從大量輸入 token 讀取資訊，再在 latent 空間處理。 | Perceiver IO、Flamingo 的 Perceiver Resampler。 |
| Multi-modal self-attention | 影像、文字、音訊等統一成 token 後，在相同 sequence 中 self-attend。 | Chameleon、部分原生多模態模型的公開架構。 |

**來源：** [T5](https://arxiv.org/abs/1910.10683)、[Flamingo](https://arxiv.org/abs/2204.14198)、[Perceiver IO](https://arxiv.org/abs/2107.14795)、[Chameleon](https://arxiv.org/abs/2405.09818)

---

## 7. 不改模型語義的 Attention 系統最佳化

下列技術常會顯著影響成本與吞吐，但通常不是 checkpoint 的架構特徵。相同模型可以採用或不採用它們。

| 技術 | 是否改變 attention 結果 | 主要作用 | 可套用模型 |
|---|---|---|---|
| FlashAttention / FlashAttention-2/3 | 否，exact attention。 | 透過 tiling 與 I/O-aware kernel 減少 HBM 讀寫與中間矩陣，改善訓練與 prefill 的速度、記憶體使用。 | 支援相容 head dimension / GPU kernel 的 MHA、GQA 等 Transformer；原始論文於 BERT-large、GPT-2 等測試。 |
| PagedAttention | 否。 | 用類似作業系統 paging 的 block 管理 KV cache，降低 fragmentation、提高 batch serving 效率。 | vLLM 支援的 decoder LLM；不是模型專屬架構。 |
| Continuous batching | 否。 | 將不同生成長度的 request 動態混批，提高 GPU 利用率。 | serving stack 支援的 decoder LLM。 |
| KV cache quantization / offload | 近似或資料表示改動，但不改 checkpoint 架構。 | 將 KV cache 以較低 bit 數儲存或移至 CPU / SSD，換取容量但可能增加誤差或延遲。 | 多數 MHA/GQA/MLA decoder LLM，依 runtime 支援而定。 |
| Ring Attention | 否，通常為 exact distributed attention。 | 在多裝置間環狀傳遞 K/V blocks，使單一 sequence 能跨裝置切分。 | 長 context 訓練 / 推論基礎設施；不綁定特定 foundation model。 |

### FlashAttention 與 PagedAttention 的差異

```text
FlashAttention:  一次 attention 計算如何讀寫 GPU memory
PagedAttention:  多個 request 的歷史 K/V cache 如何配置與回收

兩者可同時使用：前者加速 kernel，後者提升 serving 記憶體利用率。
```

**來源：** [FlashAttention](https://arxiv.org/abs/2205.14135)、[FlashAttention-2](https://arxiv.org/abs/2307.08691)、[PagedAttention / vLLM](https://arxiv.org/abs/2309.06180)、[Ring Attention](https://arxiv.org/abs/2310.01889)

---

## 8. 常見混淆

| 名稱 | 正確分類 | 說明 |
|---|---|---|
| RoPE / ALiBi | 位置表示與 score bias | 改變 attention score 如何編碼距離，不是 sparse attention。 |
| MQA / GQA / MLA | KV cache / decode 架構最佳化 | 主要減少 K/V 儲存與記憶體頻寬；不會讓 prefill 的 dense `QK^T` 自動變線性。 |
| FlashAttention | exact kernel 最佳化 | 不近似 softmax，也不改 attention topology。 |
| PagedAttention | serving 記憶體管理 | 不在 checkpoint 中；可被多種模型共用。 |
| MoE | FFN / routing 稀疏化 | MoE 是 expert routing，不是 attention 機制；可與任何上述 attention 組合。 |
| Mamba / SSM | attention 替代架構 | 不是強化 attention，而是以 state-space sequence model 取代或混合 attention。 |

---

## 9. 設計選型指南

| 需求 | 優先考慮 | 避免的誤區 |
|---|---|---|
| 一般 chatbot / coding LLM | RoPE + GQA + FlashAttention + KV cache。 | 只因 context window 大就把全部文件塞進 prompt。 |
| 高併發、長輸出 serving | GQA 或 MLA、PagedAttention、continuous batching、KV quantization 評測。 | 只比較模型參數量，忽略 decode memory bandwidth。 |
| 長文件 QA | RAG / chunking 為主；若模型端訓練，考慮 SWA、Longformer / BigBird 或 RoPE 長 context fine-tuning。 | 期待 sparse pattern 自動保留任意遠距精確關聯。 |
| 極長 sequence 訓練 | FlashAttention、sequence / context parallel、Ring Attention；依工作負載評估 sparse 或 linear 方法。 | 把理論 `O(n)` 直接等同於實際 GPU wall-clock 更快。 |
| 多模態輸入 | cross-attention / latent resampler，或統一 token 的 multimodal self-attention。 | 將視覺 token 全量加入長文字 context 而不做壓縮。 |
| 既有 MHA checkpoint 降低推論成本 | 先用 runtime KV quantization / PagedAttention；需要架構改造才評估 MHA-to-GQA / MLA 轉換。 | 假定替換 attention 後不需重新訓練或評測。 |

---

## 10. 評估指標

選 attention 方案時至少同時測量下列面向：

1. **品質：** 任務 accuracy、perplexity、長文件 retrieval、長距離依賴、generation quality。
2. **Prefill：** 固定 input length 下的 latency、tokens/s、峰值 VRAM。
3. **Decode：** 固定 context 長度與 batch size 下的 tokens/s、KV cache 容量與記憶體頻寬。
4. **Serving：** 併發 request、不同輸出長度下的 p50 / p95 latency、cache fragmentation、排隊時間。
5. **長度泛化：** 訓練長度外的品質曲線，而不只測最大 context 是否可接受輸入。

---

## 11. 延伸閱讀

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Efficient Transformers: A Survey](https://arxiv.org/abs/2009.06732)
- [FlashAttention](https://arxiv.org/abs/2205.14135)
- [GQA: Training Generalized Multi-Query Transformer Models](https://arxiv.org/abs/2305.13245)
- [DeepSeek-V2: Multi-head Latent Attention](https://arxiv.org/abs/2405.04434)
- [Mistral 7B](https://arxiv.org/abs/2310.06825)
- [PagedAttention / vLLM](https://arxiv.org/abs/2309.06180)

---

## 12. Exact softmax attention

**Exact softmax attention** 指輸出與原始 Transformer 注意力公式相同：

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

對每一個 query，模型計算它與所有「可見」key 的分數、在這些分數上做 softmax 正規化，再以所得權重加權 value。`exact` 的意思是結果沒有以核函數、低秩分解或 recurrent state 近似；它不代表演算法一定會顯式儲存完整 `n x n` 矩陣，也不代表一定是全域視野。

| 機制 | 是否為 exact softmax | 原因 |
|---|---|---|
| 標準 MHA | 是 | 直接計算原始公式。 |
| FlashAttention | 是 | 改變 GPU 分塊與記憶體 I/O 排程，但數值目標仍是相同的 softmax attention。 |
| MQA / GQA | 是 | 共用或分組 K/V heads 以減少 KV cache；每個 query head 仍在可見 token 上做原始 softmax。 |
| Sliding-window / block-sparse attention | 在其允許的連線上是 | 只保留部分 token-to-token 連線；對保留的 key 做 exact softmax。相對於「全域」softmax attention，則是稀疏且非全域。 |
| Performer / kernel linear attention | 否 | 以 feature map 或隨機特徵近似 softmax kernel，避免完整兩兩比較。 |
| Kimi Delta Attention（KDA） | 否 | 以有限 recurrent state 的 delta-rule 更新／讀取記憶，不會重現每個歷史 token 的完整 softmax 權重。 |

因此，FlashAttention、MQA 與 GQA 是在**不改變 softmax attention 數學定義**下提升效率；線性注意力則為了讓長度成本接近線性，改變或近似注意力的計算方式。

## 13. Kimi K3：Kimi Delta Attention（KDA）

Kimi K3 的線性注意力核心是 **Kimi Delta Attention（KDA）**。它不是將 softmax attention 單純以 feature map 近似，而是沿用 DeltaNet 的 **delta rule**：每個 token 先從有限大小的 recurrent state 讀取記憶，再將 value 與目前讀值的差（delta）寫回。這使 state 可以用新資訊修正舊記憶，而非只能不斷累加。

KDA 建立在 Gated DeltaNet 之上，將較粗粒度的 gate 細化為 **per-channel（逐通道）gate**。不同特徵通道因此可以分別決定保留、衰減或覆寫的速度；在固定大小 state 的限制下，模型可更有效分配記憶容量。

概念上的狀態更新可寫成：

```text
read_t  = S_{t-1} k_t
delta_t = v_t - read_t
S_t     = decay_t ⊙ S_{t-1} + write_gate_t ⊙ (delta_t k_t^T)
o_t     = S_t q_t
```

其中 `S` 是固定大小的 recurrent state，`⊙` 表示逐通道調制。實際 KDA 還包含投影、正規化及 chunkwise 演算法；上式用來說明「先讀、再以差值寫回」與細粒度遺忘／寫入的概念，並非其逐項實作公式。

Kimi K3 並非以 KDA 完全取代全域 attention。其公開配置為 **69 層 KDA + 24 層 gated MLA（Multi-head Latent Attention）**，大致是 3:1 的交錯比例：KDA 處理多數層的長序列狀態傳遞，MLA 層則定期提供可直接全域檢索的 attention。這個混合設計以少量全域層補足有限 recurrent state 可能遺失的精確 token 細節。

| 面向 | KDA 的效果 | 與 full attention / MLA 的取捨 |
|---|---|---|
| Prefill | 不需形成完整 `n x n` 注意力分數矩陣，可串流處理序列。 | 長 context 較省計算與 activation；全域 MLA 層仍有完整注意力成本。 |
| Decode 與快取 | 保存固定大小 recurrent state，不保存每個歷史 token 的完整 K/V。 | 降低長 context 的 KV-cache 壓力；state 壓縮不保證與 full attention 同等精確。 |
| 表達能力 | delta rule 可藉由誤差覆寫舊記憶；逐通道 gate 提供更細的遺忘粒度。 | 比一般 kernel linear attention 更像可寫入的記憶模型，但須靠專用 chunkwise kernel 才能取得良好硬體效率。 |
| 架構策略 | 大多數層使用 KDA，間隔配置 MLA。 | 以少量全域 attention 維持檢索能力，換取多數層的長序列效率。 |

Kimi 團隊在 Kimi Linear 的相同訓練配方比較中報告：這個混合架構相對全 MLA 最多可減少 75% KV cache，並在 1M context 的 decode 達到最高約 6 倍 throughput。這些是特定模型、kernel 與工作負載下的實驗結果，不應直接外推為所有線性注意力實作的通用保證。

K3 另加入 **Attention Residuals（AttnRes）**：讓層可依輸入內容選擇性整合較早層的表示，而不是固定累加所有 residual。它主要改善跨深度資訊流與訓練穩定性；KDA／MLA 則主要決定跨序列長度的效率與全域檢索取捨。官方 K3 報告也將百萬 token agentic RL、持續 rollout／sandbox state 及不同 reasoning effort 的後訓練列為長時程推理能力的組成，故不能將其表現完全歸因於單一 attention 公式。

### 為何 AttnRes 有助於長上下文推理

一般 residual connection 可概念化為：

```text
x_(l+1) = x_l + Layer_l(x_l)
```

每層輸出以固定權重一路累加。模型很深時，較早層找到的遠距線索可能與許多後續表示混合，導致訊號被稀釋。AttnRes 改為由目前層依內容選擇先前層表示：

```text
x_(l+1) = Layer_l(x_l) + Attention(q_l, {x_0, x_1, ..., x_l})
```

上式是概念式；實作會以 block 等方式控制跨層 attention 的記憶體與通訊成本。它讓目前層可依任務需要偏重較早層的詞彙／位置／檢索線索、中間層已整理的關係，或深層的抽象推理結果。

長上下文推理常經歷「從遠距 token 讀入訊息 → 早期層形成線索 → 中間層整合關係 → 深層做多步推理」。因此 AttnRes 有助於讓前段取得的訊號跨越深度後仍可被取用；模型不會只是看過遠距資訊，卻在最終推理層失去它。它**不會直接擴大 context window，也不取代 KDA／MLA 的序列 attention**：KDA／MLA 處理跨 token 的成本與檢索，AttnRes 處理跨 layer 的資訊傳遞，長上下文資料與 RL 則訓練模型如何運用這些能力。

### Context window 與有效長上下文

**可輸入 1M token** 是容量規格，不等於模型能在其中可靠地定位、保留、整合並推理關鍵資訊。有效長上下文還取決於位置處理與長序列訓練、遠距 retrieval／多跳推理資料、推理 token 預算，以及 agent 在多回合中的 context compaction、結構化記憶與工具狀態管理。

因此，Kimi K3 的公開優勢可較準確地表述為：KDA + gated MLA 使百萬 token 的成本更可承受，AttnRes 與長時程訓練讓模型較能利用這些資訊。Claude Fable 的完整 attention 架構尚未公開；若其在長任務評測中表現較好，較合理的公開解釋是模型訓練、推理配置與 context-management／agent harness 的整體效果，不能據此推斷它使用 KDA、MLA、GQA 或其他特定內部 attention。

**參考資料：** [Kimi Linear 技術報告](https://arxiv.org/abs/2510.26692)、[Kimi K3 技術報告](https://arxiv.org/abs/2607.24653)、[MoonshotAI/Kimi-K3 官方資料](https://github.com/MoonshotAI/Kimi-K3)、[Attention Residuals](https://arxiv.org/abs/2603.15031)、[Anthropic：長時程 agent harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 14. 中國 LLM 的 Attention 機制比較

下表比較的是各團隊在公開技術報告、模型設定或官方公告中明示的代表性設計，而非對同一實驗室所有模型的推測。模型版本會持續演進；尤其閉源 API 背後的實際 serving kernel、KV quantization 與分散式並行策略通常不會完整公開。

| 團隊／代表模型 | Attention 核心 | 是否 exact softmax | 主要效率目標 | 全域檢索能力 | 公開程度與限制 |
|---|---|---|---|---|---|
| DeepSeek-V2 / V3 / R1 | **MLA（Multi-head Latent Attention）**：以低維 latent 壓縮 K/V，再經投影供各 attention head 使用。 | 是。 | 大幅縮小 decode 時的 KV cache，同時保留全域 attention。 | 是；每個 query 仍可對全部歷史 token 計分。 | 架構由技術報告公開；MoE、MTP 與 load balancing 不是 MLA 的一部分。 |
| Qwen3 | **GQA（Grouped-Query Attention）**：多個 Q heads 共用較少 K/V heads。 | 是。 | 降低 K/V heads 數目、KV-cache 容量與 decode 記憶體頻寬。 | 是。 | 不是以 recurrent state 取代歷史 token 的線性 attention。 |
| Qwen3-Next | **Gated DeltaNet + 全域 gated attention** 的 hybrid attention；公開配置採約 3:1 混合。 | DeltaNet 部分否；全域 attention 部分是。 | 讓多數層以固定 state 處理長序列，並保留部分全域層做直接檢索。 | 混合式；全域層有，純 DeltaNet state 則是壓縮記憶。 | MoE 只節省 FFN 啟用計算，不等同線性 attention。 |
| GLM-4.5（智譜／Z.ai） | **Partial-RoPE GQA**，並以 **QK-Norm** 穩定 attention logits。 | 是。 | GQA 縮小 KV cache；partial RoPE 與 QK-Norm 著重長序列位置處理與訓練／注意力穩定性。 | 是。 | 不是 MLA，也不是線性 attention；其 MoE 是 FFN 路由設計。 |
| Kimi Linear / Kimi K3（Moonshot） | **KDA + gated MLA**；KDA 以逐通道 gate 的 delta rule 更新 recurrent state；K3 另採 AttnRes。 | KDA 否；MLA 是。 | KDA 降低多數層的長序列計算與 KV-cache 壓力，MLA 層補足全域檢索；AttnRes 改善跨層資訊流。 | 混合式。 | K3 公開配置為 69 KDA + 24 gated MLA，不是純 KDA 取代所有 attention。 |
| Claude（Anthropic；含 Fable） | 官方將 Claude 描述為 Transformer；現行旗艦的 attention head、KV 壓縮、稀疏模式與 kernel 未公開。 | 未公開。 | 公開可驗證的是 context compaction、結構化記憶與 agent harness 等長時程系統做法；不能據此反推模型內部 attention。 | 未公開。 | 不能宣稱其使用 GQA、MLA、線性或任何特定 sparse pattern。 |
| GPT（OpenAI） | 現行旗艦的 attention 架構未公開。OpenAI 曾公開研究 block-sparse Transformer，也提供 prompt caching。 | 未公開。 | prompt caching 可重用共同 prompt prefix，降低 API 的重複 prefill 成本；它是服務層快取，而非 attention 公式。 | 未公開。 | 早期 sparse-attention 研究不代表現行 GPT 必然採用；不能據此判定其是否線性。 |
| Gemini（Google DeepMind） | Gemini 1.0 技術報告明示使用如 **MQA（Multi-Query Attention）** 的高效 attention；Gemini 1.5 公開採 MoE。後續旗艦的完整細節有限。 | Gemini 1.0 的 MQA 是；後續未完整公開。 | MQA 縮小 K/V cache；MoE 降低 FFN 的活化計算。 | MQA 是；後續未完整公開。 | MoE 不是 attention 最佳化；不能由 Gemini 1.0 的披露推斷所有 Gemini 世代。 |

對 Claude、OpenAI GPT 與 Gemini 的比較必須比開放權重模型保守：**未公開不代表沒有某項技術，也不代表採用了某項技術。** 對這些模型可確認的 API prompt caching、RAG／context engineering、快取或 serving 行為，應視為系統層效率機制，而不能當作其神經網路 attention topology 的證據。

### 從 KV cache、prefill 與 decode 看取捨

```text
GQA:  減少 K/V heads
      -> KV cache 較小；仍需對歷史 token 做全域 softmax attention

MLA:  將 K/V 壓縮為 latent cache
      -> KV cache 更小；仍保留全域 softmax attention

DeltaNet / KDA:
      將歷史壓縮進固定大小 recurrent state
      -> 多數層的 prefill 與 state 成本可隨長度近似線性；不保留每個歷史 token 的獨立 K/V

Hybrid（Qwen3-Next、Kimi）:
      多數線性／state 層 + 少數全域 attention 層
      -> 在長序列效率與精確全域檢索之間折衷
```

DeepSeek 的 MLA 與 GLM／Qwen3 的 GQA 都是 **exact softmax 路線的 KV-cache 最佳化**：前者透過 latent 壓縮降低每個歷史 token 的儲存量，後者以更少的 K/V heads 降低重複。它們不會把全域 `QK^T` 的拓撲改成線性；因此在極長 context 的 prefill 上，仍會面對全域 attention 的成本，但能保留直接讀取任意歷史 token 的能力。

Qwen3-Next 的 Gated DeltaNet 與 Kimi 的 KDA 則採 **混合線性 attention 路線**。有限 recurrent state 可降低長度擴張下的快取與計算壓力，但 state 必須壓縮過去資訊；交錯的全域 attention layer 用來恢復直接檢索及降低壓縮遺失風險。實務上不應僅比較理論 `O(n)`：kernel 成熟度、head／state 維度、batch size、context 長度與任務是否依賴精確遠距 retrieval 都會改變結果。

### 選型摘要

| 工作負載 | 較契合的設計 | 原因與注意事項 |
|---|---|---|
| 高併發 chat / coding decode | GQA 或 MLA | KV-cache 與 memory bandwidth 通常是主要瓶頸；MLA 以較複雜投影換取更高壓縮率。 |
| 需要精確讀取任意遠距 token | GQA / MLA 的全域 attention | 仍保有每個歷史 token 的可尋址 K/V 表示；成本會隨 context 增長。 |
| 百萬 token 級 prefill 或長輸出 | DeltaNet / KDA hybrid | 多數層可避免全域二次成本；須用長 context retrieval、推理與實際 throughput 驗證品質。 |
| 參數容量與訓練成本 | MoE | MoE 與 attention 可互補，但只降低 FFN 的稀疏啟用成本，不能取代 KV-cache 或 attention 最佳化。 |

**來源：** [DeepSeek-V3 技術報告（MLA）](https://arxiv.org/abs/2412.19437)、[Qwen3-Next 官方公告](https://qwen.ai/blog?id=e34c4305036ce60d55a0791b170337c2b70ae51d)、[GLM-4.5 技術報告](https://arxiv.org/abs/2508.06471)、[智譜 GLM-4.5 技術頁](https://bigmodel.cn/technology-report)、[Kimi Linear 技術報告](https://arxiv.org/abs/2510.26692)

**閉源模型補充來源：** [Anthropic：Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)、[OpenAI：Prompt Caching](https://openai.com/index/api-prompt-caching/)、[OpenAI：Sparse Transformer 研究](https://openai.com/index/sparse-transformer/)、[Gemini 1.0 技術報告](https://deepmind.google/gemini/gemini_1_report.pdf)、[Gemini 1.5 MoE 公告](https://blog.google/innovation-and-ai/products/google-gemini-next-generation-model-february-2024/)

---

## 15. 截至 2026-08：公開架構的最佳化路線與判讀

> **公開資訊邊界：** 以下只列出模型供應商在 model card、技術報告或原始碼中公開的架構。GPT、Claude 與後續 Gemini 產品的完整 attention 拓撲並未全面公開；不能因為某個 API 提供 prompt cache 或長 context，就推論其內部採用 MLA、GQA、KDA 或特定 sparse pattern。

### 15.1 先依瓶頸分類，而非只看名詞

| 瓶頸 | 典型機制 | 作用 | 重要限制 |
|---|---|---|---|
| 長 prompt 的 prefill | sliding-window / banded sparse、linear attention、hybrid attention | 減少或避免所有 token 兩兩計算；dense attention 的 prefill 原本約為 `O(n^2)` | sparse / linear 可能犧牲任意兩 token 的直接精確互看 |
| 長 context 的逐 token decode | MQA、GQA、MLA、KV quantization | 降低每層 KV cache 的容量與讀取頻寬 | MQA/GQA/MLA 不會根本消除 dense prefill 的 `O(n^2)` |
| GPU attention kernel | FlashAttention 系列 | 以 tiling 與 I/O-aware kernel 減少 HBM 往返；輸出仍是 exact softmax attention | 演算法複雜度仍是 dense attention 的複雜度 |
| 多請求 serving | PagedAttention、continuous batching、prefix/prompt caching | 改善 KV cache 配置、碎片與 batch 利用率 | 屬 runtime / serving 技術，不是模型 attention topology |
| 位置與長度外推 | RoPE、YaRN、ALiBi | 提供位置關係或將可用 context window 延長 | 本身不會降低 attention 的基本運算量 |

### 15.2 exact attention 與線性／稀疏 attention 不可混為一談

| 機制 | 是否保留全域 exact softmax attention | 核心好處 |
|---|---|---|
| GQA / MQA | 是 | 多個 Query head 共用較少 K/V head；顯著縮小 KV cache |
| MLA | 是（KV 以 latent 形式壓縮） | 在保留 softmax attention 互動的前提下，壓縮 decode 所需 KV cache |
| FlashAttention | 是 | 不改數學結果，只改善 GPU 記憶體 I/O 與 kernel 執行效率 |
| sliding-window / block sparse | 僅在允許的稀疏連結上是 exact | 將互看範圍限制為 local window、block 或少數 global token |
| Gated DeltaNet / Kimi Delta Attention | 否 | 以固定大小 recurrent state 壓縮歷史，讓長序列成本更接近線性 |
| hybrid | 部分層是、部分層否 | 以線性層處理大多數 token 流，再以全域 attention 層保留精確長距 retrieval |

### 15.3 已公開模型案例

| 供應商／模型 | 已公開 attention 路線 | 主要解決的成本 |
|---|---|---|
| DeepSeek-V2 / V3 / R1 | **Multi-head Latent Attention (MLA)** | 將 K/V 壓成 latent cache，降低長 context decode 的顯存與 memory bandwidth；仍屬 softmax attention 路線。|
| Qwen3 傳統 Transformer 系列 | **Grouped-Query Attention (GQA)** | 以較少 K/V heads 換取較小 KV cache。|
| Qwen3-Next、Qwen3.5 之後的 hybrid 系列 | **Gated DeltaNet + Gated Attention** | 多數層以 fixed-state linear/recurrent 機制壓低長序列成本，定期插入全域 attention 層維持精確 retrieval。|
| Kimi K3 | **Kimi Delta Attention (KDA) + Gated MLA**，約 3:1；另有 **Attention Residuals** | KDA 壓低大多數層的長序列成本，Gated MLA 提供全域 attention；AttnRes 改善跨層資訊流。|
| GLM-4.5 | **Partial-RoPE GQA + QK-Norm** | GQA 降低 KV cache；partial RoPE 與 QK normalization 著重長上下文位置處理與 attention 穩定性。|
| OpenAI gpt-oss | **GQA + local banded sparse / dense 交替 + RoPE/YaRN**；訓練採 FlashAttention | 局部層省計算、dense 層維持全域傳遞，並以 GQA 降低 decode cache。|
| Gemini 1.0 | **Multi-Query Attention (MQA)**（公開技術報告） | 以單組 K/V 服務多個 Query heads，降低自回歸 decode 的 cache／頻寬成本。|

### 15.4 對長 context 的正確解讀

「支援 1M context」不等於每個 token 都被同等精準地檢索。GQA、MLA 與 FlashAttention 的主要價值是讓完整 attention 更能放得下、跑得動；sparse、linear 與 hybrid attention 則是在成本、遠距精確 retrieval 與模型品質間作結構性取捨。對 agent 系統而言，重要規則仍應以分層指令、檢索、測試與 CI 落實，而不應只依賴更大的 context window。

**更新參考：** [DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437)、[Qwen hybrid attention 說明](https://qwen.ai/blog?id=qwen3.8-flash-next)、[Kimi K3 官方技術公開](https://www.kimi.com/news/kimi-k3-open-source)、[GLM-4.5 Technical Report](https://arxiv.org/abs/2508.06471)、[OpenAI gpt-oss model card](https://deploymentsafety.openai.com/gpt-oss/a2)、[Gemini 1.0 Technical Report](https://deepmind.google/gemini/gemini_1_report.pdf)
