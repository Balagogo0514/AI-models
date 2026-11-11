# Claude Code Skill/Plugin 比較：superpowers vs planning-with-files vs grill-me

> 資料整理時間：2026-07-12（來源：本機已安裝 plugin 設定、官方 `claude-plugins-official` marketplace 目錄、GitHub 專案文件、Claude Code 官方文件）
> 2026-11-11 新增 `grill-me`（Matt Pocock，來源：GitHub `mattpocock/skills`，同日讀取 `main`；該 repo 持續更新，內容以安裝當下版本為準）

## 1. 環境現況

本機（`G:\ClaudeCode\AI-models`）目前只安裝了一個 plugin：

| Plugin | 來源 | 版本 | 狀態 |
|---|---|---|---|
| `superpowers` | 官方 `claude-plugins-official` marketplace | 6.1.1 | 已安裝 |
| `planning-with-files` | 第三方（[OthmanAdi/planning-with-files](https://github.com/othmanadi/planning-with-files)），非官方 marketplace | — | **未安裝** |
| `grill-me`（屬於 `mattpocock-skills`） | 第三方（[mattpocock/skills](https://github.com/mattpocock/skills)），README 列為可從 `claude-plugins-official` 安裝 | 讀取 `main`（2026-11-11） | 未檢查本機是否安裝（本次是從雲端環境讀取 GitHub） |

`planning-with-files` 不在官方 marketplace 目錄中，需另外透過 `npx skills add OthmanAdi/planning-with-files --skill planning-with-files -g`（純 skill 安裝）或 `/plugin install planning-with-files@planning-with-files`（正式 plugin 路線，需先加入其 marketplace）才能取得。

---

## 2. superpowers 描述與用法

### 2.1 是什麼

官方 `claude-plugins-official` marketplace 裡 `superpowers` 的 plugin.json 描述："Core skills library for Claude Code: TDD, debugging, collaboration patterns, and proven techniques"。作者是 Jesse Vincent（obra），MIT 授權，原始碼在 [obra/superpowers](https://github.com/obra/superpowers)。

本質是一套**可組合的 skill 庫 + 一個 SessionStart hook**，目的是讓 coding agent 從對話一開始就自動具備完整的軟體開發方法論——先釐清需求、拆解成實作計畫、TDD 逐步落地、review、驗證——而不需要使用者手動記得該呼叫哪個 skill。

### 2.2 運作機制：SessionStart hook + using-superpowers meta-skill

- `hooks/hooks.json` 註冊了一個 `SessionStart` hook（`matcher: startup|clear|compact`），每次新對話、`/clear`、或 context compaction 之後都會執行 `hooks/session-start`，把 `using-superpowers` 這個 meta-skill 的完整內容注入到對話最前面的 system context 裡（本次對話一開始出現的「SessionStart hook additional context: `<EXTREMELY_IMPORTANT>` … `using-superpowers` …」那段就是這個機制的實際輸出）。
- `using-superpowers` 的規則是強制性的：「只要有 1% 可能相關就必須呼叫對應 skill」，且「先呼叫 skill，再回答/探索/提問」，目的是防止 agent 用「這只是個簡單問題」「我先看一下程式碼就好」之類的理由跳過既有流程。
- 因此使用者**不需要手動打字呼叫**任何一個 superpowers skill——只要正常描述意圖（「我要做 X 功能」「這段測試一直失敗」），對應的 skill 就會被自動判斷並觸發。

### 2.3 內建的 13 個 skill（本機版本 6.1.1）

| Skill | 用途 |
|---|---|
| `brainstorming` | 任何「新增功能/元件/行為」前，先探索使用者意圖、需求與設計 |
| `writing-plans` | 有 spec/需求後，動手寫程式前先產出可執行的實作計畫 |
| `executing-plans` | 在獨立 session 中，帶著審查檢查點執行已寫好的計畫 |
| `subagent-driven-development` | 在目前 session 內，把計畫拆給多個 subagent 逐步執行 |
| `dispatching-parallel-agents` | 遇到 2 個以上互不依賴、無共享狀態的任務時，平行派工 |
| `test-driven-development` | 實作任何 feature/bugfix 前先寫測試（red-green-refactor） |
| `systematic-debugging` | 遇到 bug、測試失敗、非預期行為時，先系統化除錯再提修法 |
| `using-git-worktrees` | 需要與目前工作區隔離的環境時，建立 git worktree |
| `requesting-code-review` / `receiving-code-review` | 完成任務後請求 review；收到 review 意見後如何嚴謹驗證再處理（而非照單全收） |
| `verification-before-completion` | 宣稱「完成/修好/測試通過」前，先實際跑驗證指令、確認輸出 |
| `finishing-a-development-branch` | 實作完成、測試都過後，決定 merge/PR/清理的收尾流程 |
| `writing-skills` | 建立、編輯、驗證新 skill（用法比較見第 11 節與 `skill-creator` 的對照） |
| `using-superpowers` | 上述所有 skill 的「總開關」meta-skill，靠 SessionStart hook 自動注入，強制在動作前檢查是否有適用的 skill |

### 2.4 用法

安裝（本機已完成，版本 6.1.1）：

```
/plugin install superpowers@claude-plugins-official
```

若想改走社群維護的 superpowers marketplace（額外提供一些周邊 plugin）：

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

日常使用不需要任何額外指令：由於 SessionStart hook + `using-superpowers` 的強制檢查規則，只要正常描述想做的事（「幫我加個功能」「這段測試一直失敗」「這個改完了，幫我開 PR」），對應的 skill 就會自動判斷並介入。若想明確指定某個 skill，也可以直接用 Skill 呼叫機制點名（例如「用 systematic-debugging 幫我查這個 bug」）。

---

## 3. planning-with-files 描述與用法（第三方，本機未安裝）

### 3.1 是什麼

`planning-with-files` 是第三方作者 OthmanAdi 開發的持久化規劃 skill（MIT 授權，[GitHub](https://github.com/OthmanAdi/planning-with-files)）。核心定位是把 `task_plan.md`、`findings.md`、`progress.md` 存在磁碟上，讓 agent 撐過 context 遺失、`/clear`、崩潰——實作的是所謂「Manus 風格」的 context engineering：把 markdown 當成「磁碟上的工作記憶」，而不是依賴對話 context。透過開放的 SKILL.md 規格，宣稱可支援 60+ 種 AI agent/IDE。

> 注意：repo README 中列出的 star 數、fork 數、benchmark 通過率等數據為專案自述，未經獨立驗證，僅供參考、不代表事實查核結果。

### 3.2 三份核心檔案

- **`task_plan.md`** — 階段（phase）、依賴關係、進度 checkpoint
- **`findings.md`** — 研究過程中的發現、技術筆記
- **`progress.md`** — session 執行日誌、測試結果、錯誤紀錄
- 可用 slug 模式的目錄 `.planning/YYYY-MM-DD-slug/` 隔離平行進行的多個任務，各自維護一組上述三份檔案

### 3.3 安裝方式

**通用（任何 IDE，純 skill 安裝，非正式 plugin）：**
```
npx skills add OthmanAdi/planning-with-files --skill planning-with-files -g
```

**Claude Code plugin 路線（可取得完整 hook 功能）：**
```
/plugin marketplace add OthmanAdi/planning-with-files
/plugin install planning-with-files@planning-with-files
```
安裝後可用 `/planning-with-files:plan`（或簡寫 `/plan`）、`/planning-with-files:status`（或 `/plan:status`）呼叫。

**語言變體**：阿拉伯文（`-ar`）、德文（`-de`）、西班牙文（`-es`）、簡體中文（`-zh`）、繁體中文（`-zht`）等後綴版本。

### 3.4 支援平台分級

| 分級 | 涵蓋內容 | 平台 |
|---|---|---|
| **Enhanced**（hook + 生命週期自動化） | 完整 hook 整合，自動重新注入計畫、完成驗證 | Claude Code、Cursor、GitHub Copilot、Codex、Gemini CLI、Kiro、Mastra Code、CodeBuddy、FactoryAI Droid、Hermes Agent、OpenCode |
| **Standard**（僅 SKILL.md 規格） | 透過 `npx skills add` 安裝，無 hook 自動化 | Continue、Pi Agent、OpenClaw、Autohand Code、Antigravity、Kilocode、AdaL CLI/Sylph AI |
| **Sandbox** | 硬體隔離 micro-VM | BoxLite（透過 ClaudeBox） |

### 3.5 Hook 生命週期

| Hook | 時機 | 作用 |
|---|---|---|
| `SessionStart` | session 開始 | 從磁碟讀取並注入目前進行中的計畫 |
| `UserPromptSubmit` | 每次送出 prompt/呼叫工具前 | 重新讀取計畫，防止目標漂移 |
| `PreToolUse` | 工具呼叫前 | 計畫複誦（僅 legacy 模式使用） |
| `PostToolUse` | 工具呼叫後 | 提醒 agent 更新 `progress.md` |
| `PreCompact` | `/compact` 前 | 提醒先把進度寫回磁碟再壓縮 |
| `Stop` | session 結束/`/stop` | 驗證所有階段是否完成，未完成則擋停 |

### 3.6 設定與環境變數

- **`PLANNING_DISABLED=1`**：單次 session 暫時停用計畫注入與所有 hook（適合 CI、一次性 review bot），不需改任何檔案。
- **初始化模式（v3.0.0+）**：
  - 預設（v2 相容）——不加任何標記，行為與舊版一致
  - `--autonomous`——拿掉逐工具呼叫的複誦，只保留 turn 開始時注入，給能力較強的模型省 token
  - `--gated`——在 Stop hook 加上更嚴格的完成閘門，需要「gated 模式啟用、有進行中的 phase、`stop_hook_active` 為 false、擋停次數未達上限、ledger 自上次擋停後有進展」五個條件同時成立才會擋停

### 3.7 常用指令與腳本

- `/plan`、`/plan:status`、`/planning`：開始/查看規劃進度
- `/plan-goal`：與 Claude Code 內建 `/goal` 搭配
- `/plan-loop`：與 `/loop` 搭配，每隔一段時間（如 10 分鐘）自動重讀計畫
- `/plan-attest`：用 SHA-256 對 `task_plan.md` 做雜湊鎖定，防止被竄改
- 底層腳本：`init-session.sh/.ps1`（建立計畫結構）、`check-complete.sh/.ps1`（驗證階段是否完成）、`attest-plan.sh`、`resolve-plan-dir.sh`、`set-active-plan.sh`（平行計畫隔離用）

### 3.8 目前版本與本機現況

最新版本 v3.4.1（2026-07-12），本機（見第 1 節）**未安裝**。若要啟用，優先用「通用 `npx skills add`」取得純 skill 版本做快速測試；若確定要長期使用且在 Claude Code 上，再走 plugin 路線以取得完整 hook 自動化（細節見第 10 節「如何停用」，同樣適用於評估後想暫停/移除的情況）。

---

## 4. grill-me（Matt Pocock，第三方）

### 4.1 是什麼

`grill-me` 是 Matt Pocock 的 agent skills 集合 [mattpocock/skills](https://github.com/mattpocock/skills) 裡的一個 skill，MIT 授權；README 自述這些 skill「straight from my .agents directory」。✅（2026-11-11 讀取）

- 歸在 **Productivity** 類，一句話描述是「Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved」。
- SKILL.md 的 frontmatter 是 `disable-model-invocation: true`：**只能由你手動 `/grill-me` 觸發**，Claude 不會自己挑它來用。
- README 把 `/grill-me` 稱為「for non-code uses」的工具；程式相關的版本是 `grill-with-docs`（見 4.3）。

> ⚠️ 該 repo 持續演進。2026-11-11 讀到的 `grill-me` 本身只有一行：轉呼叫另一個 skill `grilling`；真正的拷問邏輯在 `grilling`。若你讀的版本不同，以你安裝的為準。

### 4.2 運作機制：轉呼叫 `grilling`

依 `grilling` 的 SKILL.md 內容整理（摘要，非逐字）：

| 規則 | 說明 |
|---|---|
| 把主題當**設計樹** | 每個決定會帶出依賴它的下一批決定 |
| **一輪問完所有「目前能回答」的問題** | 編號列出，每題附**建議答案**，寫法讓你回「yes」就等於採納；然後等你回答才繼續 |
| 有依賴的問題**留到後面輪次** | 每輪結束重新計算「目前能問的問題」 |
| **事實自己查，決策才問你** | 環境事實（檔案、設定等）由 agent 用 subagent 代查，不問你；決策屬於你 |
| **結束條件** | 沒有待問問題、每個分支都走過、沒有被默默假設的事 |
| **不先動手** | 你確認雙方理解一致之前，agent 不依結果採取行動 |

### 4.3 repo 裡的相關 skill

README 列出的相關 skill（✅ 依 README 的一句話描述）：

- **`grill-with-docs`**：同樣的拷問，但過程中會**同時建立文件**（ADR 與領域詞彙表）；也是 `disable-model-invocation: true`。
- **`to-spec`**：把對話整理成規格並發佈；**`to-tickets`**：把計畫拆成 tracer-bullet 的 ticket，附阻塞關係。
- **`implement`／`implement-spec`**：依規格或 ticket 實作，用 TDD 與 code review；後者用 task graph 與平行 subagent 跑完整份規格。
- 其他模型可自動觸發的紀律型 skill：`tdd`、`diagnosing-bugs`、`code-review`、`research`、`prototype` 等。

也就是說，Matt 的這套本身就是一條「拷問 → 規格 → ticket → 實作」的流水線。和 superpowers 的粗略對應如下（🛠 依一句話描述的對照，不代表行為相同）：

| 階段 | superpowers | mattpocock-skills |
|---|---|---|
| 澄清需求 | `brainstorming` | `grill-me`／`grill-with-docs` |
| 規格與計畫 | `writing-plans` | `to-spec`、`to-tickets` |
| 執行 | `executing-plans`、`subagent-driven-development` | `implement`、`implement-spec` |
| 測試 | `test-driven-development` | `tdd` |
| 除錯 | `systematic-debugging` | `diagnosing-bugs` |
| 審查 | `requesting-code-review`／`receiving-code-review` | `code-review` |

### 4.4 安裝

依 README ✅：

```
# Claude Code（plugin，自動更新）
claude plugin install mattpocock-skills@claude-plugins-official

# 其他 agent，或想要可編輯的檔案（複製，需手動更新）
npx skills@latest add mattpocock/skills -a <agent>
```

- **每個 agent 只選一種安裝方式**，兩種都裝每個 skill 會出現兩次。
- plugin 會自己更新；用 `npx` 複製的檔案要靠 `npx skills@latest update`。
- README 提到 `setup-matt-pocock-skills` 是「每個 repo 做一次的設定」。
- Gemini CLI、GitHub Copilot、Codex 也各有安裝指令，見 README。

### 4.5 對 context 的影響

![三者對 context 的足跡：grill-me 用到前不佔，grilling 描述常駐；superpowers 有 skill 描述常駐與 SessionStart hook 注入；planning-with-files 有六種 hook 與三個計畫檔](figures/claude-skills-context.svg)

- **`grill-me` 本身用到前不佔 context**：官方文件說，設了 `disable-model-invocation: true` 的 user-only skill，在你呼叫前什麼都不載入。✅
- **但它轉呼叫的 `grilling` 是模型可觸發的 skill**，描述會常駐（成本低）。你手動呼叫後才載入 `grill-me` 本文（極短），再載入 `grilling` 本文。
- **整包 plugin 會帶進很多 skill**：README 列了不少「模型可自動觸發」的紀律型 skill，它們的描述都會常駐。裝完用 `/context` 看實際用量；不想要的可以用 `skillOverrides` 隱藏。✅
- **與 superpowers 並裝會功能重疊**（兩邊都有 TDD、除錯、review）。plugin 的 skill 有命名空間，不會直接同名衝突 ✅，但描述互相競爭時，官方警告「描述模糊或重疊，Claude 可能載入錯的 skill」。✅
- ⚠️ 我沒有逐檔檢查 `mattpocock-skills` 是否註冊 hook；README 沒有提到，所以圖中標為「未見」。

### 4.6 適合與不適合

- **適合**：需求或設計還模糊，想被逼著把每個決定想清楚；非程式用途的規劃。它的核心價值是**把決定「問出來」**，不是產出計畫檔。
- **不適合**：需求已經清楚的小改動（多一輪問答是純成本）；希望全自動、不想被打斷的流程（它只能手動觸發，而且要等你回答才往下）。

---

## 5. 三者定位本質不同

| 面向 | superpowers（`writing-plans` / `executing-plans`） | planning-with-files | grill-me |
|---|---|---|---|
| 核心目的 | 把 spec 轉成**嚴謹的實作計畫**（TDD、bite-sized task、精確檔案路徑），交給 subagent 或 session 逐步執行 | 維持**跨 session 的持久工作記憶**，防止 context 遺失、崩潰、`/clear` 後斷線 | 計畫或設計**之前**的決策澄清：被拷問到每個分支都解決 |
| 檔案結構 | 單一計畫檔：`docs/superpowers/plans/YYYY-MM-DD-<feature>.md` | 三個檔案並存：`task_plan.md`（進度）、`findings.md`（發現）、`progress.md`（執行日誌），可用 slug 目錄隔離平行任務 | 預設**不寫檔**，產出是對話裡的共識；`grill-with-docs` 才另寫詞彙表與 ADR |
| 觸發機制 | 手動 Skill 呼叫，由 `using-superpowers` meta-skill 判斷「只要有 1% 可能相關就必須呼叫」 | IDE **hooks** 自動化：`SessionStart`/`UserPromptSubmit` 自動重新注入計畫、`PreToolUse` 執行前複誦、`PostToolUse` 提醒更新進度、`Stop` hook 擋掉未完成就結束 session | **只由你手動 `/grill-me`**（`disable-model-invocation: true`），再轉呼叫 `grilling` |
| 崩潰恢復 | 沒有專門機制——計畫檔是一般 markdown，人工重讀即可 | 有專門「catchup report」：比對 session store 時間戳，抓出崩潰/`/clear` 後遺漏的對話並自動補齊 | 沒有；只存在於對話中 |
| 多 agent 協作 | 靠 `subagent-driven-development` 手動派工 | 內建 ledger 檔，支援多 agent 共享狀態 | 不做協作；只用 subagent 代查事實 |
| 支援平台 | Claude Code（及 superpowers 支援的其他 CLI） | 18+ IDE，分三級支援（Enhanced/Standard），含 Claude Code、Cursor、Codex、Gemini CLI 等 | Claude Code、Codex、Copilot、Gemini CLI 或任何 agent（README） |

### 5.1 三者在開發流程中的位置

![三者在開發流程中的位置：grill-me 負責澄清需求（手動觸發）；superpowers 負責設計與計畫、執行與審查、驗證與收尾（自動介入）；planning-with-files 橫跨全程負責持久化](figures/claude-skills-position.svg)

三者**不在同一個層次競爭**：`grill-me` 管「想清楚要做什麼」，`superpowers` 管「怎麼做完」，`planning-with-files` 管「做很久時不丟進度」。真正會重疊的是 `grill-me` 與 `superpowers:brainstorming`（見第 8 節）。

---

## 6. 一個專案可以有很多 session——這是兩者比較的關鍵背景

Claude Code 每次對話都是獨立 session，存成一個 `.jsonl` transcript，放在 `~/.claude/projects/<專案編碼路徑>/<session-id>.jsonl`。**同一個專案資料夾底下可以累積非常多個 session**——例如本專案（`G--ClaudeCode-AI-models`）從 2026-06-29 到現在已經有 8 個獨立 session 檔案。

這件事直接決定了「靠 `--resume` 夠不夠」：

- `--resume` / `--continue` **一次只能接續其中一個 session**，不會自動整合其他 session 的進度。
- 今天用 session A 做完某功能，明天開新 session B 做另一功能，session B 預設看不到 session A 的內容，除非你手動指定 resume 回 A。
- 專案裡 session 一多，光憑 session ID 找「哪個 session 做了什麼」也不直覺。

---

## 7. 為何「靠 resume 復原」不能完全取代 planning-with-files

| 問題 | `--resume`/`--continue` 能否解決 | 說明 |
|---|---|---|
| 同一 session 崩潰/關閉後接續 | ✅ 可以 | 這是 resume 的本職 |
| 長對話自動 compaction 造成細節失真 | ⚠️ 部分——resume 拿到的是**模型生成的摘要**，不是逐字記錄，細節可能被改寫或遺漏 | 這正是本次對話已經實際發生過的情況（對話一開始就是從「上一段對話因超出 context 被壓縮」接續的） |
| 跨工具/跨 agent 讀取進度 | ❌ 不行 | resume 是 Claude Code 專屬的 session 機制，換到 Cursor、換一個 subagent、換 CI 環境都讀不到 |
| 多個平行 agent 共享同一份進度 | ❌ 不行 | 每個 session 各自獨立，無法合併多個平行 agent 的狀態 |
| 人類（非 AI）審查目前進度 | ❌ 不方便 | 翻一份 checked-in 的 `progress.md`（可 `git diff`）遠比叫人去 resume 一段對話記錄實際 |

**結論**：`resume` 適合「單一 agent、單一工具、任務不會拖過好幾天」的情境；`planning-with-files` 要解決的是「長時程、多 agent、或需要給人類/其他工具審查進度」這幾類 resume 天生無法覆蓋的問題。

---

## 8. 會衝突嗎？

目前環境不會衝突（`planning-with-files` 未安裝）。但若兩個都裝上，有兩個實際風險：

1. **重複觸發**：superpowers 的「1% 相關就必須呼叫」規則，可能讓同一個多步驟任務同時觸發 `writing-plans` 和 `planning-with-files` 的 `/plan` 流程，產生兩份格式、位置都不同的計畫檔，搞不清哪份才是真的計畫。
2. **Hook 疊加**：`planning-with-files` 掛的 `PreToolUse`/`PostToolUse`/`Stop` hooks 會主動複誦、提醒、甚至擋停；superpowers 沒有 hook，純 skill 邏輯。兩者疊加時會同時收到雙重叨念。

**建議分工**（若真要兩個並用）：讓 superpowers 的 `writing-plans` 負責生成計畫內容（把 spec 拆解成精確任務），把 `planning-with-files` 定位成純粹的崩潰恢復/跨 session 記憶層，不讓它另開一份計畫格式——但這需要在 `CLAUDE.md` 明確分工，兩者預設不會自動協調。

### 8.1 加入 grill-me 之後

- **與 planning-with-files**：不衝突。`grill-me` 沒有 hook、不寫檔（⚠️ plugin 內容未逐檔驗證）；它只在你手動呼叫時介入。
- **與 superpowers 的 `brainstorming`**：**有功能重疊**，兩者都在動手前釐清需求。差別在於：`brainstorming` 由 hook 與 meta-skill **自動觸發**、之後銜接 `writing-plans`；`grill-me` 只由你**手動觸發**、被拷問到分支都解決，結束時不自動產出計畫檔。
- **實務上不會打架**：`grill-me` 是 user-only，Claude 不會自己挑它，所以不會和 `brainstorming` 重複觸發。要留意的是 `grilling`（模型可觸發）的描述，可能在你說「幫我把這個問清楚」這類話時被挑中，和 `brainstorming` 搶；若發現行為重疊，可在 `CLAUDE.md` 寫明「需求澄清用 `/grill-me`」。⚠️（推論）
- **整包安裝 mattpocock-skills 的副作用**：會帶進與 superpowers 重疊的 `tdd`、`diagnosing-bugs`、`code-review` 等，見 4.5。

### 8.2 三者並存時，預設會發生什麼

標記：✅ 官方〈[Extend Claude Code](https://code.claude.com/docs/en/features-overview.md)〉明載　⚠️ 推論，未在三者並裝的環境實測。

- **skill 描述互相競爭** ✅：Claude 用你的任務去比對所有 skill 的描述來挑。官方警告「描述模糊或重疊，Claude 可能載入錯的 skill，或漏掉該用的」。
- **hook 全部都會觸發** ✅：不同來源的 hook 是**合併**的，沒有誰蓋掉誰。
- **同名才覆寫** ✅：skill 同名時只有一份生效（managed > user > project）；plugin 的 skill 有命名空間，不會直接同名衝突，但**功能相同**的 skill 會同時存在。
- **指示互相矛盾時由 Claude 判斷** ✅：CLAUDE.md、skill 都只是請求，不是強制，結果不確定。

**結論**：Claude Code **不會自動仲裁**三者，要靠你自己分工。

### 8.3 三個都會執行嗎？

**不會三個都「主動」執行，但 superpowers 與 planning-with-files（以 plugin 安裝時）的 hook 會一直在背景跑。** 裝了不等於執行，要看它靠什麼觸發。

![三個 skill 誰會自動執行：superpowers 的 hook 與依描述挑都會；planning-with-files 視安裝方式與描述符合；grill-me 只有手動 /grill-me，僅它轉呼叫的 grilling 可被挑；hook 是合併的](figures/claude-skills-trigger.svg)

| 觸發方式 | superpowers | planning-with-files | grill-me |
|---|---|---|---|
| **事件觸發的 hook**（不用你叫，每次都跑） | ✅ `SessionStart`（新對話、`/clear`、壓縮後）注入 `using-superpowers` 全文 | ✅ 以 plugin 安裝時有 6 種：`SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`PreCompact`、`Stop` | 沒有 ⚠️（README 未見，未逐檔驗證） |
| **Claude 依任務挑**（描述比對） | ✅ 會，且被 `using-superpowers`「有 1% 可能相關就必須呼叫」的規則推著 | 描述符合才會 | 它本身不會；轉呼叫的 `grilling` 可被挑 ⚠️ |
| **只有你手動叫才動** | 可選（點名某個 skill） | `/plan` 等指令 | ✅ `/grill-me`（`disable-model-invocation: true`） |

**一個日常情境**：你說「我要做 X 功能」。

- **superpowers**：自動介入，通常先走 `brainstorming`。
- **planning-with-files**：若以 plugin 安裝且專案已有計畫，hook 會在每次送出 prompt 時把計畫重讀進來；skill 本身要描述符合才會被挑。
- **grill-me**：不動，除非你打 `/grill-me`。

**關鍵點**

- **hook 是合併的** ✅：兩個 plugin 的 hook 會同時觸發，沒有誰蓋掉誰，所以 superpowers 與 planning-with-files 的 hook 通常**兩個都在跑**。
- **只裝 skill 沒有 hook**：planning-with-files 若以 `npx skills add` 安裝，就沒有 hook，也沒有背景執行的那部分（見 3.3、3.4）。
- **同一個任務可能觸發多個 skill**：官方沒有說一次只能用一個，這正是「兩份計畫檔」風險的來源 ⚠️（推論）。
- **你打 `/grill-me` 時，另外兩個仍在**：superpowers 注入的內容還在 context 裡，planning-with-files 的 hook 照樣觸發，不會因為你呼叫 grill-me 而暫停。這個互動沒有實測 ⚠️。

**想只讓其中一個執行**

- 不要 planning-with-files 的背景 hook：停用該 plugin，或單次設 `PLANNING_DISABLED=1`（見第 10 節）。
- 不要 superpowers 的自動介入：只能停用該 plugin；文件裡沒看到單獨關閉它 hook 的開關 ⚠️。
- grill-me：不需要處理，它本來就只由你叫才動。

### 8.4 兩兩之間的衝突風險

![三個 skill 並存時兩兩之間的衝突風險：superpowers 與 planning-with-files 風險高（兩份計畫檔、hook 疊加）；grill-me 與 superpowers 風險中（與 brainstorming 重疊）；grill-me 與 planning-with-files 風險低；三者並裝時 context 成本累加](figures/claude-skills-conflict.svg)

| 組合 | 風險 | 說明 |
|---|---|---|
| superpowers × planning-with-files | **高** | 同一個多步驟任務可能同時觸發 `writing-plans` 與 `/plan`，產出兩份位置與格式都不同的計畫檔；兩邊的 hook 疊加（見第 8 節前半） |
| grill-me × superpowers | **中** | 與 `brainstorming` 功能重疊。`grill-me` 是 user-only，不會自動重複觸發；但它轉呼叫的 `grilling` 可由模型觸發，可能在你說「幫我把這個問清楚」時搶走 `brainstorming` ⚠️ |
| grill-me × planning-with-files | 低 | 一個只在你手動呼叫時介入，一個負責持久化 |
| 三者並裝 | context 成本累加 | 三組 skill 描述常駐，再加 SessionStart 注入 `using-superpowers` 全文、planning-with-files 每次重新讀回計畫（見 4.5 的圖） |

### 8.5 怎麼處理（由輕到重）

![skill 衝突的處理方式：把分工寫進 CLAUDE.md（請求，不保證）；用 skillOverrides 隱藏（設定，有效）；只裝需要的 skill（安裝層）；暫停整個 plugin（停用，有效）；用 hook 或權限設定強制（強制）](figures/claude-skills-handling.svg)

1. **把分工寫進 CLAUDE.md**：最便宜，但只是請求，不保證遵守 ✅。例如：

   ```
   ## Skill 分工
   - 需求不清楚時，我會手動 /grill-me，你不要自己啟動需求拷問。
   - 設計與計畫用 superpowers 的 brainstorming、writing-plans，計畫只寫在 docs/superpowers/plans/。
   - 除非我明確要求 /plan，否則不要建立 task_plan.md、findings.md、progress.md。
   ```

2. **用 `skillOverrides` 隱藏不要的 skill**：把描述移出 context，不必改別人的檔案 ✅。
3. **只裝需要的 skill**：不要為了 `grill-me` 整包安裝 `mattpocock-skills`，否則會帶進與 superpowers 重疊的 `tdd`、`diagnosing-bugs` 等（見 4.5）。
4. **暫停整個 plugin**：`/plugin disable planning-with-files@planning-with-files`，恢復用 `/plugin enable`；單次 session 可用 `PLANNING_DISABLED=1`（見第 10 節）。因為 hook 是合併的，**無法讓其中一個 hook 蓋掉另一個**，要消除 hook 疊加只能停用其中一個 plugin。✅
5. **必須強制的事用 hook 或權限設定**：不要只靠 skill 或 CLAUDE.md ✅。

### 8.6 怎麼確認有沒有在打架，與建議配置

- 用 `/context` 看三組 skill 描述與注入內容實際佔了多少。
- 看對話裡實際觸發了哪些 skill：同一個任務是否啟動了兩套流程、是否出現兩份計畫檔、是否被重複提問。
- 用第 11 節的 `skill-creator` 做「該觸發／不該觸發」的評測。

| 情境 | 建議配置 |
|---|---|
| 日常開發 | 只留 superpowers；需求模糊時手動 `/grill-me` |
| 長時程、跨 session 的任務 | 再加 planning-with-files，並在 CLAUDE.md 明寫計畫檔只能有一份 |
| 不確定三個能否並存 | 先兩兩試跑，觀察是否出現雙份計畫檔或重複提問，再決定 |

> ⚠️ 以上處理方式是依官方的載入與優先規則推出來的，我沒有在三者並裝的實際環境測過行為。

### 8.7 會不會讓 LLM 更多來回、token 更多？

標記：✅ 官方〈[Manage costs effectively](https://code.claude.com/docs/en/costs.md)〉與〈[Extend Claude Code](https://code.claude.com/docs/en/features-overview.md)〉明載　⚠️ 推論或未實測。

**簡短回答**：**會，但來源不同、大小差很多。** 官方沒有針對這三個 skill 並存的實測數字，所以下面是方向，不是用量。

**兩個先記住的官方事實** ✅

- Claude Code **每次請求都把整個對話重送一次**，每次使用工具又是一個新請求，所以 context 越長，每個請求越貴。
- 有 prompt caching，重送的歷史多半以**快取讀取價**計算（一般是輸入價的 0.1 倍；Sonnet 5.5 與 Opus 5.5 為 0.05 倍），但它**仍佔 context 視窗**，也讓壓縮更早發生。

![token 與來回增加的來源與相對大小：三組 skill 描述常駐（固定、小）；superpowers 的注入（一次性、中）；planning-with-files 的 hook（每輪累積、大）；superpowers 流程（視任務）；grill-me 問答（視輪數）；session 越拉越長（累積）](figures/claude-skills-tokens.svg)

| 來源 | 多出什麼 | 大小 | 說明 |
|---|---|---|---|
| **三組 skill 描述常駐** | 每次請求多帶描述文字 | 小 | 在穩定的前綴裡，多半走快取價；grill-me 本身是 user-only，用到前不佔 ✅ |
| **superpowers 的 SessionStart 注入** | 新對話、`/clear`、壓縮後各注入一次 `using-superpowers` 全文 | 中 | 之後留在對話歷史裡，每次請求重送 |
| **planning-with-files 的 hook** | `UserPromptSubmit` 每次送出 prompt 重讀計畫；`PostToolUse` 每次工具呼叫後提醒更新進度 | **大，三者中最容易吃 token** | 官方說 **hook 輸出會成為對話的一部分** ✅，所以一路累積；`Stop` 在未完成時擋停，可能多出額外回合 ⚠️ |
| **superpowers 的流程本身** | brainstorming → 計畫 → TDD → review → 驗證，回合與工具呼叫都變多；`subagent-driven-development` 每個 subagent 另送自己的請求 ✅ | 視任務 | 這是「方法論的成本」，不是 skill 檔案的成本 |
| **grill-me** | 你和 Claude 的問答輪次變多；事實用 subagent 代查（另外的 token） | 視輪數 | 設計成**每輪批次提問**，已盡量減少來回（見 4.2） |
| **session 越拉越長** | 每個請求都更貴；壓縮本身是大請求 ✅ | 中到大 | 三者並裝時這個效應會被放大 ⚠️ |

**也有省 token 的一面**

- **hook 可以省**：官方建議用 hook 預處理資料，例如只回傳 log 裡的錯誤行，把幾萬 token 降到幾百 ✅。
- **事前澄清可以避免重工**：官方對 plan mode 的說法是「避免方向錯了之後的昂貴重做」；`grill-me` 與 `brainstorming` 的邏輯類似，但我沒有實測它們省多少 ⚠️。
- **skill 比 CLAUDE.md 省**：skill 按需載入，CLAUDE.md 每次都在 ✅。

**怎麼省**

1. **只開需要的**：日常只留 superpowers，需要時才叫 `/grill-me`；planning-with-files 只在長時程任務使用。
2. **planning-with-files 用 `--autonomous`**：拿掉逐工具呼叫的複誦，只在 turn 開頭注入（見 3.6）；單次關閉用 `PLANNING_DISABLED=1`。
3. **隱藏不要的 skill 描述**：用 `skillOverrides` ✅。
4. **任務之間用 `/clear`**：官方說陳舊的 context 會在之後每則訊息上浪費 token ✅。
5. **大量輸出交給 subagent，並選小模型**：簡單任務可指定 `model: haiku`；注意 subagent 自己的請求仍算你的用量 ✅。

**怎麼量，而不是猜**

- **`/context`**：看目前各類內容佔多少，包含 skill 描述與 MCP ✅。
- **`/usage`**：看本次 session 的 token 與 `Prompt cache` 命中率；訂閱方案另有按 skill、subagent、plugin 的用量歸屬與建議 ✅。
- **做 A/B**：同一個任務，一次只開 superpowers、一次三個都開，比較 `/usage` 的數字。這是唯一能得到你環境真實答案的方法。

---

## 9. 一般程式開發工作該用哪個？

**預設用 superpowers 就好**——已安裝、官方支援，`writing-plans → executing-plans/subagent-driven-development` 涵蓋「spec 拆解 → TDD 逐步實作 → 審查」的完整循環，足以應付大多數功能開發任務。

`planning-with-files` 的價值集中在**長時程、跨多個 session、容易被 `/clear` 或崩潰打斷**的情境（連續多天的大型 agent 任務、多 agent 協作）。一般單次或幾個 session 內能完成的開發用不到它的崩潰恢復機制，硬裝反而增加 hook 疊加、雙重計畫檔的複雜度。

只有當你發現**常常因為 context 被清掉或跨 session 而搞丟進度**時，才值得額外裝 `planning-with-files`。

**需求還沒想清楚時**：先 `/grill-me` 把決策問清楚，再交給 superpowers 的設計與計畫。`grill-me` 是 user-only、不佔常駐 context，所以只裝這一個 skill 的成本很低；但若為了它而整包安裝 `mattpocock-skills`，就會帶進一批會常駐描述的 skill（見 4.5），要先評估。需求已經很清楚的小改動，不需要它。

---

## 10. 如何停用 planning-with-files（不需完全移除）

視安裝方式而定：

**情況 1：透過 `/plugin install planning-with-files@planning-with-files` 裝的（正式 plugin 路線）**

```
/plugin disable planning-with-files@planning-with-files
```

- Plugin 還在，只是不載入（hooks、skill 都不會觸發）。
- 恢復時執行 `/plugin enable planning-with-files@planning-with-files`，設定完整保留。
- 若有其他已啟用的 plugin 依賴它，指令會失敗並附上要一併停用哪些依賴 plugin 的指令。

**情況 2：透過 `npx skills add OthmanAdi/planning-with-files -g`（純 skill 安裝，非正式 plugin）**

這種安裝方式不會出現在 plugin 註冊表裡，`/plugin disable` 找不到它，得靠它自己內建的開關：

- v3.4.0 提供環境變數 **`PLANNING_DISABLED=1`**，可針對單次 session 暫時跳過（適合 CI、一次性任務），不需改任何檔案。
- 若要「預設關閉、每次都不啟動」，官方文件沒有提供 toggle，只能手動移除或改名它的 hook 設定檔，或直接刪掉 skill 資料夾——這才算「移除」。

**重點**：`task_plan.md`/`findings.md`/`progress.md` 的內容跟 skill 本身是分開的，只是專案裡的一般 markdown 檔案。不管用哪種方式關閉/移除這個 skill，這些檔案都會留在 repo 裡，不會被連帶刪除。

---

## 11. skill-creator plugin（官方，2026-07-13 新安裝）

`skill-creator` 是 Anthropic 官方 `claude-plugins-official` marketplace 裡的獨立 plugin（作者：Anthropic），本機已透過 `/plugin install skill-creator@claude-plugins-official` 安裝（需執行 `/reload-plugins` 套用）。

### 11.1 用途

專門解決「建立/改良 skill」這件事本身，涵蓋一套完整的**草擬 → 測試 → 評分 → 迭代 → 觸發描述優化 → 打包**流程：

1. **草擬 SKILL.md**：訪談使用者釐清「這個 skill 該做什麼、何時觸發、期望輸出格式」，寫出草稿。
2. **建立測試案例**：把 2–3 個真實情境 prompt 存進 `evals/evals.json`（先只寫 prompt，斷言稍後補）。
3. **平行執行 with-skill / baseline 兩組 subagent**：同一個 prompt，一組帶 skill、一組不帶（或帶舊版 skill），結果分別存進 `<skill>-workspace/iteration-N/eval-X/`。
4. **評分與量化 benchmark**：用 `agents/grader.md` 的邏輯評估斷言，再跑 `scripts/aggregate_benchmark` 產出 `benchmark.json`/`benchmark.md`（pass rate、耗時、token 數，帶 mean ± stddev）。
5. **人工複核**：用 `eval-viewer/generate_review.py` 開一個本機頁面,讓使用者逐案比較 with-skill/baseline 的輸出並留意見回饋（`feedback.json`）。
6. **根據回饋改寫 skill**，重跑測試進下一個 iteration，反覆直到滿意。
7. **觸發描述優化（進階）**：用 `scripts/run_loop` 對 20 條「該觸發/不該觸發」的 query 做 60/40 train/test 分割,自動迭代 SKILL.md 的 `description` 欄位以提升觸發準確率。
8. **打包**：`scripts/package_skill.py` 把 skill 資料夾封裝成 `.skill` 檔供安裝/分享。

### 11.2 用法

```
/plugin install skill-creator@claude-plugins-official   # 已完成
/reload-plugins                                          # 套用後才會出現在可用 skills 清單
```

之後不需要手動呼叫，直接用自然語言描述需求即可觸發（例如「幫我做一個能檢查 PR 標題格式的 skill」、「幫我評測一下這個 skill 準不準」），skill-creator 會依 SKILL.md 描述自動判斷是否介入。

### 11.3 與 `superpowers:writing-skills` 的關係

本機同時裝了 `superpowers:writing-skills`（見上方比較），兩者目標高度重疊，但工具化程度不同：

| 面向 | `superpowers:writing-skills` | `skill-creator` |
|---|---|---|
| 理論框架 | 把「寫 skill」當成 TDD：先用 subagent 跑 baseline（RED）、寫 skill 讓 agent 通過（GREEN）、再收斂邊界情況（REFACTOR） | 同樣是草擬→測試→迭代的循環，但用「with-skill vs baseline 雙軌 subagent + 量化 benchmark」取代單純的 RED/GREEN 判讀 |
| 工具支援 | 純文件指引，沒有附帶腳本 | 附帶 `scripts/aggregate_benchmark`、`scripts/run_loop`（觸發描述優化）、`scripts/package_skill`、`eval-viewer/generate_review.py`（瀏覽器評測介面） |
| 觸發描述優化 | 沒有專門機制 | 有專門的 60/40 train/test 迭代流程，自動調整 `description` 用詞以降低「該觸發卻沒觸發」的漏觸發率 |
| 打包/分發 | 沒有 | `package_skill.py` 可直接產出 `.skill` 檔 |

兩者同時安裝時，若使用者提到「建立/改善 skill」，兩個 skill 的 description 都可能符合觸發條件。實務上可以讓 `skill-creator` 主導完整的迭代評測流程（因為它工具更完整），`writing-skills` 的 TDD 心法則可以當作補充的思維框架，不需要特別停用其中一個。

---

## 12. 團隊與多部門的 skill 治理

標記：✅ 官方文件明載（〈[Skills](https://code.claude.com/docs/en/skills.md)〉、〈[Manage Claude Code plugins for your organization](https://code.claude.com/docs/en/plugins/org.md)〉、〈[Extend Claude Code](https://code.claude.com/docs/en/features-overview.md)〉）　🛠 建議做法，不是官方流程。

情境：公司專案做 code review，**各部門各自把自己的 skill 放進專案**（假設放在 `.claude/skills/` 並一起提交）。官方沒有說這是錯的，但有幾個具體風險。

### 12.1 各自塞 skill 會發生什麼

| 問題 | 官方依據 | 對 code review 的後果 |
|---|---|---|
| **覆寫內建的 `/code-review`** | 專案 skill 與內建指令同名時，你的 skill 會取代內建指令（別名除外）✅ | 某個部門取名 `code-review`，其他人原本的內建流程就悄悄被換掉 |
| **描述重疊、互相競爭** | 描述模糊或重疊時，Claude 可能挑錯，或漏掉該用的 ✅ | 同一份 PR 會依觸發到哪個 skill 而用不同標準審，結果不穩定、難以稽核 |
| **context 成本累加** | 每個列出的 skill 每一輪都佔 context，不管有沒有用到；每個描述最多保留 1,536 字元 ✅ | N 個部門乘以數個 skill，常駐成本由所有人分攤；`/skill-doctor` 可看每個 skill 的成本 |
| **權限預先放行** | `allowed-tools` 會在 skill 執行那一輪免詢問放行工具；官方明說要審查提交進 repo 的 skill 的 `allowed-tools` ✅ | 任何部門的 skill 都可能預先放行 Bash 之類的工具，卻沒有人統一審 |
| **無擁有者、版本與發佈管道** | plugin marketplace 支援版本固定與 release channel ✅ | 專案內的 skill 隨程式碼走，沒有「誰負責、何時升級」 |

同名的情況：同一個目錄不能有兩個同名資料夾；放在不同子目錄的同名 skill 會**都載入**，但要用帶路徑的名稱呼叫（例如 `/apps/web:deploy`）✅；優先序是 enterprise > personal > project ✅。

### 12.2 建議結構

![多部門團隊的 skill 結構：公司層 plugin marketplace 由單一 owner 維護共同的 code-review 流程並用 managed settings 強制啟用；專案層前端、後端、資安的差異用帶 paths 條件的規則承接；強制層放 CI、hook 與權限設定](figures/claude-skills-governance-structure.svg)

- **共同流程只留一份**：用 plugin 發佈，plugin 的 skill 有命名空間（`/plugin-name:skill-name`），不會和別人同名衝突 ✅。
- **部門差異用規則承接，而不是另一個 review skill**：有 `paths:` 條件的規則與子目錄的 skill 都是按需載入 ✅（子目錄的 skill 在 Claude 讀或編輯該子目錄的檔案時才載入）；skill 本身也有 `paths` 欄位可限制啟用範圍 ✅。
- **重或少用的設成手動**：`disable-model-invocation: true`，描述不佔 context，也不會被自動挑中 ✅。
- **必須做的檢查別只靠 skill**：放進 CI、hook 或權限設定；skill 與 CLAUDE.md 只是請求 ✅。三層 code review 的比較見〈[Claude-Agent](Claude-Agent.md)〉。

### 12.3 想強制時用哪個設定

![想強制時用哪個設定：全公司一套用 extraKnownMarketplaces 加 enabledPlugins；只允許公司來源用 strictKnownMarketplaces 加 disableSideloadFlags；不准另放專案 skill 用 strictPluginOnlyCustomization；各部門不同設定要分別發給各群組；隱藏 skill 用 skillOverrides 但不影響 plugin；封鎖特定 plugin 用 enabledPlugins false](figures/claude-skills-governance-switches.svg)

| 目的 | 設定 | 注意 |
|---|---|---|
| 全公司都有同一套 | managed settings 的 `extraKnownMarketplaces` ＋ `enabledPlugins` | 使用者在自己的 scope 停用也擋不住，managed 優先 ✅ |
| 只允許公司的來源 | `strictKnownMarketplaces`（允許清單）＋ `disableSideloadFlags` | 只設允許清單卻漏掉 `{ "source": "skills-dir" }`，使用者放在 `.claude/skills/` 的**目錄型 plugin** 會停止載入；純 `SKILL.md` 不受影響 ✅ |
| 不准專案或個人另放 skill | `strictPluginOnlyCustomization`，可只鎖 `["skills"]` | 會讓現有的專案 skill 失效；要搭配上面兩項才完整 ✅ |
| 各部門不同設定 | 把設定分別發給各群組 | 所有 plugin 相關設定都套用到收到設定的每個人，沒有「依使用者或部門」的單一開關 ✅ |
| 隱藏某個 skill | `skillOverrides`（`on`／`name-only`／`user-invocable-only`／`off`） | **不影響 plugin 的 skill**；plugin 要用 `/plugin` 或 `enabledPlugins: false` ✅ |
| 封鎖特定 plugin | managed `enabledPlugins` 設為 `false` | 所有 scope 都擋，且從 marketplace 列表隱藏 ✅ |

另外：managed 設定只會從**一個來源**生效（server-managed、MDM、設定檔依序檢查），若要合併要設 `managedSourcesBehavior: "merge"` ✅。稽核可用 OpenTelemetry 的 `plugin_installed`、`plugin_loaded` 事件 ✅。

### 12.4 整頓步驟 🛠

![整頓多部門 skill 的六個步驟：盤點、分類、指定 owner、發佈成 plugin、鎖定來源、評測驗證，鎖定來源要等前面做完再開](figures/claude-skills-governance-steps.svg)

1. **盤點**：列出所有 review 相關 skill 的名稱、描述、擁有者、`allowed-tools`，用 `/skill-doctor` 看成本。
2. **分類**：重複的合併、部門專屬的改成規則、過期的刪除。
3. **指定一個 owner 與唯一入口**：其他部門以 PR 提需求，不自己另開 skill。專案內的 `.claude/` 可用 CODEOWNERS 要求審查（這是 GitHub 的功能，不是 Claude Code 的）。
4. **發佈成 plugin**：放在公司 marketplace，用 managed settings 強制啟用。
5. **鎖定來源**：`strictPluginOnlyCustomization` 等前面做完再開，否則現有專案 skill 會全部失效。
6. **用評測驗證**：拿真實 PR 比較整頓前後的審查結果與觸發是否正確（第 11 節的 `skill-creator` 可做觸發評測）。

### 12.5 取捨與限制

- **部門專屬的知識是合理需求**：問題不在「部門有自己的 skill」，而在「各自塞進同一個專案、重複實作 review 流程、沒有治理」。
- **強制條款會影響所有人**：先和各部門溝通再開。
- **我不清楚你們 repo 的實際結構**（例如是否 monorepo），以上是通用版；`strictPluginOnlyCustomization` 的實際影響要在測試環境先驗證 ⚠️。

---

## 13. 參考來源

- [GitHub - obra/superpowers](https://github.com/obra/superpowers)
- [GitHub - OthmanAdi/planning-with-files](https://github.com/othmanadi/planning-with-files)
- [GitHub - mattpocock/skills](https://github.com/mattpocock/skills)：README、`skills/productivity/grill-me/SKILL.md`、`skills/productivity/grilling/SKILL.md`、`skills/engineering/grill-with-docs/SKILL.md`（2026-11-11 讀取 `main`）
- Claude Code 官方〈[Extend Claude Code](https://code.claude.com/docs/en/features-overview.md)〉：user-only skill 的 context 成本、`skillOverrides`、skill 描述重疊的警告
- Claude Code 官方〈[Skills](https://code.claude.com/docs/en/skills.md)〉：skill 的位置、同名優先序、`allowed-tools`、`paths`、`skillOverrides`
- Claude Code 官方〈[Manage Claude Code plugins for your organization](https://code.claude.com/docs/en/plugins/org.md)〉：`extraKnownMarketplaces`、`enabledPlugins`、`strictKnownMarketplaces`、`strictPluginOnlyCustomization`、`disableSideloadFlags`
- [Plugins reference - Claude Code Docs](https://code.claude.com/docs/en/plugins-reference)
- 本機 `superpowers` plugin 原始碼：`~/.claude/plugins/cache/claude-plugins-official/superpowers/6.1.1/`（`.claude-plugin/plugin.json`、`hooks/hooks.json`、`skills/*/SKILL.md`）
- 本機 `skill-creator` plugin 原始碼：`~/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator/SKILL.md`
