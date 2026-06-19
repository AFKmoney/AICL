#!/usr/bin/env python3
"""
CogNetAICL corpus generator.

Produces a plain-text corpus for fine-tuning CogNet on AICL: given a library
of algorithm templates written in the AX sub-language, generates spec->code
documents and concatenates them into a single .raw file that the CogNet
train_pipeline.py can consume directly (char-level, seq_len 2048).

Format of each document in the corpus:

    ### AICL EXAMPLE: <name>
    === SPEC ===
    <spec.aicl source>
    === PYTHON ===
    <generated main.py>

Why plain text and not JSONL: CogNet is a character-level language model. It
learns the distribution of characters across the whole corpus. Exposing it to
spec source immediately followed by the compiled Python teaches it the
spec->code mapping as a character-level translation pattern.

Usage:
    py corpus_generator.py --out corpus/aicl_corpus.raw
    py corpus_generator.py --out corpus/aicl_corpus.raw --targets python rust
"""

from __future__ import annotations
import argparse
import os
import sys
import textwrap
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aicl.compiler import Compiler


# ---------------------------------------------------------------------------
# Algorithm templates written in AX.
#
# Each template is a complete .aicl spec whose Action: uses the AX sub-language.
# These are the "curriculum" CogNet learns from. Cover distinct language
# features: loops, recursion, conditionals, arithmetic, swaps, method calls.
# ---------------------------------------------------------------------------

@dataclass
class AlgoTemplate:
    name: str
    spec: str           # full .aicl source with AX Action:
    features: List[str] = field(default_factory=list)  # language features exercised


TEMPLATES: List[AlgoTemplate] = [

    AlgoTemplate(
        name="bubble_sort",
        features=["nested for", "swap", "comparison"],
        spec=textwrap.dedent("""\
            Goal:
            Sort an array of integers in ascending order using bubble sort

            Risk:
            Empty array

            Recovery:
            Return an empty array

            Layer:
            Sorting

            Validation:
            Output array is sorted in non-decreasing order

            Behavior Sort
                Input: array
                Output: array
                Action:
                    n = len(array)
                    for i in range(0, n):
                        for j in range(0, n - i - 1):
                            if array[j] > array[j + 1]:
                                array[j], array[j + 1] = array[j + 1], array[j]
                    return array
        """)),

    AlgoTemplate(
        name="linear_search",
        features=["while", "return inside loop", "comparison"],
        spec=textwrap.dedent("""\
            Goal:
            Find the index of a target value in an array via linear search

            Risk:
            Target not found

            Recovery:
            Return -1

            Layer:
            Search

            Validation:
            Returned index points to the target, or -1

            Behavior Search
                Input: array, target
                Output: index
                Action:
                    i = 0
                    while i < len(array):
                        if array[i] == target:
                            return i
                        i = i + 1
                    return -1
        """)),

    AlgoTemplate(
        name="sum_range",
        features=["for", "accumulator", "arithmetic"],
        spec=textwrap.dedent("""\
            Goal:
            Compute the sum of all integers from 0 to n exclusive

            Constraint:
            n is a non-negative integer

            Layer:
            Arithmetic

            Validation:
            Result equals n * (n - 1) / 2

            Behavior Sum
                Input: n
                Output: total
                Action:
                    total = 0
                    for i in range(0, n):
                        total = total + i
                    return total
        """)),

    AlgoTemplate(
        name="count_vowels",
        features=["for-in string", "if/elif/else", "augmented assign"],
        spec=textwrap.dedent("""\
            Goal:
            Count the number of vowels in a string

            Layer:
            Text

            Validation:
            Result is the count of a, e, i, o, u (case insensitive)

            Behavior Count
                Input: text
                Output: count
                Action:
                    count = 0
                    for ch in text:
                        if ch == "a":
                            count = count + 1
                        elif ch == "e":
                            count = count + 1
                        elif ch == "i":
                            count = count + 1
                        elif ch == "o":
                            count = count + 1
                        elif ch == "u":
                            count = count + 1
                    return count
        """)),

    AlgoTemplate(
        name="power_iterative",
        features=["while", "accumulator", "multiplication"],
        spec=textwrap.dedent("""\
            Goal:
            Compute base raised to the power of exponent iteratively

            Constraint:
            Exponent is a non-negative integer

            Layer:
            Arithmetic

            Validation:
            Result equals base multiplied by itself exponent times

            Behavior Power
                Input: base, exponent
                Output: result
                Action:
                    result = 1
                    while exponent > 0:
                        result = result * base
                        exponent = exponent - 1
                    return result
        """)),

    AlgoTemplate(
        name="max_of_array",
        features=["for", "if", "comparison"],
        spec=textwrap.dedent("""\
            Goal:
            Find the maximum value in a non-empty array of integers

            Risk:
            Empty array

            Recovery:
            Return 0

            Layer:
            Reduction

            Validation:
            Result is greater than or equal to every element

            Behavior Max
                Input: array
                Output: maximum
                Action:
                    maximum = array[0]
                    for i in range(1, len(array)):
                        if array[i] > maximum:
                            maximum = array[i]
                    return maximum
        """)),

    AlgoTemplate(
        name="reverse_array",
        features=["while", "swap", "two-pointer"],
        spec=textwrap.dedent("""\
            Goal:
            Reverse an array in place

            Layer:
            Transformation

            Validation:
            Output is the input reversed

            Behavior Reverse
                Input: array
                Output: array
                Action:
                    left = 0
                    right = len(array) - 1
                    while left < right:
                        array[left], array[right] = array[right], array[left]
                        left = left + 1
                        right = right - 1
                    return array
        """)),

    AlgoTemplate(
        name="is_even",
        features=["modulo", "if/else", "boolean return"],
        spec=textwrap.dedent("""\
            Goal:
            Determine whether an integer is even

            Layer:
            Arithmetic

            Validation:
            Returns true for even numbers, false otherwise

            Behavior Check
                Input: n
                Output: result
                Action:
                    if n % 2 == 0:
                        return true
                    else:
                        return false
        """)),

    AlgoTemplate(
        name="gcd_euclid",
        features=["while", "modulo", "swap/reassign"],
        spec=textwrap.dedent("""\
            Goal:
            Compute the greatest common divisor of two integers using Euclid's algorithm

            Layer:
            Arithmetic

            Validation:
            Result is the GCD of the two inputs

            Behavior Gcd
                Input: a, b
                Output: result
                Action:
                    while b != 0:
                        temp = b
                        b = a % b
                        a = temp
                    return a
        """)),

    AlgoTemplate(
        name="fibonacci_iterative",
        features=["for", "multiple assigns", "arithmetic"],
        spec=textwrap.dedent("""\
            Goal:
            Compute the nth Fibonacci number iteratively

            Constraint:
            n is a non-negative integer

            Layer:
            Sequence

            Validation:
            Result is the nth Fibonacci number

            Behavior Fib
                Input: n
                Output: result
                Action:
                    if n <= 1:
                        return n
                    prev = 0
                    curr = 1
                    for i in range(2, n):
                        next = prev + curr
                        prev = curr
                        curr = next
                    return curr
        """)),
]


