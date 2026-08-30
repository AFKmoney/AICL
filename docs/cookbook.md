# AICL Cookbook

> Ready-to-run recipes for real problems. Every recipe compiles to executable
> code in Python, Rust, JavaScript, and Go.

For the language grammar, see [AX Language Reference](./ax-language-reference.md).
For builtin functions, see [Standard Library Reference](./stdlib-reference.md).

---

## Table of Contents

1. [Algorithms](#1-algorithms)
2. [String Processing](#2-string-processing)
3. [Data Structures](#3-data-structures)
4. [Data Processing](#4-data-processing)
5. [File I/O](#5-file-io)
6. [Math & Numeric](#6-math--numeric)
7. [Search & Filter](#7-search--filter)
8. [Text Analysis](#8-text-analysis)
9. [CRUD Applications](#9-crud-applications)
10. [Validation](#10-validation)

---

## 1. Algorithms

### Quicksort

```aicl
Goal:
Sort an array using quicksort

Layer:
Sorter

Validation:
Output is sorted in non-decreasing order

Behavior Quicksort
    Input: array, low, high
    Output: sorted
    Action:
        if low < high:
            pi = Partition(array, low, high)
            Quicksort(array, low, pi - 1)
            Quicksort(array, pi + 1, high)
        return array

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

### Binary search

```aicl
Goal:
Find an element in a sorted array

Layer:
Searcher

Validation:
Correct index is returned or -1

Behavior BinarySearch
    Input: array, target
    Output: index
    Action:
        low = 0
        high = len(array) - 1
        while low <= high:
            mid = (low + high) // 2
            if array[mid] == target:
                return mid
            elif array[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        return -1
```

### Fibonacci (iterative)

```aicl
Goal:
Compute Fibonacci numbers

Layer:
Math

Validation:
fib(n) returns the n-th Fibonacci number

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

### Factorial (recursive)

```aicl
Goal:
Compute factorials

Layer:
Math

Validation:
fact(n) returns n!

Behavior Factorial
    Input: n
    Output: result
    Action:
        if n <= 1:
            return 1
        return n * Factorial(n - 1)
```

### GCD (Euclid)

```aicl
Behavior GCD
    Input: a, b
    Output: result
    Action:
        while b != 0:
            temp = b
            b = a % b
            a = temp
        return a
```

### Prime check

```aicl
Behavior IsPrime
    Input: n
    Output: result
    Action:
        if n < 2:
            return false
        if n == 2:
            return true
        if n % 2 == 0:
            return false
        i = 3
        while i * i <= n:
            if n % i == 0:
                return false
            i = i + 2
        return true
```

---

## 2. String Processing

### Reverse a string

```aicl
Behavior Reverse
    Input: s
    Output: result
    Action:
        result = ""
        for i in range(len(s) - 1, -1, -1):
            result = result + s[i]
        return result
```

### Count vowels

```aicl
Behavior CountVowels
    Input: text
    Output: count
    Action:
        count = 0
        for char in text.lower():
            if char in "aeiou":
                count = count + 1
        return count
```

### Title case

```aicl
Behavior TitleCase
    Input: text
    Output: result
    Action:
        words = text.split()
        result = []
        for word in words:
            if len(word) > 0:
                first = word[0].upper()
                rest = word[1:].lower()
                result.append(first + rest)
        return " ".join(result)
```

### CamelCase to snake_case

```aicl
Behavior ToSnakeCase
    Input: text
    Output: result
    Action:
        result = ""
        for char in text:
            if char >= "A" and char <= "Z":
                result = result + "_" + char.lower()
            else:
                result = result + char
        return result
```

### Palindrome check

```aicl
Behavior IsPalindrome
    Input: text
    Output: result
    Action:
        cleaned = text.lower().replace(" ", "")
        return cleaned == Reverse(cleaned)
```

### Simple template substitution

```aicl
Behavior Substitute
    Input: template, values
    Output: result
    Action:
        result = template
        for key in values:
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(values[key]))
        return result
```

---

## 3. Data Structures

### Stack

```aicl
Goal:
Implement a stack

Layer:
Stack

Validation:
Push and pop work correctly

Behavior Push
    Input: stack, item
    Output: stack
    Action:
        stack.append(item)
        return stack

Behavior Pop
    Input: stack
    Output: item
    Action:
        if len(stack) == 0:
            return none
        return stack.pop()

Behavior Peek
    Input: stack
    Output: item
    Action:
        if len(stack) == 0:
            return none
        return stack[len(stack) - 1]
```

### Queue (using list)

```aicl
Behavior Enqueue
    Input: queue, item
    Output: queue
    Action:
        queue.append(item)
        return queue

Behavior Dequeue
    Input: queue
    Output: item
    Action:
        if len(queue) == 0:
            return none
        return queue.pop(0)
```

### Frequency map

```aicl
Behavior Frequency
    Input: items
    Output: counts
    Action:
        counts = {}
        for item in items:
            if item in counts:
                counts[item] = counts[item] + 1
            else:
                counts[item] = 1
        return counts
```

### Group by key

```aicl
Behavior GroupBy
    Input: pairs
    Output: groups
    Action:
        groups = {}
        for pair in pairs:
            key = pair[0]
            value = pair[1]
            if key in groups:
                groups[key].append(value)
            else:
                groups[key] = [value]
        return groups
```

### Counter with top-N

```aicl
Behavior TopN
    Input: items, n
    Output: top
    Action:
        counts = {}
        for item in items:
            if item in counts:
                counts[item] = counts[item] + 1
            else:
                counts[item] = 1
        sorted_items = sorted(counts.items())
        return sorted_items[:n]
```

---

## 4. Data Processing

### CSV line parser

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

### Filter rows by column value

```aicl
Behavior FilterByValue
    Input: rows, column, value
    Output: filtered
    Action:
        filtered = []
        for row in rows:
            if column < len(row):
                if row[column] == value:
                    filtered.append(row)
        return filtered
```

### Sum a numeric column

```aicl
Behavior SumColumn
    Input: rows, column
    Output: total
    Action:
        total = 0
        for row in rows:
            if column < len(row):
                total = total + int(row[column])
        return total
```

### Map / Reduce

```aicl
Behavior MapSquared
    Input: nums
    Output: result
    Action:
        result = []
        for n in nums:
            result.append(n * n)
        return result

Behavior ReduceSum
    Input: nums
    Output: total
    Action:
        total = 0
        for n in nums:
            total = total + n
        return total
```

### Deduplicate

```aicl
Behavior Unique
    Input: items
    Output: result
    Action:
        seen = {}
        result = []
        for item in items:
            if item not in seen:
                seen[item] = true
                result.append(item)
        return result
```

---

## 5. File I/O

### Read and count lines

```aicl
Goal:
Count lines in a file

Layer:
LineCounter

Risk:
File not found

Recovery:
Return 0

Validation:
Line count is correct

Behavior CountLines
    Input: path
    Output: count
    Action:
        content = read_file(path)
        lines = content.split(chr(10))
        return len(lines)
```

### Read CSV and sum a column

```aicl
Goal:
Sum a column from a CSV file

Layer:
CSVSum

Risk:
Malformed CSV

Recovery:
Skip the malformed line

Validation:
Sum is correct

Behavior SumCsvColumn
    Input: path, column
    Output: total
    Action:
        content = read_file(path)
        lines = content.split(chr(10))
        total = 0
        for line in lines:
            fields = line.split(",")
            if column < len(fields):
                total = total + int(fields[column].strip())
        return total
```

### Write a log file

```aicl
Behavior AppendLog
    Input: path, message
    Output: ok
    Action:
        existing = read_file(path)
        write_file(path, existing + message + chr(10))
        return true
```

### Convert tab-separated to comma-separated

```aicl
Behavior TsvToCsv
    Input: tsv
    Output: csv
    Action:
        lines = tsv.split(chr(10))
        result = []
        for line in lines:
            fields = line.split("\t")
            result.append(",".join(fields))
        return chr(10).join(result)
```

---

## 6. Math & Numeric

### Average

```aicl
Behavior Average
    Input: nums
    Output: avg
    Action:
        if len(nums) == 0:
            return 0
        return sum(nums) / len(nums)
```

### Median

```aicl
Behavior Median
    Input: nums
    Output: m
    Action:
        n = len(nums)
        if n == 0:
            return 0
        ordered = sorted(nums)
        mid = n // 2
        if n % 2 == 1:
            return ordered[mid]
        return (ordered[mid - 1] + ordered[mid]) / 2
```

### Standard deviation

```aicl
Behavior StdDev
    Input: nums
    Output: sd
    Action:
        n = len(nums)
        if n == 0:
            return 0
        avg = sum(nums) / n
        variance = 0
        for x in nums:
            diff = x - avg
            variance = variance + diff * diff
        variance = variance / n
        return sqrt(variance)
```

### Power mod

```aicl
Behavior PowMod
    Input: base, exp, mod
    Output: result
    Action:
        result = 1
        b = base % mod
        while exp > 0:
            if exp % 2 == 1:
                result = (result * b) % mod
            exp = exp // 2
            b = (b * b) % mod
        return result
```

### Collatz sequence length

```aicl
Behavior Collatz
    Input: n
    Output: steps
    Action:
        steps = 0
        while n != 1:
            if n % 2 == 0:
                n = n // 2
            else:
                n = 3 * n + 1
            steps = steps + 1
        return steps
```

---

## 7. Search & Filter

### Linear search

```aicl
Behavior Find
    Input: items, target
    Output: index
    Action:
        for i in range(len(items)):
            if items[i] == target:
                return i
        return -1
```

### Find all matches

```aicl
Behavior FindAll
    Input: items, target
    Output: indices
    Action:
        indices = []
        for i in range(len(items)):
            if items[i] == target:
                indices.append(i)
        return indices
```

### Filter by predicate (greater than)

```aicl
Behavior FilterGreaterThan
    Input: nums, threshold
    Output: result
    Action:
        result = []
        for n in nums:
            if n > threshold:
                result.append(n)
        return result
```

### Take / Drop

```aicl
Behavior Take
    Input: items, n
    Output: result
    Action:
        if n >= len(items):
            return items
        return items[:n]

Behavior Drop
    Input: items, n
    Output: result
    Action:
        if n >= len(items):
            return []
        return items[n:]
```

---

## 8. Text Analysis

### Word count

```aicl
Behavior WordCount
    Input: text
    Output: count
    Action:
        words = text.split()
        return len(words)
```

### Word frequency

```aicl
Behavior WordFrequencies
    Input: text
    Output: counts
    Action:
        words = text.split()
        counts = {}
        for word in words:
            word = word.lower().strip()
            if len(word) > 0:
                if word in counts:
                    counts[word] = counts[word] + 1
                else:
                    counts[word] = 1
        return counts
```

### Find longest word

```aicl
Behavior LongestWord
    Input: text
    Output: longest
    Action:
        words = text.split()
        longest = ""
        for word in words:
            if len(word) > len(longest):
                longest = word
        return longest
```

### Sentence count

```aicl
Behavior CountSentences
    Input: text
    Output: count
    Action:
        count = 0
        for char in text:
            if char == "." or char == "!" or char == "?":
                count = count + 1
        return count
```

### Extract hashtags

```aicl
Behavior ExtractHashtags
    Input: text
    Output: tags
    Action:
        words = text.split()
        tags = []
        for word in words:
            if len(word) > 1 and word[0] == "#":
                tags.append(word[1:])
        return tags
```

---

## 9. CRUD Applications

### Contact book

```aicl
Goal:
Manage contacts

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

Behavior Remove
    Input: book, name
    Output: ok
    Action:
        if name in book:
            del book[name]
            return true
        return false

Behavior ListAll
    Input: book
    Output: formatted
    Action:
        lines = []
        for name in sorted(book):
            lines.append(name + ": " + book[name])
        return chr(10).join(lines)
```

### Inventory manager

```aicl
Goal:
Track product inventory

Layer:
Inventory

Risk:
Negative stock

Recovery:
Reject the operation

Validation:
Stock levels are accurate

Behavior AddStock
    Input: inventory, sku, quantity
    Output: inventory
    Action:
        if sku in inventory:
            inventory[sku] = inventory[sku] + quantity
        else:
            inventory[sku] = quantity
        return inventory

Behavior RemoveStock
    Input: inventory, sku, quantity
    Output: ok
    Action:
        if sku not in inventory:
            return false
        if inventory[sku] < quantity:
            return false
        inventory[sku] = inventory[sku] - quantity
        return true

Behavior LowStock
    Input: inventory, threshold
    Output: items
    Action:
        items = []
        for sku in inventory:
            if inventory[sku] < threshold:
                items.append(sku)
        return items
```

### Simple calculator

```aicl
Goal:
Evaluate arithmetic expressions

Layer:
Calculator

Validation:
Expressions are evaluated correctly

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

---

## 10. Validation

### Email format (basic)

```aicl
Behavior IsValidEmail
    Input: email
    Output: valid
    Action:
        if not email.contains("@"):
            return false
        if not email.contains("."):
            return false
        at_pos = email.find("@")
        if at_pos == 0:
            return false
        if at_pos == len(email) - 1:
            return false
        return true
```

### Password strength

```aicl
Behavior PasswordStrength
    Input: password
    Output: score
    Action:
        score = 0
        if len(password) >= 8:
            score = score + 1
        if len(password) >= 12:
            score = score + 1
        has_upper = false
        has_lower = false
        has_digit = false
        for char in password:
            if char >= "A" and char <= "Z":
                has_upper = true
            elif char >= "a" and char <= "z":
                has_lower = true
            elif char >= "0" and char <= "9":
                has_digit = true
        if has_upper:
            score = score + 1
        if has_lower:
            score = score + 1
        if has_digit:
            score = score + 1
        return score
```

### Range check

```aicl
Behavior InRange
    Input: value, low, high
    Output: ok
    Action:
        if value < low:
            return false
        if value > high:
            return false
        return true
```

### Phone number normalization

```aicl
Behavior NormalizePhone
    Input: phone
    Output: normalized
    Action:
        result = ""
        for char in phone:
            if char >= "0" and char <= "9":
                result = result + char
        if len(result) == 10:
            return "+1" + result
        if len(result) == 11 and result[0] == "1":
            return "+" + result
        return result
```

---

## Combining recipes

Most recipes above are self-contained Behaviors. To build a full application,
combine them in one AICL file:

```aicl
Goal:
Build a text analysis dashboard

Layer:
Analyzer

Risk:
Empty input

Recovery:
Return empty results

Validation:
All metrics are computed

Behavior WordCount
    Input: text
    Output: count
    Action:
        ...

Behavior WordFrequencies
    Input: text
    Output: counts
    Action:
        ...

Behavior LongestWord
    Input: text
    Output: longest
    Action:
        ...

Behavior Analyze
    Input: text
    Output: summary
    Action:
        wc = WordCount(text)
        freq = WordFrequencies(text)
        longest = LongestWord(text)
        summary = "Words: " + str(wc) + ", Longest: " + longest
        return summary
```

Compile and run:

```bash
aicl compile dashboard.aicl --target python
cd output && python3 -c "
from main import BuildTextAnalysisDashboard
app = BuildTextAnalysisDashboard()
print(app._behavior_analyze('the quick brown fox jumps over the lazy dog'))
"
```

---

## See also

- [How to Code in AICL](./how-to-code-in-aicl.md) — tutorial
- [AX Language Reference](./ax-language-reference.md) — grammar
- [Standard Library Reference](./stdlib-reference.md) — builtins
- [Compile Targets](./targets.md) — backend details
