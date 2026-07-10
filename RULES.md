# optofmt — optimizing Kotlin formatting rules

`optofmt` is a layout model for Kotlin. Where the common greedy formatter (`ktfmt`) fills
each line left-to-right and adds a fresh indent level every time it wraps, `optofmt` chooses
line breaks by **global optimization** and reuses **one indentation size** for every step.
The result reads like hand-written idiomatic Kotlin (the style of kotlinx libraries).

These rules are the source of truth. Given a Kotlin snippet you should be able to produce
the `optofmt` layout from them alone. Settings: **4 spaces per indent level**, **100-column
limit**.

---

[//]: # (Seva's note: courtesy of strictfmt rules)
## 1. The objective (how breaks are chosen)

For each region between mandatory breaks (statements, block boundaries), consider the legal
layouts and pick the best one by this ordered objective:

1. **Minimize the worst overflow.** Look at the single line that sticks out furthest past
   column 100; make that overshoot as small as possible. Any layout with no overflowing line
   beats any layout that has one.
2. **Then minimize how many lines overflow.**
3. **Then minimize the total number of lines.**
4. **Then prefer the layout whose deepest break sits at the shallowest indentation** (and,
   all else equal, the more compact one).

In short: don't wrap if it fits; when you must wrap, prefer the layout that overflows least,
then the one with the fewest lines, then the flattest one.

## 2. One indentation size — no drift

Every indentation step is exactly **one level (4 spaces)**. There is no separate
"continuation indent" stacked on top of a block indent. When something wraps, the wrapped
parts sit at exactly one level deeper than their owner — never two, and never drifting
further right per operand.

```kotlin
// optofmt — operands form a flat block
if (
    firstCondition &&
    secondCondition &&
    thirdCondition
) { … }
```

The wrong shape (which greedy formatters produce) indents operand 2+ an extra level past
operand 1. optofmt never does that.

## 3. Keep the introducer attached

Do **not** break right after an "introducer" token just to give its right-hand side a fresh
indented block. Keep the introducer on the same line as the opener it introduces, and let the
body or argument list wrap instead. Introducers include:

- assignment `=`
- the supertype colon `:` in a class/object header
- an infix call such as `to`
- the delegation keyword `by` — both a property delegate (`val x by provideDelegate(…)`) and a
  class delegate (`class C : I by impl`)

```kotlin
// optofmt
val teams = when (val e = state.lastEvent) { … }          // not: val teams =\n    when (…) {
object X : DumpFileCommand(name = "a", help = "b") { … }   // not: object X :\n    DumpFileCommand(
val pair = key to Override(fullName = a, displayName = b)  // not: key to\n    Override(
val cfg by provideDelegate(firstArgument, secondArgument)  // not: val cfg by\n    provideDelegate(
```

When the right-hand side is itself too long, keep the introducer + opener on the first line
and wrap the *contents* (see §4/§5), still at a single indent.

**Expression-body functions — a whole-RHS line break is author-preserving.** For a function whose
body is an expression (`fun f() = <rhs>`), attaching is the default but not forced. When the author
already broke the line *right after* the `=` **and** the entire right-hand side fits on that one
line, keep it there whole — do **not** pull it back onto the `=` line and split it (a wrapped
`if/else`, a staircased chain, one-argument-per-line). This is the same author-preservation as a
chain's receiver break (§7): optofmt keeps the single-line form the author chose, and an attached
RHS keeps the default attach-and-wrap. Both forms are idempotent. This carve-out applies **only** to
expression-body functions — every other introducer (property initializer, assignment, named
argument, `by`, infix `to`) always uses the default attach behavior above.

```kotlin
// author wrote the RHS on its own line and it fits → preserved whole (not split onto three lines):
public suspend fun <T> awaitAll(vararg deferreds: Deferred<T>): List<T> =
    if (deferreds.isEmpty()) emptyList() else AwaitAll(deferreds).await()

// a chain the author placed on its own line stays whole (not: receiver attached, `.call` dangling):
public suspend fun <T> Flow.Publisher<T>.awaitFirstOrNull(): T =
    FlowAdapters.toPublisher(this).awaitFirstOrNull()
```

**Nested introducers — the innermost yields first.** When introducers nest (an assignment `=`
whose right-hand side is itself an infix `to`, `by`, etc.) and the whole `= left to opener(` unit
is too long to sit on one line, keep the **outer** introducer attached and break after the
**inner** one — never the reverse. So a typed `val` whose header pushes the expression past the
column limit keeps `= left to` on the first line and drops the infix's right-hand side to a single
indent, rather than breaking after `=`:

```kotlin
// optofmt — `=` stays attached, the infix `to` breaks (its RHS opener at one indent, args at two):
val pair: Pair<OrganizationId, OverrideOrganizations.Override> = orgInfo.id to
    OverrideOrganizations.Override(
        fullName = substituteRaw(fullName),
        displayName = substituteRaw(displayName),
    )
```

(The sole call `OverrideOrganizations.Override(…)` is still never split between its receiver and
its call — a receiver-through-first-call is atomic, §7.)

## 4. Lists are compact or fully split

A comma-separated list (call arguments, parameters, collection literals, `when` entries with
commas) is either **all on one line** or **one item per line** — never a "fill" that packs
several per line. When it splits one-per-line, a trailing comma follows the final item (see §14).

```kotlin
call(a, b, c)                  // fits → one line, no trailing comma

call(
    firstArgument,
    secondArgument,
    thirdArgument,             // multi-line → trailing comma (§14)
)
```

**Last-item expansion.** Leading items may stay on the opener line while the *final* item
expands in place — most importantly a trailing lambda. Keep the call compact and let the block
hang off the end, as long as the opener line (up to the final item's own opener) fits in 100
columns; otherwise fall back to one-item-per-line.

```kotlin
execute(retryCount, backoff, { ctx: Ctx ->
    ctx.proceed()
})
```

(`optofmt` is layout-only: it does not *move* a trailing lambda outside the parentheses, even
though that is the most idiomatic Kotlin. That is a refactor left to the author.)

**Custom formatting — author-directed expansion.** The compact-or-split choice is normally decided
by fit (§1: don't wrap if it fits). But the author may *force* the split: **a line break placed
immediately after the opening `(` (call or declaration parameter list) or `[` (collection literal)
keeps that list one item per line**, even when the whole thing would fit on a single line. Removing
the break (joining the opener and first element onto one line) lets the list collapse again — so the
author toggles the layout by where they put the first newline. (A lambda body has the same
author-directed control off its `->`/`{` — see §13.)

```kotlin
foo(a, b, c)          // one line — collapses

foo(                  // newline right after `(` → stays exploded, even though it would fit
    a,
    b,
    c,
)
```

A trailing lambda's own header (`{ params ->`) is atomic and never splits — see **§13**.

## 5. Indent economy — hug block bodies, expand nested calls

When a call's **sole argument is a block body** — a trailing lambda, or an `object` expression —
let the opener share the call's line and let the closers **stack together**, so the body sits at a
single indent instead of staircasing:

```kotlin
// optofmt — the object body hugs the call opener; `})` stacks:
onSubscribe(object : Subscription {
    override fun request(n: Long) { … }
})
```

A **chain that ends in a trailing lambda** is block-like in the same way: a call whose sole argument
is a base call plus a sole trailing-lambda tail (`flow { … }.none { … }`, §7) hugs the opener too —
the base's block opens on the call line and the `})` closers stack:

```kotlin
// optofmt — the block-like chain hangs off `assertFalse(`; `})` stacks:
assertFalse(flow {
    emit(1)
    emit(2)
}.none {
    it == 2
})
```

The same opener-hugging applies when a call's **sole argument is itself a call or constructor**
that must wrap: the two openers **collapse onto one line** and the closers **stack together** as
`))`, so the inner argument list sits at a single indent instead of staircasing. This keys on
argument **count**, not on whether the argument is named — a named sole argument behaves the same,
with `name =` kept on the opener line (§3). Because the outer call carries a single block-like value
— not a one-per-line split — it takes **no outer trailing comma**; the inner list wraps and commas
normally (§14):

```kotlin
// optofmt — the nested call hugs the outer opener; `))` stacks, no outer comma:
add(OverrideQueue(
    waitTime,
    firstToSolveWaitTime,
    maxQueueSize,
))

add(queue = OverrideQueue(
    waitTime,
    firstToSolveWaitTime,
    maxQueueSize,
))
```

