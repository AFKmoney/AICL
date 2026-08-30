# AICL Standard Library Reference

> The AX standard library provides 40+ built-in functions available inside
> `Action:` blocks. Every builtin compiles to a native equivalent in Python,
> JavaScript, Rust, and Go.

For the language grammar, see [AX Language Reference](./ax-language-reference.md).
For tutorials, see [How to Code in AICL](./how-to-code-in-aicl.md).

---

## Table of Contents

- [Console I/O](#console-io)
- [File I/O](#file-io)
- [Type Conversion](#type-conversion)
- [Collections](#collections)
- [Math](#math)
- [Strings](#strings)
- [Iteration Helpers](#iteration-helpers)
- [Range](#range)

---

## Console I/O

### `print(...args)`

Print one or more values to stdout, separated by spaces.

```
print("Hello, world!")
print("Sum:", x + y)
print("coords:", x, y, z)
```

| Target | Generated code |
|--------|----------------|
| Python | `print("Sum:", x + y)` |
| JS | `console.log("Sum:", x + y);` |
| Rust | `println!("{}", "Sum:");` |
| Go | `fmt.Println("Sum:", x + y)` |

### `input(prompt?)`

Read a line from stdin. Blocks until the user presses Enter.

```
name = input("Enter your name: ")
age = input("Age: ")
```

| Target | Generated code |
|--------|----------------|
| Python | `input("Enter your name: ")` |
| JS | `require('readline-sync').question(...)` (Node only) |
| Rust | `std::io::stdin().read_line(...)` |
| Go | `bufio.NewReader(os.Stdin).ReadString('\n')` |

> **Note:** `input()` requires the `readline-sync` npm package in JavaScript.
> In Python, Rust, and Go it uses the standard library.

---

## File I/O

### `read_file(path)`

Read an entire file into a string.

```
content = read_file("/etc/hostname")
config = read_file("./config.json")
```

| Target | Generated code |
|--------|----------------|
| Python | `open(path).read()` |
| JS | `require('fs').readFileSync(path, 'utf8')` |
| Rust | `std::fs::read_to_string(path).unwrap()` |
| Go | `os.ReadFile(path)` (wrapped) |

### `write_file(path, content)`

Write a string to a file, overwriting any existing content.

```
write_file("/tmp/output.txt", "Hello, file!")
write_file(log_path, message + "\n")
```

| Target | Generated code |
|--------|----------------|
| Python | `open(path, 'w').write(content)` |
| JS | `require('fs').writeFileSync(path, content, 'utf8')` |
| Rust | `std::fs::write(path, content).unwrap()` |
| Go | `os.WriteFile(path, []byte(content), 0644)` (wrapped) |

---

## Type Conversion

### `int(x)`

Convert a value to an integer.

```
n = int("42")          # 42
n = int(3.99)          # 3
n = int(true)          # 1
```

| Target | Generated code |
|--------|----------------|
| Python | `int(x)` |
| JS | `parseInt(x, 10)` |
| Rust | `(x as i64)` |
| Go | helper `_axInt(x)` |

### `str(x)`

Convert any value to its string representation.

```
s = str(42)            # "42"
s = str(3.14)          # "3.14"
s = str([1, 2, 3])     # "[1, 2, 3]"
```

| Target | Generated code |
|--------|----------------|
| Python | `str(x)` |
| JS | `String(x)` |
| Rust | `format!("{}", x)` |
| Go | `fmt.Sprintf("%v", x)` |

### `float(x)`

Convert a value to a float.

```
f = float("3.14")      # 3.14
f = float(5)           # 5.0
```

| Target | Generated code |
|--------|----------------|
| Python | `float(x)` |
| JS | `parseFloat(x)` |
| Rust | `(x as f64)` |
| Go | `float64(x)` |

### `bool(x)`

Convert a value to a boolean.

```
b = bool(0)            # false
b = bool("")           # false
b = bool(1)            # true
b = bool("text")       # true
```

| Target | Generated code |
|--------|----------------|
| Python | `bool(x)` |
| JS | `Boolean(x)` |
| Rust | `(x != 0)` |
| Go | `(x != 0)` |

---

## Collections

### `len(x)`

Return the length of a string, list, dict, or set.

```
n = len("hello")             # 5
n = len([1, 2, 3])           # 3
n = len({"a": 1, "b": 2})    # 2
```

| Target | Generated code |
|--------|----------------|
| Python | `len(x)` |
| JS | `x.length` |
| Rust | `x.len() as i64` |
| Go | `len(x)` |

### `sum(iterable)`

Return the sum of all elements.

```
total = sum([1, 2, 3, 4, 5])    # 15
total = sum(prices)
```

| Target | Generated code |
|--------|----------------|
| Python | `sum(x)` |
| JS | `x.reduce((a, b) => a + b, 0)` |
| Rust | `x.iter().sum::<i64>()` |
| Go | helper `_axSum(x)` |

### `sorted(iterable)`

Return a new sorted list (ascending). The original is not modified.

```
ordered = sorted([3, 1, 4, 1, 5])    # [1, 1, 3, 4, 5]
names = sorted(people)
```

| Target | Generated code |
|--------|----------------|
| Python | `sorted(x)` |
| JS | `[...x].sort((a, b) => a - b)` |
| Rust | `{ let mut v = x.clone(); v.sort(); v }` |
| Go | helper `_axSorted(x)` |

### `reversed(iterable)`

Return a new list with elements in reverse order.

```
back = reversed([1, 2, 3])    # [3, 2, 1]
```

| Target | Generated code |
|--------|----------------|
| Python | `list(reversed(x))` |
| JS | `[...x].reverse()` |
| Rust | `{ let mut v = x.clone(); v.reverse(); v }` |
| Go | helper `_axReversed(x)` |

### `list(x)`

Convert an iterable to a list.

```
items = list(some_iterable)
chars = list("hello")        # ["h", "e", "l", "l", "o"]
```

| Target | Generated code |
|--------|----------------|
| Python | `list(x)` |
| JS | `[...x]` |
| Rust | `x.to_vec()` |
| Go | helper |

### `dict(x)`

Create a dict from an iterable of pairs.

```
d = dict([("a", 1), ("b", 2)])    # {"a": 1, "b": 2}
```

| Target | Generated code |
|--------|----------------|
| Python | `dict(x)` |
| JS | `new Map(Object.entries(x))` |
| Rust | HashMap from iter |
| Go | map literal |

### `enumerate(iterable)`

Return a list of `(index, value)` pairs.

```
for i, item in enumerate(items):
    print(i, item)
```

| Target | Generated code |
|--------|----------------|
| Python | `enumerate(x)` |
| JS | `x.map((v, i) => [i, v])` |
| Rust | `.enumerate()` |
| Go | manual loop |

### `zip(a, b)`

Return a list of pairs from two iterables.

```
for name, age in zip(names, ages):
    print(name, age)
```

| Target | Generated code |
|--------|----------------|
| Python | `zip(a, b)` |
| JS | `a.map((v, i) => [v, b[i]])` |
| Rust | `.zip()` |
| Go | manual loop |

---

## Math

### `abs(x)`

Absolute value.

```
d = abs(-5)        # 5
d = abs(x - y)
```

| Target | Generated code |
|--------|----------------|
| Python | `abs(x)` |
| JS | `Math.abs(x)` |
| Rust | `i64::abs(x)` |
| Go | helper `_absInt(x)` |

### `max(...args)` / `min(...args)`

Return the maximum / minimum of the arguments.

```
m = max(3, 7, 2)            # 7
m = min(3, 7, 2)            # 2
m = max(a, b)
```

| Target | Generated code |
|--------|----------------|
| Python | `max(...)` / `min(...)` |
| JS | `Math.max(...)` / `Math.min(...)` |
| Rust | `i64::max(...)` / `i64::min(...)` |
| Go | built-in `max` / `min` (Go 1.21+) |

### `sqrt(x)`

Square root (returns a float).

```
r = sqrt(16)       # 4.0
r = sqrt(2)        # 1.4142135623730951
```

| Target | Generated code |
|--------|----------------|
| Python | `x ** 0.5` |
| JS | `Math.sqrt(x)` |
| Rust | `(x as f64).sqrt()` |
| Go | `math.Sqrt(float64(x))` |

### `pow(base, exp)`

Exponentiation.

```
r = pow(2, 10)     # 1024
r = pow(10, 3)     # 1000
```

| Target | Generated code |
|--------|----------------|
| Python | `base ** exp` |
| JS | `Math.pow(base, exp)` |
| Rust | `i64::pow(base, exp as u32)` |
| Go | `int(math.Pow(float64(base), float64(exp)))` |

### `floor(x)` / `ceil(x)`

Round down / round up to the nearest integer.

```
f = floor(3.7)     # 3
c = ceil(3.2)      # 4
```

| Target | Generated code (floor) |
|--------|----------------|
| Python | `// 1` (or `math.floor`) |
| JS | `Math.floor(x)` |
| Rust | `(x as f64).floor() as i64` |
| Go | `int(math.Floor(float64(x)))` |

---

## Strings

### `ord(c)`

Return the Unicode code point of the first character of a string.

```
code = ord("A")        # 65
code = ord("a")        # 97
```

| Target | Generated code |
|--------|----------------|
| Python | `ord(c)` |
| JS | `c.charCodeAt(0)` |
| Rust | `c.chars().next().unwrap() as i64` |
| Go | `int([]rune(c)[0])` |

### `chr(n)`

Return a single-character string for the given code point.

```
s = chr(65)            # "A"
s = chr(97)            # "a"
```

| Target | Generated code |
|--------|----------------|
| Python | `chr(n)` |
| JS | `String.fromCharCode(n)` |
| Rust | `char::from_u32(n as u32).unwrap().to_string()` |
| Go | `string(rune(n))` |

---

## Iteration Helpers

### `range(stop)` / `range(start, stop)` / `range(start, stop, step)`

Generate a sequence of integers. Commonly used in `for` loops.

```
for i in range(10):            # 0, 1, 2, ..., 9
    print(i)

for i in range(2, 11):         # 2, 3, 4, ..., 10
    print(i)

for i in range(0, 20, 2):      # 0, 2, 4, ..., 18
    print(i)

for i in range(10, 0, -1):     # 10, 9, 8, ..., 1
    print(i)
```

In `for` loops, `range` compiles to native loop constructs:

| Target | For-loop with range |
|--------|---------------------|
| Python | `for i in range(a, b):` |
| JS | `for (let i = a; i < b; i += step) {` |
| Rust | `for i in (a)..(b).step_by(step) {` |
| Go | `for i := a; i < b; i += step {` |

When used outside a `for` loop, `range` produces a list:

| Target | Expression |
|--------|------------|
| Python | `list(range(a, b))` |
| JS | `Array.from({length: b - a}, (_, i) => a + i)` |
| Rust | `(a..b).collect::<Vec<_>>()` |
| Go | manual slice |

---

## Complete Reference Table

| Function | Signature | Returns |
|----------|-----------|---------|
| `print` | `(*args)` | `none` |
| `input` | `(prompt?)` | `string` |
| `read_file` | `(path)` | `string` |
| `write_file` | `(path, content)` | `none` |
| `int` | `(x)` | `integer` |
| `str` | `(x)` | `string` |
| `float` | `(x)` | `float` |
| `bool` | `(x)` | `boolean` |
| `len` | `(x)` | `integer` |
| `sum` | `(iterable)` | `integer` / `float` |
| `sorted` | `(iterable)` | `list` |
| `reversed` | `(iterable)` | `list` |
| `list` | `(iterable)` | `list` |
| `dict` | `(pairs)` | `dict` |
| `enumerate` | `(iterable)` | `list of (int, any)` |
| `zip` | `(a, b)` | `list of (any, any)` |
| `abs` | `(x)` | `integer` / `float` |
| `max` | `(*args)` | `integer` / `float` |
| `min` | `(*args)` | `integer` / `float` |
| `sqrt` | `(x)` | `float` |
| `pow` | `(base, exp)` | `integer` |
| `floor` | `(x)` | `integer` |
| `ceil` | `(x)` | `integer` |
| `ord` | `(c)` | `integer` |
| `chr` | `(n)` | `string` |
| `range` | `([start,] stop[, step])` | iterable |

---

## Method Reference

### String methods

| Method | Returns | Notes |
|--------|---------|-------|
| `.upper()` | `string` | Uppercase |
| `.lower()` | `string` | Lowercase |
| `.strip()` | `string` | Trim whitespace both sides |
| `.lstrip()` | `string` | Trim left |
| `.rstrip()` | `string` | Trim right |
| `.split(sep?)` | `list` | Split on separator (or whitespace) |
| `.join(iterable)` | `string` | Join with separator (called on separator) |
| `.replace(old, new)` | `string` | Replace all occurrences |
| `.find(sub)` | `integer` | Index of first occurrence (-1 if absent) |
| `.startswith(s)` | `boolean` | Prefix test |
| `.endswith(s)` | `boolean` | Suffix test |
| `.count(sub)` | `integer` | Count non-overlapping occurrences |
| `.contains(sub)` | `boolean` | Substring test (non-Python idiom) |
| `.format(*args)` | `string` | `{0}`/`{1}` formatting |

### List methods

| Method | Returns | Notes |
|--------|---------|-------|
| `.append(x)` | `none` | Add to end |
| `.pop()` | `any` | Remove and return last |
| `.insert(i, x)` | `none` | Insert at index |
| `.remove(x)` | `none` | Remove first occurrence |
| `.sort()` | `none` | Sort in place (ascending) |
| `.reverse()` | `none` | Reverse in place |
| `.extend(other)` | `none` | Append all from other |

### Dict methods

| Method | Returns | Notes |
|--------|---------|-------|
| `.get(key)` | `any` | Get value or `none` |
| `.get(key, default)` | `any` | Get value or default |
| `.keys()` | `list` | All keys |
| `.values()` | `list` | All values |
| `.items()` | `list` | List of `(key, value)` pairs |

---

## See also

- [AX Language Reference](./ax-language-reference.md) — full grammar
- [How to Code in AICL](./how-to-code-in-aicl.md) — tutorial
- [AICL Cookbook](./cookbook.md) — recipes using the stdlib
- [Compile Targets](./targets.md) — backend details
