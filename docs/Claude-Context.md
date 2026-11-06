# Claude Code 的 Context 如何組成：記憶放在哪裡？會互相取代嗎？

> 資料來源：Claude Code 官方文件 [Memory](https://code.claude.com/docs/en/memory.md)、[Explore the context window](https://code.claude.com/docs/en/context-window.md)、[Prompt caching](https://code.claude.com/docs/en/prompt-caching.md)、[Manage sessions](https://code.claude.com/docs/en/sessions.md)、[Explore the .claude directory](https://code.claude.com/docs/en/claude-directory.md)、[Subagents](https://code.claude.com/docs/en/sub-agents.md)、[Settings](https://code.claude.com/docs/en/settings.md)；另以 Claude Code v2.1.318 在本機（雲端容器）觀察檔案位置。
> 更新日期：2026-11-06
>
> 標記：✅ 官方文件明載　👁 本機實際觀察　⚠️ 官方未明載，屬推論或版本相依

---

## 一、先給答案

| 問題 | 簡短回答 |
|------|----------|
| 送給 LLM 的 context 怎麼組成？ | 每次請求都重送**整份** context：System prompt → 專案 context（CLAUDE.md、auto memory 索引、無條件 rules）→ 對話。模型在兩次請求之間不記得任何事。✅ |
| 「session memory」放在哪？ | **官方沒有這個詞**。⚠️ 它通常指下列幾件不同的東西：① 對話本身（只在記憶體與 context 中）；② 逐字稿 `~/.claude/projects/<project>/<session-id>.jsonl`（用來 resume）；③ 壓縮（compact）後留下的摘要。真正「跨 session 記住事情」的是 auto memory 與 CLAUDE.md。 |
| 專案目錄的 memory 是什麼？ | 要分兩種：**你寫的** `./CLAUDE.md`、`./.claude/rules/`、`./CLAUDE.local.md`（在專案目錄裡）；以及 **Claude 自己寫的 auto memory**（在 `~/.claude/projects/<project>/memory/`，**不在**專案目錄裡）。✅ |
| 會互相取代嗎？ | **大多不會。** CLAUDE.md 各層是疊加（concatenate）；CLAUDE.md 與 auto memory 是互補、同時載入。唯一的「取代」是：預設只在**找不到任何 CLAUDE.md** 時才改讀 AGENTS.md；以及 `/compact` 會把**對話**換成摘要（但記憶檔會從磁碟重新注入）。✅ |

---

## 二、一次請求裡有什麼

每次你送出訊息，Claude Code 都會發出一個新的 API 請求，並把完整 context 重送一次。依官方〈Prompt caching〉，順序是：System prompt（核心指示與工具定義）→ Project context（CLAUDE.md、auto memory、無條件 rules）→ Conversation。快取以「前綴」比對，所以越上面的內容越少變動。✅

![Claude Code 每次請求送出的 context 分三層：第一層 system prompt，第二層 project context（CLAUDE.md、auto memory 索引、無條件 rules），第三層對話；官方未標明層級的 skill 描述、MCP 工具名稱與 git 狀態也在啟動時載入](figures/claude-context-layers.svg)

### 2.1 啟動時就載入

依官方〈Explore the context window〉✅：

| 來源 | 說明 |
|------|------|
| CLAUDE.md | 各層檔案疊加；沒有任何 CLAUDE.md 時改讀 `AGENTS.md`（見 §五） |
| Auto memory | `MEMORY.md` 的前 200 行或 25KB（先到者為準） |
| 無條件的 `.claude/rules/*.md` | 沒有 `paths:` frontmatter 的規則 |
| MCP 工具名稱、Skill 名稱與描述 | 只有名稱／描述，完整內容用到才載入 |
| Output style、`--append-system-prompt` | 有設定才有 |
| Git 狀態快照 | 啟動時一份；可用 `includeGitInstructions` 關閉 |

> ⚠️ 官方文件把前三項歸在「Project context」，但沒有逐項標明 skill 描述、MCP 工具名稱、git 快照在請求裡的確切位置，所以圖中以虛線框另列。

### 2.2 之後才進來（按需載入）

這些內容進入**對話歷史**，不是啟動時的專案 context ✅：

- 你的訊息、Claude 的回應、每次工具呼叫的結果、讀進來的檔案內容
- 子目錄的 `CLAUDE.md`：Claude 讀、寫或編輯該子目錄的檔案時才載入
- 有 `paths:` 的 rules：讀到相符檔案時才載入
- 被呼叫的 skill 本文
- Hook 加入的 context
- Auto memory 的**主題檔**（例如 `feedback_testing.md`）：Claude 需要時用一般檔案工具讀取
- Subagent 回傳的摘要（subagent 自己的 context 是獨立的，見 §5.6）

### 2.3 它是 context，不是強制設定

CLAUDE.md 與 auto memory 都只是「放進 context 的文字」，Claude 會盡量遵守但不保證。要**強制**阻擋某個動作，官方建議用 PreToolUse hook，或用 `permissions.deny` 這類設定。✅

---

## 三、「Session memory」放在哪裡

**⚠️ 官方文件裡沒有「session memory」這個詞**（我對已下載的 Memory、Context window、Sessions、Prompt caching 等頁面搜尋過）。口語上它大概指下面四件事，位置與壽命都不同：

| 你可能指的 | 實際位置 | 壽命 | 會被載入下一個 session 嗎？ |
|-----------|----------|------|-----------------------------|
| 目前對話 | Claude Code 程序記憶體，以及每輪重送給 API 的 context | 到 `/clear`、`/compact` 或結束 | 否 |
| 逐字稿 | `~/.claude/projects/<project>/<session-id>.jsonl` | 預設 30 天（`cleanupPeriodDays`） | 只有 `--resume`／`--continue` 時還原對話 |
| 壓縮摘要 | 取代原本的對話歷史（仍在同一個 session 內） | 同上 | 隨逐字稿 resume |
| Scratchpad | `/tmp/claude-<uid>/<project>/<session-id>/scratchpad/` | 與逐字稿同壽命，系統重開機也可能清掉 | 否（Claude 放暫存檔的地方） |

👁 本機觀察：本 session 的逐字稿在 `~/.claude/projects/-home-user/<session-id>.jsonl`（約 13.6 MB），旁邊有 `tool-results/` 子目錄存放大型工具輸出。`<project>` 在這裡是工作目錄路徑把非英數字元換成 `-`。

**重點**：逐字稿是「紀錄」，不是「記憶」。新 session 不會自動把舊逐字稿讀進 context；只有你明確 resume，才會把那段對話還原。要讓下個 session 也知道的事，必須寫進 CLAUDE.md 或 auto memory。✅

---

## 四、記憶與設定檔放在哪裡

![記憶與 session 資料的位置：專案目錄放你寫的 CLAUDE.md、rules、CLAUDE.local.md、子目錄 CLAUDE.md 與 AGENTS.md；家目錄 ~/.claude 放個人 CLAUDE.md、auto memory 與逐字稿；系統層放組織管理的 CLAUDE.md；暫存目錄放 scratchpad](figures/claude-context-locations.svg)

### 4.1 你寫的指示（CLAUDE.md 家族）

| 位置 | 用途 | 載入時機 |
|------|------|----------|
| Linux／WSL：`/etc/claude-code/CLAUDE.md`；macOS：`/Library/Application Support/ClaudeCode/CLAUDE.md` | 組織管理 | 啟動；無法被 `claudeMdExcludes` 排除 |
| `~/.claude/CLAUDE.md`、`~/.claude/rules/` | 個人，所有專案 | 啟動 |
| `./CLAUDE.md` 或 `./.claude/CLAUDE.md`，以及上層目錄的同名檔 | 專案，團隊共享（進 git） | 啟動（工作目錄以上） |
| `./.claude/rules/*.md` | 專案規則 | 無 `paths:` 啟動載入；有 `paths:` 按需 |
| `./CLAUDE.local.md` | 個人專案偏好（應加進 `.gitignore`） | 啟動；同目錄內排在 `CLAUDE.md` 後面 |
| 子目錄的 `CLAUDE.md` | 局部規則 | Claude 讀寫該目錄檔案時 |

✅ 另有 `@path` 匯入語法（最多四層深）可把其他檔案併進 CLAUDE.md；被匯入的檔案跟著該 CLAUDE.md 一起載入，**不會**省 context。

### 4.2 Claude 自己寫的：auto memory

```text
~/.claude/projects/<project>/memory/
├── MEMORY.md          # 索引，啟動時載入前 200 行或 25KB
├── user_role.md       # 主題檔，不在啟動時載入，需要時才讀
└── feedback_testing.md
```

✅ 要點：

- `<project>` 取自 **git repo**：同一個 repo 的所有 worktree 與子目錄共用一份。不在 git repo 時以專案根目錄為準。
- **機器本機**：不會跨機器、跨雲端環境共享。
- 開關：`/memory` 裡切換，或設定 `autoMemoryEnabled`；位置可用 `autoMemoryDirectory` 改。
- 你可以直接編輯或刪除這些 markdown 檔；看到 "Saved N memories" 就是 Claude 在寫這個資料夾。
- 主對話的 auto memory **不會**載入 subagent（`fork` 例外）。

👁 本機觀察：這個雲端容器的 `~/.claude/projects/` 底下沒有 `memory/` 目錄，也沒有 CLAUDE.md／AGENTS.md。⚠️ 推論：auto memory 目錄是 Claude 寫入時才會出現，不是一開始就存在。

### 4.3 所以「專案目錄的 memory」到底是哪個？

| 你想講的 | 位置 | 誰寫 | 可進 git？ |
|---------|------|------|-----------|
| 專案層級的指示 | `./CLAUDE.md`、`./.claude/rules/` | 你 | 可以（團隊共享） |
| 你個人的專案偏好 | `./CLAUDE.local.md` | 你 | 不要（`.gitignore`） |
| Claude 學到的專案心得 | `~/.claude/projects/<project>/memory/` | Claude | 不在專案目錄內，預設不進 git |

---

## 五、這些會互相取代嗎？

![/compact 與 /clear 之後各種 context 來源的下場：根 CLAUDE.md、無條件 rules 與 auto memory 從磁碟重新注入；子目錄 CLAUDE.md 與條件式 rules 被摘要掉、用到時再載入；對話歷史換成結構化摘要](figures/claude-context-lifecycle.svg)

### 5.1 同類之間：疊加，不是覆寫

- **CLAUDE.md 各層**：所有找到的檔案**串接**進 context，而不是互相覆寫。順序是從檔案系統根目錄一路到工作目錄，所以越靠近你啟動位置的指示越後面讀到；同一目錄內 `CLAUDE.local.md` 在 `CLAUDE.md` 之後。✅
- **使用者規則與專案規則**：使用者層先載入、專案層後載入，但**互不覆寫**；兩者衝突時 Claude 可能照任一邊做，所以要自己保持一致。✅
- 因此：寫了互相矛盾的指示，行為是**不確定**的，不是「後者勝出」。

### 5.2 CLAUDE.md 與 auto memory：互補，同時存在

官方的說法是「兩套互補的記憶系統，每次對話開始都會載入」：CLAUDE.md 由你寫、放指示與規則；auto memory 由 Claude 寫、放它學到的偏好與慣例。✅ 一個不會把另一個擠掉，但**它們共用同一個 context 預算**——寫太長的 CLAUDE.md 或太肥的 MEMORY.md 都會讓其他內容更少空間。

### 5.3 唯一的「取代」：AGENTS.md

✅ 預設值 `claude-md-or-agents-md`：

| 你的 repo 有 | Claude 預設讀 |
|-------------|---------------|
| 只有 `AGENTS.md`，工作目錄及以上沒有 `CLAUDE.md`／`CLAUDE.local.md` | `AGENTS.md` |
| 兩者都有 | **只讀 CLAUDE.md** |
| CLAUDE.md 內 `@AGENTS.md` 匯入 | CLAUDE.md，AGENTS.md 經由匯入進來 |

- 注意：`CLAUDE.local.md` 也算「有 CLAUDE.md」。所以專案只靠 `AGENTS.md`、你再自己加一個 `CLAUDE.local.md`，反而會讓 AGENTS.md 不再被讀。
- 要兩個都讀：`/config` 把 **Project instructions** 改成 `claude-md-and-agents-md`。
- 需要 Claude Code v2.1.277 以上。

### 5.4 對話與記憶：`/compact` 與 `/clear`

| 操作 | 對話歷史 | 磁碟上的記憶（CLAUDE.md、auto memory） |
|------|----------|----------------------------------------|
| `/compact` | **換成結構化摘要** | 從磁碟**重新注入**（所以不會被摘要掉） |
| `/clear` | 清空（逐字稿仍在，可 resume） | 重新載入；此時你剛改的 CLAUDE.md 才會生效 |

✅ 其他細節（見圖）：

- 子目錄 CLAUDE.md 與有 `paths:` 的 rules 是進入**對話歷史**的，壓縮時會被一併摘要掉，之後用到才再載入。**要讓規則在壓縮後仍在，就拿掉 `paths:`，或搬進根目錄的 CLAUDE.md。**
- 讀過或編輯過的檔案：壓縮後最多重讀 5 個（最近修改的優先），超過 5,000 tokens 的只留路徑。
- 已呼叫的 skill 本文：重新注入，每個上限 5,000 tokens、合計 25,000 tokens，最舊的先丟。
- Skill 描述：重建後再注入（需 v2.1.304 以上）；git 狀態會重新取一份。
- 背景指令與背景 subagent 繼續執行，Claude 會被提醒哪些還在跑。
- 對話中途編輯 CLAUDE.md **不會立即生效**，要 `/clear`、`/compact` 或重啟才會重載。

### 5.5 設定檔不一樣：那是「覆寫」

`settings.json` 的優先順序是 managed > 命令列 > 專案 local > 專案共享 > 使用者，**較高層覆寫較低層**（陣列型設定會合併）。這和 CLAUDE.md 的「疊加」是兩套不同語意，別混為一談。✅ 更多見〈[Agentic-Engineering](Agentic-Engineering.md)〉的來源優先序整理。

### 5.6 Subagent 是獨立的 context

Subagent 以全新、隔離的 context 開始 ✅：

- **會有**：你交辦的任務訊息、CLAUDE.md 階層（Explore、Plan 除外）、git 狀態（Explore、Plan 除外）、預載的 skill
- **不會有**：主對話歷史、output style、主對話的 auto memory
- 只有摘要回到主對話，所以用 subagent 可以讓大量探索不佔主 context。

---

## 六、實務建議

1. **要跨 session 記住的事，寫進 CLAUDE.md 或讓 auto memory 記**，不要指望「同一個對話」。逐字稿只是紀錄。
2. **該遵守的規則放根目錄 CLAUDE.md**；只有局部適用的才用子目錄 CLAUDE.md 或 `paths:` rules，並記得它們壓縮後會消失、需重新觸發。
3. **控制長度**：單一 CLAUDE.md 建議在 200 行以內；`MEMORY.md` 超過 200 行或 25KB 的部分啟動時不會載入。
4. **用 `/memory` 檢視**目前有哪些記憶檔、開關 auto memory；用 `/context` 看實際 context 的分類用量。
5. **別讓指示互相矛盾**（user 規則 vs project 規則、不同層 CLAUDE.md）；矛盾時行為不確定。
6. **必須強制的事用 hook 或權限設定**，不要只靠 CLAUDE.md。
7. 用 AGENTS.md 與其他工具共用說明時：最穩的是在 CLAUDE.md 寫 `@AGENTS.md`，避免被 `CLAUDE.local.md` 意外遮蔽。
8. 除錯：懷疑沒載入時，`claude --bare` 或 `--safe-mode` 可排除自訂設定的干擾（見〈[Claude-Code-CLI](Claude-Code-CLI.md)〉）。

---

## 附錄：與本庫其他文件的出入

⚠️ 〈[Agentic-Engineering](Agentic-Engineering.md)〉某處寫「Auto memory 系統依 `description` 欄位判斷某條記憶是否相關才載入，而非把整個 `MEMORY.md` 全部塞進每次對話」。這與官方文件不一致：官方說 `MEMORY.md` 的**前 200 行或 25KB 每次啟動都會載入**，主題檔才是按需讀取。同一份文件前面的載入表格寫的是官方版本，兩處互相矛盾；以本文為準，該句待另行修正。

## 官方來源

- [Memory：How Claude remembers your project](https://code.claude.com/docs/en/memory.md)
- [Explore the context window](https://code.claude.com/docs/en/context-window.md)
- [Prompt caching](https://code.claude.com/docs/en/prompt-caching.md)
- [Manage sessions](https://code.claude.com/docs/en/sessions.md)
- [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory.md)
- [Subagents：What loads at startup](https://code.claude.com/docs/en/sub-agents.md#what-loads-at-startup)
- [Settings：Settings precedence](https://code.claude.com/docs/en/settings.md#settings-precedence)
