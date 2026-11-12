# AI Scaling Laws

描述模型效能（通常以 loss 衡量）如何隨**模型參數量**、**訓練資料量**、**運算量**三者變化的經驗規律。是過去五年推動大模型軍備競賽的核心理論依據。

> 2026-11-12 新增 10 張圖示（冪律、演進時間軸、Gopher 對 Chinchilla、D/N 比例、突現能力、推論期 scaling、Data Wall、MoE、適用範圍、常見誤解）；曲線圖皆為示意，不是實測數據，數值與論述皆取自本文既有內容。

---

## 一、核心概念

Scaling Law 的基本觀察：在合理範圍內，模型的 test loss 與規模呈現**冪律關係（power law）**，而非隨機或飽和：

```
L(x) ≈ (x_c / x)^α
```

- `x`：規模變數（參數量 N、資料量 D、或運算量 C）
- `α`：該變數的 scaling 指數（決定報酬遞減的速度）
- `x_c`：常數，代表達到 loss=1 所需的規模

三個變數同時放大時，loss 會沿著一條平滑曲線下降，**幾乎沒有明顯的天花板**（在已測試的規模範圍內）——這是與傳統機器學習「越大越容易 overfit」直覺相反的關鍵發現。

![圖：冪律關係在線性座標與 log-log 座標上的樣子，及 Kaplan 的三個指數](figures/scaling-laws-power-law.svg)

---

## 二、關鍵論文與演進

| 年份 | 論文 / 團隊 | 核心貢獻 |
|---|---|---|
| 2020 | Kaplan et al.（OpenAI）*Scaling Laws for Neural Language Models* | 首次系統性提出 N、D、C 三變數冪律關係 |
| 2022 | Hoffmann et al.（DeepMind）*Chinchilla* | 推翻 Kaplan 的資料配比，證明先前模型「參數過多、資料過少」 |
| 2022 | Wei et al.（Google）*Emergent Abilities* | 指出某些能力在跨過規模門檻後才「突現」，而非平滑漸進 |
| 2023–2024 | LLaMA / LLaMA 2/3 系列（Meta） | 刻意用遠超 Chinchilla-optimal 的資料量訓練小模型，換取推論期效率 |
| 2024 | 多篇 *Inference / Test-time Scaling* 研究 | 把 scaling 焦點從訓練期轉向推論期（見第五節） |
| 2024–2025 | Data-constrained scaling（如 Muennighoff et al.） | 探討高品質資料見頂後如何持續 scaling |

![圖：Scaling Law 從 2020 到 2025 年的演進時間軸](figures/scaling-laws-timeline.svg)

---

## 三、Kaplan Scaling Laws（2020）

OpenAI 團隊訓練一系列 GPT-2 規模的模型，發現 loss 與三個變數各自獨立呈冪律關係：

| 變數 | 關係 | 意義 |
|---|---|---|
| 參數量 N | `L(N) ∝ N^-0.076` | 固定資料與運算，模型越大 loss 越低 |
| 資料量 D | `L(D) ∝ D^-0.095` | 固定模型與運算，資料越多 loss 越低 |
| 運算量 C | `L(C) ∝ C^-0.050` | 固定其他條件，算力投入越多 loss 越低 |

**結論（後來被證明有誤）**：在固定運算預算下，應優先放大模型參數量，資料量可以相對少——這直接催生了 GPT-3（175B 參數，僅 300B tokens）等「參數優先」的巨型模型路線。

### 實際案例

| 案例 | 參數量 | 訓練 tokens | D/N 比例 | 說明 |
|---|---|---|---|---|
| GPT-3（OpenAI，2020）| 175B | 300B | 約 1.7 | Kaplan 結論最著名的實踐者，直接依「參數優先」路線放大到 175B，論文本身即引用 Kaplan et al. 的公式規劃訓練規模 |
| Gopher（DeepMind，2021）| 280B | 300B | 約 1.1 | 同樣走參數優先路線；後來正是 DeepMind 自己用 Gopher 當對照組，證明此路線嚴重欠訓練（見第四節 Chinchilla vs Gopher）|
| Megatron-Turing NLG（Microsoft + NVIDIA，2021）| 530B | 約 270B | 約 0.5 | 當時全球最大的公開稠密模型，D/N 比例甚至低於 GPT-3、Gopher，是「參數優先」路線走到極端的代表案例 |
| Jurassic-1 Jumbo（AI21 Labs，2021）| 178B | 300B | 約 1.7 | 與 GPT-3 規模、配比相近，同期業界普遍採用類似的參數優先假設 |
| GPT-3 論文自身的伏筆 | — | — | — | 論文附錄圖表顯示，訓練結束時 validation loss **仍在下降、未收斂**，事後被視為「模型仍嚴重欠訓練」的早期訊號，直接埋下 2022 年 Chinchilla 推翻此路線的伏筆 |

