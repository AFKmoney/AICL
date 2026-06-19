# Compile Targets

AICL compiles a single `.aicl` source file to four target languages. AX-written
behaviors produce **real, executable code** in every target — no stubs, no
`pass`-empty bodies.

## Supported targets

| Target | Flag | Output files | Runtime tested |
|--------|------|-------------|----------------|
| Python | `--target python` (default) | `main.py`, `test_main.py` | ✅ In-process exec |
| Rust | `--target rust` | `main.rs`, `Cargo.toml` | ✅ rustc compile + run |
| JavaScript | `--target javascript` | `main.mjs` | ✅ `node --check` |
| Go | `--target go` | `main.go`, `go.mod` | ✅ `go build` + run |

## Usage

```bash
# Compile to Python (default)
aicl compile myapp.aicl --target python -o ./output

# Compile to Rust
aicl compile myapp.aicl --target rust -o ./output

# Compile to JavaScript
aicl compile myapp.aicl --target javascript -o ./output

# Compile to Go
aicl compile myapp.aicl --target go -o ./output
```

Each target produces an identical `main.aicl-proof` file — the Proof of Origin
is target-independent. The provenance chain is the same regardless of backend.

## How AX translates

AX is a common subset of all four languages. The compiler applies
target-specific translations for the constructs that don't map 1:1:

### Loops

| AX | Python | Rust | JS | Go |
|----|--------|------|----|----|
| `for x in range(a, b)` | `for x in range(a, b):` | `for x in (a)..(b)` | `for (let x = a; x < b; x++)` | `for x := a; x < b; x++` |
| `while cond` | `while cond:` | `while cond` | `while (cond)` | `for cond` |

### Swaps

| AX | Python | Rust | JS | Go |
|----|--------|------|----|----|
| `a, b = b, a` | `a, b = b, a` | temp vars (capture-first) | `[a, b] = [b, a]` | native (names) / temps (indexed) |

### Builtins

| AX | Python | Rust | JS | Go |
|----|--------|------|----|----|
| `len(x)` | `len(x)` | `x.len() as i64` | `x.length` | `len(x)` |
| `abs(x)` | `abs(x)` | `i64::abs(x)` | `Math.abs(x)` | inline branch |
| `x // y` | `x // y` | `x / y` (int) | `Math.trunc(x / y)` | `x / y` (int) |

## Type inference for static targets

Rust and Go are statically typed. AX is dynamically typed. The compiler
infers types from usage patterns:

- **Array**: name is indexed (`x[i]`), passed to `len()`, or has list methods
- **Integer**: name is in arithmetic or augmented assignment
- **Default**: integer (for numeric contexts)

Example: `Behavior Sort: Input: array, low, high`

| Param | Inferred type | Rust | Go |
|-------|--------------|------|----|
| `array` | ARRAY (indexed) | `&mut [i64]` | `[]int` |
| `low` | INT | `i64` | `int` |
| `high` | INT | `i64` | `int` |

## Limitations

- AX behaviors compile to real code. Non-AX behaviors (English prose Actions)
  still produce structural skeletons with comments.
- The scaffolding (struct/class definitions, error handling) is generated per
  target and may need manual adjustment for production use.
- Mixed-type lists are not supported (AX lists are homogeneous: all `i64` /
  `int`).