With **two or more arguments** there is no single opener to hug, so the outer list simply splits
**one argument per line** (§4) and each nested call expands in place:

```kotlin
add(
    queue = OverrideQueue(
        waitTime,
        firstToSolveWaitTime,
        maxQueueSize,
    ),
    foo = OverrideQueue(
        waitTime,
        firstToSolveWaitTime,
        maxQueueSize,
    ),
)
```

## 6. Operator wrapping

- **Chained operators** — `&&`, `||`, `+`, `*`, and the like — wrap with the operator at the
  **end** of the line, every operand at a single shared indent (§2). Keep the first operand on
  the introducer's line when it fits.
- **Binary operators are treated as infix functions.** A **mixed-operator** expression (operators
  of different precedence, e.g. `a - b * c(…) - d`) is a *single* flat block: every operand sits at
  the **same** shared indent regardless of precedence or how the parse tree nests it. A
  higher-precedence sub-expression (the `b * c(…)` inside a `-` expression) never staircases its
  operands to a second, deeper indent — the outermost operator supplies the one continuation indent
  and every operand of the whole expression aligns under it.

  ```kotlin
  // optofmt — every operand at one shared indent, `*` does not drift deeper than `-`
  ceil(
      maxScore -
      submission.relativeTimeSeconds.inWholeMinutes *
      getProblemLooseScorePerMinute(maxScore, contestLength.inWholeMinutes),
  )
  ```
