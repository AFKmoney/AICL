# How to Code in AICL — A Practical Guide

> **AICL** (Artificial Intelligence-Centered Language) is a specification-first
> programming language. You write **architecture** (goals, risks, recoveries,
> validations, behaviors); the compiler writes **code** (Python, Rust, JS, Go);
> a cryptographic Proof of Origin explains **why**.

This guide teaches you to write real, useful programs in AICL — from your first
"Hello World" to a full data-processing pipeline. Every example here compiles
to executable code in all four targets.

---

## Table of Contents

1. [Mental Model](#1-mental-model)
2. [Your First Program](#2-your-first-program)
3. [The AICL Skeleton](#3-the-aicl-skeleton)
4. [Writing Behaviors with AX](#4-writing-behaviors-with-ax)
5. [Data Structures](#5-data-structures)
6. [Strings and Text](#6-strings-and-text)
7. [Control Flow](#7-control-flow)
8. [The Standard Library](#8-the-standard-library)
9. [Input / Output](#9-input--output)
10. [Functions and Recursion](#10-functions-and-recursion)
11. [Slicing](#11-slicing)
12. [Risk and Recovery](#12-risk-and-recovery)
13. [Entities (Typed Data)](#13-entities-typed-data)
14. [Events and Conditions](#14-events-and-conditions)
15. [Compile Targets](#15-compile-targets)
16. [Workflows](#16-workflows)
17. [Common Patterns (Cookbook)](#17-common-patterns-cookbook)
18. [Debugging](#18-debugging)
19. [Cheat Sheet](#19-cheat-sheet)

---

## 1. Mental Model

Stop thinking "how do I make the computer do X". Start thinking
"what is the architecture of the thing I'm building".

In AICL you declare:

- **Goal** — what success looks like
- **Layer** — the architectural components
- **Validation** — how you know it worked
- **Risk** + **Recovery** — what can fail and what to do about it
- **Behavior** — the operations, with real logic in `Action:` blocks

The compiler then generates a complete, runnable application — with tests,
error handling, and a cryptographic audit trail.

```aicl
Goal:
Sort a list of numbers

Layer:
Sorter

Validation:
The output is sorted
```

That's a valid AICL program. It compiles. It runs. But it's a skeleton — to
make it do real work, you add Behaviors with AX code (see section 4).

---

## 2. Your First Program

The minimal valid AICL program needs three things: a Goal, a Layer, and a
Validation.

```aicl
Goal:
Say hello to the world

Layer:
Greeter

Validation:
A greeting is produced
```

Compile it:

```bash
aicl compile hello.aicl
```

The compiler produces:

- `output/main.py` — the application
- `output/test_main.py` — generated tests
- `output/main.aicl-proof` — cryptographic Proof of Origin
- `output/architecture_tree.txt` — visual tree

**To make the program actually do something**, add a Behavior:

```aicl
Goal:
Say hello to the world

Layer:
Greeter

Validation:
A greeting is produced

Behavior Greet
    Input: name
    Output: message
    Action:
        message = "Hello, " + name + "!"
        return message
```

Now the generated `main.py` contains a real `Greet` method you can call.

---

## 3. The AICL Skeleton

Every AICL file follows this skeleton. Mandatory sections are marked **(required)**.

```aicl
# Comments start with #

Goal:                        # (required) what the program is for
<one-line objective>

Constraint:                 # (optional) limitations
<text>

Risk:                       # (optional, but recommended) what can fail
<text>

Recovery:                   # (paired with Risk) what to do about it
<text>

Layer:                      # (required) architectural component
<name>
    Sublayer:               # (optional) sub-components
    <name>

Validation:                 # (required) success criterion
<text>

Entity <Name>               # (optional) typed data structure
    <field>: <type>
    <field>: <type>

Behavior <Name>             # (optional) an operation
    Input: <params>
    Output: <return>
    Action:
        <AX code — real logic>

Condition:                  # (optional) reactive rule
    When <text>
    Then <text>

Event:                      # (optional) event handler
    On <text>
    Action: <text>

Parallel:                   # (optional) concurrent layers
    <layer1>
    <layer2>

Optimize:                   # (optional) perf target
<text>

Security:                   # (optional) security directives
    Encrypt: <text>
    Protect: <text>
```

### Rules

- A program without a `Goal` **does not compile**.
- A program without a `Layer` **does not compile**.
- A program without a `Validation` **does not compile**.
- Every `Risk` must have a paired `Recovery`.
- Keywords are **case-sensitive** — `Goal`, not `goal`.

---

## 4. Writing Behaviors with AX

AX (AICL-Action) is the sub-language you write inside `Action:` blocks. It's
a strict, compilable grammar — not English prose. AX is Turing-complete and
compiles to **real executable code** in all four targets.

### Behavior anatomy

```aicl
Behavior <Name>
    Input: <comma-separated parameter names>
    Output: <description>
    Action:
        <AX code — one statement per line, indented 4 spaces>
```

### Example: a real algorithm

```aicl
Behavior Factorial
    Input: n
    Output: result
    Action:
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result = result * i
        return result
```

This compiles to working code in Python, JavaScript, Rust, and Go. The
generated `factorial(5)` returns `120`.

### AX at a glance

| Construct | Example |
|-----------|---------|
| Assignment | `x = 5` |
| Augmented assign | `x += 1`, `x -= 2`, `x *= 3` |
| If / elif / else | `if x > 0: ... elif x == 0: ... else: ...` |
| While loop | `while x > 0: ...` |
| For loop | `for i in range(10): ...` |
| For-in loop | `for item in collection: ...` |
| Return | `return x`, `return` |
| Break / Continue | `break`, `continue` |
| Swap | `a, b = b, a` |
| Function call | `print(x)`, `len(s)` |
| Method call | `text.upper()`, `list.append(x)` |
| Index | `arr[i]`, `d["key"]` |
| Slice | `arr[1:3]`, `s[:5]`, `arr[::2]` |

---

## 5. Data Structures

### Lists

```aicl
Behavior ListDemo
    Input: n
    Output: result
    Action:
        nums = [1, 2, 3, 4, 5]
        nums.append(6)
        first = nums[0]
        last = nums[len(nums) - 1]
        middle = nums[1:4]
        return nums
```

**List methods:** `append(x)`, `pop()`, `insert(i, x)`, `remove(x)`,
`sort()`, `reverse()`, `extend(other)`.

### Dictionaries

```aicl
Behavior DictDemo
    Input: key
    Output: value
    Action:
        scores = {"alice": 90, "bob": 85}
        scores["carol"] = 78
        if key in scores:
            return scores[key]
        else:
            return 0
```

**Dict methods:** `get(key)`, `get(key, default)`, `keys()`, `values()`,
`items()`.

### Sets

```aicl
Behavior SetDemo
    Input: items
    Output: unique
    Action:
        seen = {1, 2, 3}
        for x in items:
            seen.add(x)
        return len(seen)
```

---

## 6. Strings and Text

AX has a full string toolkit. All of these compile to native string operations
in every target.

### String methods

```aicl
Behavior StringOps
    Input: text
    Output: result
    Action:
        upper = text.upper()
        lower = text.lower()
        trimmed = text.strip()
        parts = text.split(",")
        joined = ", ".join(parts)
        replaced = text.replace("old", "new")
        pos = text.find("needle")
        yes = text.startswith("Hello")
        no = text.endswith("world")
        count = text.count("a")
        return upper + lower
```

| Method | Effect |
|--------|--------|
| `.upper()` / `.lower()` | Case conversion |
| `.strip()` / `.lstrip()` / `.rstrip()` | Trim whitespace |
| `.split(sep)` / `.split()` | Split into list |
| `.join(iterable)` | Concatenate with separator |
| `.replace(old, new)` | Substring replacement |
| `.find(sub)` | Index of substring (-1 if absent) |
| `.startswith(s)` / `.endswith(s)` | Prefix/suffix test |
| `.count(sub)` | Substring count |
| `.format(...)` | Simple `{0}`/`{1}` formatting |

### String concatenation

```aicl
greeting = "Hello, " + name + "!"
multiline = line1 + chr(10) + line2
```

### Character codes

```aicl
code = ord("A")        # 65
char = chr(65)          # "A"
```

---

## 7. Control Flow

### If / elif / else

```aicl
if x > 100:
    category = "big"
elif x > 10:
    category = "medium"
else:
    category = "small"
```

### While loop

```aicl
while n > 0:
    n = n - 1
    if n == 5:
        break
    if n % 2 == 0:
        continue
```

### For loop with range

```aicl
for i in range(10):         # 0..9
    print(i)

for i in range(2, 11):      # 2..10
    print(i)

for i in range(0, 20, 2):   # 0, 2, 4, ..., 18
    print(i)

for i in range(n, 0, -1):   # countdown
    print(i)
```

### For-in loop

```aicl
for item in collection:
    print(item)

for key in dictionary:
    print(key, dictionary[key])

for word in text.split():
    print(word)
```

### Membership tests

```aicl
if item in collection:        # present
    ...

if item not in collection:    # absent
    ...

if x is none:                 # identity (Python None / JS null)
    ...

if x is not none:
    ...
```

---

## 8. The Standard Library

AX ships with 40+ built-in functions. They translate to native equivalents in
every target.

### Console I/O

```aicl
print("Hello, world!")
print("Sum:", x + y)
```

### Type conversion

```aicl
n = int("42")          # string -> int
s = str(42)            # int -> string
f = float("3.14")      # string -> float
b = bool(1)            # -> true
```

### Collections

```aicl
n = len(collection)            # length of anything
total = sum([1, 2, 3, 4, 5])   # 15
ordered = sorted([3, 1, 4, 1]) # [1, 1, 3, 4]
rev = reversed(nums)           # reversed copy
pairs = enumerate(items)       # [(0, a), (1, b), ...]
zipped = zip(a, b)             # [(a0, b0), (a1, b1)]
```

### Math

```aicl
x = abs(-5)            # 5
m = max(3, 7, 2)       # 7
m = min(3, 7, 2)       # 3
r = pow(2, 10)         # 1024
s = sqrt(16)           # 4.0
f = floor(3.7)         # 3
c = ceil(3.2)          # 4
```

### Full builtin reference

| Function | Effect | Python | JS | Rust | Go |
|----------|--------|--------|----|----|----|
| `print(...)` | Console output | `print` | `console.log` | `println!` | `fmt.Println` |
| `read_file(path)` | Read file to string | `open().read()` | `fs.readFileSync` | `fs::read_to_string` | `os.ReadFile` |
| `write_file(path, data)` | Write string to file | `open().write()` | `fs.writeFileSync` | `fs::write` | `os.WriteFile` |
| `int(x)` | Convert to int | `int()` | `parseInt` | `as i64` | helper |
| `str(x)` | Convert to string | `str()` | `String()` | `format!` | `Sprintf` |
| `float(x)` | Convert to float | `float()` | `parseFloat` | `as f64` | `float64` |
| `bool(x)` | Convert to bool | `bool()` | `Boolean()` | `!= 0` | `!= 0` |
| `len(x)` | Length | `len()` | `.length` | `.len()` | `len()` |
| `sum(list)` | Sum of items | `sum()` | `.reduce` | `.iter().sum` | helper |
| `sorted(x)` | Sorted copy | `sorted()` | `.sort()` | `.sort()` | helper |
| `reversed(x)` | Reversed copy | `reversed()` | `.reverse()` | `.reverse()` | helper |
| `abs(x)` | Absolute value | `abs()` | `Math.abs` | `i64::abs` | helper |
| `max(a, b)` / `min(a, b)` | Extremum | built-in | `Math.max/min` | `i64::max/min` | built-in |
| `range(a, b, step)` | Integer range | `range()` | for-loop | `a..b` | for-loop |
| `ord(c)` | Char to code | `ord()` | `charCodeAt` | `as i64` | `[]rune` |
| `chr(n)` | Code to char | `chr()` | `fromCharCode` | `char::from_u32` | `string(rune)` |
| `sqrt(x)` | Square root | `** 0.5` | `Math.sqrt` | `.sqrt()` | `math.Sqrt` |
| `pow(a, b)` | Power | `**` | `Math.pow` | `i64::pow` | `math.Pow` |
| `floor(x)` / `ceil(x)` | Rounding | `//` | `Math.floor/ceil` | `.floor()/ceil()` | `math.Floor/Ceil` |

---

## 9. Input / Output

### Reading files

```aicl
Behavior ReadConfig
    Input: path
    Output: content
    Action:
        content = read_file(path)
        return content
```

### Writing files

```aicl
Behavior SaveReport
    Input: path, report
    Output: success
    Action:
        write_file(path, report)
        return true
```

### Console output

```aicl
Behavior LogResult
    Input: value
    Output: ok
    Action:
        print("Result:", value)
        return true
```

### Reading stdin (interactive)

```aicl
Behavior AskUser
    Input: prompt
    Output: answer
    Action:
        answer = input(prompt)
        return answer
```

> Note: `input()` requires Node's `readline-sync` in JavaScript, but works
> natively in Python, Rust, and Go.

---

## 10. Functions and Recursion

Behaviors are your functions. A Behavior can call other Behaviors through the
generated class, but for recursion inside a single Behavior, just use the
Behavior name.

### Recursive factorial

```aicl
Behavior Factorial
    Input: n
    Output: result
    Action:
        if n <= 1:
            return 1
        return n * Factorial(n - 1)
```

### Mutual recursion

Define two Behaviors; they can call each other once compiled (call them as
methods on `self` in Python, or directly in Rust/Go where the compiler emits
free functions).

---

## 11. Slicing

Slicing works on lists and strings, in all four targets.

```aicl
Behavior SliceDemo
    Input: data
    Output: result
    Action:
        first_three = data[:3]          # first 3 elements
        last_two = data[-2:]            # last 2 (Python target)
        middle = data[2:5]              # indices 2, 3, 4
        every_other = data[::2]         # 0, 2, 4, ...
        reversed_copy = data[::-1]      # reversed (Python)
        return middle
```

| Slice | Meaning |
|-------|---------|
| `arr[a:b]` | from index `a` to `b-1` |
| `arr[:b]` | from start to `b-1` |
| `arr[a:]` | from `a` to end |
| `arr[::step]` | every `step`-th element |
| `arr[a:b:step]` | from `a` to `b` with step |

> Negative indices are fully supported in Python. Rust/Go targets fall back
> to forward-only slicing for static-typing reasons.

---

## 12. Risk and Recovery

Risks and Recoveries are **mandatory pairs**. If you declare a Risk, you must
declare a Recovery.

```aicl
Risk:
Database connection fails

Recovery:
Fall back to in-memory cache and log the error
```

The compiler generates error-handling code that detects the risk at runtime
and executes the recovery. This is real try/except, not a comment.

### Multiple risks

```aicl
Risk:
File not found

Recovery:
Create the file with default content

Risk:
Permission denied

Recovery:
Log and exit gracefully
```

---

## 13. Entities (Typed Data)

Entities define structured data with typed fields.

```aicl
Entity User
    name: string
    email: string
    age: integer
    active: boolean

Entity Order
    id: integer
    user: User
    total: float
    items: list
```

### Supported types

`string`, `integer`, `float`, `boolean`, `datetime`, `list`, `dict`, `set`,
`any`, `void`, `bytes`

---

## 14. Events and Conditions

### Conditions (When/Then)

```aicl
Condition:
    When temperature exceeds 100
    Then trigger cooling

Condition:
    When battery drops below 10 percent
    Then enter power-saving mode
```

### Events (On/Action)

```aicl
Event:
    On user login
    Action: record login time and send welcome email

Event:
    On file upload complete
    Action: scan for viruses and notify the user
```

Conditions and Events generate reactive scaffolding in the target code. The
compiler wires them into the application's main loop.

---

## 15. Compile Targets

AICL compiles the same source to four backends. Use `--target`:

```bash
aicl compile program.aicl --target python      # default
aicl compile program.aicl --target rust
aicl compile program.aicl --target javascript
aicl compile program.aicl --target go
```

### What you get per target

| Target | Main file | Test file | Notes |
|--------|-----------|-----------|-------|
| Python | `main.py` | `test_main.py` (pytest) | Default; easiest for prototyping |
| Rust | `main.rs` | inline `#[test]` | Statically typed; great for perf |
| JavaScript | `main.mjs` | — | Node or browser; ES6 classes |
| Go | `main.go` | — | Goroutines, interfaces |

The Proof of Origin (`.aicl-proof`) is **identical** across targets — the
audit trail doesn't depend on which language you compiled to.

### Target-specific notes

- **Rust**: integers are `i64`, floats are `f64`, lists are `Vec<T>`. Strings
  become `String::from(...)`.
- **Go**: lists become `[]interface{}`, dicts become `map[string]interface{}`.
- **JavaScript**: dicts compile to plain objects (so `d["key"]` works
  natively), sets to `new Set(...)`.
- **Python**: near-identity; AX is a subset of Python.

---

## 16. Workflows

### From the CLI

```bash
# Write your spec
vim myapp.aicl

# Verify it's well-formed
aicl verify myapp.aicl

# Compile to Python
aicl compile myapp.aicl --target python

# Compile to Rust
aicl compile myapp.aicl --target rust

# Explain why each line was generated
aicl explain myapp.aicl

# Audit provenance (No-Orphan Property)
aicl audit myapp.aicl

# View the architecture tree
aicl tree myapp.aicl
```

### From the web editor

1. Open the AICL Web Editor (Next.js app in `editor/`).
2. Write your spec in the center pane.
3. Click **Verify** to check spec quality.
4. Pick a target language from the dropdown.
5. Click **Compile** — output appears in the right panel.
6. Click **Audit** to verify 100% provenance coverage.
7. Click **Explain** to see the decision trace.
8. Click **AI Chat** for interactive help.

### From Python

```python
from aicl import Compiler

compiler = Compiler(target_language="python")
result = compiler.compile(source_code)

if result.success:
    print(result.source_code)   # the generated main.py
    print(result.test_code)     # the generated test_main.py
    # result.provenance has the audit trail
    # result.proof has the cryptographic Proof of Origin
```

---

## 17. Common Patterns (Cookbook)

### Word frequency counter

```aicl
Goal:
Count word frequencies in text

Layer:
Analyzer

Validation:
Counts are accurate

Behavior CountWords
    Input: text
    Output: counts
    Action:
        words = text.split()
        counts = {}
        for word in words:
            word = word.lower().strip()
            if word in counts:
                counts[word] = counts[word] + 1
            else:
                counts[word] = 1
        return counts
```

### CSV row parser

```aicl
Behavior ParseLine
    Input: line
    Output: fields
    Action:
        raw = line.split(",")
        fields = []
        for f in raw:
            fields.append(f.strip())
        return fields
```

### Fibonacci (iterative)

```aicl
Behavior Fib
    Input: n
    Output: result
    Action:
        if n <= 1:
            return n
        a = 0
        b = 1
        for i in range(2, n + 1):
            temp = a + b
            a = b
            b = temp
        return b
```

### Quicksort (with AX swap)

```aicl
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

### Contact book (CRUD)

```aicl
Goal:
Manage a contact book

Layer:
Contacts

Risk:
Duplicate contact

Recovery:
Reject the duplicate

Validation:
Contacts can be added and searched

Behavior AddContact
    Input: book, name, email
    Output: ok
    Action:
        if name in book:
            return false
        book[name] = email
        return true

Behavior Search
    Input: book, query
    Output: results
    Action:
        results = []
        query = query.lower()
        for name in book:
            if query in name.lower():
                results.append(name + " <" + book[name] + ">")
        return results
```

### Calculator (dispatch on operator)

```aicl
Behavior Calculate
    Input: expression
    Output: result
    Action:
        parts = expression.split()
        if len(parts) != 3:
            return 0
        a = int(parts[0])
        op = parts[1]
        b = int(parts[2])
        if op == "+":
            return a + b
        elif op == "-":
            return a - b
        elif op == "*":
            return a * b
        elif op == "/":
            if b == 0:
                return 0
            return a // b
        else:
            return 0
```

### File processor

```aicl
Goal:
Process a configuration file

Layer:
Config

Risk:
File not found

Recovery:
Use default configuration

Validation:
Configuration is loaded

Behavior Load
    Input: path
    Output: content
    Action:
        content = read_file(path)
        return content

Behavior Save
    Input: path, content
    Output: ok
    Action:
        write_file(path, content)
        return true
```

---

## 18. Debugging

### "Compilation failed: missing Goal"

You forgot the `Goal:` section. Add one at the top.

### "Compilation failed: missing Layer"

Add a `Layer:` section.

### "Compilation failed: missing Validation"

Add a `Validation:` section.

### "Risk without Recovery"

Every `Risk:` must be followed by a `Recovery:`.

### The Action block didn't compile to real code

If your `Action:` is English prose ("partition the array around a pivot"),
the compiler falls back to a skeleton. To get real code, write **AX** —
identifiable by `=`, `if`, `for`, `while`, `return`, or indented blocks.

Check with:

```bash
aicl check program.aicl
```

### AX syntax errors

```
line 5: expected OP ')' but got OP '.'
```

This usually means you tried to call a method on a literal in an older
version. Make sure you're on AICL 2.1+ where `"hello".upper()` parses.

### Audit coverage below 100%

Run `aicl audit program.aicl`. If coverage is < 1.0, some generated artifacts
lack provenance. Add more specific Entity/Behavior sections to give the
compiler more to tie code to.

### The generated code has TODOs

This means a Behavior's Action wasn't recognized as AX (or was incomplete).
Rewrite the Action as strict AX code.

---

## 19. Cheat Sheet

```
# Minimal program
Goal: <objective>
Layer: <component>
Validation: <success criterion>

# With a real Behavior
Behavior <Name>
    Input: <params>
    Output: <return>
    Action:
        <AX code>

# Risk/Recovery
Risk: <what can fail>
Recovery: <what to do>

# Entity
Entity <Name>
    <field>: <type>

# AX essentials
x = 5                          # assignment
x += 1                         # augmented
if x > 0:                      # conditional
    ...
elif x == 0:
    ...
else:
    ...
for i in range(10):            # counted loop
    ...
for item in collection:        # iterator
    ...
while x > 0:                   # conditional loop
    ...
return x                       # return
a, b = b, a                    # swap
if x in collection:            # membership
    ...
# Data
nums = [1, 2, 3]
d = {"key": "value"}
s = {1, 2, 3}
first = nums[0]
slice = nums[1:3]

# Strings
upper = s.upper()
parts = s.split(",")
joined = ",".join(parts)
pos = s.find("x")

# Stdlib
print(x)
n = len(s)
total = sum(nums)
ordered = sorted(nums)
n = int("42")
s = str(42)
content = read_file(path)
write_file(path, content)
```

---

## Where to go next

- **[AX Language Reference](./ax-language-reference.md)** — full grammar and
  every construct
- **[Standard Library Reference](./stdlib-reference.md)** — every builtin,
  with target mappings
- **[AICL Cookbook](./cookbook.md)** — 20+ ready-to-run recipes
- **[Getting Started](./getting-started.md)** — install and first program
- **[Proof of Origin](./proof-of-origin.md)** — the cryptographic audit trail
- **[Compile Targets](./targets.md)** — how AX maps to each backend

---

*Think better, not bigger. The architecture is the program; the code is a
byproduct.*
