# Agentic Engineering

## Graph Engineering：將 Agent 設計成可控的狀態圖

**Graph Engineering** 是把 Agent 的執行流程明確建模為「節點（nodes）、狀態（state）與轉移（edges）」的工程方法。它不是只寫一段 prompt 讓模型自由決定下一步，而是先定義：目前位於哪個狀態、哪些工具可用、何時可以重試、何時必須升級或停止。

它特別適合多步驟、長時間、需人工核准或有成本／安全限制的任務，例如程式修復、CI 排障、文件審查與 coredump 分析。

| 元素 | 角色 | 設計問題 |
|---|---|---|
| Node | 一個明確工作單位，例如擷取證據、規劃、呼叫工具、驗證、產出報告 | 這一步唯一要負責什麼？輸入與輸出是什麼？ |
| Edge | 節點間的條件式轉移 | 哪些條件能進下一步？哪些條件應停止或升級？ |
| State | 跨節點保存的結構化工作記憶 | 哪些事實、證據、預算和未解問題必須持久化？ |
| Guard | 不交給模型任意決定的政策邊界 | 是否可執行工具？是否超出成本、權限或風險上限？ |
| Terminal state | 明確結束條件 | 已完成、需要人工、預算耗盡或不可恢復失敗時要怎麼結束？ |

### 流程圖

![圖：Graph Engineering 流程——Plan、Guard、Act、Observe、Validate 與重試／升級迴圈](figures/agentic-engineering-graph-flow.svg)

### Loop Engineering 與 Graph Engineering 比較

兩者都處理 Agent 的「下一步」，但工程層次不同：Loop Engineering 關心單一 agent 如何反覆思考與行動；Graph Engineering 關心整個 workflow 有哪些節點、狀態與允許的轉移。

| 面向 | Loop Engineering | Graph Engineering |
|---|---|---|
| 核心問題 | Agent 如何反覆思考、行動、觀察與修正？ | 系統有哪些狀態、節點與可允許的轉移？ |
| 基本結構 | `Plan → Act → Observe → Reflect → 再試` | `Node + State + Edge + Guard + Terminal state` |
| 重點 | 單一 Agent 的迭代品質與停止條件 | 多步驟 workflow 的可控性、可恢復性與可稽核性 |
| 分支控制 | 常由模型依當前結果決定 | 常由明確條件、政策或程式規則決定 |
| 狀態保存 | 常偏向 conversation、memory、summary | 外部結構化 state，例如 DB、JSON 或 event log |
| 適合任務 | 探索、除錯、研究、反覆修程式 | CI、審批、客服、coredump、部署等正式流程 |
| 主要風險 | 無限循環、重複工具呼叫、context 膨脹 | state schema 複雜、圖設計過度僵化 |

可用下列方式理解兩者關係：

```text
Graph Engineering：決定 Agent 可以走哪些路。
Loop Engineering ：決定 Agent 在每一條路上如何反覆推理與行動。
```

以 coredump 分析為例：

```text
Graph（外層）：
ingest → normalize → fingerprint lookup
      → known report
      或 model triage → source search → deep analysis / human review

Loop（內層，在 model triage 或 deep analysis 節點中）：
Plan → 讀取 facts → 判斷證據缺口 → 查詢 source → 驗證 → 產出結論
```

正式系統宜採「外層 Graph、內層 Loop」：Graph 控制去重、預算、升級、人類核准與終止條件；Loop 讓模型在單一分析節點內反覆使用受控工具補足證據。只有 Loop 容易造成不受控的重試；只有 Graph 則會使每個節點的調查能力過度僵硬。

### 與 Context、Harness、Loop Engineering 的關係

