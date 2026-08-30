# AICL Language Specification v0.1

**AI-Centric Language: Specification-First Programming**

Author: Philippe-Antoine  
Version: 0.1.0  
Date: 2026-06-13  
Status: Draft

---

## 1. Overview

AICL (AI-Centric Language) is a specification-first programming language where software is defined through structured architectural intent rather than implementation instructions. Instead of writing executable code directly, developers specify objectives, architectural layers, anticipated failure modes, recovery procedures, constraints, validation criteria, and optimization goals.

The AICL compiler transforms these high-level architectural specifications into executable software through a multi-stage compilation pipeline.

---

## 2. Design Principles

1. **Architecture is the program** — The specification IS the source code
2. **Risks are first-class** — Failure modeling is mandatory, not optional
3. **Validation is built-in** — Success criteria are part of the language
4. **Strict grammar** — Deterministic parsing, not free-form natural language
5. **AI-native compilation** — The compiler reasons about architecture, not just translates

---

## 3. Formal Grammar (BNF)

```
<program>       ::= <section>*
<section>       ::= <goal-section>
                  | <constraint-section>
                  | <risk-section>
                  | <recovery-section>
                  | <layer-section>
                  | <validation-section>
                  | <entity-section>
                  | <behavior-section>
                  | <condition-section>
                  | <event-section>
                  | <parallel-section>
                  | <optimize-section>
                  | <learn-section>
                  | <adapt-section>
                  | <security-section>
                  | <native-section>

<goal-section>      ::= "Goal:" <text>
<constraint-section>::= "Constraint:" <text>
<risk-section>      ::= "Risk:" <text>
<recovery-section>  ::= "Recovery:" <text>
<validation-section>::= "Validation:" <text>
<optimize-section>  ::= "Optimize:" <text>
<priority-section>  ::= "Priority:" <text>

<layer-section>     ::= "Layer:" <text> <sublayer-section>*
<sublayer-section>  ::= "Sublayer:" <text>

<entity-section>    ::= "Entity" <identifier> <entity-body>
<entity-body>       ::= INDENT <field-def>+ DEDENT
<field-def>         ::= <identifier> ":" <type-name>

<behavior-section>  ::= "Behavior" <identifier> <behavior-body>
<behavior-body>     ::= INDENT (<input-section> | <output-section> | <action-section>)+ DEDENT
<input-section>     ::= "Input:" <text>
<output-section>    ::= "Output:" <text>
<action-section>    ::= "Action:" <text>

<condition-section> ::= "Condition:" <condition-body>
<condition-body>    ::= INDENT <when-clause> <then-clause> DEDENT
<when-clause>       ::= "When" <text>
<then-clause>       ::= "Then" <text>

<event-section>     ::= "Event:" <event-body>
<event-body>        ::= INDENT <on-clause> <action-section> DEDENT
<on-clause>         ::= "On" <text>

<parallel-section>  ::= "Parallel:" <layer-list>
<layer-list>        ::= INDENT <text>+ DEDENT

<learn-section>     ::= "Learn:" <text> <learn-goal>
<learn-goal>        ::= INDENT "Goal:" <text> DEDENT

<adapt-section>     ::= "Adapt:" <text> <adapt-based>
<adapt-based>       ::= INDENT "Based:" <text> DEDENT

<security-section>  ::= "Security:" <security-body>
<security-body>     ::= INDENT (<encrypt-action> | <protect-action>)* DEDENT
<encrypt-action>    ::= "Encrypt:" <text>
<protect-action>    ::= "Protect:" <text>

<native-section>    ::= "Native:" <language-name> <native-block>
<native-block>      ::= "{" <raw-code> "}"

<type-name>     ::= "string" | "integer" | "float" | "boolean"
                  | "datetime" | "list" | "dict" | "set" | "any"
                  | "void" | "bytes" | <identifier>

<identifier>    ::= <letter> (<letter> | <digit> | "_")*
<text>          ::= <any printable text until end of line>
<language-name> ::= <identifier>
<raw-code>      ::= <any text between braces>
```

---

## 4. Keywords

AICL has 27 reserved keywords:

| Keyword | Level | Purpose |
|---------|-------|---------|
| Goal | 1 | Define system objective |
| Constraint | 1 | Define system limitation |
| Risk | 1 | Define failure condition |
| Recovery | 1 | Define corrective action |
| Layer | 1 | Define architectural layer |
| Sublayer | 1 | Define sub-layer within a layer |
| Validation | 1 | Define success criterion |
| Entity | 2 | Define data entity |
| Behavior | 3 | Define entity behavior |
| Input | 3 | Define behavior input |
| Output | 3 | Define behavior output |
| Action | 3/5 | Define action to perform |
| Condition | 4 | Define conditional behavior |
| When | 4 | Condition trigger |
| Then | 4 | Condition consequence |
| Event | 5 | Define event-driven behavior |
| On | 5 | Event trigger |
| Parallel | 6 | Define concurrent execution |
| Optimize | 7 | Define optimization target |
| Priority | 7 | Define optimization priority |
| Learn | 8 | Define learning objective |
| Adapt | 8 | Define adaptive behavior |
| Based | 8 | Adaptation criterion |
| Security | 9 | Define security requirements |
| Encrypt | 9 | Encryption directive |
| Protect | 9 | Protection directive |
| Native | 10 | Inline native code |

---

## 5. Language Levels

### Level 1 — Architecture (Mandatory)
Core architectural specification: Goal, Constraint, Risk, Recovery, Layer, Validation.