- **Elvis `?:`** stays on the **same line** as its left-hand side **when the expression fits**
  (§1). Only when it does not fit does it wrap — and then with the operator at the **start** of the
  continuation line (this reads best for null-fallbacks, and matches kotlinx usage):

  ```kotlin
  val name = findName() ?: error("missing")            // fits → stays on one line

  // too long to fit → `?:` starts the continuation line, at one indent:
  val displayName = lookupPreferredDisplayName(userId, localeSettings)
      ?: error("no display name is available for the requested user")
  ```

## 7. Call chains

When a member-access call chain (`a.b().c().d()`) is too long for one line, keep the receiver
**through its first call** on the introducer's line, then put **each subsequent `.call` /
`.property` on its own line at one indent**. Do not break after `=`/`:` to start the chain, and
do not add a second indent level.

```kotlin
val dir = Path.of("")
    .absolute()
    .resolve("tests")
    .resolve("data")
```

This holds **even when keeping the receiver attached costs an extra line** — attaching the receiver
is preferred over breaking after `=` to fit the whole chain on one wrapped line:

```kotlin
// optofmt — the receiver-through-first-call stays on the `=` line, `.padding`s wrap one per line;
// NOT `val x =\n    Modifier.…().padding(…).padding(…)` on a single wrapped line.
val contentModifier = Modifier.verticalScroll(scrollState)
    .padding(bottom = 24.dp)
    .padding(bottomInsetPadding())
```

The receiver-through-first-call is treated as a **whole** unit — its own arguments never wrap to
keep it on the line. When that unit itself is too long to sit on the `=` line, only *then* does the
chain break after `=`, dropping the whole receiver-first-call to the next line at one indent (its
arguments still kept together there):

```kotlin
val queryResult =
    repository.findAllByStatusAndCategoryOrderByCreatedDate(activeStatus, selectedCategory)
    .map { it.id }
    .distinct()
```

**A sole trailing-lambda call applied directly to the receiver stays attached.** When the chain is
just a receiver followed by one trailing-lambda call (`receiver(args).collect { … }`) and the
receiver must wrap its own arguments, the receiver wraps **only its own arguments** at a single
indent and the `.call {` stays **attached to the receiver's `)`** — it is not dropped onto its own
line, and the arguments are not pushed to a second indent. The lambda body hangs one indent below:

```kotlin
// optofmt — the receiver `merge(…)` wraps its own args at one indent; `.collect {` hugs the `)`:
merge(
    flow.map { Update(it) },
    triggerFlow.receiveAsFlow().conflate(),
    advancedPropsStateFlow.map { Trigger },
).collect {
    handle(it)
}
```

This applies only when the lambda call is applied **directly** to the receiver-through-first-call.
A genuine multi-call chain (an intermediate `.call` precedes the trailing lambda) keeps the general
rule — each subsequent `.call`, including the trailing-lambda one, on its own line at one indent.

It also holds when the receiver-through-first-call's *own* first call carries a trailing lambda: a
single terminal `.call { … }` still hugs its `}` when it fits. Only a *second* trailing-lambda call
tips it into a multi-call chain (one per line). This is true whether the base receiver is a
`receiver.call { … }` or a **bare call** that is itself the first call (`flow { … }`, `buildList
{ … }`, `runCatching { … }`, an implicit-receiver `mapValues { … }`) — the tail `.call { … }` hugs
the base's `}` and the base's own body sits at a single indent, not two:

