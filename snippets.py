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
        "name": "Multi-line boolean condition",
        "source": "kotlinx.coroutines · JobSupport.kt:273",
        "thesis": "ktfmt ergonomics keeps every operand at one indent; ktfmt rectangle pushes each operand after the first a level deeper.",
        "why": "A condition too long for one line must wrap to stacked operands. ktfmt ergonomics opens the "
               "paren and lays every operand at the same body indent — one indentation size, so the "
               "operands form a clean rectangular block. ktfmt rectangle adds a continuation indent on top of "
               "the block indent, so operand 2+ drift one step further right than operand 1, with no "
               "structural meaning a reader can attach to.",
        "input": "fun f() { if (unwrapped !== rootCause && unwrapped !== unwrappedCause && unwrapped "
                 "!is CancellationException && seenExceptions.add(unwrapped)) { "
                 "rootCause.addSuppressed(unwrapped) } }",
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
        "idiomatic": "optofmt",
    },
    {
        "id": "indent-economy",
        "name": "Nested call wrapping (indent economy)",
        "source": "icpc/live-v3 · Rules.kt:219",
        "thesis": "ktfmt ergonomics collapses the wrapper openers and stacks the closers; ktfmt rectangle staircases with lonely parens.",
        "why": "When an outer call's single argument is itself a call that must split, ktfmt ergonomics lets the "
               "two openers share a line (<code>add(OverrideQueue(</code>) and the closers collapse "
               "onto one line (<code>))</code>) — the arguments sit one level in. ktfmt rectangle cannot share "
               "indentation: each opener gets its own line and a deeper indent, and each closer gets a "
               "line of its own, leaving orphaned parens and an extra indentation level.",
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
        queueSettings.maxUntestedRun
    ))
}""",
        "idiomatic": "optofmt",
        "extra": [{
            "note": "Here collapsing isn't cosmetic — it decides fit vs. overflow. The single "
                    "argument is one unbreakable token. Staircased (ktfmt rectangle) it lands at indent 12 "
                    "and hits column 101; with the openers collapsed it sits at indent 8 and "
                    "fits in 97. Same §5 mechanism, now arbitrating §1's “minimize the worst "
                    "overflow.”",
            "ktfmt": """fun f() {
    registerHandler(
        buildHandler(
            aLongUnbreakableArgumentIdentifierDeliberatelySizedToOverflowTheColumnLimitNoMatterWhatXY
        )
    )
}""",
            "optofmt": """fun f() {
    registerHandler(buildHandler(
        aLongUnbreakableArgumentIdentifierDeliberatelySizedToOverflowTheColumnLimitNoMatterWhatXY
    ))
}""",
        }, {
            "note": "The boundary of §5: collapsing only applies when the expandable call is the outer "
                    "call's <em>only</em> argument. Once it has siblings, the openers no longer touch, "
                    "so there's nothing to share — ktfmt ergonomics just splits the outer list one item per line "
                    "(§4) and lets <code>OverrideQueue(</code> expand in place. The result matches ktfmt rectangle "
                    "line-for-line except for the trailing commas. So the collapse never over-applies to "
                    "produce a ragged <code>add(arg1, arg2, OverrideQueue(</code>.",
            "ktfmt": """fun f() {
    add(
        arg1,
        arg2,
        OverrideQueue(
            queueSettings.waitTime,
            queueSettings.firstToSolveWaitTime,
            queueSettings.maxQueueSize,
            queueSettings.maxUntestedRun,
        ),
        arg3,
        arg4,
    )
}""",
            "optofmt": """fun f() {
    add(
        arg1,
        arg2,
        OverrideQueue(
            queueSettings.waitTime,
            queueSettings.firstToSolveWaitTime,
            queueSettings.maxQueueSize,
            queueSettings.maxUntestedRun
        ),
        arg3,
        arg4
    )
}""",
            "idiomatic": "parity",
        }, {
            "note": "Name the single argument (<code>add(queue = OverrideQueue(</code>) and ktfmt rectangle gets "
                    "worse still: it now breaks after <code>queue =</code> <em>as well</em> before it "
                    "staircases the call, so the arguments land at indent 16 — three levels deep. ktfmt ergonomics "
                    "treats the named-argument <code>=</code> as an introducer (§3) and keeps it on the "
                    "opener line, so the §5 collapse is untouched: <code>add(queue = OverrideQueue(</code> "
                    "stays whole and the body still sits at a single indent.",
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
        queueSettings.maxUntestedRun
    ))
}""",
            "idiomatic": "optofmt",
        }, {
            "note": "Two named arguments, each an expandable call, combine the previous two boundaries. "
                    "The §5 collapse cannot apply — neither call is the <em>only</em> argument, so the "
                    "openers don't touch — yet unlike the positional-siblings case this is <em>not</em> "
                    "parity: ktfmt ergonomics still keeps each named-argument <code>=</code> introducer attached "
                    "(§3), so <code>queue = OverrideQueue(</code> stays whole and its body sits at indent "
                    "12. ktfmt rectangle breaks after every <code>=</code>, staircasing each branch's arguments down "
                    "to indent 16.",
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
            queueSettings.maxUntestedRun
        ),
        foo = OverrideQueue(
            queueSettings.waitTime,
            queueSettings.firstToSolveWaitTime,
            queueSettings.featuredRunWaitTime,
            queueSettings.inProgressRunWaitTime,
            queueSettings.maxQueueSize,
            queueSettings.maxUntestedRun
        )
    )
}""",
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
    displayName = substituteRaw(displayName)
)""",
        "idiomatic": "optofmt",
        "extra": [{
            "note": "Add an explicit type and the header no longer fits — "
                    "<code>val pair: Pair&lt;…&gt; = orgInfo.id to OverrideOrganizations.Override(</code> "
                    "is 110 columns. Even so, ktfmt ergonomics does <em>not</em> break after <code>=</code> (§3): "
                    "it keeps the introducer and the first operand together and wraps at the infix "
                    "operator instead (§6), <code>to</code> at the end of the line and the second operand "
                    "at a single indent. ktfmt rectangle breaks after <em>both</em> <code>=</code> and "
                    "<code>to</code>, staircasing the call three levels deep.",
            "ktfmt": """val pair: Pair<OrganizationId, OverrideOrganizations.Override> =
    orgInfo.id to
        OverrideOrganizations.Override(
            fullName = substituteRaw(fullName),
            displayName = substituteRaw(displayName),
        )""",
            "optofmt": """val pair: Pair<OrganizationId, OverrideOrganizations.Override> = orgInfo.id to
    OverrideOrganizations.Override(
        fullName = substituteRaw(fullName),
        displayName = substituteRaw(displayName)
    )""",
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
    outputHelp = "Path to new zip file"
) {}""",
        "idiomatic": "optofmt",
        "extra": [{
            "note": "Add a few interfaces to the supertype list and ktfmt rectangle fragments it completely: it "
                    "breaks after <code>:</code>, staircases the constructor an extra level, then drops "
                    "each interface onto its own line. ktfmt ergonomics still keeps <code>:</code> attached (§3) "
                    "and expands only the constructor's argument list; the short interfaces ride the "
                    "closing <code>)</code> line — the §5 legality allows a closer line to carry trailing "
                    "content — so the header reads as one supertype clause rather than a four-line ladder.",
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
    outputHelp = "Path to new zip file"
), Runnable, Closeable, KoinComponent {}""",
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
            "note": "A <code>try</code>/<code>catch</code>/<code>finally</code> used as an expression is the "
                    "same case — a block-valued RHS. ktfmt rectangle breaks after <code>=</code> and indents the whole "
                    "<code>try</code> an extra level; ktfmt ergonomics keeps <code>val result = try {</code> attached. "
                    "(okio · Okio.kt:60)",
            "ktfmt": "fun <T> f(block: () -> T): T? {\n    var thrown: Throwable? = null\n    val result =\n        try {\n            block()\n        } catch (t: Throwable) {\n            thrown = t\n            null\n        } finally {\n            cleanup()\n        }\n    return result\n}",
            "optofmt": "fun <T> f(block: () -> T): T? {\n    var thrown: Throwable? = null\n    val result = try {\n        block()\n    } catch (t: Throwable) {\n        thrown = t\n        null\n    } finally {\n        cleanup()\n    }\n    return result\n}",
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
    private val subscriptionWaitingFlow: MutableStateFlow<Int>
) {}""",
        "idiomatic": "optofmt",
    },
    {
        "id": "comment-preservation",
        "name": "Block-comment / KDoc prose is not reflowed",
        "source": "icpc/live-v3 · contest-config KDoc",
        "thesis": "ktfmt ergonomics preserves the author's comment line breaks; ktfmt rectangle rewraps KDoc prose to its own width.",
        "why": "ktfmt rectangle reflows the text inside <code>/** … */</code> KDoc comments to fill the column, "
               "merging and re-splitting sentences the author laid out deliberately and churning "
               "diffs on unrelated edits. ktfmt ergonomics treats comment text as opaque: it owns the "
               "surrounding whitespace but never reflows the words, so hand-formatted comment blocks, "
               "tables, and lists survive intact.",
        "input": """/**
 * Ideally, all this information should be received from the contest system.
 * Unfortunately, in the real world, it is not always possible, or information
 * can be not fully correct or convenient to display.
 */
