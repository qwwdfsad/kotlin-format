#!/usr/bin/env python3
"""Build report.html from snippets.py.

Each snippet renders two columns by default — ktfmt rectangle (--kotlinlang-style) and
ktfmt ergonomics (per RULES.md) — plus an optional third column when a strictly better
option exists.

On every run the current ktfmt ergonomics layouts are saved to .optofmt-state.json. If a
previous state exists and some snippets' ergonomics layout changed (e.g. after editing
RULES.md and reformatting), a diff.html is also written showing before/after for only the
changed snippets.

    python3 generate.py
"""
import base64
import html
import json
from pathlib import Path

from snippets import SNIPPETS

HERE = Path(__file__).resolve().parent
STATE = HERE / ".optofmt-state.json"
LIMIT = 100

COL_LABEL = {"ktfmt": "ktfmt &middot; rectangle", "optofmt": "ktfmt &middot; ergonomics",
             "third": "ktfmt &middot; ergonomics v2"}


def esc(t):
    return html.escape(t)


def code_block(text):
    """Emit raw Kotlin for highlight.js. The over-100-column line indices are passed via
    data-over so the client can re-apply the amber marking after highlighting + line split."""
    lines = text.splitlines() or [""]
    over = ",".join(str(i) for i, ln in enumerate(lines) if len(ln) > LIMIT)
    code = esc("\n".join(lines))
    return (f'<pre><code class="language-kotlin" data-over="{over}">{code}</code></pre>')


def columns(panes):
    """panes: list of (key, label, code)."""
    texts = [c for _, _, c in panes]
    cells = []
    for i, (key, label, code) in enumerate(panes):
        earlier = next((panes[j][1] for j in range(i) if texts[j] == code), None)
        same = ' <span class="same">&equiv; identical</span>' if earlier else ""
        cells.append(f'''<div class="col">
        <div class="hd {key}">{label}{same}</div>
        {code_block(code)}
      </div>''')
    grid = "cols3" if len(panes) == 3 else "cols"
    return f'<div class="{grid}">\n      ' + "\n      ".join(cells) + "\n    </div>"


def panes_for(d):
    """The rectangle pane, an optional ergonomics pane (omitted when `optofmt` is absent
    or None — e.g. when it would be equivalent to rectangle), and an optional third. A
    `third` entry may be a plain code string (labelled "ergonomics v2") or a {"label",
    "code"} dict."""
    panes = [("ktfmt", COL_LABEL["ktfmt"], d["ktfmt"])]
    if d.get("optofmt") is not None:
        panes.append(("optofmt", COL_LABEL["optofmt"], d["optofmt"]))
    third = d.get("third")
    if third is not None:
        if isinstance(third, dict):
            panes.append(("third", third["label"], third["code"]))
        else:
            panes.append(("third", COL_LABEL["third"], third))
    return panes


def card(s):
    panes = panes_for(s)
    note = f'<p class="note">{s["note"]}</p>' if s.get("note") else ""
    extras = "".join(
        f'''
      <div class="extra">
        <p class="thesis">{ex["note"]}</p>
        {columns(panes_for(ex))}
      </div>'''
        for ex in s.get("extra", []))
    return f'''
    <section class="card">
      <h2>{esc(s["name"]).replace("`", "")} <span class="src">{s["source"]}</span></h2>
      <p class="thesis">{s["thesis"]}</p>
      {columns(panes)}
      {extras}
      {note}
    </section>'''


