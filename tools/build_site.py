#!/usr/bin/env python3
"""把 docs/*.md 轉成共用樣式的靜態網頁（首頁索引 + 每篇一頁），輸出到 _site/。

用法：
    python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
    .venv/bin/python tools/build_site.py            # 輸出到 _site/
    .venv/bin/python tools/build_site.py --out /tmp/site

新增文件：把 .md 放進 docs/ 即可，會自動出現在首頁的「其他」分類；
想放進特定分類，編輯下方的 CATS。
"""
import argparse
import html
import pathlib
import re
import shutil

from markdown_it import MarkdownIt

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "docs"
ASSETS = REPO / "tools" / "site"
GITHUB = "https://github.com/Balagogo0514/AI-models"
GITHUB_DOCS = GITHUB + "/blob/master/docs/"
SITE_TITLE = "AI 模型筆記庫"
SITE_HEADING = "AI 模型與 Agent 筆記庫"

# 首頁分類：(分類名稱, [(檔名不含 .md, 一句話說明), ...])
CATS = [
    ("模型與訓練", [
        ("Scaling-Laws", "模型效能如何隨參數量、資料量、運算量變化的冪律關係"),
        ("Post-Training", "後訓練、RL 的分類，以及企業知識整合時 RAG 夠不夠"),
        ("Transformer-Attention", "MHA、MQA、GQA、MLA 等注意力強化機制與 KV cache 瓶頸"),
        ("Long-Context-Note", "Lost in the Middle：為何模型容易遺失中段資訊"),
        ("Claude-Model", "Sonnet／Opus／Fable 等模型的規格、價格與 API 差異"),
        ("OpenAI-Model", "OpenAI 模型（API 版）的場景建議與比較"),
    ]),
    ("Agent 與開發工具", [
        ("Agentic-Engineering", "Graph Engineering：把 Agent 執行流程建模為節點、狀態與轉移"),
        ("Claude-Code-CLI", "Claude Code 指令、旗標、斜線指令、Hooks、MCP、Plugin 的完整參考"),
        ("Claude-Context", "Claude Code 送給 LLM 的 context 如何組成、記憶放在哪、彼此是否取代"),
        ("Enterprise-AI-Integration", "六個整合層次、八階段流程、RAG 與 MCP 怎麼接內部資料與系統、權限階梯、API／自架／微調的資源與成本判斷"),
        ("Claude-Agent", "平行工作方式選型、多 Agent code review、追蹤彙整，含 fastpath refcount 實戰範例"),
        ("Claude-Code-Skills", "superpowers 與 planning-with-files 的 Skill／Plugin 比較"),
        ("CodeX-CLI", "OpenAI Codex CLI 的指令、sandbox、approval、設定的完整參考"),
        ("CodeX-Agent", "Codex 的 Subagents、Cloud、codex exec 平行與 code review 做法"),
        ("OpenAI-Python-Agent", "以 Python 控制的 coredump 自動分析流程設計"),
    ]),
]

# 這些頁面沿用手工設計的 HTML（含 SVG 圖），來源在 tools/site/<名稱>.src.html。
# 注意：它不會隨 .md 自動更新，.md 改了之後要手動同步這份 HTML。
CUSTOM_PAGES = {"Post-Training"}

HEAD_COMMON = (
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="claude:viewport-fit-sides" content="cover">\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;500;700&display=swap">\n'
    '<link rel="stylesheet" href="style.css">\n'
)

# CommonMark 在「粗體結尾為標點、後面緊接中文字」時不認結尾標記（GitHub 同樣如此）。
# 只處理程式碼區塊以外的行：先換成私有標記，轉換後再還原成 <strong>。
CJK_PAIR = re.compile(
    r"\*\*(?=[^\s*|　-〿＀-￯)\]])"
    r"([^*|\n]*?[　-〿＀-￯)\]」』】》”’])\*\*"
    r"(?=[一-鿿぀-ヿ])"
)


def clean_heading(t: str) -> str:
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    return re.sub(r"[`*_]", "", t).strip()


def discover(cats):
    """把 docs/ 裡沒列在 CATS 的 .md 自動放進「其他」分類。"""
    known = {s for _, items in cats for s, _ in items}
    extra = []
    for p in sorted(SRC.glob("*.md")):
        if p.stem in known:
            continue
        desc = ""
        for line in p.read_text(encoding="utf-8").split("\n")[1:]:
            line = line.strip()
            if line and not line.startswith(("#", ">", "|", "-", "`", "!")):
                desc = clean_heading(line)[:60]
                break
        extra.append((p.stem, desc))
    return cats + ([("其他", extra)] if extra else [])


def make_md() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    md.renderer.rules["table_open"] = lambda tokens, idx, options, env: '<div class="scroll"><table>\n'
    md.renderer.rules["table_close"] = lambda tokens, idx, options, env: "</table></div>\n"
    return md


