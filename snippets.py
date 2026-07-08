"""The ktfmt-comparison corpus: one entry per distinct layout problem.

Each entry:
  id        - stable slug
  name      - the pattern/problem, used as the card title
  source    - where the example came from
  thesis    - one-line summary shown under the title
  why       - longer explanation (collapsed under "Why")
  input     - raw Kotlin (what you'd paste in); ktfmt output is reproducible from it
  ktfmt     - real `./ktfmt.sh` output, the ktfmt rectangle column (Kotlin-language
              style, 4-space, 100 cols)
  optofmt   - the ktfmt ergonomics layout per RULES.md
  third     - optional {"label", "code"}: a strictly better option neither column
              produces (e.g. a refactor); shown as a third column when present
  idiomatic - retained for reference only; no longer rendered:
              "optofmt" | "ktfmt" | "third" | "parity"

The ktfmt column is stored verbatim from the bundled formatter (rectangle). The optofmt
column is the ktfmt ergonomics layout expected from the rules in RULES.md; regenerate/
verify them with the skills.
"""

SNIPPETS = [
    {
        "id": "boolean-condition",
        "name": "Boolean conditions",
        "source": "kotlinx.coroutines · JobSupport.kt:273",
        "thesis": "A single condition is laid out identically by both engines; adding more conditions forces a wrap, where they diverge.",
        "input": "fun f() { if (unwrapped !== rootCause) { rootCause.addSuppressed(unwrapped) } }",
        "ktfmt": """fun f() {
    if (unwrapped !== rootCause) {
        rootCause.addSuppressed(unwrapped)
    }
}""",
        "optofmt": """fun f() {
    if (unwrapped !== rootCause) {
        rootCause.addSuppressed(unwrapped)
    }
}""",
        "idiomatic": "parity",
        "extra": [{
            "note": "Add more conditions and the line must wrap: ktfmt ergonomics keeps every operand "
                    "at one indent; ktfmt rectangle pushes each operand after the first a level deeper. "
                    "A third option keeps the first condition on the <code>if</code> line.",
            "ktfmt": """fun f() {
    if (
        unwrapped !== rootCause &&
            unwrapped !== unwrappedCause &&
            unwrapped !is CancellationException &&
            seenExceptions.add(unwrapped)
    ) {
        rootCause.addSuppressed(unwrapped)
    }
}""",
            "optofmt": """fun f() {
    if (
        unwrapped !== rootCause &&
        unwrapped !== unwrappedCause &&
        unwrapped !is CancellationException &&
        seenExceptions.add(unwrapped)
    ) {
        rootCause.addSuppressed(unwrapped)
    }
}""",
            "third": """fun f() {
    if (unwrapped !== rootCause &&
        unwrapped !== unwrappedCause &&
        unwrapped !is CancellationException &&
        seenExceptions.add(unwrapped)
    ) {
        rootCause.addSuppressed(unwrapped)
    }
}""",
        }],
    },
    {
        "id": "nested-long-argument",
        "name": "Nested call with a long argument",
        "source": "synthetic example",
        "thesis": "A short nested call fits on one line and both engines agree; rename the inner argument to something long enough to overflow and the call must wrap.",
        "input": "fun f() { registerHandler(buildHandler(handler)) }",
        "ktfmt": """fun f() {
    registerHandler(buildHandler(handler))
}""",
        "optofmt": """fun f() {
    registerHandler(buildHandler(handler))
}""",
        "idiomatic": "parity",
        "extra": [{
            "note": "Rename the argument to one long enough to overflow, and the inner call must "
                    "break. ktfmt rectangle staircases the openers, dropping <code>buildHandler(</code> "
                    "and then the argument onto successively deeper lines. ktfmt ergonomics hugs the two "
                    "openers (<code>registerHandler(buildHandler(</code>) so the body sits at one indent "
                    "and the call closes with a shared <code>))</code>.",
            "ktfmt": """fun f() {
    registerHandler(
        buildHandler(
            aLongUnbreakableHandlerArgumentDeliberatelySizedToOverflowTheHundredColumnLimit
        )
    )
}""",
            "optofmt": """fun f() {
    registerHandler(buildHandler(
        aLongUnbreakableHandlerArgumentDeliberatelySizedToOverflowTheHundredColumnLimit,
    ))
}""",
        }],
    },
    {
        "id": "indent-economy",
        "name": "Nested call argument wrapping",
        "source": "icpc/live-v3 · Rules.kt:219",
        "thesis": "A single nested-call argument — positional or named — reads compactly under ktfmt ergonomics: it hugs the openers so the body sits at one indent, where ktfmt rectangle staircases each opener onto its own line. With several arguments both engines split one per line and agree.",
        "why": "When an outer call's single argument is itself a call that must wrap, ktfmt ergonomics breaks "
               "after the outer <code>(</code>, hangs the inner call on its own indented line, and lets "
               "it wrap one further level in; it does <em>not</em> collapse the two openers onto one "
               "line (an earlier ktfmt ergonomics did — §5 now reserves opener-hugging for block bodies such as "
               "trailing lambdas and <code>object</code> expressions). So a positional nested call "
               "matches ktfmt rectangle line-for-line. The difference appears once the argument is "
               "<em>named</em>: ktfmt ergonomics treats the argument's <code>=</code> as an introducer (§3) and "
               "keeps <code>queue = OverrideQueue(</code> whole, so the body sits at a single indent; "
               "ktfmt rectangle breaks after <code>queue =</code> first, pushing the body a further level right. "
               "The third column, <em>ktfmt ergonomics v2</em>, revives opener-hugging whenever the outer "
               "call has a <em>single</em> nested-call argument, named or not: it collapses the two openers "
               "onto one line (<code>add(OverrideQueue(</code> or <code>add(queue = OverrideQueue(</code>) and "
               "closes with a shared <code>))</code>, saving an indent level. The rule keys on argument "
               "<em>count</em>, not on whether the argument is named — with two or more arguments there is no "
               "single opener to hug, so the outer list simply splits one per line and v2 lands back on the "
               "ergonomics layout. So v2 diverges from ergonomics only when there is exactly one argument; "
               "everywhere else in this family the two are identical.",
        "input": "fun f() { add(OverrideQueue(queueSettings.waitTime, queueSettings.firstToSolveWaitTime, "
                 "queueSettings.featuredRunWaitTime, queueSettings.inProgressRunWaitTime, "
                 "queueSettings.maxQueueSize, queueSettings.maxUntestedRun)) }",
        "ktfmt": """fun f() {
    add(
        OverrideQueue(
            queueSettings.waitTime,
            queueSettings.firstToSolveWaitTime,
            queueSettings.featuredRunWaitTime,
            queueSettings.inProgressRunWaitTime,
            queueSettings.maxQueueSize,
            queueSettings.maxUntestedRun,
        )
    )
}""",
        "optofmt": """fun f() {
    add(OverrideQueue(
        queueSettings.waitTime,
        queueSettings.firstToSolveWaitTime,
        queueSettings.featuredRunWaitTime,
        queueSettings.inProgressRunWaitTime,
        queueSettings.maxQueueSize,
        queueSettings.maxUntestedRun,
    ))
}""",
        "idiomatic": "parity",
        "extra": [{
            "note": "Name the single argument and ktfmt rectangle breaks after <code>queue =</code> "
                    "<em>as well</em>, staircasing the arguments to indent 16 — three levels deep. "
                    "ktfmt ergonomics hugs the openers, keeping <code>add(queue = OverrideQueue(</code> "
                    "on one line so the body sits at a single indent. A virtual ergonomics v2 keeps "
                    "<code>queue = OverrideQueue(</code> together but drops it to its own line under "
                    "<code>add(</code>.",
            "ktfmt": """fun f() {
    add(
        queue =
            OverrideQueue(
                queueSettings.waitTime,
                queueSettings.firstToSolveWaitTime,
                queueSettings.featuredRunWaitTime,
                queueSettings.inProgressRunWaitTime,
                queueSettings.maxQueueSize,
                queueSettings.maxUntestedRun,
            )
    )
}""",
            "optofmt": """fun f() {
    add(queue = OverrideQueue(
        queueSettings.waitTime,
        queueSettings.firstToSolveWaitTime,
        queueSettings.featuredRunWaitTime,
        queueSettings.inProgressRunWaitTime,
        queueSettings.maxQueueSize,
        queueSettings.maxUntestedRun,
    ))
}""",
            "third": """fun f() {
    add(
        queue = OverrideQueue(
            queueSettings.waitTime,
            queueSettings.firstToSolveWaitTime,
            queueSettings.featuredRunWaitTime,
            queueSettings.inProgressRunWaitTime,
            queueSettings.maxQueueSize,
            queueSettings.maxUntestedRun,
    ))
}""",
            "idiomatic": "optofmt",
        }, {
            "note": "Two named arguments, each an expandable call. The outer list splits one item per "
                    "line, and this is <em>not</em> parity: ktfmt ergonomics keeps each named-argument "
                    "<code>=</code> introducer attached, so <code>queue = OverrideQueue(</code> stays whole "
                    "and its body sits at indent 12, while ktfmt rectangle breaks after every "
                    "<code>=</code>, staircasing each branch's arguments down to indent 16.",
            "ktfmt": """fun f() {
    add(
        queue =
            OverrideQueue(
                queueSettings.waitTime,
                queueSettings.firstToSolveWaitTime,
                queueSettings.featuredRunWaitTime,
                queueSettings.inProgressRunWaitTime,
                queueSettings.maxQueueSize,
                queueSettings.maxUntestedRun,
            ),
        foo =
            OverrideQueue(
                queueSettings.waitTime,
                queueSettings.firstToSolveWaitTime,
                queueSettings.featuredRunWaitTime,
                queueSettings.inProgressRunWaitTime,
                queueSettings.maxQueueSize,
                queueSettings.maxUntestedRun,
            ),
    )
}""",
            "optofmt": """fun f() {
    add(
        queue = OverrideQueue(
            queueSettings.waitTime,
            queueSettings.firstToSolveWaitTime,
            queueSettings.featuredRunWaitTime,
            queueSettings.inProgressRunWaitTime,
            queueSettings.maxQueueSize,
            queueSettings.maxUntestedRun,
        ),
        foo = OverrideQueue(
            queueSettings.waitTime,
            queueSettings.firstToSolveWaitTime,
            queueSettings.featuredRunWaitTime,
            queueSettings.inProgressRunWaitTime,
            queueSettings.maxQueueSize,
            queueSettings.maxUntestedRun,
        ),
    )
}
""",
            "idiomatic": "optofmt",
        }],
    },
    {
        "id": "infix-attached",
        "name": "Infix call (`to`) stays attached",
        "source": "icpc/live-v3 · OverrideOrganizations",
        "thesis": "ktfmt ergonomics keeps the key and the call opener together; ktfmt rectangle breaks after `to` and double-indents.",
        "why": "ktfmt rectangle breaks after the infix <code>to</code> and indents the call an extra level, "
               "leaving <code>to</code> dangling at the end of a line. ktfmt ergonomics keeps the introducer "
               "attached to the opener it introduces — <code>orgInfo.id to "
               "OverrideOrganizations.Override(</code> stays on one line and only the argument list "
               "wraps, exactly as a human writes a key/value pair.",
        "input": "val pair = orgInfo.id to OverrideOrganizations.Override(fullName = "
                 "substituteRaw(fullName), displayName = substituteRaw(displayName))",
        "ktfmt": """val pair =
    orgInfo.id to
        OverrideOrganizations.Override(
            fullName = substituteRaw(fullName),
            displayName = substituteRaw(displayName),
        )""",
        "optofmt": """val pair = orgInfo.id to OverrideOrganizations.Override(
    fullName = substituteRaw(fullName),
    displayName = substituteRaw(displayName),
)
""",
        "idiomatic": "optofmt",
        "extra": [{
            "note": "Add an explicit type and the header no longer fits — "
                    "<code>val pair: Pair&lt;…&gt; = orgInfo.id to OverrideOrganizations.Override(</code> "
                    "is 110 columns. Even so, ktfmt ergonomics does <em>not</em> break after <code>=</code>: "
                    "it keeps <code>= orgInfo.id to OverrideOrganizations</code> on the first line and "
                    "wraps at the <code>.Override</code> call, dropping it to a single indent. ktfmt "
                    "rectangle breaks after <em>both</em> <code>=</code> and <code>to</code>, staircasing "
                    "the call three levels deep.",
            "ktfmt": """val pair: Pair<OrganizationId, OverrideOrganizations.Override> =
    orgInfo.id to
        OverrideOrganizations.Override(
            fullName = substituteRaw(fullName),
            displayName = substituteRaw(displayName),
        )""",
            "optofmt": """val pair: Pair<OrganizationId, OverrideOrganizations.Override> = orgInfo.id to OverrideOrganizations
    .Override(fullName = substituteRaw(fullName), displayName = substituteRaw(displayName))""",
            "idiomatic": "optofmt",
        }],
    },
    {
        "id": "supertype-attached",
        "name": "Supertype constructor call stays attached to `:`",
        "source": "icpc/live-v3 · ClicsArchiveCommand",
        "thesis": "ktfmt ergonomics keeps `Name : Base(` on one line; ktfmt rectangle breaks after `:` and strands the supertype.",
        "why": "<code>object X : DumpFileCommand(</code> fits on one line, but ktfmt rectangle breaks after the "
               "supertype <code>:</code> and indents the constructor call an extra level, leaving the "
               "supertype name alone on its own line. ktfmt ergonomics keeps the introducer attached and wraps "
               "only the argument list — same family as not breaking after <code>=</code>.",
        "input": "object ClicsArchiveCommand : DumpFileCommand(name = \"clics-archive\", help = "
                 "\"Dump CLICS contest archive (zip)\", defaultFileName = \"contest-archive.zip\", "
                 "outputHelp = \"Path to new zip file\") {\n}",
        "ktfmt": """object ClicsArchiveCommand :
    DumpFileCommand(
        name = "clics-archive",
        help = "Dump CLICS contest archive (zip)",
        defaultFileName = "contest-archive.zip",
        outputHelp = "Path to new zip file",
    ) {}""",
        "optofmt": """object ClicsArchiveCommand : DumpFileCommand(
    name = "clics-archive",
    help = "Dump CLICS contest archive (zip)",
    defaultFileName = "contest-archive.zip",
    outputHelp = "Path to new zip file",
) {}
""",
        "idiomatic": "optofmt",
        "extra": [{
            "note": "Add a few interfaces to the supertype list and ktfmt rectangle fragments it completely: it "
                    "breaks after <code>:</code>, staircases the constructor an extra level, then drops "
                    "each interface onto its own line. ktfmt ergonomics still keeps <code>:</code> attached "
                    "and expands only the constructor's argument list; the short interfaces ride the "
                    "closing <code>)</code> line, so the header reads as one supertype clause rather than "
                    "a four-line ladder.",
            "ktfmt": """object ClicsArchiveCommand :
    DumpFileCommand(
        name = "clics-archive",
        help = "Dump CLICS contest archive (zip)",
        defaultFileName = "contest-archive.zip",
        outputHelp = "Path to new zip file",
    ),
    Runnable,
    Closeable,
    KoinComponent {}""",
            "optofmt": """object ClicsArchiveCommand : DumpFileCommand(
    name = "clics-archive",
    help = "Dump CLICS contest archive (zip)",
    defaultFileName = "contest-archive.zip",
    outputHelp = "Path to new zip file",
), Runnable, Closeable, KoinComponent {}
""",
            "idiomatic": "optofmt",
        }, {
            "note": "Drop the constructor and leave only interfaces: ktfmt rectangle still breaks after "
                    "<code>:</code>, stranding it on its own line and stacking every interface below. "
                    "ktfmt ergonomics keeps the first interface on the header line "
                    "(<code>: Runnable</code>) and lists the rest one per line.",
            "ktfmt": """object ClicsArchiveCommand :
    Runnable,
    Closeable,
    KoinComponent,
    AutoCloseable,
    Comparable<ClicsArchiveCommand>,
    Iterable<String> {}""",
            "optofmt": """object ClicsArchiveCommand : Runnable,
    Closeable,
    KoinComponent,
    AutoCloseable,
    Comparable<ClicsArchiveCommand>,
    Iterable<String> {}""",
            "idiomatic": "optofmt",
        }],
    },
    {
        "id": "long-call-chain",
        "name": "Long call chain",
        "source": "icpc/live-v3 · CdsLoadersTest",
        "thesis": "ktfmt ergonomics keeps the receiver on the `=` line and breaks each call at one indent; ktfmt rectangle breaks after `=` and double-indents.",
        "why": "A fluent chain that overflows breaks before each call. ktfmt ergonomics keeps the receiver on "
               "the introducer's line and puts each subsequent call on its own line at one indent. "
               "ktfmt rectangle first breaks after <code>=</code> (an extra line) and then indents the whole "
               "chain a second level — more lines and deeper nesting for the same chain.",
        "input": "fun f() { val testDataDir: Path = Path.of(\"\").absolute().parent.parent."
                 "resolve(\"tests\").resolve(\"testData\").resolve(\"loaders\")."
                 "relativeTo(Path.of(\"\").absolute()) }",
        "ktfmt": """fun f() {
    val testDataDir: Path =
        Path.of("")
            .absolute()
            .parent
            .parent
            .resolve("tests")
            .resolve("testData")
            .resolve("loaders")
            .relativeTo(Path.of("").absolute())
}""",
        "optofmt": """fun f() {
    val testDataDir: Path = Path.of("")
        .absolute()
        .parent
        .parent
        .resolve("tests")
        .resolve("testData")
        .resolve("loaders")
        .relativeTo(Path.of("").absolute())
}""",
        "idiomatic": "optofmt",
    },
    {
        "id": "block-rhs",
        "name": "Block-valued right-hand side (`when`/`if`/`try`) stays on the `=` line",
        "source": "icpc/live-v3 · AbstractScoreboardCalculator.kt:202",
        "thesis": "ktfmt ergonomics keeps `val x = when (…) {` attached; ktfmt rectangle pushes the block below `=` and indents every branch deeper.",
        "why": "ktfmt rectangle breaks after <code>=</code> and indents the whole block-valued right-hand side an "
               "extra level, although <code>val teamsAffected = when (val event = state.lastEvent) {</code> "
               "fits easily. ktfmt ergonomics treats an assignment prefix like a header and keeps the block "
               "opener attached, so the branches sit one level in instead of two. The same rule covers "
               "any block-valued RHS — a <code>when</code> or an <code>if</code>/<code>else</code> used "
               "as an expression.",
        "input": "fun f() {\nval teamsAffected = when (val event = state.lastEvent) {\n"
                 "is CommentaryMessagesUpdate -> emptyList()\nis InfoUpdate -> info.teams.keys.toList()\n"
                 "is RunUpdate -> {\nlastSubmissionTime = maxOf(lastSubmissionTime, event.newInfo.time)\n"
                 "runsByTeamId.applyEvent(state)\n}\n}\n}",
        "ktfmt": """fun f() {
    val teamsAffected =
        when (val event = state.lastEvent) {
            is CommentaryMessagesUpdate -> emptyList()
            is InfoUpdate -> info.teams.keys.toList()
            is RunUpdate -> {
                lastSubmissionTime = maxOf(lastSubmissionTime, event.newInfo.time)
                runsByTeamId.applyEvent(state)
            }
        }
}""",
        "optofmt": """fun f() {
    val teamsAffected = when (val event = state.lastEvent) {
        is CommentaryMessagesUpdate -> emptyList()
        is InfoUpdate -> info.teams.keys.toList()
        is RunUpdate -> {
            lastSubmissionTime = maxOf(lastSubmissionTime, event.newInfo.time)
            runsByTeamId.applyEvent(state)
        }
    }
}""",
        "idiomatic": "optofmt",
        "extra": [{
            "note": "Time passes and someone adds an explicit type. ktfmt ergonomics is unmoved: the type glues "
                    "to its <code>:</code> (§9) and <code>= when (</code> stays attached (§3), so the "
                    "branches keep their single indent — the layout barely changes as the code evolves. "
                    "ktfmt rectangle breaks after <code>=</code> as before, so the whole <code>when</code> now "
                    "drops a level and its branches sit at indent 12.",
            "input": "fun f() {\nval teamsAffected: List<TeamId> = when (val event = state.lastEvent) {\n"
                     "is CommentaryMessagesUpdate -> emptyList()\nis InfoUpdate -> info.teams.keys.toList()\n"
                     "is RunUpdate -> {\nlastSubmissionTime = maxOf(lastSubmissionTime, event.newInfo.time)\n"
                     "runsByTeamId.applyEvent(state)\n}\n}\n}",
            "ktfmt": """fun f() {
    val teamsAffected: List<TeamId> =
        when (val event = state.lastEvent) {
            is CommentaryMessagesUpdate -> emptyList()
            is InfoUpdate -> info.teams.keys.toList()
            is RunUpdate -> {
                lastSubmissionTime = maxOf(lastSubmissionTime, event.newInfo.time)
                runsByTeamId.applyEvent(state)
            }
        }
}""",
            "optofmt": """fun f() {
    val teamsAffected: List<TeamId> = when (val event = state.lastEvent) {
        is CommentaryMessagesUpdate -> emptyList()
        is InfoUpdate -> info.teams.keys.toList()
        is RunUpdate -> {
            lastSubmissionTime = maxOf(lastSubmissionTime, event.newInfo.time)
            runsByTeamId.applyEvent(state)
        }
    }
}""",
            "idiomatic": "optofmt",
        }, {
            "note": "An <code>if</code>/<code>else</code> used as an expression is the same case — a "
                    "block-valued RHS. ktfmt rectangle breaks after <code>=</code> and indents both branches an "
                    "extra level; ktfmt ergonomics keeps <code>val builder = if (!builders.isEmpty()) {</code> "
                    "attached. (Kotlin · ControlFlowInstructionsGenerator)",
            "ktfmt": """fun f() {
    val builder =
        if (!builders.isEmpty()) {
            builders.peek()
        } else {
            null
        }
}""",
            "optofmt": """fun f() {
    val builder = if (!builders.isEmpty()) {
        builders.peek()
    } else {
        null
    }
}""",
        }, {
            "note": "Same evolution for the <code>if</code>/<code>else</code> expression, but now the "
                    "header overflows. ktfmt ergonomics still won't break after <code>=</code>: it keeps "
                    "<code>= if (</code> attached and wraps the condition inside the parens at one indent, "
                    "so the branches stay at one indent. ktfmt rectangle breaks after <code>=</code>, "
                    "dropping the whole <code>if</code> and both branches a level deeper.",
            "input": "fun f() {\nval builder: InstructionBuilder? = "
                     "if (!builders.isEmpty() && builders.peek().isReadyForOverride()) {\n"
                     "builders.peek()\n} else {\nnull\n}\n}",
            "ktfmt": """fun f() {
    val builder: InstructionBuilder? =
        if (!builders.isEmpty() && builders.peek().isReadyForOverride()) {
            builders.peek()
        } else {
            null
        }
}""",
            "optofmt": """fun f() {
    val builder: InstructionBuilder? = if (
        !builders.isEmpty() && builders.peek().isReadyForOverride()
    ) {
        builders.peek()
    } else {
        null
    }
}""",
            "idiomatic": "optofmt",
        }, {
            "note": "A <code>try</code>/<code>catch</code>/<code>finally</code> used as an expression is the "
                    "same case — a block-valued RHS. ktfmt rectangle breaks after <code>=</code> and indents the whole "
                    "<code>try</code> an extra level; ktfmt ergonomics keeps <code>val result = try {</code> attached. "
                    "(okio · Okio.kt:60)",
            "ktfmt": "fun <T> f(block: () -> T): T? {\n    var thrown: Throwable? = null\n    val result =\n        try {\n            block()\n        } catch (t: Throwable) {\n            thrown = t\n            null\n        } finally {\n            cleanup()\n        }\n    return result\n}",
            "optofmt": "fun <T> f(block: () -> T): T? {\n    var thrown: Throwable? = null\n    val result = try {\n        block()\n    } catch (t: Throwable) {\n        thrown = t\n        null\n    } finally {\n        cleanup()\n    }\n    return result\n}",
        }, {
            "note": "And the <code>try</code> expression: add the explicit <code>T?</code> type and "
                    "<code>= try {</code> stays attached; ktfmt rectangle drops the whole <code>try</code> below "
                    "<code>=</code>, its clauses a level deeper.",
            "input": "fun <T> f(block: () -> T): T? {\nvar thrown: Throwable? = null\nval result: T? = try {\n"
                     "block()\n} catch (t: Throwable) {\nthrown = t\nnull\n} finally {\ncleanup()\n}\nreturn result\n}",
            "ktfmt": "fun <T> f(block: () -> T): T? {\n    var thrown: Throwable? = null\n    val result: T? =\n        try {\n            block()\n        } catch (t: Throwable) {\n            thrown = t\n            null\n        } finally {\n            cleanup()\n        }\n    return result\n}",
            "optofmt": "fun <T> f(block: () -> T): T? {\n    var thrown: Throwable? = null\n    val result: T? = try {\n        block()\n    } catch (t: Throwable) {\n        thrown = t\n        null\n    } finally {\n        cleanup()\n    }\n    return result\n}",
            "idiomatic": "optofmt",
        }, {
            "note": "What happens when the header itself overflows? Here the one-line "
                    "<code>val teamsAffected = when (val event = …) {</code> is 101 columns, so the "
                    "subject can't stay on the <code>=</code> line. ktfmt ergonomics still won't break after "
                    "<code>=</code> (§3): it keeps <code>= when (</code> attached and wraps the "
                    "<em>subject</em> inside the parens at one indent, so the branches stay at one "
                    "indent. ktfmt rectangle breaks after <code>=</code> first, then nests the branches a second "
                    "level. (More lines for ktfmt ergonomics here, but §3 forbids the break-after-<code>=</code> "
                    "form regardless — flatter branches over fewer lines.)",
            "ktfmt": """fun f() {
    val teamsAffected =
        when (val event = state.veryLooooooooooooooooooooooooooooongLastEventValue) {
            is InfoUpdate -> info.teams.keys.toList()
            else -> emptyList()
        }
}""",
            "optofmt": """fun f() {
    val teamsAffected = when (
        val event = state.veryLooooooooooooooooooooooooooooongLastEventValue
    ) {
        is InfoUpdate -> info.teams.keys.toList()
        else -> emptyList()
    }
}""",
        }],
    },
    {
        "id": "accessor-block-body",
        "name": "Block-valued accessor (`get() = when`) stays on the property line",
        "source": "kotlinx-knit · linked in review thread",
        "thesis": "ktfmt ergonomics keeps `… get() = when (…) {` on one line and the branches at one indent; ktfmt rectangle makes three break decisions — accessor, `=`, and block — stacking the branches three levels deep.",
        "why": "This is the accessor case (§accessor) and the block-valued RHS case (§3) compounded. ktfmt rectangle "
               "force-breaks all three joints: it drops <code>get()</code> onto its own line, then breaks "
               "after <code>=</code>, then indents the <code>when</code> block again — so the branches "
               "land three levels in. Both the accessor and the <code>= when (…) {</code> header fit "
               "well under 100 columns, so ktfmt ergonomics keeps the whole header on the property line (don't "
               "wrap what fits, §1) and treats the assignment as an attached introducer, leaving the "
               "branches at a single indent. The denser form kotlinx code favours for an expression "
               "getter whose body is a <code>when</code>.",
        "input": "val outText: MutableList<String> get() = when (inputTextPart) {\n"
                 "InputTextPart.PRE_TOC -> preTocText\nInputTextPart.POST_TOC -> postTocText\n"
                 "else -> throw IllegalStateException(\"Wrong state: $inputTextPart\")\n}",
        "ktfmt": """val outText: MutableList<String>
    get() =
        when (inputTextPart) {
            InputTextPart.PRE_TOC -> preTocText
            InputTextPart.POST_TOC -> postTocText
            else -> throw IllegalStateException("Wrong state: $inputTextPart")
        }""",
        "optofmt": """val outText: MutableList<String> get() = when (inputTextPart) {
    InputTextPart.PRE_TOC -> preTocText
    InputTextPart.POST_TOC -> postTocText
    else -> throw IllegalStateException("Wrong state: $inputTextPart")
}""",
        "idiomatic": "optofmt",
    },
    {
        "id": "trailing-lambda",
        "name": "Trailing lambda / last-argument expansion",
        "source": "icpc/live-v3",
        "thesis": "ktfmt ergonomics keeps the leading args inline and lets the block hang off; ktfmt rectangle explodes every argument.",
        "why": "ktfmt ergonomics may keep leading arguments on the opener line while the final lambda expands "
               "in place, so the call stays compact with the block hanging off the end. ktfmt rectangle is "
               "all-or-nothing: once the call doesn't fit, every argument goes on its own line, "
               "including the lambda.",
        "input": "fun run() { executeWithRetryPolicy(maximumRetryCount, backoffStrategy, "
                 "{ requestContext: RequestContext -> requestContext.proceed() }) }",
        "ktfmt": """fun run() {
    executeWithRetryPolicy(
        maximumRetryCount,
        backoffStrategy,
        { requestContext: RequestContext -> requestContext.proceed() },
    )
}""",
        "optofmt": """fun run() {
    executeWithRetryPolicy(maximumRetryCount, backoffStrategy, { requestContext: RequestContext ->
        requestContext.proceed()
    })
}""",
        "note": "Note that while having a trailing lambda out of the parentheses is a preferrable way "
                "of formatting, such transformation is potentially a binary-breaking change and cannot "
                "be performed by a formatter.",
        "idiomatic": "optofmt",
    },
    {
        "id": "compact-header",
        "name": "Compact declaration header (annotations & modifiers)",
        "source": "kotlinx.coroutines · SharedFlowSubscriptionScope",
        "thesis": "ktfmt ergonomics keeps annotations & modifiers on the declaration line; ktfmt rectangle drops each onto its own line.",
        "why": "Facing a long constructor header, ktfmt rectangle puts the class line, the <code>@PublishedApi</code> "
               "annotation, and <code>internal constructor(</code> on three separate lines before it "
               "even reaches the parameters. ktfmt ergonomics keeps the whole modifier run together and wraps "
               "only the parameter list — the part that actually needs it.",
        "input": "public class SharedFlowSubscriptionScope<T> @PublishedApi internal constructor("
                 "@PublishedApi internal val flow: SharedFlow<T>, private val subscriptionWaitingFlow: "
                 "MutableStateFlow<Int>) {\n}",
        "ktfmt": """public class SharedFlowSubscriptionScope<T>
@PublishedApi
internal constructor(
    @PublishedApi internal val flow: SharedFlow<T>,
    private val subscriptionWaitingFlow: MutableStateFlow<Int>,
) {}""",
        "optofmt": """public class SharedFlowSubscriptionScope<T> @PublishedApi internal constructor(
    @PublishedApi internal val flow: SharedFlow<T>,
    private val subscriptionWaitingFlow: MutableStateFlow<Int>,
) {}
""",
        "idiomatic": "optofmt",
    },
    {
        "id": "grouped-declarations",
        "name": "Grouped one-line declarations keep no blank lines",
        "source": "synthetic",
        "thesis": "ktfmt ergonomics keeps a run of one-line declarations tight; ktfmt rectangle forces a blank line between each.",
        "why": "ktfmt rectangle injects a blank line between consecutive one-line <code>typealias</code> (and "
               "<code>fun</code>) declarations, doubling the height of a tight family of related "
               "one-liners. ktfmt ergonomics preserves the author's grouping: consecutive same-kind "
               "declarations stay together, multiple blank lines collapse to one, and a blank is "
               "inserted only between declarations of different kinds.",
        "input": """typealias TeamId = StrongId<TeamTag>
typealias RunId = StrongId<RunTag>
typealias MessageId = StrongId<MessageTag>""",
        "ktfmt": """typealias TeamId = StrongId<TeamTag>

typealias RunId = StrongId<RunTag>

typealias MessageId = StrongId<MessageTag>""",
        "optofmt": """typealias TeamId = StrongId<TeamTag>
typealias RunId = StrongId<RunTag>
typealias MessageId = StrongId<MessageTag>""",
        "idiomatic": "optofmt",
    },
    {
        "id": "long-parameter-list",
        "name": "Long parameter list",
        "source": "synthetic",
        "thesis": "Parity — both split parameters one per line and keep `) {` together (ktfmt rectangle adds a trailing comma). A virtual ergonomics v2 instead fills the parameters to the line width, several per line.",
        "why": "Included to show the comparison is fair: on the bread-and-butter case the two engines "
               "agree. The only difference is ktfmt rectangle's added trailing comma. The wins elsewhere are "
               "specific structural cases, not a blanket claim.",
        "input": "fun registerEventListener(eventType: EventType, listenerPriority: ListenerPriority, "
                 "listenerCallback: EventListener) { installListener() }",
        "ktfmt": """fun registerEventListener(
    eventType: EventType,
    listenerPriority: ListenerPriority,
    listenerCallback: EventListener,
) {
    installListener()
}""",
        "optofmt": """fun registerEventListener(
    eventType: EventType,
    listenerPriority: ListenerPriority,
    listenerCallback: EventListener,
) {
    installListener()
}
""",
        "third": """fun registerEventListener(
    eventType: EventType, listenerPriority: ListenerPriority,
    listenerCallback: EventListener
) {
    installListener()
}""",
        "idiomatic": "parity",
    },
    {
        "id": "elvis-fits",
        "name": "Elvis (`?:`) stays inline when it fits",
        "source": "null-fallback idiom · §6",
        "thesis": "ktfmt ergonomics keeps `?:` on the same line while the expression fits (§1); only when it overflows does it wrap — and then it keeps `=` attached and the operator at a single indent, where ktfmt rectangle also breaks after `=` and drifts a level deeper.",
        "why": "A null-fallback that fits on one line reads best inline, and ktfmt ergonomics keeps it there — the "
               "elvis break is a candidate, not a forced one (§6/§1), so both engines agree while it "
               "fits. The difference appears only once the operands overflow: ktfmt ergonomics keeps the "
               "introducer attached (§3), so <code>val entry =</code> stays on the first line, and drops "
               "<code>?:</code> to the start of the next line at a single indent (§2/§6). ktfmt rectangle breaks "
               "after <code>=</code> as well, then indents the <code>?:</code> a further level, so the "
               "fallback drifts two levels deep.",
        "input": "fun f() { val entry = registry.lookup(requestedName) ?: registry.defaultFor(requestedName) }",
        "ktfmt": """fun f() {
    val entry = registry.lookup(requestedName) ?: registry.defaultFor(requestedName)
}""",
        "optofmt": """fun f() {
    val entry = registry.lookup(requestedName) ?: registry.defaultFor(requestedName)
}""",
        "idiomatic": "parity",
        "extra": [{
            "note": "Lengthen the operands until the line overflows and the fit-driven choice flips to a "
                    "wrap. ktfmt ergonomics keeps the <code>=</code> introducer attached (§3) and starts the "
                    "continuation with <code>?:</code> at one indent (§2/§6). ktfmt rectangle breaks after "
                    "<code>=</code> too, so the left operand lands at indent 8 and the <code>?:</code> "
                    "fallback at indent 12 — a level deeper than ktfmt ergonomics.",
            "input": "fun f() { val entry = registry.lookupByQualifiedName(requestedName, currentScope) ?: registry.defaultEntryForScope(currentScope) }",
            "ktfmt": """fun f() {
    val entry =
        registry.lookupByQualifiedName(requestedName, currentScope)
            ?: registry.defaultEntryForScope(currentScope)
}""",
            "optofmt": """fun f() {
    val entry = registry.lookupByQualifiedName(requestedName, currentScope)
        ?: registry.defaultEntryForScope(currentScope)
}""",
            "idiomatic": "optofmt",
        }],
    },
    {
        "id": "accessor-placement",
        "name": "Trivial property accessor stays on the property line",
        "source": "Kotlin project · ktfmt diff study",
        "thesis": "ktfmt ergonomics keeps a short `get()` on the property line because it fits (§1); ktfmt rectangle always drops the accessor onto its own line.",
        "why": "ktfmt rectangle unconditionally moves a property accessor onto its own indented line, even when "
               "the whole declaration fits: <code>val placeOfGetter: String get() = \"hello\"</code> is "
               "well under 100 columns. ktfmt ergonomics follows the §1 objective — don't wrap what fits — and "
               "keeps the trivial accessor inline, the denser form kotlinx code favours for "
               "one-expression getters. (When the accessor body is long enough to overflow, ktfmt ergonomics "
               "moves it to its own line at one indent like any other wrap.)",
        "input": 'val placeOfGetter: String get() = "hello"',
        "ktfmt": 'val placeOfGetter: String\n    get() = "hello"',
        "optofmt": 'val placeOfGetter: String get() = "hello"',
        "idiomatic": "optofmt",
    },
    {
        "id": "control-flow-lambda",
        "name": "Lambda that fits stays on one line (even with `return`)",
        "source": "Kotlin project · ktfmt diff study",
        "thesis": "ktfmt ergonomics keeps a one-line lambda inline because it fits; ktfmt rectangle force-expands any lambda containing `return`/`break`/`continue`.",
        "why": "ktfmt rectangle preserves author line breaks in lambdas, but it still force-expands a lambda whose "
               "body is a control-flow jump: <code>nullableString?.let { return }</code> becomes three "
               "lines. The single statement fits comfortably, so ktfmt ergonomics keeps it inline per §1 (don't "
               "wrap what fits) — the compact guard-style form that is idiomatic for "
               "<code>?.let { return }</code> and friends.",
        "input": "fun lambdasWithReturns(nullableString: String?) { nullableString?.let { return } }",
        "ktfmt": """fun lambdasWithReturns(nullableString: String?) {
    nullableString?.let {
        return
    }
}""",
        "optofmt": """fun lambdasWithReturns(nullableString: String?) {
    nullableString?.let { return }
}""",
        "idiomatic": "optofmt",
    },
    {
        "id": "when-comma-condition",
        "name": "Comma-separated `when` conditions stay on one line when they fit",
        "source": "synthetic",
        "thesis": "ktfmt ergonomics keeps `0, 1 -> …` on one line because it fits (§1/§4); ktfmt rectangle force-splits the conditions one per line.",
        "why": "ktfmt rectangle treats the comma-separated condition list of a <code>when</code> entry as a "
               "breakable list and splits it one-per-line even when the whole entry fits comfortably: "
               "<code>0, 1 -> println(\"a or b\")</code> becomes two lines for the conditions plus the "
               "body. ktfmt ergonomics follows §1 (don't wrap what fits) and §4 (a comma list is compact when it "
               "fits) and keeps the entry on a single line — the form a human writes for a short "
               "multi-value branch. (When the conditions genuinely overflow, §4 splits them one per "
               "line.)",
        "input": "fun f(x: Int) {\nwhen (x) {\n0, 1 -> println(\"a or b\")\n}\n}",
        "ktfmt": """fun f(x: Int) {
    when (x) {
        0,
        1 -> println("a or b")
    }
}""",
        "optofmt": """fun f(x: Int) {
    when (x) {
        0, 1 -> println("a or b")
    }
}""",
        "idiomatic": "optofmt",
        "extra": [{
            "note": "The flip side, and where the two agree: when the conditions genuinely overflow, §4 "
                    "splits them one per line. Here the single-line entry is 103 columns, so ktfmt ergonomics "
                    "fully splits the list — exactly what ktfmt rectangle does. Parity, not a win: the divergence "
                    "above is only about entries that <em>fit</em>. It's really important to agree on the column width.",
            "ktfmt": """fun f() {
    when (it.resolvedCall.resultingDescriptor) {
        is LocalVariableDescriptor,
        is ValueParameterDescriptor,
        is ReceiverParameterDescriptor -> true
        else -> false
    }
}""",
            "optofmt": """fun f() {
    when (it.resolvedCall.resultingDescriptor) {
        is LocalVariableDescriptor,
        is ValueParameterDescriptor,
        is ReceiverParameterDescriptor -> true
        else -> false
    }
}""",
            "idiomatic": "parity",
        }],
    },
    {
        "id": "assign-introducer-attached",
        "name": "Introducer `=` stays attached (scope-function / concatenation / collection)",
        "source": "okio \u00b7 Okio.kt:60",
        "thesis": "ktfmt ergonomics keeps <code>= receiver.run {</code>, <code>= setOf(</code> or <code>= (\"\u2026\" +</code> on the assignment line and wraps only the body; ktfmt rectangle breaks right after <code>=</code> and adds a second indent level.",
        "why": "\u00a73 says never break after an introducer just to give its right-hand side a fresh indented block. Pattern <em>block-valued RHS</em> covers only <code>when</code>/<code>if</code>; the real ktfmt ergonomics applies the same rule to every block- or call-valued RHS. It keeps the <code>=</code> and the opener (<code>receiver.run {</code>, <code>(\"\u2026\" +</code>, <code>setOf(</code>) together and lays the body at a single indent, reproducing the hand-written kotlinx shape. ktfmt rectangle eagerly drops the whole right-hand side to a new line and indents it twice.",
        "input": "fun digest(algorithm: String): ByteString {\nval digestBytes = MessageDigest.getInstance(algorithm).run {\nupdate(data, 0, size)\ndigest()\n}\nreturn ByteString(digestBytes)\n}",
        "ktfmt": "fun digest(algorithm: String): ByteString {\n    val digestBytes =\n        MessageDigest.getInstance(algorithm).run {\n            update(data, 0, size)\n            digest()\n        }\n    return ByteString(digestBytes)\n}",
        "optofmt": "fun digest(algorithm: String): ByteString {\n    val digestBytes = MessageDigest.getInstance(algorithm).run {\n        update(data, 0, size)\n        digest()\n    }\n    return ByteString(digestBytes)\n}",
        "idiomatic": "optofmt",
        "extra": [
            {
                "note": "Same rule, a parenthesised <code>+</code>-concatenation: ktfmt ergonomics keeps <code>= (\"\u2026\" +</code> on the line and stacks the remaining strings at one flat indent (\u00a76); ktfmt rectangle breaks after <code>=</code> and staircases the operands.",
                "ktfmt": "fun f() {\n    val raw =\n        (\"Um, I'll tell you the problem with the scientific power that you're using here, \" +\n            \"it didn't require any discipline to attain it. You read what others had done and you \" +\n            \"took the next step. You didn't earn the knowledge for yourselves, so you don't take any \")\n}",
                "optofmt": "fun f() {\n    val raw = (\"Um, I'll tell you the problem with the scientific power that you're using here, \" +\n        \"it didn't require any discipline to attain it. You read what others had done and you \" +\n        \"took the next step. You didn't earn the knowledge for yourselves, so you don't take any \")\n}",
            },
            {
                "note": "Same rule, a collection literal that must fully explode: <code>= setOf(</code> stays attached with items one-per-line at a single indent and no trailing comma; ktfmt rectangle breaks after <code>=</code>, adds a second indent level and a trailing comma.",
                "ktfmt": "package org.jetbrains.exposed.sql.vendors\n\nval ANSI_SQL_2003_KEYWORDS: Set<String> =\n    setOf(\n        \"A\",\n        \"ABS\",\n        \"ABSOLUTE\",\n        \"ACTION\",\n        \"ADA\",\n        \"ADD\",\n        \"ADMIN\",\n        \"AFTER\",\n        \"ALL\",\n        \"ALLOCATE\",\n        \"ALTER\",\n        \"ALWAYS\",\n        \"AND\",\n        \"ANY\",\n        \"ARE\",\n        \"ARRAY\",\n        \"AS\",\n        \"ASC\",\n    )",
                "optofmt": "package org.jetbrains.exposed.sql.vendors\n\nval ANSI_SQL_2003_KEYWORDS: Set<String> = setOf(\n    \"A\",\n    \"ABS\",\n    \"ABSOLUTE\",\n    \"ACTION\",\n    \"ADA\",\n    \"ADD\",\n    \"ADMIN\",\n    \"AFTER\",\n    \"ALL\",\n    \"ALLOCATE\",\n    \"ALTER\",\n    \"ALWAYS\",\n    \"AND\",\n    \"ANY\",\n    \"ARE\",\n    \"ARRAY\",\n    \"AS\",\n    \"ASC\",\n)",
            },
        ],
    },
    {
        "id": "argumentless-annotation-own-line",
        "name": "Argument-less annotation on its own line",
        "source": "sqldelight \u00b7 SqlDelightExtension.kt:6",
        "thesis": "ktfmt ergonomics puts an argument-less annotation (outside a small interop allowlist) on its own line above the declaration; ktfmt rectangle keeps it inline whenever it fits under 100 columns.",
        "why": "The <em>annotation-with-arguments</em> pattern already breaks a standalone annotation that carries arguments onto its own line. The real ktfmt ergonomics extends this to <em>argument-less</em> annotations: only a modifier-like allowlist (<code>@JvmStatic</code>, <code>@JvmInline</code>, <code>@JvmOverloads</code>, <code>@PublishedApi</code>) stays inline; every other annotation (<code>@DslMarker</code>, <code>@Test</code>, <code>@SpringBootApplication</code>, <code>@Serializable</code>, \u2026) goes on its own line, matching idiomatic Kotlin. ktfmt rectangle keeps any short annotation inline. This holds for classes, properties, and expression-body functions alike.",
        "input": "@DslMarker\nannotation class SqlDelightDsl",
        "ktfmt": "@DslMarker annotation class SqlDelightDsl",
        "optofmt": "@DslMarker\nannotation class SqlDelightDsl",
        "idiomatic": "optofmt",
        "extra": [
            {
                "note": "An annotation that carries arguments lands on its own line too: ktfmt ergonomics drops <code>@JvmName(\"other\")</code> above <code>fun</code>, while ktfmt rectangle keeps it inline with the declaration.",
                "ktfmt": '@JvmName("other") fun testSomething() {}',
                "optofmt": '@JvmName("other")\nfun testSomething() {}',
            },
            {
                "note": "The same split happens even on an <em>expression-body</em> function \u2014 <code>@Test</code> stays above <code>fun \u2026 = doTest(\u2026)</code>; ktfmt rectangle packs the annotation, <code>fun</code> and body onto one line.",
                "ktfmt": "class FooTest {\n    @Test fun `kotlin-stdlib-1_9_20`(testInfo: TestInfo) = doTest(testInfo)\n}",
                "optofmt": "class FooTest {\n    @Test\n    fun `kotlin-stdlib-1_9_20`(testInfo: TestInfo) = doTest(testInfo)\n}",
            },
            {
                "note": "Multiple annotations each keep their own line above a bodyless accessor; ktfmt rectangle collapses them and the bare <code>set</code> onto one line because it fits.",
                "ktfmt": "class Database private constructor(val config: DatabaseConfig) {\n    var useNestedTransactions: Boolean = config.useNestedTransactions\n        @Deprecated(\"Use DatabaseConfig to define the useNestedTransactions\") @TestOnly set\n}",
                "optofmt": "class Database private constructor(val config: DatabaseConfig) {\n    var useNestedTransactions: Boolean = config.useNestedTransactions\n        @Deprecated(\"Use DatabaseConfig to define the useNestedTransactions\")\n        @TestOnly\n        set\n}",
            },
        ],
    },
    {
        "id": "multi-supertype-list-one-per-line",
        "name": "Multiple supertypes: one per line, never packed",
        "source": "sqldelight \u00b7 ArrayValueExpressionMixin.kt:20",
        "thesis": "ktfmt ergonomics keeps the first supertype attached to `:` (\u00a73) and drops each remaining supertype to its own line (\u00a74); ktfmt rectangle breaks right after `:` and packs every supertype onto one continuation line. A virtual ergonomics v2 also wraps the constructor parameters onto their own line, so <code>) : SqlCompositeElementImpl(node),</code> begins the supertype list.",
        "why": "The supertype <code>:</code> is an introducer (\u00a73): ktfmt ergonomics keeps <code>) : SqlCompositeElementImpl(node)</code> on the header line and puts each <em>remaining</em> supertype on its own line at one indent (\u00a74 \u2014 a comma list is compact or one-per-line). ktfmt rectangle instead breaks right after <code>:</code> and then fill-packs every supertype onto the single continuation line, so the list reads as one dense run rather than an aligned column.",
        "input": "internal abstract class ArrayValueExpressionMixin(node: ASTNode) :\n  SqlCompositeElementImpl(node),\n  SqlExpr,\n  PostgreSqlArrayValueExpression {\n  val x = 1\n}",
        "ktfmt": "internal abstract class ArrayValueExpressionMixin(node: ASTNode) :\n    SqlCompositeElementImpl(node), SqlExpr, PostgreSqlArrayValueExpression {\n    val x = 1\n}",
        "optofmt": "internal abstract class ArrayValueExpressionMixin(node: ASTNode) : SqlCompositeElementImpl(node),\n    SqlExpr,\n    PostgreSqlArrayValueExpression {\n    val x = 1\n}",
        "third": """internal abstract class ArrayValueExpressionMixin(
    node: ASTNode
) : SqlCompositeElementImpl(node),
    SqlExpr,
    PostgreSqlArrayValueExpression {
    val x = 1
}""",
        "idiomatic": "optofmt",
    },
    {
        "id": "small-overflow-tolerance",
        "name": "Small overflow tolerated instead of exploding a compact signature",
        "source": "sqldelight \u00b7 SqlDelightRefactoringSupportProvider.kt:8",
        "thesis": "When a signature spills only 1\u20132 columns past 100, ktfmt ergonomics keeps it on one line (matching the hand-written source); ktfmt rectangle explodes the parameter list one-per-line the instant it crosses 100.",
        "why": "The real ktfmt ergonomics applies a small, <em>bounded</em> overflow tolerance (~2 columns): rather than fragment a short signature into a five-line block for the sake of two characters, it keeps the authorial single line. Beyond ~102 columns it does explode, so the slack is bounded. Note this trades against \u00a71's strict \u201cno overflowing line\u201d objective \u2014 it is a pragmatic convergence with how these signatures are actually written in the stdlib and elsewhere; the amber mark shows the residual one-column overflow.",
        "input": "class C : RefactoringSupportProvider() {\n  override fun isMemberInplaceRenameAvailable(element: PsiElement, context: PsiElement?): Boolean {\n    return element is NamedElement\n  }\n}",
        "ktfmt": "class C : RefactoringSupportProvider() {\n    override fun isMemberInplaceRenameAvailable(\n        element: PsiElement,\n        context: PsiElement?,\n    ): Boolean {\n        return element is NamedElement\n    }\n}",
        "optofmt": "class C : RefactoringSupportProvider() {\n    override fun isMemberInplaceRenameAvailable(element: PsiElement, context: PsiElement?): Boolean {\n        return element is NamedElement\n    }\n}",
        "idiomatic": "optofmt",
        "extra": [
            {
                "note": "Same tolerance on a generic stdlib signature: <code>buildList(\u2026): List&lt;E&gt;</code> sits at 102 columns on one line; ktfmt rectangle splits the single parameter across three lines.",
                "ktfmt": "public inline fun <E> buildList(\n    @BuilderInference builderAction: MutableList<E>.() -> Unit\n): List<E> {\n    return listOf()\n}",
                "optofmt": "public inline fun <E> buildList(@BuilderInference builderAction: MutableList<E>.() -> Unit): List<E> {\n    return listOf()\n}",
            },
        ],
    },
    {
        "id": "trailing-comment-excluded-from-wrap",
        "name": "Trailing line-comment does not force a wrap",
        "source": "kotlinx.coroutines \u00b7 DebugCoroutineInfo.kt:18",
        "thesis": "When only a trailing <code>// comment</code> pushes a line past 100, ktfmt ergonomics keeps the whole line intact (matching the author); ktfmt rectangle wraps the value onto a new line to fit.",
        "why": "The code itself \u2014 <code>internal val \u2026 = source.creationStackBottom</code> \u2014 is well within 100 columns; only the trailing <code>// comment</code> spills over. ktfmt ergonomics does not count a trailing end-of-line comment toward the column limit, so it sees no reason to break a one-line property in two, and reproduces the hand-written kotlinx source verbatim. ktfmt rectangle measures the raw character count (comment included) and breaks after <code>=</code> to bring the code under 100 \u2014 scattering a single logical line across two. This is a deliberate trailing-comment exemption from \u00a71's width objective; the amber mark on the ktfmt ergonomics line is the comment overflow it chooses to keep.",
        "input": "class DebugCoroutineInfo {\n    internal val creationStackBottom: CoroutineStackFrame? = source.creationStackBottom // field is used as of 1.4-M3\n}",
        "ktfmt": "class DebugCoroutineInfo {\n    internal val creationStackBottom: CoroutineStackFrame? =\n        source.creationStackBottom // field is used as of 1.4-M3\n}",
        "optofmt": "class DebugCoroutineInfo {\n    internal val creationStackBottom: CoroutineStackFrame? = source.creationStackBottom // field is used as of 1.4-M3\n}",
        "idiomatic": "optofmt",
    },
    {
        "id": "raw-string-sole-arg-attached",
        "name": "Triple-quoted string as sole call argument stays attached",
        "source": "kotlinx.coroutines \u00b7 CoroutineExceptionHandlerImpl.kt:17",
        "thesis": "When a multiline raw (\"\"\"\u2026\"\"\") string is the only argument of a call, ktfmt ergonomics keeps the opening `(\"\"\"` on the call line and the closing `\"\"\")` on the string's last line (indent economy \u00a75); ktfmt rectangle puts the `(` and `\"\"\"` on separate stacked lines and stacks a lone `)` below.",
        "why": "The whole raw string is a single indivisible token; breaking around the parentheses only adds two lines and an extra indent level without helping the width objective. ktfmt ergonomics keeps the opening <code>(\"\"\"</code> on the call line and the closing <code>\"\"\")</code> on the string's last line, reusing one body indent (\u00a75); ktfmt rectangle stacks <code>(</code>, <code>\"\"\"</code> and a lonely <code>)</code> on separate lines.",
        "input": "fun f() {\n    js(\"\"\"\n        var error = new Error();\n        error.message = message;\n    \"\"\")\n}",
        "ktfmt": "fun f() {\n    js(\n        \"\"\"\n        var error = new Error();\n        error.message = message;\n    \"\"\"\n    )\n}",
        "optofmt": "fun f() {\n    js(\"\"\"\n        var error = new Error();\n        error.message = message;\n    \"\"\")\n}",
        "idiomatic": "optofmt",
    },
]
