# LLM Wiki：讓 LLM 維護知識庫的模式，以及用在 coredump 案例庫的評估

> 資料日期：2026-11-23  
> 範圍：Karpathy 的 **LLM Wiki** 是什麼、三層結構、三個操作、與 RAG 的差別、適用與不適用的情況，以及我把它用在 coredump 案例庫的**設計構想**。  
> 讀法：**【原文】** 取自 Karpathy 的 gist，由代理人讀取原文後回報（gist 本文為逐字讀取；底下的留言串只有摘要；我沒有親自開啟頁面）；**【二手】** 取自搜尋結果的摘要，我沒有開啟原文；**【建議】** 是我的歸納；**【推論】** 是我的類推，沒有直接依據。  
> ⚠️ **我沒有實作過 LLM Wiki，也沒有在 coredump 案例上試過。** 第 5 節是設計構想，不是驗證過的做法。

## 先看結論

- **LLM Wiki 是一個設計模式，不是軟體**：讓 LLM 在你和原始資料之間，**持續建立並維護一組互相連結的 markdown 頁面**，而不是每次提問都從原始檔重新推導。Karpathy 在 2026-04-04 以 gist 發佈，自稱是「intentionally abstract」的想法（【原文】）。
- **三層、三個操作**：原始資料（唯讀）、wiki（LLM 維護）、schema（規定怎麼維護）；ingest（匯入）、query（查詢）、lint（健檢）（第 1–2 節）。
- **與 RAG 的差別在時機**：RAG 在提問時才檢索與推導；LLM Wiki 在匯入時就把知識整理成頁面，之後持續維護（第 3 節）。兩者互補，不是取代。
- **適用規模**：gist 說用 `index.md` 就能在「約 100 份資料、數百頁」的規模下運作；更大的規模我沒有資料（第 6 節）。
- **用在 coredump 案例庫**：每個分析完的案件寫回一頁，下次相同簽章的案件先查 wiki。這與既有的 fingerprint 去重同方向，但**要加人工審閱，否則錯誤結論會被累積**（第 5 節）。
- **最大風險**：LLM 的錯誤會被寫進頁面並被後續引用，gist 本身沒有列出自己的限制（【原文】），這是我的推論。

---

## 1. 是什麼：三層結構

![圖：LLM Wiki 的三層：原始資料（唯讀、你提供）、wiki（LLM 擁有並維護）、schema（規範 LLM 怎麼維護）](figures/llm-wiki-layers.svg)

【原文】gist 的核心主張：一般用 LLM 處理文件（RAG）時，模型每次都從原始檔重新找、重新推導，**知識不會累積**。它提議讓 LLM 增量地建立並維護一組互相連結的 markdown 頁面，「the wiki is a persistent, compounding artifact」。

| 層 | 內容 | 誰負責 |
|---|---|---|
| **原始資料（raw）** | 文章、論文、圖片、資料檔；**唯讀**，是事實來源 | 你提供 |
| **wiki** | LLM 產生的 markdown 目錄：摘要、實體與概念頁、比較、總覽，以及 `index.md`、`log.md` | LLM 擁有並維護 |
| **schema** | 一份設定文件，如 `CLAUDE.md` 或 `AGENTS.md`，規定結構、慣例與工作流程；gist 稱它是「the key configuration file」 | 規範 LLM 如何維護 wiki |

- **分工**：你負責挑資料、提問、審閱；LLM 負責整理、交叉引用、歸檔與維護。gist 說，人類維護 wiki 之所以失敗，是維護成本太高，而 LLM 讓這個成本「近乎零」（【原文】摘要）。
- **「只是一個 git repo」**：gist 說 wiki 就是一個 markdown 檔案的 git repo，所以有版本歷史與分支可用（【原文】）。
- **gist 沒有給固定的目錄結構**；結構、頁面格式與工具「依你的領域而定」。它自稱是可以貼給 LLM agent 的「idea file」，由 agent 與你一起建出具體版本（【原文】）。

---

## 2. 三個操作：ingest、query、lint

![圖：三欄：ingest 匯入、query 查詢、lint 健檢的步驟](figures/llm-wiki-ops.svg)

【原文】（摘要，細節以原文為準）

- **Ingest（匯入）**：你放入一份新資料；LLM 讀它、與你討論，寫一頁摘要，更新 index，更新相關的實體與概念頁，並在 log 加一筆。**一份資料可能動到 10–15 頁**；作者偏好一次匯入一份。
- **Query（查詢）**：LLM 搜尋並閱讀 wiki 頁面，回答時附引用。**好的答案可以存回 wiki 成為新頁面**，知識因此累積；輸出形式可以是 markdown、比較表、Marp 簡報或 matplotlib 圖表。
- **Lint（健檢）**：定期檢查矛盾、過時說法、孤立頁面、缺少的概念、缺少的交叉引用與資料缺口。

**兩個輔助檔**（【原文】）：