| 面向 | 解決的問題 | Graph Engineering 如何補強 |
|---|---|---|
| Context Engineering | 讓模型取得正確且足量的資訊 | State 決定哪些已驗證事實、摘要與 evidence ID 要帶入下一個 node |
| Harness Engineering | 工具、權限、hooks、sandbox 與驗證 | Guard 與 edge 把工具可用條件、核准與失敗處理寫成可執行流程 |
| Loop Engineering | Plan → Act → Observe 的反覆迴圈 | Graph 為迴圈加上狀態、分支、最大迭代次數與明確終止條件 |

Graph Engineering 不取代前三者；它把三者編排為可以測試、觀測與恢復的 workflow。

### 設計原則

1. **Node 單一職責**：一個 node 只做一件可驗證的事，例如「抽取 facts」或「驗證 backtrace」，不要同時規劃、執行和發布結果。
2. **State 結構化且可版本化**：保存 facts、evidence IDs、open questions、tool outputs 摘要、預算與決策紀錄；不要把完整歷史只留在對話上下文。
3. **Edge 以明確條件決定**：例如 `symbols_missing`、`confidence < 0.7`、`budget_remaining == 0`；不要只依模型文字敘述猜測流程。
4. **所有循環都要有上限**：設定最大工具呼叫數、最大重試數、timeout 與 token budget，避免 agent 無限循環。
5. **先驗證再轉移**：工具輸出先經 schema、權限、品質或 evidence 檢查，再更新 state 與進入下一個 node。
6. **人工核准是節點，不是例外**：高風險寫入、成本升級、部署與不可逆操作應進入 `awaiting_approval` state，可在核准後恢復。
7. **記錄每條轉移**：保存 node、edge condition、工具版本、輸入摘要、輸出 evidence、耗時與成本，才能重放與評測。

### 以 coredump 分析為例

```text
ingest
  → normalize_artifacts
  → fingerprint_lookup
  → known_root_cause? ──是→ report
                     └─否→ model_triage
                                → evidence_sufficient? ──是→ report
                                                    └─否→ source_search
                                                           → deep_analysis_or_human_review
```

在此例中，fingerprint 去重、每案預算、artifact 存取範圍與深度分析核准應由 graph 的 guard / edge 控制；模型只在 `model_triage` 或 `deep_analysis` node 中負責判讀證據。

建構 AI Agent 系統的工程學科，涵蓋三個核心層次：**Context Engineering**、**Harness Engineering**、**Loop Engineering**。

---

## 三層架構總覽

```
┌─────────────────────────────────────────┐
│           Loop Engineering              │  ← 決定「怎麼跑」
│   (agent 迴圈、排程、子 agent 編排)       │
├─────────────────────────────────────────┤
│          Harness Engineering            │  ← 決定「能做什麼」
│   (工具、權限、hooks、沙箱、MCP)          │
├─────────────────────────────────────────┤
│          Context Engineering            │  ← 決定「看到什麼」
│   (prompt、RAG、memory、token 預算)      │
└─────────────────────────────────────────┘
                    ↑
               LLM 在這裡
```

---

## Context Engineering（情境工程）

**核心問題：模型「看到什麼」？**

控制進入 LLM context window 的所有資訊。給 LLM 的 token 每一個都值錢，目標是最大化信噪比。

| 責任範圍 | 範例 |
|---|---|
| System prompt 設計 | 角色定義、行為規範 |
| 資訊選取 | RAG 檢索哪些文件 |
| Memory 管理 | 哪些過去記憶值得帶入 |
| Token 預算 | 壓縮 / 截斷策略 |
| 工具結果格式 | tool_result 如何呈現給模型 |

> 背景：「Context Engineering」一詞由 Shopify CEO Tobi Lütke 於 2025 年發文推廣，逐漸取代「prompt engineering」成為主流說法。

### Claude Code 實作：上下文來源與優先順序

Claude Code 的 context window 並非單一來源，而是多個獨立機制在不同時機拼接而成。實際盤點如下：

**固定於 session 開頭載入（不論用不用得到）**

