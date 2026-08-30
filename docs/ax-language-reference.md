# AX Language Reference

> **AX** (AICL-Action) is the Turing-complete sub-language used inside
> `Action:` sections of AICL Behaviors. It is a strict, compilable grammar
> that produces **real executable code** in Python, Rust, JavaScript, and Go —
> no stubs, no `pass`-empty bodies.

This is the complete reference. For a tutorial, see
[How to Code in AICL](./how-to-code-in-aicl.md).

---

## Table of Contents

1. [Lexical Structure](#1-lexical-structure)
2. [Grammar (BNF)](#2-grammar-bnf)
3. [Statements](#3-statements)
4. [Expressions](#4-expressions)
5. [Operators](#5-operators)
6. [Literals](#6-literals)
7. [Data Structures](#7-data-structures)
8. [Indexing and Slicing](#8-indexing-and-slicing)
9. [Method Calls](#9-method-calls)
10. [Function Calls (Builtins)](#10-function-calls-builtins)
11. [Keywords](#11-keywords)
12. [Type Inference](#12-type-inference)
13. [Cross-Target Translation](#13-cross-target-translation)

---

## 1. Lexical Structure

### Character set

AX source is UTF-8. Identifiers may contain letters, digits, and underscores;
they must start with a letter or underscore.

### Indentation

AX is **indentation-sensitive** (like Python). Use 4 spaces per level. Tabs
are rejected.

```
if x > 0:
    do_thing()        # indented 4 spaces — body of the if
do_next()             # not indented — after the if
```

### Comments

Lines starting with `#` (after optional whitespace) are comments and ignored.

```
# This is a comment
x = 5  # trailing comment
```

### Blank lines

Blank lines inside `Action:` blocks are ignored.

### Multi-line expressions

Newlines inside `(...)`, `[...]`, or `{...}` are ignored, so you can write:

```
result = some_function(
    arg1,
    arg2,
    arg3
)
```

---

## 2. Grammar (BNF)

```
action        ::= stmt+

stmt          ::= simple_stmt | compound_stmt
simple_stmt   ::= assign | aug_assign | swap | return_stmt | break
              |   continue | pass | expr_stmt
compound_stmt ::= if_stmt | while_stmt | for_stmt

assign        ::= target "=" expr NEWLINE
aug_assign    ::= target aug_op expr NEWLINE
swap          ::= target_list "=" expr_list NEWLINE
return_stmt   ::= "return" expr? NEWLINE
expr_stmt     ::= expr NEWLINE

if_stmt       ::= "if" expr ":" block ("elif" expr ":" block)* ("else" ":")? block?
while_stmt    ::= "while" expr ":" block
for_stmt      ::= "for" NAME "in" expr ":" block
block         ::= NEWLINE INDENT stmt+ DEDENT

expr          ::= or_expr
or_expr       ::= and_expr ("or" and_expr)*
and_expr      ::= not_expr ("and" not_expr)*
not_expr      ::= "not" not_expr | comparison
comparison    ::= arith (comp_op arith)*
arith         ::= term (("+" | "-") term)*
term          ::= factor (("*" | "/" | "//" | "%") factor)*
factor        ::= "-" factor | power
power         ::= postfix ("**" factor)?
postfix       ::= atom suffix*
suffix        ::= "[" slice_or_index "]" | "." NAME | "(" args? ")"
atom          ::= literal | NAME | "(" expr ")" | list_lit | dict_lit | set_lit

literal       ::= INT | FLOAT | STRING | "true" | "false" | "none"
list_lit      ::= "[" (expr ("," expr)*)? "]"
dict_lit      ::= "{" (pair ("," pair)*)? "}"
set_lit       ::= "{" (expr ("," expr)*)? "}"      # no colons
pair          ::= expr ":" expr
slice_or_index::= expr? ":" expr? (":" expr?)?     # slice
              |   expr                              # index

comp_op       ::= "==" | "!=" | "<" | "<=" | ">" | ">="
              |   "in" | "not" "in" | "is" | "is" "not"
aug_op        ::= "+=" | "-=" | "*=" | "/=" | "//=" | "%=" | "**="

target        ::= NAME | postfix "[" expr "]" | postfix "." NAME
target_list   ::= target ("," target)*
args          ::= expr ("," expr)*
```

---

## 3. Statements

### Assignment

```
x = 5
name = "alice"
nums = [1, 2, 3]
d = {"key": "value"}
d["new_key"] = "new_value"          # index assignment
obj.field = 42                      # attribute assignment
```

### Augmented assignment

```
x += 1        # add and assign
x -= 2        # subtract and assign
x *= 3        # multiply and assign
x /= 2        # divide and assign
x //= 3       # floor-divide and assign
x %= 10       # modulo and assign
x **= 2       # exponentiate and assign
```

### Tuple swap

```
a, b = b, a                      # classic swap
arr[i], arr[j] = arr[j], arr[i]  # indexed swap (correct in all targets)
x, y, z = z, x, y                # three-way rotation
```

The swap captures all right-hand values into temporaries **before** any
assignment, so indexed swaps (like `arr[i], arr[j] = arr[j], arr[i]`) are
correct even in Rust and Go where naive in-place swapping would be wrong.

### Return

```
return                          # bare return (None)
return x                        # return a value
return a + b                    # return an expression
```

### Break / Continue / Pass

```
while true:
    if done:
        break
    if skipped:
        continue
    pass                        # no-op (useful for empty bodies)
```

### Expression statement

A bare expression as a statement — typically a function or method call.

```
print("hello")
list.append(x)
result = compute(x)
```

---

## 4. Expressions

### Operator precedence (lowest to highest)

| Precedence | Operator | Description |
|------------|----------|-------------|
| 1 (lowest) | `or` | Logical or |
| 2 | `and` | Logical and |
| 3 | `not` | Logical not (unary) |
| 4 | `in`, `not in`, `is`, `is not`, `==`, `!=`, `<`, `<=`, `>`, `>=` | Comparison / membership |
| 5 | `+`, `-` | Addition, subtraction |
| 6 | `*`, `/`, `//`, `%` | Multiplication, division, floor div, modulo |
| 7 | unary `-` | Negation |
| 8 | `**` | Exponent (right-assoc) |
| 9 (highest) | `[...]`, `.`, `(...)` | Postfix (index, attr, call) |

### Parenthesized expressions

```
result = (a + b) * c
ok = (x > 0) and (y > 0)
```

---

## 5. Operators

### Arithmetic

| Op | Meaning | Python | JS | Rust | Go |
|----|---------|--------|----|----|----|
| `+` | Addition | `+` | `+` | `+` | `+` |
| `-` | Subtraction | `-` | `-` | `-` | `-` |
| `*` | Multiplication | `*` | `*` | `*` | `*` |
| `/` | True division | `/` | `/` | `/` | `/` |
| `//` | Floor division | `//` | `Math.trunc(a/b)` | `/` (i64) | `/` |
| `%` | Modulo | `%` | `%` | `%` | `%` |
| `**` | Exponent | `**` | `Math.pow` | `i64::pow` | `math.Pow` |

### Comparison

| Op | Meaning |
|----|---------|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |

### Membership

| Op | Meaning | Example |
|----|---------|---------|
| `in` | Contained in | `if x in collection:` |
| `not in` | Not contained in | `if x not in collection:` |

**Target mapping:**

- Python: `in` / `not in` (native)
- JS: `collection.includes(x)` / `!collection.includes(x)`
- Rust: `collection.contains(&x)` / `!collection.contains(&x)`
- Go: `_axContains(collection, x)` / `!_axContains(...)`

### Identity

| Op | Meaning | Example |
|----|---------|---------|
| `is` | Identity (same object) | `if x is none:` |
| `is not` | Not identical | `if x is not none:` |

**Target mapping:**

- Python: `is` / `is not` (native)
- JS: `===` / `!==`
- Rust: `==` / `!=`
- Go: `==` / `!=`

### Logical

| Op | Meaning | Python | JS | Rust | Go |
|----|---------|--------|----|----|----|
| `and` | Logical and | `and` | `&&` | `&&` | `&&` |
| `or` | Logical or | `or` | `\|\|` | `\|\|` | `\|\|` |
| `not` | Logical not (unary) | `not` | `!` | `!` | `!` |

### Truthiness

The following are falsy: `false`, `none`, `0`, `""`, `[]`, `{}`. Everything
else is truthy.

---

## 6. Literals

### Integer

```
42
0
-17
1000000
```

> Integers are `i64` in Rust, `int` in Go, regular numbers in Python/JS.

### Float

```
3.14
-0.5
2.0
```

> Floats are `f64` in Rust, `float64` in Go.

### String

```
"hello, world"
'hello, world'
"with \"escaped\" quotes"
"backslash: \\"
```

Both single and double quotes are accepted. Escape sequences: `\\`, `\"`, `\'`,
`\n`, `\t`.

### Boolean

```
true
false
```

> Map to `True`/`False` in Python, `true`/`false` in JS/Rust/Go.

### None

```
none
```

> Maps to `None` in Python, `null` in JS, `None::<i64>` in Rust, `0` in Go
> (Go has no generic nil for integers).

---

## 7. Data Structures

### List literal

```
[]
[1, 2, 3]
["a", "b", "c"]
[1, "mixed", true, none]
[nested, [2, 3], x + 1]
```

**Target mapping:**

- Python: `[1, 2, 3]`
- JS: `[1, 2, 3]`
- Rust: `vec![1i64, 2i64, 3i64]`
- Go: `[]interface{}{1, 2, 3}`

### Dict literal

```
{}
{"key": "value"}
{"alice": 30, "bob": 25}
{1: "one", 2: "two"}
{name: age}              # variables as keys
```

**Target mapping:**

- Python: `{"key": "value"}`
- JS: `Object.fromEntries([["key", "value"]])` (plain object, supports `[]` indexing)
- Rust: `_ax_dict!(("key", "value"))` (HashMap macro)
- Go: `map[string]interface{}{"key": "value"}`

### Set literal

```
{1, 2, 3}
{"a", "b", "c"}
```

> An empty `{}` is a dict, not a set. Use explicit construction for empty
> sets in Python (`set()`); in other targets this is handled automatically.

**Target mapping:**

- Python: `{1, 2, 3}`
- JS: `new Set([1, 2, 3])`
- Rust: `_ax_set!(1, 2, 3)`
- Go: `map[interface{}]struct{}{1: struct{}{}, ...}`

---

## 8. Indexing and Slicing

### Index

```
first = arr[0]
last = arr[len(arr) - 1]
value = d["key"]
char = s[3]
```

**Target mapping for index:**

- Python: `arr[0]`
- JS: `arr[0]`
- Rust: `arr[0 as usize]` (i64 → usize cast)
- Go: `arr[0]`

### Slice

```
first_three = arr[:3]           # 0, 1, 2
middle = arr[2:5]               # 2, 3, 4
end = arr[3:]                   # 3 to end
every_other = arr[::2]          # 0, 2, 4, ...
countdown = arr[::-1]           # reversed (Python only)
custom = arr[1:10:3]            # 1, 4, 7
```

**Slice syntax:**

```
arr[start:stop]         # indices start..stop-1
arr[:stop]              # 0..stop-1
arr[start:]             # start..end
arr[::step]             # every step-th element
arr[start:stop:step]
```

**Target mapping for slice:**

- Python: `arr[1:3]` (native)
- JS: `arr.slice(1, 3)` (step uses `.filter()`)
- Rust: `arr[1..3].to_vec()` (step uses iterators)
- Go: `arr[1:3]` (step uses helper)

---

## 9. Method Calls

Method calls have the form `target.method(args)`.

### String methods

| Method | Effect | Python | JS | Rust | Go |
|--------|--------|--------|----|----|----|
| `.upper()` | Uppercase | `.upper()` | `.toUpperCase()` | `.to_uppercase()` | `strings.ToUpper` |
| `.lower()` | Lowercase | `.lower()` | `.toLowerCase()` | `.to_lowercase()` | `strings.ToLower` |
| `.strip()` | Trim whitespace | `.strip()` | `.trim()` | `.trim()` | `strings.TrimSpace` |
| `.lstrip()` | Left trim | `.lstrip()` | regex | n/a | n/a |
| `.rstrip()` | Right trim | `.rstrip()` | regex | n/a | n/a |
| `.split(sep)` | Split | `.split(sep)` | `.split(sep)` | `.split(sep)` | `strings.Split` |
| `.split()` | Split on whitespace | `.split()` | `.split(/\s+/)` | `.split_whitespace()` | `strings.Fields` |
| `.join(iter)` | Join | `sep.join(iter)` | `iter.join(sep)` | n/a | `strings.Join` |
| `.replace(old, new)` | Replace | `.replace()` | `.split().join()` | `.replace()` | `strings.ReplaceAll` |
| `.find(sub)` | Find index | `.find()` | `.indexOf()` | `.find()` | `strings.Index` |
| `.startswith(s)` | Prefix test | `.startswith()` | `.startsWith()` | `.starts_with()` | `strings.HasPrefix` |
| `.endswith(s)` | Suffix test | `.endswith()` | `.endsWith()` | `.ends_with()` | `strings.HasSuffix` |
| `.count(sub)` | Count occurrences | `.count()` | `.split().length-1` | n/a | n/a |
| `.contains(sub)` | Contains test | `in` | `.includes()` | `.contains()` | `strings.Contains` |
| `.format(...)` | Format | `.format()` | regex replace | `format!` | `Sprintf` |

> Note: in AX, `.join()` is called on the separator, not the iterable
> (Python convention). Example: `", ".join(parts)`.

### List methods

| Method | Effect | Python | JS | Rust | Go |
|--------|--------|--------|----|----|----|
| `.append(x)` | Add to end | `.append()` | `.push()` | `.push()` | `append()` |
| `.pop()` | Remove last | `.pop()` | `.pop()` | `.pop().unwrap()` | helper |
| `.insert(i, x)` | Insert at index | `.insert()` | `.splice()` | `.insert()` | helper |
| `.remove(x)` | Remove first x | `.remove()` | splice+indexOf | `.remove()` | helper |
| `.sort()` | Sort in place | `.sort()` | `.sort((a,b)=>a-b)` | `.sort()` | `sort.Ints` |
| `.reverse()` | Reverse in place | `.reverse()` | `.reverse()` | `.reverse()` | helper |
| `.extend(other)` | Append all | `.extend()` | `.push(...)` | `.extend()` | helper |

### Dict methods

| Method | Effect | Python | JS | Rust | Go |
|--------|--------|--------|----|----|----|
| `.get(key)` | Get or None | `.get()` | `obj[key]` | `.get()` | helper |
| `.get(key, default)` | Get with default | `.get()` | ternary | `.unwrap_or()` | helper |
| `.keys()` | All keys | `.keys()` | `Object.keys()` | `.keys()` | helper |
| `.values()` | All values | `.values()` | `Object.values()` | `.values()` | helper |
| `.items()` | (key, value) pairs | `.items()` | `Object.entries()` | `.iter()` | helper |

---

## 10. Function Calls (Builtins)

AX provides 40+ builtin functions. See
[stdlib-reference.md](./stdlib-reference.md) for the complete list with
target mappings. Highlights:

```
print(x, y, z)               # console output
len(s)                       # length of string/list/dict
sum([1, 2, 3])               # 6
sorted([3, 1, 2])            # [1, 2, 3]
reversed(nums)               # reversed copy
abs(-5)                      # 5
max(3, 7)                    # 7
min(3, 7)                    # 3
int("42")                    # 42
str(42)                      # "42"
float("3.14")                # 3.14
bool(0)                      # false
ord("A")                     # 65
chr(65)                      # "A"
sqrt(16)                     # 4.0
pow(2, 10)                   # 1024
floor(3.7)                   # 3
ceil(3.2)                    # 4
range(10)                    # 0..9
range(2, 11)                 # 2..10
range(0, 20, 2)              # 0, 2, 4, ..., 18
read_file(path)              # read file to string
write_file(path, content)    # write string to file
input(prompt)                # read from stdin
```

---

## 11. Keywords

AX has 16 reserved keywords. They cannot be used as identifiers.

| Keyword | Context |
|---------|---------|
| `if` | Conditional |
| `elif` | Else-if branch |
| `else` | Else branch |
| `while` | Conditional loop |
| `for` | Iterator loop |
| `in` | Membership / for-in |
| `return` | Return from Behavior |
| `break` | Exit loop |
| `continue` | Skip iteration |
| `pass` | No-op |
| `and` | Logical and |
| `or` | Logical or |
| `not` | Logical not |
| `true` | Boolean true |
| `false` | Boolean false |
| `none` | Null/None |

---

## 12. Type Inference

AX is dynamically typed, but the Rust and Go targets are statically typed.
The compiler infers types for Behavior parameters:

- A name indexed with `[]` or called with `.append()` → **ARRAY**
- A name used in arithmetic / augmented assignment → **INT**
- Otherwise → **ANY** (emitter picks a default)

Example:

```aicl
Behavior Partition
    Input: array, low, high      # array → ARRAY, low/high → INT
    ...
        for j in range(low, high):  # j → INT (from range)
            if array[j] < pivot:
                ...
```

You usually don't need to think about this — the compiler does it for you.

---

## 13. Cross-Target Translation

The same AX source compiles to four targets. Here's how the major constructs
translate:

### Variables

| AX | Python | JS | Rust | Go |
|----|--------|----|----|----|
| `x = 5` (first) | `x = 5` | `let x = 5;` | `let mut x = 5i64;` | `x := 5` |
| `x = 5` (reassign) | `x = 5` | `x = 5;` | `x = 5;` | `x = 5` |

### Control flow

| AX | Python | JS | Rust | Go |
|----|--------|----|----|----|
| `if x:` | `if x:` | `if (x) {` | `if x {` | `if x {` |
| `elif x:` | `elif x:` | `} else if (x) {` | `} else if x {` | `} else if x {` |
| `else:` | `else:` | `} else {` | `} else {` | `} else {` |
| `while x:` | `while x:` | `while (x) {` | `while x {` | `for x {` |
| `for i in range(n):` | `for i in range(n):` | `for (let i=0; i<n; i++) {` | `for i in 0..n {` | `for i:=0; i<n; i++ {` |
| `for x in coll:` | `for x in coll:` | `for (let x of coll) {` | `for x in coll {` | `for _, x := range coll {` |

### Booleans / None

| AX | Python | JS | Rust | Go |
|----|--------|----|----|----|
| `true` | `True` | `true` | `true` | `true` |
| `false` | `False` | `false` | `false` | `false` |
| `none` | `None` | `null` | `None::<i64>` | `0` |

### Swap

AX: `a, b = b, a`

- Python: `a, b = b, a` (native)
- JS: `[a, b] = [b, a]` (destructuring)
- Rust: capture into temps, then assign (verbose but correct)
- Go: native for simple names; temps for indexed swaps

### Floor division

AX: `a // b`

- Python: `a // b`
- JS: `Math.trunc(a / b)`
- Rust: `a / b` (i64 truncates toward zero)
- Go: `a / b` (int division truncates)

### Power

AX: `a ** b`

- Python: `a ** b`
- JS: `Math.pow(a, b)`
- Rust: `i64::pow(a, b as u32)`
- Go: `int(math.Pow(float64(a), float64(b)))`

---

## See also

- [How to Code in AICL](./how-to-code-in-aicl.md) — practical tutorial
- [Standard Library Reference](./stdlib-reference.md) — every builtin
- [AICL Cookbook](./cookbook.md) — ready-to-run recipes
- [Compile Targets](./targets.md) — backend details
- [Formal Grammar](../python/spec/grammar.md) — full BNF