class Site:
    def __init__(self, out: pathlib.Path):
        self.out = out
        self.cats = discover(CATS)
        self.order = [s for _, items in self.cats for s, _ in items]
        self.cat_of = {s: c for c, items in self.cats for s, _ in items}
        self.desc = {s: d for _, items in self.cats for s, d in items}
        self.titles = {}
        self.stats = {}
        for slug in self.order:
            text = (SRC / f"{slug}.md").read_text(encoding="utf-8")
            m = re.search(r"^# (.+)$", text, flags=re.M)
            self.titles[slug] = clean_heading(m.group(1)) if m else slug

    # ---- Markdown -> HTML ----
    def render(self, slug):
        text = (SRC / f"{slug}.md").read_text(encoding="utf-8")
        mer, maths = [], []

        def sub_mer(m):
            mer.append(m.group(1))
            return f"\n\nMERMAIDPH{len(mer) - 1}\n\n"

        def sub_math(m):
            maths.append(m.group(1))
            return f"\n\nMATHPH{len(maths) - 1}\n\n"

        text = re.sub(r"^```mermaid[ \t]*\n(.*?)^```[ \t]*$", sub_mer, text, flags=re.S | re.M)
        text = re.sub(r"^\$\$[ \t]*\n(.*?)\n\$\$[ \t]*$", sub_math, text, flags=re.S | re.M)

        out_lines, in_fence = [], False
        for line in text.split("\n"):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            out_lines.append(line if in_fence else CJK_PAIR.sub("\\1", line))
        text = "\n".join(out_lines)

        md = make_md()
        tokens = md.parse(text)
        title, toc, out_tokens, n, i = None, [], [], 0, 0
        while i < len(tokens):
            t = tokens[i]
            if t.type == "heading_open":
                level = int(t.tag[1])
                inline = tokens[i + 1]
                if level == 1 and title is None:
                    title = clean_heading(inline.content)
                    i += 3  # 略過 h1 的 open / inline / close，標題改由頁首顯示
                    continue
                n += 1
                sid = f"sec-{n}"
                t.attrSet("id", sid)
                if level in (2, 3):
                    toc.append((level, sid, clean_heading(inline.content)))
            out_tokens.append(t)
            i += 1
        body = md.renderer.render(out_tokens, md.options, {})

        for k, code in enumerate(mer):
            body = body.replace(f"<p>MERMAIDPH{k}</p>", f'<pre class="mermaid">{html.escape(code.rstrip())}</pre>')
        for k, tex in enumerate(maths):
            esc = html.escape(tex.strip(), quote=True)
            body = body.replace(f"<p>MATHPH{k}</p>", f'<div class="math" data-tex="{esc}"><pre>{esc}</pre></div>')
        body = body.replace("", "<strong>").replace("", "</strong>")
        # 單獨一行的圖片包進可捲動容器：手機上圖保持可讀的最小寬度，超出時只在圖片區塊內捲動
        body = re.sub(r"<p>(<img [^>]*>)</p>", r'<div class="figwrap">\1</div>', body)

        def fix_link(m):
            name, frag = m.group(1), m.group(2) or ""
            return f'href="{name}.html{frag}"' if name in self.order else m.group(0)

        body = re.sub(r'href="(?:docs/)?([A-Za-z0-9._-]+)\.md(#[^"]*)?"', fix_link, body)
        return title or slug, toc, body, bool(maths), text.count("\n") + 1

    # ---- 頁面 ----
    @staticmethod
    def toc_html(toc, cls):
        items = "".join(f'<li class="l{lvl}"><a href="#{sid}">{html.escape(txt)}</a></li>' for lvl, sid, txt in toc)
        return f'<nav class="toc {cls}" aria-label="目錄"><ul>{items}</ul></nav>'

    def page(self, slug):
        title, toc, body, has_math, lines = self.render(slug)
        idx = self.order.index(slug)
        prev = self.order[idx - 1] if idx > 0 else None
        nxt = self.order[idx + 1] if idx < len(self.order) - 1 else None

        def pager_link(s, label):
            if not s:
                return "<span></span>"
            return f'<a href="{s}.html"><small>{label}</small>{html.escape(self.titles[s])}</a>'

        h2 = sum(1 for lvl, _, _ in toc if lvl == 2)
        doc = f"""<!doctype html>
<html lang="zh-Hant">
<head>
{HEAD_COMMON}<title>{html.escape(title)}</title>
</head>
<body>
<div class="topbar"><a href="index.html">← 首頁</a><a href="{GITHUB_DOCS}{slug}.md" target="_blank" rel="noopener">在 GitHub 看原始檔</a></div>
<div class="layout">
  {self.toc_html(toc, "side")}
  <main class="doc">
    <details class="toc-m"><summary>目錄（{h2} 節）</summary>{self.toc_html(toc, "mob")}</details>
    <header class="doc-head">
      <div class="kicker">{html.escape(self.cat_of[slug])}</div>
      <h1>{html.escape(title)}</h1>
      <div class="meta">{html.escape(self.desc[slug])}</div>
    </header>
    {body}
    <div class="pager">{pager_link(prev, "上一篇")}{pager_link(nxt, "下一篇")}</div>
  </main>
</div>
{SPY}
{MATH if has_math else ""}
</body>
</html>
"""
        (self.out / f"{slug}.html").write_text(doc, encoding="utf-8")
        return title, h2, lines

    def custom_page(self, slug):
        """沿用手工設計的 HTML：補上完整檔頭與返回首頁連結。"""
        src = (ASSETS / f"{slug}.src.html").read_text(encoding="utf-8")
        head, rest = src.split("<main>", 1)
        reset = (
            "<style>\n:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); color-scheme: light; }\n"
            "html { color-scheme: light; }\n.backlink { font-size: 14px; color: var(--muted); text-decoration: none; }\n"
            ".backlink:hover { color: var(--accent); }\n</style>\n"
        )
        page_html = (
            '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + reset
            + '</head>\n<body style="margin:0">\n<main>\n<a class="backlink" href="index.html">← 首頁</a>\n'
            + rest.replace("</main>", "</main>\n</body>\n</html>\n", 1)
        )
        (self.out / f"{slug}.html").write_text(page_html, encoding="utf-8")

    def index(self):
        cards = []
        for cat, items in self.cats:
            cs = []
            for slug, desc in items:
                t, h2, lines = self.stats[slug]
                cs.append(
                    f'<a class="card" href="{slug}.html"><b>{html.escape(t)}</b>'
                    f'<span>{html.escape(desc)}</span><small>{h2} 節 · {lines} 行</small></a>'
                )
            cards.append(f'<section class="cat"><h2>{html.escape(cat)}</h2><div class="grid">{"".join(cs)}</div></section>')
        idx = f"""<title>{SITE_TITLE}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;500;700&display=swap">
<link rel="stylesheet" href="style.css">
<div class="hub">
  <header>
    <div class="kicker">AI-models</div>
    <h1>{SITE_HEADING}</h1>
    <p class="lede">AI 模型、Agent 工程與開發工具的中文筆記集，涵蓋模型原理與訓練、Claude Code／Codex 等 Agent 工具的使用與選型。共 {len(self.order)} 篇，點卡片開啟。</p>
  </header>
  {"".join(cards)}
  <footer>內容來源：GitHub repo <a href="{GITHUB}" target="_blank" rel="noopener">Balagogo0514/AI-models</a> 的 docs/。頁面為轉換版，原始 Markdown 以 repo 為準。</footer>
</div>
"""
        (self.out / "index.html").write_text(idx, encoding="utf-8")

    def build(self):
        self.out.mkdir(parents=True, exist_ok=True)
        shutil.copy(ASSETS / "style.css", self.out / "style.css")
        figures = SRC / "figures"  # 筆記內以相對路徑 figures/xxx.svg 引用的圖片
        if figures.is_dir():
            shutil.copytree(figures, self.out / "figures", dirs_exist_ok=True)
        for slug in self.order:
            if slug in CUSTOM_PAGES and (ASSETS / f"{slug}.src.html").exists():
                title, toc, _, _, lines = self.render(slug)
                self.stats[slug] = (title, sum(1 for lvl, _, _ in toc if lvl == 2), lines)
                self.custom_page(slug)
            else:
                self.stats[slug] = self.page(slug)
        self.index()
        for slug in self.order:
            p = self.out / f"{slug}.html"
            print(f"{slug:26s} {p.stat().st_size // 1024:5d} KB  {self.stats[slug][1]:3d} 節  {self.stats[slug][2]:5d} 行")
        print("OK ->", self.out)