```kotlin
// optofmt — the sole `.none { … }` hugs the `}` of the base call `flow { … }`:
assertFalse(flow {
    emit(1)
    emit(2)
    expectUnreached()
}.none {
    it == 2
})

// optofmt — the sole `.filterValues { … }` hugs the `}` of `mapValues`:
val filtered = v.mapValues { (_, value) ->
    transform(value)
}.filterValues { it !is JsonNull }

// two trailing-lambda tails → genuine multi-call chain, each on its own line:
val filtered = v.mapValues { (_, value) ->
    transform(value)
}
    .filterValues { it !is JsonNull }
    .mapKeys { it.key.lowercase() }
```

**A chain the author broke across lines is author-preserving — even when it would fit.** For any
member-access chain with at least two links (`.foo().bar()`), both a one-line form and a staircase read
well. Rather than always collapse a chain that fits (§1), optofmt **preserves what the author wrote**:
if the source already broke the chain — a line break after the receiver-through-first-call, before the
first subsequent `.call` — that staircase is kept, one `.call` per line, **even if the whole chain
would fit on a single line**. A chain the author wrote on **one line** stays on one line (it collapses
if it fits). So the author toggles between the two forms by where they place the newlines; both are
idempotent (a staircased output re-reads as broken, a one-line output re-reads as collapsible).

```kotlin
// author wrote it on one line and it fits → stays on one line:
val y = obj.foo(1).bar(2).baz(3)

// author staircased it → kept staircased even though it fits:
Flowable.fromArray(1)
    .onBackpressureDrop()
    .collect {
        assertEquals(1, it)
        expect(2)
    }
```

If the author additionally broke the **receiver itself** off (a newline before the FIRST `.call`), the
receiver sits **alone** on the introducer's line with **every** `.call`, including the first, on its own
line:

```kotlin
// source kept the receiver and its first call together → receiver-through-first-call attached:
val x = someReceiverObject.firstMethodCall(argOne)
    .secondMethodCall(argTwo)
    .thirdMethodCall(argThree)

// source broke the receiver off → preserved, every `.call` on its own line:
val x = someReceiverObject
    .firstMethodCall(argOne)
    .secondMethodCall(argTwo)
    .thirdMethodCall(argThree)
```

This holds for any chain, trailing lambdas or not. It does **not** apply to a single-call chain
(`OverrideOrganizations.Override(…)` — one link): the receiver through its first call is atomic and
stays whole even if the source wrapped it (see §7's atomicity rule above).

## 8. Comments are never reflowed, and they hold their own line

Treat the text inside `//` and `/** … */` comments as opaque. optofmt owns the blank lines and
indentation *around* comments, but it never rewraps the words inside one. Hand-formatted
comment blocks, tables, and lists are preserved exactly.

A comment also **holds its line**, and that can shape the surrounding layout. An end-of-line (`//`)
comment must end its line, and a comment written on its **own line** stays on its own line — it is
never pulled up onto the previous token's line. So a comment placed before a construct that would
otherwise be kept **inline** (§1) forces that construct onto its own line. For example a trivial
accessor normally rides the property line (`val x: T get() = …`), but an own-line comment before it
keeps both the comment and the accessor on their own lines, one indent in:

```kotlin
val isClosedForSend: Boolean
    // Protect by lock to synchronize with close/cancel.
    get() = lock.withLock { super.isClosedForSend }
```

(The reverse — a comment forcing a *wrap* purely by its width — does not happen: a trailing
`// comment` that spills past column 100 does not break the code line.)

## 9. Declaration headers stay compact

Keep a declaration's **modifiers** (`internal`, `public`, `private`, `open`, `override`, …) on the
same line as the declared name; when the header is too long, wrap **only** the parameter list (§4),
not the modifier run.

Annotation placement is its own concern — see **§12**.

**Types glue to their colon.** A function's return type and an explicit property type stay attached
to the `:` that introduces them; the type is never pushed onto a line by itself. When the header is
too long, wrap the parameter list (§4) and keep the closing `): ReturnType` (and `name: Type`)
together — never break right before the `:` or right after it just to move the type down.

```kotlin
// optofmt — the return type rides with `)`, it does not get its own line:
override fun isMemberInplaceRenameAvailable(
    element: PsiElement,
    context: PsiElement?,
): Boolean {
    …
}

val subscriptionWaitingFlow: MutableStateFlow<Int> = MutableStateFlow(0)   // not: name\n    : Type
```

