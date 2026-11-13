# 長上下文分析：為何模型容易遺失中間資訊？

## 結論摘要

長上下文模型常出現 **Lost in the Middle**（中段遺失）現象：在其他條件相同時，關鍵資訊位於內容開頭或結尾，模型通常較容易正確使用；資訊位於中段時，正確率常會下降。

這不是對所有 Transformer 都成立的數學定理，也不表示模型真的把中段 token 刪除了。它是目前許多模型上可重現的**位置偏差**：模型雖能接受長上下文，卻未必能在所有位置同等可靠地檢索與運用資訊。

近年的後續研究顯示，這個偏差並非固定不變：較新的模型在簡單檢索任務上對 U 型比較穩健，但位置偏差沒有完全消失，仍會受輸入長度與任務類型影響（見〈後續研究與近年觀察〉）。

## 實驗證據

Liu et al.（2024）以多文件問答與 key-value retrieval 進行控制實驗：保留問題與正確答案，只變更包含正確資訊的段落位置。

![控制實驗設計示意：同一題、同一組 k 份文件，只改變含答案的那份文件排第幾位；答案在開頭或結尾時正確率較高，在中間時較低](figures/lost-in-the-middle-experiment.svg)

結果顯示，多個模型的表現常呈 **U 型曲線**：

![關鍵資訊的位置與模型正確率的示意曲線：開頭與結尾較高，中段較低，呈 U 型；此為趨勢示意圖，非實測數據](figures/lost-in-the-middle-u-curve.svg)

- **開頭較強（primacy bias）**：模型傾向把前段辨識為任務設定、規則或高層背景。
- **結尾較強（recency bias）**：結尾最接近生成答案時的查詢，較容易成為當前推理焦點。
- **中段較弱**：它同時缺乏開頭與結尾的相對優勢，且必須與大量資訊競爭被重新定位的機會。

參考：<https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long>

## 後續研究與近年觀察

> 本節依搜尋結果中的論文摘要整理，**未逐篇閱讀原文**；數字與結論請以原文為準。

- **原論文的範圍**：Liu et al. 以多文件問答與 key-value retrieval 為任務，並指出輸入變長時表現會明顯下降，即使是明確設計給長上下文的模型也是如此。
- **偏差會隨輸入長度變化**：2025 年 8 月的一篇研究（arXiv:2508.07479）報告，中段遺失在輸入約占模型 context window 一半以內時最明顯；超過後，開頭優勢減弱、結尾優勢大致穩定，中段的凹陷變得不明顯，剩下的是「越靠近結尾越好」的距離偏差。該研究也主張，推理上的偏差源自檢索失敗。
- **較新的模型較穩健，但偏差未消失**：LongPiBench（ACL Findings 2025）測試了 3 個商用與 6 個開源模型，發現多數模型對「中段遺失」比較穩健，但在「多個相關資訊片段彼此間距」上仍有明顯偏差。
- **偏差可以被校正**：Found in the Middle（arXiv:2406.16008）把 U 型的位置注意力偏差與內容相關度分開建模，讓模型不論相關內容在哪個位置都能注意到；論文報告相較基線最多提升 15 個百分點。

整理後的實務意涵（這是我的歸納，不是原論文的結論）：

1. 不能假設「中段一定最差」，要在自己的任務與輸入長度下實測。
2. 輸入越長、需要整合的資訊片段越多，越要留意位置與片段間距，不只是單一事實的位置。
3. 針眼測試通過，不代表多資訊整合沒問題。

## 是否有理論證明？

### 沒有通用的「中段必然遺忘」定理

標準自注意力對某位置 `i` 的權重可寫成：

$$
\alpha_i = \mathrm{softmax}\left(
  \frac{q^\top k_i}{\sqrt{d}} + b(\text{position})
\right)
$$

其中 `q` 是目前查詢、`k_i` 是位置 `i` 的 key，`b` 表示位置相關的影響。只要中段資訊的匹配分數足夠高，模型可以直接注意到它；原始 Transformer 的全注意力機制本身不規定中段權重一定較低。

因此，對任意模型參數都宣稱「中段一定最差」是錯的。可以建造一個模型，專門對中間位置給高注意力。

### 為何現實模型仍常出現它？

這個現象是下列因素共同產生，而非單一公式必然導出：

1. **訓練分布與文件慣例**：指令與標題常在開頭；最新問題、結論或需立即回應的訊息常在結尾。模型會學到這些統計規律。
2. **位置編碼與長度外推**：模型必須藉位置編碼區分 token 的順序。當推理長度接近或超過訓練常見範圍時，位置表徵可能較不穩定；不同位置編碼與延長上下文方式的偏差也不同。
3. **注意力容量與訊號競爭**：每層、每個 head 的表示能力有限。即使可注意全部 token，模型仍需從大量相似段落中分配有限的注意力與中間表示。
4. **因果式生成的近期偏好**：生成答案時，最後讀到的資訊離目前的生成位置最近，常有更直接的推理路徑。
5. **多層傳遞誤差**：關鍵資訊若未能在早期層被正確辨識與保留，後續層不一定能穩定地恢復它。

