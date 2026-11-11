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

---

## 八、hook：必須強制的事（可選）

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

## 九、本機測試與驗證

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

## 十、發佈與強制啟用

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

## 十一、對 context 的影響

| 元件 | 載入時機 | 對 context |
|------|----------|------------|
| skill | 描述常駐，本文用到才載入 | 描述每輪都佔；多個 plugin 累加 ✅ |
| MCP | 啟動載入工具名稱，完整 schema 延後（tool search） | 低；工具結果會進 context ✅ |
| agent | 被叫用時在獨立 context 執行 | 不佔主對話 ✅ |
| hook | 事件觸發 | 零成本，除非回傳輸出 ✅ |
| plugin 本身 | — | 只是打包層，本身不另佔 context ⚠️（推論）；裡面各元件各自遵守上面的規則 |

細節見〈[Claude-Context](Claude-Context.md)〉第六章。

---

## 十二、注意事項

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
- 〈[Claude-Code-Skills](Claude-Code-Skills.md)〉：skill 的比較、並存衝突、團隊治理
- 〈[Claude-Context](Claude-Context.md)〉：擴充機制對 context 的影響
- 〈[Enterprise-AI-Integration](Enterprise-AI-Integration.md)〉：RAG、MCP 與企業整合
