# AI 學習資源

> 資料日期：2026-11-16  
> 範圍：整理學習 AI 模型、LLM 與 Agent 的課程、書籍、論文、官方文件與持續追蹤的來源，並對應到本筆記庫的文件。  
> 讀法：每個資源都標示驗證狀態——**✅** 表示我查到官方頁面、出版方頁面，或本庫文件已引用；**🔎** 表示只有二手來源確認它存在，連結與內容請自行核對。課程、書籍與網站會更新，請以官方頁面為準。

## 先看結論

- **非技術背景**：先看吳恩達的 *AI for Everyone*（不需寫程式），了解 AI 能做什麼、怎麼導入與對社會的影響。
- **想建立直覺**：先看 3Blue1Brown 的[神經網路系列](https://www.3blue1brown.com/neural-networks)，再看 Karpathy 的 [*Neural Networks: Zero to Hero*](https://karpathy.ai/zero-to-hero.html)；想先聽概念，可看他的 [*Intro to Large Language Models*](https://www.youtube.com/watch?v=zjkBMFhNj_g) 演講。
- **想自己動手**：Karpathy 的[系列](https://karpathy.ai/zero-to-hero.html) → Raschka 的 *Build a Large Language Model (From Scratch)* → Stanford CS336。
- **想用 LLM 做應用或 Agent**：Chip Huyen 的 *AI Engineering*、Hugging Face 的 Agents Course、Anthropic 的 *Building effective agents*，再讀各家官方文件。
- **偏好中文**：台大李宏毅老師的課程是最常被推薦的起點，影片主頁見第 6 節的 [YouTube 頻道](https://www.youtube.com/@HungyiLeeNTU/videos)；上海交大也有公開的講義與實作教程，同樣在第 6 節。
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
| Hugging Face：LLM Course（[Hugging Face Learn](https://huggingface.co/learn)） | transformers、微調、部署 | 🔎 |
| [Hugging Face：Agents Course](https://huggingface.co/learn/agents-course) | 免費；涵蓋 smolagents、LlamaIndex、LangGraph；需要免費的 Hugging Face 帳號 | ✅ |

> Karpathy 系列的影片編號各來源說法不一（例如 tokenizer 是第幾講），請直接看官方頁面或播放清單，不要依編號找。

### 3.2 書與文章

| 資源 | 內容 | 狀態 |
|---|---|---|
| [Sebastian Raschka：*Build a Large Language Model (From Scratch)*](https://www.manning.com/books/build-a-large-language-model-from-scratch) | Manning，2024 年 9 月；從設計、預訓練到微調，一步步自己做一個 LLM | ✅ |
| [Jay Alammar、Maarten Grootendorst：*Hands-On Large Language Models*](https://www.oreilly.com/library/view/hands-on-large-language/9781098150952/) | O'Reilly，2024 年 9 月；以視覺化方式講如何運用預訓練模型做分類、RAG、多模態 | ✅ |
| Chip Huyen：*AI Engineering*（O'Reilly） | 在既有基礎模型上做應用：評測、prompt、RAG 與 agents、微調、資料集工程、推論最佳化 | 🔎（出版年份各來源不一，請以 O'Reilly 頁面為準） |
| [Jay Alammar：*The Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/) | 2018 年的圖解文章，一步步拆解 self-attention 與 encoder-decoder | 🔎 |

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

## 5. Agent 與開發工具：官方文件

| 資源 | 內容 | 本庫對應 | 狀態 |
|---|---|---|---|
| [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)（2024-12-19） | 區分 workflow 與 agent，建議先用簡單模式、不要一開始就上重型框架 | [Agentic-Engineering](Agentic-Engineering.md) | ✅ |
| [Anthropic：Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | context 工程與長時程 agent 的做法 | [Claude-Context](Claude-Context.md) | ✅（本庫已引用） |
| [Claude Code 文件](https://code.claude.com/docs/en/features-overview.md) | 功能總覽、skills、plugins、MCP、context window 等 | [Claude-Code-CLI](Claude-Code-CLI.md) | ✅（本庫已引用） |
| [Model Context Protocol 文件](https://modelcontextprotocol.io/docs/getting-started/intro) | MCP 的官方介紹與規格；文件有依協議版本分開的副本，引用時要註明版本 | [Claude-Code-CLI](Claude-Code-CLI.md) | ✅ |
| [OpenAI API：Agents 指南](https://developers.openai.com/api/docs/guides/agents) | OpenAI 的 agent 開發指南 | [OpenAI-Python-Agent](OpenAI-Python-Agent.md) | ✅（本庫已引用） |
| [Codex 文件](https://developers.openai.com/codex/cli) | Codex CLI、sandbox、subagents 等 | [CodeX-CLI](CodeX-CLI.md)、[CodeX-Agent](CodeX-Agent.md) | ✅（本庫已引用） |

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
| 上海交大：《動手學大模型》（*Dive into LLMs*） | 由上海交通大學《自然語言處理前沿技術》（NIS8021）、《人工智能安全技術》（NIS3353）的講義拓展而來，授課教師為張倬勝；定位為免費、公益性質的實作教程，附教程文檔與 Slides。我只看到第三方的 [Gitee 鏡像](https://gitee.com/hbwei/dive-into-llms)，沒有核對官方（GitHub）專案網址；影片請到 B 站搜尋「動手學大模型」或「張倬勝」，我沒有確認是否有錄影 | 🔎 |
| 上海交大 NLP 課程組講義（cs2916） | 公開在 `gair-nlp.github.io/cs2916` 的投影片，例如[第 1 講（part 1）](https://gair-nlp.github.io/cs2916/assets/files/lecture-01-part1-9be930f9852f269ab8c9267df3ae97e8.pdf)；搜尋結果顯示另有一講涵蓋機器翻譯、Transformer 與大模型（作者林洲漢）。只有投影片，沒有確認錄影 | 🔎 |
| 上海交大約翰·霍普克羅夫特中心（John Hopcroft Center）課程頁 | 有[機器學習（CS420，張偉楠；2019 春季頁面）](https://jhc.sjtu.edu.cn/courses/2019/0305/18.html)與[人工智能（李帥；2021 秋季頁面）](https://jhc.sjtu.edu.cn/courses/2021/1112/44.html)等課程頁；李帥的 VE445 機器學習[第 1 講投影片](https://shuaili8.github.io/Teaching/VE445/L1_intro_light.pdf)也公開。這些是舊學期的課程頁與講義，內容可能已更新，我沒有確認有公開錄影 | ✅（頁面存在）／🔎（內容與時效） |

> 上海交大的公開資源，我查到的以**課程網站與講義、實作教程**為主；沒有查到官方的 MOOC 課程或可確認的完整錄影。要找影片，建議到中國大學 MOOC（icourse163.org）搜尋「上海交通大學」，或到各教師的個人網頁確認；我沒有在這個環境開啟這些網站。
| 本筆記庫 | 繁體中文、含圖示，主題見網站首頁或 GitHub 的 README 索引 | ✅ |

---

## 7. 持續追蹤：部落格、電子報與資料

| 來源 | 內容 | 狀態 |
|---|---|---|
| [Lilian Weng：Lil'Log](https://lilianweng.github.io) | 長篇技術整理，常被引用為某個主題的入門總覽 | 🔎 |
| [Sebastian Raschka：Ahead of AI](https://magazine.sebastianraschka.com) | Substack 電子報，談 LLM 與研究進展 | 🔎 |
| [Jay Alammar 的部落格](https://jalammar.github.io) | 圖解文章 | 🔎 |
| [Epoch AI](https://epoch.ai/blog/will-we-run-out-of-data) | 訓練運算、資料與趨勢的研究；本庫 Scaling-Laws 引用它 | ✅ |
| [Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents) | Anthropic 的工程文章，含 agent 與 context 工程 | ✅ |

---

## 8. 依目標選資源

![圖：七種學習目標與優先資源](figures/ai-learning-resources-choose.svg)

> 這一節是我依各資源的定位做的歸納，不是官方建議。

---

## 9. 怎麼學比較有效

以下是建議，不是研究結論：

1. **每個階段都要有動手的產出**：例如跟著 Karpathy 寫出一個能生成文字的小模型，比只看影片更能暴露不懂的地方。
2. **論文先讀摘要、結論與圖表**，需要時再回頭讀方法；先讀本庫對應文件，再讀原文，可以少走彎路。
3. **數字以原文為準**：價格、模型規格、基準分數會變，本庫文件都標有資料日期。
4. **區分官方資訊與二手整理**：本文的「✅／🔎」就是為了讓你知道哪些我確認過、哪些要自己再核對。

---

## 10. 驗證說明與限制

- 驗證日期是 2026-11-16。我用網路搜尋核對各資源是否存在；沙箱連不到 `arxiv.org`，也沒有開啟多數課程官方頁面，所以標 🔎 的項目只能保證「有二手來源提到它存在」。
- 沒有核對的內容：各課程目前的版本與時數、書籍最新版次、Hugging Face LLM Course 的官方頁面、*AI for Everyone* 目前的價格與註冊方式、Karpathy 頻道頁面與兩支演講影片的網址與上傳日期、Let's build GPT 影片頁面本身與兩個 GitHub 專案的目前狀態、3Blue1Brown 第 6、7 章與 LLM 簡介的確切網址和頻道頁面、上海交大各項資源是否有公開錄影、《動手學大模型》官方專案網址、李宏毅 YouTube 頻道頁面本身與各課程的單一播放清單網址、五篇 🔎 論文的 arXiv 編號。
- 這份清單不評價資源品質，也沒有涵蓋所有主題（例如電腦視覺、語音、強化學習專書）；它對應的是本筆記庫涵蓋的範圍。
- 若發現連結失效或內容有誤，請在該項目標示 ⚠️ 並改為官方連結。

---

## 11. 官方來源

- Karpathy：<https://karpathy.ai>、<https://karpathy.ai/zero-to-hero.html>、<https://github.com/karpathy/nn-zero-to-hero>
- Karpathy 的 YouTube（網址取自二手來源，未開啟）：<https://www.youtube.com/@AndrejKarpathy>、<https://www.youtube.com/watch?v=kCc8FmEb1nY>（Let's build GPT）、<https://www.youtube.com/watch?v=zjkBMFhNj_g>、<https://www.youtube.com/watch?v=7xTGNNLPyMI>
- Stanford CS336（2025 春季存檔）：<https://stanford-cs336.github.io/spring2025/>
- DeepLearning.AI：*AI for Everyone*：<https://www.deeplearning.ai/courses/ai-for-everyone>、<https://www.coursera.org/learn/ai-for-everyone>
- 3Blue1Brown：<https://www.3blue1brown.com/neural-networks>、<https://www.3blue1brown.com/lessons/gpt>；頻道（網址取自二手來源，未開啟）：<https://www.youtube.com/@3blue1brown>
- Hugging Face Agents Course：<https://huggingface.co/learn/agents-course>
- Manning：<https://www.manning.com/books/build-a-large-language-model-from-scratch>
- O'Reilly：<https://www.oreilly.com/library/view/hands-on-large-language/9781098150952/>
- Anthropic：<https://www.anthropic.com/engineering/building-effective-agents>、<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Model Context Protocol：<https://modelcontextprotocol.io/docs/getting-started/intro>
- 上海交大：<https://jhc.sjtu.edu.cn/courses/2019/0305/18.html>、<https://jhc.sjtu.edu.cn/courses/2021/1112/44.html>、<https://shuaili8.github.io/Teaching/VE445/L1_intro_light.pdf>、<https://gair-nlp.github.io/cs2916/assets/files/lecture-01-part1-9be930f9852f269ab8c9267df3ae97e8.pdf>、Gitee 鏡像 <https://gitee.com/hbwei/dive-into-llms>
- 李宏毅個人網頁：<https://speech.ee.ntu.edu.tw/~hylee/index.php>
- 李宏毅 2024 春季課程資料：<https://speech.ee.ntu.edu.tw/~hylee/genai/2024-spring-course-data/0223/0223_course.pdf>
- 李宏毅 YouTube 頻道（網址取自二手彙整，未開啟）：<https://www.youtube.com/@HungyiLeeNTU/videos>
- Epoch AI：<https://epoch.ai/blog/will-we-run-out-of-data>
