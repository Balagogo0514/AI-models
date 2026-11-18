# Claude Code 如何結合 React 本機開發

> 資料日期：2026-11-18  
> 範圍：在本機用 Claude Code 開發 React 專案（Vite、Next.js 等）的工作流程：專案設定、權限、dev server 與測試、瀏覽器驗證、hooks、平行開發與 CI。  
> 讀法：文中分兩種內容——**【官方】** 表示功能與設定語法取自本庫已整理的官方資料（[Claude-Code-CLI](Claude-Code-CLI.md)、[Claude-Context](Claude-Context.md)、[Agentic-Engineering](Agentic-Engineering.md)），或官方 Chrome 整合頁面；**【建議】** 是我依這些功能整理的 React 開發做法，**不是官方指定流程**。React 專屬的部分（元件目錄、測試工具、dev server 的用法）沒有官方依據，都屬於【建議】。  
> ⚠️ **我沒有實際在 React 專案上跑過本文的流程**；範例是依文件寫的，請在你的專案上先小範圍試用。

## 先看結論

- **Claude Code 不是 React 專用工具**：它是在你的專案目錄裡讀檔、改檔、跑指令的 agent；React 的特性靠你寫進 `CLAUDE.md`、權限與 hooks 來告訴它。
- **開發循環**：你下指令 → Claude 改檔 → hook 自動 lint → dev server 熱更新 → 跑測試與瀏覽器驗證 → 把關 → 你審查 diff（第 1 節）。
- **讓它「看到」結果是關鍵**：只改程式碼不夠，要讓 Claude 能跑測試、看到錯誤訊息，必要時看到畫面。畫面可以用 **Chrome 整合**或 **Playwright MCP**（第 4 節）。
- **要強制的規則用 hooks 與 deny，不要只靠 `CLAUDE.md`**：`CLAUDE.md` 是放進 context 的文字，Claude 會盡量遵守但不保證（【官方】，見 [Claude-Context](Claude-Context.md)）。
- **大規模改寫**（例如元件遷移）可用 `/batch` 搭配 worktree；官方範例之一就是 `/batch migrate src/ from Solid to React`。

---

## 1. 整體流程：Claude 在本機 React 開發循環中的位置

![圖：Claude Code 在本機 React 開發循環中的位置，七個步驟與誰負責](figures/claude-code-react-loop.svg)

| 步驟 | 誰做 | 用到的功能 | 依據 |
|---|---|---|---|
| 1 下指令 | 你 | 大改動先用 `plan` 權限模式探索與規劃（`Shift+Tab` 切換） | 【官方】 |
| 2 改檔 | Claude | Edit／Write；權限常用 `acceptEdits`，事後審 diff | 【官方】 |
| 3 自動檢查 | hook | `PostToolUse` 在 Edit／Write 後跑 lint 或 format | 【官方】範例 |
| 4 熱更新 | dev server | 建議你在**另一個終端機**跑 `npm run dev`，讓 Claude 專注改檔與驗證 | 【建議】 |
| 5 驗證 | Claude | 跑測試；用 Chrome 整合或 Playwright MCP 看畫面 | 【官方】功能／【建議】用法 |
| 6 把關 | hook | `Stop` hook 在測試沒過時 block，要求 Claude 繼續修 | 【官方】範例 |
| 7 審查 | 你 | 看 diff、用 `/review`，再 commit | 【官方】 |

---

## 2. 專案準備：CLAUDE.md、權限與設定檔

### 2.1 設定檔放哪裡

![圖：React 專案裡 Claude Code 相關檔案放哪裡，哪些可 commit、哪些是個人的](figures/claude-code-react-files.svg)

【官方】hooks 與權限可放在 `~/.claude/settings.json`（個人，所有專案）、`.claude/settings.json`（專案，可 commit 共享）、`.claude/settings.local.json`（專案，個人不共享）。MCP 的 `project` scope 寫入專案根目錄的 `.mcp.json`，可 commit 共享。

