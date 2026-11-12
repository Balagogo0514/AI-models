# AI 模型與 Agent 筆記庫

AI 模型、Agent 工程與開發工具的中文筆記集，涵蓋模型原理與訓練、Claude Code／Codex 等 Agent 工具的使用與選型。以繁體中文撰寫。

> 共 16 篇筆記。點標題即可開啟對應文件。

## 模型與訓練

| 筆記 | 內容 |
|---|---|
| [Scaling Laws](docs/Scaling-Laws.md) | 模型效能如何隨參數量、資料量、運算量變化的冪律關係 |
| [Post-Training](docs/Post-Training.md) | 預訓練之後的後訓練：讓模型更符合任務、偏好與安全需求 |
| [Transformer Attention](docs/Transformer-Attention.md) | MHA、MQA、GQA、MLA 等注意力強化機制與 KV cache 瓶頸 |
| [長上下文分析](docs/Long-Context-Note.md) | Lost in the Middle：為何模型容易遺失中段資訊 |
| [Claude 模型差異](docs/Claude-Model.md) | Sonnet／Opus／Fable 等模型的規格、價格與 API 差異 |
| [OpenAI 模型比較](docs/OpenAI-Model.md) | OpenAI 模型（API 版）的場景建議與比較 |

## Agent 與開發工具

| 筆記 | 內容 |
|---|---|
| [Agentic Engineering](docs/Agentic-Engineering.md) | Graph Engineering：把 Agent 執行流程建模為節點、狀態與轉移 |
| [Claude Code CLI](docs/Claude-Code-CLI.md) | Claude Code 指令、旗標、斜線指令、Hooks、MCP、Plugin 的完整參考 |
| [Claude Code Context 組成](docs/Claude-Context.md) | 送給 LLM 的 context 如何組成、記憶（CLAUDE.md／auto memory／逐字稿）放在哪、彼此是否取代 |
| [建立公司內部 plugin](docs/Claude-Plugin-Internal.md) | 把 skill、agent、MCP、local knowledge 包成內部 plugin：結構、manifest、測試、發佈與全公司強制啟用 |
| [企業整合模型：RAG、MCP、流程與資源判斷](docs/Enterprise-AI-Integration.md) | 六個整合層次、八階段流程、RAG 與 MCP 怎麼接內部資料與系統、權限階梯、API／自架／微調的資源與成本判斷 |
| [Claude Code 多 Agent 與 Code Review](docs/Claude-Agent.md) | 平行工作方式選型、多 Agent code review、追蹤彙整，含 fastpath refcount 實戰範例 |
| [Claude Code Skill／Plugin 比較](docs/Claude-Code-Skills.md) | superpowers、planning-with-files 與 grill-me 的比較 |
| [Codex CLI](docs/CodeX-CLI.md) | OpenAI Codex CLI 的指令、sandbox、approval、設定的完整參考 |
| [Codex 多 Agent 與 Code Review](docs/CodeX-Agent.md) | Codex 的 Subagents、Cloud、`codex exec` 平行與 code review 做法 |
| [Python + OpenAI coredump 分析 Agent](docs/OpenAI-Python-Agent.md) | 以 Python 控制的 coredump 自動分析流程設計 |

## 其他

| 項目 | 說明 |
|---|---|
| [c-code-review/](c-code-review/SKILL.md) | C 程式碼審查用的 skill（`SKILL.md`） |
| [tools/](tools/README.md) | 把 `docs/` 轉成網頁的建置腳本 |

---

## 文件約定

- **放置**：筆記一篇一檔，平放在 `docs/`。
- **命名**：英文 Title-Case 加連字號，例如 `Scaling-Laws.md`、`Claude-Code-CLI.md`。
- **結構**：`# 標題` → 簡介 → 數字編號的 `## 1.`、`## 2.` 章節。
- **圖片**：放在 `docs/figures/`，筆記內以相對路徑引用，例如 `![說明文字](figures/example.svg)`，並寫完整的 alt 文字。
- **新增筆記時**：同步更新本 README 的對應分類表與上方的篇數。

## 文件撰寫原則

### 1. 能用圖就用圖

- 流程、分流、比較、選型、層次與時間順序，優先畫成圖，再用文字補充；表格留給需要逐項查閱的資料。
- 圖要能單獨讀懂：標題說明「這張圖在回答什麼」，不要只當裝飾。
- 流程圖一律畫成 SVG，**不要用 mermaid 區塊**：網頁版與部分檢視環境不會渲染，只會顯示原始碼。

### 2. 圖的規格

- 格式為 SVG，`viewBox` 寬 640，手機上由頁面內捲動，不撐破版面。
- 色彩使用 CSS 變數，同時支援淺色與深色模式；用顏色以外的線索（文字、形狀、標記）傳達意義，不單靠顏色。
- 每張圖都有 `<title>`、`<desc>`，筆記內的 alt 文字寫出圖中的重點，不只寫「示意圖」。
- 檔名為 `<文件前綴>-<主題>.svg`，全小寫，例如 `claude-agent-chooser.svg`；一張圖只講一件事。
- 圖放進筆記後，確認：淺色與深色都看得清楚、文字沒有超出框、桌機與手機都沒有橫向捲軸。

### 3. 內容要有依據

- **只畫文件裡已有的內容**：圖是整理既有論述，不在圖裡新增數字、名詞或結論。
- **示意圖要標明**：曲線、連線模式、head 對應等概念圖，在圖與文字中註明「示意」，不當實測數據。
- **沿用文件已有的標記**（如 ✅、🔎、⚠️、🛠），不要在同一份文件裡新增含義不同的符號。
- **不確定就標出來**：文件寫「未驗證」「未公開」「傳言」「未單列」的項目，圖中同樣標示，不補數字、不推測。
- **文件之間或文件內有矛盾時**，不在圖裡擅自擇一；在圖與 PR 說明中標出，由作者決定怎麼改。

### 4. 日期與時效

- 價格、模型清單、版本這類會變的資料，標明資料日期（如「資料日期：2026-07-12」），並盡量附官方來源。
- 只補圖、沒有更新內容時，在文件開頭加一行說明「新增了哪些圖示、數值未更新、資料日期仍為何時」，避免讀者誤以為內容已重新查證。
- 閉源或未公開的架構，只寫公開文件能確認的部分；「未公開」不等於「沒有」，也不等於「採用某項技術」。

### 5. 變更流程

- 一次變更一個主題，開分支、commit、開 PR；合併前由審閱者確認。
- 新增或刪除筆記時，同步更新本 README 的分類表與篇數。
- 刪除已合併的遠端分支由維護者處理。

## 閱讀方式

- **GitHub**：直接點上方連結，GitHub 會渲染 Markdown。
- **本機**：`git clone` 或 `git pull` 後，用 VS Code（`Ctrl/Cmd+Shift+V` 預覽）、Typora 或 Obsidian 開啟。
- **網頁版**：`tools/build_site.py` 可把 `docs/` 轉成含首頁索引與章節目錄導覽的靜態網頁，用法見 [tools/README.md](tools/README.md)。
