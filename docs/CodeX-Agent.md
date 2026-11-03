# Codex 多 Agent 工作與 Code Review 指南

> 本文是 `Claude-Agent.md` 的 OpenAI Codex 對應版：聚焦「工作流程與選型」——何時用哪種平行工作方式、如何同時審查不同部分、如何追蹤與彙整。
> 指令與旗標的完整清單請見 `CodeX-CLI.md`；Agents SDK 與 coredump 分析架構請見 `openAI-python-agent.md`。
>
> 狀態：骨架草稿，逐節討論中。更新日期：2026-11-03

---

## 資料來源與驗證狀態

> **重要**：撰寫本文時，`developers.openai.com` 不在這個雲端 session 的允許網域內，**無法直接讀取 OpenAI 官方頁面**；本機也未安裝 `codex`，**無法用 `--help` 實測**。因此下列內容的來源與可信度分三級，後續每節都會沿用這些標記。

| 標記 | 意義 |
|------|------|
| ✅ 本地文件 | 取自 `CodeX-CLI.md`（codex-cli 0.137.0，2026-06-05 實測 help） |
| 🔎 官方（間接） | 官方頁面經網路搜尋摘要得到，**未直接讀取原頁**；細節以官方最新文件為準 |
| ⚠️ 未驗證 | 只見於第三方文章，或來源互相矛盾 |

**目前已掌握的重點：**

| 項目 | 狀態 | 內容 |
|------|------|------|
| Subagents 存在 | 🔎 | 可平行跑多個 agent 並彙整結果；**只有在你明確要求時才會 spawn** |
| 啟用方式 | ⚠️ | 實驗性功能；來源提到 `/experimental` 或 `config.toml` 的 `[features]` 旗標，**旗標名稱各來源不一致，需以當前版本確認** |
| 自訂 agent | 🔎 | 每個 agent 一個 TOML 檔，放 `~/.codex/agents/`（個人）或 `.codex/agents/`（專案）；可設描述、developer instructions、model、sandbox、MCP |
| 並行與深度上限 | 🔎 | `[agents]` 表：`max_threads` 預設 6、`max_depth` 預設 1（官方建議保持預設，避免 fan-out 暴增）、`job_max_runtime_seconds`（CSV 批次每 worker 逾時，預設 1800 秒）|
| Sandbox | 🔎 | subagent 繼承目前的 sandbox 政策，可針對單一 agent 覆寫（例如設唯讀）|
| 管理 | ✅🔎 | `/agent` 切換 agent thread（本地文件已列）；可要求 Codex steer / stop / close subagent |
| 適用場景與風險 | 🔎 | 適合讀取為主的工作（探索、測試、分流）；多個 agent 同時**寫**同一份程式碼會衝突；token 用量高於單 agent |
| GitHub code review | 🔎 | PR 留言 `@codex review` 觸發；可附焦點（如 `@codex review for security regressions`）；GitHub 上只標 P0 / P1；可設自動審新 PR；常駐規則寫在 repo 的 `AGENTS.md`；`@codex fix …` 可啟動雲端任務 |
| 本機 review 指令 | ✅ | `/review`、`codex review`、`codex exec review`（見 `CodeX-CLI.md` 第七、八章）|
| Codex Cloud | ✅ | `codex cloud exec/list/status/apply/diff`（見 `CodeX-CLI.md` 第十五章）|
| Worktree / 保留數量 | ⚠️ | 只見於第三方，且對保留數量說法不一，**不採用具體數字** |

**參考來源（官方頁面，間接）：**
[Subagents](https://developers.openai.com/codex/subagents)、
[Subagents 概念](https://developers.openai.com/codex/concepts/subagents)、
[GitHub integration](https://developers.openai.com/codex/integrations/github)、
[Cloud code review](https://developers.openai.com/codex/cloud/code-review)。

---

## 1. 概念與定位

> TODO：Codex 裡平行工作的幾種機制，逐一詳細介紹 —— Subagents（agent thread）、Codex Cloud 平行任務、`codex exec` 搭配多程序、`codex mcp-server` + Agents SDK 編排；並劃清 CLI 層級與 API 層級。

---

## 2. 平行工作方式的選型

> TODO：Workflow vs Worktree 釐清框（Codex 的隔離：git worktree vs sandbox 模式，兩件事）＋八欄選型對照表。

---

## 3. Code Review 的多 Agent 做法

> TODO：`/review`、`codex review`、`codex exec review`、Cloud 並行、手動分檔、GitHub `@codex review`，以及 review 相關指令總覽。

---

## 4. 如何追蹤與彙整

> TODO：`codex cloud list/status/diff/apply`、`resume` / `fork`、`/agent`、`/goal`、worktree 清理。

---

## 5. 實務建議與陷阱

> TODO：sandbox 與 approval 組合、成本、Git repo 限制、何時用哪種。

---

## 附錄 A　實戰範例：用 Codex 追蹤 fastpath 的 memory / refcount 難題

> TODO：與 `Claude-Agent.md` 附錄 A 同一情境，改用 Codex 分工與範例 prompt；可銜接 `openAI-python-agent.md` 的 coredump 分析架構。