> 這些案例的共同點：2020–2021 年間主流大模型幾乎都遵循 Kaplan 團隊「參數優先、資料相對少」的配比建議，直到 Chinchilla（見第四節）用實驗證明這條路線效率低下，業界配比才整體轉向。

---

## 四、Chinchilla Scaling Laws（2022）——修正版

DeepMind 用超過 400 個不同規模的模型重新做實驗，發現 Kaplan 團隊的方法論有缺陷（未正確處理 learning rate schedule），得出不同結論：

### Compute-optimal 配比

給定固定運算預算 `C`，最佳的參數量 `N` 與資料量 `D` 應**同比例增長**：

```
N_opt ∝ C^0.5
D_opt ∝ C^0.5
```

經驗法則：**每個參數約需 20 個訓練 token**（`D ≈ 20N`）。

### 實驗證據：Chinchilla vs Gopher

| 模型 | 參數量 | 訓練 tokens | 運算量（FLOPs，近似）|
|---|---|---|---|
| Gopher（舊路線）| 280B | 300B | 相同 |
| Chinchilla（新配比）| 70B | 1.4T | 相同 |

結果：**參數量僅 1/4 的 Chinchilla 在多數 benchmark 上顯著超越 Gopher**——證明先前一代大模型「嚴重欠訓練（undertrained）」，把過多運算浪費在參數規模而非資料量上。

![圖：同運算量下 Gopher 與 Chinchilla 的參數量與訓練 tokens 配比](figures/scaling-laws-chinchilla-gopher.svg)

### 影響

此後主流模型（GPT-4、Claude、Gemini 等）訓練配比大幅轉向「加大資料量」，而非單純堆參數。

### 實際案例

| 案例 | D/N 比例（相對 Chinchilla 的 20）| 說明 |
|---|---|---|
| LLaMA（Meta，2023）| 遠超 20（7B 模型用約 1T token，比例約 140）| 論文明言參考 Hoffmann et al.，但**刻意違背 compute-optimal**：訓練成本不是唯一考量，故意「訓練更久」換取推論時更小、更省錢的模型——這是文件第二節提到「LLaMA 系列」策略的具體數字 |
| LLaMA 2（Meta，2023）| 更高（7B–70B 均訓練 2T token）| 延續同一策略，資料量進一步加大 |
| LLaMA 3（Meta，2024）| 更極端（405B 模型用 15T+ token，比例約 37，但遠超 405B 對應的 Chinchilla-optimal 資料量約 8T）| 文件第八節「Data Wall」案例中同一模型，同時也是 Chinchilla 配比被大幅突破的代表 |
| MosaicML MPT 系列（2023）| 接近 20（官方明確標榜「Chinchilla-optimal」訓練）| 業界少數嚴格遵循原始配比訓練的公開案例，作為對照組 |
| Besiroglu et al. 2024，*Chinchilla Scaling: A Replication Attempt* | — | 重新分析 DeepMind 論文附錄公開的實驗數據，發現原始論文其中一種擬合方法（parametric loss fit）估計的信賴區間過窄、與其他兩種方法結果不完全一致，對外界一度引發「Chinchilla 結論是否可靠」的討論；但三種方法**共同結論**（Gopher 欠訓練、需要更多資料）並未被推翻，僅精確指數估計值有爭議 |

> 這些案例顯示：Chinchilla 提出的 `D≈20N` 是**訓練損失最小化**下的最優解，但業界實務上常有除了 loss 以外的考量（如推論成本、部署裝置限制），因此主動偏離這個比例、往資料量更多的方向去訓練，而非盲目照搬。

![圖：各代表模型的訓練 tokens 與參數量比例 D/N（對數座標）](figures/scaling-laws-dn-ratio.svg)

---

## 五、Emergent Abilities（突現能力）

Wei et al. 觀察到：某些任務（如多步驟算術推理、指令遵循）的表現曲線並非平滑冪律，而是在跨過某個規模門檻後**急遽跳升**，小模型上幾乎是隨機水準。

