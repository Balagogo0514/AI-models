# Claude 如何結合 React 本機開發：Claude Code 與 Codex

> 資料日期：2026-11-18  
> 範圍：在本機用 Claude Code 開發 React 專案（Vite、Next.js 等）的工作流程：專案設定、權限、dev server 與測試、瀏覽器驗證、hooks、平行開發與 CI；第 10 節補上用 Codex 做同樣的事。  
> 讀法：文中分兩種內容——**【官方】** 表示功能與設定語法取自本庫已整理的官方資料（[Claude-Code-CLI](Claude-Code-CLI.md)、[Claude-Context](Claude-Context.md)、[Agentic-Engineering](Agentic-Engineering.md)），或官方 Chrome 整合頁面；**【建議】** 是我依這些功能整理的 React 開發做法，**不是官方指定流程**。React 專屬的部分（元件目錄、測試工具、dev server 的用法）沒有官方依據，都屬於【建議】。  
> ⚠️ **我沒有實際在 React 專案上跑過本文的流程**；範例是依文件寫的，請在你的專案上先小範圍試用。

## 先看結論

- **Claude Code 不是 React 專用工具**：它是在你的專案目錄裡讀檔、改檔、跑指令的 agent；React 的特性靠你寫進 `CLAUDE.md`、權限與 hooks 來告訴它。
- **開發循環**：你下指令 → Claude 改檔 → hook 自動 lint → dev server 熱更新 → 跑測試與瀏覽器驗證 → 把關 → 你審查 diff（第 1 節）。
- **範例流程**：用 `localhost` 跑 React，再讓 Claude Code 用 Chrome 整合直接檢查 console 與畫面，見第 4.4 節。
- **讓它「看到」結果是關鍵**：只改程式碼不夠，要讓 Claude 能跑測試、看到錯誤訊息，必要時看到畫面。畫面可以用 **Chrome 整合**或 **Playwright MCP**（第 4 節）。
- **要強制的規則用 hooks 與 deny，不要只靠 `CLAUDE.md`**：`CLAUDE.md` 是放進 context 的文字，Claude 會盡量遵守但不保證（【官方】，見 [Claude-Context](Claude-Context.md)）。
- **用 Codex 也行**：`AGENTS.md` 對應 `CLAUDE.md`、sandbox 加 approval 對應權限、瀏覽器驗證用 Browser plugin 或 Playwright MCP，見第 10 節；官方頁面我打不開，該節多處只來自搜尋摘要。
- **大規模改寫**（例如元件遷移）可用 `/batch` 搭配 worktree；官方範例之一就是 `/batch migrate src/ from Solid to React`。

![圖：文件導覽，五個區塊依序是準備、看見結果、把關與規模、用 Codex 做同樣的事、查閱](figures/claude-react-map.svg)

---

## 1. 整體流程：Claude 在本機 React 開發循環中的位置

![圖：Claude Code 在本機 React 開發循環中的位置，七個步驟與誰負責](figures/claude-react-loop.svg)

| 步驟 | 誰做 | 用到的功能 | 依據 |
|---|---|---|---|
| 1 下指令 | 你 | 大改動先用 `plan` 權限模式探索與規劃（`Shift+Tab` 切換） | 【官方】 |
| 2 改檔 | Claude | Edit／Write；權限常用 `acceptEdits`，事後審 diff | 【官方】 |
| 3 自動檢查 | hook | `PostToolUse` 在 Edit／Write 後跑 lint 或 format | 【官方】範例 |
| 4 熱更新 | dev server | 建議你在**另一個終端機**跑 `yarn start`，讓 Claude 專注改檔與驗證 | 【建議】 |
| 5 驗證 | Claude | 跑測試；用 Chrome 整合或 Playwright MCP 看畫面 | 【官方】功能／【建議】用法 |
| 6 把關 | hook | `Stop` hook 在測試沒過時 block，要求 Claude 繼續修 | 【官方】範例 |
| 7 審查 | 你 | 看 diff、用 `/review`，再 commit | 【官方】 |

---

## 2. 專案準備：CLAUDE.md、權限與設定檔

### 2.1 設定檔放哪裡

