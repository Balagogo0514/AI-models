# Claude Code Skill/Plugin 比較：superpowers vs planning-with-files

> 資料整理時間：2026-07-12（來源：本機已安裝 plugin 設定、官方 `claude-plugins-official` marketplace 目錄、GitHub 專案文件、Claude Code 官方文件）

## 1. 環境現況

本機（`G:\ClaudeCode\AI-models`）目前只安裝了一個 plugin：

| Plugin | 來源 | 版本 | 狀態 |
|---|---|---|---|
| `superpowers` | 官方 `claude-plugins-official` marketplace | 6.1.1 | 已安裝 |
| `planning-with-files` | 第三方（[OthmanAdi/planning-with-files](https://github.com/othmanadi/planning-with-files)），非官方 marketplace | — | **未安裝** |

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

## 5. 兩者定位本質不同

| 面向 | superpowers（`writing-plans` / `executing-plans`） | planning-with-files |
|---|---|---|
| 核心目的 | 把 spec 轉成**嚴謹的實作計畫**（TDD、bite-sized task、精確檔案路徑），交給 subagent 或 session 逐步執行 | 維持**跨 session 的持久工作記憶**，防止 context 遺失、崩潰、`/clear` 後斷線 |
| 檔案結構 | 單一計畫檔：`docs/superpowers/plans/YYYY-MM-DD-<feature>.md` | 三個檔案並存：`task_plan.md`（進度）、`findings.md`（發現）、`progress.md`（執行日誌），可用 slug 目錄（`.planning/YYYY-MM-DD-slug/`）隔離平行任務 |
| 觸發機制 | 手動 Skill 呼叫，由 `using-superpowers` meta-skill 判斷「只要有 1% 可能相關就必須呼叫」 | IDE **hooks** 自動化：`SessionStart`/`UserPromptSubmit` 自動重新注入計畫、`PreToolUse` 執行前複誦、`PostToolUse` 提醒更新進度、`Stop` hook 擋掉未完成就結束 session |
| 崩潰恢復 | 沒有專門機制——計畫檔是一般 markdown，人工重讀即可 | 有專門「catchup report」：比對 session store 時間戳，抓出崩潰/`/clear` 後遺漏的對話並自動補齊 |
| 多 agent 協作 | 靠 `subagent-driven-development` 手動派工 | 內建 ledger 檔，支援多 agent 共享狀態 |
| 支援平台 | Claude Code（及 superpowers 支援的其他 CLI） | 18+ IDE，分三級支援（Enhanced/Standard），含 Claude Code、Cursor、Codex、Gemini CLI 等 |

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

## 8. 兩者會衝突嗎？

目前環境不會衝突（`planning-with-files` 未安裝）。但若兩個都裝上，有兩個實際風險：

1. **重複觸發**：superpowers 的「1% 相關就必須呼叫」規則，可能讓同一個多步驟任務同時觸發 `writing-plans` 和 `planning-with-files` 的 `/plan` 流程，產生兩份格式、位置都不同的計畫檔，搞不清哪份才是真的計畫。
2. **Hook 疊加**：`planning-with-files` 掛的 `PreToolUse`/`PostToolUse`/`Stop` hooks 會主動複誦、提醒、甚至擋停；superpowers 沒有 hook，純 skill 邏輯。兩者疊加時會同時收到雙重叨念。

**建議分工**（若真要兩個並用）：讓 superpowers 的 `writing-plans` 負責生成計畫內容（把 spec 拆解成精確任務），把 `planning-with-files` 定位成純粹的崩潰恢復/跨 session 記憶層，不讓它另開一份計畫格式——但這需要在 `CLAUDE.md` 明確分工，兩者預設不會自動協調。

---

## 9. 一般程式開發工作該用哪個？

**預設用 superpowers 就好**——已安裝、官方支援，`writing-plans → executing-plans/subagent-driven-development` 涵蓋「spec 拆解 → TDD 逐步實作 → 審查」的完整循環，足以應付大多數功能開發任務。

`planning-with-files` 的價值集中在**長時程、跨多個 session、容易被 `/clear` 或崩潰打斷**的情境（連續多天的大型 agent 任務、多 agent 協作）。一般單次或幾個 session 內能完成的開發用不到它的崩潰恢復機制，硬裝反而增加 hook 疊加、雙重計畫檔的複雜度。

只有當你發現**常常因為 context 被清掉或跨 session 而搞丟進度**時，才值得額外裝 `planning-with-files`。

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

## 12. 參考來源

- [GitHub - obra/superpowers](https://github.com/obra/superpowers)
- [GitHub - OthmanAdi/planning-with-files](https://github.com/othmanadi/planning-with-files)
- [Plugins reference - Claude Code Docs](https://code.claude.com/docs/en/plugins-reference)
- 本機 `superpowers` plugin 原始碼：`~/.claude/plugins/cache/claude-plugins-official/superpowers/6.1.1/`（`.claude-plugin/plugin.json`、`hooks/hooks.json`、`skills/*/SKILL.md`）
- 本機 `skill-creator` plugin 原始碼：`~/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator/SKILL.md`
