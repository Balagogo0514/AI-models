# AI 模型與 Agent 筆記庫

AI 模型、Agent 工程與開發工具的中文筆記集，涵蓋模型原理與訓練、Claude Code／Codex 等 Agent 工具的使用與選型，以及工作中的工程分析。以繁體中文撰寫。

> 共 13 篇筆記，另有 3 份工程分析。點標題即可開啟對應文件。

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
| [Claude Code 多 Agent 與 Code Review](docs/Claude-Agent.md) | 平行工作方式選型、多 Agent code review、追蹤彙整，含 fastpath refcount 實戰範例 |
| [Claude Code Skill／Plugin 比較](docs/Claude-Code-Skills.md) | superpowers 與 planning-with-files 的比較 |
| [Codex CLI](docs/CodeX-CLI.md) | OpenAI Codex CLI 的指令、sandbox、approval、設定的完整參考 |
| [Codex 多 Agent 與 Code Review](docs/CodeX-Agent.md) | Codex 的 Subagents、Cloud、`codex exec` 平行與 code review 做法 |
| [Python + OpenAI coredump 分析 Agent](docs/OpenAI-Python-Agent.md) | 以 Python 控制的 coredump 自動分析流程設計 |

## 工程分析

> 以下為工程分析文件，檔案保留在原位置，僅在此建立索引。

| 文件 | 主題 |
|---|---|
| [FRR-framework.md](FRR-framework.md) | 6WIND FastPath + FRR 架構與流程 |
| [fp-rte-crash-11332.md](fp-rte-crash-11332.md) | FP RTE Crash Analysis |
| [glibc-malloc-trim.md](glibc-malloc-trim.md) | glibc malloc_trim 對 conntrack fallback fragmentation 的修改評估 |

## 其他

| 項目 | 說明 |
|---|---|
| [c-code-review/](c-code-review/SKILL.md) | C 程式碼審查用的 skill（`SKILL.md`） |
| [AGENTS.md](AGENTS.md) | 協作規則：建立、修改、搬移或刪除檔案前，先說明並等待核准 |

---

## 文件約定

- **放置**：筆記一篇一檔，平放在 `docs/`。
- **命名**：英文 Title-Case 加連字號，例如 `Scaling-Laws.md`、`Claude-Code-CLI.md`。
- **結構**：`# 標題` → 簡介 → 數字編號的 `## 1.`、`## 2.` 章節。
- **圖片**：放在 `docs/figures/`（有第一張圖時再建立），筆記內以相對路徑引用，例如 `![說明文字](figures/example.svg)`，並寫完整的 alt 文字。
- **新增筆記時**：同步更新本 README 的對應分類表與上方的篇數。

## 閱讀方式

- **GitHub**：直接點上方連結，GitHub 會渲染 Markdown。
- **本機**：`git clone` 或 `git pull` 後，用 VS Code（`Ctrl/Cmd+Shift+V` 預覽）、Typora 或 Obsidian 開啟。
