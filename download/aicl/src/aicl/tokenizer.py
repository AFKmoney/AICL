"""
AICL Tokenizer - Lexical Analysis (Line-Based)

Converts AICL source code into a stream of tokens using a line-based
approach that correctly handles the AICL format where values appear
on the line AFTER their keyword header.

AICL Format:
    Keyword:
    Value on next line

    OR

    Keyword: Value on same line
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for the AICL language."""
    # Keywords - Section Headers
    GOAL = auto()
    CONSTRAINT = auto()
    RISK = auto()
    RECOVERY = auto()
    LAYER = auto()
    SUBLAYER = auto()
    VALIDATION = auto()
    ENTITY = auto()
    BEHAVIOR = auto()
    CONDITION = auto()
    WHEN = auto()
    THEN = auto()
    EVENT = auto()
    ON = auto()
    ACTION = auto()
    INPUT = auto()
    OUTPUT = auto()
    PARALLEL = auto()
    OPTIMIZE = auto()
    PRIORITY = auto()
    LEARN = auto()
    ADAPT = auto()
    BASED_ON = auto()
    SECURITY = auto()
    ENCRYPT = auto()
    PROTECT = auto()
    NATIVE = auto()

    # Structural tokens
    COLON = auto()
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()

    # Value tokens
    IDENTIFIER = auto()
    STRING_VALUE = auto()
    TYPE_NAME = auto()
    INTEGER_VALUE = auto()
    FLOAT_VALUE = auto()

    # Special
    LBRACE = auto()
    RBRACE = auto()
    COMPARISON = auto()
    EOF = auto()


# Mapping of keyword strings to token types
KEYWORDS = {
    "Goal": TokenType.GOAL,
    "Constraint": TokenType.CONSTRAINT,
    "Risk": TokenType.RISK,
    "Recovery": TokenType.RECOVERY,
    "Layer": TokenType.LAYER,
    "Sublayer": TokenType.SUBLAYER,
    "Validation": TokenType.VALIDATION,
    "Entity": TokenType.ENTITY,
    "Behavior": TokenType.BEHAVIOR,
    "Condition": TokenType.CONDITION,
    "When": TokenType.WHEN,
    "Then": TokenType.THEN,
    "Event": TokenType.EVENT,
    "On": TokenType.ON,
    "Action": TokenType.ACTION,
    "Input": TokenType.INPUT,
    "Output": TokenType.OUTPUT,
    "Parallel": TokenType.PARALLEL,
    "Optimize": TokenType.OPTIMIZE,
    "Priority": TokenType.PRIORITY,
    "Learn": TokenType.LEARN,
    "Adapt": TokenType.ADAPT,
    "Based": TokenType.BASED_ON,
    "Security": TokenType.SECURITY,
    "Encrypt": TokenType.ENCRYPT,
    "Protect": TokenType.PROTECT,
    "Native": TokenType.NATIVE,
}

# Built-in type names
TYPE_NAMES = {
    "string", "integer", "float", "boolean",
    "datetime", "list", "dict", "set", "any",
    "void", "bytes",
}


@dataclass
class Token:
    """Represents a single token in the AICL source code."""
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


class TokenizerError(Exception):
    """Raised when the tokenizer encounters invalid input."""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Tokenizer error at line {line}, column {column}: {message}")


