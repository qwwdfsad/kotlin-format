# kotlin-format

## Note from Seva

Most of the content in this repo is **agent-generated**. It is meant to be a playground 
for experimentation and exploration for the potential ktfmt change,
but beware of weird fluctuations in the output and inconsistencies, as well as do not
try to make a lot of sense from anything but [report.html](report.html) code snippets.
`.md` files are mostly write-only, don't waste your time on them.

The optimized layout is not in fact guaranteed, and I rely on the ability of the agent to reproduce
the output from the somehow-synthesized [RULES.md](RULES.md).

The column-limit is 100 to make snippets-generation easier, it's not an actual production target.

**Quickstart**:
* Look at [report.html](report.html). It is nice
* Run `claude` -- ask it to add your snippet to the report and see if it is a duplicate
* If you don't like one of the results -- write me, there is probably a rule missing

====== End of human-written content ===== 

**Greedy vs. optimizing Kotlin layout, side by side.**

The same Kotlin, formatted two ways: by `ktfmt` (a greedy, line-at-a-time formatter) and by
**optofmt** — an *optimizing* layout model that chooses line breaks globally and reuses one
indentation size for every step. The output reads like hand-written idiomatic Kotlin (the
style of the kotlinx libraries). This repo collects the cases where the two diverge, says which
is more idiomatic, and explains why.

It's small and self-contained: tweak the rules and regenerate, or drop in a new snippet, and
the report updates.

## Quickstart

```sh
./download-ktfmt.sh        # one-time: fetch the formatter jar into vendor/ (needs JDK 11+)
python3 generate.py        # build report.html
open report.html           # (macOS) or open it in any browser
```

`generate.py` needs no jar to render — it ships the stored layouts. The jar is only used to
(re)format Kotlin when you add or revise a snippet.

## What the report shows

Each card is one **layout pattern**, with the same Kotlin in two columns by default:

- **ktfmt** — real output of the greedy formatter (`--kotlinlang-style`).
- **optofmt** — the layout entailed by the rules in [`RULES.md`](RULES.md).

A **third column** appears when a strictly better option exists that neither formatter produces
(e.g. a refactor). The **idiomatic** column is outlined in **green**; **amber** marks any line
past the 100-column limit. Every card keeps a one-line thesis, a "why", and a source.

Current tally: **12 patterns — 9 optofmt wins, 2 parity, 1 with a better third option.**

## optofmt in a nutshell

The full spec is [`RULES.md`](RULES.md); the gist:

- **One indentation size.** Wrapped parts sit exactly one level deeper — never a second
  "continuation" level, never drifting further right per operand.
- **Keep the introducer attached.** Don't break after `=`, the supertype `:`, or an infix call
  like `to` just to indent the right-hand side; wrap its body/list instead.
- **Indent economy.** Let nested openers share a line and closers stack (`))`), so nested
  groups share one body indent instead of staircasing.
- **Lists are compact or fully split** — never a half-packed "fill" — and the final item (a
  trailing lambda, say) may expand in place while leading items stay inline.
- **Global break choice.** When something must wrap, minimize the worst overflow, then the
  number of lines, then nesting depth.
- **Leave prose alone.** Comments and KDoc are never reflowed; grouped one-liners stay tight;
  declaration headers keep their modifiers on one line.

## Repository layout

| Path | What it is |
| --- | --- |
| [`RULES.md`](RULES.md) | The optofmt rules — the source of truth, in plain language. |
| `snippets.py` | The corpus: one entry per pattern (ktfmt output, optofmt output, source, notes). |
| `generate.py` | Builds `report.html` (and `diff.html` after a rules change). |
| `report.html` | The report (generated). |
| `download-ktfmt.sh` | Fetches the pinned, checksum-verified formatter jar into `vendor/`. |
| `ktfmt.sh` | Runs the formatter: `./ktfmt.sh -` formats stdin. |
| `.claude/skills/` | Two skills (below). |
| [`AGENTS.md`](AGENTS.md) | Notes for working in the repo with an agent. |

## Workflows

Two skills automate the upkeep (available as `/optofmt-adjust-rules` and `/optofmt-add-snippet`
when the repo is opened as a Claude Code project):

- **optofmt-adjust-rules** — change `RULES.md`, reformat every snippet to match, and produce
  `report.html` plus a `diff.html` showing the before/after of *only* the snippets whose layout
  changed.
- **optofmt-add-snippet** — add a Kotlin snippet, but only if it shows a *new* pattern; if the
  pattern is already covered, it asks before overwriting.

## Conventions

Kotlin only. Everywhere: **4-space indent**, **100-column limit**, ktfmt `--kotlinlang-style`.
Don't hand-edit `report.html`/`diff.html` — change `snippets.py` or `RULES.md` and regenerate.
