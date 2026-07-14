"""The ktfmt-comparison corpus: one entry per distinct layout problem.

Each entry:
  id        - stable slug
  group     - integer; related cards share a group number (shown as a badge)
  name      - the pattern/problem, used as the card title
  source    - where the example came from
  thesis    - one-line summary shown under the title
  input     - raw Kotlin (what you'd paste in); ktfmt output is reproducible from it
  ktfmt     - real `./ktfmt.sh` output, the ktfmt rectangle column (Kotlin-language
              style, 4-space, 100 cols)
  optofmt   - the ktfmt ergonomics layout per RULES.md
  third     - optional {"label", "code"}: a strictly better option neither column
              produces (e.g. a refactor); shown as a third column when present

The ktfmt column is stored verbatim from the bundled formatter (rectangle). The optofmt
column is the ktfmt ergonomics layout expected from the rules in RULES.md; regenerate/
verify them with the skills.
"""

SNIPPETS = [
    {
        "id": "boolean-condition",
        "group": 1,
        "name": "Boolean conditions",
        "source": "kotlinx.coroutines · JobSupport.kt:273",
        "thesis": "A single condition is laid out identically by both engines.",
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
        "extra": [{
            "note": "Add more conditions and the line must wrap: ktfmt rectangle pushes each operand "
                    "after the first a level deeper. ktfmt ergonomics keeps every operand at one indent. "
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
        "group": 2,
        "name": "Nested call with a long argument",
        "source": "synthetic example",
        "thesis": "A short nested call, the same story — identical layout at first.",
        "input": "fun f() { registerHandler(buildHandler(handler)) }",
        "ktfmt": """fun f() {
    registerHandler(buildHandler(handler))
}""",
        "optofmt": """fun f() {
    registerHandler(buildHandler(handler))
}""",
        "extra": [{
            "note": "Rename the argument to one long enough to overflow, and the inner call must "
                    "break.",
            "ktfmt": """fun f() {
    registerHandler(
        buildHandler(
            aLongUnbreakableHandlerArgumentDeliberatelySizedToOverflowTheHundredColumnLimit
        )
    )
}""",
            "optofmt": """fun f() {
    registerHandler(
        buildHandler(
            aLongUnbreakableHandlerArgumentDeliberatelySizedToOverflowTheHundredColumnLimit,
        )
    )
}""",
            "third": """fun f() {
    registerHandler(buildHandler(
        aLongUnbreakableHandlerArgumentDeliberatelySizedToOverflowTheHundredColumnLimit,
    ))
}""",
        }],
    },
    {
        "id": "indent-economy",
        "group": 2,
        "name": "Nested call argument wrapping",
        "source": "icpc/live-v3 · Rules.kt:219",
        "thesis": "A single nested positional call argument that is long enough to break.",
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
        "extra": [{
            "note": "Change the argument from positional to named as part of the code evolution.",
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
        )
    )
}""",
        }, {
            "note": "Now it's two named arguments, each being an expandable call.",
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
        }],
    },
    {
        "id": "infix-attached",
        "group": 3,
        "name": "Infix call (`to`) stays attached",
        "source": "icpc/live-v3 · OverrideOrganizations",
        "thesis": "Reasonably long infix `to` operator.",
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
        "extra": [{
            "note": "Add an explicit type so the line no longer fits the limit and should be broken.",
            "ktfmt": """val pair: Pair<OrganizationId, OverrideOrganizations.Override> =
    orgInfo.id to
        OverrideOrganizations.Override(
            fullName = substituteRaw(fullName),
            displayName = substituteRaw(displayName),
        )""",
            "optofmt": """val pair: Pair<OrganizationId, OverrideOrganizations.Override> = orgInfo.id to
    OverrideOrganizations.Override(
        fullName = substituteRaw(fullName),
        displayName = substituteRaw(displayName),
    )""",
        }],
    },
    {
        "id": "supertype-attached",
        "group": 3,
        "name": "Supertype constructor call stays attached to `:`",
        "source": "icpc/live-v3 · ClicsArchiveCommand",
        "thesis": "Supertype that is long enough to have a linebreak.",
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
        "extra": [{
            "note": "Then add a few interfaces to the supertype list.",
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
        }, {
            "note": "Drop the constructor and leave only interfaces.",
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
        }],
    },
    {
        "id": "long-call-chain",
        "group": 4,
        "name": "Long call chain",
        "source": "icpc/live-v3 · CdsLoadersTest",
        "thesis": "A long chain call -- one of the most popular patterns in Kotlin",
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
    },
    {
        "id": "delegate-call-chain",
        "group": 4,
        "name": "Delegated property (`by`) call chain",
        "source": "ktor client · delegated response",
        "thesis": "",
        "input": "val list by get().response<TagsResponse>().failure<GenericErrorModel>(HttpStatusCode.UnprocessableEntity)",
        "ktfmt": """val list by
    get().response<TagsResponse>().failure<GenericErrorModel>(HttpStatusCode.UnprocessableEntity)""",
        "optofmt": """val list by get()
    .response<TagsResponse>()
    .failure<GenericErrorModel>(HttpStatusCode.UnprocessableEntity)""",
    },
    {
        "id": "block-rhs",
        "group": 5,
        "name": "Block-valued right-hand side (`when`/`if`/`try`) stays on the `=` line",
        "source": "icpc/live-v3 · AbstractScoreboardCalculator.kt:202",
        "thesis": "",
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
        "extra": [{
            "note": "Time passes and someone adds an explicit type that is long enough to break the line.",
            "input": "fun f() {\nval teamsAffected: List<org.jetbrains.kotlinx.icpc.TeamId> = when (val event = state.lastEvent) {\n"
                     "is CommentaryMessagesUpdate -> emptyList()\nis InfoUpdate -> info.teams.keys.toList()\n"
                     "is RunUpdate -> {\nlastSubmissionTime = maxOf(lastSubmissionTime, event.newInfo.time)\n"
                     "runsByTeamId.applyEvent(state)\n}\n}\n}",
            "ktfmt": """fun f() {
    val teamsAffected: List<org.jetbrains.kotlinx.icpc.TeamId> =
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
    val teamsAffected: List<org.jetbrains.kotlinx.icpc.TeamId> = when (
        val event = state.lastEvent
    ) {
        is CommentaryMessagesUpdate -> emptyList()
        is InfoUpdate -> info.teams.keys.toList()
        is RunUpdate -> {
            lastSubmissionTime = maxOf(lastSubmissionTime, event.newInfo.time)
            runsByTeamId.applyEvent(state)
        }
    }
}""",
        }, {
            "note": "A similar example -- but now with <code>if</code> condition",
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
            "note": "The same next step -- we are adding an explicit type that forces the line to break",
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
        }, {
            "note": "A <code>try</code>/<code>catch</code>/<code>finally</code> used in a similar manner. "
                    "(Okio.kt:60)",
            "ktfmt": "fun <T> f(block: () -> T): T? {\n    var thrown: Throwable? = null\n    val result =\n        try {\n            block()\n        } catch (t: Throwable) {\n            thrown = t\n            null\n        } finally {\n            cleanup()\n        }\n    return result\n}",
            "optofmt": "fun <T> f(block: () -> T): T? {\n    var thrown: Throwable? = null\n    val result = try {\n        block()\n    } catch (t: Throwable) {\n        thrown = t\n        null\n    } finally {\n        cleanup()\n    }\n    return result\n}",
        }],
    },
    {
        "id": "accessor-block-body",
        "group": 5,
        "name": "Block-valued accessor (`get() = when`) stays on the property line",
        "source": "kotlinx-knit · linked in review thread",
        "thesis": "",
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
    },
    {
        "id": "trailing-lambda",
        "group": 6,
        "name": "Trailing lambda / last-argument expansion",
        "source": "icpc/live-v3",
        "thesis": "",
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
    },
    {
        "id": "compact-header",
        "group": 7,
        "name": "Compact declaration header (annotations & modifiers)",
        "source": "kotlinx.coroutines · SharedFlowSubscriptionScope",
        "thesis": "",
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
    },
    {
        "id": "grouped-declarations",
        "group": 7,
        "name": "Grouped one-line declarations keep no blank lines",
        "source": "synthetic",
        "thesis": "",
        "input": """typealias TeamId = StrongId<TeamTag>
typealias RunId = StrongId<RunTag>
typealias MessageId = StrongId<MessageTag>""",
        "ktfmt": """typealias TeamId = StrongId<TeamTag>

typealias RunId = StrongId<RunTag>

typealias MessageId = StrongId<MessageTag>""",
        "optofmt": """typealias TeamId = StrongId<TeamTag>
typealias RunId = StrongId<RunTag>
typealias MessageId = StrongId<MessageTag>""",
    },
    {
        "id": "elvis-fits",
        "group": 8,
        "name": "Elvis (`?:`) stays inline when it fits",
        "source": "null-fallback idiom",
        "thesis": "A short enough expression with elvis.",
        "input": "fun f() { val entry = registry.lookup(requestedName) ?: registry.defaultFor(requestedName) }",
        "ktfmt": """fun f() {
    val entry = registry.lookup(requestedName) ?: registry.defaultFor(requestedName)
}""",
        "optofmt": """fun f() {
    val entry = registry.lookup(requestedName) ?: registry.defaultFor(requestedName)
}""",
        "extra": [{
            "note": "Now let's make this expression longer so it has to be broken in two lines.",
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
        }],
    },
    {
        "id": "accessor-placement",
        "group": 8,
        "name": "Trivial property accessor stays on the property line",
        "source": "Kotlin project · ktfmt diff study",
        "thesis": "",
        "input": 'val placeOfGetter: String get() = "hello"',
        "ktfmt": 'val placeOfGetter: String\n    get() = "hello"',
        "optofmt": 'val placeOfGetter: String get() = "hello"',
    },
    {
        "id": "control-flow-lambda",
        "group": 6,
        "name": "Lambda that fits stays on one line (even with `return`)",
        "source": "Kotlin project · ktfmt diff study",
        "thesis": "",
        "input": "fun lambdasWithReturns(nullableString: String?) { nullableString?.let { return } }",
        "ktfmt": """fun lambdasWithReturns(nullableString: String?) {
    nullableString?.let {
        return
    }
}""",
        "optofmt": """fun lambdasWithReturns(nullableString: String?) {
    nullableString?.let { return }
}""",
    },
    {
        "id": "when-comma-condition",
        "group": 8,
        "name": "Comma-separated `when` conditions stay on one line when they fit",
        "source": "synthetic",
        "thesis": "",
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
        "extra": [{
            "note": "",
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
        }],
    },
    {
        "id": "assign-introducer-attached",
        "group": 8,
        "name": "Introducer `=` stays attached (scope-function / concatenation / collection)",
        "source": "okio \u00b7 Okio.kt:60",
        "thesis": "",
        "input": "fun digest(algorithm: String): ByteString {\nval digestBytes = MessageDigest.getInstance(algorithm).run {\nupdate(data, 0, size)\ndigest()\n}\nreturn ByteString(digestBytes)\n}",
        "ktfmt": "fun digest(algorithm: String): ByteString {\n    val digestBytes =\n        MessageDigest.getInstance(algorithm).run {\n            update(data, 0, size)\n            digest()\n        }\n    return ByteString(digestBytes)\n}",
        "optofmt": "fun digest(algorithm: String): ByteString {\n    val digestBytes = MessageDigest.getInstance(algorithm).run {\n        update(data, 0, size)\n        digest()\n    }\n    return ByteString(digestBytes)\n}",
        "extra": [
            {
                "note": "",
                "ktfmt": "fun f() {\n    val raw =\n        (\"Um, I'll tell you the problem with the scientific power that you're using here, \" +\n            \"it didn't require any discipline to attain it. You read what others had done and you \" +\n            \"took the next step. You didn't earn the knowledge for yourselves, so you don't take any \")\n}",
                "optofmt": "fun f() {\n    val raw = (\"Um, I'll tell you the problem with the scientific power that you're using here, \" +\n        \"it didn't require any discipline to attain it. You read what others had done and you \" +\n        \"took the next step. You didn't earn the knowledge for yourselves, so you don't take any \")\n}",
            },
            {
                "note": "",
                "ktfmt": "package org.jetbrains.exposed.sql.vendors\n\nval ANSI_SQL_2003_KEYWORDS: Set<String> =\n    setOf(\n        \"A\",\n        \"ABS\",\n        \"ABSOLUTE\",\n        \"ACTION\",\n        \"ADA\",\n        \"ADD\",\n        \"ADMIN\",\n        \"AFTER\",\n        \"ALL\",\n        \"ALLOCATE\",\n        \"ALTER\",\n        \"ALWAYS\",\n        \"AND\",\n        \"ANY\",\n        \"ARE\",\n        \"ARRAY\",\n        \"AS\",\n        \"ASC\",\n    )",
                "optofmt": "package org.jetbrains.exposed.sql.vendors\n\nval ANSI_SQL_2003_KEYWORDS: Set<String> = setOf(\n    \"A\",\n    \"ABS\",\n    \"ABSOLUTE\",\n    \"ACTION\",\n    \"ADA\",\n    \"ADD\",\n    \"ADMIN\",\n    \"AFTER\",\n    \"ALL\",\n    \"ALLOCATE\",\n    \"ALTER\",\n    \"ALWAYS\",\n    \"AND\",\n    \"ANY\",\n    \"ARE\",\n    \"ARRAY\",\n    \"AS\",\n    \"ASC\",\n)",
            },
        ],
    },
    {
        "id": "argumentless-annotation-own-line",
        "group": 9,
        "name": "Argument-less annotation on its own line",
        "source": "sqldelight \u00b7 SqlDelightExtension.kt:6",
        "thesis": "Well, a @DslMaker",
        "input": "@DslMarker\nannotation class SqlDelightDsl",
        "ktfmt": "@DslMarker annotation class SqlDelightDsl",
        "optofmt": "@DslMarker\nannotation class SqlDelightDsl",
        "extra": [
            {
                "note": "An annotation on a function declaration.",
                "ktfmt": '@JvmName("other") fun testSomething() {}',
                "optofmt": '@JvmName("other")\nfun testSomething() {}',
            },
            {
                "note": "An annotation on a function declaration, slightly different context",
                "ktfmt": "class FooTest {\n    @Test fun `kotlin-stdlib-1_9_20`(testInfo: TestInfo) = doTest(testInfo)\n}",
                "optofmt": "class FooTest {\n    @Test\n    fun `kotlin-stdlib-1_9_20`(testInfo: TestInfo) = doTest(testInfo)\n}",
            },
            {
                "note": "Multiple annotations on a getter.",
                "ktfmt": "class Database private constructor(val config: DatabaseConfig) {\n    var useNestedTransactions: Boolean = config.useNestedTransactions\n        @Deprecated(\"Use DatabaseConfig to define the useNestedTransactions\") @TestOnly set\n}",
                "optofmt": "class Database private constructor(val config: DatabaseConfig) {\n    var useNestedTransactions: Boolean = config.useNestedTransactions\n        @Deprecated(\"Use DatabaseConfig to define the useNestedTransactions\")\n        @TestOnly\n        set\n}",
            },
        ],
    },
    {
        "id": "multi-supertype-list-one-per-line",
        "group": 9,
        "name": "Multiple supertypes: one per line, never packed",
        "source": "sqldelight \u00b7 ArrayValueExpressionMixin.kt:20",
        "thesis": "",
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
    },
    {
        "id": "small-overflow-tolerance",
        "group": 10,
        "name": "Small overflow tolerated instead of exploding a compact signature",
        "source": "sqldelight \u00b7 SqlDelightRefactoringSupportProvider.kt:8",
        "thesis": "When a signature spills only 1\u20132 columns past 100, ktfmt ergonomics keeps it on one line (matching the hand-written source); ktfmt rectangle explodes the parameter list one-per-line the instant it crosses 100.",
        "input": "class C : RefactoringSupportProvider() {\n  override fun isMemberInplaceRenameAvailable(element: PsiElement, context: PsiElement?): Boolean {\n    return element is NamedElement\n  }\n}",
        "ktfmt": "class C : RefactoringSupportProvider() {\n    override fun isMemberInplaceRenameAvailable(\n        element: PsiElement,\n        context: PsiElement?,\n    ): Boolean {\n        return element is NamedElement\n    }\n}",
        "optofmt": "class C : RefactoringSupportProvider() {\n    override fun isMemberInplaceRenameAvailable(element: PsiElement, context: PsiElement?): Boolean {\n        return element is NamedElement\n    }\n}",
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
        "group": 10,
        "name": "Trailing line-comment does not force a wrap",
        "source": "kotlinx.coroutines \u00b7 DebugCoroutineInfo.kt:18",
        "thesis": "When only a trailing <code>// comment</code> pushes a line past 100, ktfmt ergonomics keeps the whole line intact (matching the author); ktfmt rectangle wraps the value onto a new line to fit.",
        "input": "class DebugCoroutineInfo {\n    internal val creationStackBottom: CoroutineStackFrame? = source.creationStackBottom // field is used as of 1.4-M3\n}",
        "ktfmt": "class DebugCoroutineInfo {\n    internal val creationStackBottom: CoroutineStackFrame? =\n        source.creationStackBottom // field is used as of 1.4-M3\n}",
        "optofmt": "class DebugCoroutineInfo {\n    internal val creationStackBottom: CoroutineStackFrame? = source.creationStackBottom // field is used as of 1.4-M3\n}",
    },
    {
        "id": "raw-string-sole-arg-attached",
        "group": 10,
        "name": "Triple-quoted string as sole call argument stays attached",
        "source": "kotlinx.coroutines \u00b7 CoroutineExceptionHandlerImpl.kt:17",
        "thesis": "",
        "input": "fun f() {\n    js(\"\"\"\n        var errorNo = new Error();\n        error.message = message;\n    \"\"\")\n}",
        "ktfmt": "fun f() {\n    js(\n        \"\"\"\n        var error = new Error();\n        error.message = message;\n    \"\"\"\n    )\n}",
        "optofmt": "fun f() {\n    js(\"\"\"\n        var error = new Error();\n        error.message = message;\n    \"\"\")\n}",
    },
]
