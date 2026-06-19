"""
AICL Parser - Direct Line-Based Parsing

Parses AICL source code directly into an AST using a line-based approach.
This is more reliable for AICL's format where values can appear on the
same line as the keyword or on the following line.

AICL Format:
    Keyword: Value on same line
    Keyword:
    Value on next line
"""

from typing import List, Optional, Tuple

from .ast import (
    AICLProgram, GoalSection, ConstraintSection, RiskSection,
    RecoverySection, LayerSection, ValidationSection, EntitySection,
    BehaviorSection, ConditionSection, EventSection, ParallelSection,
    OptimizeSection, LearnSection, AdaptSection, SecuritySection,
    NativeSection, EntityField, BehaviorInput, BehaviorOutput,
    SecurityAction,
)


# All AICL keywords (case-sensitive)
KEYWORDS = {
    'Goal', 'Constraint', 'Risk', 'Recovery', 'Layer', 'Sublayer',
    'Validation', 'Entity', 'Behavior', 'Condition', 'When', 'Then',
    'Event', 'On', 'Action', 'Input', 'Output', 'Parallel',
    'Optimize', 'Priority', 'Learn', 'Adapt', 'Based',
    'Security', 'Encrypt', 'Protect', 'Native',
}

# Type names
TYPE_NAMES = {
    'string', 'integer', 'float', 'boolean', 'datetime',
    'list', 'dict', 'set', 'any', 'void', 'bytes',
}


class ParseError(Exception):
    """Raised when the parser encounters invalid syntax."""

    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"Parse error at line {line}: {message}" if line else f"Parse error: {message}")


