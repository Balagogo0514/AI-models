# tools/：把 docs/ 轉成網頁

`build_site.py` 把 `docs/*.md` 轉成共用樣式的靜態網頁：一個首頁索引加每篇一頁，含章節目錄導覽、深淺色主題與手機版面。

## 使用

```bash
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/build_site.py            # 輸出到 _site/
.venv/bin/python tools/build_site.py --out /tmp/site   # 指定輸出目錄
```

輸出是純靜態檔案（`index.html`、每篇的 `.html`、`style.css`），可直接用瀏覽器開 `_site/index.html`，或放到任何靜態網站主機。`_site/` 與 `.venv/` 已加入 `.gitignore`，不會被提交。

## 目錄

| 檔案 | 說明 |
|---|---|
| `build_site.py` | 轉換腳本 |
| `requirements.txt` | 依賴（`markdown-it-py`，CommonMark 規則，與 GitHub 的巢狀清單判定一致） |
| `site/style.css` | 共用樣式，色彩全用 token，淺色／深色各一組 |
| `site/Post-Training.src.html` | Post-Training 的手工設計頁面（含 SVG 圖），見下方注意事項 |

## 新增文件

把 `.md` 放進 `docs/`，重跑腳本即可。沒有列在 `build_site.py` 的 `CATS` 裡的文件，會自動放進首頁的「其他」分類，說明取自檔案開頭的第一段文字。想放進特定分類或自訂一句話說明，編輯 `CATS`。

## 轉換細節

- 標題（`#`）改由頁首顯示，內文從第一個 `##` 開始；`##`、`###` 組成目錄。
- 表格包在可橫向捲動的容器裡，手機上不會撐寬頁面。
- ` ```mermaid ` 區塊輸出為 `<pre class="mermaid">`，由支援 Mermaid 的檢視環境渲染；不支援時顯示為原始碼文字。
- 單獨一行的 `$$ … $$` 公式以 KaTeX 的 MathML 輸出渲染（載入 cdnjs 上的 KaTeX 0.16.9）；載入失敗時顯示原始 LaTeX。其他地方的 `$` 不當作公式。
- 「粗體結尾為標點、後面緊接中文字」時，CommonMark（含 GitHub）不認結尾的 `**`，會把星號原樣露出來；本腳本在轉換前處理這種情況，頁面上會顯示成正確的粗體。
- 文件之間的相對連結（`X.md`）會轉成 `X.html`。
- 圖片放在 `docs/figures/`，筆記內以 `figures/xxx.svg` 相對路徑引用；建置時整個資料夾會複製到輸出的 `figures/`。SVG 內可用 `prefers-color-scheme` 讓圖跟著深淺色切換。

## 注意事項

- **Post-Training 頁面不會自動更新。** 它沿用手工設計的 HTML（`site/Post-Training.src.html`），`docs/Post-Training.md` 改了之後，需要手動同步這份 HTML，否則兩者會不一致。想改用純 Markdown 轉換，從 `build_site.py` 的 `CUSTOM_PAGES` 移除 `"Post-Training"` 即可（會失去手繪的圖）。
- **頁面是轉換版**，原始 Markdown 以 repo 為準。
- 網頁載入 Google Fonts（Noto Sans TC、JetBrains Mono）；離線時退回系統字型。
