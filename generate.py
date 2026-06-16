#!/usr/bin/env python3
"""Build report.html from snippets.py.

Each snippet renders two columns by default — ktfmt (greedy) and optofmt (optimizing, per
RULES.md) — plus an optional third column when a strictly better option exists. The most
idiomatic column is highlighted in red.

On every run the current optofmt layouts are saved to .optofmt-state.json. If a previous
state exists and some snippets' optofmt changed (e.g. after editing RULES.md and reformatting),
a diff.html is also written showing before/after for only the changed snippets.

    python3 generate.py
"""
import html
import json
from pathlib import Path

from snippets import SNIPPETS

HERE = Path(__file__).resolve().parent
STATE = HERE / ".optofmt-state.json"
LIMIT = 100

COL_LABEL = {"ktfmt": "ktfmt &middot; greedy", "optofmt": "optofmt &middot; optimizing"}


def esc(t):
    return html.escape(t)


def code_block(text):
    rows = []
    for ln in text.splitlines():
        over = ' class="over"' if len(ln) > LIMIT else ""
        rows.append(f"<span{over}>{esc(ln) or '&nbsp;'}</span>")
    return "<pre>" + "\n".join(rows) + "</pre>"


def columns(panes, idiomatic):
    """panes: list of (key, label, code). idiomatic: key to highlight red, or 'parity'."""
    texts = [c for _, _, c in panes]
    cells = []
    for i, (key, label, code) in enumerate(panes):
        earlier = next((panes[j][1] for j in range(i) if texts[j] == code), None)
        same = ' <span class="same">&equiv; identical</span>' if earlier else ""
        is_idio = key == idiomatic
        tag = ' <span class="best">idiomatic</span>' if is_idio else ""
        cls = "col" + (" idiomatic" if is_idio else "")
        cells.append(f'''<div class="{cls}">
        <div class="hd {key}">{label}{tag}{same}</div>
        {code_block(code)}
      </div>''')
    grid = "cols3" if len(panes) == 3 else "cols"
    return f'<div class="{grid}">\n      ' + "\n      ".join(cells) + "\n    </div>"


def card(s):
    panes = [("ktfmt", COL_LABEL["ktfmt"], s["ktfmt"]),
             ("optofmt", COL_LABEL["optofmt"], s["optofmt"])]
    if s.get("third"):
        panes.append(("third", s["third"]["label"], s["third"]["code"]))
    why = f'<details><summary>Why</summary><p>{s["why"]}</p></details>' if s.get("why") else ""
    verdict = {"optofmt": "optofmt wins", "ktfmt": "ktfmt wins",
               "third": "neither — see column 3", "parity": "parity"}[s["idiomatic"]]
    vcls = "parity" if s["idiomatic"] == "parity" else "win"
    extras = "".join(
        f'''
      <div class="extra">
        <p class="thesis"><span class="same-rule">same rule</span> {ex["note"]}</p>
        {columns([("ktfmt", COL_LABEL["ktfmt"], ex["ktfmt"]),
                  ("optofmt", COL_LABEL["optofmt"], ex["optofmt"])], ex.get("idiomatic", s["idiomatic"]))}
      </div>'''
        for ex in s.get("extra", []))
    return f'''
    <section class="card">
      <h2>{esc(s["name"]).replace("`", "")} <span class="src">{s["source"]}</span>
        <span class="verdict {vcls}">{verdict}</span></h2>
      <p class="thesis">{s["thesis"]}</p>
      {columns(panes, s["idiomatic"])}
      {extras}
      {why}
    </section>'''