STYLE = """
  /* Dark is the base palette; light overrides below. */
  :root, :root[data-theme="dark"] {
          --bg:#0f1115; --panel:#171a21; --line:#262b36; --txt:#d7dce5; --mut:#8b94a7;
          --grn:#3fb950; --red:#f85149; --amb:#d29922; --acc:#58a6ff; --pur:#bc8cff;
          --code-bg:#222733;
          --grn-bg:rgba(63,185,80,.16); --mut-bg:rgba(139,148,167,.16); --over:rgba(210,153,34,.18);
          /* IntelliJ Darcula editor scheme */
          --pre-bg:#2b2b2b; --syn-fg:#a9b7c6; --syn-kw:#cc7832; --syn-num:#6897bb; --syn-str:#6a8759;
          --syn-comment:#808080; --syn-fn:#ffc66d; --syn-annot:#bbb529; --syn-prop:#9876aa; }
  :root[data-theme="light"] {
          --bg:#ffffff; --panel:#f6f8fa; --line:#d0d7de; --txt:#1f2328; --mut:#656d76;
          --grn:#1a7f37; --red:#cf222e; --amb:#9a6700; --acc:#0969da; --pur:#8250df;
          --code-bg:#eaeef2;
          --grn-bg:rgba(26,127,55,.12); --mut-bg:rgba(101,109,118,.12); --over:rgba(154,103,0,.16);
          /* IntelliJ Light editor scheme */
          --pre-bg:#ffffff; --syn-fg:#080808; --syn-kw:#0033b3; --syn-num:#1750eb; --syn-str:#067d17;
          --syn-comment:#8c8c8c; --syn-fn:#00627a; --syn-annot:#9e880d; --syn-prop:#871094; }
  @media (prefers-color-scheme: light) {
    :root[data-theme="system"] {
          --bg:#ffffff; --panel:#f6f8fa; --line:#d0d7de; --txt:#1f2328; --mut:#656d76;
          --grn:#1a7f37; --red:#cf222e; --amb:#9a6700; --acc:#0969da; --pur:#8250df;
          --code-bg:#eaeef2;
          --grn-bg:rgba(26,127,55,.12); --mut-bg:rgba(101,109,118,.12); --over:rgba(154,103,0,.16);
          /* IntelliJ Light editor scheme */
          --pre-bg:#ffffff; --syn-fg:#080808; --syn-kw:#0033b3; --syn-num:#1750eb; --syn-str:#067d17;
          --syn-comment:#8c8c8c; --syn-fn:#00627a; --syn-annot:#9e880d; --syn-prop:#871094; }
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--txt);
         font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif; }
  header,footer { max-width:1320px; margin:0 auto; padding:34px 28px 18px; }
  footer { padding:0 28px 50px; color:var(--mut); font-size:13px; }
  h1 { margin:0 0 10px; font-size:25px; letter-spacing:-.01em; }
  header p { color:var(--mut); max-width:92ch; margin:8px 0; }
  header.b { border-bottom:1px solid var(--line); }
  .pills { margin-top:14px; display:flex; gap:10px; flex-wrap:wrap; }
  .pill { font-size:13px; padding:4px 11px; border-radius:99px; border:1px solid var(--line);
          background:var(--panel); color:var(--mut); }
  .lead { color:var(--txt); font-size:16px; max-width:92ch; margin:10px 0 18px; }
  .engines { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:16px 0; }
  @media (max-width:900px) { .engines { grid-template-columns:1fr; } }
  .engine { border:1px solid var(--line); border-radius:10px; padding:14px 18px;
            background:var(--panel); }
  .engine h3 { margin:0 0 7px; font-size:15px; letter-spacing:-.01em; }
  .engine p { color:var(--txt); margin:0; max-width:none; font-size:14px; }
  .engine.rect { border-left:3px solid var(--amb); }
  .engine.rect h3 { color:var(--amb); }
  .engine.ergo { border-left:3px solid var(--acc); }
  .engine.ergo h3 { color:var(--acc); }
  .goal { color:var(--txt); max-width:92ch; margin:18px 0 6px; }
  .legend { color:var(--mut); max-width:92ch; margin:6px 0; font-size:13px; }
  main { max-width:1320px; margin:0 auto; padding:6px 28px 40px; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
          padding:18px 20px; margin:22px 0; }
  h2 { font-size:18px; margin:2px 0 8px; font-weight:600; }
  .src { font:12px ui-monospace,SFMono-Regular,Menlo,monospace; color:var(--mut);
         font-weight:400; margin-left:6px; }
  .thesis { color:var(--txt); margin:6px 0 14px; }
  .note { color:var(--txt); margin:14px 0 0; padding:10px 14px; border-radius:7px;
          background:var(--over); border-left:3px solid var(--amb); font-size:14px; }
  code { background:var(--code-bg); padding:1px 5px; border-radius:4px; font-size:.92em; }
  .card a { color:var(--acc); }
  .resources ul { margin:6px 0 0; padding-left:20px; }
  .resources li { margin:8px 0; }
  .resources li p { color:var(--mut); margin:2px 0 0; font-size:13px; }
  .cols { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  .cols3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }
  @media (max-width:900px) { .cols,.cols3 { grid-template-columns:1fr; } }
  .col { min-width:0; }
  .hd { font-size:12px; font-weight:600; padding:6px 10px; border-radius:7px 7px 0 0;
        border:1px solid var(--line); border-bottom:none; color:var(--mut); }
  .hd.ktfmt { color:var(--amb); }
  .hd.optofmt { color:var(--acc); }
  .hd.third { color:var(--pur); }
  .same { font-size:11px; color:var(--mut); margin-left:6px; font-weight:400; }
  .extra { margin-top:16px; padding-top:14px; border-top:1px dashed var(--line); }
  .extra .thesis { margin:0 0 12px; }
  pre { margin:0; background:var(--pre-bg); border:1px solid var(--line); border-radius:0 0 7px 7px;
        padding:12px 14px; overflow-x:auto; font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; }
  pre code { background:none; padding:0; border-radius:0; font:inherit; color:var(--syn-fg); }
  pre .line { display:block; white-space:pre; }
  pre .line:empty::after { content:" "; }
  pre .line.over { background:var(--over); }
  /* highlight.js token colors matching IntelliJ (Darcula dark / IntelliJ Light). */
  .hljs-keyword, .hljs-literal { color:var(--syn-kw); font-weight:bold; }
  .hljs-built_in, .hljs-operator, .hljs-punctuation, .hljs-params, .hljs-variable { color:var(--syn-fg); }
  .hljs-string, .hljs-char, .hljs-regexp, .hljs-subst { color:var(--syn-str); }
  .hljs-number, .hljs-symbol { color:var(--syn-num); }
  .hljs-title.function_, .hljs-section { color:var(--syn-fn); }
  .hljs-title, .hljs-title.class_, .hljs-type, .hljs-built_in.class_ { color:var(--syn-fg); }
  .hljs-attr, .hljs-attribute, .hljs-property { color:var(--syn-prop); }
  .hljs-comment, .hljs-quote { color:var(--syn-comment); }
  .hljs-meta, .hljs-meta .hljs-keyword { color:var(--syn-annot); font-weight:normal; }
  .hljs-meta .hljs-string { color:var(--syn-str); }
  details { margin-top:8px; }
  summary { cursor:pointer; color:var(--acc); font-size:13px; }
  details p { color:var(--mut); margin:8px 0 2px; max-width:92ch; }
  .theme-toggle { position:fixed; top:16px; right:18px; z-index:10; cursor:pointer;
        font:13px/1 -apple-system,Segoe UI,Roboto,sans-serif; padding:7px 13px; border-radius:99px;
        border:1px solid var(--line); background:var(--panel); color:var(--mut); }
  .theme-toggle:hover { color:var(--txt); border-color:var(--mut); }
"""


