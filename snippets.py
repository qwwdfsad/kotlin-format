"""The optofmt corpus: one entry per distinct layout problem.

Each entry:
  id        - stable slug
  name      - the pattern/problem, used as the card title
  source    - where the example came from
  thesis    - one-line summary shown under the title
  why       - longer explanation (collapsed under "Why")
  input     - raw Kotlin (what you'd paste in); ktfmt output is reproducible from it
  ktfmt     - real `./ktfmt.sh` output (Kotlin-language style, 4-space, 100 cols)
  optofmt   - the optofmt layout per RULES.md
  third     - optional {"label", "code"}: a strictly better option neither formatter
              produces (e.g. a refactor); shown as a third column when present
  idiomatic - which column is the idiomatic one (highlighted in green):
              "optofmt" | "ktfmt" | "third" | "parity" (parity = no clear winner)

ktfmt columns are stored verbatim from the bundled formatter. optofmt columns are the
expected output of the rules in RULES.md; regenerate/verify them with the skills.
"""

SNIPPETS = [
    {
        "id": "boolean-condition",
        "name": "Multi-line boolean condition",
        "source": "kotlinx.coroutines · JobSupport.kt:273",
        "thesis": "optofmt keeps every operand at one indent; ktfmt pushes each operand after the first a level deeper.",
        "why": "A condition too long for one line must wrap to stacked operands. optofmt opens the "
               "paren and lays every operand at the same body indent — one indentation size, so the "
               "operands form a clean rectangular block. ktfmt adds a continuation indent on top of "
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
        "thesis": "optofmt collapses the wrapper openers and stacks the closers; ktfmt staircases with lonely parens.",
        "why": "When an outer call's single argument is itself a call that must split, optofmt lets the "
               "two openers share a line (<code>add(OverrideQueue(</code>) and the closers collapse "
               "onto one line (<code>))</code>) — the arguments sit one level in. ktfmt cannot share "
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
                    "argument is one unbreakable token. Staircased (ktfmt) it lands at indent 12 "
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
        }],
    },
    {
        "id": "infix-attached",
        "name": "Infix call (`to`) stays attached",
        "source": "icpc/live-v3 · OverrideOrganizations",
        "thesis": "optofmt keeps the key and the call opener together; ktfmt breaks after `to` and double-indents.",
        "why": "ktfmt breaks after the infix <code>to</code> and indents the call an extra level, "
               "leaving <code>to</code> dangling at the end of a line. optofmt keeps the introducer "
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
    },
    {
        "id": "supertype-attached",
        "name": "Supertype constructor call stays attached to `:`",
        "source": "icpc/live-v3 · ClicsArchiveCommand",
        "thesis": "optofmt keeps `Name : Base(` on one line; ktfmt breaks after `:` and strands the supertype.",
        "why": "<code>object X : DumpFileCommand(</code> fits on one line, but ktfmt breaks after the "
               "supertype <code>:</code> and indents the constructor call an extra level, leaving the "
               "supertype name alone on its own line. optofmt keeps the introducer attached and wraps "
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
    },
    {
        "id": "block-rhs",
        "name": "Block-valued right-hand side (`when`/`if`) stays on the `=` line",
        "source": "icpc/live-v3 · AbstractScoreboardCalculator.kt:202",
        "thesis": "optofmt keeps `val x = when (…) {` attached; ktfmt pushes the block below `=` and indents every branch deeper.",
        "why": "ktfmt breaks after <code>=</code> and indents the whole block-valued right-hand side an "
               "extra level, although <code>val teamsAffected = when (val event = state.lastEvent) {</code> "
               "fits easily. optofmt treats an assignment prefix like a header and keeps the block "
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
                    "block-valued RHS. ktfmt breaks after <code>=</code> and indents both branches an "
                    "extra level; optofmt keeps <code>val builder = if (!builders.isEmpty()) {</code> "
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
        }],
    },
    {
        "id": "long-call-chain",
        "name": "Long call chain",
        "source": "icpc/live-v3 · CdsLoadersTest",
        "thesis": "optofmt keeps the receiver on the `=` line and breaks each call at one indent; ktfmt breaks after `=` and double-indents.",
        "why": "A fluent chain that overflows breaks before each call. optofmt keeps the receiver on "
               "the introducer's line and puts each subsequent call on its own line at one indent. "
               "ktfmt first breaks after <code>=</code> (an extra line) and then indents the whole "
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
        "id": "trailing-lambda",
        "name": "Trailing lambda / last-argument expansion",
        "source": "synthetic",
        "thesis": "optofmt keeps the leading args inline and lets the block hang off; ktfmt explodes every argument. The most idiomatic move is to take the lambda out of the parentheses entirely.",
        "why": "optofmt may keep leading arguments on the opener line while the final lambda expands "
               "in place, so the call stays compact with the block hanging off the end. ktfmt is "
               "all-or-nothing: once the call doesn't fit, every argument goes on its own line, "
               "including the lambda. Neither moves the lambda; the most idiomatic Kotlin pulls a "
               "trailing lambda outside the parentheses (third column) — a refactor a pure formatter "
               "leaves to the author.",
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
        "third": {
            "label": "idiomatic — trailing lambda outside ()",
            "code": """fun run() {
    executeWithRetryPolicy(maximumRetryCount, backoffStrategy) { requestContext ->
        requestContext.proceed()
    }
}""",
        },
        "idiomatic": "third",
    },
    {
        "id": "compact-header",
        "name": "Compact declaration header (annotations & modifiers)",
        "source": "kotlinx.coroutines · SharedFlowSubscriptionScope",
        "thesis": "optofmt keeps annotations & modifiers on the declaration line; ktfmt drops each onto its own line.",
        "why": "Facing a long constructor header, ktfmt puts the class line, the <code>@PublishedApi</code> "
               "annotation, and <code>internal constructor(</code> on three separate lines before it "
               "even reaches the parameters. optofmt keeps the whole modifier run together and wraps "
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
        "thesis": "optofmt preserves the author's comment line breaks; ktfmt rewraps KDoc prose to its own width.",
        "why": "ktfmt reflows the text inside <code>/** … */</code> KDoc comments to fill the column, "
               "merging and re-splitting sentences the author laid out deliberately and churning "
               "diffs on unrelated edits. optofmt treats comment text as opaque: it owns the "
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
        "thesis": "optofmt keeps a run of one-line declarations tight; ktfmt forces a blank line between each.",
        "why": "ktfmt injects a blank line between consecutive one-line <code>typealias</code> (and "
               "<code>fun</code>) declarations, doubling the height of a tight family of related "
               "one-liners. optofmt preserves the author's grouping: consecutive same-kind "
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
        "thesis": "Parity — both split parameters one per line and keep `) {` together (ktfmt adds a trailing comma).",
        "why": "Included to show the comparison is fair: on the bread-and-butter case the two engines "
               "agree. The only difference is ktfmt's added trailing comma. The wins elsewhere are "
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
    listenerCallback: EventListener
) {
    installListener()
}""",
        "idiomatic": "parity",
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
        "thesis": "optofmt drops an argument-carrying annotation onto its own line above the declaration; ktfmt keeps it inline with `fun`.",
        "why": "Kotlin convention places an annotation that carries arguments "
               "(<code>@JvmName(\"other\")</code>, <code>@Test</code>, <code>@Deprecated(...)</code>) on "
               "its own line directly above the declaration; only argument-less modifier-like "
               "annotations (<code>@PublishedApi</code>, <code>@JvmStatic</code>) stay inline. ktfmt "
               "keeps every annotation glued to the declaration line, so "
               "<code>@JvmName(\"other\") fun testSomething() {}</code> reads as a single run and the "
               "annotation loses the visual separation a reader expects. optofmt breaks after the "
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
        "thesis": "optofmt keeps a short `get()` on the property line because it fits (§1); ktfmt always drops the accessor onto its own line.",
        "why": "ktfmt unconditionally moves a property accessor onto its own indented line, even when "
               "the whole declaration fits: <code>val placeOfGetter: String get() = \"hello\"</code> is "
               "well under 100 columns. optofmt follows the §1 objective — don't wrap what fits — and "
               "keeps the trivial accessor inline, the denser form kotlinx code favours for "
               "one-expression getters. (When the accessor body is long enough to overflow, optofmt "
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
        "thesis": "optofmt keeps a one-line lambda inline because it fits; ktfmt force-expands any lambda containing `return`/`break`/`continue`.",
        "why": "ktfmt preserves author line breaks in lambdas, but it still force-expands a lambda whose "
               "body is a control-flow jump: <code>nullableString?.let { return }</code> becomes three "
               "lines. The single statement fits comfortably, so optofmt keeps it inline per §1 (don't "
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
        "thesis": "optofmt keeps `0, 1 -> …` on one line because it fits (§1/§4); ktfmt force-splits the conditions one per line.",
        "why": "ktfmt treats the comma-separated condition list of a <code>when</code> entry as a "
               "breakable list and splits it one-per-line even when the whole entry fits comfortably: "
               "<code>0, 1 -> println(\"a or b\")</code> becomes two lines for the conditions plus the "
               "body. optofmt follows §1 (don't wrap what fits) and §4 (a comma list is compact when it "
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
                    "splits them one per line. Here the single-line entry is 103 columns, so optofmt "
                    "fully splits the list — exactly what ktfmt does. Parity, not a win: the divergence "
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
        "thesis": "optofmt extends its paren indent-economy to angle brackets — keeping the head on the `=` line and breaking inside `<…>` with the `>()` stacked like a closer — but here that splits an intact generic type across three lines where ktfmt's break-after-`=` keeps it whole in two.",
        "why": "This is the angle-bracket analogue of the indent-economy rule: optofmt would rather keep "
               "<code>val x = IdentityHashMap&lt;</code> on the assignment line and break <em>inside</em> "
               "the type argument list, stacking the closing <code>&gt;()</code> on its own line, than "
               "break after <code>=</code>. For parenthesised argument lists that collapsing is a clear "
               "win, but a generic type is a single conceptual unit: tearing it open leaves a dangling "
               "<code>&lt;</code> and a lonely <code>&gt;()</code>, and costs a line. ktfmt breaks after "
               "<code>=</code> and keeps <code>IdentityHashMap&lt;…&gt;()</code> intact on one "
               "continuation line — fewer lines and the type stays readable, so it reads as the more "
               "idiomatic choice here. A case where optofmt's economy instinct overreaches; the same "
               "mechanism applied to a long extension-receiver type produces genuinely broken output.",
        "input": "class C {\ninternal val pendingInitializationLambdas = "
                 "IdentityHashMap<Entity<Any>, MutableList<(Entity<Any>) -> Unit>>()\n}",
        "ktfmt": """class C {
    internal val pendingInitializationLambdas =
        IdentityHashMap<Entity<Any>, MutableList<(Entity<Any>) -> Unit>>()
}""",
        "optofmt": """class C {
    internal val pendingInitializationLambdas = IdentityHashMap<
        Entity<Any>, MutableList<(Entity<Any>) -> Unit>
    >()
}""",
        "idiomatic": "ktfmt",
    },
]