| 來源 | 實際路徑 | 備註 |
|---|---|---|
| System prompt + 環境資訊 | 內建 | 工作目錄、平台、shell、git 狀態 |
| Auto Memory 索引 | `~/.claude/projects/<project>/memory/MEMORY.md` | 只載前 200 行或 25KB，細節主題檔另外 on-demand |
| CLAUDE.md（全部層級） | 見下方優先順序表 | 由檔案系統根目錄往工作目錄逐層載入 |
| MCP 工具「名稱」 | 已掛載的 MCP servers | 只有名稱，完整 schema 靠 ToolSearch 延遲載入 |
| Skills「一行描述」 | `.claude/skills/<name>/SKILL.md` frontmatter | 完整內容不載入，除非被呼叫或判定相關 |
| 使用者層 rules | `~/.claude/rules/**/*.md` | 無 `paths:` 條件的規則 |

**依需求 on-demand 載入（省 token 的關鍵）**

| 來源 | 觸發時機 |
|---|---|
| MCP 完整工具 schema | 透過 ToolSearch 實際要呼叫該工具時 |
| Skill 完整內容 | 被 `/skill-name` 呼叫或 Claude 判斷相關時 |
| 路徑限定 rules（`.claude/rules/` 帶 `paths:`） | 讀取到符合 glob 的檔案時 |
| Memory 主題檔（非 MEMORY.md 索引本身） | Claude 判斷需要細節時才讀 |
| 子目錄的巢狀 CLAUDE.md | 讀取到該子目錄下的檔案時 |
| Subagent 回傳 | 只回傳最終摘要文字，過程中讀的檔案內容留在 subagent 自己的 context，不外流 |

**預設不會進入 context**：其他 settings 值（model、theme 等）、subagent 內部對話過程、hook 的 stdout（只有 `additionalContext` 欄位會被注入）、未使用到的 MCP 工具 schema、未觸發的 skills 完整內容。

**相對優先順序**——這是最容易搞混的地方，兩套機制規則不同：

| 機制 | 規則 | 優先順序（高→低） |
|---|---|---|
| `settings.json` | **覆寫制**：高優先權完全取代低優先權 | managed（組織）> 命令列參數 > local > project > user；例外：`permissions` 的 deny 規則是跨層級合併，不會被覆寫掉 |
| `CLAUDE.md` | **疊加制**：所有層級「全部串接」進 context，不是誰蓋過誰 | 載入順序：根目錄 → 工作目錄逐層 `CLAUDE.md`，同層再讀 `CLAUDE.local.md` |
| Skills（同名衝突時） | 覆寫制：只啟用最高優先權那一份 | project > user（個人）> plugin 內建 |

> 關鍵易錯點：**CLAUDE.md 不是「覆寫」而是「疊加」**——專案的 `CLAUDE.md` 不會取代使用者層的 `~/.claude/CLAUDE.md`，兩者內容都會進 context，這跟 `settings.json` 的覆寫語意完全相反，寫多層規則時要注意重複或矛盾的敘述會一起被塞進去，而不是自動被「更精確的那層」蓋掉。

### 應用實例

**1. System prompt 設計：用 CLAUDE.md 定義穩定的角色與規範**

專案根目錄的 `CLAUDE.md` 寫入程式碼風格、commit 慣例、禁止事項等長期不變的規則，每次對話自動載入，不用每輪重新提醒模型「請用 tab 縮排」「不要加註解」。這是把「行為規範」這種高頻復用資訊固定進 context 的做法，跟 harness 層「能不能執行某指令」是不同層次的問題。

**2. 資訊選取：用 Grep/Glob 精準檢索取代整包塞進 context**

需要找某個函式定義時，用 `Grep` 搜特定 symbol 只取回命中片段，而非把整個 100KB 的檔案讀進來；`head_limit` 進一步限制回傳筆數。這是「RAG 檢索哪些文件」在程式碼場景的具體實踐——選對資訊比選多資訊重要，目標是最大化信噪比而非覆蓋率。

**3. Memory 管理：只帶入跟當前任務相關的記憶**