```
表現
 │                              ●━━━●━━━● (突然跳升)
 │                    ●
 │        ●━━━●━━━●
 │  ●
 └──────────────────────────────── 規模 →
       (隨機水準持平)      (門檻)
```

### 兩派解讀

| 觀點 | 論述 |
|---|---|
| 真實突現 | 模型內部形成新的表徵或電路（circuit），能力質變 |
| 測量假象（Schaefer et al. 2023）| 突現是**評估指標的非線性**（如 exact-match 這種離散指標）造成的錯覺；換成連續指標（如 token 機率）後曲線其實平滑 |

> 對實務的啟示：小規模模型的測試結果**不能線性外推**判斷大模型是否具備某能力，需保留驗證空間。

![圖：離散指標與連續指標下突現能力的差異，以及兩派解讀](figures/scaling-laws-emergent.svg)

### 實際案例

| 案例 | 出處 | 觀察到的突現行為 |
|---|---|---|
| 三位數加法 / 模運算（modular arithmetic）| Wei et al. 2022（原始論文引用的 BIG-Bench 任務）| GPT-3 系列在約 13B 以下準確率接近 0（隨機猜），跨過某個規模門檻後才突然跳升到高準確率 |
| Chain-of-Thought prompting 本身的效果 | Wei et al. 2022b，*Chain-of-Thought Prompting Elicits Reasoning* | CoT 提示對 <100B 的模型幾乎沒用（甚至有害），但在 PaLM 540B、GPT-3 175B 等大模型上大幅提升多步驟推理準確率——「CoT 有效」這件事本身就是一種突現能力 |
| Few-shot in-context learning | Brown et al. 2020，GPT-3 論文 | GPT-3 不需要梯度更新，僅靠 prompt 中的少量範例就能做新任務，這種能力在更小的 GPT-2 規模上幾乎不存在 |
| 笑話解釋 / 邏輯推理鏈 | Google PaLM 540B 論文（2022）| 540B 版本能解釋為何某個笑話好笑、進行多步驟邏輯推導，62B 版本則明顯做不到 |
| 音標轉寫（IPA transliteration）、單詞還原（word unscrambling）| Wei et al. 2022（BIG-Bench 任務集）| 同屬論文中列舉的「跳躍型」曲線任務，常被拿來當作突現能力的代表圖例 |
| 反例：Schaefer et al. 2023 對上述任務的重新分析 | *Are Emergent Abilities of Large Language Models a Mirage?*（NeurIPS 2023）| 把「三位數加法」等任務的評分方式從 exact-match（全對才算對）換成連續指標（如逐字元準確率）後，原本的跳躍曲線變成**平滑漸進**，支持「測量假象」一派的論點 |
| GPT-4 技術報告中的能力預測（OpenAI, 2023）| GPT-4 System Card | OpenAI 宣稱透過訓練初期的 loss 曲線，成功「預測」GPT-4 在部分 benchmark 上的最終表現，顯示至少某些能力提升仍循可預測的 scaling 曲線，而非純粹隨機突現 |
| 易混淆案例：Grokking（Power et al. 2022）| *Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets* | 常被誤認為與 emergent abilities 是同一現象，但自變數不同：Grokking 是**同一個固定大小的模型**訓練步數拉長後，在訓練 loss 早已收斂許久後才「突然」學會泛化；emergent abilities 則是**模型規模（參數/資料/運算）跨過門檻**才突現能力。兩者都是「突然跳升」的曲線，但一個是訓練時間軸上的現象，一個是規模軸上的現象，不應混為一談 |

> 這些案例也呼應第九節的誤解澄清：突現能力究竟是模型「真的學會了新東西」，還是「evaluation 指標本身不夠平滑」，至今仍是學界未有共識的開放問題。

---

## 六、Scaling 的三個維度總覽

| 維度 | 說明 | 代表策略 |
|---|---|---|
| **參數 scaling** | 增加模型權重數量 | 更深/更寬的 Transformer、MoE |
| **資料 scaling** | 增加訓練 token 數 | 網路爬蟲擴增、合成資料、多輪 epoch |
| **運算 scaling** | 增加訓練 FLOPs（= N × D 的函數）| 更多 GPU/TPU、更長訓練時間 |
| **推論期 scaling**（新興）| 增加推論時的運算（見下節）| Chain-of-thought、多次採樣投票、樹狀搜尋 |

---

## 七、Inference-Time / Test-Time Scaling（2024 年後新戰場）