def sanitize_for_tokenizer(text: str) -> str:
    """Replace characters outside the CogNet CharTokenizer vocab.

    The tokenizer covers printable ASCII + accented chars + tab/newline.
    The AICL scaffolding emits a few non-ASCII glyphs (arrows, dashes) that
    would be dropped on encode. Substitute them with ASCII equivalents so the
    corpus round-trips losslessly.
    """
    replacements = {
        "\u2192": "->",   # rightwards arrow
        "\u2014": "--",   # em dash
        "\u2013": "-",    # en dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text


def build_document(template: AlgoTemplate, targets: List[str]) -> str:
    """Build a single corpus document: spec + generated code for each target.

    Each document teaches CogNet that the spec maps to the generated code.
    """
    parts = [f"### AICL EXAMPLE: {template.name}\n"]
    parts.append("=== SPEC ===")
    parts.append(template.spec.rstrip())
    parts.append("")

    compiler = Compiler()
    for target in targets:
        try:
            result = compiler.compile(template.spec, target_language=target) \
                if "target_language" in Compiler.compile.__code__.co_varnames \
                else _compile_with_target(template.spec, target)
            code = result.source_code if hasattr(result, "source_code") else str(result)
            label = {"python": "PYTHON", "javascript": "JAVASCRIPT",
                     "rust": "RUST", "go": "GO"}.get(target, target.upper())
            parts.append(f"=== {label} ===")
            parts.append(sanitize_for_tokenizer(code).rstrip())
            parts.append("")
        except Exception as e:
            # If a target fails to compile, skip it rather than poison the corpus.
            parts.append(f"=== {target.upper()} (compile failed: {e}) ===")
            parts.append("")

    return "\n".join(parts) + "\n\n"


def _compile_with_target(spec: str, target: str):
    """Compile with a specific target language."""
    c = Compiler(target_language=target)
    return c.compile(spec)


def generate_corpus(out_path: str, targets: List[str], verbose: bool = True) -> int:
    """Generate the full corpus and write it to out_path. Returns char count."""
    documents = []
    for template in TEMPLATES:
        if verbose:
            features = ", ".join(template.features)
            print(f"  [{len(documents)+1}/{len(TEMPLATES)}] {template.name:24} ({features})")
        documents.append(build_document(template, targets))

    corpus = "".join(documents)
    corpus = sanitize_for_tokenizer(corpus)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(corpus)
    if verbose:
        print(f"\n[done] {len(TEMPLATES)} documents, {len(corpus):,} chars -> {out_path}")
        print(f"       approx {len(corpus) // 2048 + 1} sequences at seq_len=2048")
    return len(corpus)


def main():
    parser = argparse.ArgumentParser(description="Generate the CogNetAICL training corpus.")
    parser.add_argument("--out", default="corpus/aicl_corpus.raw",
                        help="output path (default: corpus/aicl_corpus.raw)")
    parser.add_argument("--targets", nargs="+", default=["python"],
                        choices=["python", "javascript", "rust", "go"],
                        help="compile targets to include in the corpus")
    args = parser.parse_args()
    generate_corpus(args.out, args.targets)


if __name__ == "__main__":
    main()
