#!/usr/bin/env python3
"""
AICL White Paper Generator
Generates a comprehensive academic white paper for the AICL language.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm, inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ━━ Color Palette ━━
ACCENT       = colors.HexColor('#bb4822')
TEXT_PRIMARY  = colors.HexColor('#212325')
TEXT_MUTED    = colors.HexColor('#767c83')
BG_SURFACE   = colors.HexColor('#dce0e5')
BG_PAGE      = colors.HexColor('#edeff1')
TABLE_HEADER_COLOR = ACCENT
TABLE_HEADER_TEXT  = colors.white
TABLE_ROW_EVEN     = colors.white
TABLE_ROW_ODD      = BG_SURFACE

# ━━ Page Setup ━━
PAGE_W, PAGE_H = A4
LEFT_MARGIN = 22 * mm
RIGHT_MARGIN = 22 * mm
TOP_MARGIN = 25 * mm
BOTTOM_MARGIN = 25 * mm
CONTENT_W = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN

# ━━ Register Fonts ━━
_font_dir = '/usr/share/fonts/truetype'
pdfmetrics.registerFont(TTFont('DejaVuSerif', f'{_font_dir}/dejavu/DejaVuSerif.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSerifBold', f'{_font_dir}/dejavu/DejaVuSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Carlito', f'{_font_dir}/english/Carlito-Regular.ttf'))
pdfmetrics.registerFont(TTFont('CarlitoBold', f'{_font_dir}/english/Carlito-Bold.ttf'))
pdfmetrics.registerFont(TTFont('CarlitoItalic', f'{_font_dir}/english/Carlito-Italic.ttf'))
pdfmetrics.registerFont(TTFont('CarlitoBoldItalic', f'{_font_dir}/english/Carlito-BoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', f'{_font_dir}/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', f'{_font_dir}/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansMono', f'{_font_dir}/dejavu/DejaVuSansMono.ttf'))

from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('DejaVuSerif', normal='DejaVuSerif', bold='DejaVuSerifBold')
registerFontFamily('Carlito', normal='Carlito', bold='CarlitoBold', italic='CarlitoItalic', boldItalic='CarlitoBoldItalic')

# ━━ Styles ━━
styles = getSampleStyleSheet()

# Cover styles
cover_title_style = ParagraphStyle(
    'CoverTitle', parent=styles['Title'],
    fontName='DejaVuSerif', fontSize=36, leading=42,
    textColor=TEXT_PRIMARY, alignment=TA_LEFT,
    spaceAfter=8*mm,
)
cover_subtitle_style = ParagraphStyle(
    'CoverSubtitle', parent=styles['Title'],
    fontName='Carlito', fontSize=16, leading=22,
    textColor=TEXT_MUTED, alignment=TA_LEFT,
    spaceAfter=4*mm,
)
cover_meta_style = ParagraphStyle(
    'CoverMeta', parent=styles['Normal'],
    fontName='Carlito', fontSize=11, leading=16,
    textColor=TEXT_MUTED, alignment=TA_LEFT,
)

# Body styles
h1_style = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName='DejaVuSerif', fontSize=22, leading=28,
    textColor=ACCENT, spaceBefore=16*mm, spaceAfter=6*mm,
)
h2_style = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName='DejaVuSerif', fontSize=16, leading=22,
    textColor=TEXT_PRIMARY, spaceBefore=10*mm, spaceAfter=4*mm,
)
h3_style = ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontName='DejaVuSerifBold', fontSize=13, leading=18,
    textColor=TEXT_PRIMARY, spaceBefore=6*mm, spaceAfter=3*mm,
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName='Carlito', fontSize=10.5, leading=16,
    textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY,
    spaceAfter=3*mm, firstLineIndent=0,
)
body_indent_style = ParagraphStyle(
    'BodyIndent', parent=body_style,
    leftIndent=12*mm,
)
code_style = ParagraphStyle(
    'Code', parent=styles['Code'],
    fontName='DejaVuSansMono', fontSize=9, leading=13,
    textColor=colors.HexColor('#333333'),
    backColor=colors.HexColor('#f5f5f5'),
    leftIndent=8*mm, rightIndent=8*mm,
    spaceBefore=3*mm, spaceAfter=3*mm,
    borderPadding=(4, 4, 4, 4),
)
quote_style = ParagraphStyle(
    'Quote', parent=body_style,
    fontName='DejaVuSerif', fontSize=11, leading=17,
    textColor=ACCENT, leftIndent=16*mm, rightIndent=16*mm,
    spaceBefore=5*mm, spaceAfter=5*mm,
    borderWidth=0, borderColor=ACCENT,
)
caption_style = ParagraphStyle(
    'Caption', parent=styles['Normal'],
    fontName='CarlitoItalic', fontSize=9, leading=13,
    textColor=TEXT_MUTED, alignment=TA_CENTER,
    spaceBefore=2*mm, spaceAfter=4*mm,
)
toc_h1_style = ParagraphStyle(
    'TOCH1', parent=styles['Normal'],
    fontName='DejaVuSerifBold', fontSize=12, leading=20,
    textColor=TEXT_PRIMARY, leftIndent=0,
)
toc_h2_style = ParagraphStyle(
    'TOCH2', parent=styles['Normal'],
    fontName='Carlito', fontSize=10.5, leading=18,
    textColor=TEXT_MUTED, leftIndent=8*mm,
)
abstract_style = ParagraphStyle(
    'Abstract', parent=body_style,
    fontName='CarlitoItalic', fontSize=10, leading=15,
    textColor=TEXT_MUTED, leftIndent=10*mm, rightIndent=10*mm,
    spaceBefore=4*mm, spaceAfter=4*mm,
)
footnote_style = ParagraphStyle(
    'Footnote', parent=styles['Normal'],
    fontName='Carlito', fontSize=8, leading=11,
    textColor=TEXT_MUTED,
)

# ━━ Helper Functions ━━
def heading1(text):
    return Paragraph(text, h1_style)

def heading2(text):
    return Paragraph(text, h2_style)

def heading3(text):
    return Paragraph(text, h3_style)

def body(text):
    return Paragraph(text, body_style)

def body_indent(text):
    return Paragraph(text, body_indent_style)

def code(text):
    return Paragraph(text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), code_style)

def quote(text):
    return Paragraph(text, quote_style)

def spacer(h=4*mm):
    return Spacer(1, h)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceBefore=4*mm, spaceAfter=4*mm)

def make_table(data, col_widths=None, header=True):
    """Create a styled table."""
    if col_widths is None:
        col_widths = [CONTENT_W / len(data[0])] * len(data[0])

    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)

    style_cmds = [
        ('FONTNAME', (0, 0), (-1, -1), 'Carlito'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEADING', (0, 0), (-1, -1), 13),
        ('TEXTCOLOR', (0, 0), (-1, -1), TEXT_PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]

    if header:
        style_cmds.extend([
            ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
            ('FONTNAME', (0, 0), (-1, 0), 'CarlitoBold'),
        ])

    for i in range(1 if header else 0, len(data)):
        bg = TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD
        style_cmds.append(('BACKGROUND', (0, i), (-1, i), bg))

    style_cmds.append(('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')))
    t.setStyle(TableStyle(style_cmds))
    return t


def make_callout(title, text, accent=True):
    """Create a callout box."""
    data = [[
        Paragraph(f'<b>{title}</b>', ParagraphStyle('CalloutTitle', parent=body_style, fontName='CarlitoBold', fontSize=10.5, textColor=ACCENT if accent else TEXT_PRIMARY)),
        Paragraph(text, ParagraphStyle('CalloutBody', parent=body_style, fontSize=10, leading=14)),
    ]]
    t = Table(data, colWidths=[35*mm, CONTENT_W - 40*mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (0, 0), 8),
        ('LEFTPADDING', (1, 0), (1, 0), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#faf8f6')),
        ('LINEAFTER', (0, 0), (0, -1), 2, ACCENT if accent else TEXT_MUTED),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0ddd8')),
    ]))
    return t


# ━━ Page Number Handler ━━
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Carlito', 8)
    canvas.setFillColor(TEXT_MUTED)
    page_num = canvas.getPageNumber()
    if page_num > 1:  # Skip page number on cover
        text = f"AICL White Paper v0.3.0  |  Page {page_num}"
        canvas.drawCentredString(PAGE_W / 2, 15 * mm, text)
    canvas.restoreState()


# ━━ Build Document ━━
output_path = '/home/z/my-project/download/aicl/docs/whitepaper.pdf'

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=LEFT_MARGIN,
    rightMargin=RIGHT_MARGIN,
    topMargin=TOP_MARGIN,
    bottomMargin=BOTTOM_MARGIN,
    title='AICL: Architecture as Programming Language',
    author='Philippe-Antoine',
    subject='AICL White Paper - Specification-First Programming Language',
)

story = []

# ══════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════

story.append(Spacer(1, 45*mm))

# Accent line
story.append(HRFlowable(width="40%", thickness=3, color=ACCENT, spaceBefore=0, spaceAfter=8*mm))

story.append(Paragraph('AICL', cover_title_style))
story.append(Paragraph('AI-Centric Language', ParagraphStyle(
    'CoverTitle2', parent=cover_title_style, fontSize=28, leading=34, spaceAfter=12*mm
)))
story.append(Paragraph('Architecture as Programming Language', cover_subtitle_style))
story.append(Spacer(1, 8*mm))
story.append(HRFlowable(width="25%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=12*mm))

story.append(Paragraph('A Specification-First Programming Language<br/>Where Risks Are Syntax and Validations Compile', ParagraphStyle(
    'CoverDesc', parent=cover_meta_style, fontSize=12, leading=18, textColor=TEXT_PRIMARY
)))
story.append(Spacer(1, 30*mm))

story.append(Paragraph('Version 0.3.0', cover_meta_style))
story.append(Paragraph('June 2026', cover_meta_style))
story.append(Paragraph('Philippe-Antoine', cover_meta_style))
story.append(Spacer(1, 6*mm))
story.append(Paragraph('MIT License', ParagraphStyle('CoverLicense', parent=cover_meta_style, fontSize=9)))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════

story.append(heading1('Table of Contents'))
story.append(spacer(4*mm))

toc_data = [
    ('1', 'Introduction', ''),
    ('2', 'The Problem: Architecture as Documentation', ''),
    ('3', 'Design Principles', ''),
    ('4', 'Language Design', ''),
    ('4.1', 'Language Levels', ''),
    ('4.2', 'Formal Grammar', ''),
    ('4.3', 'Type System', ''),
    ('4.4', 'Keyword Reference', ''),
    ('5', 'Compilation Architecture', ''),
    ('5.1', 'Nine-Stage Pipeline', ''),
    ('5.2', 'Architecture Tree IR', ''),
    ('5.3', 'Deterministic Behavior Compilation', ''),
    ('5.4', 'Compilation Provenance', ''),
    ('6', 'Comparative Analysis', ''),
    ('6.1', 'AICL vs Traditional Languages', ''),
    ('6.2', 'AICL vs DSLs and ADLs', ''),
    ('6.3', 'AICL vs AI Code Generation', ''),
    ('7', 'Worked Examples', ''),
    ('7.1', 'Blue Square (Level 1)', ''),
    ('7.2', 'Pong Game (Levels 1-6)', ''),
    ('7.3', 'Chat Application (Levels 1-9)', ''),
    ('7.4', 'Multiplayer Chess (Levels 1-9)', ''),
    ('8', 'Implementation Status', ''),
    ('9', 'Future Directions', ''),
    ('10', 'Conclusion', ''),
    ('', 'References', ''),
]

toc_table_data = []
for num, title, _ in toc_data:
    if num and '.' not in num:
        toc_table_data.append([
            Paragraph(f'<b>{num}</b>', ParagraphStyle('TOCNum', parent=body_style, fontName='CarlitoBold', fontSize=11, textColor=ACCENT)),
            Paragraph(f'<b>{title}</b>', ParagraphStyle('TOCTitle', parent=body_style, fontName='CarlitoBold', fontSize=11)),
        ])
    elif num:
        toc_table_data.append([
            Paragraph(num, ParagraphStyle('TOCNum2', parent=body_style, fontSize=10, textColor=TEXT_MUTED)),
            Paragraph(title, ParagraphStyle('TOCTitle2', parent=body_style, fontSize=10, textColor=TEXT_MUTED)),
        ])
    else:
        toc_table_data.append([
            Paragraph('', body_style),
            Paragraph(f'<b>{title}</b>', ParagraphStyle('TOCTitleR', parent=body_style, fontName='CarlitoBold', fontSize=11, textColor=ACCENT)),
        ])

toc_t = Table(toc_table_data, colWidths=[15*mm, CONTENT_W - 20*mm])
toc_t.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 2),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.HexColor('#e8e6e2')),
]))
story.append(toc_t)

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════
# 1. INTRODUCTION
# ══════════════════════════════════════════════════════════════

story.append(heading1('1. Introduction'))

story.append(Paragraph(
    '<i>Architecture is the program. Risks are syntax. Validations compile.</i>',
    abstract_style
))
story.append(spacer(2*mm))

story.append(body(
    'AICL (AI-Centric Language) is a specification-first programming language that fundamentally '
    'reimagines the relationship between software architecture and executable code. In traditional '
    'software development, architecture is documentation: diagrams in Confluence, design documents '
    'in Google Docs, and risk assessments in spreadsheets. These artifacts describe what the system '
    'should do, what could go wrong, and how to recover, but nothing enforces their implementation. '
    'The result is a persistent gap between architectural intent and operational reality, a gap where '
    'most production failures originate.'
))

story.append(body(
    'AICL closes this gap by making architecture the source code itself. Instead of writing '
    'implementation instructions, developers write specifications: goals, constraints, risks, '
    'recoveries, architectural layers, and validation criteria. The compiler then transforms these '
    'specifications into executable programs, generating not just the happy-path logic but also '
    'the error handling, recovery mechanisms, and test suites that are typically neglected or '
    'incomplete in hand-written code. The key innovation is that risks, recoveries, and validations '
    'are not optional documentation or best-effort addenda; they are mandatory syntactic elements '
    'that the compiler enforces with the same rigor that type checkers enforce type constraints.'
))

story.append(body(
    'This white paper presents the design, formal specification, and implementation of AICL v0.3.0. '
    'We describe the ten-level language hierarchy, the formal BNF grammar with 27 reserved keywords, '
    'the nine-stage compilation pipeline, the deterministic behavior pattern library that eliminates '
    'TODO placeholders from compiled output, and the compilation provenance system that ensures every '
    'generated line of code is traceable to its source specification. We provide worked examples '
    'across four domains and a comparative analysis against traditional languages, domain-specific '
    'languages, and AI code generation tools.'
))

# ══════════════════════════════════════════════════════════════
# 2. THE PROBLEM
# ══════════════════════════════════════════════════════════════

story.append(heading1('2. The Problem: Architecture as Documentation'))

story.append(body(
    'The software industry has a well-documented problem: architectural knowledge degrades over time. '
    'Design documents become stale as code evolves. Risk assessments are written once and forgotten. '
    'Recovery procedures exist in runbooks that nobody reads until 3 AM. Validation criteria are '
    'expressed as vague prose rather than executable assertions. This is not a failure of individual '
    'engineers; it is a structural failure of the tools and languages we use. No mainstream programming '
    'language requires you to specify what can fail. No compiler checks whether you have recovery '
    'procedures for every identified risk. No build system verifies that your tests actually cover '
    'the success criteria you defined during design.'
))

story.append(heading2('2.1 The Intent-Implementation Gap'))

story.append(body(
    'Consider a typical production incident: a payment processing service begins timing out under load. '
    'The architecture document specified a risk of "database connection pool exhaustion under high '
    'concurrency" with a recovery of "implement circuit breaker with fallback to cached data." But '
    'this risk existed only in the design document. No code enforced it. No test verified it. When '
    'the incident occurred, the on-call engineer had to rediscover the risk, reimplement the recovery, '
    'and deploy a patch, all under time pressure. The architecture document described the solution '
    'months before the incident, but because it was documentation rather than code, it could not '
    'prevent the failure.'
))

story.append(make_callout(
    'Core Insight',
    'The gap between architectural intent and executable implementation is where most production failures live. '
    'Every risk documented in Confluence but not compiled into code is a latent incident waiting to happen.'
))

story.append(heading2('2.2 The Optional Afterthought Problem'))

story.append(body(
    'In every mainstream language, error handling is optional. You can write a function without a try/catch. '
    'You can deploy a service without a circuit breaker. You can skip writing tests for edge cases. The '
    'language does not care. The compiler does not check. The result is predictable: error handling, '
    'recovery logic, and validation are the first things cut when deadlines approach, and the last things '
    'added after incidents occur. AICL makes these mandatory. You cannot write a valid AICL program '
    'without specifying risks and recoveries. The compiler will reject your program if you try. This is '
    'the same enforcement model that made type systems successful: it works not because it is convenient, '
    'but because it is unavoidable.'
))

# ══════════════════════════════════════════════════════════════
# 3. DESIGN PRINCIPLES
# ══════════════════════════════════════════════════════════════

story.append(heading1('3. Design Principles'))

story.append(body(
    'AICL is built on five foundational principles that distinguish it from existing specification '
    'languages, architecture description languages, and AI code generation tools. These principles '
    'are not merely aspirational; they are enforced by the language grammar and the compiler.'
))

principles_data = [
    [Paragraph('<b>Principle</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9.5, textColor=colors.white)),
     Paragraph('<b>Statement</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9.5, textColor=colors.white)),
     Paragraph('<b>Enforcement</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9.5, textColor=colors.white))],
    ['Architecture is the program', 'The specification IS the source code', 'Compiler rejects programs without Goal, Layer, Validation'],
    ['Risks are first-class', 'Failure modeling is mandatory, not optional', 'Every Risk requires a paired Recovery; compiler validates pairing'],
    ['Validation is built-in', 'Success criteria are part of the language', 'Validations compile to test suites; compilation fails without them'],
    ['Strict grammar', 'Deterministic parsing, not free-form natural language', '27 reserved keywords; formal BNF grammar; no ambiguity'],
    ['Deterministic compilation', 'Same input always produces same output', 'Pattern library + sub-language; no AI guessing in default mode'],
]
story.append(make_table(principles_data, [42*mm, 55*mm, CONTENT_W - 102*mm]))

# ══════════════════════════════════════════════════════════════
# 4. LANGUAGE DESIGN
# ══════════════════════════════════════════════════════════════

story.append(heading1('4. Language Design'))

story.append(body(
    'AICL is organized as a ten-level progressive hierarchy. Level 1 (Architecture) is mandatory for '
    'every AICL program; higher levels are used as needed based on the complexity of the system being '
    'specified. This design allows simple programs to remain simple while supporting arbitrarily complex '
    'specifications through the additive composition of higher levels. The progressive structure also '
    'serves as a learning gradient: developers can start with Level 1 and incrementally adopt higher '
    'levels as their understanding of the language deepens.'
))

story.append(heading2('4.1 Language Levels'))

levels_data = [
    [Paragraph('<b>Level</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Feature</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Keywords</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Description</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white))],
    ['1', 'Architecture', 'Goal, Constraint, Risk, Recovery, Layer, Sublayer, Validation', 'Mandatory core: define what, what could fail, how to recover'],
    ['2', 'Entities', 'Entity', 'Typed data structures with field definitions'],
    ['3', 'Behaviors', 'Behavior, Input, Output, Action', 'Entity operations with deterministic compilation'],
    ['4', 'Conditions', 'Condition, When, Then', 'Replace if/else with declarative When/Then clauses'],
    ['5', 'Events', 'Event, On, Action', 'Event-driven programming with On/Action pairs'],
    ['6', 'Concurrency', 'Parallel', 'Concurrent layer execution with compiler-managed threading'],
    ['7', 'Optimization', 'Optimize, Priority', 'Performance targets and priority hints'],
    ['8', 'Learning', 'Learn, Adapt, Based', 'Machine learning integration and adaptive behavior'],
    ['9', 'Security', 'Security, Encrypt, Protect', 'Built-in security directives'],
    ['10', 'Native Code', 'Native', 'Escape hatch for low-level implementation in any language'],
]
story.append(make_table(levels_data, [14*mm, 26*mm, 52*mm, CONTENT_W - 97*mm]))

story.append(heading3('Minimal Valid Program'))

story.append(body(
    'A Level 1 AICL program requires exactly three elements: a Goal that states what the system must '
    'achieve, a Layer that defines the architectural structure, and a Validation that specifies the '
    'measurable success criterion. This minimal program compiles to a complete Python application with '
    'error handling and a test suite, even without any behavioral specifications.'
))

story.append(code(
    'Goal:\n'
    '    Hello World\n\n'
    'Layer:\n'
    '    Core\n\n'
    'Validation:\n'
    '    Output is produced'
))

story.append(heading2('4.2 Formal Grammar'))

story.append(body(
    'AICL has a formal BNF grammar that specifies the syntax for all ten language levels. The grammar '
    'is deterministic: every valid AICL program has exactly one parse tree. There is no ambiguity in '
    'keyword interpretation, indentation handling, or section boundaries. This determinism is essential '
    'for the compiler to produce consistent, reproducible output and for the provenance tracker to '
    'accurately trace every generated line of code back to its source specification.'
))

story.append(code(
    '&lt;program&gt;       ::= &lt;section&gt;*\n'
    '&lt;section&gt;       ::= &lt;goal-section&gt; | &lt;constraint-section&gt;\n'
    '                  | &lt;risk-section&gt; | &lt;recovery-section&gt;\n'
    '                  | &lt;layer-section&gt; | &lt;validation-section&gt;\n'
    '                  | &lt;entity-section&gt; | &lt;behavior-section&gt;\n'
    '                  | &lt;condition-section&gt; | &lt;event-section&gt;\n'
    '                  | &lt;parallel-section&gt; | &lt;optimize-section&gt;\n'
    '                  | &lt;learn-section&gt; | &lt;adapt-section&gt;\n'
    '                  | &lt;security-section&gt; | &lt;native-section&gt;\n\n'
    '&lt;goal-section&gt;      ::= "Goal:" &lt;text&gt;\n'
    '&lt;risk-section&gt;      ::= "Risk:" &lt;text&gt;\n'
    '&lt;recovery-section&gt;  ::= "Recovery:" &lt;text&gt;\n'
    '&lt;layer-section&gt;     ::= "Layer:" &lt;text&gt; &lt;sublayer-section&gt;*\n'
    '&lt;behavior-section&gt;  ::= "Behavior" &lt;identifier&gt; &lt;behavior-body&gt;\n'
    '&lt;behavior-body&gt;     ::= INDENT (&lt;input-section&gt; | &lt;output-section&gt; | &lt;action-section&gt;)+ DEDENT\n'
    '&lt;condition-section&gt; ::= "Condition:" &lt;condition-body&gt;\n'
    '&lt;condition-body&gt;    ::= INDENT &lt;when-clause&gt; &lt;then-clause&gt; DEDENT'
))

story.append(body(
    'The full grammar specification, including all production rules for all ten levels, is available '
    'in the AICL repository at spec/grammar.md. The grammar defines 16 distinct section types, each '
    'with its own sub-grammar for nested elements. The parser implements the grammar as a line-based '
    'recursive descent parser that correctly handles AICL\'s format where values can appear on the same '
    'line as the keyword or on the following line, and where indented blocks denote nested structures.'
))

story.append(heading2('4.3 Type System'))

story.append(body(
    'AICL provides 11 built-in types that cover the data modeling needs of most specification-level '
    'programs. These types are used in Entity field definitions and Behavior input/output declarations. '
    'The compiler maps each AICL type to the corresponding Python type in the generated code, with '
    'appropriate type annotations and validation logic. The "any" type serves as an escape hatch for '
    'cases where the specification does not need to constrain the type, while "void" indicates that '
    'a behavior produces no output.'
))

type_data = [
    [Paragraph('<b>AICL Type</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Python Target</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Description</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white))],
    ['string', 'str', 'Text data and identifiers'],
    ['integer', 'int', 'Whole numbers and counters'],
    ['float', 'float', 'Floating-point calculations'],
    ['boolean', 'bool', 'True/False state flags'],
    ['datetime', 'datetime', 'Timestamps and date handling'],
    ['list', 'List[Any]', 'Ordered collections'],
    ['dict', 'Dict[str, Any]', 'Key-value mappings'],
    ['set', 'set', 'Unique element collections'],
    ['any', 'Any', 'Dynamic type escape hatch'],
    ['void', 'None', 'No return value'],
    ['bytes', 'bytes', 'Binary data handling'],
]
story.append(make_table(type_data, [30*mm, 35*mm, CONTENT_W - 70*mm]))

story.append(heading2('4.4 Keyword Reference'))

story.append(body(
    'AICL has 27 reserved keywords, distributed across the ten language levels. Keywords are '
    'case-sensitive and form the structural skeleton of every AICL program. No keyword can be used '
    'as an identifier. The keyword set is intentionally small: each keyword has a single, unambiguous '
    'purpose, and the compiler knows exactly how to handle each one. This is a deliberate contrast '
    'with natural-language programming approaches, where the same word might be interpreted differently '
    'in different contexts.'
))

kw_data = [
    [Paragraph('<b>Keyword</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Level</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Purpose</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white))],
    ['Goal', '1', 'Define the system objective'],
    ['Constraint', '1', 'Define system limitation'],
    ['Risk', '1', 'Define failure condition'],
    ['Recovery', '1', 'Define corrective action'],
    ['Layer', '1', 'Define architectural layer'],
    ['Sublayer', '1', 'Define sub-layer within layer'],
    ['Validation', '1', 'Define success criterion'],
    ['Entity', '2', 'Define data entity with fields'],
    ['Behavior', '3', 'Define entity behavior'],
    ['Input', '3', 'Define behavior input parameter'],
    ['Output', '3', 'Define behavior output'],
    ['Action', '3/5', 'Define action to perform'],
    ['Condition', '4', 'Define conditional behavior'],
    ['When', '4', 'Condition trigger clause'],
    ['Then', '4', 'Condition consequence clause'],
    ['Event', '5', 'Define event-driven behavior'],
    ['On', '5', 'Event trigger clause'],
    ['Parallel', '6', 'Define concurrent execution'],
    ['Optimize', '7', 'Define optimization target'],
    ['Priority', '7', 'Define optimization priority'],
    ['Learn', '8', 'Define learning objective'],
    ['Adapt', '8', 'Define adaptive behavior'],
    ['Based', '8', 'Adaptation criterion'],
    ['Security', '9', 'Define security requirements'],
    ['Encrypt', '9', 'Encryption directive'],
    ['Protect', '9', 'Protection directive'],
    ['Native', '10', 'Inline native code escape hatch'],
]
story.append(make_table(kw_data, [28*mm, 16*mm, CONTENT_W - 49*mm]))

# ══════════════════════════════════════════════════════════════
# 5. COMPILATION ARCHITECTURE
# ══════════════════════════════════════════════════════════════

story.append(heading1('5. Compilation Architecture'))

story.append(body(
    'The AICL compiler transforms architectural specifications into executable programs through a '
    'nine-stage pipeline. Unlike conventional compilers that primarily translate syntax, the AICL '
    'compiler reasons about the architecture, validates risk/recovery completeness, synthesizes '
    'recovery logic from recovery specifications, generates test suites from validation criteria, '
    'and produces a complete, deployable application. The compilation is fully deterministic: the '
    'same input always produces the same output, regardless of the execution environment.'
))

story.append(heading2('5.1 Nine-Stage Pipeline'))

pipeline_data = [
    [Paragraph('<b>Stage</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Name</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Input</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Output</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Description</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white))],
    ['1', 'Specification Parsing', 'AICL source', 'AST', 'Line-based parser produces 17-node AST'],
    ['2', 'Architecture Validation', 'AST', 'Validation report', 'Checks Goal, Layer, Validation presence'],
    ['3', 'Dependency Analysis', 'AST', 'Dependency graph', 'Layer dependency ordering'],
    ['4', 'Risk Analysis', 'AST', 'Risk/Recovery pairs', 'Every Risk paired with Recovery'],
    ['5', 'Recovery Synthesis', 'Risk/Recovery pairs', 'Recovery logic', 'Generates try/except and fallback code'],
    ['6', 'Code Generation', 'AST + patterns', 'Python source', 'Behavior patterns produce deterministic code'],
    ['7', 'Test Generation', 'Validations', 'pytest suite', 'Each Validation becomes a test case'],
    ['8', 'Optimization', 'Optimize hints', 'Optimized code', 'Applies Optimize/Priority directives'],
    ['9', 'Final Construction', 'All outputs', 'main.py + tests + tree', 'Assembles final deliverables'],
]
story.append(make_table(pipeline_data, [12*mm, 30*mm, 28*mm, 28*mm, CONTENT_W - 103*mm]))

story.append(heading2('5.2 Architecture Tree IR'))

story.append(body(
    'The Architecture Tree is the central intermediate representation of the AICL compiler. It transforms '
    'the flat list of AST sections into a hierarchical tree structure that mirrors the system\'s actual '
    'architecture. Each node in the tree represents an architectural layer with its associated risks, '
    'recoveries, validations, constraints, behaviors, conditions, and events. The tree structure enables '
    'several critical compilation features that would be impossible with a flat AST: risk propagation '
    'from parent layers to child sublayers, dependency ordering through topological sorting of layer '
    'nodes, and contextual code generation where behaviors are compiled differently depending on their '
    'position in the architecture.'
))

story.append(body(
    'The Architecture Tree is constructed in three phases. First, layer nodes are created from Layer and '
    'Sublayer declarations, establishing the hierarchical structure. Second, entity and behavior nodes '
    'are attached to their respective layers based on keyword matching. Third, global risks, recoveries, '
    'and validations are distributed to the most specific applicable layer using a keyword-overlap '
    'scoring algorithm. This distribution ensures that recovery code is generated at the correct level '
    'of the architecture, rather than being centralized in a generic error handler that lacks context '
    'about the specific layer\'s requirements.'
))

story.append(heading2('5.3 Deterministic Behavior Compilation'))

story.append(body(
    'The most significant innovation in AICL v0.3 is the deterministic behavior compilation engine. '
    'Previous versions of the compiler generated TODO placeholders for behavior actions, producing code '
    'that could not be executed without manual intervention. The current version uses a two-mechanism '
    'approach to eliminate all TODOs: pattern matching and sub-language parsing.'
))

story.append(heading3('5.3.1 Behavior Pattern Library'))

story.append(body(
    'The pattern library contains over 30 deterministic patterns organized into 15 categories. Each '
    'pattern maps a class of action descriptions to a parameterized code template. When the compiler '
    'encounters a Behavior Action, it attempts to match the action description against the pattern '
    'library. If a match is found, the pattern\'s template is instantiated with the extracted parameters '
    'to produce deterministic, executable code. The matching algorithm uses keyword extraction, semantic '
    'categorization, and confidence scoring to select the best pattern. The entire process is deterministic: '
    'the same action description always matches the same pattern with the same parameters.'
))

pattern_data = [
    [Paragraph('<b>Category</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Patterns</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Example Action</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Generated Code</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white))],
    ['Movement', 'MOVE, BOUNCE, ORBIT', 'Update paddle position', 'Position += velocity * delta'],
    ['Creation', 'CREATE, INITIALIZE, SPAWN', 'Create new game', 'obj = ClassName(**params)'],
    ['Update', 'UPDATE, ASSIGN, CLAMP', 'Clamp ball position', 'pos = max(0, min(pos, bound))'],
    ['Communication', 'BROADCAST, SEND, RECEIVE', 'Transmit message', 'channel.send(message)'],
    ['Validation', 'VALIDATE, CHECK, VERIFY', 'Validate move', 'return rules.is_valid(move)'],
    ['Transform', 'TRANSFORM, CONVERT, PARSE', 'Parse input', 'result = parse(input_data)'],
    ['Storage', 'STORE, LOAD, PERSIST', 'Save game state', 'storage.save(key, data)'],
    ['Security', 'ENCRYPT, HASH, PROTECT', 'Encrypt message', 'encrypted = cipher.encrypt(data)'],
    ['Filtering', 'FILTER, SELECT, REJECT', 'Filter messages', '[m for m in items if cond(m)]'],
    ['Sorting', 'SORT, RANK, ORDER', 'Sort by priority', 'sorted(items, key=fn)'],
    ['Routing', 'ROUTE, DISPATCH, FORWARD', 'Route to handler', 'router.dispatch(event)'],
    ['Serialization', 'SERIALIZE, DESERIALIZE', 'Serialize data', 'json.dumps(data)'],
    ['Deletion', 'DELETE, REMOVE, DESTROY', 'Remove channel', 'channels.remove(ch)'],
    ['Iteration', 'LOOP, ITERATE, REPEAT', 'Process all items', 'for item in items: process(item)'],
]
story.append(make_table(pattern_data, [24*mm, 34*mm, 35*mm, CONTENT_W - 98*mm]))

story.append(heading3('5.3.2 Sub-Language Parser'))

story.append(body(
    'When no pattern matches an action description, the sub-language parser provides an explicit, '
    'deterministic alternative. The sub-language consists of a small set of action verbs with '
    'well-defined semantics: assign (variable assignment with arithmetic), clamp (bounded value '
    'constraining), check (boolean condition evaluation), send (message transmission), create '
    '(object instantiation), and delete (object removal). Each sub-language statement compiles '
    'to exactly one Python statement with no ambiguity. The sub-language is not intended to be '
    'Turing-complete; it is a deliberately limited notation for expressing the most common '
    'behavioral patterns in a way that the compiler can translate without guessing.'
))

story.append(code(
    'Behavior MovePaddle\n'
    '    Input: Player direction string\n'
    '    Action: assign paddle_position += direction * speed\n'
    '            clamp paddle_position between 0 and screen_width'
))

story.append(heading2('5.4 Compilation Provenance'))

story.append(body(
    'Every line of code generated by the AICL compiler has a traceable provenance chain. The '
    'provenance system records the complete decision path from AICL source to generated code: '
    'which section the code came from, what pattern matched (or sub-language rule applied), '
    'what template was instantiated, and what parameters were used. This information is accessible '
    'through the "aicl explain" command, which produces a human-readable trace of every compilation '
    'decision.'
))

story.append(body(
    'The provenance system addresses a fundamental risk of compiler complexity: as the pattern library '
    'grows from 30 patterns to potentially hundreds, the compiler becomes increasingly difficult to '
    'understand and debug. The provenance tracker ensures that every decision remains explainable, '
    'regardless of the pattern library\'s size. Each provenance record includes the source type '
    '(pattern match, sub-language, fallback, architecture template, direct mapping, or recovery '
    'synthesis), the source location in the AICL program, the resolution path through the compiler\'s '
    'decision logic, the generated code, and a confidence score.'
))

story.append(make_callout(
    'Design Principle',
    'The compiler must always know exactly why it generated a line of code. If it cannot explain it, '
    'it should not generate it. This principle is enforced by the provenance system, which records '
    'every compilation decision as an auditable, queryable record.'
))

# ══════════════════════════════════════════════════════════════
# 6. COMPARATIVE ANALYSIS
# ══════════════════════════════════════════════════════════════

story.append(heading1('6. Comparative Analysis'))

story.append(heading2('6.1 AICL vs Traditional Languages'))

story.append(body(
    'Traditional programming languages (Python, Java, Rust, Go) treat error handling as optional. '
    'Developers can write functions without try/catch blocks, deploy services without circuit breakers, '
    'and ship code without tests. The language does not enforce completeness. AICL takes the opposite '
    'approach: every Risk must have a paired Recovery, every Validation must be testable, and every '
    'Layer must be accounted for in the generated architecture. This is not a linting rule that can be '
    'suppressed; it is a compile-time requirement built into the language grammar.'
))

comp_data = [
    [Paragraph('<b>Dimension</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Traditional Languages</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>AICL</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white))],
    ['Risks', 'Optional try/catch', 'Mandatory Risk keyword'],
    ['Recovery', 'Scattered error handlers', 'Paired Recovery per risk'],
    ['Validation', 'Separate test files, best effort', 'Compiled from Validation sections'],
    ['Architecture', 'Documentation and diagrams', 'Executable Layer definitions'],
    ['Behavior', 'Free-form function bodies', 'Deterministic pattern compilation'],
    ['Provenance', 'None', 'Every line traceable via aicl explain'],
    ['Compiler', 'Translates syntax', 'Reasons about architecture'],
    ['Output', 'Partial (requires manual TODO filling)', 'Complete (zero TODOs)'],
]
story.append(make_table(comp_data, [28*mm, 55*mm, CONTENT_W - 88*mm]))

story.append(heading2('6.2 AICL vs DSLs and ADLs'))

story.append(body(
    'Domain-Specific Languages (DSLs) like SQL and regular expressions excel at expressing solutions '
    'within a narrow domain, but they lack architectural expressiveness. You cannot describe failure '
    'modes or recovery strategies in SQL. Architecture Description Languages (ADLs) like Wright and '
    'Acme can describe system structure and component interactions, but they produce documentation, '
    'not executable code. AICL occupies a unique position: it is both architecturally expressive '
    '(like an ADL) and compilable to executable code (like a DSL). The key difference is that AICL\'s '
    'architectural descriptions are not just documentation; they are the source code that the compiler '
    'transforms into working software.'
))

story.append(heading2('6.3 AICL vs AI Code Generation'))

story.append(body(
    'AI code generation tools (GitHub Copilot, ChatGPT, Claude) can produce implementation code from '
    'natural language descriptions, but they have three fundamental limitations that AICL addresses. '
    'First, they are non-deterministic: the same prompt can produce different code on different runs, '
    'making reproducibility impossible. Second, they do not enforce completeness: nothing prevents '
    'the AI from skipping error handling or omitting recovery logic. Third, they lack provenance: '
    'there is no way to trace why the AI generated a particular line of code or verify that it '
    'correctly implements the intended behavior. AICL is deterministic by design, enforces completeness '
    'through its grammar, and provides full provenance for every generated line. AI-assisted code '
    'filling is available as an optional mode (--ai-fill), but the default compilation path is fully '
    'deterministic and does not depend on any AI model.'
))

# ══════════════════════════════════════════════════════════════
# 7. WORKED EXAMPLES
# ══════════════════════════════════════════════════════════════

story.append(heading1('7. Worked Examples'))

story.append(body(
    'The AICL repository includes four example programs of increasing complexity, each demonstrating '
    'different language levels and compilation features. These examples are not toy programs; they '
    'represent realistic software systems that exercise the full compilation pipeline, from parsing '
    'through code generation and test synthesis.'
))

story.append(heading2('7.1 Blue Square (Level 1)'))

story.append(body(
    'The simplest AICL program demonstrates Level 1 features only: Goal, Risk, Recovery, Layer, '
    'and Validation. This 44-line program specifies a graphical application that displays a blue '
    'square on screen. It defines two risks (graphics device unavailable, shader compilation failure) '
    'with paired recoveries (use software renderer, load fallback shader), four architectural layers, '
    'and two validation criteria. The compiler generates a complete Python application with error '
    'handling for both risks and a test suite that verifies both validations.'
))

story.append(heading2('7.2 Pong Game (Levels 1-6)'))

story.append(body(
    'The Pong game example expands to Levels 1-6, introducing Entities (Player, Ball), Behaviors '
    '(MovePaddle, UpdateBall), Conditions (When ball hits paddle, When score reaches 10), Events '
    '(On key press, On collision), and Parallel execution of rendering, input, and physics layers. '
    'This 128-line program demonstrates how AICL scales from simple specifications to interactive, '
    'event-driven systems. The compiler generates a complete game loop with input handling, physics '
    'simulation, collision detection, score tracking, and error recovery for all identified risks.'
))

story.append(heading2('7.3 Chat Application (Levels 1-9)'))

story.append(body(
    'The chat application example uses Levels 1-9, adding Optimization targets (memory usage, '
    'network latency), Learning objectives (user behavior for message suggestions), and Security '
    'directives (encrypt message content, protect user credentials). This 182-line program represents '
    'a realistic production system with network resilience, offline mode, message persistence, '
    'concurrent UI and networking layers, and cryptographic security. The compiler generates a '
    'complete WebSocket-based chat application with automatic reconnection, offline message queuing, '
    'and encryption/decryption handlers.'
))

story.append(heading2('7.4 Multiplayer Chess (Levels 1-9)'))

story.append(body(
    'The most complex example is a multiplayer chess game that exercises the full language up to '
    'Level 9, including Adaptive behavior (graphics quality adapts to device performance). This '
    '190-line program specifies complex state management (board, pieces, game state), multiple '
    'behaviors (MakeMove, ValidateMove), three conditions (check, checkmate, stalemate), three '
    'events (piece selection, move submission, opponent move), and parallel execution of UI and '
    'networking. The compiler generates a complete chess application with move validation, '
    'check/checkmate detection, network synchronization with latency compensation, and adaptive '
    'graphics quality adjustment.'
))

examples_data = [
    [Paragraph('<b>Example</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Lines</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Levels</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Entities</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Behaviors</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Risks</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white))],
    ['Blue Square', '44', '1', '0', '0', '2'],
    ['Pong Game', '128', '1-6', '2', '2', '3'],
    ['Chat App', '182', '1-9', '3', '2', '4'],
    ['Chess', '190', '1-9', '3', '2', '4'],
]
story.append(make_table(examples_data, [28*mm, 16*mm, 16*mm, 20*mm, 22*mm, CONTENT_W - 107*mm]))

# ══════════════════════════════════════════════════════════════
# 8. IMPLEMENTATION STATUS
# ══════════════════════════════════════════════════════════════

story.append(heading1('8. Implementation Status'))

story.append(body(
    'AICL v0.3.0 is implemented as a Python package with a command-line interface. The implementation '
    'consists of nine modules totaling approximately 5,000 lines of Python code, with 38 tests all '
    'passing. The following table summarizes the current implementation status of each component.'
))

impl_data = [
    [Paragraph('<b>Component</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Module</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Lines</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Status</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white)),
     Paragraph('<b>Notes</b>', ParagraphStyle('TH', parent=body_style, fontName='CarlitoBold', fontSize=9, textColor=colors.white))],
    ['Parser', 'parser.py', '650', 'Complete', 'Line-based, handles all 10 levels'],
    ['AST Nodes', 'ast_nodes.py', '271', 'Complete', '17 node types with validation'],
    ['Tokenizer', 'tokenizer.py', '361', 'Complete', 'Stand-alone; not used by parser'],
    ['Architecture Tree', 'architecture_tree.py', '282', 'Complete', 'IR with risk distribution'],
    ['Compiler', 'compiler.py', '1,476', 'Complete', '9-stage pipeline, Python target'],
    ['Pattern Library', 'patterns.py', '1,384', 'Complete', '30+ patterns, 15 categories'],
    ['Provenance', 'provenance.py', '244', 'Complete', 'Full audit trail for compilation'],
    ['CLI', 'cli.py', '248', 'Complete', '5 commands + version'],
    ['Tests', 'test_aicl.py', '1,006', 'Complete', '38 tests, all passing'],
]
story.append(make_table(impl_data, [30*mm, 32*mm, 16*mm, 20*mm, CONTENT_W - 103*mm]))

story.append(body(
    'The compiler currently targets Python only. All four example programs compile to zero-TODO, '
    'fully executable Python code with error handling, recovery logic, and test suites. The '
    'provenance system provides a complete audit trail for every generated line of code, accessible '
    'through the "aicl explain" command.'
))

# ══════════════════════════════════════════════════════════════
# 9. FUTURE DIRECTIONS
# ══════════════════════════════════════════════════════════════

story.append(heading1('9. Future Directions'))

story.append(heading2('9.1 Multi-Language Targets'))

story.append(body(
    'The current compiler generates Python only. Future versions will add code generation backends '
    'for Rust (targeting performance-critical systems), JavaScript/TypeScript (targeting web '
    'applications), and Go (targeting distributed systems and microservices). Each backend will '
    'implement the same nine-stage pipeline with language-specific code generation in Stage 6 and '
    'language-specific test frameworks in Stage 7. The behavior pattern library and sub-language '
    'parser are language-agnostic and will be shared across all backends.'
))

story.append(heading2('9.2 Architecture Template Selection'))

story.append(body(
    'The ArchitectureTemplateMapper currently maps Goal descriptions to application structure '
    'templates (game loop, event-driven, pipeline, CRUD). Future work will expand this to a '
    'richer set of templates derived from analysis of real-world architectures, including '
    'microservices, lambda/event-server, CQRS, and real-time streaming patterns. The Goal keyword '
    'will serve as the primary input to the template selector, allowing the compiler to make '
    'informed decisions about the overall structure of the generated application based on the '
    'stated objective.'
))

story.append(heading2('9.3 Self-Healing Runtime'))

story.append(body(
    'The ultimate vision for AICL is a self-healing runtime that automatically executes recovery '
    'procedures when risks materialize at runtime. Currently, the compiler generates recovery code '
    'as try/except blocks with explicit recovery logic. In future versions, the runtime will monitor '
    'risk conditions continuously and execute recovery procedures automatically, without requiring '
    'the failure to propagate to an exception handler. This shifts the recovery model from reactive '
    '(wait for failure, then recover) to proactive (detect risk condition, execute recovery before '
    'failure occurs).'
))

story.append(heading2('9.4 Autonomous Architecture Optimization'))

story.append(body(
    'The Learn and Adapt keywords at Level 8 currently generate placeholder learning code. Future '
    'versions will integrate with actual ML pipelines to enable the system to learn from runtime '
    'behavior and adapt its architecture accordingly. For example, a system that learns that a '
    'particular database query is consistently slow could automatically add a caching layer, or a '
    'system that learns that a particular API endpoint is rarely used could deprioritize its '
    'resource allocation. This represents the long-term convergence of architecture-as-code and '
    'AI-driven optimization, where the architecture specification evolves in response to real-world '
    'operational data.'
))

# ══════════════════════════════════════════════════════════════
# 10. CONCLUSION
# ══════════════════════════════════════════════════════════════

story.append(heading1('10. Conclusion'))

story.append(body(
    'AICL demonstrates that it is possible to build a programming language where architectural '
    'intent is not documentation but source code, where failure modeling is not optional but '
    'mandatory, and where validation criteria are not afterthoughts but compiled assertions. The '
    'language achieves this through a strict, deterministic grammar with 27 reserved keywords, a '
    'nine-stage compilation pipeline that reasons about architecture rather than merely translating '
    'syntax, and a deterministic behavior compilation engine that eliminates TODO placeholders from '
    'generated code.'
))

story.append(body(
    'The key technical contributions are the Architecture Tree intermediate representation, which '
    'enables hierarchical risk propagation and contextual code generation; the behavior pattern '
    'library, which maps 30+ behavioral patterns to deterministic code templates; the sub-language '
    'parser, which provides an explicit notation for behavioral specifications that fall outside the '
    'pattern library; and the compilation provenance system, which ensures that every generated line '
    'of code has a traceable origin in the source specification.'
))

story.append(body(
    'AICL is not intended to replace general-purpose programming languages. It is designed for the '
    'class of systems where architectural correctness is more important than implementation flexibility: '
    'distributed systems, real-time applications, safety-critical software, and any system where the '
    'cost of failure is high enough to justify the overhead of specification-first development. For '
    'these systems, AICL offers a fundamental advantage: the architecture is no longer documentation. '
    'The architecture is the program.'
))

story.append(spacer(10*mm))
story.append(hr())

# ══════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════

story.append(heading1('References'))

refs = [
    '[1] AICL Repository: https://github.com/AFKmoney/AICL',
    '[2] AICL Language Specification v0.3.0, spec/grammar.md',
    '[3] Allen, R., and Garlan, D. "A Formal Basis for Architectural Connection." ACM Transactions on Software Engineering and Methodology, 1997.',
    '[4] Garlan, D., Monroe, R., and Wile, D. "Acme: Architectural Description of Component-Based Systems." Foundations of Component-Based Systems, 2000.',
    '[5] Clements, P., et al. Documenting Software Architectures: Views and Beyond. Addison-Wesley, 2010.',
    '[6] Gamma, E., et al. Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley, 1994.',
    '[7] Fowler, M. Patterns of Enterprise Application Architecture. Addison-Wesley, 2002.',
    '[8] Nygard, M. Release It!: Design and Deploy Production-Ready Software. Pragmatic Bookshelf, 2018.',
]

for ref in refs:
    story.append(Paragraph(ref, ParagraphStyle('Ref', parent=body_style, fontSize=9, leading=13, spaceAfter=2*mm)))

# ━━ Build ━━
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"White paper generated: {output_path}")