![圖：React 專案裡 Claude Code 相關檔案放哪裡，哪些可 commit、哪些是個人的](figures/claude-react-files.svg)

【官方】hooks 與權限可放在 `~/.claude/settings.json`（個人，所有專案）、`.claude/settings.json`（專案，可 commit 共享）、`.claude/settings.local.json`（專案，個人不共享）。MCP 的 `project` scope 寫入專案根目錄的 `.mcp.json`，可 commit 共享。

### 2.2 CLAUDE.md：把 React 專案慣例寫進去

> 本文的指令用 yarn：你們的 GUI 是用 `yarn start` 啟動。`test`、`lint`、`typecheck` 等 script 名稱只是範例，**以你專案 `package.json` 的 `scripts` 為準**。

【官方】`CLAUDE.md` 會在每次請求時放進 context；它是文字指示，Claude 會盡量遵守但不保證（詳見 [Claude-Context](Claude-Context.md)）。下面是 React 專案的**範例**（【建議】，內容請依你的專案調整）：

```markdown
# 專案慣例（範例）

## 指令
- 開發：yarn start（我會自己開著，不要重複啟動）
- 測試：yarn test；單一檔案：yarn test <檔名>
- 檢查：yarn lint、yarn typecheck

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
    "allow": ["Bash(yarn start*)", "Bash(yarn test*)", "Bash(yarn lint*)", "Edit(src/**)"]
  }
}
```

![圖：Claude Code 權限流程，先看 deny、再看 allow，都沒命中就依權限模式](figures/claude-react-permissions.svg)

- 我故意**沒有**把 `yarn add`、`yarn install` 放進 `allow`：安裝套件會執行第三方腳本，建議每次由你確認（【建議】）。
- 各 pattern 的比對細節我沒有逐一驗證；寫好後請實際觸發一次確認有擋到。
- 權限模式：`default` 只自動放行唯讀；`acceptEdits` 自動放行檔案編輯；`plan` 只讀不寫；`auto`、`dontAsk`、`bypassPermissions` 見 [Claude-Code-CLI 第 16 節](Claude-Code-CLI.md)（【官方】）。

---

## 3. 讓 Claude 看見結果：dev server 與測試

![圖：讓 Claude 看見結果的四種回饋訊號：測試、lint 與型別、瀏覽器、可驗證的完成條件](figures/claude-react-signals.svg)

- **dev server**（【建議】）：在另一個終端機自己執行 `yarn start`，Claude 改檔後熱更新會自動套用。這樣不必讓 Claude 管理長時間執行的程序；也避免兩邊各開一個 server 造成 port 衝突。
- **測試**（【建議】）：讓 Claude 在改完後自己跑 `yarn test`，並把失敗訊息當作下一步的依據。React 專案常見的測試組合是 Vitest 或 Jest 加 React Testing Library；本文不涉及這些工具的官方文件，請參考各自的說明。
- **把「通過」寫成可驗證的條件**：【官方】`/goal` 的有效條件要有「單一可量測終態」，例如 `npm test exits 0`（官方原文；你們用 yarn 就寫 `yarn test exits 0`）；官方範例也有 `migrate all API call sites to v2 and npm run build exits 0` 與 `all linting errors fixed, or stop after 20 turns`。React 的對應寫法（【建議】）：

```text
/goal all tests in src/components pass and yarn lint exits 0, or stop after 15 turns
```

- **型別檢查**（【建議】）：若是 TypeScript 專案，把 `yarn typecheck` 也放進驗證條件，React 元件的 props 型別錯誤常在這一步才會露出。

---

## 4. 瀏覽器驗證：Chrome 整合與 Playwright MCP

測試通過不等於畫面對。要讓 Claude 看到實際渲染，有兩條路：

### 4.1 Chrome 整合：Claude 怎麼直接看到瀏覽器的輸出