當「預訓練 scaling」的邊際報酬逐漸放緩（高品質文字資料接近見頂），業界焦點轉向**推論時多花運算換取更好答案**：

| 技術 | 原理 |
|---|---|
| Chain-of-Thought（CoT）| 讓模型「多想幾步」再回答，等同於用更多 token 换取推理深度 |
| Self-consistency / 多次採樣 | 同一問題生成多個答案，多數決或用 verifier 挑選 |
| Best-of-N / 樹狀搜尋 | 生成多條路徑，用 reward model 評分後選最佳 |
| 專用推理模型（如 OpenAI o 系列、Claude 的 extended thinking）| 訓練模型學會「何時該想更久」，把推論運算轉化為可控的 effort level |

**核心發現**：推論期運算與模型能力之間**也存在類似冪律關係**——同一個模型，允許它「想更久」，效果可媲美訓練一個大幾倍的模型，且成本結構不同（一次性訓練成本 vs. 按次付費的推論成本）。

這也是 Claude Code 中 `/effort` 指令（low/medium/high/xhigh/max）背後的理論基礎：讓使用者在「推論成本」與「答案品質」之間動態取捨。

![圖：推論期 scaling 的報酬曲線與四類技術](figures/scaling-laws-inference-time.svg)

### 實際案例

| 案例 | 技術 | 觀察到的 scaling 效果 |
|---|---|---|
| OpenAI o1（2024）| 內建 CoT + RL 訓練的推理鏈 | 官方公布的曲線顯示：AIME 數學競賽準確率隨**推論期運算量**呈近似對數線性（log-linear）成長，與訓練期 compute scaling 曲線的形狀相似 |
| OpenAI o3 / o3-mini（2024–2025）| 同上，並可調整 reasoning effort（low/medium/high）| 在 ARC-AGI、競賽數學等 benchmark 上，effort 調高、推論成本上升，正確率隨之提升，呈報酬遞減曲線 |
| DeepSeek-R1（2025）| 純 RL（GRPO）誘導出的長 CoT 推理 | 證明不需要大量人工標註的 CoT 資料，模型可透過 RL 自行「學會想更久」，且推理長度與任務難度正相關 |
| Claude 的 extended thinking（含 Claude Code `/effort`）| 可控 thinking budget（token 上限）| thinking budget 越高，複雜推理與 coding 任務準確率越高，直到達到邊際效益遞減的平台期 |
| Google AlphaCode / AlphaCode 2 | 大量採樣（單題生成數萬到百萬個候選解）+ 篩選 | 競賽程式解題率隨採樣數量近似對數成長；靠推論期暴力搜尋彌補模型本身推理深度不足 |
| Self-consistency（Wang et al. 2022，GSM8K 等數學題）| 同一問題採樣多次、多數決 | 採樣路徑數從 1 增加到 40，準確率持續上升但邊際效益遞減，驗證「多次推論 ≈ 更強推理」的早期實證 |
| AlphaProof / AlphaGeometry（DeepMind，2024 IMO）| 樹狀搜尋 + 形式化驗證器（verifier）| 用大量推論期搜尋與自我對弈驗證，在國際數學奧林匹亞（IMO）題目上達到銀牌等級表現，凸顯 verifier 品質對推論期 scaling 上限的決定性影響 |
| Snell et al. 2024（DeepMind + UC Berkeley），*Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters* | 首篇正式提出「推論期運算 scaling law」的學術論文 | 證明依問題難度**動態分配**推論運算（而非固定策略），在同等運算預算下效率可媲美 14 倍大的模型參數 scaling；是 o1、R1 等推理模型背後的理論源頭，而非只有產品層級的應用 |
| Google Gemini 2.0 Flash Thinking / Deep Think（2024–2025）| 同 OpenAI o 系列的可控思考模式 | 驗證多家廠商（OpenAI、Google、Anthropic、DeepSeek）各自獨立收斂到「可控推論期運算」路線，並非單一公司的個案 |

> 共同模式：這些案例都把「訓練一次、固定权重」變成「訓練一次、推論時動態決定要花多少運算」，把 scaling 的自由度從「模型多大」轉移到「這一題要想多久」。

---

## 八、資料見頂問題（Data Wall）

高品質公開文字資料估計在 **數十兆（trillions）token** 量級見頂，可能早於 2028 年被主流模型訓練用盡。因應策略：