## 10. Empty bodies are compact

An empty block — a class/object/function body or any `{ }` with nothing inside — is written as
`{}` on the same line, never split across two lines. This holds even when the header above it
wrapped:

```kotlin
object X : Base(
    a = 1,
    b = 2,
) {}
```

## 11. Declaration grouping

Keep a run of consecutive **same-kind** one-line declarations together: never *insert* a blank
line between them, and collapse multiple blank lines to a single one — but **preserve** a single
blank line the author put there. Insert a blank line only between declarations of **different**
kinds (e.g. a property group and a following function).

```kotlin
typealias TeamId = StrongId<TeamTag>
typealias RunId = StrongId<RunTag>
typealias MessageId = StrongId<MessageTag>
```

The same grouping applies to **enum entries**: adjacent entries stay tight, but an author blank
line before an entry (for example, one separating an entry from the KDoc of the next) is
preserved.

```kotlin
enum class PenaltyRoundingMode {
    /** Round down. */
    @SerialName("down")
    EACH_SUBMISSION_DOWN_TO_MINUTE,

    /** Round up. */
    @SerialName("up")
    EACH_SUBMISSION_UP_TO_MINUTE,
}
```

## 12. Annotation placement

Where an annotation sits depends on whether it takes arguments and on what it annotates:

- An **argument-less** annotation (`@PublishedApi`, `@JvmStatic`, `@Volatile`, `@BuilderInference`)
  stays **inline** on the declaration's line when it annotates a **function or constructor value
  parameter** (including a `val`/`var` parameter-property) or a **primary constructor**
  (`@Inject constructor(…)`). For every other target — a regular (standalone) **property**, a
  **function**, a **class** / `object` / `interface`, a property **accessor** — it goes on its
  **own line** directly above the declaration.
- An annotation that **carries arguments** (`@JvmName("other")`, `@Test`, `@Deprecated(…)`,
  `@Suppress(…)`) **always** goes on its **own line** above the declaration, whatever it annotates.
- **Type annotations** are the exception: an annotation that is part of a **type** always stays
  inline and never breaks away from it. This covers a **type-parameter** annotation
  (`<@UnsafeVariance T>`) and a **type-use** annotation on a parameter/property type
  (`compactHeader: @Composable () -> Unit`, `items: @Ann List<T>`) — the annotation rides with the
  type on the `:` line (§9), it is not dropped onto its own line even when it carries arguments.

(ktfmt keeps every annotation inline; optofmt breaks as above.)

```kotlin
@JvmName("other")                                     // has arguments → own line
fun testSomething() {}

@Test                                                 // argument-less, on a function → own line
fun testOther() {}

@JvmStatic
val instance = create()                               // argument-less, on a (regular) property → own line

public class Scope<T> @PublishedApi internal constructor(   // argument-less, on the constructor → inline
    @PublishedApi internal val flow: SharedFlow<T>,         // argument-less, on a parameter-property → inline
    private val waiting: MutableStateFlow<Int>,
) { … }
```

## 13. Lambda header stays on the brace line

A lambda's opening `{`, its parameters, and its `->` all sit on **one line** and are **never split
apart from one another** — neither the parameters from `{` (`{\n    cont ->`) nor `->` from the
parameters (`{ cont\n    ->`). When that header would overflow, wrap *earlier* — break the enclosing
introducer/call per §3/§7 — never inside `{ params ->`.

