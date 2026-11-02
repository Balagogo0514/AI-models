# Claude Code 多 Agent 工作與 Code Review 指南

> 本文聚焦「工作流程與選型」：何時用哪種平行工作方式、如何同時審查不同部分、如何追蹤與彙整。
> 指令與參數的完整清單請見 `Claude-Code-CLI.md`（第十四章 Multi-agent 使用方法）。
>
> 狀態：骨架草稿，逐節討論中。更新日期：2026-11-02

---

## 1. 概念與定位

> TODO：釐清四個容易混淆的詞 —— Subagents、Agent teams、Workflows、Managed Agents / Agent SDK，各自解決什麼問題、誰跑在哪裡。

---

## 2. 四種平行工作方式的選型

> TODO：比較表 —— 誰決定下一步、中間結果放哪、檔案隔離方式、可否重播、規模、如何追蹤。

---

## 3. Code Review 的多 Agent 做法

> TODO：
> - `/code-review ultra`（雲端多 reviewer + 每個 finding 獨立驗證）
> - 手動派多個 subagent 分檔／分模組審查
> - 各自的追蹤方式與適用時機

---

## 4. 如何追蹤與彙整

> TODO：狀態圖示、peek 面板、task 通知、`/tasks` 與 Agent View、worktree 清理。

---

## 5. 實務建議與陷阱

> TODO：何時用哪種、token 成本、文件 vs 程式碼審查的差異、常見誤用。