| 策略 | 說明 | 風險 |
|---|---|---|
| 多輪 epoch（repeat data）| 同一資料重複訓練多次 | 超過約 4 epoch 後報酬急遽遞減 |
| 合成資料（synthetic data）| 用強模型生成訓練資料餵給新模型 | 可能導致「model collapse」（分布坍縮）|
| 多模態資料 | 納入圖片、影片、程式碼、音訊等 | 資料類型間的 transfer 效果仍在研究中 |
| 提升資料品質而非數量 | 精煉/過濾（如 FineWeb、textbook-quality data）| 品質評估本身仍缺乏統一標準 |
| 轉向推論期 scaling | 見第七節 | 需要額外的 RL / verifier 訓練成本 |

![圖：資料見頂的五種因應策略與各自風險](figures/scaling-laws-data-wall.svg)

### 實際案例

| 案例 | 對應策略 | 說明 |
|---|---|---|
| Epoch AI 研究（2024）| — | 估計高品質公開文字資料庫存量約 300 兆 token，主流模型若持續依現有速度擴大訓練資料，約 **2026–2032 年間**會用盡；也是文件 Data Wall 論述的主要引用來源 |
| Muennighoff et al. 2023，*Scaling Data-Constrained Language Models* | 多輪 epoch 的理論依據 | 首篇系統性研究「資料量固定時如何分配運算」的論文：重複訓練同一資料**到約 4 epoch 前**，效益接近使用等量全新資料；超過後報酬急遽遞減——這就是表格中「多輪 epoch」策略與第二節引用來源的具體實證，也是「超過約 4 epoch」這個經驗值的出處 |
| Llama 3（Meta，2024）| 多輪 epoch + 大量資料 | 405B 模型用 **15T+ token** 訓練，遠超 Chinchilla-optimal 比例（`D≈20N` 只需約 8T），刻意「餵過量資料」換取推論期效率，同時逼近可取得公開資料的規模上限 |
| Microsoft Phi 系列（Phi-1/2/3/4）| 合成資料 | 用強模型生成「教科書等級」的高品質合成資料訓練小模型（1.3B–14B），證明資料**品質**可以部分取代數量，小模型在推理 benchmark 上逼近大幾倍的模型 |
| Model Collapse 研究（Shumailov et al., *Nature* 2024）| 合成資料的風險 | 證實遞迴地用模型生成的資料訓練下一代模型，會導致輸出分布逐漸坍縮、多樣性喪失——驗證文件表格中「可能導致 model collapse」的風險並非理論假設 |
| Reddit–Google 資料授權（2024，年約 $60M）| 資料授權採購 | 高品質公開資料見頂後，各家轉向**付費授權**取得非公開/半公開語料（論壇、問答社群）|
|《紐約時報》v. OpenAI/Microsoft 訴訟（2023 起）| 資料版權爭議 | 反映公開網路資料的「可自由使用」假設正被版權訴訟挑戰，間接壓縮可合法取得的高品質文字資料池 |
| OpenAI 用 Whisper 轉錄 YouTube 影片（媒體報導，2024）| 多模態資料 | 將影片語音轉成文字補充訓練語料，是文件「多模態資料」策略在文字資料見頂後的實際應用之一 |
| FineWeb / FineWeb-Edu（Hugging Face，2024）| 提升資料品質 | 對 Common Crawl 做大規模品質過濾與去重，證明同樣的 token 預算下，過濾後的資料集能訓練出效能更好的模型，驗證「品質優於數量」策略 |

---

## 九、常見誤解澄清

| 誤解 | 實際情況 |
|---|---|
| 「模型越大就一定越聰明」 | 需搭配對應資料量（Chinchilla-optimal），否則是欠訓練 |
| 「Scaling Law 是物理定律，永遠成立」 | 是**特定資料分布與架構下的經驗觀察**，換架構、換資料分布後指數會變 |
| 「Emergent abilities 證明模型有『頓悟』」 | 部分被認為是評估指標離散化造成的假象（見第五節）|
| 「小模型 scaling 曲線可以直接外推到大模型」 | 常用於估算大模型表現，但突現能力與訓練不穩定性使外推有誤差 |
| 「只要堆算力就能解決一切」 | 運算量需要「正確配比」到參數與資料上，盲目堆單一維度效益遞減 |
| 「Scaling Law 只適用於預訓練」 | 只是最初、最經典的版本；概念已延伸到推論期、post-training/RL、微調等各階段（見第十一節） |