【官方】來源是 [Use Claude Code with Chrome](https://code.claude.com/docs/en/chrome)（我於 2026-11-18 取得該頁全文，下列內容都取自它）。

![圖：Claude Code 如何直接檢查 Chrome 的輸出，從 prompt 到讀回 console 與 DOM](figures/claude-react-chrome.svg)

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

### 4.4 完整範例流程：用 localhost 啟動 React，讓 Claude Code 直接檢查結果

情境：你在本機用 `localhost` 跑 React，想讓 Claude Code 直接開瀏覽器檢查。這裡用官方範例的情境「登入表單的驗證」走一遍。**以下是依官方文件與範例組成的流程，我沒有實際跑過**；指令與提示詞照官方寫法，檔名、網址與埠號是示意，請換成你的專案。

![圖：localhost 範例流程，你、dev server、Claude Code 與 Chrome 的互動順序](figures/claude-react-localhost-flow.svg)

**事前條件**（第 4.1 節）：已安裝 Claude in Chrome 擴充功能（1.0.36 以上）、用 `/login` 登入 Claude Code、不是透過 Bedrock 等第三方供應商。

**步驟 1：終端機 A 啟動 dev server**（【建議】）

```bash
yarn start
```

記下終端機印出的網址（官方範例用 `localhost:3000`，**實際埠號以你專案的輸出為準**）。讓這個終端機一直開著，Claude 改檔後由 dev server 熱更新（是否熱更新依專案設定）。

**步驟 2：終端機 B 在專案目錄啟動 Claude Code**（【官方】）

```bash
cd your-react-app
claude --chrome
```

首次會出現一次性對話框，按 Enter 繼續。接著輸入 `/chrome`，**狀態面板顯示 `Status: Enabled` 與 `Extension: Installed` 就代表整合正常**。

**步驟 3：請 Claude 檢查目前的畫面**（【官方】範例，換成你的登入頁網址）

```text
Open localhost:3000/login, submit the form with an empty email and with an
invalid email, and check if the error messages appear correctly. Also check
the console for any errors.
```

Claude 會開新分頁、操作表單，並回報它觀察到的結果（官方原文：「Claude navigates to your local server, interacts with the form, and reports what it observes」）。如果它要做的瀏覽器動作需要許可，會跳出以 `Claude in Chrome wants to` 開頭的對話框；可以只允許這次，或允許該網站在本次 session 的所有動作。**回報的內容會因專案而異，我沒有範例輸出可以給你。**

**步驟 4：發現問題就請它修，並重新驗證**（【建議】）

```text
Based on what you just observed, fix the validation in
src/components/LoginForm.tsx, then reload the page and verify it again.
```

這時 Claude 會編輯檔案（需要編輯權限，常用 `acceptEdits`，第 2.3 節）；dev server 熱更新後，它再請瀏覽器重新載入並確認。

**步驟 5：留下證據**（【官方】範例）

```text
Take a screenshot of the login page and save it to disk
```

Claude 會把圖存到磁碟並回報路徑。也可以請它錄成 GIF，但**錄影會拍下畫面上的所有內容，分享前要先檢查**。

**步驟 6：收尾**（【建議】）：跑 `yarn test` 與 `yarn lint`，用 `/review` 看過 diff 再 commit（第 1、5、6 節）。

**補充**：
- 【建議】把驗證方式寫進 `CLAUDE.md`，每次都不必重講，例如：「瀏覽器驗證：用 Chrome 整合開 `http://localhost:3000`，只看 console 的 error 與 warning，不要貼完整 log」。這呼應官方的提醒：告訴 Claude 要找哪種訊息，不要要求全部 console 輸出。
- 【推論】**`localhost` 是從你的 Chrome 所在的那台機器來解析的**。如果 Claude Code 跑在別台機器（例如遠端），而 dev server 也跑在遠端，你的 Chrome 打不開那個 `localhost`；要讓 dev server 與 Chrome 在同一台機器，或自行處理連線轉發。官方頁面沒有針對這個情況說明，我沒有驗證。
- 官方說 `Enabled by default` 會讓瀏覽器工具常駐、增加 context 用量，不常用就用 `--chrome` 臨時開。

### 4.5 檢查不到結果時

![圖：Chrome 整合檢查不到結果時的六種症狀與處理](figures/claude-react-chrome-troubleshoot.svg)

前五項取自官方頁面的疑難排解與錯誤訊息表（【官方】），最後一項是我加的（【建議】）。官方還提醒：如果你的 Claude 帳號屬於多個組織，擴充功能必須登入**與 Claude Code 相同的組織**，用 `/status` 的 `Organization` 欄位確認；若登出擴充功能，會失去存在擴充功能裡的捷徑與排程任務，所以先試其他修法。

---

## 5. Hooks：自動 lint 與測試把關

【官方】hooks 的設定結構、觸發時機與位置見 [Claude-Code-CLI 第 17 節](Claude-Code-CLI.md)。官方整理的兩個範例，直接適合 React 專案（官方範例寫的是 `npm`，這裡換成 yarn）：

![圖：兩個 hook 的時機：編輯後 PostToolUse 跑 lint，結束前 Stop hook 跑測試，沒過就 block 讓 Claude 繼續修](figures/claude-react-hooks.svg)

**編輯後自動 lint（`PostToolUse`）**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "yarn lint --fix" }]
      }
    ]
  }
}
```

**測試沒過就不讓 Claude 結束（`Stop`）**

```bash
#!/bin/bash
# 若測試失敗，回傳 block 讓 Claude 繼續修復
yarn test > /tmp/test-output.txt 2>&1
if [ $? -ne 0 ]; then
  RESULT=$(cat /tmp/test-output.txt)
  echo "{\"decision\":\"block\",\"reason\":\"測試失敗，請修復後再停止\",\"additionalContext\":\"$RESULT\"}"