這些是合理的機制說明；它們不構成對所有模型與所有任務的完整證明。

## Context Window 不等於有效上下文

模型宣稱可接受 `N` tokens，表示架構與服務允許輸入到該長度；它不保證在每個位置、每種任務、每份資料上都有等量的理解與檢索能力。

應區分：

| 概念 | 意義 |
|---|---|
| Context window | 能放入多少 token 的上限 |
| 有效上下文 | 模型可穩定使用的資訊範圍與位置 |
| 針眼測試（needle test） | 將明確事實插入長文本，測試是否可取回 |
| 真實任務能力 | 除了找回事實，還要理解衝突、條件、推論與輸出格式 |

「能找到針」不等於能可靠完成多文件分析；反過來，單一模型的中段表現也會隨任務、提示格式與內容冗餘而變動。

## Prompt 與 Markdown 的緩解策略

核心策略是：**重要規則置前、權威事實結構化置中、不可遺漏項在結尾濃縮重述。**

```md
# 任務

請根據資料產出……

# 不可違反的規則

- 使用繁體中文。
- 不得補造未提供的資料。
- 遇到衝突時，以「權威資料」為準。

# 權威資料（唯一事實來源）

| 欄位 | 值 |
|---|---|
| 截止日 | 2026-08-15 |
| 預算 | 50 萬 |

# 參考資料

## 文件 A
……

## 文件 B
……

# 回答前自檢

1. 只使用「權威資料」與參考資料中的事實。
2. 截止日必須為 2026-08-15。
3. 依指定格式輸出；若資料衝突，指出衝突，不自行猜測。
```

### 撰寫原則

- **建立唯一權威區塊**：明定資料衝突時的優先來源，避免模型從長文其他位置採用過期或矛盾版本。
- **使用固定標籤**：全篇一致使用同一欄位名，例如都寫「截止日」，不要混用 `deadline`、交付時間與到期日。
- **將關鍵事實表格化**：比埋在敘述段落中更容易被定位、比對與引用。
- **結尾只重述高風險資訊**：例如限制條件、決策規則、日期、數字與輸出格式；不要把整份背景再次貼上，否則會增加噪音。
- **要求來源回指**：可要求每個結論標示依據的 `##` 區段，促使模型重新檢索，而非僅依最近文字作答。
- **長任務分兩階段**：先萃取「事實表／衝突表／決策表」，再以精簡後的結構化資料產出答案。

### 文件重排（RAG 與多文件輸入）

檢索回來的文件通常依相關度由高到低排列，這會讓最不相關的文件落在結尾這個較強的位置。常見做法是**重排**：把最相關的放在開頭與結尾，最不相關的放在中段。

![文件重排示意：上方依相關度由高到低排列，最不相關的落在結尾；下方重排後，排名 1 與 2 的文件分別在開頭與結尾，排名最後的放在中段](figures/lost-in-the-middle-reorder.svg)

- LangChain 提供的 LongContextReorder 即屬此類做法（出處為社群文件，不是論文）。
- 這是啟發式做法，**不保證有效**；效果取決於模型與任務，要用自己的評測集驗證。
- 比重排更直接的是**減少放進去的文件數**：只放真正需要的片段，降低中段的資訊量。

### 需要改模型或推論方式的方法

- **位置偏差校正**：Found in the Middle（arXiv:2406.16008）。
- **位置無關的分解式訓練**：He et al.（2023），*Never Lost in the Middle*（arXiv:2311.09198）。

這類方法需要存取模型權重或推論過程；一般透過 API 使用模型時做不到，只能靠上面的 prompt 與輸入結構策略。

## 建議的兩階段工作流

```text
原始長資料
    ↓
階段 1：萃取權威事實、限制條件、矛盾點與來源標題
    ↓
人工或程式檢查事實表
    ↓
階段 2：只以事實表與必要摘錄產生分析／報告
```

此流程不會讓模型的上下文能力變成完美，但能將「在長文中反覆尋找關鍵事實」改成「對較短且有明確結構的資料推理」，通常更可靠。

## 為何 Claude Fable 5 與 Kimi K3 的長上下文體感較好？

長上下文能力不只取決於可輸入的 token 上限。較可靠的長任務表現通常同時來自：

```text
長視窗容量
  + 長距資訊傳遞的模型設計
  + 長任務／工具使用的後訓練
  + 摘要、快取與壓縮等代理層管理
  = 實際可用的長上下文能力
```

### 公開資訊比較

| 面向 | Claude Fable 5 | Kimi K3 |
|---|---|---|
| 可輸入上下文 | 1M tokens | 1M tokens |
| 長任務定位 | 長時間代理、跨階段規劃、自我檢查 | 長時程 coding、知識工作與 agentic 任務 |
| 公開架構細節 | 有限；不能從公開資料斷言其特定注意力機制 | Kimi Delta Attention（KDA）與 Attention Residuals（AttnRes） |
| 公開後訓練資訊 | 公開產品資訊強調自主規劃、工具工作與驗證 | 公開技術報告說明含百萬 token agentic RL、持久化 rollout 與 sandbox 狀態 |
| 上下文管理 | task budget、保留推理歷史、server-side compaction | preserved thinking history、context caching、工具代理框架 |