![圖：Scaling Law 的六個常見誤解與實際情況](figures/scaling-laws-myths.svg)

---

## 十、延伸方向（研究前沿）

- **MoE（Mixture of Experts）scaling**：稀疏啟用架構下，「有效參數量」與「總參數量」的 scaling 行為不同，需要獨立的 scaling law（實際案例見下）
- **多模態 scaling**：文字、圖像、影片混合訓練時的最佳配比仍無定論（實際案例見下）
- **RL / post-training scaling**：RLHF、RLAIF 等對齊階段的運算投入與模型行為改善之間的關係，是否也遵循冪律（實際案例見下）
- **長 context scaling**：context window 長度對訓練與推論運算的 scaling 影響（通常是二次方或近似線性，視 attention 架構而定；實際案例見下）

### MoE scaling 實際案例

| 案例 | 說明 |
|---|---|
| GShard（Lepikhin et al. 2020，Google）| 早期大規模 MoE 實證，用於機器翻譯，總參數量推到 600B，證明稀疏架構能在**相近運算成本**下大幅超越稠密模型的容量上限 |
| Switch Transformer（Fedus et al. 2021，Google）| 把 MoE 推到 1.6T 參數，簡化路由機制為「每 token 只選 1 個專家」，論文明確比較稀疏 scaling 與稠密 scaling 曲線，發現**相同運算預算下稀疏模型收斂更快** |
| Clark et al. 2022（DeepMind），*Unified Scaling Laws for Routed Language Models* | 首篇專門為 MoE／路由模型推導 scaling law 的論文：證明「總參數量」不能直接套用稠密模型的 Kaplan/Chinchilla 公式，必須改用**有效參數量（effective parameter count）**才能準確預測 loss，兩者的關係本身也是一條獨立曲線 |
| Krajewski et al. 2024，*Scaling Laws for Fine-Grained Mixture of Experts* | 進一步研究「專家粒度」（把每個專家切得更細、數量更多 vs 更粗、數量更少）對 scaling 曲線的影響，發現細粒度專家配置能在同運算量下達到更低 loss，但路由與通訊開銷也隨之增加 |
| Mixtral 8x7B / 8x22B（Mistral AI，2023–2024）| 開源權重的實際 MoE 產品：8x7B 總參數量約 47B，但每個 token 只啟用約 13B（2 個專家），效能逼近甚至超越同期 70B 稠密模型，是「有效參數量遠小於總參數量」的具體例證 |
| DeepSeek-V2 / V3（DeepSeek，2024）| 採用「細粒度專家 + 共享專家（shared expert）」設計：V3 總參數量 671B，每 token 僅啟用約 37B，在大幅壓低推論成本的同時維持接近稠密旗艦模型的效能，是目前公開文獻中 MoE scaling 效率最極端的案例之一 |
| GPT-4（OpenAI，傳言/洩漏資訊，未經官方證實）| 業界廣泛流傳 GPT-4 採用 MoE 架構，總參數量約 1.8T、每 token 啟用約 220B——若屬實，則是文件第二節提到「主流模型轉向資料量」之外，另一條「用稀疏架構繞開參數量瓶頸」的路線；因缺乏官方確認，僅供參考 |

> 核心啟示：MoE 的「參數量」數字容易誤導——比較不同模型時，應該看**有效參數量（推論時實際啟用的參數）**而非總參數量，這也是為什麼 Clark et al. 認為 MoE 需要一套獨立於 Kaplan/Chinchilla 的 scaling law。

![圖：MoE 模型的總參數量與每 token 啟用參數量](figures/scaling-laws-moe-active.svg)

### Post-training / RL scaling 實際案例