fi
exit 0
```

React 專案的注意事項（【建議】）：

- **確認 `yarn test` 是一次性執行，不是 watch 模式**，否則 `Stop` hook 會卡住等不到結束。
- 每次編輯都跑整個 lint 可能很慢；hook 有 `async` 欄位可以在背景執行、`timeout` 可設逾時（【官方】欄位說明取自 v2.1.316 設定 schema，各欄位適用於哪些 handler 類型尚未逐一驗證）。
- 強制規則（例如不准改 lockfile）用 `PreToolUse` hook 或 `permissions.deny`，不要只寫在 `CLAUDE.md`。

---

## 6. 平行開發與大規模改動：worktree、/batch、審查

![圖：主 checkout 與兩個 worktree，/batch 在 worktree 中平行執行，Codex 要自己建 worktree](figures/claude-react-worktree.svg)

- **Worktree**（【官方】）：`claude --worktree <名稱>` 在 `.claude/worktrees/<名稱>/` 建立隔離的工作目錄與分支；用來同時開發兩個功能而不互踩。
  - `.env` 等 gitignore 的檔案不會自動進 worktree，要用 repo 根目錄的 `.worktreeinclude` 指定複製（語法同 `.gitignore`）。
  - **React 專案的額外注意**（【建議】）：worktree 是乾淨的 checkout，`node_modules` 不會跟著來，每個 worktree 都要自己安裝依賴；同時開多個 dev server 時要用不同的 port。
- **`/batch`**（【官方】）：把大型改動拆成 5 到 30 個獨立單元，每個在隔離的 worktree 由背景 subagent 執行、跑測試、開 PR；適合大規模、機械性的改動。官方範例有 `migrate src/ from Solid to React`、`add JSDoc comments to every exported function in src/api/`。React 的對應用途（【建議】）：把 class component 改成 function component、統一換成新的 API client。需要 git repository，且你要先確認它拆出來的計畫。
- **審查**（【官方】）：`/review` 與 `/code-review`；多 Agent 審查的做法見 [Claude-Agent](Claude-Agent.md)。

---

## 7. CI 與非互動模式

![圖：CI 中 claude -p 與 codex exec 並排：限制範圍、輸出、由 CI 檢查退出碼](figures/claude-react-ci.svg)

下文先說 Claude Code，Codex 的對應做法見第 10.5 節。

【官方】`claude -p` 是非互動（print）模式，搭配旗標限制範圍。官方的 CI 範例（官方寫 `Bash(npm test)`，這裡換成 yarn）：

```bash
claude -p "run tests and report failures" \
  --max-turns 8 \
  --max-budget-usd 2 \
  --allowedTools "Read,Bash(yarn test)" \
  --output-format json