### Level 2 — Entities
Data structure definitions with typed fields.

### Level 3 — Behaviors
Define what entities do, with inputs, outputs, and actions.

### Level 4 — Conditions
Replace traditional if/else with When/Then clauses.

### Level 5 — Events
Event-driven programming with On/Action pairs.

### Level 6 — Concurrency
Parallel execution of layers, with compiler deciding threading strategy.

### Level 7 — Optimization
Optimization targets and priorities.

### Level 8 — Learning
Machine learning integration and adaptive behavior.

### Level 9 — Security
Built-in security directives (encryption, protection).

### Level 10 — Native Code
Escape hatch for low-level implementation in any language.

---

## 6. Compilation Pipeline

1. **Specification Parsing** — Parse AICL source into AST
2. **Architecture Validation** — Check structural completeness
3. **Dependency Analysis** — Determine layer dependencies
4. **Risk Analysis** — Pair risks with recovery procedures
5. **Recovery Synthesis** — Generate recovery logic
6. **Code Generation** — Generate target language code
7. **Test Generation** — Generate tests from validations
8. **Optimization** — Apply optimization strategies
9. **Final Construction** — Produce final executable output

---

## 7. Minimal Valid Program

```
Goal:
Hello World

Layer:
Core

Validation:
Output is produced
```

---

## 8. File Extension

AICL source files use the `.aicl` extension.

---

## 9. Comments

Lines starting with `#` are treated as comments and ignored by the parser.

---

## 10. Type System

| AICL Type | Python Target | Description |
|-----------|--------------|-------------|
| string | str | Text data |
| integer | int | Whole numbers |
| float | float | Floating-point numbers |
| boolean | bool | True/False values |
| datetime | datetime | Date and time |
| list | List[Any] | Ordered collection |
| dict | Dict[str, Any] | Key-value mapping |
| set | set | Unique collection |
| any | Any | Dynamic type |
| void | None | No return value |

---

## 11. AX Sub-Language (Turing-complete)

AX (AICL-Action) is a strict, compilable sub-language used inside `Action:`
sections of Behaviors. Instead of free-form English prose that the compiler
can only skeleton, AX provides real logic: conditionals, loops, recursion,
arithmetic, and data operations. AX compiles to **executable code** in all
four targets (Python, Rust, JavaScript, Go).

### AX Grammar

```
action        ::= stmt+
stmt          ::= assign | if_stmt | while_stmt | for_stmt | return_stmt
              |   call_stmt | break | continue | swap | pass
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
comp_op       ::= "==" | "!=" | "<" | "<=" | ">" | ">="
              |   "in" | "not" "in" | "is" | "is" "not"
arith         ::= term (("+" | "-") term)*
term          ::= factor (("*" | "/" | "//" | "%") factor)*
factor        ::= "-" factor | power
power         ::= postfix ("**" factor)?
postfix       ::= atom suffix*
suffix        ::= "[" slice_or_index "]" | "." NAME | "(" args? ")"
atom          ::= literal | NAME | "(" expr ")" | list | dict | set | call | index | attr
literal       ::= int | float | string | true | false | none
list          ::= "[" (expr ("," expr)*)? "]"
dict          ::= "{" (pair ("," pair)*)? "}"
set           ::= "{" (expr ("," expr)*)? "}"            # no colons
pair          ::= expr ":" expr
slice_or_index::= expr? ":" expr? (":" expr?)?           # slice
              |   expr                                    # index
swap          ::= lvalue_list "=" expr_list   (e.g. a, b = b, a)
```

### AX Builtins

| Builtin | Effect |
|---------|--------|
| `range(a, b)` | Iterator from a to b exclusive |
| `range(a, b, c)` | Iterator from a to b exclusive, step c |
| `len(x)` | Length of array/string/dict |
| `abs(x)` | Absolute value |
| `max(a, b)` / `min(a, b)` | Maximum / minimum |
| `sum(list)` | Sum of all elements |
| `sorted(x)` | Sorted copy |
| `reversed(x)` | Reversed copy |
| `int(x)` / `str(x)` / `float(x)` / `bool(x)` | Type conversion |
| `ord(c)` / `chr(n)` | Character <-> code point |
| `sqrt(x)` / `pow(a, b)` / `floor(x)` / `ceil(x)` | Math |
| `print(...)` | Console output |
| `input(prompt?)` | Read from stdin |
| `read_file(path)` / `write_file(path, content)` | File I/O |
| `enumerate(x)` / `zip(a, b)` | Iteration helpers |
| `list(x)` / `dict(x)` | Collection constructors |
| `result.append(x)` | Append to list |

### AX Data Structures

AX supports lists, dictionaries, and sets:

```
nums = [1, 2, 3, 4, 5]
scores = {"alice": 90, "bob": 85}
unique = {1, 2, 3}
```

### AX Slicing

AX supports Python-style slicing on lists and strings:

```
first_three = arr[:3]
middle = arr[2:5]
every_other = arr[::2]
reversed = arr[::-1]
```

### AX Membership Operators

```
if item in collection:    # present
    ...
if item not in collection:  # absent
    ...
if x is none:              # identity check
    ...
if x is not none:
    ...
```

### AX Example

```
Behavior Quicksort
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

See [`docs/ax-reference.md`](../../docs/ax-reference.md) for the full reference
and [`docs/targets.md`](../../docs/targets.md) for how AX translates to each
compile target.
| bytes | bytes | Binary data |