| 案例 | 說明 |
|---|---|
| Ouyang et al. 2022（OpenAI），*InstructGPT* | RLHF 最著名的早期示範：僅 **1.3B 參數**經過 RLHF 對齊後的輸出，人類評分者的偏好度**超過未對齊的 175B GPT-3 base 模型**——首次證明「post-training 投入」可以彌補甚至超越單純放大預訓練規模的效果 |
| Gao, Schulman & Hilton 2022（OpenAI），*Scaling Laws for Reward Model Overoptimization* | 直接研究 RL 階段的 scaling 行為：發現 policy 對 reward model 的優化程度（以與初始模型的 KL 距離衡量）越高，proxy reward 與真實人類偏好會逐漸**脫鉤**，且此脫鉤曲線本身也呈現可預測的規律；reward model 越大，能抵抗 overoptimization 的空間也越大 |
| DeepSeek-R1-Zero（DeepSeek，2025）| 完全跳過 SFT 暖身，直接用純 RL（GRPO）從 base 模型訓練出推理能力，證明推理能力可以單純從 RL 訓練步數與運算量中「長出來」，且能力隨 RL 訓練量持續提升 |
| LLaMA 2（Meta，2023）| 論文揭露對齊流程跑了 **5 輪迭代 RLHF**，每輪重新蒐集人類偏好資料、重新訓練 reward model，並觀察到 reward model 品質與訓練資料規模同步提升時，最終對齊效果才跟著提升——凸顯 post-training scaling 不只看運算量，還要看 reward model 本身的 scaling |
| Anthropic Constitutional AI / RLAIF（2022 起）| 用 AI 回饋取代部分人類回饋來擴大 RL 訓練資料規模，繞開人類標註產能的瓶頸，是「用更多運算換取更多對齊訓練資料」的具體實作 |
| OpenAI o1 / o3 官方說法（2024–2025）| 官方明確將 RL 訓練階段的運算量稱為**獨立於預訓練的第二條 scaling 軸線**：除了訓練期 compute、推論期 compute，「RL 訓練期 compute」被視為第三個可獨立投入、獨立產生報酬遞減曲線的資源維度 |

> 與預訓練 scaling 不同，post-training / RL scaling 的曲線**更早出現飽和**，且高度依賴 reward model 或 verifier 的品質上限——reward model 本身不準，policy 訓練得再久也只是在優化一個錯誤的目標（即上表 Gao et al. 描述的 overoptimization 現象）。

### Long-context scaling 實際案例

| 案例 | 說明 |
|---|---|
| FlashAttention（Dao et al. 2022）| 並非拉長 context 本身，而是讓標準 attention 的記憶體/運算瓶頸從「隨長度平方增長」變成 IO-aware 的可行實作，是後續所有商用長 context 模型的**前提技術**——沒有這類優化，context 拉長的硬體成本會直接爆炸 |
| Gemini 1.5 Pro（Google，2024）| 技術報告專門討論「long-context scaling」：context window 一舉推進到 1M（後續版本 2M）token，並用「needle in a haystack」測試證明在超長輸入中仍能近乎完美檢索指定資訊 |
| Claude 系列（Anthropic）| context window 從早期數千 token，逐步擴大到 100K、200K，最新版本已提供 1M token beta——是 Claude Code 本身能處理大型 codebase 對話的基礎 |
| Ring Attention（Liu et al. 2023，UC Berkeley）| 把 attention 運算拆分到多台設備上分散計算，讓 context 長度的 scaling 從「單卡記憶體上限」變成「近似隨裝置數線性增長」，是拉到百萬級 token 的關鍵演算法之一 |
| RoPE Scaling / Position Interpolation / YaRN（Chen et al. 2023 等）| 讓一個**已經訓練好、context 較短**的模型，事後用內插或改寫位置編碼的方式延伸到更長 context，而不需要從頭重新訓練——是低成本擴充既有模型 context 的常見手法 |
| Mamba / State Space Models（Gu & Dao, 2023）| 用線性時間複雜度的序列建模架構取代二次方複雜度的 attention，是「換架構」而非「優化 attention」來解決 long-context scaling 問題的代表路線，惟尚未在旗艦級商用模型中全面取代 Transformer |
| Needle in a Haystack 測試（Greg Kamradt, 2023）| 業界標準的長 context 評測方法，發現許多模型雖然「宣稱」context window 很大，但實際**有效可用**的長度遠小於名目長度（尤其資訊藏在輸入中段時準確率明顯下滑）——提醒「context window 大小」與「context scaling 是否真正有效」是兩回事 |

> 與其他 scaling 曲線不同，long-context scaling 同時牽涉**演算法（如何讓 attention 不要吃爆記憶體）**與**訓練資料（模型是否真的見過夠多長文本範例）**兩個獨立瓶頸，單純擴大宣稱的 context window 數字，不代表模型真的能有效利用這麼長的輸入。

### 多模態 scaling 實際案例

