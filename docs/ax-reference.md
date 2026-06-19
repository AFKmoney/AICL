# AX Sub-Language Reference

AX (AICL-Action) is a Turing-complete sub-language for `Action:` sections in
AICL Behaviors. Instead of free-form English that the compiler can only
skeleton, AX gives Behaviors a strict, compilable grammar. The compiler
translates any valid AX program to **executable code** in Python, Rust,
JavaScript, and Go.

## Design principle

AX is deliberately a subset of Python. This makes the Python translation
near-identity, and the Rust/JS/Go translations mechanical. The grammar covers
exactly what's needed for algorithms — control flow, recursion, arithmetic,
data structures — and nothing more.

## Grammar

```
action        ::= stmt+
stmt          ::= assign | if_stmt | while_stmt | for_stmt | return_stmt
              |   call_stmt | break | continue | swap
assign        ::= lvalue "=" expr
              |   lvalue aug_op expr           (+= -= *= /= //= %= **=)
if_stmt       ::= "if" expr block ("elif" expr block)* ("else" block)?
while_stmt    ::= "while" expr block
for_stmt      ::= "for" name "in" expr block
return_stmt   ::= "return" expr?
block         ::= INDENT stmt+ DEDENT
expr          ::= or_expr
or_expr       ::= and_expr ("or" and_expr)*
and_expr      ::= not_expr ("and" not_expr)*
not_expr      ::= "not" not_expr | comparison
comparison    ::= arith (comp_op arith)*
arith         ::= term (("+" | "-") term)*
term          ::= factor (("*" | "/" | "//" | "%") factor)*
factor        ::= "-" factor | power
power         ::= atom ("**" factor)?
atom          ::= literal | name | "(" expr ")" | list | call | index | attr
literal       ::= int | float | string | true | false | none
list          ::= "[" (expr ("," expr)*)? "]"
swap          ::= lvalue_list "=" expr_list   (e.g. a, b = b, a)
```

## Statements

### Assignment

```
x = 5
y = x + 1
result = []
total += count
```

### If / elif / else

```
if n < 0:
    return -n
elif n == 0:
    return 0
else:
    return n
```

### While

```
while i < len(array):
    if array[i] == target:
        return i
    i = i + 1
```

### For

```
for j in range(low, high):
    if array[j] < pivot:
        total = total + array[j]
```

`range(a, b)` iterates from `a` to `b` exclusive. `range(n)` iterates 0 to n.

### Return

```
return result
return              # bare return (returns None/null)
```

### Swap

```
array[i], array[j] = array[j], array[i]
```

This compiles to native swap in Python/JS, and temp-variable swap in Rust/Go
(correct for indexed locations — both sides captured before any mutation).

## Expressions

### Arithmetic

| Operator | Meaning | Python | Rust | JS | Go |
|----------|---------|--------|------|----|----|
| `+` `-` `*` | Standard | `+` | `+` | `+` | `+` |
| `/` | Division | `/` | `/` | `/` | `/` |
| `//` | Floor division | `//` | `/` (int) | `Math.trunc(a/b)` | `/` (int) |
| `%` | Modulo | `%` | `%` | `%` | `%` |
| `**` | Power | `**` | `i64::pow` | `Math.pow` | `int(math.Pow)` |

### Comparisons

`==`, `!=`, `<`, `<=`, `>`, `>=` — map 1:1 to all targets.

### Boolean logic

`and`, `or`, `not` → `&&`, `||`, `!` in JS/Rust/Go; native in Python.

### Builtins

| Builtin | Effect |
|---------|--------|
| `len(x)` | Length of array/string |
| `abs(x)` | Absolute value |
| `max(a, b)` / `min(a, b)` | Maximum / minimum |
| `range(a, b)` | Iterator from a to b |

### Method calls

```
result.append(x)       # append to list
result.pop()           # remove last element
```

Method calls compile to native list operations in each target.

## Type inference

AX is dynamically typed, but the Rust and Go targets need static types. The
compiler infers types from usage:

- A name **indexed** (`x[i]`) or passed to `len()` → array
- A name in **arithmetic** → integer
- Otherwise → default (int for numeric, array for collections)

This is conservative — it only types what it can prove. See
`python/src/aicl/ax/typeinfer.py`.

## Complete example: quicksort

```aicl
Goal:
Sort an array of integers in ascending order

Constraint:
Use the Lomuto partition scheme

Risk:
Empty input array

Recovery:
Return an empty array

Layer:
Partition

Validation:
Output array is sorted

Behavior Partition
    Input: array, low, high
    Output: pivot_index
    Action:
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] < pivot:
                i = i + 1
                array[i], array[j] = array[j], array[i]
        array[i + 1], array[high] = array[high], array[i + 1]
        return i + 1
```

This compiles to real, executable code in all four targets. The Rust version
compiles with `rustc` and sorts correctly. The JavaScript version runs in Node.
The Go version builds and executes.

## What AX does NOT cover

- Classes / objects (AX is procedural)
- String manipulation beyond comparison and `len()`
- I/O (files, sockets, graphics) — use `Native:` sections for that
- Exception handling (use Risk/Recovery instead — that's the point of AICL)

For anything AX can't express, the behavior falls back to a structural skeleton
(with a warning during `aicl verify`). You can also use `Native:` sections to
embed raw target-language code.