Auto memory 分兩層：`MEMORY.md` 索引的前 200 行或 25KB **每次啟動都會載入**；詳細的主題檔（如 `user_role.md`、`feedback_testing.md`）不在啟動時載入，Claude 判斷需要時才用一般檔案工具讀取。例如使用者是資料科學家在查 logging，Claude 只需去讀相關的 user／feedback 主題檔，不必讀跟前端偏好無關的舊記錄。因此索引要保持精簡，細節放進主題檔——這避免 context 被不相關的歷史資訊稀釋。完整載入規則見〈[Claude-Context](Claude-Context.md)〉。

**4. Token 預算：Subagent 摘要回傳而非原始輸出直通主對話**

派 subagent 去讀 20 個檔案做程式碼審查時，主對話只收到 subagent 最後整理的摘要文字，20 個檔案的原始內容留在 subagent 自己的 context 裡不外流。這是「壓縮 / 截斷策略」的具體做法：把大量中間資料隔離在子任務層，只把結論性資訊帶回主 context。

**5. 工具結果格式：控制 tool_result 呈現方式**

同樣是搜尋，`output_mode: "files_with_matches"` 只回傳檔案路徑清單，`"content"` 才回傳完整命中行；需要判斷「這功能有沒有被用到」選前者就夠，需要看實際程式碼邏輯才選後者。呈現格式本身就是一種 context 設計決策，選錯格式會讓模型看到過多無關雜訊或看不到關鍵細節。

---

## Harness Engineering（執行環境工程）

**核心問題：模型「活在什麼環境裡」？**

Agent 的基礎設施層，定義工具、權限、Hooks 與沙箱邊界。以 Claude Code 為例，Harness 由以下機制組成：

| 責任範圍 | 範例 | Claude Code 對應機制 |
|---|---|---|
| 工具定義與權限 | 允許哪些 Bash 指令、哪些檔案可讀寫 | `settings.json` 的 `permissions.allow/deny`（支援 glob，如 `Bash(npm *)`、`Read(.env*)`） |
| Hooks 自動化 | pre-tool / post-stop 觸發腳本 | `PreToolUse`、`PostToolUse`、`UserPromptSubmit`、`SessionStart/End`、`Stop`、`SubagentStart/Stop` 等生命週期事件 |
| 沙箱與安全邊界 | 防止破壞性操作（`rm -rf`、force push） | permission mode（`default` / `acceptEdits` / `plan` / `auto`）+ deny rules |
| 設定管理 | settings.json、環境變數 | 四層 scope：managed（組織）> local > project > user，逐層覆寫 |
| MCP 整合 | 掛載外部工具伺服器（DB、瀏覽器、API） | `.mcp.json`，可依 subagent 做工具隔離 |
| 能力封裝 | 把重複工作包成可重用單元 | Skills（`.claude/skills/`）、Subagents（`.claude/agents/`）、Plugins |

> 注意：自動化行為（「每次 X 發生時執行 Y」）必須透過 harness hooks 設定，無法單靠模型記憶或偏好設定達成——harness 才是真正攔截與執行的層次。

### Claude Code 實作：優先順序

Harness 層常見多條規則同時命中同一個動作，實際判定順序：

| 情境 | 規則 | 說明 |
|---|---|---|
| `deny` 與 `allow` 同時命中 | **deny 絕對優先，跟規則寫得多精確無關** | 評估順序固定為 `deny → ask → allow`，取第一個命中的結果。例如 `Bash(aws *)` 設 deny，即使另有更精確的 `Bash(aws s3 ls)` allow，照樣被擋 |
| 多個 hooks 同時命中同一事件（如兩個 `PreToolUse` 都匹配同一個 Bash 呼叫） | **全部平行執行到完成，取「最嚴格」的結果** | 不是循序執行、不是先跑先贏；決策順序一樣是 `deny → defer → ask → allow`，任一 hook 回傳 deny，其他 hook 不會因此被跳過，但最終結果會是 deny |
| Permission mode：CLI 的 `--permission-mode` vs `settings.json` 的 `defaultMode` | **未明確定義覆寫關係**，CLI 只設定啟動時的初始模式，之後可用 `Shift+Tab` 隨時切換 | 兩者不是嚴格的優先權關係，比較像「初始值 vs 執行中可變更的狀態」 |
| MCP 工具名稱衝突（兩個 server 掛同名工具，或撞到內建工具名） | **官方未文件化**——只有 server 本身重複掛載時的 scope 順序有定義（local > project > user > plugins > claude.ai connectors） | 工具層級的同名衝突屬於未定義行為，實務上應避免讓不同 MCP server 掛同名工具 |