```

- `--permission-mode dontAsk` 會拒絕所有不在 `permissions.allow` 內的工具呼叫（適合預先定義白名單的 CI）。
- `--bare` 會跳過 hooks、auto-memory、`CLAUDE.md` 自動載入等；需要 context 時要明確傳入。

---

## 8. 依需求選做法

![圖：依需求選做法：畫面、邏輯、lint、大規模改寫與 CI](figures/claude-react-choose.svg)

> 這是我依各功能定位做的歸納，不是官方建議。

---

## 9. 常見陷阱（【建議】）

![圖：六個常見陷阱與對策](figures/claude-react-pitfalls.svg)

1. **只看測試、不看畫面**：樣式與版面問題測試抓不到，重要頁面要用第 4 節的方式看一次。
2. **把規則只寫在 `CLAUDE.md`**：它不保證被遵守；會出事的規則（碰 `.env`、改依賴）要用 deny 或 hook 擋。
3. **讓 Claude 隨意 `yarn add`／`yarn install`**：新增依賴會改 `package.json` 與 lockfile，建議每次由你確認。
4. **一次要求太大**：一次一個元件或一個功能；大改動先用 `plan` 模式看計畫。
5. **不看 diff**：`acceptEdits` 是「事後審查」，不是「不用審查」。
6. **在 `.mcp.json` 用 `@latest`**：團隊共用時固定版本，避免不同人拿到不同行為。

---

## 10. 使用 Codex：同樣的 React 開發循環

前面的流程不是 Claude Code 專屬：OpenAI 的 Codex 也能在本機專案目錄讀檔、改檔、跑指令，做法的骨架相同（寫專案慣例 → 設權限 → 讓它看見結果 → 審查）。這一節說明對應關係，並用 `localhost` 跑 React 走一遍範例流程。

**依據與標記**（請先讀）：
- 【官方】：取自本庫已整理的 Codex 文件（[CodeX-CLI](CodeX-CLI.md)、[CodeX-Agent](CodeX-Agent.md)）。
- 【官方\*】：OpenAI 官方頁面（網址見第 12 節）的內容，但**我在這個環境打不開 `developers.openai.com`**（網路政策擋住），所以只看到搜尋結果對該頁的摘要，**沒有讀到原文**；細節請以官方頁面為準。
- 【建議】、【推論】：與前面各節同義，是我的歸納或推論，沒有官方依據。
- ⚠️ **本節的流程我沒有實際跑過**，也沒有 Codex 的範例輸出可以給你。

### 10.1 與 Claude Code 的對照

![圖：React 開發循環中，Claude Code 與 Codex 的功能對照，綠色表示可對應，橘色表示未驗證或沒有對應](figures/claude-react-codex-map.svg)

幾個要注意的差異：

- **專案慣例檔是 `AGENTS.md`**。【官方\*】Codex 在開始工作前讀 `AGENTS.md`：家目錄的 `~/.codex/AGENTS.md` 與專案根目錄、子目錄的檔案會合併，**離工作目錄越近的優先**；子目錄可放 `AGENTS.override.md` 蓋過上層規則；載入量有上限（`project_doc_max_bytes`）；官方建議保持簡短。【官方】`/init` 會產生 `AGENTS.md` 的範本。
- **權限是 sandbox 與 approval 兩個維度**，不是 `allow`／`deny` 清單。【官方】`-s` 選 `read-only`、`workspace-write`、`danger-full-access`；`-a` 選 `untrusted`、`on-request`、`never`；互動中用 `/permissions` 調整。本庫整理的資料裡**沒有**對應 `permissions.deny` 的逐指令規則；Codex 是否另有規則檔，我沒有查證。
- **自動把關**：【官方】Codex 有 lifecycle hooks（`/hooks`），也有跳過 hook 信任的旗標；但事件名稱與設定寫法我沒查證，所以本文不給 hook 設定範例（見 10.5）。
- **大規模平行改動**：本庫的 [CodeX-Agent](CodeX-Agent.md) 整理的結論是，Codex 沒有已驗證的 per-subagent worktree 機制，**要自己建 `git worktree`** 再用 `-C` 指向它；也沒有已驗證的 `/batch` 對應功能。

### 10.2 專案準備：AGENTS.md、sandbox 與 approval

`AGENTS.md` 的內容可以直接沿用第 2.2 節的 `CLAUDE.md` 範例（【建議】，依你的專案調整）：

```markdown
# 專案慣例（範例）