### 2.2 CLAUDE.md：把 React 專案慣例寫進去

【官方】`CLAUDE.md` 會在每次請求時放進 context；它是文字指示，Claude 會盡量遵守但不保證（詳見 [Claude-Context](Claude-Context.md)）。下面是 React 專案的**範例**（【建議】，內容請依你的專案調整）：

```markdown
# 專案慣例（範例）

## 指令
- 開發：npm run dev（我會自己開著，不要重複啟動）
- 測試：npm test；單一檔案：npm test -- <檔名>
- 檢查：npm run lint、npm run typecheck

## 規範
- 元件放在 src/components，一個元件一個資料夾
- 使用 function component 與 hooks，不寫 class component
- 新元件要附測試（React Testing Library）

## 不要做
- 不要改 package.json 的依賴版本，除非我明說
- 不要讀取或修改 .env*
```

### 2.3 權限：允許常用指令、擋住敏感檔案

【官方】權限規則寫在 `settings.json` 的 `permissions.allow` 與 `permissions.deny`，支援 glob；`deny` 與 `allow` 同時命中時，**deny 絕對優先**（見 [Agentic-Engineering](Agentic-Engineering.md)）。下面是依官方整理的範例寫法，套到 React 專案（【建議】）：

```json
{
  "permissions": {
    "deny": ["Read(.env*)", "Bash(rm -rf*)", "Bash(git push --force*)"],
    "allow": ["Bash(npm run *)", "Bash(npm test*)", "Edit(src/**)"]
  }
}
```

- 我故意**沒有**把 `npm install` 放進 `allow`：安裝套件會執行第三方腳本，建議每次由你確認（【建議】）。
- 各 pattern 的比對細節我沒有逐一驗證；寫好後請實際觸發一次確認有擋到。
- 權限模式：`default` 只自動放行唯讀；`acceptEdits` 自動放行檔案編輯；`plan` 只讀不寫；`auto`、`dontAsk`、`bypassPermissions` 見 [Claude-Code-CLI 第 16 節](Claude-Code-CLI.md)（【官方】）。

---

## 3. 讓 Claude 看見結果：dev server 與測試

- **dev server**（【建議】）：在另一個終端機自己執行 `npm run dev`，Claude 改檔後熱更新會自動套用。這樣不必讓 Claude 管理長時間執行的程序；也避免兩邊各開一個 server 造成 port 衝突。
- **測試**（【建議】）：讓 Claude 在改完後自己跑 `npm test`，並把失敗訊息當作下一步的依據。React 專案常見的測試組合是 Vitest 或 Jest 加 React Testing Library；本文不涉及這些工具的官方文件，請參考各自的說明。
- **把「通過」寫成可驗證的條件**：【官方】`/goal` 的有效條件要有「單一可量測終態」，例如 `npm test exits 0`；官方範例也有 `migrate all API call sites to v2 and npm run build exits 0` 與 `all linting errors fixed, or stop after 20 turns`。React 的對應寫法（【建議】）：

```text
/goal all tests in src/components pass and npm run lint exits 0, or stop after 15 turns
```

- **型別檢查**（【建議】）：若是 TypeScript 專案，把 `npm run typecheck` 也放進驗證條件，React 元件的 props 型別錯誤常在這一步才會露出。

---

## 4. 瀏覽器驗證：Chrome 整合與 Playwright MCP

測試通過不等於畫面對。要讓 Claude 看到實際渲染，有兩條路：

### 4.1 Chrome 整合：Claude 怎麼直接看到瀏覽器的輸出

