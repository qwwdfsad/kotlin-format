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

```kotlin
// optofmt
val teams = when (val e = state.lastEvent) { … }          // not: val teams =\n    when (…) {
object X : DumpFileCommand(name = "a", help = "b") { … }   // not: object X :\n    DumpFileCommand(
val pair = key to Override(fullName = a, displayName = b)  // not: key to\n    Override(
```

When the right-hand side is itself too long, keep the introducer + opener on the first line
and wrap the *contents* (see §4/§5), still at a single indent.

## 4. Lists are compact or fully split

A comma-separated list (call arguments, parameters, collection literals, `when` entries with
commas) is either **all on one line** or **one item per line** — never a "fill" that packs
several per line. Do not add a trailing comma after the final item.

```kotlin
call(a, b, c)                  // fits → one line

call(
    firstArgument,
    secondArgument,
    thirdArgument              // no trailing comma
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

## 5. Indent economy — collapse openers, stack closers

When delimiter groups nest and must split, let the opening delimiters **share one line** and
let the closing delimiters **stack together**, so the nested groups share a single body
indent instead of staircasing.

```kotlin
// optofmt
add(OverrideQueue(
    waitTime,
    firstToSolveWaitTime,
    maxQueueSize
))
```

Legality: the opening line ends with the opener(s); the closing line begins with all the
matching closers (then any trailing `{`, `,`, etc.). Use this whenever an outer call's only
argument is a call/constructor that itself has to wrap.

## 6. Operator wrapping

- **Chained operators** — `&&`, `||`, `+`, `*`, and the like — wrap with the operator at the
  **end** of the line, every operand at a single shared indent (§2). Keep the first operand on
  the introducer's line when it fits.
- **Elvis `?:`** wraps with the operator at the **start** of the continuation line (this reads
  best for null-fallbacks, and matches kotlinx usage):

  ```kotlin
  val name = findName()
      ?: error("missing")
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

## 8. Comments are never reflowed

Treat the text inside `//` and `/** … */` comments as opaque. optofmt owns the blank lines and
indentation *around* comments, but it never rewraps the words inside one. Hand-formatted
comment blocks, tables, and lists are preserved exactly.

## 9. Declaration headers stay compact

Keep a declaration's **modifiers** and **argument-less annotations** (`internal`, `public`,
`@PublishedApi`, `@JvmStatic`) on the same line as the declared name; when the header is too
long, wrap **only** the parameter list (§4), not the modifier run.

A standalone **annotation that carries arguments** (`@JvmName("other")`, `@Test`,
`@Deprecated(...)`) goes on its **own line** directly above the declaration — matching Kotlin
convention. ktfmt keeps it inline; optofmt breaks after it.

```kotlin
@JvmName("other")
fun testSomething() {}
```

```kotlin
public class Scope<T> @PublishedApi internal constructor(
    @PublishedApi internal val flow: SharedFlow<T>,
    private val waiting: MutableStateFlow<Int>
) { … }
```

## 10. Empty bodies are compact

An empty block — a class/object/function body or any `{ }` with nothing inside — is written as
`{}` on the same line, never split across two lines. This holds even when the header above it
wrapped:

```kotlin
object X : Base(
    a = 1,
    b = 2
) {}
```

## 11. Declaration grouping

Keep a run of consecutive **same-kind** one-line declarations together with no blank lines
between them. Collapse multiple blank lines to a single one. Insert a blank line only between
declarations of **different** kinds (e.g. a property group and a following function).

```kotlin
typealias TeamId = StrongId<TeamTag>
typealias RunId = StrongId<RunTag>
typealias MessageId = StrongId<MessageTag>
```

---

## Differences from ktfmt to expect

- optofmt uses one indent level where ktfmt stacks block + continuation indents (no drift).
- optofmt keeps introducers (`=`, `:`, infix) attached; ktfmt eagerly breaks after them.
- optofmt collapses nested openers (indent economy); ktfmt staircases.
- optofmt keeps leading args inline with an expanding final item; ktfmt explodes all args.
- optofmt does not add trailing commas; ktfmt does.
- optofmt never reflows comment prose; ktfmt rewraps KDoc.
- optofmt keeps grouped one-liners tight; ktfmt inserts blank lines between them.
- optofmt puts a standalone annotation-with-arguments on its own line; ktfmt keeps it inline.
- optofmt keeps a construct that fits on one line inline per §1 — a trivial property accessor
  (`val x: T get() = …`), a control-flow lambda (`?.let { return }`); ktfmt force-breaks both.