### Kimi K3：模型層與訓練層皆有公開說明

Moonshot 公開表示 Kimi K3 使用 **Kimi Delta Attention（KDA）** 與 **Attention Residuals（AttnRes）**，用來改善資訊跨序列長度與模型深度的傳遞。其技術報告也提到百萬 token 的 agentic RL、持久化 rollout 與 sandbox 狀態。這表示訓練目標不只是塞入更長輸入，而包含長時間工具操作、狀態延續與任務完成。

Kimi K3 為 Mixture-of-Experts 模型，總參數 2.8T、每 token 約啟用 104B 參數，並支援 1,048,576 tokens 的上下文。模型規模本身不是長上下文可靠度的充分條件，但它提供了足夠的模型容量；KDA、AttnRes 和長任務訓練才是較直接相關的公開因素。

來源：

- <https://arxiv.org/abs/2607.24653>
- <https://github.com/MoonshotAI/Kimi-K3>

### Claude Fable 5：產品與代理工作流訊號較明確

Anthropic 公開說明 Claude Fable 5 具有 1M-token context window，單次請求可輸出最高 128K tokens，並將其定位於長時間、少監督的代理工作。官方也說明它可在代理框架中跨階段規劃、委派子代理與檢查自己的工作。

但 Anthropic 並未在這些公開產品文件中披露與 KDA 對等的底層注意力架構或長上下文訓練配方。因此可以觀察到 Fable 的長任務定位與產品能力，卻不應把未公開的技術細節當作已證實事實。

其實務表現也受上下文管理影響：Claude 文件列出 Fable 5 的推理歷史預設保留、可設定 task budget，且可使用 server-side compaction 將較早的對話摘要化以延續超過單一 context window 的工作。

來源：

- <https://www.anthropic.com/claude/fable>
- <https://platform.claude.com/docs/en/build-with-claude/context-windows>

### 為何代理模式會放大差異？

長文本或大型程式庫中的關鍵問題，不只是「能否讀入」，還包括模型能否在多個工具呼叫、推理回合與輸出之後，保留正確的目標與事實。較好的 agent harness 通常會：

1. 保留關鍵決策、工具結果與必要的推理狀態。
2. 在快接近上限時摘要或壓縮較早內容。
3. 將測試、檢索與工具結果作為外部可驗證記憶。
4. 讓模型依回饋修正，而不是一次性依長 prompt 作答。

因此，使用者感受到的「長上下文能力」，常是模型、提示策略、上下文管理和工具迴圈的綜合結果。

### 比較時的注意事項

不要以供應商或單一社群測試就推論絕對優劣。應盡量控制以下條件：

- 使用相同任務、相同資料、相同關鍵資訊位置與相近 token 長度。
- 使用相同 agent harness、工具、推理／思考預算與溫度。
- 明確記錄是否啟用 RAG、快取、摘要或 context compaction。
- 檢查是否觸發安全 fallback、拒答或模型降級。

例如 Kimi K3 的公開 benchmark 表格本身採用多種不同 harness，並註明部分 Claude Fable 任務觸發 fallback；這類差異會影響結果，不能把所有分數直接歸因於底層模型。

## 參考資料

1. Liu, N. F., et al. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. Transactions of the Association for Computational Linguistics. <https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long>
2. Vaswani, A., et al. (2017). *Attention Is All You Need*. <https://arxiv.org/abs/1706.03762>
3. He, J., et al. (2023). *Never Lost in the Middle: Mastering Long-Context Question Answering with Position-Agnostic Decompositional Training*. <https://arxiv.org/abs/2311.09198>
4. Moonshot AI. (2026). *Kimi K3: Open Frontier Intelligence*. <https://arxiv.org/abs/2607.24653>
5. Anthropic. (2026). *Claude Fable 5*. <https://www.anthropic.com/claude/fable>
6. Anthropic. (2026). *Context windows*. <https://platform.claude.com/docs/en/build-with-claude/context-windows>
7. Liu, N. F., et al. (2023). *Lost in the Middle: How Language Models Use Long Contexts*（預印本）。<https://arxiv.org/abs/2307.03172>
8. *Found in the Middle: Calibrating Positional Attention Bias Improves Long Context Utilization*（2024）。<https://arxiv.org/abs/2406.16008>
9. 2025 年 8 月關於中段遺失與輸入長度關係的研究，arXiv:2508.07479。<https://arxiv.org/abs/2508.07479>
10. *LongPiBench*（ACL Findings 2025），關於相關資訊片段間距的位置偏差評測；細節請至 ACL Anthology 查閱。

第 7 至 10 項是透過搜尋結果的摘要找到，未逐篇閱讀原文；引用前請先核對原文。