【官方】來源是 [Use Claude Code with Chrome](https://code.claude.com/docs/en/chrome)（我於 2026-11-18 取得該頁全文，下列內容都取自它）。

![圖：Claude Code 如何直接檢查 Chrome 的輸出，從 prompt 到讀回 console 與 DOM](figures/claude-code-react-chrome.svg)

**機制**：Claude Code 透過 **Claude in Chrome 瀏覽器擴充功能**連到你的 Chrome。Claude 為瀏覽器任務開**新分頁**、共用你的登入狀態；動作在**可見的 Chrome 視窗**即時進行；遇到登入頁或 CAPTCHA 會暫停，請你手動處理。擴充功能把 Claude 開的分頁收進一個與 session 綁定的分頁群組。

**它能看到什麼**（官方列出的能力）：
- **即時除錯**：直接讀 **console 錯誤與 DOM 狀態**，再去修造成錯誤的程式。
- **設計驗證**：照 Figma 稿做出介面後，開在瀏覽器裡確認是否一致。
- **網頁測試**：表單驗證、視覺回歸、使用者流程。
- **截圖存檔**與**錄成 GIF**；也能上傳檔案、擷取頁面資料（錄影會拍下畫面上所有內容，含已登入頁面的帳號資訊，分享前要檢查）。
- 完整的瀏覽器工具清單：在 Claude Code 裡執行 `/mcp`，選 `claude-in-chrome`，再選 **View tools**。
- ⚠️ **Network 請求**：官方頁面沒有列出這項；有第三方文章說可以，我沒有確認。

**怎麼用**（官方範例，React 專案請把網址換成你的 dev server，例如 `localhost:3000`）：

```text
I just updated the login form validation. Can you open localhost:3000,
try submitting the form with invalid data, and check if the error
messages appear correctly?
```

```text
Open the dashboard page and check the console for any errors when
the page loads.
```

- 官方提醒：**告訴 Claude 要找哪種訊息，不要要求「全部 console 輸出」**，因為 log 可能很冗長（Claude 讀 console 訊息後可以依樣式或錯誤類型過濾）。
- 啟動：`claude --chrome`（首次會出現一次性說明對話框）；之後可用 `/chrome` 檢查連線（正常時顯示 `Status: Enabled`、`Extension: Installed`）、管理權限、重新連線、選擇瀏覽器；`Enabled by default` 可以不帶旗標，但**會讓瀏覽器工具與說明常駐、增加 context 用量**，所以需要時再開比較省。
- 【建議】React 專案：先在另一個終端機啟動 dev server，再請 Claude 檢查頁面載入時 console 有沒有錯誤；改完元件後請它重新載入並確認。

**需求與限制**（官方）：
- 瀏覽器：Chrome 與 Edge；Claude Code 也會偵測並設定 Brave、Arc、Vivaldi、Opera 等 Chromium 系瀏覽器。**不支援 WSL**。
- Claude in Chrome 擴充功能 **1.0.36 以上**，以及直接的 Anthropic 方案（Pro、Max、Ultra、Team、Enterprise）。
- 必須用 `/login` 登入；用 API key 或 `claude setup-token` 的長效 token 時，**即使帶了 `--chrome`，整合仍保持關閉**。**不能**透過 Amazon Bedrock、Google Cloud、Microsoft Foundry 等第三方供應商使用。
- 啟用 Zero Data Retention 的組織無法在 Claude Code 使用；啟用 HIPAA 的 Enterprise 組織預設關閉。
- 擴充功能與 Claude Code 要登入**同一個 claude.ai 帳號與組織**，否則會出現 `Browser extension is not connected`。
- **專案的 `.claude/settings.json` 不能替你開啟 Chrome 整合**（會被忽略並顯示警告），因為你 checkout 的 repo 不該有權限連到你的瀏覽器；要用請自己執行 `/chrome` 或加 `--chrome`。

**常見問題**（官方）：頁面上跳出 `alert`／`confirm`／`prompt` 對話框會擋住瀏覽器指令，先手動關掉再叫 Claude 繼續；長時間閒置後連線可能中斷，執行 `/chrome` 選 `Reconnect extension`；第一次啟用後若偵測不到擴充功能，重啟 Chrome。

### 4.2 Playwright MCP

【官方】MCP server 的加法：`claude mcp add [options] <name> -- <command> [args...]`；`--scope project` 會寫入 `.mcp.json` 供團隊共享（見 [Claude-Code-CLI 第 18 節](Claude-Code-CLI.md)）。Playwright 的 MCP server 套件名稱與安裝指令，搜尋結果（含 Playwright 官方文件）一致列出：

```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

- 搜尋結果提到：需要 Node.js 18 以上；第一次使用時 Playwright 會下載瀏覽器；團隊共用或 CI 時建議**固定版本**，因為 `@latest` 可能拉到 beta 造成不穩定。
- 第三方指南提到 `--headless`（不開視窗）與 `--browser` 等選項，**我沒有查官方旗標清單**。
- 對 React：典型做法是先啟動 dev server，再讓瀏覽器連到本機網址（【建議】）。搜尋結果沒有針對 React 的官方說明。

### 4.3 怎麼選（【建議】）

| 面向 | Chrome 整合 | Playwright MCP | 只靠測試 |
|---|---|---|---|
| 設定 | 裝擴充功能、用 `/login`、需直接的 Anthropic 方案 | `claude mcp add` 一行 | 專案本來就有 |
| 適合 | 在你自己的 Chrome 裡驗證、除錯（共用登入狀態、可見視窗） | 可寫進 `.mcp.json` 讓團隊共用、較容易重現 | 邏輯、元件行為 |
| 限制 | 依賴 `/login` 與擴充功能；不支援 WSL；不能用 API key | 要下載瀏覽器；版本需固定 | 看不到實際畫面與樣式 |

---

## 5. Hooks：自動 lint 與測試把關

【官方】hooks 的設定結構、觸發時機與位置見 [Claude-Code-CLI 第 17 節](Claude-Code-CLI.md)。官方整理的兩個範例，直接適合 React 專案：

**編輯後自動 lint（`PostToolUse`）**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "npm run lint --fix" }]
      }
    ]
  }
}
```

**測試沒過就不讓 Claude 結束（`Stop`）**

```bash
#!/bin/bash
# 若測試失敗，回傳 block 讓 Claude 繼續修復
npm test > /tmp/test-output.txt 2>&1
if [ $? -ne 0 ]; then
  RESULT=$(cat /tmp/test-output.txt)
  echo "{\"decision\":\"block\",\"reason\":\"測試失敗，請修復後再停止\",\"additionalContext\":\"$RESULT\"}"
fi
exit 0
```

React 專案的注意事項（【建議】）：

- **確認 `npm test` 是一次性執行，不是 watch 模式**，否則 `Stop` hook 會卡住等不到結束。
- 每次編輯都跑整個 lint 可能很慢；hook 有 `async` 欄位可以在背景執行、`timeout` 可設逾時（【官方】欄位說明取自 v2.1.316 設定 schema，各欄位適用於哪些 handler 類型尚未逐一驗證）。
- 強制規則（例如不准改 lockfile）用 `PreToolUse` hook 或 `permissions.deny`，不要只寫在 `CLAUDE.md`。

---

## 6. 平行開發與大規模改動：worktree、/batch、審查

- **Worktree**（【官方】）：`claude --worktree <名稱>` 在 `.claude/worktrees/<名稱>/` 建立隔離的工作目錄與分支；用來同時開發兩個功能而不互踩。
  - `.env` 等 gitignore 的檔案不會自動進 worktree，要用 repo 根目錄的 `.worktreeinclude` 指定複製（語法同 `.gitignore`）。
  - **React 專案的額外注意**（【建議】）：worktree 是乾淨的 checkout，`node_modules` 不會跟著來，每個 worktree 都要自己安裝依賴；同時開多個 dev server 時要用不同的 port。
- **`/batch`**（【官方】）：把大型改動拆成 5 到 30 個獨立單元，每個在隔離的 worktree 由背景 subagent 執行、跑測試、開 PR；適合大規模、機械性的改動。官方範例有 `migrate src/ from Solid to React`、`add JSDoc comments to every exported function in src/api/`。React 的對應用途（【建議】）：把 class component 改成 function component、統一換成新的 API client。需要 git repository，且你要先確認它拆出來的計畫。
- **審查**（【官方】）：`/review` 與 `/code-review`；多 Agent 審查的做法見 [Claude-Agent](Claude-Agent.md)。

---

## 7. CI 與非互動模式

【官方】`claude -p` 是非互動（print）模式，搭配旗標限制範圍。官方的 CI 範例：

```bash
claude -p "run tests and report failures" \
  --max-turns 8 \
  --max-budget-usd 2 \
  --allowedTools "Read,Bash(npm test)" \
  --output-format json
```

- `--permission-mode dontAsk` 會拒絕所有不在 `permissions.allow` 內的工具呼叫（適合預先定義白名單的 CI）。
- `--bare` 會跳過 hooks、auto-memory、`CLAUDE.md` 自動載入等；需要 context 時要明確傳入。

---

## 8. 依需求選做法

![圖：依需求選做法：畫面、邏輯、lint、大規模改寫與 CI](figures/claude-code-react-choose.svg)

> 這是我依各功能定位做的歸納，不是官方建議。

---

## 9. 常見陷阱（【建議】）

1. **只看測試、不看畫面**：樣式與版面問題測試抓不到，重要頁面要用第 4 節的方式看一次。
2. **把規則只寫在 `CLAUDE.md`**：它不保證被遵守；會出事的規則（碰 `.env`、改依賴）要用 deny 或 hook 擋。
3. **讓 Claude 隨意 `npm install`**：新增依賴會改 `package.json` 與 lockfile，建議每次由你確認。
4. **一次要求太大**：一次一個元件或一個功能；大改動先用 `plan` 模式看計畫。
5. **不看 diff**：`acceptEdits` 是「事後審查」，不是「不用審查」。
6. **在 `.mcp.json` 用 `@latest`**：團隊共用時固定版本，避免不同人拿到不同行為。

---

## 10. 驗證說明與限制

- 資料日期 2026-11-18。**我沒有實際在 React 專案上跑過本文的流程**，也沒有執行任何範例指令。
- **【官方】** 的內容取自本庫已整理的 Claude Code 文件（來源為 `code.claude.com` 的官方文件，包括 hooks、MCP、worktree、`/batch`、`/goal`、權限與非互動模式），並與本庫對應章節一致；第 4.1 節的 Chrome 整合取自官方頁面[Use Claude Code with Chrome](https://code.claude.com/docs/en/chrome)，我於 2026-11-18 取得了全文；**但我沒有實際安裝擴充功能或執行過 `claude --chrome`**，所以沒有親眼驗證它能讀到什麼。其餘各節我沒有開啟官方頁面，內容取自本庫已整理的資料。
- **Playwright MCP** 的指令取自搜尋結果（含 Playwright 官方文件），不是 Claude Code 文件；各旗標請以 Playwright 官方說明為準。
- **【建議】** 都是我的歸納，沒有官方依據；React、Vite、Next.js、Vitest、Jest 與 React Testing Library 各自的用法，本文沒有查證。
- Claude Code 更新很快，功能名稱、旗標與預設值以官方文件為準；本庫的 [Claude-Code-CLI](Claude-Code-CLI.md) 標有它整理時的版本資訊。

---

## 11. 官方來源

- Claude Code 的 Chrome 整合（第 4.1 節的依據）：<https://code.claude.com/docs/en/chrome>
- Claude Code 的 MCP：<https://code.claude.com/docs/en/mcp.md>
- Claude Code 的 memory（CLAUDE.md）：<https://code.claude.com/docs/en/memory.md>
- Playwright MCP 入門：<https://playwright.dev/python/docs/getting-started-mcp>
- 本庫對應文件：[Claude-Code-CLI](Claude-Code-CLI.md)、[Claude-Context](Claude-Context.md)、[Agentic-Engineering](Agentic-Engineering.md)、[Claude-Agent](Claude-Agent.md)
