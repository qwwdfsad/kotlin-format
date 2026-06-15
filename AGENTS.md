# kotlin-format

A small, self-contained study of **Kotlin code layout**: where the common greedy formatter
(`ktfmt`) diverges from an **optimizing** layout model called **optofmt**, and which one reads
as more idiomatic Kotlin.

It is meant to be reusable: tweak the optofmt rules and regenerate, or drop in a new Kotlin
snippet, and the report updates.

## What's here

| Path | What it is |
| --- | --- |
| `RULES.md` | The **optofmt** rules — how the optimizing model lays out Kotlin, in plain language. The source of truth; you should be able to format a snippet from these alone. |
| `snippets.py` | The corpus: one entry per distinct layout problem, each with the `ktfmt` output, the `optofmt` output, an optional better third option, source, and notes. |
| `generate.py` | Builds `report.html` (and `diff.html` after a rules change). |
| `report.html` | The report — generated; open it in a browser. |
| `download-ktfmt.sh` | Fetches the greedy formatter jar into `vendor/` (pinned to a released version, checksum-verified). The jar is **not** committed. |
| `ktfmt.sh` | Runs the formatter: `./ktfmt.sh -` formats stdin in Kotlin-language style (4-space, 100 cols). |
| `.claude/skills/` | Two skills (below). |

## The report

Each snippet is the same Kotlin shown in two columns by default — **ktfmt** (greedy) and
**optofmt** (optimizing) — with a **third column** when a strictly better option exists that
neither formatter produces. The **most idiomatic** column is outlined in **red**; amber marks
any line past the 100-column limit. Every card names the pattern it demonstrates and keeps a
"why" and a source.

ktfmt columns are real formatter output. optofmt columns are the layout entailed by `RULES.md`
(applied by hand — there is no optofmt binary).

## Setup & regenerate

```sh
./download-ktfmt.sh        # one-time: fetch vendor/ktfmt.jar (needs a JDK 11+ and network)
python3 generate.py        # writes report.html
```

`generate.py` itself needs no jar (it renders stored layouts); the jar is only needed to
(re)format Kotlin via `./ktfmt.sh` when adding or revising snippets.

## Workflows (skills)

- **optofmt-adjust-rules** — change `RULES.md`, reformat every snippet to match, and produce
  `report.html` plus a `diff.html` showing before/after for *only* the snippets whose optofmt
  layout changed.
- **optofmt-add-snippet** — add a Kotlin snippet, but only if it shows a *new* pattern; if the
  pattern is already covered, it asks before overwriting the existing one.

When working in this repo as a Claude Code project, these are available as `/optofmt-adjust-rules`
and `/optofmt-add-snippet`.

## Conventions

- Kotlin only. Settings everywhere: **4-space indent**, **100-column limit**, ktfmt
  `--kotlinlang-style`.
- Keep `RULES.md` self-contained and human-readable — it is the spec a fresh reader (or agent)
  applies to reproduce optofmt layouts.
- Don't hand-edit `report.html` / `diff.html`; change `snippets.py` or `RULES.md` and
  regenerate.