| 檔案 | 用途 | 格式建議 |
|---|---|---|
| `index.md` | 內容導向的目錄：每頁一個連結、一行摘要、可選的中繼資料 | 查詢時先讀它找到相關頁面；gist 說在「約 100 份資料、數百頁」的規模下可行，避開 embedding 式 RAG |
| `log.md` | 只增不改的時間紀錄 | 用一致的前綴，如 `## [2026-04-02] ingest \| Article Title`，方便 `grep` |

**工具**（【原文】）：Obsidian 當閱讀介面（圖譜檢視、Web Clipper）；Claude Code 或 OpenAI Codex 當執行的 agent；`qmd`（本機 markdown 搜尋，含 CLI 與 MCP server）是選用；Marp、Dataview、matplotlib 做輸出；git 做版本管理。

---

## 3. 與 RAG 的差別

![圖：RAG 在提問時才檢索與推導，不累積；LLM Wiki 在匯入時就編譯成頁面並持續維護，好答案存回 wiki](figures/llm-wiki-vs-rag.svg)

- 【原文】RAG 在查詢時「retrieves relevant chunks」；LLM Wiki 則是「The knowledge is compiled once and then _kept current_, not re-derived on every query」。gist 把 NotebookLM、ChatGPT 檔案上傳與多數 RAG 系統，視為「沒有累積」的基準。
- **兩者互補**（【二手】）：LLM Wiki 的整理發生在匯入時，RAG 發生在查詢時；實務上常見搭配，而不是擇一。
- **代價**（【二手】）：來源更新後要重新匯入，wiki 與最新事實之間會有落差；需要定期 lint 與審閱。我沒有開啟這些二手來源的原文。

---

## 4. 實作要點（示意）

gist 沒有給固定結構，下面是我依它的描述整理的示意（【建議】，沒有實作過）。

```text
my-wiki/
  raw/                  # 原始資料，唯讀（不要讓 LLM 改它）
  wiki/
    index.md            # 每頁一行：連結、一句話摘要
    log.md              # 只增不改：## [2026-11-23] ingest | 標題
    sources/            # 每份原始資料一頁摘要
    concepts/           # 概念與實體頁
  CLAUDE.md             # schema：規定 LLM 怎麼匯入、查詢、健檢
```

schema 該寫什麼（【建議】）：

```markdown
# Wiki 維護規則（示意）

## 匯入（ingest）
- 一次只處理一份 raw/ 內的資料；先摘要給我看，確認後再寫入。
- 每份資料建立 sources/ 的一頁；更新相關的 concepts/ 頁；更新 index.md；在 log.md 加一筆。
- 每個論述都要標註來源（連到 sources/ 的頁面）；不確定的寫「待確認」，不要編造。

## 查詢（query）
- 先讀 index.md 找頁面，再讀頁面；回答要附引用。
- 好的答案要先問我，再存成新頁面。

## 健檢（lint）
- 找：互相矛盾的說法、沒有來源的論述、孤立頁、index 沒收錄的頁、過時的內容。
- 只列出問題與建議的修正，經我同意再改。

## 禁止
- 不得修改 raw/ 內的任何檔案。
```

- **來源要可追溯**：每頁都引用 `sources/`，這樣 lint 與人工審閱才抓得到錯。
- **版本管理**：用 git；每次 ingest 一個 commit，方便回溯與還原（【原文】說 wiki 就是 git repo）。
- **人在迴圈**：匯入時先讓你看摘要與要改的頁面，再寫入；不要全自動（【建議】）。

---

## 5. 用在 coredump 案例庫（設計構想）

![圖：coredump 案例庫的流程：新案件先用簽章查 wiki，命中就引用既有根因頁；沒命中就由 Claude 分析、驗證、人工審閱後 ingest 回 wiki；定期 lint](figures/llm-wiki-coredump.svg)

**構想**（【推論】，沒有實作過）：[Claude-Coredump-Agent](Claude-Coredump-Agent.md) 的成本漏斗第 0 層是「fingerprint 去重」，命中既有簽章就不呼叫模型。LLM Wiki 可以當這個「既有分析」的**可讀、可累積的版本**：

| 頁面類型 | 內容 | 例子 |
|---|---|---|
| 簽章頁 | 一種 crash 簽章：signal、top frames、出現過的案件、對應的根因頁 | `signatures/sigsegv-parse_header.md` |
| 根因頁 | 一種根因：說明、證據（引用 `evidence_id`）、影響的版本、修復版本、反證 | `root-causes/null-deref-in-parse_header.md` |
| 模組頁 | 某模組的已知問題、常見 crash、相關人員與文件 | `modules/parser.md` |
| 案件頁 | 一個 Jira ticket 的分析摘要與連結 | `cases/CORE-123.md` |
| `index.md`、`log.md` | 目錄與時間紀錄 | — |

**流程**（對應上圖）：
1. 新案件先用簽章查 wiki（簽章頁）。**命中**就引用既有根因頁與相關案件；**仍要驗證版本是否相符**，因為同樣的簽章在不同版本可能是不同原因（【建議】）。
2. **沒命中**就走 [Claude-Coredump-Code](Claude-Coredump-Code.md) 的分析流程，產生報告並通過 schema 驗證。
3. **人工審閱後才 ingest**：寫案件頁，更新簽章頁、根因頁、模組頁、`index.md` 與 `log.md`。**錯誤的結論不要被累積**（【建議】）。
4. **定期 lint**：找互相矛盾的根因、沒有證據的論述、已修復版本卻仍標「未修」的頁面、孤立頁（【建議】）。

