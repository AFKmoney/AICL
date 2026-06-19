"""Lexer for the AICL-Action (AX) sub-language.

Tokenizes AX source into a flat token stream, then post-processes indentation
into INDENT/DEDENT/NEWLINE tokens (Python-style). AX is indentation-sensitive
because it lives inside multi-line ``Action:`` blocks where the body of an
``if``/``while``/``for`` is expressed by indenting it.

Token kinds:
    NAME      identifiers / keywords
    INT       integer literal
    FLOAT     float literal
    STRING    string literal
    OP        operators and punctuation: + - * / // % ** = += ... ( ) [ ] , . : < > <= >= == !=
    NEWLINE   logical end of line
    INDENT    increase in indentation
    DEDENT    decrease in indentation
    EOF       end of input
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List

KEYWORDS = {
    "if", "else", "elif", "while", "for", "in", "return", "break",
    "continue", "and", "or", "not", "true", "false", "none",
}

# multi-char operators must be tried before single-char ones (longest match)
_OPS = [
    "//=", "**=", "==", "!=", "<=", ">=", "//", "**", "+=", "-=",
    "*=", "/=", "%=", "<", ">", "+", "-", "*", "/", "%", "=",
    "(", ")", "[", "]", "{", "}", ",", ".", ":",
]


@dataclass
class Token:
    kind: str        # NAME / INT / FLOAT / STRING / OP / NEWLINE / INDENT / DEDENT / EOF
    value: str
    line: int
    col: int


class AXSyntaxError(Exception):
    """Raised when the AX source cannot be tokenized or parsed."""


def tokenize(source: str) -> List[Token]:
    """Tokenize AX source into a token list with INDENT/DEDENT/NEWLINE.

    ``source`` is the raw Action body (without the leading 'Action:' marker).
    Leading/trailing blank lines are stripped. Tabs are rejected (spaces only).
    """
    if "\t" in source:
        raise AXSyntaxError("AX uses spaces for indentation, not tabs")

    raw_lines = source.split("\n")
    # strip trailing blank lines but keep internal structure
    while raw_lines and raw_lines[-1].strip() == "":
        raw_lines.pop()

    tokens: List[Token] = []
    indent_stack: List[int] = [0]
    paren_depth = 0  # track () [] {} so newlines inside them are ignored

    for lineno, line in enumerate(raw_lines, start=1):
        # Inside open parens, newlines are not logical line ends.
        if paren_depth == 0:
            stripped = line.lstrip()
            if stripped == "" or stripped.startswith("#"):
                continue  # blank or comment line
            indent = len(line) - len(stripped)
        else:
            stripped = line.strip()
            if stripped == "":
                continue
            indent = indent_stack[-1]

        # Handle indentation changes (only at logical line start, outside parens)
        if paren_depth == 0:
            if indent > indent_stack[-1]:
                indent_stack.append(indent)
                tokens.append(Token("INDENT", "", lineno, indent))
            else:
                while indent < indent_stack[-1]:
                    indent_stack.pop()
                    tokens.append(Token("DEDENT", "", lineno, indent))
                if indent != indent_stack[-1]:
                    raise AXSyntaxError(
                        f"line {lineno}: inconsistent indentation (dedent to {indent} "
                        f"but expected one of {indent_stack})"
                    )

        # Tokenize the content of the line
        col = indent
        i = 0
        text = stripped
        while i < len(text):
            c = text[i]

            if c == " ":
                col += 1
                i += 1
                continue

            # comments
            if c == "#":
                break

            # numbers (int or float)
            if c.isdigit():
                j = i
                while j < len(text) and text[j].isdigit():
                    j += 1
                is_float = False
                if j < len(text) and text[j] == "." and j + 1 < len(text) and text[j + 1].isdigit():
                    is_float = True
                    j += 1
                    while j < len(text) and text[j].isdigit():
                        j += 1
                lexeme = text[i:j]
                tokens.append(Token("FLOAT" if is_float else "INT", lexeme, lineno, col))
                col += j - i
                i = j
                continue

            # strings (single or double quotes)
            if c in ('"', "'"):
                quote = c
                j = i + 1
                buf = []
                while j < len(text) and text[j] != quote:
                    if text[j] == "\\" and j + 1 < len(text):
                        # simple escape pass-through
                        buf.append(text[j])
                        buf.append(text[j + 1])
                        j += 2
                        continue
                    buf.append(text[j])
                    j += 1
                if j >= len(text):
                    raise AXSyntaxError(f"line {lineno}: unterminated string")
                tokens.append(Token("STRING", "".join(buf), lineno, col))
                col += (j + 1 - i)
                i = j + 1
                continue

            # names / keywords
            if c.isalpha() or c == "_":
                j = i
                while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                    j += 1
                lexeme = text[i:j]
                kind = "NAME"  # keywords are NAME tokens with keyword value; parser distinguishes
                tokens.append(Token(kind, lexeme, lineno, col))
                col += j - i
                i = j
                continue

            # operators (longest match)
            matched = None
            for op in _OPS:
                if text.startswith(op, i):
                    matched = op
                    break
            if matched is None:
                raise AXSyntaxError(f"line {lineno}: unexpected character {c!r}")
            tokens.append(Token("OP", matched, lineno, col))
            if matched in ("(", "[", "{"):
                paren_depth += 1
            elif matched in (")", "]", "}"):
                if paren_depth > 0:
                    paren_depth -= 1
            col += len(matched)
            i += len(matched)

        # logical newline (only when not inside parens)
        if paren_depth == 0:
            tokens.append(Token("NEWLINE", "", lineno, col))

    # close any remaining open indents at EOF
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "", lineno if raw_lines else 1, 0))

    tokens.append(Token("EOF", "", -1, 0))
    return tokens