THEME_HEAD = """
<script>
  // Apply saved theme before first paint to avoid a flash. Default is system; the
  // picker toggles between light and dark.
  (function () {
    var t = localStorage.getItem("theme");
    document.documentElement.setAttribute("data-theme", (t === "light" || t === "dark") ? t : "system");
  })();
</script>"""

THEME_SCRIPT = """
<script>
  (function () {
    var LABELS = { system: "◐ System", light: "☀ Light", dark: "☾ Dark" };
    var root = document.documentElement;
    var btn = document.getElementById("theme-toggle");
    function stored() {
      var t = localStorage.getItem("theme");
      return (t === "light" || t === "dark") ? t : null;
    }
    function effective() {
      return stored() || (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
    }
    function apply() {
      var s = stored();
      root.setAttribute("data-theme", s || "system");
      btn.textContent = LABELS[s || "system"];
    }
    apply();
    btn.addEventListener("click", function () {
      localStorage.setItem("theme", effective() === "light" ? "dark" : "light");
      apply();
    });
  })();
</script>"""


# highlight.js is inlined (not loaded from a CDN) so the single report.html file highlights
# everywhere — including htmlpreview.github.io, which silently drops non-GitHub external
# <script src> tags. We embed each library as base64 and decode+run it at load time: the
# payload then contains no `<script`/`</script>` substrings, which matters because
# htmlpreview runs a naive global regex over the page that would otherwise corrupt the
# library (its XML grammar contains `/<script(?=\s|>)/`). Vendored from cdn-release@11.9.0;
# refresh via download-hljs.sh.
_HLJS_DIR = HERE / "vendor" / "hljs"