**與既有設計的關係**：
- **不取代**案件資料庫與 fingerprint 去重：它們負責「精確、可程式查詢」；wiki 負責「可讀、可累積的敘述與關聯」（【建議】）。
- **evidence_id 要保留**：根因頁引用的證據仍要能回查到工具輸出，才不會變成沒有根據的敘述（呼應報告驗證規則）。
- **Jira 回寫**：命中時可以把既有根因頁的連結放進 comment（【建議】）。

**要特別注意**：
- **資料外送與敏感資料**：wiki 頁面是從 dump 的分析衍生的，可能含客戶資料或機密；放在哪、誰能讀、能不能送給外部 API，要依公司政策（見 [Claude-Coredump-Agent](Claude-Coredump-Agent.md) 第 7 節）。
- **成本**：【原文】一份資料的 ingest 可能動到 10–15 頁，每次要讀寫多個頁面；**我沒有估算 token 與費用**，成本模型見該文件第 6 節，要自己代入實測數字。
- **規模**：gist 的規模描述是約 100 份資料、數百頁；案件量遠大於此時能否只靠 `index.md`，我沒有資料。
- **簽章比對**：簽章要怎麼正規化、怎麼避免誤命中，是額外的工程問題，本文沒有處理。

---

## 6. 什麼情況適合

![圖：五種情況：資料約一百份適合；資料量遠大於此要評估；要即時反映最新狀態要承擔落差；要可追溯可稽核適合；沒有人審閱錯誤會累積則不建議](figures/llm-wiki-choose.svg)

---

## 7. 風險與限制（【建議】與【推論】）

1. **錯誤會被累積**：LLM 寫進頁面的錯誤，會被後續的 ingest 與 query 引用；沒有人審閱就沒有防線（【推論】）。
2. **過時**：來源更新後 wiki 不會自動跟上；要靠 lint 與重新匯入（【二手】）。
3. **矛盾與淘汰**：留言串提到矛盾處理與過時內容的淘汰尚未解決（【原文】留言摘要，我沒驗證）。
4. **來源要可追溯**：沒有引用來源的頁面，無法審閱也無法 lint。
5. **成本與延遲**：每次 ingest 要讀寫多頁；規模變大後，`index.md` 可能不夠（【原文】只談到數百頁）。
6. **安全**：把外部資料交給有寫入權限的 agent，要注意 prompt injection（資料中的文字可能是指令）；schema 要寫明資料是不可信輸入，並限制 agent 只能寫 wiki 目錄（【建議】）。
7. **社群實作良莠不齊**：留言串有許多第三方專案的連結，我沒有驗證任何一個；二手來源說已有 30 多個實作（【二手】，未確認）。

---

## 8. 驗證說明與限制

- 資料日期 2026-11-23。**我沒有實作過 LLM Wiki，也沒有在 coredump 案例上試過。**
- **【原文】** 來自 Karpathy 的 gist（標題 *LLM Wiki*，檔名 `llm-wiki.md`，頁面顯示建立於 2026-04-04）：代理人讀取，本文為逐字讀取，**留言串只有摘要**；我沒有親自開啟頁面。gist 說自己是「intentionally abstract」，**沒有列出自己的限制**。
- **【二手】** 來自搜尋結果的摘要（DataCamp、AFFiNE、Analytics Vidhya 等的整理），我沒有開啟原文；其中「與 RAG 互補」「更新有落差」「30 多個社群實作」是二手說法。
- **第 4–5 節是我的設計構想**：目錄結構、schema 範例、頁面類型、流程與風險，都是依 gist 描述與本庫的 coredump 設計整理，沒有驗證。
- 沒有評估過：成本與準確率、案件量遠大於數百頁時的表現、簽章正規化與誤命中、與 Jira 與既有案件資料庫的整合。

---

## 9. 參考

- 原文：Andrej Karpathy，*LLM Wiki*（gist，2026-04-04）：<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>（代理人讀取）。
- 二手整理（搜尋結果網址，**我沒有開啟**）：DataCamp <https://www.datacamp.com/blog/llm-wiki>、AFFiNE <https://affine.pro/blog/what-is-llm-wiki>、Analytics Vidhya <https://www.analyticsvidhya.com/blog/2026/04/llm-wiki-by-andrej-karpathy/>。
- 本庫：[Claude-Coredump-Agent](Claude-Coredump-Agent.md)（fingerprint 去重、成本漏斗、安全）、[Claude-Coredump-Code](Claude-Coredump-Code.md)（分析流程與報告驗證）、[Claude-Coredump-MVP](Claude-Coredump-MVP.md)、[Claude-Context](Claude-Context.md)（`CLAUDE.md` 與記憶）。