## 指令
- 開發：yarn start（我會自己開著，不要重複啟動）
- 測試：yarn test；單一檔案：yarn test <檔名>
- 檢查：yarn lint、yarn typecheck
- 完成前一定要跑 yarn test 與 yarn lint，結果貼在回覆裡

## 規範
- 元件放在 src/components，一個元件一個資料夾
- 使用 function component 與 hooks，不寫 class component
- 新元件要附測試（React Testing Library）

## 不要做
- 不要改 package.json 的依賴版本，除非我明說
- 不要讀取或修改 .env*
```

啟動方式（【官方】本庫整理的「一般本機開發」組合）：

```bash
codex -C . -s workspace-write -a on-request
```

![圖：Codex 權限的兩個維度 sandbox 與 approval，以及本庫整理的常用組合](figures/claude-react-codex-permissions.svg)

想固定下來，可寫進 `config.toml`（【官方】本庫範例，欄位名稱以你版本的 `config-reference` 為準）：

```toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

- 【建議】**不要為了讓指令跑起來就用 `danger-full-access` 或 `--dangerously-bypass-approvals-and-sandbox`**；本庫把後者標為「極危險」。指令被擋時，先用 `/permissions` 看是哪一項，再決定放行什麼。
- **我沒有查證**：在 `workspace-write` 下 `yarn install`、下載套件或連到本機埠是否被擋。若被擋，這會影響第 10.4 節的流程。
- **敏感檔案**：Claude Code 可以用 `deny` 擋 `.env*`；Codex 這邊我沒有查到等價的規則。`AGENTS.md` 裡寫「不要讀取 `.env*`」只是文字指示，**不保證**被遵守。【建議】開發用的機密不要放在 Codex 的工作目錄裡。

### 10.3 瀏覽器驗證：Codex 怎麼看到畫面

![圖：Codex 怎麼看到瀏覽器：app 用 Browser plugin，CLI 建議用 Playwright MCP，需要登入的網站先確認需求，頁面內容當作不受信任的輸入](figures/claude-react-codex-browser.svg)

**Codex app 的 Browser plugin**（【官方\*】）：
- 官方頁面（<https://developers.openai.com/codex/app/browser>）說，app 內建瀏覽器讓你和 Codex 在 thread 裡**共看同一個渲染後的頁面**，用途包含建置與除錯網頁應用、預覽頁面、對頁面留視覺化評論。
- 使用方式：安裝並啟用 Browser plugin，之後請 Codex 用瀏覽器，或用 `@Browser` 指定。
- 官方建議先請 Codex 啟動或檢查 dev server 再開瀏覽器；改完程式後再看更新後的路由；改動則在 review pane 看 diff 並留評論。
- 官方提醒：**頁面內容要當作不受信任的輸入，不要把機密貼進瀏覽器流程**。
- **我沒有查證** Codex CLI 能不能用這個 plugin。官方頁面講的是 app。

**CLI 用 Playwright MCP**（【建議】）：
- 【官方】加 MCP server 的語法是 `codex mcp add <NAME> -- <COMMAND> [ARGS...]`，用 `codex mcp list` 查看。
- Playwright MCP 的套件與啟動指令，與第 4.2 節 Claude Code 的相同（取自搜尋結果，含 Playwright 官方文件）。兩者組合起來是：

```bash
codex mcp add playwright -- npx @playwright/mcp@latest
codex mcp list
```

- 也可以寫在 `config.toml`。【官方\*】MCP 設定寫在 `[mcp_servers.<名稱>]`，stdio server 用 `command` 與 `args`：

```toml
[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@latest"]
```