SPY = """<script>
(function () {
  var links = [].slice.call(document.querySelectorAll('.toc a'));
  var heads = [].slice.call(document.querySelectorAll('.doc h2[id], .doc h3[id]'));
  if (!('IntersectionObserver' in window) || !heads.length) return;
  var map = {}, current = null;
  links.forEach(function (a) { var id = a.getAttribute('href').slice(1); (map[id] = map[id] || []).push(a); });
  function set(id) {
    if (current === id) return; current = id;
    links.forEach(function (a) { a.classList.remove('on'); });
    (map[id] || []).forEach(function (a) { a.classList.add('on'); });
    var box = document.querySelector('.toc.side'), el = box && box.querySelector('a.on');
    if (box && el && box.offsetParent) {
      var r = el.getBoundingClientRect(), b = box.getBoundingClientRect();
      if (r.top < b.top + 8 || r.bottom > b.bottom - 8) box.scrollTop += r.top - b.top - 60;
    }
  }
  var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) set(e.target.id); }); }, { rootMargin: '0px 0px -75% 0px' });
  heads.forEach(function (h) { io.observe(h); });
})();
</script>"""

MATH = """<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script>
document.querySelectorAll('.math').forEach(function (el) {
  try { if (window.katex) window.katex.render(el.getAttribute('data-tex'), el, { displayMode: true, output: 'mathml', throwOnError: false }); } catch (e) {}
});
</script>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="docs/*.md -> 靜態網頁")
    ap.add_argument("--out", default=str(REPO / "_site"), help="輸出目錄（預設 _site/）")
    args = ap.parse_args()
    Site(pathlib.Path(args.out)).build()
