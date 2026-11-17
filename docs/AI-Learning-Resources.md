# AI 學習資源

> 資料日期：2026-11-16（第 3.4 節「Hugging Face」、第 5.2 節「模型廠商」與第 7 節「大學課程」為 2026-11-17）  
> 範圍：整理學習 AI 模型、LLM 與 Agent 的課程、書籍、論文、大學公開課、官方文件與持續追蹤的來源，並對應到本筆記庫的文件。  
> 讀法：每個資源都標示驗證狀態——**✅** 表示我查到官方頁面、出版方頁面，或本庫文件已引用；**🔎** 表示只有二手來源確認它存在，連結與內容請自行核對。課程、書籍與網站會更新，請以官方頁面為準。

## 先看結論

- **非技術背景**：先看吳恩達的 *AI for Everyone*（不需寫程式），了解 AI 能做什麼、怎麼導入與對社會的影響。
- **想建立直覺**：先看 3Blue1Brown 的[神經網路系列](https://www.3blue1brown.com/neural-networks)，再看 Karpathy 的 [*Neural Networks: Zero to Hero*](https://karpathy.ai/zero-to-hero.html)；想先聽概念，可看他的 [*Intro to Large Language Models*](https://www.youtube.com/watch?v=zjkBMFhNj_g) 演講；更多影片見他的 [YouTube 頻道](https://www.youtube.com/@AndrejKarpathy)。
- **想自己動手**：Karpathy 的[系列](https://karpathy.ai/zero-to-hero.html)（影片在他的 [YouTube 頻道](https://www.youtube.com/@AndrejKarpathy)） → Raschka 的 *Build a Large Language Model (From Scratch)* → Stanford CS336。
- **想看各家模型的官方文件與範例**：Claude、OpenAI、Gemini、DeepSeek 的入口都在第 5.2 節。
- **想用 LLM 做應用或 Agent**：Chip Huyen 的 *AI Engineering*、Hugging Face 的 [Agents Course](https://huggingface.co/learn/agents-course)、Anthropic 的 *Building effective agents*，再讀各家官方文件。
- **偏好中文**：台大李宏毅老師的課程是最常被推薦的起點，影片主頁見第 6 節的 [YouTube 頻道](https://www.youtube.com/@HungyiLeeNTU/videos)。
- **想上大學公開課**：史丹佛、MIT、清華、北大、浙大的課程，每門都附連結，見第 7 節。
- **想讀研究**：從第 4 節的論文清單開始，每個主題都對應到本筆記庫的一份文件。
- 這份清單是「入口」，不是完整書目；我沒有逐一上完或讀完每個資源，品質判斷不在範圍內。

---

## 1. 學習路徑

![圖：AI 學習路徑——基礎直覺、LLM 原理與實作、訓練與研究、應用與 Agent 四個階段](figures/ai-learning-resources-path.svg)

| 階段 | 目標 | 對應本庫文件 |
|---|---|---|
| 1 基礎直覺 | 神經網路、反向傳播、訓練在做什麼 | — |
| 2 LLM 原理與實作 | tokenizer、Transformer、從零訓練小型 GPT | [Transformer-Attention](Transformer-Attention.md) |
| 3 訓練、評測與研究 | scaling、後訓練、注意力、長上下文 | [Scaling-Laws](Scaling-Laws.md)、[Post-Training](Post-Training.md)、[Long-Context-Note](Long-Context-Note.md) |
| 4 應用與 Agent | RAG、tool use、Agent 工程、開發工具 | [Agentic-Engineering](Agentic-Engineering.md)、[Claude-Agent](Claude-Agent.md)、[CodeX-Agent](CodeX-Agent.md) |

> 「有程式基礎可從階段 2 開始、只想用 Agent 可直接到階段 4」是我依目的做的歸納，不是任何課程或官方的建議。

---

## 2. 基礎：機器學習與深度學習

![圖：依背景選起點——要不要寫程式、偏好中文、先看原理還是先寫程式](figures/ai-learning-resources-start.svg)

> 圖中的分流是我依各資源的定位做的歸納，不是學校或作者的建議。

| 資源 | 形式 | 適合 | 狀態 |
|---|---|---|---|
| [吳恩達：*AI for Everyone*](https://www.deeplearning.ai/courses/ai-for-everyone)（[Coursera 頁面](https://www.coursera.org/learn/ai-for-everyone)） | DeepLearning.AI 在 Coursera 開的入門課；DeepLearning.AI 頁面標示約 6 小時 54 分、35 支影片，共 4 週，第 3 週談在公司裡建 AI、第 4 週談 AI 與社會 | 非技術背景的人、想了解 AI 導入與策略的管理者；不需寫程式 | ✅ |
| [3Blue1Brown：神經網路系列](https://www.3blue1brown.com/neural-networks) | 官方主題頁，整理成一系列課程：前面章節講神經網路的基礎與學習的數學，之後接 GPT 與 Transformer。[第 5 章 *Transformers, the tech behind LLMs*](https://www.3blue1brown.com/lessons/gpt) 在官方頁面標為 2024-04-01；第 6 章（attention）與第 7 章（LLM 如何儲存事實）的標題取自第三方彙整，請以官方主題頁的章節列表為準 | 零基礎，重視視覺直覺（動畫） | ✅（官方主題頁與第 5 章頁）／🔎（第 6、7 章） |
| 3Blue1Brown：*Large Language Models explained briefly* | 較輕量的 LLM 簡介，搜尋結果標為 2024-11-20；我沒有取得可確認的官方網址，請到官網的課程列表找 | 想先用短時間了解 LLM 的人 | 🔎 |
| [3Blue1Brown 網站](https://www.3blue1brown.com) 與 [YouTube 頻道](https://www.youtube.com/@3blue1brown) | 頻道由 Grant Sanderson 經營，官網也放文字與互動版的課程；頻道網址取自第三方文章列出的帳號，我沒有開啟頻道頁面，訂閱數各來源不同，不列數字 | — | ✅（官網）／🔎（頻道） |
| 李宏毅：機器學習（2021） | 台大課程影片 | 想用中文系統學基礎 | 🔎 |
| fast.ai：*Practical Deep Learning for Coders* | 免費課程 | 先寫程式、再回頭理解原理 | 🔎 |
| [*Dive into Deep Learning*（d2l.ai）](https://d2l.ai) | 免費互動式教科書 | 想要程式碼與理論並行的教材 | 🔎 |

*AI for Everyone* 是搜尋結果直接回傳 DeepLearning.AI 與 Coursera 的課程頁，但我沒有開啟頁面，時數與影片數取自搜尋結果摘要；價格與是否有免費註冊方式會變，請以官方頁面為準。3Blue1Brown 的官方頁面是搜尋結果直接回傳的網址，但我沒有開啟頁面。這一節其餘項目都是從課程彙整文章確認存在，我沒有開啟各官方頁面；課程版本、時數請自行核對。

---

## 3. LLM 原理與動手實作

![圖：LLM 由淺到深的學習路線，以及可以看每一層輸出的互動網站](figures/ai-learning-resources-llm-route.svg)

### 3.1 課程與影片

| 資源 | 內容 | 狀態 |
|---|---|---|
| [Karpathy：*Neural Networks: Zero to Hero*](https://karpathy.ai/zero-to-hero.html)（[GitHub](https://github.com/karpathy/nn-zero-to-hero)） | 從反向傳播一路寫到 GPT，含 [*Let's build GPT*](https://www.youtube.com/watch?v=kCc8FmEb1nY)（下一列） | ✅ |
| [Karpathy：*Let's build GPT: from scratch, in code, spelled out*](https://www.youtube.com/watch?v=kCc8FmEb1nY) | Zero to Hero 系列裡寫出 GPT 的那一講，約 1 小時 56 分，2023-01-17 發佈；從空檔案開始，照 *Attention Is All You Need* 與 GPT-2／GPT-3 的做法，在 Tiny Shakespeare（約 1 MB 文字）上訓練字元層級的小型 Transformer。影片說明附有 Colab 筆記本（我沒有查到可確認的網址，請到影片說明找）、[ng-video-lecture](https://github.com/karpathy/ng-video-lecture)（這一講的程式碼）與 [nanoGPT](https://github.com/karpathy/nanoGPT)（完整版）兩個 GitHub 專案；建議先看前面的 makemore 系列再看這一講 | 🔎（影片網址取自第三方網站；GitHub 專案取自搜尋結果對影片說明的轉述） |
| [Karpathy 個人網站](https://karpathy.ai) | 他的教學影片與專案入口；站上列有他的 YouTube 頻道，內容分成技術向與一般大眾向兩條線 | ✅ |
| [Karpathy YouTube 頻道](https://www.youtube.com/@AndrejKarpathy) | 影片主頁；網址取自第三方連結與他個人網站所列的頻道，我沒有開啟頻道頁面，訂閱數各來源差異大，不列數字 | 🔎 |
| [Karpathy：*[1hr Talk] Intro to Large Language Models*](https://www.youtube.com/watch?v=zjkBMFhNj_g) | 約 1 小時、2023 年 11 月的一般大眾演講；以 Llama 2 70B 為例，講預訓練與微調，以及 jailbreak、prompt injection 等安全風險。適合想先建立概念、不急著寫程式的人 | 🔎（影片網址取自轉錄網站） |
| [Karpathy：*Deep Dive into LLMs like ChatGPT*](https://www.youtube.com/watch?v=7xTGNNLPyMI) | 約 3 小時 31 分、2025 年初的一般大眾深度講解；涵蓋推論與後訓練（SFT、RLHF）。上傳日期各來源說法不一（2 月 5 日或 27 日），以影片頁面為準 | 🔎（影片網址取自搜尋結果） |
| [Stanford CS336：*Language Modeling from Scratch*](https://stanford-cs336.github.io/spring2025/) | Percy Liang 與 Tatsunori Hashimoto 開設；錄影免費上 YouTube；作業需要 GPU | 🔎 |
| Stanford CS224N：*NLP with Deep Learning* | NLP 與深度學習，偏進階 | 🔎 |

> Karpathy 系列的影片編號各來源說法不一（例如 tokenizer 是第幾講），請直接看官方頁面或播放清單，不要依編號找。

### 3.2 書與文章

| 資源 | 內容 | 狀態 |
|---|---|---|
| [Sebastian Raschka：*Build a Large Language Model (From Scratch)*](https://www.manning.com/books/build-a-large-language-model-from-scratch) | Manning，2024 年 9 月；從設計、預訓練到微調，一步步自己做一個 LLM | ✅ |
| [Jay Alammar、Maarten Grootendorst：*Hands-On Large Language Models*](https://www.oreilly.com/library/view/hands-on-large-language/9781098150952/) | O'Reilly，2024 年 9 月；以視覺化方式講如何運用預訓練模型做分類、RAG、多模態 | ✅ |
| Chip Huyen：*AI Engineering*（O'Reilly） | 在既有基礎模型上做應用：評測、prompt、RAG 與 agents、微調、資料集工程、推論最佳化 | 🔎（出版年份各來源不一，請以 O'Reilly 頁面為準） |
| [Jay Alammar：*The Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/) | 2018 年的圖解文章，一步步拆解 self-attention 與 encoder-decoder | 🔎 |

### 3.3 互動視覺化網站：看每一層的輸出

想「親眼看到」資料怎麼一層一層流過 Transformer，可以用下面這些網站與工具。它們各有側重，沒有一個能涵蓋全部：

| 資源 | 能看到什麼 | 連結 | 狀態 |
|---|---|---|---|
| LLM Visualization（Brendan Bycroft） | 3D、可互動的 GPT 逐步走讀：可以旋轉、縮放、飛進結構裡，滑鼠移到元件上會顯示它屬於哪個結構、列數與欄數。內建小型的 nano-GPT（約 8.5 萬個參數，取自 Karpathy 的 minGPT），也能切換到 GPT-2 等較大的模型；因為依比例繪製，可以直接比較大小。程式碼開源 | [bbycroft.net/llm](https://bbycroft.net/llm)、[GitHub](https://github.com/bbycroft/llm-viz) | ✅（GitHub）／🔎（網站網址取自搜尋摘要） |
| Transformer Explainer（Georgia Tech 與 IBM Research） | 在瀏覽器裡**直接跑一個 GPT-2**（不用安裝）：自注意力的各個 head 與注意力權重矩陣、前饋網路、layer normalization、殘差連接，到最後的 logits。只涵蓋一個小型 GPT-2，結果不能類推到大型 LLM。論文發表於 AAAI 2025，作者自述有 12.5 萬人使用，程式碼為 MIT 授權 | [線上展示](https://poloclub.github.io/transformer-explainer/)、[GitHub](https://github.com/poloclub/transformer-explainer)、[論文（AAAI 2025）](https://ojs.aaai.org/index.php/AAAI/article/view/35347)、[arXiv 2408.04619](https://arxiv.org/abs/2408.04619) | ✅ |
| BertViz | 在 Jupyter 或 Colab 裡視覺化 Transformer 的注意力，有「model view」可以一次看**所有層與所有 head**；不含 logit lens | [GitHub](https://github.com/jessevig/bertviz) | ✅ |
| LM Transparency Tool（Meta） | 瀏覽器介面，可以對選定的表示做 **logit lens**，並看選定的注意力 head 推升或壓低了哪些 token，較偏研究與分析；有 Hugging Face Spaces 的展示 | [GitHub](https://github.com/facebookresearch/llm-transparency-tool)、[ACL 2024 demo 論文](https://aclanthology.org/2024.acl-demos.6.pdf) | ✅（論文）／🔎（GitHub 網址、展示頁） |

> 如果你記得的是「3D 方塊一層一層飛過去、可以看每一層的矩陣大小」，那最像 **LLM Visualization**；如果是「輸入一段文字、看 GPT-2 每個 head 的注意力與最後的機率」，那最像 **Transformer Explainer**。我是依描述推測，不確定是哪一個。
>
> 這些網站我**沒有開啟**：說明取自搜尋結果的摘要，LLM Visualization 的網址是搜尋結果直接指名的網站，LM Transparency Tool 的 GitHub 網址與展示頁取自轉述。對應的原理可以回頭看本庫的 [Transformer-Attention](Transformer-Attention.md)。

### 3.4 Hugging Face 學習資源

Hugging Face 把課程集中在 [Hugging Face Learn](https://huggingface.co/learn)；多數是免費、開源的課程，學習時通常需要一個免費的 Hugging Face 帳號。

![圖：依目標選 Hugging Face 的課程](figures/ai-learning-resources-hf-courses.svg)

| 資源 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| Hugging Face Learn（入口） | 課程目錄；搜尋結果顯示它列有 LLM、Agents、Diffusion、Audio、Deep RL、Computer Vision、smol course、Robotics（LeRobot）、ML for 3D 等課程與 Open-Source AI Cookbook | [huggingface.co/learn](https://huggingface.co/learn) | ✅ |
| LLM Course | 用 Hugging Face 的函式庫處理 LLM，涵蓋用 Transformers 訓練、微調與部署；一個來源說有 12 章 | 在 Learn 入口內（我沒有看到官方頁面的網址） | 🔎 |
| Agents Course | 免費；涵蓋 smolagents、LlamaIndex、LangGraph；需要免費的 Hugging Face 帳號；搜尋結果說結業證書免費 | [huggingface.co/learn/agents-course](https://huggingface.co/learn/agents-course) | ✅ |
| smol course | 對齊小型語言模型的免費開放課程，以 SmolLM3 與 SmolVLM2 為例，技巧也可用在其他小型 LLM／VLM；社群貼文說 v2 有排行榜與認證，細節請以官方為準 | [huggingface.co/learn/smol-course](https://huggingface.co/learn/smol-course)、[GitHub](https://github.com/huggingface/smol-course) | 🔎 |
| MCP Course | 教 Model Context Protocol 的理論、設計與實作，來源說有測驗與影片；**各來源對它有沒有列在 Learn 目錄說法不一** | 在 Learn 入口內（我沒有看到網址） | 🔎 |
| Diffusion／Audio／Deep RL／Computer Vision 課程 | 分別是擴散模型與 Diffusers、用 Transformers 處理音訊（語音辨識、音訊分類、語音合成）、深度強化學習、電腦視覺；後兩者我只看到名稱，沒有看到內容描述 | 在 Learn 入口內 | 🔎 |
| Open-Source AI Cookbook | 實作專案與範例集，適合已經有具體專案想做的時候 | 在 Learn 入口內（我沒有看到網址） | 🔎 |

> 搜尋結果裡有一個頁面把 Agents Course 描述成電腦視覺相關，應該是第三方的複製錯誤，我沒有採用。這一節我**沒有開啟任何頁面**；課程是否持續更新、章節數與是否仍開放，請以 Learn 入口為準。我也沒有查到 Transformers 文件、Hugging Face 部落格與 Papers 頁面的可確認網址，所以沒有列。

---

## 4. 論文閱讀清單（對應本筆記庫）

![圖：七個主題的代表論文，以及對應的本筆記庫文件](figures/ai-learning-resources-papers.svg)

| 主題 | 論文 | 本庫對應 | 狀態 |
|---|---|---|---|
| Transformer 基礎 | [Attention Is All You Need](https://arxiv.org/abs/1706.03762)（2017） | [Transformer-Attention](Transformer-Attention.md) | ✅ |
| Scaling | [Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361)（Kaplan et al., 2020） | [Scaling-Laws](Scaling-Laws.md) | ✅ |
| Scaling | [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)（Hoffmann et al., 2022；Chinchilla） | [Scaling-Laws](Scaling-Laws.md) | ✅ |
| 資料見頂 | [Will we run out of data?](https://epoch.ai/blog/will-we-run-out-of-data)（Epoch AI, 2024；arXiv 2211.04325） | [Scaling-Laws](Scaling-Laws.md) §八 | ✅ |
| 後訓練 | *Training language models to follow instructions with human feedback*（Ouyang et al., 2022；InstructGPT） | [Post-Training](Post-Training.md) | 🔎 |
| 後訓練 | *Direct Preference Optimization*（Rafailov et al., 2023；DPO） | [Post-Training](Post-Training.md) | 🔎 |
| 後訓練 | *LoRA: Low-Rank Adaptation of Large Language Models*（Hu et al., 2021） | [Post-Training](Post-Training.md) | 🔎 |
| 長上下文 | *Lost in the Middle*（Liu et al., 2023；[arXiv 2307.03172](https://arxiv.org/abs/2307.03172)） | [Long-Context-Note](Long-Context-Note.md) | ✅ |
| 注意力與 serving | [FlashAttention](https://arxiv.org/abs/2205.14135)、[GQA](https://arxiv.org/abs/2305.13245)、[DeepSeek-V2（MLA）](https://arxiv.org/abs/2405.04434) | [Transformer-Attention](Transformer-Attention.md) | ✅ |
| 推理與 Agent | *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*（Wei et al., 2022） | [Scaling-Laws](Scaling-Laws.md) §七 | 🔎 |
| 推理與 Agent | *ReAct: Synergizing Reasoning and Acting in Language Models*（Yao et al., 2022） | [Agentic-Engineering](Agentic-Engineering.md) | 🔎 |
| 推理與 Agent | [DeepSeek-R1](https://arxiv.org/abs/2501.12948)（2025） | [Scaling-Laws](Scaling-Laws.md) §七 | ✅ |
| RAG | [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)（Lewis et al., 2020） | [Post-Training](Post-Training.md)、[Enterprise-AI-Integration](Enterprise-AI-Integration.md) | ✅ |

標 🔎 的論文我只確認標題、作者與年份，**沒有核對 arXiv 編號**（沙箱連不到 arxiv.org），所以不放連結；請用標題在 arXiv 搜尋。標 ✅ 的連結，一部分是我用搜尋核對過標題與編號，一部分是本庫其他文件已經引用的來源。

---

## 5. 官方文件：Agent 工具與模型廠商

### 5.1 Agent 與開發工具

![圖：官方文件對應本筆記庫的哪份文件](figures/ai-learning-resources-docs-map.svg)

| 資源 | 內容 | 本庫對應 | 狀態 |
|---|---|---|---|
| [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)（2024-12-19） | 區分 workflow 與 agent，建議先用簡單模式、不要一開始就上重型框架 | [Agentic-Engineering](Agentic-Engineering.md) | ✅ |
| [Anthropic：Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | context 工程與長時程 agent 的做法 | [Claude-Context](Claude-Context.md) | ✅（本庫已引用） |
| [Claude Code 文件](https://code.claude.com/docs/en/features-overview.md) | 功能總覽、skills、plugins、MCP、context window 等 | [Claude-Code-CLI](Claude-Code-CLI.md) | ✅（本庫已引用） |
| [Model Context Protocol 文件](https://modelcontextprotocol.io/docs/getting-started/intro) | MCP 的官方介紹與規格；文件有依協議版本分開的副本，引用時要註明版本 | [Claude-Code-CLI](Claude-Code-CLI.md) | ✅ |
| [OpenAI API：Agents 指南](https://developers.openai.com/api/docs/guides/agents) | OpenAI 的 agent 開發指南 | [OpenAI-Python-Agent](OpenAI-Python-Agent.md) | ✅（本庫已引用） |
| [Codex 文件](https://developers.openai.com/codex/cli) | Codex CLI、sandbox、subagents 等 | [CodeX-CLI](CodeX-CLI.md)、[CodeX-Agent](CodeX-Agent.md) | ✅（本庫已引用） |

### 5.2 模型廠商：Claude、OpenAI、Gemini、DeepSeek

![圖：Claude、OpenAI、Gemini、DeepSeek 在官方文件、範例、課程、論文與技術文章查到的連結](figures/ai-learning-resources-vendor-matrix.svg)

| 廠商 | 資源 | 內容 | 本庫對應 | 狀態 |
|---|---|---|---|---|
| Claude | [Claude 開發者文件](https://platform.claude.com/docs/en/)（[API 概覽](https://platform.claude.com/docs/en/api/overview)、[繁體中文版](https://platform.claude.com/docs/zh-TW/api/overview)） | API、Messages、認證與限制等；搜尋結果也有 `docs.claude.com`，應是較早的網址 | [Claude-Model](Claude-Model.md)、[Claude-Code-CLI](Claude-Code-CLI.md) | ✅ |
| Claude | [Anthropic Academy](https://anthropic.skilljar.com/)（[anthropic.com/learn](https://anthropic.com/learn)） | 免費、自學的訓練平台，涵蓋不寫程式、開發者與雲端平台等方向；課程數各來源說法不一（13 到 21 門不等），請以官方頁面為準 | — | ✅ |
| Claude | [anthropics/courses](https://github.com/anthropics/courses) | Jupyter 筆記本教程：API 基礎、prompt engineering、tool use。有來源指出最後更新在 2024 年 6 月，範例偏向較舊的模型，使用前先看目前的模型名稱 | — | ✅（專案）／🔎（時效） |
| Claude | [Claude Cookbook](https://github.com/anthropics/claude-cookbooks)（舊稱 anthropic-cookbook） | 官方的 Jupyter 範例集，依主題整理；我沒有看到這個網址直接出現在搜尋結果，是依「主要倉庫」的說法與舊名推得，請自行核對 | — | 🔎 |
| OpenAI | [OpenAI 開發者文件](https://developers.openai.com) | APIs、模型與 ChatGPT apps 的入口；本庫已引用其[模型頁](https://developers.openai.com/api/docs/models)與[定價頁](https://developers.openai.com/api/docs/pricing) | [OpenAI-Model](OpenAI-Model.md)、[CodeX-CLI](CodeX-CLI.md) | ✅ |
| OpenAI | [OpenAI Cookbook](https://cookbook.openai.com)（[developers.openai.com/cookbook](https://developers.openai.com/cookbook)） | 常見 API 任務的範例程式與指南 | — | ✅ |
| Gemini | [Gemini API 文件](https://ai.google.dev/gemini-api/docs) | 官方 API 文件；網址取自 Cookbook README 指向 `ai.google.dev` 的說法，沒有在搜尋結果直接看到 `/gemini-api/docs` | [Transformer-Attention](Transformer-Attention.md)（Gemini 1.0 的 MQA） | 🔎 |
| Gemini | [Gemini API Cookbook（ai.google.dev）](https://ai.google.dev/gemini-api/cookbook)、[google-gemini/cookbook（GitHub）](https://github.com/google-gemini/cookbook) | 官方範例集；快速入門涵蓋 Batch API、Live API、grounding 等。GitHub 上有不少 fork，請用 `google-gemini/cookbook` 這個官方倉庫 | — | ✅ |
| Gemini | [Google AI Studio](https://aistudio.google.com) | 用 Google 帳號登入、建立 API key 的入口；網址取自搜尋摘要的文字，沒有直接出現在結果 | — | 🔎 |
| DeepSeek | [DeepSeek API 文件](https://api-docs.deepseek.com) | 官方 API 文件；第三方指南列出此網址，並說 OpenAI SDK 可改用自訂 base URL；我沒有確認，請以官方頁面為準 | — | 🔎 |
| DeepSeek | [github.com/deepseek-ai](https://github.com/deepseek-ai) | 開源模型、工具與範例專案的 GitHub 組織；網址取自第三方指南 | — | 🔎 |
| DeepSeek | 技術報告：[DeepSeek-V2（MLA）](https://arxiv.org/abs/2405.04434)、[DeepSeek-V3](https://arxiv.org/abs/2412.19437)、[DeepSeek-R1](https://arxiv.org/abs/2501.12948) | V3 為 MoE，總參數 671B、每 token 啟用約 37B；R1 以強化學習強化推理 | [Transformer-Attention](Transformer-Attention.md)（MLA）、[Scaling-Laws](Scaling-Laws.md)（MoE、R1） | ✅ |

> 這次**沒有查到**：OpenAI Academy 的可確認連結、Google DeepMind 的 Gemini 模型頁、DeepSeek 在 Hugging Face 的頁面、Gemini 與 OpenAI 的模型技術報告。這不代表它們不存在。模型名稱與價格變動很快，請以各家官方頁面為準；本庫的 [Claude-Model](Claude-Model.md) 與 [OpenAI-Model](OpenAI-Model.md) 記錄了兩家的模型與價格，並標有資料日期。

---

## 6. 中文與繁體中文資源

| 資源 | 說明 | 狀態 |
|---|---|---|
| [李宏毅 YouTube 頻道](https://www.youtube.com/@HungyiLeeNTU/videos) | 課程影片的主頁：機器學習、深度學習、人類語言處理、生成式 AI 等；有教學講義與錄影可搭配觀看。網址來自 2024 年的 AI YouTuber 彙整文章，我沒有開啟頻道頁面，訂閱數與影片數各來源差異大，不列數字 | 🔎 |
| [李宏毅個人網頁（台大）](https://speech.ee.ntu.edu.tw/~hylee/index.php) | 各學期課程網頁、投影片與作業的入口；課程資料大多放在 `speech.ee.ntu.edu.tw/~hylee/` 之下 | ✅ |
| 李宏毅：生成式人工智慧導論（2024 春季） | 台大課程；內容大致分為生成式 AI 能做什麼、模型內部如何運作、如何訓練、如何微調。課程網頁為 [genai/2024-spring.php](https://speech.ee.ntu.edu.tw/~hylee/genai/2024-spring.php)，也可直接看[第一堂簡報](https://speech.ee.ntu.edu.tw/~hylee/genai/2024-spring-course-data/0223/0223_course.pdf)；影片在上面的 YouTube 頻道（我沒有找到可確認的單一播放清單網址） | ✅（課程簡報）／🔎（課程網頁、影片） |
| 李宏毅：生成式人工智慧與機器學習導論（2025 秋季） | 較新的一學期；搜尋結果列出課程網頁 [GenAI-ML/2025-fall.php](https://speech.ee.ntu.edu.tw/~hylee/GenAI-ML/2025-fall.php)，並有一份介紹語言模型運作原理的講義；我沒有開啟課程網頁，課程內容與是否有公開錄影請自行確認 | 🔎 |
| 李宏毅：機器學習（2021／2022／2023） | 搜尋結果建議與生成式 AI 導論搭配觀看；2022 與 2023 的課程資料也在上面的個人網頁底下（如 `ml/ml2022-course-data/`、`ml/2023-spring.php`） | 🔎 |
| 動手學深度學習（*Dive into Deep Learning* 的中文版） | d2l 的中文版本 | 🔎 |
| 本筆記庫 | 繁體中文、含圖示，主題見網站首頁或 GitHub 的 README 索引 | ✅ |

> 中國大陸高校（清華、北大、浙大）的 MOOC 見第 7 節。

---

## 7. 大學課程：史丹佛、MIT、清華、北大、浙大

非校園系列（Karpathy、李宏毅、吳恩達等）以外，各大學公開的課程也是很好的入口。這一節整理史丹佛、MIT、清華、北大、浙大公開的 AI 相關課程，**每一門都附連結**，並標示驗證狀態；偏重機器學習、深度學習、NLP 與 LLM，並列出補數學基礎的課。

- **英文、系統化**：史丹佛的 CS229（機器學習）、CS231n（視覺）、CS224N（NLP）、CS336（從零寫語言模型），以及 MIT 的 6.S191（深度學習入門）。
- **補數學**：MIT OpenCourseWare 的 18.06SC（線性代數）與 18.065（機器學習的矩陣方法）。
- **中文、有平台**：浙大《機器學習》《人工智能：模型與算法》在中國大學 MOOC；清華在學堂在線有三門 AI 相關課程；北大有《人工智能原理》。
- **這次沒查到的**：北大、清華、浙大專門講「大模型」的公開課；北大的深度學習課程。這不代表它們沒有，只是我在可用的搜尋範圍內沒找到可確認的連結。

![圖：史丹佛、MIT、清華、北大、浙大在機器學習、NLP 與 LLM、數學基礎、AI 概論四個主題查到的課程](figures/ai-learning-resources-univ-matrix.svg)

> 我**沒有開啟任何課程頁面**（沙箱連不到這些網站）；課程簡介取自搜尋結果的摘要，開課學期、是否仍開放、是否有錄影，都以各頁面現況為準。✅ 表示連結是搜尋結果直接回傳的官方或平台網址；🔎 表示網址取自第三方文章或是該校慣用的位置，沒有在搜尋結果裡直接看到。

### 7.1 史丹佛大學（Stanford）

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| CS224N：*Natural Language Processing with Deep Learning* | NLP 與深度學習。目前這一期的投影片在 `slides_w26` 之下；課程網站列出的歷年錄影存檔包含 Spring 2024、Winter 2023、Winter 2021、Winter 2019、Winter 2017。官方 YouTube 播放清單我沒有確認 | [課程網站](https://web.stanford.edu/class/cs224n/)、[2026 第 1 講投影片](https://web.stanford.edu/class/cs224n/slides_w26/cs224n-2026-lecture01-intro.pdf) | ✅ |
| CS336：*Language Modeling from Scratch* | Percy Liang 與 Tatsunori Hashimoto 開設；從零做語言模型。搜尋結果提到錄影公開在 YouTube，作業需要 GPU | [Spring 2025 課程網站](https://cs336.stanford.edu/spring2025)（另有[存檔站](https://stanford-cs336.github.io/spring2025/)） | ✅ |
| CS231n：*Convolutional Neural Networks for Visual Recognition* | 視覺方向的卷積神經網路與深度學習。搜尋結果顯示 Stanford Online 的 YouTube 有 Spring 2025 的講座（例如 *Lecture 7: Recurrent Neural Networks*）；另有說法是目前一期的錄影只給修課學生，各來源不一致 | [cs231n.stanford.edu](https://cs231n.stanford.edu) | 🔎 |
| CS229：*Machine Learning* | 機器學習。搜尋結果顯示 Andrew Ng 2018 年秋季的講座有公開錄影；`cs229.stanford.edu` 這個網域確實存在（有一份相關課程的 PDF 在它底下），但我沒有看到首頁 | [cs229.stanford.edu](https://cs229.stanford.edu) | 🔎 |
| CS25：*Transformers United* | Transformer 主題的系列課。搜尋結果列出 2021 年秋季的講座有錄影，並說可旁聽或看直播；是否仍開課請看網站 | [課程網站](https://web.stanford.edu/class/cs25/) | 🔎 |

### 7.2 麻省理工學院（MIT）

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| 6.S191：*Introduction to Deep Learning* | MIT 的深度學習入門，由 Alexander Amini 與 Ava Soleimany 主持；講座免費公開，每年有一個頁面，我查到的存檔涵蓋 2017–2022，**最新一年我只看到 2022**，是否有更新請看網站。實驗使用 TensorFlow（依搜尋結果） | [introtodeeplearning.com](https://introtodeeplearning.com/2022)（[2021](https://introtodeeplearning.com/2021/index.html)、[2020](https://introtodeeplearning.com/2020/)） | ✅ |
| 18.06SC：*Linear Algebra*（Gilbert Strang） | OCW 的自學版線性代數；頁面列有 35 支講座影片與 36 支輔導解題影片。搜尋結果的新聞稿提到 Strang 在 2023 年春季教完最後一次 18.06 | [OCW 18.06SC](https://www.ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011) | ✅ |
| 18.065：*Matrix Methods in Data Analysis, Signal Processing, and Machine Learning* | Strang 在 2017 年開的課，講線性代數如何支撐機器學習、深度學習與神經網路；教科書是 *Linear Algebra and Learning from Data*（2019） | [OCW 18.065 課綱](https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/pages/syllabus) | ✅ |

> MIT 的 6.034（人工智慧）與 6.036（機器學習導論）這次沒有查到可確認的 OCW 頁面，所以沒有列。

### 7.3 清華大學（Tsinghua）

清華的公開課主要在**學堂在線**（XuetangX）。以下三門都是搜尋結果回傳的學堂在線頁面：

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| 大數據機器學習 | 面向資訊學科高年級本科生或研究生；統計學習基本理論、機器學習基本方法、深度學習理論與方法。主講人袁春（清華大學深圳國際研究生院）。國家高等教育智慧教育平台顯示開課平台為學堂在線，標為開課中（2026/07/23–2027/01/12） | [學堂在線](https://www.xuetangx.com/course/THU08091001026/1076286)、[智慧教育平台頁面](https://higher.smartedu.cn/course/622ac974bee70ef79f3e4f41) | ✅ |
| 深度學習訓練營 | 胡曉林副教授主講；涵蓋 NN、RNN、CNN、LSTM 等主流演算法，設計了 6 個實戰案例 | [學堂在線](https://www.xuetangx.com/course/DP08091003375/) | ✅ |
| 大數據與機器智能 | 目標是快速掌握機器學習與深度學習的基礎，並了解 AI 產業的前沿應用 | [學堂在線](https://www.xuetangx.com/course/thu08091010085/18960834) | ✅ |
| 清華 AI 素養網站 | 清華官網提到 2025 年 2 月發布；內容由校內師生講授，涵蓋生成式 AI 概念、AI 賦能教與學、倫理與責任。這個網址是官網新聞轉述的，我沒有看到頁面本身，也不確定它是否屬於公開課 | [yuketang.tsinghua.edu.cn/ai](https://yuketang.tsinghua.edu.cn/ai) | 🔎 |

> 搜尋結果也出現過「清華大模型公開課」的第三方筆記，但沒有查到官方課程頁，所以沒有列。這三門學堂在線的課是否仍開放報名，請以頁面為準。

### 7.4 北京大學（PKU）

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| 人工智能原理 | 王文敏主講；介紹人工智能的發展歷程、核心思想、基本理論與應用。2017 年 10 月在中國大學 MOOC 首次開設，為國家精品在線開放課程；搜尋結果顯示第 14 次開課是 2024-03-18 至 2024-06-07，**已結束**，往期不提供結課證書 | [中國大學 MOOC](https://icourse163.org/course/PKU-1002188003) | ✅ |

> 北大的深度學習或大模型專門課程，這次**沒有查到**，所以沒有列。

### 7.5 浙江大學（ZJU）

| 課程 | 內容 | 連結 | 狀態 |
|---|---|---|---|
| 人工智能：模型與算法 | 吳飛主講，為國家級首批線上一流課程；內容含邏輯推理、搜尋求解、監督學習、無監督學習、深度學習、強化學習與博弈對抗，並有以深度學習為核心的垃圾分類實訓。對應教材是高等教育出版社的《人工智能導論：模型與算法》 | [中國大學 MOOC](https://www.icourse163.org/course/ZJU-1003377027) | ✅ |
| 機器學習 | 介紹支持向量機、人工神經網路、深度學習、強化學習等模組，含 PyTorch 的程式實驗；搜尋結果摘要也提到 GAN、RNN 與 LSTM、AlphaGo 解析。主講人我沒有確認 | [中國大學 MOOC](https://www.icourse163.org/course/ZJU-1206573810) | ✅ |

> 這次沒有查到浙大專門以「大模型」為主題的 MOOC；《人工智能：模型與算法》的摘要提到「智海-三樂」這個教育垂直領域大模型，是作為教學工具出現，不是課程主題。

### 7.6 平台入口

| 平台 | 說明 | 連結 | 狀態 |
|---|---|---|---|
| 中國大學 MOOC | 北大、浙大的課都放在這裡；搜尋「學校名稱」或教師姓名可找到更多 | [icourse163.org](https://www.icourse163.org) | ✅（課程頁所在的網站） |
| 學堂在線（XuetangX） | 清華的公開課所在平台 | [xuetangx.com](https://www.xuetangx.com) | ✅（課程頁所在的網站） |
| 國家高等教育智慧教育平台 | 彙整各校課程，搜尋結果顯示它也列有清華《大數據機器學習》 | [higher.smartedu.cn](https://higher.smartedu.cn) | ✅（課程頁所在的網站） |
| MIT OpenCourseWare | MIT 的開放課程平台 | [ocw.mit.edu](https://ocw.mit.edu) | ✅（課程頁所在的網站） |

### 7.7 依目標選大學課程

![圖：六種學習目標與優先課程](figures/ai-learning-resources-univ-choose.svg)

> 這是我依各課程的定位做的歸納，不是學校或平台的建議。

---

## 8. 持續追蹤：部落格、電子報與資料

| 來源 | 內容 | 狀態 |
|---|---|---|
| [Karpathy 的 YouTube 頻道](https://www.youtube.com/@AndrejKarpathy) | 追蹤他的新影片；他的個人網站把內容分成技術向與一般大眾向兩條線。網址取自第三方連結與他個人網站所列的頻道，我沒有開啟頻道頁面，不寫更新頻率與訂閱數 | 🔎 |
| [Lilian Weng：Lil'Log](https://lilianweng.github.io) | 長篇技術整理，常被引用為某個主題的入門總覽 | 🔎 |
| [Sebastian Raschka：Ahead of AI](https://magazine.sebastianraschka.com) | Substack 電子報，談 LLM 與研究進展 | 🔎 |
| [Jay Alammar 的部落格](https://jalammar.github.io) | 圖解文章 | 🔎 |
| [Epoch AI](https://epoch.ai/blog/will-we-run-out-of-data) | 訓練運算、資料與趨勢的研究；本庫 Scaling-Laws 引用它 | ✅ |
| [Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents) | Anthropic 的工程文章，含 agent 與 context 工程 | ✅ |

---

## 9. 依目標選資源

![圖：七種學習目標與優先資源](figures/ai-learning-resources-choose.svg)

> 這一節是我依各資源的定位做的歸納，不是官方建議。

---

## 10. 怎麼學比較有效

以下是建議，不是研究結論：

1. **每個階段都要有動手的產出**：例如跟著 Karpathy 寫出一個能生成文字的小模型，比只看影片更能暴露不懂的地方。
2. **論文先讀摘要、結論與圖表**，需要時再回頭讀方法；先讀本庫對應文件，再讀原文，可以少走彎路。
3. **數字以原文為準**：價格、模型規格、基準分數會變，本庫文件都標有資料日期。
4. **區分官方資訊與二手整理**：本文的「✅／🔎」就是為了讓你知道哪些我確認過、哪些要自己再核對。

---

## 11. 驗證說明與限制

- 驗證日期是 2026-11-16。我用網路搜尋核對各資源是否存在；沙箱連不到 `arxiv.org`，也沒有開啟多數課程官方頁面，所以標 🔎 的項目只能保證「有二手來源提到它存在」。
- 沒有核對的內容：各課程目前的版本與時數、書籍最新版次、Hugging Face LLM Course 與 MCP Course 的官方頁面、smol course 的目前版本、*AI for Everyone* 目前的價格與註冊方式、Karpathy 頻道頁面與兩支演講影片的網址與上傳日期、各互動視覺化網站目前是否可用與內容、Let's build GPT 影片頁面本身與兩個 GitHub 專案的目前狀態、3Blue1Brown 第 6、7 章與 LLM 簡介的確切網址和頻道頁面、李宏毅 YouTube 頻道頁面本身與各課程的單一播放清單網址、五篇 🔎 論文的 arXiv 編號。
- 這份清單不評價資源品質，也沒有涵蓋所有主題（例如電腦視覺、語音、強化學習專書）；它對應的是本筆記庫涵蓋的範圍。
- **第 7 節（大學課程）的補充**：驗證日期是 2026-11-17。我**沒有開啟任何課程頁面**，簡介取自搜尋結果的摘要。標 🔎 的有 CS231n、CS229、CS25 的網址（各課程慣用的位置，沒有在搜尋結果直接看到）與清華 AI 素養網站（官網新聞轉述）。沒有核對的還有：各課程的開課學期與是否仍開放、哪些有完整錄影、教師名單、CS224N 官方 YouTube 播放清單、CS231n 目前一期是否公開錄影、浙大《機器學習》的主講人。
- **第 7 節這次沒查到、因此沒有列的課程**：北大的深度學習與大模型課程、清華與浙大專門的大模型公開課、MIT 6.034 與 6.036。這不代表它們不存在；其他知名學校（例如 Berkeley、CMU、Harvard 的 CS50 AI）也沒有涵蓋，要擴充請指定學校。
- **第 5.2 節（模型廠商）的補充**：驗證日期是 2026-11-17；我**沒有開啟任何網站**。標 🔎 的有 Claude Cookbook、Gemini API 文件、Google AI Studio、DeepSeek API 文件與 GitHub 組織的網址；Anthropic Academy 的課程數、`anthropics/courses` 的時效、DeepSeek 的 API 模型名稱與 base URL 也都沒有核對。沒查到的項目見該節最後一段。
- 若發現連結失效或內容有誤，請在該項目標示 ⚠️ 並改為官方連結。

---

## 12. 官方來源

- Karpathy：<https://karpathy.ai>、<https://karpathy.ai/zero-to-hero.html>、<https://github.com/karpathy/nn-zero-to-hero>
- Karpathy 的 YouTube（網址取自二手來源，未開啟）：<https://www.youtube.com/@AndrejKarpathy>、<https://www.youtube.com/watch?v=kCc8FmEb1nY>（Let's build GPT）、<https://www.youtube.com/watch?v=zjkBMFhNj_g>、<https://www.youtube.com/watch?v=7xTGNNLPyMI>
- Stanford CS336（2025 春季存檔）：<https://stanford-cs336.github.io/spring2025/>
- DeepLearning.AI：*AI for Everyone*：<https://www.deeplearning.ai/courses/ai-for-everyone>、<https://www.coursera.org/learn/ai-for-everyone>
- 3Blue1Brown：<https://www.3blue1brown.com/neural-networks>、<https://www.3blue1brown.com/lessons/gpt>；頻道（網址取自二手來源，未開啟）：<https://www.youtube.com/@3blue1brown>
- 互動視覺化：<https://bbycroft.net/llm>、<https://github.com/bbycroft/llm-viz>、<https://poloclub.github.io/transformer-explainer/>、<https://github.com/poloclub/transformer-explainer>、<https://ojs.aaai.org/index.php/AAAI/article/view/35347>、<https://github.com/jessevig/bertviz>、<https://github.com/facebookresearch/llm-transparency-tool>、<https://aclanthology.org/2024.acl-demos.6.pdf>
- Hugging Face：<https://huggingface.co/learn>、<https://huggingface.co/learn/agents-course>、<https://huggingface.co/learn/smol-course>、<https://github.com/huggingface/smol-course>
- Manning：<https://www.manning.com/books/build-a-large-language-model-from-scratch>
- O'Reilly：<https://www.oreilly.com/library/view/hands-on-large-language/9781098150952/>
- Anthropic：<https://www.anthropic.com/engineering/building-effective-agents>、<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Model Context Protocol：<https://modelcontextprotocol.io/docs/getting-started/intro>
- 李宏毅個人網頁：<https://speech.ee.ntu.edu.tw/~hylee/index.php>
- 李宏毅 2024 春季課程資料：<https://speech.ee.ntu.edu.tw/~hylee/genai/2024-spring-course-data/0223/0223_course.pdf>
- 李宏毅 YouTube 頻道（網址取自二手彙整，未開啟）：<https://www.youtube.com/@HungyiLeeNTU/videos>
- Epoch AI：<https://epoch.ai/blog/will-we-run-out-of-data>
- 論文（arXiv）：<https://arxiv.org/abs/1706.03762>、<https://arxiv.org/abs/2001.08361>、<https://arxiv.org/abs/2203.15556>、<https://arxiv.org/abs/2005.11401>、<https://arxiv.org/abs/2205.14135>、<https://arxiv.org/abs/2305.13245>、<https://arxiv.org/abs/2307.03172>、<https://arxiv.org/abs/2405.04434>、<https://arxiv.org/abs/2501.12948>、<https://arxiv.org/abs/2408.04619>（Transformer Explainer）、<https://arxiv.org/abs/2412.19437>（DeepSeek-V3）
- Karpathy 的 GitHub 專案：<https://github.com/karpathy/ng-video-lecture>、<https://github.com/karpathy/nanoGPT>
- 官方文件：<https://code.claude.com/docs/en/features-overview.md>、<https://developers.openai.com/api/docs/guides/agents>、<https://developers.openai.com/codex/cli>
- 課程與教材入口：<https://huggingface.co/learn>、<https://d2l.ai>、<https://www.3blue1brown.com>
- 部落格與電子報（網址取自二手來源，未開啟）：<https://jalammar.github.io/illustrated-transformer/>、<https://jalammar.github.io>、<https://lilianweng.github.io>、<https://magazine.sebastianraschka.com>
- 李宏毅課程網頁：<https://speech.ee.ntu.edu.tw/~hylee/genai/2024-spring.php>、<https://speech.ee.ntu.edu.tw/~hylee/GenAI-ML/2025-fall.php>
- 史丹佛（第 7.1 節）：<https://web.stanford.edu/class/cs224n/>、<https://web.stanford.edu/class/cs224n/slides_w26/cs224n-2026-lecture01-intro.pdf>、<https://cs336.stanford.edu/spring2025>、<https://web.stanford.edu/class/cs25/>、<https://cs231n.stanford.edu>、<https://cs229.stanford.edu>
- MIT（第 7.2 節）：<https://introtodeeplearning.com/2022>、<https://introtodeeplearning.com/2021/index.html>、<https://introtodeeplearning.com/2020/>、<https://www.ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011>、<https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/pages/syllabus>、<https://ocw.mit.edu>
- 清華（第 7.3 節）：<https://www.xuetangx.com/course/THU08091001026/1076286>、<https://www.xuetangx.com/course/DP08091003375/>、<https://www.xuetangx.com/course/thu08091010085/18960834>、<https://higher.smartedu.cn/course/622ac974bee70ef79f3e4f41>、<https://yuketang.tsinghua.edu.cn/ai>（網址取自二手轉述）
- 北大（第 7.4 節）：<https://icourse163.org/course/PKU-1002188003>
- 浙大（第 7.5 節）：<https://www.icourse163.org/course/ZJU-1003377027>、<https://www.icourse163.org/course/ZJU-1206573810>
- 大學課程平台（第 7.6 節）：<https://www.icourse163.org>、<https://www.xuetangx.com>、<https://higher.smartedu.cn>
- 模型廠商（第 5.2 節）：<https://platform.claude.com/docs/en/>、<https://platform.claude.com/docs/en/api/overview>、<https://platform.claude.com/docs/zh-TW/api/overview>、<https://anthropic.skilljar.com/>、<https://anthropic.com/learn>、<https://github.com/anthropics/courses>、<https://github.com/anthropics/claude-cookbooks>（網址未直接見於搜尋結果）、<https://developers.openai.com>、<https://developers.openai.com/api/docs/models>、<https://developers.openai.com/api/docs/pricing>、<https://cookbook.openai.com>、<https://developers.openai.com/cookbook>、<https://ai.google.dev/gemini-api/docs>、<https://ai.google.dev/gemini-api/cookbook>、<https://github.com/google-gemini/cookbook>、<https://aistudio.google.com>、<https://api-docs.deepseek.com>、<https://github.com/deepseek-ai>