- 這是【推論】：我把已知的兩段（Codex 的加法、Playwright 的套件）接在一起，**沒有實際執行**；團隊共用時建議像第 4.2 節一樣固定版本，不要用 `@latest`。
- 需要登入的網站：第三方文章提到 Codex 有 Chrome 擴充功能可用於登入狀態（🔎 [文章](https://codex.danielvaughan.com/2026/05/07/codex-for-chrome-extension-browser-integration-authenticated-workflows/)，我沒有開啟、也沒有驗證）。【推論】Playwright 通常自己啟動瀏覽器，不帶你日常 Chrome 的登入狀態；本機開發的 `localhost` 頁面通常不需要登入。

### 10.4 完整範例流程：用 localhost 啟動 React，讓 Codex 直接檢查結果

情境與第 4.4 節相同（登入表單的驗證），下面用 CLI ＋ Playwright MCP。**這是我依上面各段組成的流程，沒有實際跑過**；提示詞是我寫的（官方沒有針對 Playwright MCP 的範例），檔名、網址與埠號是示意。

![圖：Codex 的 localhost 範例流程，你、dev server、Codex CLI 與瀏覽器的互動順序](figures/claude-react-codex-flow.svg)

**步驟 1：終端機 A 啟動 dev server**（【建議】）

```bash
yarn start
```

記下終端機印出的網址。本文範例用 `localhost:3000`，**實際埠號以 `yarn start` 在終端機印出的網址為準**。

**步驟 2：終端機 B 在專案目錄啟動 Codex**（【官方】）

```bash
cd your-react-app
codex -C . -s workspace-write -a on-request
```

**步驟 3：確認 MCP 工具有載入**（【官方】`/mcp` 列出目前可用的 MCP tools）

```text
/mcp
```

應該看得到 `playwright` 的工具；工具名稱依版本而定，我沒有實際看過。

**步驟 4：請 Codex 檢查目前的畫面**（【建議】提示詞）

```text
Open http://localhost:3000/login in the browser, submit the form with an empty
email and with an invalid email, and check that the error messages appear
correctly. Also report any console errors. Do not edit files yet.
```

**步驟 5：發現問題就請它修，並重新驗證**（【建議】）

```text
Based on what you observed, fix the validation in
src/components/LoginForm.tsx, then reload the page and verify it again.
Run yarn test and yarn lint before you finish.
```

`-a on-request` 下，Codex 會視需要請你批准指令或寫檔；dev server 熱更新後它再請瀏覽器重新載入確認。

**步驟 6：收尾**（【官方】）：用 `/diff` 看變更，用 `/review` 審查 working tree，或在終端機執行 `codex review --uncommitted`，再自己 commit。

**補充**：
- 【推論】Playwright MCP 由 Codex 所在的機器啟動瀏覽器，所以 `localhost` 指的是**那台機器**。Codex Cloud 的任務是在雲端機器跑，你本機的 dev server 對它是看不到的；要讓 Codex 驗證 `localhost` 頁面，dev server 與瀏覽器要和 Codex 在同一台。官方資料沒有針對這個情況說明，我沒有驗證。
- 【建議】把驗證方式寫進 `AGENTS.md`，例如：「瀏覽器驗證：開 `http://localhost:3000`，只回報 console 的 error 與 warning」。
- 官方提醒頁面內容是不受信任的輸入：被檢查的頁面如果會顯示使用者輸入或外部內容，請別讓它的文字左右 Codex 的後續動作。

### 10.5 把關、審查、平行開發與 CI

- **把關**：因為 hook 的設定我沒查證，【建議】先用較樸素的做法：在 `AGENTS.md` 要求「完成前跑 `yarn test` 與 `yarn lint`」，再用 CI 或 git 的 pre-commit hook 擋住沒過的 commit。`AGENTS.md` 是文字指示，不保證被遵守，所以真正的把關要放在 CI。
- **目標條件**：【官方】Codex 有 `/goal`（設定、暫停、恢復、清除目標）。可以用像第 3 節那樣**可驗證**的條件（測試全過、lint 退出碼為 0）；`/goal` 的細部行為我沒查證，請以 `/goal` 的說明為準。
- **審查**：【官方】`/review`、`/diff`、`codex review --uncommitted`；多 Agent 審查見 [CodeX-Agent](CodeX-Agent.md)。
- **平行開發**：【官方】自己建 worktree 並用 `-C` 指向，不是 Codex 內建功能：

```bash
git worktree add ../app-feature-b -b feature-b
codex -C ../app-feature-b -s workspace-write -a on-request
```

  【建議】和第 6 節一樣：新的 worktree 沒有 `node_modules`，要自己安裝依賴；同時開多個 dev server 要用不同的 port。
- **CI**：【官方】用 `codex exec`。本庫整理的 CI 用法是 `codex exec -a never --json`，並用 `--sandbox` 控制範圍；本庫另提醒：`CODEX_API_KEY` 只支援 `codex exec`，要注入**單次 job**，不要設成會被測試或依賴 hook 讀到的 job-level 環境變數。範例（【建議】，沒有實際執行）：

```bash
codex exec --json --sandbox workspace-write -a never \
  "Run yarn test and summarize the failing tests. Do not change files."
```

  只要 Codex 分析、不改檔，可改成 `--sandbox read-only`；但測試若需要寫入暫存檔，read-only 會失敗，請在隔離的 CI worktree 用 `workspace-write`。

### 10.6 用 Codex 做這件事的限制

- 我**沒有讀到** OpenAI 官方頁面原文（網路被擋），Browser plugin、`AGENTS.md`、MCP 設定的細節只來自搜尋摘要，標了【官方\*】。
- 沒有驗證：Browser plugin 能否在 CLI 使用；hook 的事件與設定；Codex 能否禁止讀 `.env`；`workspace-write` 下 `yarn add`／`yarn install` 與連本機埠的行為；`/goal` 的細部行為。
- 範例流程與提示詞是我組合的，沒有在實際的 React 專案上跑過。
- Codex 更新快，旗標與功能以你當下的 `codex --help` 與官方文件為準。

---

## 11. 驗證說明與限制

- 資料日期 2026-11-18。**我沒有實際在 React 專案上跑過本文的流程**，也沒有執行任何範例指令。
- **【官方】** 的內容取自本庫已整理的 Claude Code 文件（來源為 `code.claude.com` 的官方文件，包括 hooks、MCP、worktree、`/batch`、`/goal`、權限與非互動模式），並與本庫對應章節一致；第 4.1 節的 Chrome 整合取自官方頁面[Use Claude Code with Chrome](https://code.claude.com/docs/en/chrome)，我於 2026-11-18 取得了全文；**但我沒有實際安裝擴充功能或執行過 `claude --chrome`**，所以沒有親眼驗證它能讀到什麼。其餘各節我沒有開啟官方頁面，內容取自本庫已整理的資料。
- **第 10 節（Codex）**：【官方】取自本庫的 Codex 文件；【官方\*】只來自搜尋結果對 OpenAI 官方頁面的摘要，我**沒有開啟原文**（`developers.openai.com` 在這個環境無法連線）；沒有實際執行任何 Codex 指令。
- **Playwright MCP** 的指令取自搜尋結果（含 Playwright 官方文件），不是 Claude Code 文件；各旗標請以 Playwright 官方說明為準。
- **【建議】** 都是我的歸納，沒有官方依據；React、Vite、Next.js、Vitest、Jest 與 React Testing Library 各自的用法，本文沒有查證。
- Claude Code 更新很快，功能名稱、旗標與預設值以官方文件為準；本庫的 [Claude-Code-CLI](Claude-Code-CLI.md) 標有它整理時的版本資訊。

---

## 12. 官方來源

- Claude Code 的 Chrome 整合（第 4.1 節的依據）：<https://code.claude.com/docs/en/chrome>
- Claude Code 的 MCP：<https://code.claude.com/docs/en/mcp.md>
- Claude Code 的 memory（CLAUDE.md）：<https://code.claude.com/docs/en/memory.md>
- Playwright MCP 入門：<https://playwright.dev/python/docs/getting-started-mcp>
- Codex 的瀏覽器（Browser plugin，第 10.3 節）：<https://developers.openai.com/codex/app/browser>
- Codex 的 AGENTS.md：<https://developers.openai.com/codex/guides/agents-md>
- Codex 的 MCP：<https://developers.openai.com/codex/mcp>
- Codex 設定參考：<https://developers.openai.com/codex/config-reference>
- 以上四個網址來自搜尋結果，**我沒有開啟原文**。
- 本庫對應文件：[Claude-Code-CLI](Claude-Code-CLI.md)、[Claude-Context](Claude-Context.md)、[Agentic-Engineering](Agentic-Engineering.md)、[Claude-Agent](Claude-Agent.md)、[CodeX-CLI](CodeX-CLI.md)、[CodeX-Agent](CodeX-Agent.md)