```kotlin
// optofmt — `{ cont ->` stays together; the `=` breaks instead:
internal suspend fun sendBroadcast(element: E): Boolean =
    suspendCancellableCoroutine { cont ->
        …
    }
```

**Custom formatting — author-directed body expansion.** Whether a lambda body collapses onto its
header line (`{ … }`) is normally decided by fit (§1). But the author may *force* it open: **a line
break right after `->` (or after `{` when the lambda has no parameters) keeps the body on its own
line(s)**, even when it would fit. Removing that break lets the body collapse again — the mirror of
the list rule in §4.

```kotlin
run { doThing() }     // one line — collapses

run {                 // newline right after `{`/`->` → body stays on its own line
    doThing()
}
```

## 14. Trailing comma on multi-line lists

A comma-separated list that is formatted **multi-line** (one item per line, per §4) always ends
with a **trailing comma** after its final item. A list that stays on **one line** never has one.
The comma is a property of the layout, not the source: it is added when the list wraps and dropped
when it collapses, so the result is idempotent and independent of whether the input had one.

```kotlin
call(a, b, c)                  // one line → no trailing comma

call(
    firstArgument,
    secondArgument,
    thirdArgument,             // multi-line → trailing comma
)
```

This applies wherever Kotlin permits a trailing comma and the list splits one-per-line — call
arguments, function/constructor value parameters, and collection literals. It does **not** apply to
constructs where a trailing comma is illegal (a supertype list, a function-type parameter list, a
`where` clause) or to a list that never splits (a kept-whole type-argument list), nor to a
last-item-expansion / hanging trailing lambda (§4), which is not a one-per-line split.

(This matches ktfmt and idiomatic Kotlin. Earlier drafts of optofmt omitted trailing commas; this
rule supersedes that.)

## 15. If-expression branch bodies attach to their keyword

In an `if`/`else` used as a **value** (branches are expressions, not `{ }` blocks), each branch body
stays **attached to the keyword that introduces it** — `if (cond)` for the `then` value, `else` for
the `else` value — exactly as an introducer keeps its right-hand side (§3). When a branch does not
fit, its **own contents wrap** (a call's arguments per §4), rather than pushing the whole body onto
a fresh indented line and leaving a bare `if (cond)` or a bare `else`. The clauses split at the
`else` boundary: the whole thing on one line if it fits, otherwise `if (cond) then` on one line and
`else …` on the next.

```kotlin
// fits → one line:
val kind = if (isRoot) Root else Child

// must wrap → each body stays with its keyword; the `else` call keeps its opener and wraps its args:
if (cond) shortThenValue
else buildResultObject(
    firstArgumentHere,
    secondArgumentHere,
    thirdArgumentHere,
    fourthArgumentHere,
    fifthArgument,
)
```

This is the same shape a multi-way `else if` **chain** already has — each `if (c) v` clause kept
together, only the `else` boundaries wrapping:

```kotlin
val x = if (firstConditionHere) firstValue
    else if (secondConditionHere) secondValue
    else theFallbackValueThatIsQuiteLongIndeedYesVeryMuchSoReally
```

A branch that can **neither** attach (it would overflow) **nor** wrap its own contents (it is a
plain reference, not a call) is the only case that drops onto its own line, one indent below its
keyword — everything that *can* hug its keyword still does:

```kotlin
val x = if (someCondition) shortValue
    else
        aVeryLongUnwrappablePlainReferenceValueThatOverflowsColumnLimitAndHasNoArgumentsToWrapAcrossLines
```

When such an `if` is the right-hand side of an introducer (`= if (…)`), the introducer keeps the
`if` and its condition attached (§3). A branch that is itself a `{ }` block is unaffected — its
braces already carry the structure.

(ktfmt keeps the `then` value inline but breaks after `else`, leaving a bare `else` above an
extra-indented body; optofmt attaches both bodies and wraps their contents instead.)

---

## Differences from ktfmt to expect

- optofmt uses one indent level where ktfmt stacks block + continuation indents (no drift).
- optofmt keeps introducers (`=`, `:`, infix, `by`) attached; ktfmt eagerly breaks after them —
  including a named argument's `=` (`add(queue = OverrideQueue(…`), which ktfmt drops onto its own
  line.
- optofmt keeps leading args inline with an expanding final item; ktfmt explodes all args.
- optofmt never reflows comment prose; ktfmt rewraps KDoc.
- optofmt keeps grouped one-liners tight; ktfmt inserts blank lines between them.
- optofmt puts an annotation on its own line unless it is argument-less on a value parameter (§12);
  ktfmt keeps annotations inline.
- optofmt keeps a function's return type / a property's type glued to its `:` (§9); it never drops
  the type onto a line by itself.
- optofmt keeps a construct that fits on one line inline per §1 — a trivial property accessor
  (`val x: T get() = …`), a control-flow lambda (`?.let { return }`); ktfmt force-breaks both.
- optofmt keeps an `if`/`else` value's branch bodies attached to their keyword and wraps their
  contents (§15); ktfmt keeps the `then` value inline but breaks after `else`, leaving a bare `else`
  above an extra-indented body.