def _hljs_b64(rel):
    path = _HLJS_DIR / rel
    if not path.exists():
        raise SystemExit(f"error: {path} not found. Run ./download-hljs.sh to vendor it.")
    return base64.b64encode(path.read_bytes()).decode("ascii")


HIGHLIGHT_SCRIPT = f"""
<script>
  (function () {{
    // Decode each base64'd library and run it as a real (global-scope) script, in order.
    function run(b64) {{
      var js = new TextDecoder().decode(
        Uint8Array.from(atob(b64), function (c) {{ return c.charCodeAt(0); }}));
      var s = document.createElement("script");
      s.textContent = js;
      document.head.appendChild(s);
    }}
    run("{_hljs_b64("highlight.min.js")}");
    run("{_hljs_b64("languages/kotlin.min.js")}");
  }})();
</script>
<script>
  (function () {{
    if (!window.hljs) return;
    // Highlight the whole block (so multi-line strings/comments keep context), then split the
    // result into per-line spans, reopening any spans that cross a newline, and re-apply the
    // amber "over 100 columns" marking from data-over.
    function splitLines(htmlStr) {{
      var lines = [], open = [], buf = "";
      var re = /(<span\\b[^>]*>)|(<\\/span>)|(\\n)|([^<\\n]+)/g, m;
      while ((m = re.exec(htmlStr))) {{
        if (m[1]) {{ buf += m[1]; open.push(m[1]); }}
        else if (m[2]) {{ buf += "</span>"; open.pop(); }}
        else if (m[3]) {{ buf += "</span>".repeat(open.length); lines.push(buf); buf = open.join(""); }}
        else {{ buf += m[4]; }}
      }}
      lines.push(buf);
      return lines;
    }}
    document.querySelectorAll("pre > code.language-kotlin").forEach(function (code) {{
      var over = (code.getAttribute("data-over") || "").split(",").filter(Boolean);
      var overSet = {{}};
      over.forEach(function (i) {{ overSet[i] = true; }});
      var res = hljs.highlight(code.textContent, {{ language: "kotlin", ignoreIllegals: true }});
      code.innerHTML = splitLines(res.value).map(function (ln, i) {{
        return '<span class="line' + (overSet[i] ? " over" : "") + '">' + ln + "</span>";
      }}).join("");
      code.classList.add("hljs");
    }});
  }})();
</script>"""


def page(title, intro, body, pills=""):
    return f"""<!doctype html>
<html lang="en" data-theme="system"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{STYLE}</style>{THEME_HEAD}</head>
<body>
<button id="theme-toggle" class="theme-toggle" type="button" aria-label="Toggle theme">System</button>
<header class="b">
  <h1>{title}</h1>
  {intro}
  {pills}
</header>
<main>{body}</main>
<footer>Generated by <code>python3 generate.py</code> from <code>snippets.py</code>;
  ktfmt ergonomics rules live in <code>RULES.md</code>.</footer>
{HIGHLIGHT_SCRIPT}
{THEME_SCRIPT}
</body></html>"""


RESOURCES = '''
    <section class="card resources">
      <h2>Further reading &amp; prototype</h2>
      <p class="thesis">Related examples</p>
      <ul>
        <li>
          <a href="https://github.com/Kotlin/kotlinx.coroutines/pull/4696" target="_blank" rel="noopener">kotlinx.coroutines &middot; formatted with ktfmt (rectangle)</a>
          <p>kotlinx.coroutines reformatted with the current ktfmt engine.</p>
        </li>
        <li>
          <a href="https://github.com/Kotlin/kotlinx.coroutines/pull/4697" target="_blank" rel="noopener">kotlinx.coroutines &middot; formatted with ktfmt (ergonomics)</a>
          <p>The same repository reformatted with the ktfmt ergonomics engine.</p>
        </li>
        <li>
          <a href="https://github.com/qwwdfsad/ktfmt/pull/2" target="_blank" rel="noopener">Try out the prototype</a>
          <p>An experimental implementation of the ergonomics engine &mdash; but read the disclaimer.</p>
        </li>
      </ul>
    </section>'''