class Parser:
    """
    AICL line-based parser.

    Parses AICL source code into an AICLProgram AST using a direct
    line-by-line approach that correctly handles AICL's format.

    Usage:
        parser = Parser(source_code)
        program = parser.parse()
    """

    def __init__(self, source: str):
        self.lines = source.split('\n')
        self.pos = 0  # Current line index

    def _current_line(self) -> Optional[str]:
        """Get the current line without advancing."""
        if self.pos < len(self.lines):
            return self.lines[self.pos]
        return None

    def _advance(self) -> Optional[str]:
        """Advance to the next line and return it."""
        if self.pos < len(self.lines):
            line = self.lines[self.pos]
            self.pos += 1
            return line
        return None

    def _peek_next(self) -> Optional[str]:
        """Look at the next line without advancing."""
        if self.pos + 1 < len(self.lines):
            return self.lines[self.pos + 1]
        return None

    def _count_indent(self, line: str) -> int:
        """Count the indentation level of a line."""
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += 4
            else:
                break
        return indent

    def _is_blank_or_comment(self, line: str) -> bool:
        """Check if a line is blank or a comment."""
        stripped = line.strip()
        return not stripped or stripped.startswith('#')

    def _skip_blank_lines(self) -> None:
        """Skip blank lines and comments."""
        while self.pos < len(self.lines) and self._is_blank_or_comment(self.lines[self.pos]):
            self.pos += 1

    def _parse_keyword_line(self, line: str) -> Optional[Tuple[str, str, int]]:
        """
        Parse a line that starts with a keyword.

        Returns (keyword, value, indent) or None if not a keyword line.
        Handles:
            Keyword: Value          (same line, with colon)
            Keyword:                (next line value, with colon)
            Keyword Value           (same line, no colon - for Entity, Behavior)
        """
        stripped = line.strip()
        indent = self._count_indent(line)

        if not stripped:
            return None

        # Get the first word
        words = stripped.split()
        if not words:
            return None

        first_word = words[0].rstrip(':')

        # Check if first word is a keyword
        if first_word not in KEYWORDS:
            return None

        # Case 1: "Keyword: Value" or "Keyword:" (with colon)
        colon_pos = stripped.find(':')
        if colon_pos != -1:
            keyword_part = stripped[:colon_pos].strip()
            value_part = stripped[colon_pos + 1:].strip()
            if keyword_part in KEYWORDS:
                return (keyword_part, value_part, indent)

        # Case 2: "Keyword Value" (no colon - for Entity, Behavior, etc.)
        if len(words) >= 2:
            value_part = ' '.join(words[1:])
            return (first_word, value_part, indent)

        # Case 3: "Keyword" alone (no value, no colon)
        return (first_word, '', indent)

    def _read_value_line(self, base_indent: int) -> str:
        """
        Read a value from the next line if the current keyword line
        had no value on the same line.

        The value can be at the same indent level or greater, as long
        as the next line doesn't start with a known AICL keyword.
        """
        self._skip_blank_lines()

        if self.pos >= len(self.lines):
            return ""

        next_line = self.lines[self.pos]
        next_indent = self._count_indent(next_line)
        next_stripped = next_line.strip()

        if not next_stripped:
            return ""

        # The next line is a value line if:
        # 1. It's at the same or greater indent level than the keyword
        # 2. It doesn't look like a new section (Keyword: or Keyword Value
        #    where Keyword is a section header, not just any keyword)
        # We only reject lines that clearly start a new section:
        #   - "Keyword:" (keyword followed by colon)
        #   - "Keyword Name" for keywords that take name args (Entity, Behavior)
        colon_pos = next_stripped.find(':')
        first_word = next_stripped.split()[0].rstrip(':')

        # Check if this looks like a new section header
        is_section_header = False
        if colon_pos == len(first_word) and first_word in KEYWORDS:
            # "Keyword:" format - this is a new section
            is_section_header = True
        elif first_word in ('Entity', 'Behavior') and len(next_stripped.split()) >= 2:
            # "Entity Name" or "Behavior Name" format
            is_section_header = True

        if next_indent >= base_indent and not is_section_header:
            self.pos += 1
            return next_stripped

        return ""

    def _read_indented_block(self, base_indent: int) -> List[Tuple[str, str, int]]:
        """
        Read an indented block of keyword-value pairs.

        Returns a list of (keyword, value, indent) tuples.
        """
        block = []
        self._skip_blank_lines()

        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            if self._is_blank_or_comment(line):
                self.pos += 1
                continue

            indent = self._count_indent(line)
            if indent <= base_indent:
                break

            parsed = self._parse_keyword_line(line)
            if parsed:
                keyword, value, kw_indent = parsed
                self.pos += 1

                # If no value on same line, read from next line
                if not value:
                    value = self._read_value_line(kw_indent)

                block.append((keyword, value, kw_indent))
            else:
                # Not a keyword line; might be a plain value
                stripped = line.strip()
                block.append(('__value__', stripped, indent))
                self.pos += 1

        return block

    def parse(self) -> AICLProgram:
        """
        Parse the entire AICL source code into an AICLProgram AST.

        Returns:
            AICLProgram AST node representing the entire program.

        Raises:
            ParseError: If the source code does not conform to AICL syntax.
        """
        program = AICLProgram()

        while self.pos < len(self.lines):
            self._skip_blank_lines()
            if self.pos >= len(self.lines):
                break

            line = self.lines[self.pos]
            parsed = self._parse_keyword_line(line)

            if parsed is None:
                # Skip unrecognized lines
                self.pos += 1
                continue

            keyword, value, indent = parsed
            self.pos += 1

            # Only read value from next line for keywords that take simple text values.
            # Keywords with structured bodies (Condition, Event, Layer, Entity,
            # Behavior, Security, Parallel, Learn, Adapt, Native) handle their
            # own sub-parsing via _read_indented_block.
            SIMPLE_VALUE_KEYWORDS = {
                'Goal', 'Constraint', 'Risk', 'Recovery',
                'Validation', 'Optimize', 'Priority',
            }

            if not value and keyword in SIMPLE_VALUE_KEYWORDS:
                value = self._read_value_line(indent)

            self._dispatch_keyword(keyword, value, indent, program)

        return program

    def _dispatch_keyword(self, keyword: str, value: str, indent: int, program: AICLProgram) -> None:
        """Dispatch a keyword to the appropriate parsing method."""

        # Level 1 - Architecture
        if keyword == 'Goal':
            program.goals.append(GoalSection(description=value))
        elif keyword == 'Constraint':
            program.constraints.append(ConstraintSection(description=value))
        elif keyword == 'Risk':
            program.risks.append(RiskSection(description=value))
        elif keyword == 'Recovery':
            program.recoveries.append(RecoverySection(description=value))
        elif keyword == 'Layer':
            self._parse_layer(value, indent, program)
        elif keyword == 'Sublayer':
            # Sublayer at top level - shouldn't happen but handle gracefully
            if program.layers:
                program.layers[-1].sublayers.append(LayerSection(name=value))
        elif keyword == 'Validation':
            program.validations.append(ValidationSection(description=value))

        # Level 2 - Entities
        elif keyword == 'Entity':
            self._parse_entity(value, indent, program)

        # Level 3 - Behaviors
        elif keyword == 'Behavior':
            self._parse_behavior(value, indent, program)

        # Level 4 - Conditions
        elif keyword == 'Condition':
            self._parse_condition(value, indent, program)

        # Level 5 - Events
        elif keyword == 'Event':
            self._parse_event(value, indent, program)

        # Level 6 - Concurrency
        elif keyword == 'Parallel':
            self._parse_parallel(value, indent, program)

        # Level 7 - Optimization
        elif keyword == 'Optimize':
            program.optimizations.append(OptimizeSection(target=value))
        elif keyword == 'Priority':
            program.optimizations.append(OptimizeSection(target=value))

        # Level 8 - Learning
        elif keyword == 'Learn':
            self._parse_learn(value, indent, program)
        elif keyword == 'Adapt':
            self._parse_adapt(value, indent, program)

        # Level 9 - Security
        elif keyword == 'Security':
            self._parse_security(value, indent, program)

        # Level 10 - Native
        elif keyword == 'Native':
            self._parse_native(value, indent, program)

    # =========================================================================
    # Level 1 - Architecture
    # =========================================================================

    def _parse_layer(self, name: str, indent: int, program: AICLProgram) -> None:
        """Parse a Layer section with optional sublayers."""
        # If no name on the same line, try reading it from the next line
        if not name:
            self._skip_blank_lines()
            if self.pos < len(self.lines):
                next_line = self.lines[self.pos]
                next_stripped = next_line.strip()
                next_indent = self._count_indent(next_line)
                # Value line: same or greater indent, not a section header
                if next_stripped and next_indent >= indent:
                    # Only reject if it's clearly a new section header
                    # (keyword followed by colon, or Entity/Behavior with name)
                    is_section_header = False
                    colon_pos = next_stripped.find(':')
                    first_word = next_stripped.split()[0].rstrip(':')
                    if colon_pos == len(first_word) and first_word in KEYWORDS:
                        is_section_header = True
                    elif first_word in ('Entity', 'Behavior') and len(next_stripped.split()) >= 2:
                        is_section_header = True

                    if not is_section_header:
                        name = next_stripped
                        self.pos += 1

        layer = LayerSection(name=name)

        # Read indented block for sublayers
        block = self._read_indented_block(indent)
        for kw, val, _ in block:
            if kw == 'Sublayer':
                layer.sublayers.append(LayerSection(name=val))

        program.layers.append(layer)

    # =========================================================================
    # Level 2 - Entities
    # =========================================================================

    def _parse_entity(self, name: str, indent: int, program: AICLProgram) -> None:
        """Parse an Entity section with fields."""
        entity = EntitySection(name=name)

        # Read indented block for fields
        block = self._read_indented_block(indent)
        for kw, val, _ in block:
            if kw == '__value__':
                # Field definition: "name: type"
                if ':' in val:
                    field_name, field_type = val.split(':', 1)
                    entity.fields.append(EntityField(
                        name=field_name.strip(),
                        field_type=field_type.strip()
                    ))

        program.entities.append(entity)

    # =========================================================================
    # Level 3 - Behaviors
    # =========================================================================

    def _parse_input_list(self, val: str) -> list:
        """Parse an Input: value into one or more BehaviorInput objects.

        Two formats are supported:
          - "name type"          → single typed input, e.g. Input: player Player
          - "a, b, c"            → comma-separated untyped inputs, e.g. Input: array, low, high
          - "name: type"         → single typed input (colon form)
        Comma-separated items may each optionally carry a type ("a: int, b: int").
        """
        from aicl.ast import BehaviorInput
        val = val.strip()
        if ',' in val:
            # comma-separated form
            inputs = []
            for chunk in val.split(','):
                chunk = chunk.strip()
                if not chunk:
                    continue
                if ':' in chunk:
                    name, _, ptype = chunk.partition(':')
                    inputs.append(BehaviorInput(name=name.strip(), param_type=ptype.strip() or 'any'))
                elif ' ' in chunk:
                    parts = chunk.split(None, 1)
                    inputs.append(BehaviorInput(name=parts[0], param_type=parts[1]))
                else:
                    inputs.append(BehaviorInput(name=chunk, param_type='any'))
            return inputs
        # single item
        if ':' in val:
            name, _, ptype = val.partition(':')
            return [BehaviorInput(name=name.strip(), param_type=ptype.strip() or 'any')]
        parts = val.split()
        if len(parts) >= 2:
            return [BehaviorInput(name=parts[0], param_type=parts[1])]
        return [BehaviorInput(name=parts[0] if parts else val, param_type='any')]

    def _parse_behavior(self, name: str, indent: int, program: AICLProgram) -> None:
        """Parse a Behavior section.

        Behaviors can have their sub-sections (Input, Output, Action) either:
        1. Indented inside the behavior block, OR
        2. At the same indent level following the Behavior declaration

        This method handles both formats.
        """
        behavior = BehaviorSection(name=name)

        # Try reading indented block first
        block = self._read_indented_block(indent)

        # If no indented block, read subsequent same-level keywords
        # (Input, Output, Action at the same indent level as Behavior)
        if not block:
            block = self._read_behavior_flat_block(indent)

        i = 0
        while i < len(block):
            kw, val, kw_indent = block[i]

            if kw == 'Input':
                # Parse input parameters.
                # Supports two formats:
                #   Input: name type              (single, typed)
                #   Input: name1, name2, name3    (comma-separated, type 'any')
                if val:
                    for inp in self._parse_input_list(val):
                        behavior.inputs.append(inp)
                # Check if next line(s) are plain values (multi-line input)
                while i + 1 < len(block) and block[i + 1][0] == '__value__':
                    i += 1
                    extra_val = block[i][1].strip()
                    if extra_val:
                        for inp in self._parse_input_list(extra_val):
                            behavior.inputs.append(inp)

            elif kw == 'Output':
                if val:
                    parts = val.strip().split()
                    if len(parts) >= 2:
                        behavior.output = BehaviorOutput(name=parts[0], output_type=parts[1])
                    elif len(parts) == 1:
                        behavior.output = BehaviorOutput(name=val, output_type=val)

            elif kw == 'Action':
                # Action may be a single line (prose or one-liner) or a
                # multi-line indented block (the AX sub-language). Collect
                # the inline value plus any following __value__ lines, then
                # normalize indentation: subtract the minimum column so the
                # resulting block starts at column 0 with its internal
                # structure intact (needed for AX's if/while/for bodies).
                #
                # The inline value sits on the 'Action:' keyword line but is
                # logically part of the body, so when a multi-line block
                # follows we treat it as indented one level under the keyword.
                action_raw = []  # (indent, text)
                has_block = i + 1 < len(block) and block[i + 1][0] == '__value__'
                if val:
                    inline_indent = (kw_indent + 4) if has_block else kw_indent
                    action_raw.append((inline_indent, val.strip()))
                while i + 1 < len(block) and block[i + 1][0] == '__value__':
                    i += 1
                    action_raw.append((block[i][2], block[i][1].strip()))
                if action_raw:
                    base = min(ind for ind, _ in action_raw)
                    behavior.action = '\n'.join(
                        ' ' * (ind - base) + txt for ind, txt in action_raw
                    )

            i += 1

        program.behaviors.append(behavior)

    def _read_behavior_flat_block(self, base_indent: int) -> List[Tuple[str, str, int]]:
        """
        Read Behavior sub-sections at the same indent level.

        This handles the format where Input, Output, Action appear
        at the same indent level as the Behavior keyword:
            Behavior MovePaddle
            Input: Player direction string
            Action: Update paddle position
        """
        block = []
        # Keywords that belong to a behavior block
        BEHAVIOR_SUBKEYWORDS = {'Input', 'Output', 'Action'}

        while self.pos < len(self.lines):
            self._skip_blank_lines()
            if self.pos >= len(self.lines):
                break

            line = self.lines[self.pos]
            stripped = line.strip()

            # Check if this line is a behavior sub-keyword
            parsed = self._parse_keyword_line(line)
            if parsed:
                kw, val, indent = parsed
                if kw in BEHAVIOR_SUBKEYWORDS:
                    self.pos += 1
                    # If no value on same line, read from next line
                    if not val:
                        val = self._read_value_line(indent)
                    block.append((kw, val, indent))
                    continue

            # If it's a value line (indented), add it
            line_indent = self._count_indent(line)
            if line_indent > base_indent and stripped and not self._is_blank_or_comment(line):
                self.pos += 1
                block.append(('__value__', stripped, line_indent))
                continue

            # Any other keyword or unindented line ends the block
            break

        return block

    # =========================================================================
    # Level 4 - Conditions
    # =========================================================================

    def _parse_condition(self, value: str, indent: int, program: AICLProgram) -> None:
        """Parse a Condition section with When/Then."""
        when_clause = ""
        then_clause = ""

        # Read indented block
        block = self._read_indented_block(indent)
        for kw, val, _ in block:
            if kw == 'When':
                when_clause = val
            elif kw == 'Then':
                then_clause = val

        # Also try parsing from the value itself if it contains When/Then
        if not when_clause and not then_clause:
            if 'then' in value.lower():
                parts = value.split('then', 1)
                when_part = parts[0].strip()
                then_part = parts[1].strip() if len(parts) > 1 else ""
                if when_part.lower().startswith('when '):
                    when_clause = when_part[5:].strip()
                else:
                    when_clause = when_part
                then_clause = then_part

        program.conditions.append(ConditionSection(
            when_clause=when_clause, then_clause=then_clause
        ))

    # =========================================================================
    # Level 5 - Events
    # =========================================================================

    def _parse_event(self, value: str, indent: int, program: AICLProgram) -> None:
        """Parse an Event section with On/Action."""
        on_clause = ""
        action = ""

        # Read indented block
        block = self._read_indented_block(indent)
        for kw, val, _ in block:
            if kw == 'On':
                on_clause = val
            elif kw == 'Action':
                action = val

        program.events.append(EventSection(on_clause=on_clause, action=action))

    # =========================================================================
    # Level 6 - Concurrency
    # =========================================================================

    def _parse_parallel(self, value: str, indent: int, program: AICLProgram) -> None:
        """Parse a Parallel section."""
        layers = []

        # Read indented block for layer names
        block = self._read_indented_block(indent)
        for kw, val, _ in block:
            if kw == '__value__':
                layers.append(val)
            elif val:
                layers.append(val)

        # Also parse inline value
        if value and not layers:
            layers = [l.strip() for l in value.split(',') if l.strip()]

        program.parallels.append(ParallelSection(layers=layers))

    # =========================================================================
    # Level 8 - Learning
    # =========================================================================

    def _parse_learn(self, value: str, indent: int, program: AICLProgram) -> None:
        """Parse a Learn section."""
        goal = ""

        # Read indented block for Goal
        block = self._read_indented_block(indent)
        for kw, val, _ in block:
            if kw == 'Goal':
                goal = val

        program.learns.append(LearnSection(subject=value, goal=goal))

    def _parse_adapt(self, value: str, indent: int, program: AICLProgram) -> None:
        """Parse an Adapt section."""
        based_on = ""

        # Read indented block for Based
        block = self._read_indented_block(indent)
        for kw, val, _ in block:
            if kw == 'Based':
                based_on = val

        program.adapts.append(AdaptSection(subject=value, based_on=based_on))

    # =========================================================================
    # Level 9 - Security
    # =========================================================================

    def _parse_security(self, value: str, indent: int, program: AICLProgram) -> None:
        """Parse a Security section with Encrypt/Protect."""
        actions = []

        # Read indented block
        block = self._read_indented_block(indent)
        for kw, val, _ in block:
            if kw == 'Encrypt':
                actions.append(SecurityAction(action_type='encrypt', target=val))
            elif kw == 'Protect':
                actions.append(SecurityAction(action_type='protect', target=val))

        program.securities.append(SecuritySection(actions=actions))

    # =========================================================================
    # Level 10 - Native
    # =========================================================================

    def _parse_native(self, value: str, indent: int, program: AICLProgram) -> None:
        """Parse a Native code section."""
        code = ""

        # Read indented block for code
        block = self._read_indented_block(indent)
        code_lines = []
        for kw, val, _ in block:
            code_lines.append(val)
        code = '\n'.join(code_lines)

        program.natives.append(NativeSection(language=value, code=code))