class ContestConfigOverrides""",
        "ktfmt": """/**
 * Ideally, all this information should be received from the contest system. Unfortunately, in the
 * real world, it is not always possible, or information can be not fully correct or convenient to
 * display.
 */
class ContestConfigOverrides""",
        "optofmt": """/**
 * Ideally, all this information should be received from the contest system.
 * Unfortunately, in the real world, it is not always possible, or information
 * can be not fully correct or convenient to display.
 */
class ContestConfigOverrides""",
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
        "id": "elvis-wrap",
        "name": "Elvis (`?:`) operator wrap",
        "source": "kotlin-toolchain · PetTypeFormatter.kt:44",
        "thesis": "Parity — both put `?:` at the start of the continuation line (the kotlinx-majority style).",
        "why": "Elvis is one of the operators that reads best with the operator leading the "
               "continuation line, and both engines agree: keep the left side on the first line and "
               "start the wrapped line with <code>?:</code> at one indent. (This is the opposite of "
               "the chain operators like <code>&amp;&amp;</code>, which trail.)",
        "input": "fun f(): PetType { return findPetTypes.find { it.name == text } ?: "
                 "throw ParseException(\"type not found: \" + text, 0) }",
        "ktfmt": """fun f(): PetType {
    return findPetTypes.find { it.name == text }
        ?: throw ParseException("type not found: " + text, 0)
}""",
        "optofmt": """fun f(): PetType {
    return findPetTypes.find { it.name == text }
        ?: throw ParseException("type not found: " + text, 0)
}""",
        "idiomatic": "parity",
    },
    {
        "id": "annotation-placement",
        "name": "Annotation with arguments on its own line",
        "source": "Kotlin project · ktfmt diff study",
        "thesis": "ktfmt ergonomics drops an argument-carrying annotation onto its own line above the declaration; ktfmt rectangle keeps it inline with `fun`.",
        "why": "Kotlin convention places an annotation that carries arguments "
               "(<code>@JvmName(\"other\")</code>, <code>@Test</code>, <code>@Deprecated(...)</code>) on "
               "its own line directly above the declaration; only argument-less modifier-like "
               "annotations (<code>@PublishedApi</code>, <code>@JvmStatic</code>) stay inline. ktfmt rectangle "
               "keeps every annotation glued to the declaration line, so "
               "<code>@JvmName(\"other\") fun testSomething() {}</code> reads as a single run and the "
               "annotation loses the visual separation a reader expects. ktfmt ergonomics breaks after the "
               "argument-carrying annotation (§9).",
        "input": '@JvmName("other") fun testSomething() {}',
        "ktfmt": '@JvmName("other") fun testSomething() {}',
        "optofmt": '@JvmName("other")\nfun testSomething() {}',
        "idiomatic": "optofmt",
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
        "id": "generic-type-arg-economy",
        "name": "Long generic type-argument list",
        "source": "Exposed · EntityCache.kt",
        "thesis": "A generic type-argument list is not a wrappable body, so ktfmt ergonomics keeps the type whole and breaks after `=` — landing on the same compact two-line layout as ktfmt rectangle. Parity.",
        "why": "When the declaration overflows, §3 keeps the introducer (<code>=</code>) attached only when "
               "the right-hand side has a wrappable <em>body</em> — and §4 names exactly which: call "
               "arguments, parameters, collection literals, <code>when</code> entries. A generic "
               "type-argument list <code>&lt;…&gt;</code> is none of those (nor a call chain, §7, nor a "
               "nested call group, §5): <code>IdentityHashMap&lt;…&gt;()</code> is a single type applied "
               "to an empty <code>()</code>. With no §3 body to wrap, the only break that clears the "
               "overflow is after <code>=</code>. Among the legal layouts §1 then decides: break-after-"
               "<code>=</code> keeps the type intact in <strong>two</strong> lines (the wrapped line is "
               "74 cols, well within 100), whereas tearing the type open inside the angle brackets costs "
               "<strong>three</strong> — so §1's fewest-lines tiebreaker picks the two-line form, and "
               "ktfmt ergonomics and ktfmt rectangle agree. (The prototype currently tears the type across three lines, "
               "leaving a dangling <code>&lt;</code> and a lonely <code>&gt;()</code> — it over-applies "
               "§3/§5 to a construct they don't cover and violates §1's own line count. That is a bug in "
               "the executable, not the layout the rules prescribe.)",
        "input": "class C {\ninternal val pendingInitializationLambdas = "
                 "IdentityHashMap<Entity<Any>, MutableList<(Entity<Any>) -> Unit>>()\n}",
        "ktfmt": """class C {
    internal val pendingInitializationLambdas =
        IdentityHashMap<Entity<Any>, MutableList<(Entity<Any>) -> Unit>>()
}""",
        "optofmt": """class C {
    internal val pendingInitializationLambdas =
        IdentityHashMap<Entity<Any>, MutableList<(Entity<Any>) -> Unit>>()
}""",
        "idiomatic": "parity",
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
                "optofmt": "package org.jetbrains.exposed.sql.vendors\n\nval ANSI_SQL_2003_KEYWORDS: Set<String> = setOf(\n    \"A\",\n    \"ABS\",\n    \"ABSOLUTE\",\n    \"ACTION\",\n    \"ADA\",\n    \"ADD\",\n    \"ADMIN\",\n    \"AFTER\",\n    \"ALL\",\n    \"ALLOCATE\",\n    \"ALTER\",\n    \"ALWAYS\",\n    \"AND\",\n    \"ANY\",\n    \"ARE\",\n    \"ARRAY\",\n    \"AS\",\n    \"ASC\"\n)",
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
        "thesis": "When a class header is too long and must break after the supertype colon, ktfmt ergonomics puts each supertype on its own line (a fully-split list per \u00a74); ktfmt rectangle packs all supertypes onto the single continuation line.",
        "why": "Distinct from <em>supertype constructor attached to <code>:</code></em>: here <strong>both</strong> formatters break after the colon; the divergence is list layout. ktfmt ergonomics treats the supertype list like any comma list \u2014 compact or fully split, never fill-packed (\u00a74) \u2014 so each supertype sits on its own line, matching the hand-written original. ktfmt rectangle packs every supertype onto a single continuation line.",
        "input": "internal abstract class ArrayValueExpressionMixin(node: ASTNode) :\n  SqlCompositeElementImpl(node),\n  SqlExpr,\n  PostgreSqlArrayValueExpression {\n  val x = 1\n}",
        "ktfmt": "internal abstract class ArrayValueExpressionMixin(node: ASTNode) :\n    SqlCompositeElementImpl(node), SqlExpr, PostgreSqlArrayValueExpression {\n    val x = 1\n}",
        "optofmt": "internal abstract class ArrayValueExpressionMixin(node: ASTNode) :\n    SqlCompositeElementImpl(node),\n    SqlExpr,\n    PostgreSqlArrayValueExpression {\n    val x = 1\n}",
        "idiomatic": "optofmt",
    },
    {
        "id": "supertype-by-delegation-attached",
        "name": "Supertype `by` delegation attached to `:`, `as` cast wraps",
        "source": "kotlinx.coroutines \u00b7 BufferedChannel.kt:239",
        "thesis": "For a class header whose supertype list is an interface delegation, ktfmt ergonomics keeps `: Iface by delegate` on the header line and wraps only the trailing `as Cast` onto the next line at one indent; ktfmt rectangle breaks right after `:` and pushes the entire `Iface by delegate as Cast` down a level.",
        "why": "<code>:</code> is an introducer (\u00a73): keep it and the delegate attached, and wrap only the overflowing tail. ktfmt ergonomics leaves <code>: Waiter by cont</code> on the header line and drops the trailing <code>as CancellableContinuationImpl&lt;Boolean&gt;</code> to one indent; ktfmt rectangle breaks right after <code>:</code> and re-indents the whole <code>Iface by delegate as Cast</code> clause even though only the cast needed room.",
        "input": "private class SendBroadcast(val cont: CancellableContinuation<Boolean>) : Waiter by cont as CancellableContinuationImpl<Boolean>",
        "ktfmt": "private class SendBroadcast(val cont: CancellableContinuation<Boolean>) :\n    Waiter by cont as CancellableContinuationImpl<Boolean>",
        "optofmt": "private class SendBroadcast(val cont: CancellableContinuation<Boolean>) : Waiter by cont\n    as CancellableContinuationImpl<Boolean>",
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
