# CogNet Integration

AICL is the training ground for [CogNet](https://github.com/AFKmoney/CogNet),
a non-transformer language model with O(n) cognitive routing. CogNet is
fine-tuned on a corpus of AICL spec → code pairs so it learns to write
executable code from architectural specifications.

## The pipeline

```
AICL spec (.aicl)  →  corpus_generator  →  training corpus (.raw)
                                              ↓
                                    CogNet fine-tuning
                                              ↓
                                    CogNetAICL model
                                              ↓
                              Generates new AICL specs + code
```

## Corpus generator

The corpus generator (`python/tools/corpus_generator.py`) produces plain-text
training data: each document is an AICL spec followed by its compiled code.
CogNet is character-level, so it learns the spec→code mapping as a character
distribution.

```bash
# Generate Python-only corpus (30 algorithms, 258k chars)
python tools/corpus_generator.py --out corpus/aicl_corpus.raw --targets python

# Generate multi-target corpus (Python + Rust, 305k chars)
python tools/corpus_generator.py --out corpus/aicl_corpus_multitarget.raw --targets python rust
```

### Algorithms in the corpus

30 templates covering: bubble sort, insertion sort, selection sort, quicksort
(Lomuto partition), linear search, binary search, factorial (iterative +
recursive), Fibonacci, GCD (Euclid), prime check, Collatz steps, digit sum,
power of two check, palindrome check, count vowels, string length, sum array,
max/min, second largest, reverse array, array equality, multiplication table,
count down, clamp, absolute value, copy filtered, count occurrences, median
of three.

Each template exercises distinct AX features: nested loops, recursion, while,
if/elif/else chains, method calls, swaps, modulo, boolean returns.

### Corpus format

```
### AICL EXAMPLE: bubble_sort

=== SPEC ===
Goal:
Sort an array of integers...

=== PYTHON ===
"""AICL Generated Application..."""
class SortArrayOfIntegers...
    def _behavior_sort(self, array):
        ...

```

### Tokenizer compatibility

The corpus round-trips losslessly through CogNet's CharTokenizer (printable
ASCII + accented chars). Non-ASCII glyphs in the compiler's output (arrows,
em-dashes) are sanitized to ASCII equivalents automatically.

## Training

CogNet's training pipeline is in the [CogNet repo](https://github.com/AFKmoney/CogNet).
The `cloud_train.py` script handles everything:

```bash
git clone https://github.com/AFKmoney/CogNet.git
cd CogNet
pip install -r requirements_aicl.txt

# Small model (163M params, 8-12 GB VRAM)
python cloud_train.py --steps 5000 --model small

# Full 1B model (24-40 GB VRAM, A100 recommended)
python cloud_train.py --steps 5000 --model 1b

# Multi-target corpus
python cloud_train.py --steps 5000 --model 1b --multitarget
```

See [`CLOUD_TRAINING.md`](https://github.com/AFKmoney/CogNet/blob/main/CLOUD_TRAINING.md)
in the CogNet repo for GPU recommendations, timing estimates, and checkpoint
usage.

## Model sizes

| Flag | Parameters | VRAM | Recommended GPU |
|------|-----------|------|-----------------|
| `--model small` | 163M | 8–12 GB | RTX 3060, T4 |
| `--model 1b` | 1.01B | 24–40 GB | A100 40GB, 2× RTX 4090 |

Both use `seq_len=2048` — the full AICL spec context window.

## After training

```bash
# Generate text from the fine-tuned model
python infer.py --checkpoint checkpoints/cognet_best.pt \
    --prompt "Goal:\nSort an array\n\nBehavior Sort\n    Input: array\n    Action:\n"
```

A successfully fine-tuned model should produce output resembling valid AICL
specifications and compilable Python code.