class Tokenizer:
    """
    AICL line-based lexical analyzer.

    Processes AICL source code line by line, producing tokens that
    correctly represent the AICL format where values appear on the
    line after their keyword header.

    Usage:
        tokenizer = Tokenizer(source_code)
        tokens = tokenizer.tokenize()
    """

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.indent_stack: List[int] = [0]

    def _make_token(self, type: TokenType, value: str, line: int, column: int = 1) -> Token:
        """Create a token."""
        return Token(type=type, value=value, line=line, column=column)

    def _count_indent(self, line: str) -> int:
        """Count the indentation level of a line (spaces and tabs)."""
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += 4
            else:
                break
        return indent

    def _parse_line_tokens(self, line: str, line_num: int) -> List[Token]:
        """Parse a single line into tokens."""
        tokens = []
        stripped = line.strip()

        if not stripped or stripped.startswith('#'):
            return tokens

        # Split the line into words
        words = stripped.split()
        pos = 0

        for i, word in enumerate(words):
            # Find the column position
            col = stripped.find(word, pos) + 1
            pos = col + len(word)

            # Check for keyword
            if word in KEYWORDS:
                tokens.append(self._make_token(KEYWORDS[word], word, line_num, col))

                # Check if colon follows this keyword (same word or next)
                if word.endswith(':'):
                    tokens.append(self._make_token(TokenType.COLON, ':', line_num, col + len(word) - 1))
                elif i + 1 < len(words) and words[i + 1] == ':':
                    tokens.append(self._make_token(TokenType.COLON, ':', line_num, col + len(word)))
                elif i + 1 < len(words) and words[i + 1].endswith(':'):
                    # Handle "Keyword:" (no space before colon)
                    pass

                # After keyword + colon, the rest is a string value
                rest_start = stripped.find(':', stripped.find(word)) + 1
                if rest_start > 0 and rest_start < len(stripped):
                    rest_value = stripped[rest_start:].strip()
                    if rest_value:
                        tokens.append(self._make_token(TokenType.STRING_VALUE, rest_value, line_num, rest_start + 1))
                break  # Rest of line captured as STRING_VALUE

            elif word in TYPE_NAMES:
                tokens.append(self._make_token(TokenType.TYPE_NAME, word, line_num, col))

            elif word == ':':
                tokens.append(self._make_token(TokenType.COLON, ':', line_num, col))
                # Capture rest of line as string value
                colon_pos = stripped.find(':', pos - len(word) - 1)
                rest_start = colon_pos + 1
                if rest_start < len(stripped):
                    rest_value = stripped[rest_start:].strip()
                    if rest_value:
                        tokens.append(self._make_token(TokenType.STRING_VALUE, rest_value, line_num, rest_start + 1))
                break

            elif word.endswith(':') and word[:-1] in KEYWORDS:
                # "Goal:" as single token
                keyword = word[:-1]
                tokens.append(self._make_token(KEYWORDS[keyword], keyword, line_num, col))
                tokens.append(self._make_token(TokenType.COLON, ':', line_num, col + len(keyword)))
                # Rest of line
                rest_start = stripped.find(':', col) + 1
                if rest_start < len(stripped):
                    rest_value = stripped[rest_start:].strip()
                    if rest_value:
                        tokens.append(self._make_token(TokenType.STRING_VALUE, rest_value, line_num, rest_start + 1))
                break

            elif word.endswith(':') and i == 0:
                # Unknown keyword with colon
                keyword = word[:-1]
                tokens.append(self._make_token(TokenType.IDENTIFIER, keyword, line_num, col))
                tokens.append(self._make_token(TokenType.COLON, ':', line_num, col + len(keyword)))
                # Rest of line
                rest_start = stripped.find(':', col) + 1
                if rest_start < len(stripped):
                    rest_value = stripped[rest_start:].strip()
                    if rest_value:
                        tokens.append(self._make_token(TokenType.STRING_VALUE, rest_value, line_num, rest_start + 1))
                break

            elif word.startswith('{'):
                tokens.append(self._make_token(TokenType.LBRACE, '{', line_num, col))
                # Capture everything between braces as native code
                brace_start = stripped.find('{')
                brace_end = stripped.rfind('}')
                if brace_end > brace_start:
                    native_code = stripped[brace_start + 1:brace_end].strip()
                    if native_code:
                        tokens.append(self._make_token(TokenType.STRING_VALUE, native_code, line_num, brace_start + 2))
                    tokens.append(self._make_token(TokenType.RBRACE, '}', line_num, brace_end + 1))

            elif word.endswith('}'):
                tokens.append(self._make_token(TokenType.RBRACE, '}', line_num, col))

            elif word[0].isdigit() or (word[0] == '-' and len(word) > 1 and word[1].isdigit()):
                # Number
                if '.' in word:
                    tokens.append(self._make_token(TokenType.FLOAT_VALUE, word, line_num, col))
                else:
                    tokens.append(self._make_token(TokenType.INTEGER_VALUE, word, line_num, col))

            elif word in ('>', '<', '>=', '<=', '==', '!='):
                tokens.append(self._make_token(TokenType.COMPARISON, word, line_num, col))

            else:
                # Regular identifier or type name
                clean_word = word.rstrip('.,;:')
                if clean_word in TYPE_NAMES:
                    tokens.append(self._make_token(TokenType.TYPE_NAME, clean_word, line_num, col))
                else:
                    tokens.append(self._make_token(TokenType.IDENTIFIER, clean_word, line_num, col))

        return tokens

    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire source code and return a list of tokens.

        Uses a line-based approach:
        1. Split source into lines
        2. For each line, determine indentation level and content
        3. Emit INDENT/DEDENT tokens based on indentation changes
        4. Parse each line into tokens

        Returns:
            List of Token objects representing the tokenized source.
        """
        lines = self.source.split('\n')
        prev_indent = 0

        i = 0
        while i < len(lines):
            line = lines[i]
            line_num = i + 1

            # Count indentation
            indent = self._count_indent(line)
            stripped = line.strip()

            # Skip blank lines and comments
            if not stripped or stripped.startswith('#'):
                i += 1
                continue

            # Emit INDENT/DEDENT tokens
            if indent > prev_indent:
                self.tokens.append(self._make_token(TokenType.INDENT, str(indent), line_num))
                self.indent_stack.append(indent)
            elif indent < prev_indent:
                while self.indent_stack[-1] > indent:
                    self.indent_stack.pop()
                    self.tokens.append(self._make_token(TokenType.DEDENT, '', line_num))

            prev_indent = indent

            # Parse this line into tokens
            line_tokens = self._parse_line_tokens(line, line_num)
            self.tokens.extend(line_tokens)

            # Check if the next line is a value line (no keyword, just text)
            # This handles the "Keyword:\nValue" pattern
            if line_tokens and line_tokens[-1].type == TokenType.COLON:
                # Look ahead: if the next non-blank line has the same or greater indent
                # and doesn't start with a keyword, it's a value line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    next_line = lines[j].strip()
                    next_indent = self._count_indent(lines[j])
                    # Check if the next line is NOT a keyword line
                    first_word = next_line.split()[0] if next_line.split() else ''
                    first_word_clean = first_word.rstrip(':')
                    if first_word_clean not in KEYWORDS and next_indent >= indent:
                        # This is a value line
                        value = next_line
                        self.tokens.append(self._make_token(
                            TokenType.STRING_VALUE, value, j + 1
                        ))
                        # Skip the value line and handle its indent
                        i = j  # Will be incremented at end of loop

            # Add newline between sections
            self.tokens.append(self._make_token(TokenType.NEWLINE, '\\n', line_num))

            i += 1

        # Emit remaining DEDENT tokens
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(self._make_token(TokenType.DEDENT, '', len(lines)))

        # Emit EOF
        self.tokens.append(self._make_token(TokenType.EOF, '', len(lines)))

        return self.tokens