def build_report():
    intro = (
        '<p class="lead">The page presents a comparison between two potential ktfmt '
        'engines &mdash; <b>&ldquo;The Rectangle Rule&rdquo;</b>, the current ktfmt engine, '
        'and a potential new one &mdash; <b>&ldquo;The ergonomics rule&rdquo;</b>.</p>'
        '<div class="engines">'
        '<div class="engine rect"><h3>The Rectangle Rule</h3>'
        '<p>a strict engine that follows the corresponding '
        '<a href="https://github.com/google/google-java-format/wiki/The-Rectangle-Rule" '
        'target="_blank" rel="noopener">rule</a>. It is very strict and predictable '
        '&mdash; every syntax subtree is in its own bounding rectangle, it is very local '
        "(changes in one line rarely affect surrounding lines&rsquo; formatting) and thus "
        'Git-history-friendly. Because of these properties, it also produces quite a few '
        'newlines and additional layers of tabular nesting</p></div>'
        '<div class="engine ergo"><h3>The ergonomics rule</h3>'
        '<p>an engine that prioritizes concise and ergonomic Kotlin. Its goal is to '
        'format code in a compact manner, minimizing its width and length, but without '
        'general loss of readability. It subjectively improves information density but with '
        'the opposite tradeoffs &mdash; it is less predictable and less local.</p></div>'
        '</div>'
        '<p class="goal"><b>Our goal is to understand the stylistic preferences of Kotlin '
        'developers.</b> So the current page has a series of snippets formatted in two ways '
        'to showcase the difference between these two engines, for you to pick the one you '
        'prefer. Some snippets are grouped in a way that shows how the code might evolve '
        'over time to showcase formatting locality (or lack of thereof).</p>'
        '<p class="legend">Both use <b>4-space indent</b> and a <b>100-column limit</b>; '
        'amber marks any line past 100 columns.</p>')
    pills = f'<div class="pills"><span class="pill">{len(SNIPPETS)} patterns</span></div>'
    body = "".join(card(s) for s in SNIPPETS) + RESOURCES
    (HERE / "report.html").write_text(page("ktfmt code style comparison", intro, body, pills))


def build_diff():
    """Write diff.html for snippets whose optofmt changed vs the saved state."""
    prev = json.loads(STATE.read_text()) if STATE.exists() else None
    cur = {s["id"]: s["optofmt"] for s in SNIPPETS}
    by_id = {s["id"]: s for s in SNIPPETS}
    changed = []
    if prev is not None:
        changed = [sid for sid, code in cur.items() if sid in prev and prev[sid] != code]
    STATE.write_text(json.dumps(cur, indent=2))
    if not changed:
        # nothing to diff; remove a stale diff if present
        (HERE / "diff.html").unlink(missing_ok=True)
        return 0
    cards = []
    for sid in changed:
        s = by_id[sid]
        panes = [("ktfmt", "ktfmt ergonomics &middot; before", prev[sid]),
                 ("optofmt", "ktfmt ergonomics &middot; after", cur[sid])]
        cards.append(f'''
    <section class="card">
      <h2>{esc(s["name"]).replace("`", "")} <span class="src">{s["source"]}</span></h2>
      {columns(panes)}
    </section>''')
    intro = ('<p>ktfmt ergonomics layouts that changed since the last run (e.g. after editing '
             '<code>RULES.md</code> and reformatting). Only changed snippets are shown.</p>')
    (HERE / "diff.html").write_text(page("ktfmt ergonomics diff — before / after", intro, "".join(cards)))
    return len(changed)


if __name__ == "__main__":
    build_report()
    n_changed = build_diff()
    msg = f"Wrote report.html ({len(SNIPPETS)} patterns)"
    if n_changed:
        msg += f"; wrote diff.html ({n_changed} changed)"
    print(msg)