STYLE = """
  :root { --bg:#0f1115; --panel:#171a21; --line:#262b36; --txt:#d7dce5; --mut:#8b94a7;
          --grn:#3fb950; --red:#f85149; --amb:#d29922; --acc:#58a6ff; --pur:#bc8cff; }
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
  main { max-width:1320px; margin:0 auto; padding:6px 28px 40px; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
          padding:18px 20px; margin:22px 0; }
  h2 { font-size:18px; margin:2px 0 8px; font-weight:600; }
  .src { font:12px ui-monospace,SFMono-Regular,Menlo,monospace; color:var(--mut);
         font-weight:400; margin-left:6px; }
  .verdict { font-size:11px; padding:2px 8px; border-radius:6px; margin-left:8px;
             vertical-align:2px; font-weight:600; }
  .verdict.win { background:rgba(63,185,80,.16); color:var(--grn); }
  .verdict.parity { background:rgba(139,148,167,.16); color:var(--mut); }
  .thesis { color:var(--txt); margin:6px 0 14px; }
  code { background:#222733; padding:1px 5px; border-radius:4px; font-size:.92em; }
  .cols { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  .cols3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }
  @media (max-width:900px) { .cols,.cols3 { grid-template-columns:1fr; } }
  .col { min-width:0; }
  .hd { font-size:12px; font-weight:600; padding:6px 10px; border-radius:7px 7px 0 0;
        border:1px solid var(--line); border-bottom:none; color:var(--mut); }
  .hd.ktfmt { color:var(--amb); }
  .hd.optofmt { color:var(--acc); }
  .hd.third { color:var(--pur); }
  .col.idiomatic .hd { color:var(--grn); border-color:var(--grn); }
  .col.idiomatic pre { border-color:var(--grn); box-shadow:inset 3px 0 0 var(--grn); }
  .best { font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:var(--grn);
          border:1px solid var(--grn); border-radius:5px; padding:1px 5px; margin-left:6px; }
  .same { font-size:11px; color:var(--mut); margin-left:6px; font-weight:400; }
  .extra { margin-top:16px; padding-top:14px; border-top:1px dashed var(--line); }
  .extra .thesis { margin:0 0 12px; }
  .same-rule { font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:var(--acc);
          border:1px solid var(--acc); border-radius:5px; padding:1px 5px; margin-right:6px; }
  pre { margin:0; background:#0c0e13; border:1px solid var(--line); border-radius:0 0 7px 7px;
        padding:12px 14px; overflow-x:auto; font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; }
  pre span { display:block; white-space:pre; }
  pre span.over { background:rgba(210,153,34,.18); }
  details { margin-top:8px; }
  summary { cursor:pointer; color:var(--acc); font-size:13px; }
  details p { color:var(--mut); margin:8px 0 2px; max-width:92ch; }
"""


def page(title, intro, body, pills=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{STYLE}</style></head>
<body>
<header class="b">
  <h1>{title}</h1>
  {intro}
  {pills}
</header>
<main>{body}</main>
<footer>Generated by <code>python3 generate.py</code> from <code>snippets.py</code>;
  optofmt rules live in <code>RULES.md</code>.</footer>
</body></html>"""


def build_report():
    wins = sum(1 for s in SNIPPETS if s["idiomatic"] == "optofmt")
    parity = sum(1 for s in SNIPPETS if s["idiomatic"] == "parity")
    ktwins = sum(1 for s in SNIPPETS if s["idiomatic"] == "ktfmt")
    thirds = sum(1 for s in SNIPPETS if s["idiomatic"] == "third")
    intro = (
        '<p>Each snippet is the same Kotlin formatted two ways: <b>ktfmt</b> '
        '(<code>--kotlinlang-style</code>, the greedy engine) on the left, and <b>optofmt</b> '
        '(the optimizing model in <code>RULES.md</code>) on the right. A third column appears '
        'when a strictly better option exists that neither formatter produces. Both use '
        '<b>4-space indent</b> and a <b>100-column limit</b>.</p>'
        '<p>The <span style="color:var(--grn);font-weight:600">idiomatic</span> column is '
        'outlined in green; amber marks any line past 100 columns. ktfmt output is real; optofmt '
        'output is the layout entailed by the rules.</p>')
    pills = (f'<div class="pills"><span class="pill">{len(SNIPPETS)} patterns</span>'
             f'<span class="pill">{wins} optofmt wins</span>'
             f'<span class="pill">{parity} parity</span>'
             f'<span class="pill">{ktwins} ktfmt wins</span>'
             f'<span class="pill">{thirds} better 3rd option</span></div>')
    body = "".join(card(s) for s in SNIPPETS)
    (HERE / "report.html").write_text(page("ktfmt vs optofmt", intro, body, pills))
    return wins, parity, ktwins


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
        panes = [("ktfmt", "optofmt &middot; before", prev[sid]),
                 ("optofmt", "optofmt &middot; after", cur[sid])]
        cards.append(f'''
    <section class="card">
      <h2>{esc(s["name"]).replace("`", "")} <span class="src">{s["source"]}</span></h2>
      {columns(panes, "optofmt")}
    </section>''')
    intro = ('<p>optofmt layouts that changed since the last run (e.g. after editing '
             '<code>RULES.md</code> and reformatting). Only changed snippets are shown.</p>')
    (HERE / "diff.html").write_text(page("optofmt diff — before / after", intro, "".join(cards)))
    return len(changed)


if __name__ == "__main__":
    wins, parity, ktwins = build_report()
    n_changed = build_diff()
    msg = f"Wrote report.html ({len(SNIPPETS)} patterns: {wins} optofmt, {parity} parity, {ktwins} ktfmt)"
    if n_changed:
        msg += f"; wrote diff.html ({n_changed} changed)"
    print(msg)
