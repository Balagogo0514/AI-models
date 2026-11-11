# 如何建立公司內部 plugin：skill、agent、MCP 與 local knowledge

> 資料來源：Claude Code 官方〈[Create a Claude Code plugin](https://code.claude.com/docs/en/plugins/create.md)〉、〈[Add components to a plugin](https://code.claude.com/docs/en/plugins/components.md)〉、〈[Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md)〉、〈[Create a marketplace](https://code.claude.com/docs/en/plugins/marketplace-reference.md)〉（2026-11-11 讀取）；組織強制啟用見〈[Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org.md)〉。
> 更新日期：2026-11-11
>
> 標記：✅ 官方文件明載　🛠 建議做法，非官方流程　⚠️ 未驗證或需實測
>
> 本文是 Claude Code 的做法；claude.ai 與 Cowork 載入的元件子集不同（例如有 `bin/` 的 plugin 不會安裝），細節見官方的 component support table。

---

## 一、先給答案

| 問題 | 簡短回答 |
|------|----------|
| 能把 skill、agent、MCP 都包進同一個 plugin 嗎？ | **可以。** plugin 是一個目錄，裡面可以有 skills、agents、hooks、MCP servers，加上一個 `plugin.json`；沒有任何元件是必要的 ✅ |
| 怎麼命名？ | plugin 的 skill 與 agent 自動加上 plugin 名稱當前綴，例如 `/acme-toolkit:code-review`，不會和別人同名衝突 ✅ |
| local knowledge 放哪？ | **小而穩定**的放 skill 的輔助檔；**大、常改、要搜尋**的用 MCP 服務；**不能**放 plugin 根目錄的 `CLAUDE.md`，它不會被載入 ✅ |
| 公司有很多份 markdown，怎麼放？ | **依「任務」分組，不依「檔案」分組**：一個 skill 掛多份 markdown；規則放 `CLAUDE.md`／rules，大型文件庫用 MCP 檢索服務（見第八節）✅ |
| 怎麼測試？ | `claude plugin validate`、`claude --plugin-dir`、`/reload-plugins`、`/plugin`、`/mcp`、`claude plugin eval` ✅ |
| 怎麼全公司推？ | 放進公司 marketplace，再用 managed settings 的 `extraKnownMarketplaces` ＋ `enabledPlugins` 強制啟用 ✅ |

---

## 二、目錄結構

![公司內部 plugin 的目錄結構與載入後的名稱：skill 是 /plugin名:目錄名，agent 是 @agent-plugin名:agent名，MCP 是 plugin:plugin名:server名，hook 載入後就在事件上觸發，根目錄的 CLAUDE.md 不會載入](figures/claude-plugin-structure.svg)

```text
acme-toolkit/
├── .claude-plugin/
│   └── plugin.json          # 只有它放在 .claude-plugin/ 裡
├── skills/
│   ├── code-review/
│   │   ├── SKILL.md
│   │   └── checklist.md     # skill 的輔助檔
│   └── onboarding/SKILL.md
├── agents/
│   └── security-reviewer.md
├── .mcp.json                # 內部系統與知識庫
├── hooks/hooks.json         # 必須強制的檢查（可選）
└── scripts/                 # hook 呼叫的腳本
```

> **最常見的錯誤** ✅：`.claude-plugin/` 裡**只能放 `plugin.json`**，其他元件放在 plugin 根目錄；放進 `.claude-plugin/` 的元件不會載入。另外，plugin 的根目錄是它自己的目錄，不是 `~/.claude/` 本身。

| 元件 | 預設位置 | 載入後的名稱 |
|------|----------|--------------|
| manifest | `.claude-plugin/plugin.json` | — |
| skill | `skills/<名稱>/SKILL.md` | `/<plugin>:<目錄名>` |
| agent | `agents/*.md` | `<plugin>:<name>`，可用 `@agent-<plugin>:<name>` 明確呼叫 |
| MCP server | `.mcp.json` | `/mcp` 顯示 `plugin:<plugin>:<server>`；工具名稱是 `mcp__plugin_<plugin>_<server>__<tool>` |
| hook | `hooks/hooks.json` | 無前綴 |
| 其他 | `commands/`（舊格式）、`.lsp.json`、`output-styles/`、`workflows/`、`bin/`、`settings.json` 等 | 見官方 |

---

## 三、manifest 與 userConfig

只有 `name` 必填；沒有 manifest 也能載入，但公司內部 plugin 建議寫上描述、版本與設定。

```json
{
  "name": "acme-toolkit",
  "version": "1.0.0",
  "description": "公司內部的 review、onboarding 與知識庫工具",
  "author": { "name": "平台團隊" },
  "userConfig": {
    "kb_url": {
      "type": "string",
      "title": "知識庫網址",
      "description": "內部知識庫 MCP 服務的 URL"
    },
    "kb_token": {
      "type": "string",
      "title": "知識庫 token",
      "description": "存取知識庫的 token",
      "sensitive": true
    }
  }
}
```

- **名稱規則** ✅：用 kebab-case，不含空白、`@`、`:`；**不能以 `claude-`、`anthropic-` 開頭**（`claude plugin validate` 會報錯），也不要用看起來像官方的名稱。
- **`version`** ✅：設了就會把使用者**固定在該版本，直到你修改它**；發新版時要記得更新。⚠️ 不設 `version` 時的更新行為我沒有查證，不在此斷言。
- **`userConfig`** ✅：讓使用者在對話框填值，不用自己編輯 `settings.json`。`"sensitive": true` 會遮蔽輸入並存進平台的安全儲存，而不是 `settings.json`。
- **在哪裡引用** ✅：`${user_config.KEY}` 可用在 MCP 與 LSP 設定、exec-form hook 的 `args`、skill 與 agent 內容；**在 skill 與 agent 內容裡，sensitive 值會變成佔位符**。shell-form 的 hook 指令、monitor 指令與 MCP 的 `headersHelper` **不能**用 `${user_config.*}`。
- **對話框何時出現** ✅：只在透過 `/plugin` 安裝或啟用時；用 `--plugin-dir` 載入時，要在 session 裡執行 `/plugin configure <plugin>`。

---

## 四、skill：公司的審查與流程

**`skills/code-review/SKILL.md`**

```markdown
---
description: 依公司規範審查 PR。當被要求 review 程式碼時使用。
---

依 ${CLAUDE_PLUGIN_ROOT}/skills/code-review/checklist.md 逐項審查變更的檔案。
先報告安全問題，再報告風格與測試。
```

- **描述就是路由訊號** ✅：Claude 讀每個 skill 的 `description`，符合任務才載入本文；描述要寫清楚「何時用」。
- **輔助檔** ✅：skill 可以帶自己的支援檔案（清單、範例），用到才讀；`${CLAUDE_PLUGIN_ROOT}` 在 skill 內容中會被替換成 plugin 的安裝路徑。
- **誰能呼叫** ✅：`disable-model-invocation: true` 讓 Claude 不自動用它，只能你手動呼叫；少用或有副作用的 skill 建議這樣設，描述也就不佔常駐 context。
- **要放「指示」就寫成 skill** ✅：官方明說 plugin 根目錄的 `CLAUDE.md` 不會載入。
- **和 `commands/` 的關係** ✅：commands 是舊格式，新做的請用 skill；`commands/` 留給從 `.claude/commands/` 搬過來的檔案。

---

## 五、agent：專用的 subagent

**`agents/security-reviewer.md`**

```markdown
---
name: security-reviewer
description: 審查程式變更的安全問題。在修改認證或輸入處理後使用。
model: sonnet
---

你是安全審查員。閱讀變更的檔案，回報注入、認證與密鑰處理的風險。
```

- **可用的欄位** ✅：`name`、`description`、`model`、`effort`、`maxTurns`、`autoCompactWindow`、`tools`、`disallowedTools`、`skills`、`memory`、`background`、`omitClaudeMd`、`isolation`（唯一有效值是 `"worktree"`）、`color`。
- **會被忽略的欄位** ✅：`permissionMode`、`hooks`、`mcpServers`、`initialPrompt`。**agent 檔自己帶不了 hook 與 MCP**，要放在 plugin 層的 `hooks/hooks.json` 與 `.mcp.json`。
- **子資料夾** ✅：`agents/review/security.md` 會載入成 `<plugin>:review:security`。
- **frontmatter 解析失敗**時 agent 仍會載入，但所有欄位被忽略，描述變成 `Agent from <plugin> plugin`；用 `claude plugin validate` 找出這類檔案。
- **要讓 agent 預載公司 skill**：用 `skills:` 欄位（見〈[Claude-Code-Skills](Claude-Code-Skills.md)〉對 skill 與 subagent 的比較）。
- **plugin 預設設定** ✅：plugin 根目錄的 `settings.json` 只有 `agent` 與 `subagentStatusLine` 兩個鍵會生效，其餘都會被丟棄；設 `agent` 可以讓整個 session 的主執行緒用 plugin 自己的 agent。使用者自己的 `agent` 設定會覆蓋它。

---

## 六、MCP：內部系統與知識庫

**`.mcp.json`**（連到公司內部的知識庫服務）

```json
{
  "mcpServers": {
    "kb": {
      "type": "http",
      "url": "${user_config.kb_url}",
      "headers": { "Authorization": "Bearer ${user_config.kb_token}" }
    }
  }
}
```

**本機行程的 server**（腳本放在 plugin 內）

```json
{
  "mcpServers": {
    "db": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.js"]
    }
  }
}
```

- **格式** ✅：和專案的 `.mcp.json` 相同；`mcpServers` 外層包裝可省略。`claude plugin validate` 會檢查 `.mcp.json`，把 Claude Code 載入時會丟棄的項目回報為錯誤（需 v2.1.281 以上）。
- **名稱** ✅：server 顯示為 `plugin:<plugin>:<server>`，工具是 `mcp__plugin_<plugin>_<server>__<tool>`；**權限規則與 hook 的 matcher 要寫這個完整名稱**，只寫 server 名稱的 matcher 永遠不會觸發。
- **變數替換** ✅：`${CLAUDE_PLUGIN_ROOT}` 在 `command`、`args`、`env` 都會替換；遠端 server 的 `url`、`headers` 也會替換。
- **重新載入** ✅：`/reload-plugins` 時，設定沒變的 server 保持連線，有變的重連，被移除的斷線。
- **打包的 MCPB** ✅：`mcpServers` 也接受 `.mcpb` 或 `.dxt` 檔，可以是 plugin 內的路徑或 `https://` 網址。
- **平台範圍** ✅：本機 stdio server 在 Claude Code 與桌面版 Cowork 可用，**在 claude.ai 上不可用**；要讓那邊也能用，改用遠端的 `https://` 網址。
- **安全與組織管控**（`allowedMcpServers`、`deniedMcpServers`、`managedMcpServers`、prompt injection 風險）見〈[Enterprise-AI-Integration](Enterprise-AI-Integration.md)〉第六章。

---

## 七、local knowledge 放哪

![local knowledge 該放哪：小而穩定放 skill 輔助檔；大、常改、要搜尋用 MCP 服務；權限敏感在服務端依身分過濾；只屬於某專案放該專案的 CLAUDE.md 或 rules；要快取或建索引寫進 CLAUDE_PLUGIN_DATA](figures/claude-plugin-knowledge.svg)

| 知識的性質 | 建議放法 | 原因 |
|------------|----------|------|
| **小而穩定**（規範、檢查清單、範例） | skill 目錄的輔助檔，由 `SKILL.md` 引用 | 用到才載入，不佔常駐 context ✅ |
| **大、常改、要搜尋**（文件庫、wiki、RAG） | **MCP 服務**提供檢索；知識留在服務端 | 每次更新 plugin 就是一份新複本；內容一改就要發版 🛠 |
| **權限敏感** | 服務端依使用者身分過濾 | 模型不會自己守權限 🛠 |
| **只屬於某一個專案** | 該專案的 `CLAUDE.md` 或帶 `paths:` 的 rules | plugin 不能帶 `CLAUDE.md` ✅ |
| **要快取或建索引** | `${CLAUDE_PLUGIN_DATA}` | 位於 `~/.claude/plugins/data/<id>/`，**更新後仍保留** ✅ |

**兩個路徑變數的差別** ✅

- **`${CLAUDE_PLUGIN_ROOT}`**：plugin 的安裝目錄。**每個版本有自己的快取目錄，路徑會隨更新改變，不要在那裡寫狀態。**
- **`${CLAUDE_PLUGIN_DATA}`**：更新後仍保留，適合 `node_modules`、虛擬環境、快取；第一次引用時建立；解除安裝時預設會被刪除。

**這些變數的作用範圍** ✅：在 skill、agent 的 Markdown 內容、hook 與 monitor 指令、MCP 與 LSP 設定中會替換；**不會**出現在 Claude 用 Bash 工具執行的指令環境裡。

> 為什麼大型知識不該打包進 plugin：打包後沒有權限控管、沒有新鮮度、更新靠發版。RAG 的流程與企業要求見〈[Enterprise-AI-Integration](Enterprise-AI-Integration.md)〉第五章。
>
> 知識**很多**、而且是**很多份不同功能的 markdown** 時，見下一節。

---

## 八、知識很多：很多份不同功能的 markdown 怎麼放

**不要把它們全塞成一個大 skill，也不要拆成幾百個 skill。** 做法是分層：常駐的只放「導航」，領域知識按需載入，大型語料交給檢索服務。

### 8.1 為什麼不能全塞 skill ✅

| 限制 | 官方說法（〈[Skills](https://code.claude.com/docs/en/skills.md)〉） |
|------|------|
| **描述有總預算** | skill 清單的字元預算約為模型 context 視窗的 **1%**；超出時 Claude Code 會**從最少用的 skill 開始丟掉描述**（名稱仍全部列出），關鍵字消失就匹配不到 |
| **每個描述有上限** | `description` 加 `when_to_use` 合計最多 **1,536 字元**，要把關鍵用途放最前面 |
| **載入後是重複成本** | skill 一旦載入就留在對話裡，「每一行都是持續的 token 成本」 |
| **壓縮後只留開頭** | 壓縮後只能保留被呼叫 skill 的前段，重要指示放 `SKILL.md` 最上面 |
| **長度建議** | `SKILL.md` 控制在 **500 行以內**，詳細參考資料拆到別的檔案 |

預算可以調（`skillListingBudgetFraction`、`SLASH_COMMAND_TOOL_CHAR_BUDGET`、`skillListingMaxDescChars`），但那只是把成本推給所有人，不是解法。`/context` 的 Skills 列顯示套用預算之後的清單大小，`/doctor` 會估算清單的 context 成本與最大貢獻者。

### 8.2 三層放法

![知識很多時的三層放法：L1 常駐的導航；L2 按需載入的領域知識；L3 服務端的大型語料；專案專屬的事實放該 repo 的 CLAUDE.md 或 rules](figures/claude-plugin-scale-layers.svg)

- **L1 常駐：導航**。少量 skill，描述精準。可以做一個「公司知識導覽」skill，列出各領域與去哪找 🛠。
- **L2 按需：領域知識**。每個領域一個 skill，`SKILL.md` 只當地圖，指向輔助檔。
- **L3 服務端：大型語料**。MCP 檢索服務，工具少而精（例如 `search`、`get_doc`、`list_domains`，加 `domain` 參數）🛠；MCP 的工具定義預設延後載入，idle 時成本低 ✅。
- **專案專屬的事實**：放該 repo 的 `CLAUDE.md` 或帶 `paths:` 的 rules。

### 8.3 第一步：把每份 markdown 分類

![每份 markdown 該放哪：必須遵守的規則放 CLAUDE.md 或 rules；流程步驟放 SKILL.md；參考資料放 skill 輔助檔；範例與模板放 examples 或 templates；量大常改的文件庫用 MCP 檢索服務](figures/claude-plugin-markdown-routing.svg)

| 這份 markdown 是… | 例子 | 放哪 |
|-------------------|------|------|
| **每個 session 都必須遵守的規則** | 命名規範、安全底線 | **不放 plugin**：plugin 根目錄的 `CLAUDE.md` 不會載入 ✅。全公司通用用 managed `CLAUDE.md`（由 IT 發佈到每台機器）✅；專案專屬放該 repo 的 `CLAUDE.md` 或 `.claude/rules/` |
| **某個任務的流程步驟** | 上線檢查、PR review、事故處理 | `SKILL.md` 本身 |
| **查閱用的參考資料** | API 規格、術語表、錯誤碼 | 該 skill 的輔助檔 |
| **範例與模板** | 回覆範本、設定範例 | 該 skill 的 `examples/` 或 `templates/` |
| **量大或常改的文件庫** | wiki、設計文件、FAQ | **不打包**，用 MCP 檢索服務 🛠 |

### 8.4 第二步：用情境切 skill，一個 skill 掛多份 markdown

```text
acme-toolkit/skills/
├── acme-guide/               # 導航（可選）
│   └── SKILL.md              # 列出各領域，「想做什麼就用哪個 skill」
├── release-check/
│   ├── SKILL.md              # 流程 + 地圖（<500 行）
│   ├── checklist.md          # 檢查清單
│   ├── rollback.md           # 回滾步驟
│   └── examples/
├── billing-integration/
│   ├── SKILL.md
│   ├── api-reference.md
│   ├── error-codes.md
│   └── templates/
└── incident-response/
    ├── SKILL.md
    └── runbooks/
```

`SKILL.md` 當地圖。官方建議在其中**寫清楚每個檔案是什麼、何時讀**，Claude 才知道要不要載入 ✅。輔助檔**不需要 frontmatter**，只有 `SKILL.md` 需要。

```markdown
---
description: 上線前檢查與回滾。當被要求發佈、上線或回滾服務時使用。
---

## 流程
（核心步驟，簡短）

## 需要細節時再讀
| 檔案 | 內容 | 何時讀 |
|---|---|---|
| ${CLAUDE_SKILL_DIR}/checklist.md | 逐項檢查清單 | 開始上線前 |
| ${CLAUDE_SKILL_DIR}/rollback.md | 回滾步驟 | 出問題需要回滾時 |
```

`${CLAUDE_SKILL_DIR}` 在 skill 內容中會被替換成該 skill 目錄的路徑，不論它裝在個人、專案或 plugin 層都能解析 ✅。

### 8.5 幾個 markdown 合成一個 skill，還是拆開？

| 情況 | 做法 |
|------|------|
| 總是一起用於同一個任務 | 放同一個 skill，當輔助檔 |
| 有自己獨立、不同的觸發情境 | 拆成獨立 skill |
| 只是「查一下」的資料，不是流程 | 輔助檔，或交給 MCP |
| 同一份內容被好幾個任務共用 | 放一個共用 skill 或 MCP，不要複製多份 🛠 |

**不要「一份 markdown 一個 skill」**：每個 skill 的描述每輪都佔 context，數量一多就會撞到上面的預算。

### 8.6 功能很多時的具體技巧

1. **用 `paths:` 限定啟用範圍** ✅：設了之後，Claude 只在處理相符檔案時才自動載入該 skill；把領域 skill 綁到對應的程式碼目錄。路徑相對於 Claude 目前的工作目錄，目錄外的檔案不會符合。
2. **少用或重的設成手動** ✅：`disable-model-invocation: true`，描述不進清單，用 `/plugin名:skill名` 呼叫。
3. **plugin 作者要注意** ✅：`skillOverrides` **不影響 plugin 的 skill**，所以「改成 `name-only`」這招對 plugin 無效；要靠 `paths`、手動觸發，或拆成不同 plugin。
4. **用腳本代替長文** ✅：skill 目錄裡的腳本是「執行」不是「載入」，只有輸出進 context。
5. **大型語料別打包進 plugin**：每次更新就是一份新複本，也沒有權限控管。
6. **很長的 markdown 要拆成主題檔**，並在 `SKILL.md` 的地圖裡寫明；一份幾千行的檔案被整份讀入，是純成本 🛠。

### 8.7 拆 plugin 的方式

- **共同的 `acme-core`**（導航、通用規範）＋**每個領域一個 plugin**（如 `acme-billing`、`acme-risk`），各部門只啟用需要的。
- **官方沒有「依使用者或部門」的單一開關** ✅，要把 managed settings 分別發給各群組（見〈[Claude-Code-Skills](Claude-Code-Skills.md)〉第 12 節）。
- **不要把所有領域放進同一個 plugin 再全員啟用**：每個人都會背著全部的 skill 描述。

### 8.8 很多份 markdown 怎麼維護 🛠

1. **來源只有一份**：markdown 留在公司的文件 repo；由 CI 在發版時同步進各 skill 的輔助檔，或由 MCP 服務直接從文件 repo 建索引，不手動複製。
2. **導航表自動產生**：從每份 markdown 的標題或 frontmatter 產生 `SKILL.md` 的檔案表，避免漏列或過期。
3. **每個領域指定 owner**：用 CODEOWNERS 要求審查（這是 GitHub 的功能）；輔助檔寫明更新日期。
4. **量測**：`/skill-doctor` 顯示每個 skill 的成本與使用頻率，找出沒人用的（需 v2.1.252 以上）✅；`claude plugin eval` 用 `tool_used: Skill` 的 grader 測觸發率 ✅。

### 8.9 一個粗略的例子 ⚠️

假設有 40 份 markdown：

- 6 份「必須遵守」→ managed `CLAUDE.md` 與各專案 rules。
- 18 份流程與參考 → 切成 5 個領域 skill，各自掛輔助檔。
- 10 份範例與模板 → 放各領域 skill 的 `templates/`。
- 6 份大型 wiki → MCP 檢索服務。

這個比例只是示意，不是標準；官方沒有「多少個 skill 算太多」的數字，只有 1% 預算這個機制，實際上限取決於你們的模型 context 大小與描述長度，要用 `/context` 實測。「公司知識導覽」索引 skill 與 MCP 工具的切法是我的建議，不是官方範式。

---

## 九、hook：必須強制的事（可選）

**`hooks/hooks.json`**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/scripts/format.sh\""
          }
        ]
      }
    ]
  }
}
```

- **頂層要有 `"hooks"` 包裝**，只有事件對應表的檔案會載入失敗 ✅。
- **載入就生效** ✅：不必等這個 plugin 的 skill 被用到；要縮小範圍，收窄 `matcher`。
- **環境變數** ✅：hook 行程會拿到 `CLAUDE_PLUGIN_ROOT`、`CLAUDE_PLUGIN_DATA`，以及每個 `userConfig` 值的 `CLAUDE_PLUGIN_OPTION_<KEY>`。
- **引號** ✅：沒有 `args` 時指令走 shell，`${CLAUDE_PLUGIN_ROOT}` 路徑要用雙引號包起來；改用 `args`（exec 形式）則每個元素是一個參數，不需引號。
- **hook 沒有前綴** ✅：如果同一個 hook 既在 `settings.json` 又在 plugin 的 `hooks/hooks.json`，會**跑兩次**。從 `.claude/` 搬進 plugin 後，要刪除原本的。
- **必須每次發生的規則放 hook，不要只靠 skill** ✅，見〈[Claude-Context](Claude-Context.md)〉第六章。

---

## 十、本機測試與驗證

![內部 plugin 從本機測試到全公司強制啟用的流程：validate、plugin-dir、reload 與除錯、eval、發佈到 marketplace、managed settings 強制啟用](figures/claude-plugin-workflow.svg)

1. **檢查**：`claude plugin validate ./acme-toolkit`，檢查 manifest、每個 skill 與 agent 的 frontmatter、`.mcp.json`；`--strict` 會把警告也當失敗。✅
2. **載入**：`claude --plugin-dir ./acme-toolkit`，只在這個 session 載入，不用安裝。可重複旗標載入多個，也可載入 `.zip`。✅
3. **除錯**：改檔後 `/reload-plugins`；`/plugin` 的 **Errors** 分頁列出載入失敗的原因；`/mcp` 看 server 是否連線；`claude plugin list` 看狀態。✅
4. **驗證行為**：`claude plugin eval` 會用有無 plugin 各跑一次測試案例並評分，確認 plugin 真的改變 Claude 的行為。✅
5. **常見失敗** ✅：
   - 元件放進 `.claude-plugin/` 裡：不會載入。
   - `--plugin-dir` 指到 marketplace 根目錄：不會讀 `marketplace.json`，底下的 plugin 不會載入，也不報錯；要指到單一 plugin 的資料夾。
   - manifest 裡的元件路徑不存在或超出 plugin 根目錄：Errors 分頁會顯示 `path not found` 或 `path escapes plugin directory`；路徑必須以 `./` 開頭。
   - `userConfig` 對話框沒出現：見第三節。

**想請 Claude 協助** ✅：安裝官方的 `plugin-dev` plugin（在 `claude-plugins-official` marketplace），執行 `/plugin-dev:create-plugin` 加上你的描述，Claude 會帶你設計、建立並驗證。

**從現有的 `.claude/` 搬過來** ✅：把 `.claude/skills`、`agents`、`commands` 複製到 plugin 根目錄，hook 從 `settings.json` 複製到 `hooks/hooks.json`；搬完驗證沒問題再刪原件。原件還在時 skill 與 agent 不會衝突（plugin 的有前綴），hook 則會跑兩次。

---

## 十一、發佈與強制啟用

### 10.1 放進公司 marketplace ✅

marketplace 是一個含 `.claude-plugin/marketplace.json` 的目錄或 repo，推到 git host（可以是私有 repo）：

```json
{
  "name": "acme-marketplace",
  "description": "公司內部 plugin",
  "owner": { "name": "平台團隊" },
  "plugins": [
    {
      "name": "acme-toolkit",
      "source": "./plugins/acme-toolkit",
      "description": "review、onboarding 與知識庫工具"
    }
  ]
}
```

```bash
claude plugin validate ./acme-marketplace
claude plugin marketplace add your-org/acme-marketplace
claude plugin install acme-toolkit@acme-marketplace
```

- `source` 是**從 marketplace 根目錄算起**的相對路徑，且不能含 `..`。
- 條目的 `name` 要和 plugin 自己 `plugin.json` 的 `name` **一致**，否則用 manifest 名稱安裝會找不到。
- marketplace 的 `name` 選個別人不太會用的，因為使用者不能有兩個同名的 marketplace。
- 私有 repo：每個使用者要有讀取權限，clone 在使用者機器上用已儲存的認證、不會跳出提示。

### 10.2 全公司強制啟用 ✅

在 managed settings 同時設兩個鍵：`extraKnownMarketplaces` 在每台機器註冊 marketplace，`enabledPlugins` 指定要安裝並啟用的 plugin：

```json
{
  "extraKnownMarketplaces": {
    "acme-marketplace": {
      "source": { "source": "github", "repo": "your-org/acme-marketplace" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "acme-toolkit@acme-marketplace": true
  }
}
```

- 使用者在自己的 scope 停用也擋不住，managed 優先。
- 想限制只能從公司來源安裝、不准另外塞 skill，見〈[Claude-Code-Skills](Claude-Code-Skills.md)〉第 12 節。
- 只針對**單一 repo** 的人：在該 repo 的 `.claude/settings.json` 設同樣兩個鍵；但 `enabledPlugins` **不會自動安裝**，每位貢獻者還要執行 `claude plugin install <name>@<marketplace> --scope project`。

---

## 十二、對 context 的影響

| 元件 | 載入時機 | 對 context |
|------|----------|------------|
| skill | 描述常駐，本文用到才載入 | 描述每輪都佔；多個 plugin 累加 ✅ |
| MCP | 啟動載入工具名稱，完整 schema 延後（tool search） | 低；工具結果會進 context ✅ |
| agent | 被叫用時在獨立 context 執行 | 不佔主對話 ✅ |
| hook | 事件觸發 | 零成本，除非回傳輸出 ✅ |
| plugin 本身 | — | 只是打包層，本身不另佔 context ⚠️（推論）；裡面各元件各自遵守上面的規則 |

細節見〈[Claude-Context](Claude-Context.md)〉第六章。

---

## 十三、注意事項

| 項目 | 說明 |
|------|------|
| **plugin 會在使用者機器上執行程式** | MCP 的 stdio server、hook、monitor 都以使用者權限執行；monitor 還在 sandbox 外。上架前要審查 ✅ |
| **monitor 不給 userConfig** | monitor 指令不能引用 `${user_config.*}`，也拿不到 `CLAUDE_PLUGIN_OPTION_<KEY>` ✅ |
| **不要用保留名稱** | 以 `claude-`、`anthropic-`、`anthropics-`、`cc-plugin-` 開頭，或含 `official` 搭配 claude／anthropic，會被 validate 擋下 ✅ |
| **agent 不能自帶 MCP 與 hook** | 放在 plugin 層 ✅ |
| **hook 可能跑兩次** | 搬移後要刪掉 `.claude/` 裡的原件 ✅ |
| **版本** | 設了 `version` 就要記得更新 ✅ |
| **各平台差異** | 有 `bin/` 的 plugin 不會安裝到 claude.ai 與 Cowork；本機 stdio MCP 也不能在 claude.ai 使用 ✅ |
| **本文沒有逐項實測** | 範例對照官方格式撰寫，實際載入請用 `claude plugin validate` 與 `--plugin-dir` 驗證 ⚠️ |

---

## 官方來源與相關文件

- [Create a Claude Code plugin](https://code.claude.com/docs/en/plugins/create.md)
- [Add components to a plugin](https://code.claude.com/docs/en/plugins/components.md)
- [Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md)
- [Create a marketplace](https://code.claude.com/docs/en/plugins/marketplace-reference.md)
- [Manage Claude Code plugins for your organization](https://code.claude.com/docs/en/plugins/org.md)
- [Skills](https://code.claude.com/docs/en/skills.md)：skill 清單預算、`paths`、輔助檔、`/skill-doctor`
- 〈[Claude-Code-Skills](Claude-Code-Skills.md)〉：skill 的比較、並存衝突、團隊治理
- 〈[Claude-Context](Claude-Context.md)〉：擴充機制對 context 的影響
- 〈[Enterprise-AI-Integration](Enterprise-AI-Integration.md)〉：RAG、MCP 與企業整合