| 案例 | 說明 |
|---|---|
| Henighan et al. 2020（OpenAI），*Scaling Laws for Autoregressive Generative Modeling* | 繼 Kaplan 之後，同一團隊把 scaling law 延伸到**圖像、影片、圖像轉文字（image-to-text）**等生成任務，發現這些模態各自也呈現與文字類似的冪律關係——證明 scaling law 不是文字模型獨有的現象 |
| Aghajanyan et al. 2023（Meta），*Scaling Laws for Generative Mixed-Modal Language Models* | 目前最直接針對「混合模態」的 scaling 研究：訓練同時包含文字、圖像、語音、程式碼的模型時，發現不同模態間存在**競爭（competition）與協同（synergy）**兩種效果，取決於模態混合比例——某些配比下模態互相拖累，某些配比下互相增益，最佳比例目前仍無定論（呼應上方「配比仍無定論」的論述）|
| CLIP（OpenAI，2021）| 對比學習訓練圖文配對模型，論文附錄顯示 zero-shot 準確率隨模型規模與資料量呈現平滑冪律成長，是視覺-語言領域最早的 scaling 實證之一 |
| Flamingo（DeepMind，2022）| 視覺-語言少樣本學習模型，將預訓練 LLM 與視覺編碼器結合，驗證「凍結大型語言模型 + 少量視覺參數」也能呈現隨規模平滑提升的 scaling 曲線 |
| Gemini 1.0 / 1.5（Google，2023–2024）| 與「先訓文字模型、再接視覺模組」的做法不同，Gemini 從頭以**原生多模態（native multimodal）**方式聯合訓練文字、圖像、音訊、影片，官方技術報告強調此設計是為了讓 scaling 效益能跨模態共享 |
| Sora（OpenAI，2024）| 影片生成模型技術報告明確展示：同一 prompt 在不同訓練運算量下的生成結果並排比較，畫質與時間一致性隨運算量增加呈現**可預測的漸進提升**，直接把「運算量 scaling」的敘事从文字模型套用到影片生成 |
| Chameleon（Meta，2024）| 採用「early fusion」架構，把圖像也轉成離散 token 與文字混合訓練（而非圖文分開編碼再融合），代表多模態 scaling 研究中「統一 token 化」路線的代表案例 |

> 目前共識：多模態 scaling law 的形狀（指數、報酬遞減速度）**因模態組合與資料配比而異**，不像文字領域已有 Chinchilla 這種公認的最優比例，仍是活躍研究領域。

---

## 十一、Scaling Law 的適用範圍：不只是預訓練

Kaplan、Chinchilla 這類最初、最經典的 Scaling Law 專指**預訓練（pretraining）loss** 與 N/D/C 的冪律關係，但這個概念早已延伸到訓練與推論的各個階段。廣義來說，只要「投入的資源」與「某種效能指標」之間呈現可預測的冪律曲線，就可以稱為 scaling law。

| 階段 | 對應章節 | Scaling 的對象 |
|---|---|---|
| 預訓練 Scaling | 第三、四節 | N（參數）、D（資料）、C（運算）對 pretraining loss 的關係 |
| 推論期 Scaling | 第七節 | 訓練完成後，回答問題當下投入的運算量（CoT、多次採樣、樹狀搜尋）|
| Post-training / RL Scaling | 第十節 | RLHF、RLAIF 等對齊階段的運算投入，效果常較早飽和，且依賴 verifier 品質 |
| Fine-tuning / SFT Scaling | — | 微調用的 token 數與下游任務表現的關係，通常比預訓練更快飽和 |
| Downstream task scaling | 第五節 | Loss 平滑下降不保證特定任務（數學、coding）同步線性提升，是 Emergent Abilities 爭議的根源 |
| Long-context scaling | 第十節 | context 長度對訓練/推論運算的影響，通常呈二次方或近似線性 |
| 多模態 scaling | 第十節 | 文字、圖像、影片混合訓練時的最佳配比，冪律指數可能與純文字模型不同 |

![圖：Scaling Law 七個適用範圍的對象與特性](figures/scaling-laws-stages.svg)

**目前業界最活躍的其實是推論期 scaling**（第七節）：預訓練那條曲線的邊際效益開始遞減（第八節 Data Wall），加上高品質公開文字資料見頂，把資源投入「訓練完之後讓模型多想一下」反而更划算。

---

## 參考公式速查

```
Kaplan (2020):     L(N, D) 近似獨立冪律，資料配比偏低
Chinchilla (2022): N_opt ∝ C^0.5, D_opt ∝ C^0.5, D ≈ 20N
推論期 scaling:     Accuracy ∝ f(推論運算)，同樣呈現報酬遞減的冪律曲線
```