> 與 Context Engineering 的 CLAUDE.md「疊加制」不同，Harness 層的 permission/hook 判定是**收斂到單一最嚴格結果**——多條規則不會全部生效，而是取最保守的那一個，這是安全邊界該有的設計（寧可誤擋，不可誤放）。

### 應用實例

**1. Hook：強制 commit 前跑 lint**

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [{ "type": "command", "command": "npm run lint" }]
      }
    ]
  }
}
```
lint 失敗時回傳非 0 exit code，Claude Code 會阻擋該次 commit 並把錯誤訊息回饋給模型，模型可自行修正後重試——這是「harness 主動攔截」，而不是靠提示詞提醒模型記得要 lint。

**2. 權限邊界：禁止碰敏感檔案、限制危險指令**

```json
{
  "permissions": {
    "deny": ["Read(.env*)", "Bash(rm -rf*)", "Bash(git push --force*)"],
    "allow": ["Bash(npm *)", "Bash(git *)", "Edit(src/**)"]
  }
}
```
即使模型「想」讀取 `.env` 或強制推送，harness 層會直接擋下，安全邊界不依賴模型自律，而是基礎設施層的硬限制。

**3. Subagent 隔離：把高風險 / 高耗 token 任務關進獨立 context**

例如審查用的 subagent 只授予 `Read`、`Grep`、`Glob` 三個唯讀工具，且擁有獨立 context window，審查完只回傳摘要給主 agent——既避免大量檔案讀取污染主對話的 context 預算，也天生阻絕誤寫入的風險，這是 harness 層的權限設計，而非 loop 層的編排問題。

**4. MCP 整合：外部能力即插即用而非寫死在 prompt 裡**

專案掛載 `postgres` MCP server 後，Agent 直接呼叫其暴露的 `query` 工具存取資料庫，不需要自己拼 SQL 連線邏輯。「這個 agent 能不能碰資料庫」是 harness 決定的事（掛不掛載這個 MCP server、給不給對應權限），而不是靠 prompt 寫「請不要亂改資料庫」去約束模型。

**5. Plugin 打包分享：讓 Harness 設定可版本化、可分發**

把一組 skills + hooks + MCP 設定打包成 plugin（`.claude-plugin/plugin.json`），團隊內以 marketplace 分享安裝，確保每個工程師本地的 harness 一致，不會出現「我的 Claude 會擋，你的不會」的落差——這是把 Harness Engineering 的產出從單機設定變成團隊共享資產。

---

## Loop Engineering（迴圈工程）

**核心問題：模型「如何迭代」？**

設計 Agent 的推理-行動-觀察迴圈，以及多 Agent 協作流程。

| 責任範圍 | 範例 |
|---|---|
| Think → Act → Observe 節奏 | 何時繼續 vs 暫停等人 |
| 錯誤恢復 | 工具失敗後如何重試或改路 |
| 子 Agent 編排 | 何時 spawn / fork agent |
| 定時排程 | cron-based 自動觸發 |
| 上下文壓縮點 | 長對話何時 summarize |

### Claude Code 實作：優先順序

Loop 層跟 Context / Harness 不同——這裡多數機制是**互相獨立的並行系統，而非有明確覆寫關係的優先序**。整理如下，刻意標注哪些真的有官方文件定義的優先順序、哪些只是「看起來像但其實沒有」：

| 情境 | 是否有明確優先順序 | 說明 |
|---|---|---|
| `ScheduleWakeup`（動態排程）vs `CronCreate`（固定排程）同時存在 | **沒有**，兩者是獨立子系統 | 排程器每秒檢查一次到期任務，以低優先權排入佇列；兩套機制不互相搶佔，只是剛好都在等 |
| 使用者傳新訊息 vs 排程任務觸發時機重疊 | **隱含使用者優先**，但非明文規定 | 官方文件只說「排程 prompt 在你的回合之間觸發，不會打斷 Claude 正在輸出的回應」，可推斷使用者輸入不會被排程任務打斷，但沒有寫成正式的優先權規則 |
| Foreground vs Background subagent 同時跑 | **沒有資源優先權**，各自獨立執行 | Foreground 會擋住主對話直到完成，background 則讓你繼續操作；兩者不互相搶資源、也不互相阻擋 |
| `Stop` hook 想要求繼續 vs 模型自己判斷任務已完成 | **未文件化** | 官方只定義 `Stop` 何時觸發（Claude 講完話時），沒有明確定義 hook 回傳阻擋決策時，跟模型自身完成判斷之間誰蓋過誰——實務上應假設 hook 的 block 決策會生效，但這是推論而非官方保證 |

> 跟 Harness 層「收斂到單一最嚴格結果」不同，Loop 層的多數機制設計上就是要**並行不衝突**，所以與其問「誰的優先權比較高」，更準確的問法是「這兩個機制有沒有互相影響的必要」——多數情況答案是沒有，各跑各的。真正需要謹慎設計的是唯一有隱含優先序但未寫死的那條：使用者中斷 vs agent 正在跑的迴圈，這也是為什麼不該用忙等（polling loop）去等背景任務，而要依賴通知機制。

### 應用實例

**1. 動態排程：讓 agent 自己決定下次醒來的時間**

用 `/loop`（無固定間隔）搭配 `ScheduleWakeup`，模型依「正在等的東西」自行決定下一次檢查的間隔——輪詢 CI 用 60~270 秒（留在 5 分鐘 prompt cache 窗口內），單純空轉待命則拉長到 1200~1800 秒。這是 loop 層在做「節奏設計」，跟 harness 層「有沒有權限跑指令」是完全不同的問題。

**2. 定期排程：cron-based 自動觸發**

```
schedule: 每天 09:00 執行 /babysit-prs
```
用 `CronCreate` 建立排程 agent，固定時間點自動醒來執行任務（如巡查未合併的 PR、跑每日報表）。跟第 1 點的差異在於：這裡是「固定時刻觸發」而非「模型自行判斷該等多久」，適合真正週期性、與外部事件無關的任務。

**3. 子 Agent 平行編排：獨立任務同時派工**

審查一個大型 PR 時，同時 spawn 三個 subagent 分別檢查「型別安全」「測試覆蓋率」「安全漏洞」，三者互不依賴、無共享狀態，可在同一輪並行呼叫後統一匯總結果，而非依序執行三次、白白拉長總時長。這是 loop 層決定「任務怎麼拆、怎麼併」；子 agent 各自能碰哪些工具則是 harness 層的事。

**4. 錯誤恢復：工具失敗後的重試路徑**

Bash 指令因 lint hook（harness 層設定）被擋下後，loop 不是直接放棄，而是讀取 hook 回傳的錯誤訊息、修正程式碼、重新嘗試同一個 tool call；連續失敗達門檻才升級為向使用者求助，而非無限重試。這條「失敗 → 修正 → 重試 → 升級」路徑正是 loop engineering 的核心產出。

**5. 上下文壓縮點：長對話何時 summarize**

長任務執行到一半，主 context 快被工具輸出塞滿時，loop 主動把「已確認的中間結論」寫入 memory 或 plan 文件，再讓系統自動壓縮舊訊息，確保後續推理不因摘要遺漏關鍵決策而失控——這呼應了 context engineering 的 token 預算問題，但「什麼時候觸發壓縮、觸發後如何接續任務」是 loop 層要解決的節奏問題。

**6. 事件驅動迴圈：repo 更新自動觸發學習**

Claude Code 沒有內建「自動監看 repo 並學習」的功能，但可以用官方 `claude-code-action`（GitHub Action）拼出事件驅動的 loop：PR merge 到 main 時觸發，而非固定時間輪詢。

```yaml
# .github/workflows/claude-learn.yml
on:
  pull_request:
    types: [closed]
    branches: [main]

