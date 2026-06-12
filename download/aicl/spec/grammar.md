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
| bytes | bytes | Binary data |
