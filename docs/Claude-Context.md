# Claude Code 的 Context 如何組成：記憶放在哪裡？會互相取代嗎？

> 資料來源：Claude Code 官方文件 [Memory](https://code.claude.com/docs/en/memory.md)、[Explore the context window](https://code.claude.com/docs/en/context-window.md)、[Prompt caching](https://code.claude.com/docs/en/prompt-caching.md)、[Manage sessions](https://code.claude.com/docs/en/sessions.md)、[Explore the .claude directory](https://code.claude.com/docs/en/claude-directory.md)、[Subagents](https://code.claude.com/docs/en/sub-agents.md)、[Settings](https://code.claude.com/docs/en/settings.md)、[Extend Claude Code](https://code.claude.com/docs/en/features-overview.md)；另以 Claude Code v2.1.318 在本機（雲端容器）觀察檔案位置。
> 更新日期：2026-11-11
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
| 切換帳號會影響這些紀錄嗎？ | 本機的逐字稿與 auto memory 只依工作目錄路徑存放，不分帳號；換帳號後應該仍看得到並能 resume，但官方未明說 ⚠️，且模型、組織設定、啟動旗標不一定相同（見 §3.2）。 |
| skill、MCP、subagent、hook、plugin 對 context 的意義？ | 它們是在決定**什麼內容進 context、何時進、誰決定**：CLAUDE.md 與 output style 常駐；skill 只有描述常駐、本文按需；MCP 只有工具名稱常駐、**工具結果會進 context**；subagent 在獨立 context 做事、只回傳摘要；hook 在 context 外執行、零成本；plugin 只是打包層（見 §六）。對模型來說它們都只是 context（見 §6.1）。✅ |

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

### 3.1 逐字稿多久更新、多久清理

**寫入**：官方說 session 是「as you work 持續儲存」，每個訊息、工具呼叫與結果都會寫進逐字稿，沒有固定間隔。✅ 👁 本機驗證：逐字稿的修改時間與查詢當下完全相同。

**清理**：檔案超過 `cleanupPeriodDays` 就會被自動刪除。✅

| 項目 | 規則 |
|------|------|
| 期限 | 預設 30 天，最小 1，設 `0` 會驗證失敗；在 `settings.json` 調整 |
| 同一期限也適用於 | scratchpad、貼上的圖片、孤立的 worktree |
| 不受清理影響 | auto memory（`projects/<project>/memory/`）、`history.jsonl`（除非套用 HIPAA 設定） |
| Claude Desktop／Cowork 的逐字稿 | 預設不限年齡；用 `desktopSessionCleanupPeriodDays` 設期限（v2.1.248 以上） |
| 清理會被跳過 | `claude -p --bare` 那次執行；無法確定保留期限時（例如設定檔壞掉）會暫停，並在 `/status` 警告 |
| 立即清除 | `claude purge`（不動 temp 目錄裡的 scratchpad 與圖片） |

- ⚠️ 官方沒寫清理多久跑一次，也沒明說「年齡」從建立還是最後修改時間算起。
- 👁 本機有 `~/.claude/.last-cleanup`，內容是時間戳（觀察時為 `2026-11-06T01:37:50Z`，落在 session 進行途中，不像只在啟動時跑）。官方文件沒提到這個檔案，用途與間隔是推論。
- 逐字稿是**明文**：工具讀過的 `.env` 內容、印出的密碼都會留在裡面。介意就調小 `cleanupPeriodDays`。

### 3.2 切換帳號會怎樣

**不受影響（官方有明載或可由結構看出）**

- `projects/<project>/` 的 `<project>` 只由工作目錄路徑算出，路徑裡沒有帳號資訊。✅ 👁
- 登入身分存在 `~/.claude.json` 的 `oauthAccount`，不在 `projects/` 底下。👁
- 登出只刪帳號相關的快取：`policy-limits.json`（含 `.stamp.json`）與 `remote-settings.json`。官方沒有提到逐字稿。✅
- auto memory 與 CLAUDE.md 在磁碟上，不分帳號，新 session 照常載入。✅

**同一個工作目錄換帳號後，能 resume 舊帳號的 session 嗎？**

⚠️ **官方沒有明說，我也沒實測。** 依據：sessions 頁面把 resume 描述為讀取專案目錄的本機逐字稿，整頁沒有提到帳號是條件；存放路徑也沒有帳號分區。所以推論新帳號看得到、也能 resume。要確認，可在本機 `claude auth logout`，改用另一帳號登入，再 `claude --resume`。

**但「完全」還原不成立**

| 項目 | 換帳號後 |
|------|----------|
| 對話歷史 | 照舊還原；若曾壓縮，從最後一次壓縮的摘要與之後的訊息接續 ✅ |
| 模型 | 預設沿用 session 當時的模型 ✅；新帳號若無該模型權限會如何，官方未載 ⚠️ |
| 組織管理的設定與政策 | 換成新帳號所屬組織的 |
| 權限模式 | 依一般 resume 規則還原，與帳號無關 ✅ |
| 啟動旗標 | `--mcp-config`、`--settings`、`--plugin-dir`、`--fallback-model`、`--add-dir` 不會還原，要重新傳；`settings.json` 一類標準設定檔每次啟動重讀 ✅ |
| 逐字稿既有內容 | 原樣保留，包括舊帳號環境下的工具結果 |

**注意**

1. **隱私**：新帳號的使用者能讀到舊帳號對話與其中的密碼（明文）。多人共用一台機器時，每個帳號用不同的 `CLAUDE_CONFIG_DIR`（例如 `CLAUDE_CONFIG_DIR=/srv/tenant-a claude`），設定、session 歷史、auto memory 與外掛都會存到那裡。✅
2. **記憶一致性**：新帳號看到的 auto memory 是舊帳號的 Claude 累積的，之後會被新帳號的 session 繼續使用與修改。
3. 雲端（claude.ai）session 綁帳號，不在本機 `~/.claude`，不在此討論範圍。

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

✅ **兩種檔案 Claude Code 都接受**（可直接讀 `AGENTS.md` 當專案指示，不必先用 CLAUDE.md 匯入）。差別只在預設是否**同時**載入：預設值 `claude-md-or-agents-md` 一次只選一組。

| 你的 repo 有 | Claude 預設讀 |
|-------------|---------------|
| 只有 `AGENTS.md`，工作目錄及以上沒有 `CLAUDE.md`／`CLAUDE.local.md` | `AGENTS.md` |
| 兩者都有 | **只讀 CLAUDE.md** |
| CLAUDE.md 內 `@AGENTS.md` 匯入 | CLAUDE.md，AGENTS.md 經由匯入進來 |

- 注意：`CLAUDE.local.md` 也算「有 CLAUDE.md」。所以專案只靠 `AGENTS.md`、你再自己加一個 `CLAUDE.local.md`，反而會讓 AGENTS.md 不再被讀。
- 要兩個都讀：`/config` 把 **Project instructions** 改成 `claude-md-and-agents-md`（同目錄 `CLAUDE.md` 先載入、`AGENTS.md` 在後；已匯入或 symlink 的不會重複載入），或在 CLAUDE.md 裡寫 `@AGENTS.md`。
- 其他可選值：`claude-md`（只讀 CLAUDE.md）、`managed-only`（只讀組織管理的 CLAUDE.md 與 auto memory）。
- 需要 Claude Code v2.1.277 以上。

#### 子目錄的 AGENTS.md：載入時機與優先權

✅ 只有「沒有任何 CLAUDE.md」時（預設），AGENTS.md 才會被讀，載入分兩段：

| 位置 | 何時載入 |
|------|----------|
| 工作目錄**及以上各層**的 `AGENTS.md`、`.claude/AGENTS.md` | 啟動時全部載入 |
| 工作目錄**底下子目錄**的 `AGENTS.md` | Claude 用 **Read 工具**打開該子目錄的檔案時才載入 |

**優先權：沒有覆寫機制，只有串接。**

- 根目錄與子目錄的 AGENTS.md 同時存在於 context，沒有誰蓋掉誰。
- CLAUDE.md 的官方排序是「從檔案系統根目錄排到工作目錄，越靠近工作目錄越後面讀到」。⚠️ 官方沒有逐字說 AGENTS.md 也同樣排序，這是推論。
- 兩層互相矛盾時，官方只說 Claude 可能照任一邊做，**不保證後讀到的勝出**。要避免衝突，就別在兩層寫相反的規則。

與子目錄 CLAUDE.md 的差異 ✅：

| | 子目錄 `CLAUDE.md` | 子目錄 `AGENTS.md`（經 Project instructions 設定讀入） |
|--|--------------------|------------------------------------------------------|
| 觸發 | 讀、寫或編輯該目錄的檔案 | 只有 **Read** 該目錄的檔案 |
| 該子目錄另有 CLAUDE.md | 載入該 CLAUDE.md | **不讀**該目錄的 AGENTS.md（條件是子目錄沒有自己的三種 CLAUDE.md） |
| `InstructionsLoaded` hook | 會觸發 | 不觸發（被 CLAUDE.md 匯入或 symlink 的 AGENTS.md 則照常觸發） |

- ⚠️ `/compact` 後：官方對子目錄 CLAUDE.md 明說會被摘要掉、用到才重載；子目錄 AGENTS.md 同樣是按需載入進對話，推論行為相同。
- 確認有沒有讀到：在 session 裡用 `/memory` 找該路徑（v2.1.280 之前不會列出直接讀入的 AGENTS.md）。

實務建議：

1. 要讓子目錄規則可靠載入：在該子目錄放自己的 `CLAUDE.md`，內容寫 `@AGENTS.md`，觸發條件與 hook 就和 CLAUDE.md 一致。
2. 要根目錄與子目錄都吃到：把 **Project instructions** 設為 `claude-md-and-agents-md`。
3. 子目錄 AGENTS.md 不要放「必須全程遵守」的全域規則。

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

## 六、擴充機制（skill、MCP、subagent、hook、plugin）對 context 的意義

Claude Code 有一整層「擴充」機制，用來決定 Claude 知道什麼、能連到什麼、怎麼自動化。從 context 的角度看，它們的差別只有一件事：**什麼內容、在什麼時候、由誰決定，被放進 context window。**（本章依官方〈Extend Claude Code〉整理 ✅）

### 6.1 先釐清：對模型來說，skill 就是 context 中的一段內容

模型只看得到 token；「skill」「MCP」「subagent」這些名詞都是 **harness（Claude Code 這層）的概念**，不是模型的概念。所以回答「skill 是不是只是 context 中的某段內容」：**對模型，幾乎是；對整個機制，不只。**

![skill 的四個層次：文字層與載入層在 context 內，harness 規則與附帶的腳本、hook 在 context 外運作](figures/claude-context-skill-layers.svg)

| 層 | 內容 | 是不是 context |
|---|---|---|
| ① **文字層** | SKILL.md 的描述與本文 | 是。官方說 skill 是「Claude 讀了再遵循的指示」，Claude 在詮釋它，所以結果會變 ✅ |
| ② **載入層** | 描述每次請求常駐；本文被呼叫時才載入；壓縮後重新注入，單個 ≤5,000、合計 ≤25,000 tokens ✅ | harness 的規則，決定「何時、多少」進 context |
| ③ **harness 規則** | `disable-model-invocation`（被擋下時 Claude Code 會封鎖該次呼叫）、`allowed-tools`（免詢問放行，但**不限制**有哪些工具可用）、`paths`（限制啟用範圍）、`context: fork`（在隔離的 subagent 跑）✅ | **不是文字**，是 harness 執行的規則 |
| ④ **附帶能力** | 隨 skill 附的腳本、plugin 的 hook | 在 context 外執行，只有輸出會進來 ✅ |

**一句話**：skill 的**內容**是 context，skill 的**行為保證**不是。

**這個看法的實際意義**

1. **skill、CLAUDE.md、貼進對話的文字，在模型眼中沒有本質差別**，差別只在「何時載入」「誰決定」「能不能復用與打包」。
2. **skill 的價值在於延遲載入**：不像 CLAUDE.md 每次都付費，用到才進來。這是 context 管理，不是新能力。
3. **要「保證」就不能靠 skill**：模型是否採用它由模型決定；要強制，用 hook 或權限設定 ✅。
4. **多個 skill 衝突，就是同一份 context 裡的指示互相打架**，沒有仲裁（見〈[Claude-Code-Skills](Claude-Code-Skills.md)〉）。
5. **描述是路由訊號**：它決定 skill 會不會在對的時候被載入，描述重疊就會挑錯 ✅。
6. **真正讓 skill 多於文字的是腳本**：腳本在 context 外執行，只把結果帶回來，這也是省 token 的來源。

> ⚠️ skill 本文被載入時，是以什麼訊息角色進入對話（工具結果、使用者訊息或其他），官方只說「完整內容載入到對話」，沒有說明角色。所以不能斷言它相對於你的指示是優先還是次要，只能說它是對話歷史的一部分。

### 6.2 各名詞的作用與對 context 的影響

| 名詞 | 是什麼、為什麼存在 | 誰決定用 | 對 context 的實質影響 |
|------|--------------------|----------|------------------------|
| **CLAUDE.md／rules** | 你寫的「永遠要知道」的規則：慣例、build 指令 | 自動載入 | **每次請求都付費**；官方建議 200 行內 |
| **Output style** | 設定回應的角色、語氣、格式 | 你切換 | 啟用中的完整指示每次都在；Default 風格不佔 |
| **Skill** | 可重複使用的知識或工作流（`/deploy`） | 你用 `/名稱`，或 Claude 依描述比對 | **描述每次都在**（成本低），**本文用到才載入**；設 `disable-model-invocation: true` 則用到前完全不佔 |
| **MCP** | 連外部服務的**協定**，提供工具與資料存取 | Claude 呼叫 | 啟動只載工具名稱與 server 指示，完整 schema 延後（tool search 預設開啟）；**工具回傳的結果會進 context**，這才是主要成本 |
| **Subagent** | 在**獨立 context** 跑自己迴圈的工作者 | Claude 或你生成 | 不佔主對話；中間過程留在它自己的 context，**只有摘要回來** |
| **Dynamic workflow** | Claude 寫的腳本，背景跑很多 subagent，回傳一個結果 | 腳本決定下一步 | 同 subagent；由腳本而非 Claude 逐輪決定 |
| **Hook** | 在生命週期事件（編輯後、送出前等）自動執行的腳本、HTTP、MCP 呼叫、prompt 或 subagent | 事件觸發，**不經 Claude 判斷** | **零成本**，除非它回傳輸出（輸出會成為對話的一部分） |
| **Plugin／Marketplace** | **打包與分發層**：把 skills、hooks、subagents、MCP 包成一個可安裝單位；plugin 的 skill 加命名空間（如 `/my-plugin:review`） | 你安裝 | 本身不另外佔 context ⚠️（推論）；裡面各元件各自遵守上列規則 |
| **Code intelligence（LSP）** | 讓 Claude 用語言伺服器做符號導覽與型別錯誤 | Claude | 低；常能取代大範圍讀檔，淨用量可能下降 |

### 6.3 什麼時候進入 context

![各擴充機制何時進入 context：常駐（CLAUDE.md、rules、auto memory 索引、output style、skill 名稱與描述、MCP 工具名稱）、按需（skill 本文、MCP 完整 schema、子目錄 CLAUDE.md、檔案、工具結果、hook 輸出）、隔離（subagent、workflow）、不進（hook、plugin）](figures/claude-context-extensions-loading.svg)

- **常駐**的內容每次請求都要付費，所以越短越好，細節移到按需的地方。
- **按需**的內容進入對話歷史，`/compact` 時會被一起摘要掉（見 §5.4）。
- 用 `/context all` 可以看每個已載入的 MCP 工具用了多少 tokens；用 `/mcp` 看各 server 狀態，不用的 server 可以斷線。✅

### 6.4 這件事該放哪

![依序問六個問題決定放哪：永遠要遵守的放 CLAUDE.md；必須每次發生的放 hook；有時才需要的放 skill；連外部服務用 MCP；大量中間輸出交給 subagent；多 repo 重用則打包成 plugin](figures/claude-context-extensions-decision.svg)

官方的經驗法則（節錄）：

| 觸發情況 | 該加什麼 |
|----------|----------|
| Claude 同一個慣例或指令錯了兩次 | 寫進 CLAUDE.md |
| 你第三次把同一份流程貼進對話 | 存成 skill |
| 你一直從 Claude 看不到的系統複製資料 | 接成 MCP server |
| 一個旁支任務的輸出灌爆對話，之後又不會引用 | 交給 subagent |
| 想讓某件事每次都發生，不必開口要求 | 寫成 hook |
| 第二個 repo 需要同樣的設定 | 打包成 plugin |

**重點差異**

- **CLAUDE.md vs Skill**：CLAUDE.md 每個 session 自動載入，放「永遠要遵守」；skill 按需載入，放參考資料與可觸發的流程。
- **Skill vs Subagent**：skill 是可載入任何 context 的內容，會**增加**主視窗；subagent 是隔離的工作者，用**另一個**視窗。兩者可以搭配：subagent 預載 skill（`skills:` 欄位），skill 也能用 `context: fork` 在隔離環境執行。
- **MCP vs Skill**：MCP 提供**工具與資料存取**；skill 提供**怎麼用這些工具的知識**。兩者解決不同問題，常一起用。
- **Hook vs Skill**：hook 在事件發生時**確定執行**，不經 Claude 判斷；skill 是 Claude **讀了再詮釋**的指示，結果會變。「絕不編輯 `.env`」寫在 CLAUDE.md 或 skill 裡只是請求，用 `PreToolUse` hook 擋下才是強制。

### 6.5 同名時：疊加、合併還是覆寫

![同一種機制在多個層級都有定義時的語意：CLAUDE.md 疊加、hook 合併；skill、subagent、MCP server 依名稱覆寫並各有優先序；settings.json 較高層覆寫較低層](figures/claude-context-extensions-layering.svg)

### 6.6 搭配方式

| 組合 | 做法 | 例子 |
|------|------|------|
| Skill + MCP | MCP 提供連線，skill 教 Claude 怎麼用好 | MCP 連資料庫，skill 記錄 schema 與查詢慣例 |
| CLAUDE.md + Skill | CLAUDE.md 放常駐規則，skill 放按需參考 | CLAUDE.md 寫「遵守我們的 API 慣例」，skill 放完整 API 指南 |
| Skill + Subagent | skill 同時啟動多個 subagent 平行工作 | `/audit` 啟動安全、效能、風格三個 subagent |
| Hook + MCP | hook 透過 MCP 觸發外部動作 | 編輯重要檔案後，hook 透過 MCP 發 Slack 通知 |

### 6.7 「Agent」有兩種意思

- **概念上的 agent**：模型加工具加一個迴圈（蒐集 context → 行動 → 驗證）。Claude Code 本身就是這樣運作。
- **Claude Code 的 subagent**：這個迴圈的「分身」，擁有獨立 context，用來隔離雜訊或平行處理；它不會繼承主對話歷史與主對話的 auto memory（見 §5.6）。

> 別家產品的對應名詞與行為不一定相同（例如 Codex 同樣讀 AGENTS.md、也有自己的 MCP 設定），本章只以 Claude Code 官方文件為準；Codex 的做法見〈[CodeX-CLI](CodeX-CLI.md)〉。

---

## 七、實務建議

1. **要跨 session 記住的事，寫進 CLAUDE.md 或讓 auto memory 記**，不要指望「同一個對話」。逐字稿只是紀錄。
2. **該遵守的規則放根目錄 CLAUDE.md**；只有局部適用的才用子目錄 CLAUDE.md 或 `paths:` rules，並記得它們壓縮後會消失、需重新觸發。
3. **控制長度**：單一 CLAUDE.md 建議在 200 行以內；`MEMORY.md` 超過 200 行或 25KB 的部分啟動時不會載入。
4. **用 `/memory` 檢視**目前有哪些記憶檔、開關 auto memory；用 `/context` 看實際 context 的分類用量。
5. **別讓指示互相矛盾**（user 規則 vs project 規則、不同層 CLAUDE.md）；矛盾時行為不確定。
6. **必須強制的事用 hook 或權限設定**，不要只靠 CLAUDE.md。
7. 用 AGENTS.md 與其他工具共用說明時：最穩的是在 CLAUDE.md 寫 `@AGENTS.md`，避免被 `CLAUDE.local.md` 意外遮蔽。
8. **把常駐內容壓到最小**：CLAUDE.md 只放「永遠要遵守」；參考資料移進 skill；用不到的 MCP server 斷線；會吃 context 的旁支任務交給 subagent。
9. 除錯：懷疑沒載入時，`claude --bare` 或 `--safe-mode` 可排除自訂設定的干擾（見〈[Claude-Code-CLI](Claude-Code-CLI.md)〉）。

---

## 附錄：與本庫其他文件的出入

〈[Agentic-Engineering](Agentic-Engineering.md)〉曾寫「Auto memory 系統依 `description` 欄位判斷某條記憶是否相關才載入，而非把整個 `MEMORY.md` 全部塞進每次對話」，與官方不一致（官方：`MEMORY.md` 前 200 行或 25KB 每次啟動都載入，主題檔才按需讀取）。該句已改為與官方一致的說法。

## 官方來源

- [Memory：How Claude remembers your project](https://code.claude.com/docs/en/memory.md)
- [Explore the context window](https://code.claude.com/docs/en/context-window.md)
- [Prompt caching](https://code.claude.com/docs/en/prompt-caching.md)
- [Manage sessions](https://code.claude.com/docs/en/sessions.md)
- [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory.md)
- [Subagents：What loads at startup](https://code.claude.com/docs/en/sub-agents.md#what-loads-at-startup)
- [Settings：Settings precedence](https://code.claude.com/docs/en/settings.md#settings-precedence)
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview.md)：各擴充機制的選擇與 context 成本