jobs:
  learn-from-merge:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            檢視這次 merge 的 diff，若引入新的程式碼慣例或該記住的坑，
            更新 CLAUDE.md 對應段落並寫一條 project 記憶。
            改動請開新 branch 提 PR，不要直接推 main。
```

跟第 2 點「定期排程」的差異在於觸發條件：這裡是「PR merge」這個外部事件本身驅動迴圈，比固定時間輪詢更即時、也更省——這是 loop 層在做「事件 vs 時間」的節奏選擇；而「能不能直接改 main」則是交給 harness 層的權限設定（只准開 PR）去把關，「該記住哪些慣例」才是 context 層的篩選問題。三層在這個例子裡缺一不可。

---

## 三者關係與分工

| 層次 | 一句話定義 | 缺失時的症狀 |
|---|---|---|
| Context | 模型的**輸入品質** | 模型做出錯誤決策、幻覺頻繁 |
| Harness | 模型的**執行邊界** | agent 越權操作、自動化失效 |
| Loop | 模型的**任務節奏** | 任務失控、無法判斷完成條件 |

三者缺一不可：再好的 context 放在設計糟糕的 loop 裡一樣失控；再穩的 harness 沒有 context engineering 支撐也會讓模型做出錯誤決策。

---

## 延伸主題：持續學習（Continuous Learning）橫跨三層

「Claude Code 如何持續學習」不是第四層，而是一個**橫跨三層的複合能力**——模型權重本身不會被重新訓練，「學習」指的是外部狀態的持久化與跨 session 累積：

| 層次 | 在持續學習裡扮演的角色 | 對應機制 |
|---|---|---|
| Context | 決定「該記住什麼、怎麼呈現」 | Auto Memory（`user`/`feedback`/`project`/`reference` 四型）、`CLAUDE.md` |
| Harness | 決定「誰有權限寫回、能碰到什麼」 | 只准開 PR 不准直推 main 的權限設定、Skills 封裝 |
| Loop | 決定「什麼時候觸發學習」 | 事件驅動（Loop Engineering 應用實例 6）vs 定期排程（應用實例 2） |

具體落地方式見各層的應用實例：Context 層的「Memory 管理只帶入相關記憶」、Loop 層的「事件驅動迴圈：repo 更新自動觸發學習」。三者合起來才是一套完整的「repo 更新 → 自動學習」pipeline，缺任何一層都不成立：只有 context 沒有 loop，學到的東西不會自動被觸發寫入；只有 loop 沒有 harness，agent 可能直接改壞 main；只有 harness 沒有 context 層的篩選邏輯，寫回的東西會是雜訊而非真正有用的規範。

---

## 統一稱呼

目前業界**尚無單一通用術語**涵蓋三者，最接近的說法：

| 稱呼 | 使用場合 |
|---|---|
| **Agent Engineering** | 最常見的廣義說法 |
| **AI Systems Engineering** | 偏學術／基礎設施視角 |
| **Agentic AI Infrastructure** | 強調自主運作的底層建設 |

Harness / Loop 的術語在不同框架（LangGraph、Claude Code、AutoGen 等）各自有不同命名，跨社群共識仍在演化中。撰寫文件時建議以 **Agent Engineering（三層架構：Context / Harness / Loop）** 方式自行定義。
