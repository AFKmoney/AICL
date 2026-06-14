#!/usr/bin/env python3
"""
AICL White Paper PDF Generator

Generates a comprehensive 40+ page academic white paper for the
AI-Centric Language (AICL) project using ReportLab Platypus.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, ListFlowable, ListItem, Flowable, Frame, PageTemplate,
    BaseDocTemplate, NextPageTemplate,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

# ─── Palette ────────────────────────────────────────────────────────────────
ACCENT       = colors.HexColor('#cb552e')
TEXT_PRIMARY  = colors.HexColor('#262422')
TEXT_MUTED    = colors.HexColor('#817d75')
BG_SURFACE   = colors.HexColor('#e5e2db')
BG_PAGE      = colors.HexColor('#f4f4f2')
BG_CODE      = colors.HexColor('#f0efeb')
BORDER_LIGHT = colors.HexColor('#d5d2ca')

# ─── Fonts ──────────────────────────────────────────────────────────────────
FONT_DIR_SERIF  = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FONT_DIR_SERIF_B= '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FONT_DIR_SANS_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_DIR_SANS_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_DIR_MONO   = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
FONT_DIR_MONO_B = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
FONT_DIR_MONO_I = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf'

pdfmetrics.registerFont(TTFont('DejaVuSerif', FONT_DIR_SERIF))
pdfmetrics.registerFont(TTFont('DejaVuSerif-Bold', FONT_DIR_SERIF_B))
pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_DIR_SANS_R))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', FONT_DIR_SANS_B))
pdfmetrics.registerFont(TTFont('DejaVuMono', FONT_DIR_MONO))
pdfmetrics.registerFont(TTFont('DejaVuMono-Bold', FONT_DIR_MONO_B))
pdfmetrics.registerFont(TTFont('DejaVuMono-Oblique', FONT_DIR_MONO_I))

addMapping('DejaVuSerif', 0, 0, 'DejaVuSerif')
addMapping('DejaVuSerif', 1, 0, 'DejaVuSerif-Bold')
addMapping('DejaVuSans', 0, 0, 'DejaVuSans')
addMapping('DejaVuSans', 1, 0, 'DejaVuSans-Bold')
addMapping('DejaVuMono', 0, 0, 'DejaVuMono')
addMapping('DejaVuMono', 1, 0, 'DejaVuMono-Bold')

# ─── Page setup ─────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
LEFT_MARGIN   = 2.5 * cm
RIGHT_MARGIN  = 2.5 * cm
TOP_MARGIN    = 2.5 * cm
BOTTOM_MARGIN = 2.5 * cm
CONTENT_W = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN

# ─── Styles ─────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

sH1 = ParagraphStyle(
    'AiclH1', parent=styles['Heading1'],
    fontName='DejaVuSans-Bold', fontSize=18, leading=24,
    textColor=ACCENT, spaceBefore=28, spaceAfter=12,
    borderWidth=0, borderPadding=0,
)
sH2 = ParagraphStyle(
    'AiclH2', parent=styles['Heading2'],
    fontName='DejaVuSans-Bold', fontSize=14, leading=19,
    textColor=TEXT_PRIMARY, spaceBefore=20, spaceAfter=8,
)
sH3 = ParagraphStyle(
    'AiclH3', parent=styles['Heading3'],
    fontName='DejaVuSans-Bold', fontSize=11.5, leading=15,
    textColor=TEXT_PRIMARY, spaceBefore=14, spaceAfter=6,
)
sBody = ParagraphStyle(
    'AiclBody', parent=styles['Normal'],
    fontName='DejaVuSerif', fontSize=10, leading=15,
    textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY,
    spaceBefore=4, spaceAfter=6,
)
sBodyMuted = ParagraphStyle(
    'AiclBodyMuted', parent=sBody,
    textColor=TEXT_MUTED, fontSize=9.5,
)
sAbstract = ParagraphStyle(
    'AiclAbstract', parent=sBody,
    fontSize=10, leading=15, textColor=TEXT_MUTED,
    leftIndent=1.5*cm, rightIndent=1.5*cm,
    spaceBefore=6, spaceAfter=6,
)
sCode = ParagraphStyle(
    'AiclCode', parent=styles['Code'],
    fontName='DejaVuMono', fontSize=8.2, leading=11.5,
    textColor=TEXT_PRIMARY, backColor=BG_CODE,
    borderWidth=0.5, borderColor=BORDER_LIGHT,
    borderPadding=(6, 8, 6, 8),
    spaceBefore=6, spaceAfter=8,
    leftIndent=0.6*cm,
)
sCodeLabel = ParagraphStyle(
    'AiclCodeLabel', parent=sBody,
    fontName='DejaVuSans-Bold', fontSize=8, leading=10,
    textColor=TEXT_MUTED, spaceBefore=10, spaceAfter=0,
)
sCaption = ParagraphStyle(
    'AiclCaption', parent=sBody,
    fontName='DejaVuSans', fontSize=8.5, leading=12,
    textColor=TEXT_MUTED, alignment=TA_CENTER,
    spaceBefore=4, spaceAfter=12,
)
sBullet = ParagraphStyle(
    'AiclBullet', parent=sBody,
    leftIndent=1.2*cm, bulletIndent=0.4*cm,
    spaceBefore=2, spaceAfter=2,
)
sTableCell = ParagraphStyle(
    'AiclTableCell', parent=sBody,
    fontSize=8.5, leading=11.5,
    spaceBefore=2, spaceAfter=2,
)
sTableHeader = ParagraphStyle(
    'AiclTableHeader', parent=sTableCell,
    fontName='DejaVuSans-Bold', textColor=colors.white,
)
sCoverTitle = ParagraphStyle(
    'AiclCoverTitle', fontName='DejaVuSans-Bold',
    fontSize=32, leading=40, textColor=ACCENT,
    alignment=TA_CENTER, spaceBefore=0, spaceAfter=8,
)
sCoverSub = ParagraphStyle(
    'AiclCoverSub', fontName='DejaVuSans',
    fontSize=14, leading=20, textColor=TEXT_MUTED,
    alignment=TA_CENTER, spaceBefore=4, spaceAfter=4,
)
sCoverInfo = ParagraphStyle(
    'AiclCoverInfo', fontName='DejaVuSans',
    fontSize=11, leading=16, textColor=TEXT_PRIMARY,
    alignment=TA_CENTER, spaceBefore=2, spaceAfter=2,
)
sTOC_H1 = ParagraphStyle(
    'AiclTOC_H1', fontName='DejaVuSans-Bold', fontSize=11,
    leading=18, textColor=TEXT_PRIMARY, leftIndent=0,
    spaceBefore=6, spaceAfter=2,
)
sTOC_H2 = ParagraphStyle(
    'AiclTOC_H2', fontName='DejaVuSans', fontSize=10,
    leading=16, textColor=TEXT_PRIMARY, leftIndent=1.0*cm,
    spaceBefore=2, spaceAfter=1,
)
sRef = ParagraphStyle(
    'AiclRef', parent=sBody,
    fontSize=9, leading=13,
    leftIndent=0.8*cm, firstLineIndent=-0.8*cm,
    spaceBefore=2, spaceAfter=4,
)

# ─── Helper functions ────────────────────────────────────────────────────────

def h1(text):
    return Paragraph(text, sH1)

def h2(text):
    return Paragraph(text, sH2)

def h3(text):
    return Paragraph(text, sH3)

def p(text):
    return Paragraph(text, sBody)

def p_muted(text):
    return Paragraph(text, sBodyMuted)

def p_abstract(text):
    return Paragraph(text, sAbstract)

def code(text):
    """Render code block. Escape XML special chars first."""
    safe = (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )
    lines = safe.strip().split('\n')
    formatted = '<br/>'.join(lines)
    return Paragraph(formatted, sCode)

def code_label(text):
    return Paragraph(text, sCodeLabel)

def caption(text):
    return Paragraph(text, sCaption)

def spacer(h=0.3):
    return Spacer(1, h * cm)

def bullet_list(items):
    """Return a list of bullet-point paragraphs."""
    result = []
    for item in items:
        result.append(Paragraph(
            '<bullet>&bull;</bullet> ' + item, sBullet
        ))
    return result

def make_table(headers, rows, col_widths=None):
    """Build a professional styled table."""
    header_paras = [Paragraph(h, sTableHeader) for h in headers]
    data = [header_paras]
    for row in rows:
        data.append([Paragraph(str(c), sTableCell) for c in row])
    if col_widths is None:
        col_widths = [CONTENT_W / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSerif'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_PAGE]),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t

# ─── Accent Rule Flowable ───────────────────────────────────────────────────

class AccentRule(Flowable):
    """A thin horizontal accent-colored rule."""
    def __init__(self, width, thickness=1.5):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.height = thickness + 4
    def draw(self):
        self.canv.setStrokeColor(ACCENT)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 2, self.width, 2)

# ─── Page number callback ───────────────────────────────────────────────────

def add_page_number(canvas, doc):
    """Add page number to footer (skip page 1 = cover)."""
    page_num = doc.page
    if page_num <= 1:
        return
    canvas.saveState()
    canvas.setFont('DejaVuSans', 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawCentredString(PAGE_W / 2.0, 1.2 * cm, str(page_num - 1))
    # thin top rule on content pages
    canvas.setStrokeColor(BORDER_LIGHT)
    canvas.setLineWidth(0.4)
    canvas.line(LEFT_MARGIN, PAGE_H - 1.8*cm, PAGE_W - RIGHT_MARGIN, PAGE_H - 1.8*cm)
    canvas.restoreState()

# ═══════════════════════════════════════════════════════════════════════════
# CONTENT
# ═══════════════════════════════════════════════════════════════════════════

def build_document():
    """Assemble all content and return a list of Flowables."""

    story = []

    # ── COVER PAGE ───────────────────────────────────────────────────────
    story.append(Spacer(1, 5*cm))
    story.append(Paragraph('AICL', sCoverTitle))
    story.append(Paragraph('AI-Centric Language', ParagraphStyle(
        'CoverSub2', fontName='DejaVuSans', fontSize=18, leading=24,
        textColor=TEXT_PRIMARY, alignment=TA_CENTER, spaceBefore=4, spaceAfter=12,
    )))
    story.append(AccentRule(CONTENT_W, 2))
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph(
        'A Specification-First Programming Language<br/>for AI-Native Software Development',
        sCoverSub
    ))
    story.append(Spacer(1, 2.5*cm))
    story.append(Paragraph('Philippe-Antoine', sCoverInfo))
    story.append(Paragraph('Version 0.1.0', sCoverInfo))
    story.append(Paragraph('March 2026', sCoverInfo))
    story.append(Spacer(1, 2.5*cm))
    story.append(Paragraph(
        '<i>"Risks, recoveries, and validations are not documentation -- '
        'they are mandatory syntactic elements of the language."</i>',
        ParagraphStyle('CoverQuote', fontName='DejaVuSerif', fontSize=10.5,
                       leading=16, textColor=TEXT_MUTED, alignment=TA_CENTER,
                       leftIndent=2*cm, rightIndent=2*cm)
    ))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        '<b>Abstract.</b> AICL (AI-Centric Language) is a specification-first programming '
        'language where software is defined through structured architectural intent rather '
        'than implementation instructions. Unlike traditional programming languages that '
        'require developers to write step-by-step executable code, AICL enables developers '
        'to specify objectives, architectural layers, anticipated failure modes, recovery '
        'procedures, constraints, and validation criteria. The AICL compiler then transforms '
        'these high-level architectural specifications into executable software through a '
        'multi-stage, AI-native compilation pipeline. This white paper presents the '
        'motivation, philosophy, formal grammar, operational semantics, and implementation '
        'strategy of AICL, along with comparative analyses and research hypotheses that '
        'position AICL as a foundational contribution to AI-native software engineering.',
        ParagraphStyle('CoverAbstract', fontName='DejaVuSerif', fontSize=9.5,
                       leading=14, textColor=TEXT_MUTED, alignment=TA_JUSTIFY,
                       leftIndent=1.5*cm, rightIndent=1.5*cm,
                       spaceBefore=6, spaceAfter=6)
    ))
    story.append(PageBreak())

    # ── TABLE OF CONTENTS ────────────────────────────────────────────────
    story.append(h1('Table of Contents'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.4))

    toc_items = [
        ('1', 'Introduction', []),
        ('2', 'Motivation and Problem Statement', []),
        ('3', 'Core Philosophy', []),
        ('4', 'Language Design', [
            '4.1  Level 1: Architecture',
            '4.2  Level 2: Entities',
            '4.3  Level 3: Behaviors',
            '4.4  Level 4: Conditions',
            '4.5  Level 5: Events',
            '4.6  Level 6: Concurrency',
            '4.7  Level 7: Optimization',
            '4.8  Level 8: Learning',
            '4.9  Level 9: Security',
            '4.10 Level 10: Native Code',
        ]),
        ('5', 'Formal Grammar', [
            '5.1  BNF Grammar',
            '5.2  Keyword Table',
            '5.3  Type System',
        ]),
        ('6', 'Operational Semantics', [
            '6.1  Compilation Stages',
            '6.2  Architecture Tree IR',
            '6.3  Transformation Rules',
        ]),
        ('7', 'AI-Native Compilation Pipeline', [
            '7.1  Stage 1: Specification Parsing',
            '7.2  Stage 2: Architecture Validation',
            '7.3  Stage 3: Dependency Analysis',
            '7.4  Stage 4: Risk Analysis',
            '7.5  Stage 5: Recovery Synthesis',
            '7.6  Stage 6: Code Generation',
            '7.7  Stage 7: Test Generation',
            '7.8  Stage 8: Optimization',
            '7.9  Stage 9: Final Construction',
        ]),
        ('8', 'Comparative Analysis', [
            '8.1  Traditional Programming Languages',
            '8.2  DSLs and Model-Driven Engineering',
            '8.3  Specification Languages',
            '8.4  LLM Code Generation Tools',
            '8.5  Intentional Programming',
            '8.6  Comparison Table',
        ]),
        ('9', 'Example Programs', [
            '9.1  Blue Square',
            '9.2  Pong Game',
            '9.3  Chat Application',
            '9.4  Chess Game',
        ]),
        ('10', 'Research Hypotheses', []),
        ('11', 'Implementation', [
            '11.1  Parser Architecture',
            '11.2  Compiler Pipeline',
            '11.3  Architecture Tree IR',
        ]),
        ('12', 'Roadmap', []),
        ('13', 'Related Work', []),
        ('14', 'Conclusion', []),
        ('', 'References', []),
    ]

    for num, title, subs in toc_items:
        label = f'{num}  {title}' if num else title
        story.append(Paragraph(label, sTOC_H1))
        for sub in subs:
            story.append(Paragraph(sub, sTOC_H2))

    story.append(PageBreak())

    # ── 1. INTRODUCTION ─────────────────────────────────────────────────
    story.append(h1('1. Introduction'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'The history of programming languages is a story of progressive abstraction. '
        'From the raw binary instructions of early computing machines, through the mnemonic '
        'shorthands of assembly language, to the structured imperatives of FORTRAN and C, '
        'each generational shift has lifted the level at which humans communicate their '
        'intentions to machines. Object-oriented programming introduced encapsulation and '
        'inheritance; functional programming brought compositional purity; domain-specific '
        'languages offered tailored vocabularies for specialized problems. Yet despite these '
        'advances, the fundamental relationship between programmer and computer has remained '
        'largely unchanged: the programmer writes instructions, and the computer executes them.'
    ))
    story.append(p(
        'This instruction-centric paradigm has served the software industry well for decades, '
        'but it suffers from a critical and increasingly apparent limitation. As software '
        'systems grow in complexity, the gap between what developers intend and what they '
        'actually implement widens precipitously. Architectural decisions are documented in '
        'design documents that drift from the codebase. Failure modes are noted in post-mortem '
        'reports rather than prevented in the source. Validation criteria exist as external '
        'test suites that may or may not correspond to the actual requirements. The result '
        'is a fragmented development ecosystem where intent, implementation, and verification '
        'are disconnected artifacts that must be manually kept in sync.'
    ))
    story.append(p(
        'The emergence of large language models (LLMs) and AI-assisted development tools has '
        'made this gap both more visible and more consequential. When an AI system generates '
        'code from a natural language prompt, it is essentially guessing at the developer\'s '
        'architectural intent from ambiguous input. The AI has no structured way to understand '
        'the constraints that bound the solution, the risks that threaten it, or the validation '
        'criteria that define its success. Current LLM code generation tools treat software '
        'development as a translation problem -- converting natural language to code -- rather '
        'than a reasoning problem that requires understanding architecture, risk, and validation '
        'as first-class concerns.'
    ))
    story.append(p(
        'AICL (AI-Centric Language) proposes a fundamentally different approach. Rather than '
        'writing implementation instructions, developers using AICL specify the architecture '
        'of their system: its goals, constraints, risks, recovery procedures, layers, and '
        'validation criteria. These specifications are not documentation comments or external '
        'artifacts; they are mandatory syntactic elements of the language itself. The AICL '
        'compiler then transforms these architectural specifications into executable software '
        'through a multi-stage compilation pipeline that reasons about the architecture rather '
        'than merely translating it. In AICL, the architecture is the program.'
    ))
    story.append(p(
        'This white paper presents AICL in its entirety: the motivation and problem statement '
        'that give rise to it, the core philosophy that underpins its design, the complete '
        'language specification with its ten hierarchical levels, the formal grammar and '
        'operational semantics, the AI-native compilation pipeline, comparative analyses with '
        'existing approaches, illustrative example programs, research hypotheses, and the '
        'current implementation status. The goal is to provide a comprehensive reference for '
        'researchers, language designers, and practitioners interested in the intersection of '
        'programming language theory and AI-native software development.'
    ))

    story.append(PageBreak())

    # ── 2. MOTIVATION AND PROBLEM STATEMENT ─────────────────────────────
    story.append(h1('2. Motivation and Problem Statement'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(h2('2.1 Disconnected Artifacts'))
    story.append(p(
        'Modern software development relies on a constellation of disconnected artifacts to '
        'define what a system should do and verify that it does it correctly. Requirements '
        'documents capture stakeholder needs in natural language. Architecture diagrams depict '
        'system structure in visual notation. Design documents specify patterns and constraints. '
        'Test suites encode verification criteria in code. Monitoring configurations define '
        'operational health checks. Incident runbooks describe recovery procedures. Each of '
        'these artifacts contains critical information about the system, but they exist in '
        'different formats, different tools, and different domains of expertise. The codebase '
        'itself -- the artifact that actually runs in production -- is but one piece of this '
        'puzzle, and it often bears little structural resemblance to the architectural vision '
        'that motivated it.'
    ))
    story.append(p(
        'The consequences of this fragmentation are well-documented and severe. When '
        'requirements change, the code may not be updated to reflect them. When the code '
        'evolves, the architecture documentation drifts out of sync. When failures occur in '
        'production, the recovery procedures documented in runbooks may no longer be applicable '
        'to the current system state. Studies in empirical software engineering have '
        'consistently shown that the majority of software defects originate not from incorrect '
        'implementations of well-understood designs, but from misalignments between intent and '
        'implementation -- precisely the kind of misalignment that disconnected artifacts make '
        'inevitable. The cost of this drift is measured not only in bugs and outages, but in '
        'the enormous cognitive overhead that developers bear when they must constantly '
        'reconcile multiple sources of truth about a single system.'
    ))

    story.append(h2('2.2 The Implementation-Centric Paradigm'))
    story.append(p(
        'Contemporary programming languages are fundamentally implementation-centric. They '
        'provide constructs for defining data structures, algorithms, control flow, and '
        'communication protocols, but they treat architectural concerns as second-class '
        'citizens at best. Consider a typical web application: the architecture specifies '
        'that the system must be resilient to database failures, but this requirement lives '
        'in a design document, not in the source code. The code implements retry logic and '
        'circuit breakers, but the relationship between the architectural requirement and '
        'its implementation is implicit and undocumented in the programming language itself. '
        'If a developer removes the circuit breaker during a refactoring, no compiler or '
        'linter will flag the violation because the language has no mechanism to express that '
        'the circuit breaker was architecturally mandated.'
    ))
    story.append(p(
        'This implementation-centric paradigm also fails to leverage the reasoning capabilities '
        'of modern AI systems. When an LLM is asked to generate or modify code, it operates '
        'on the implementation level: it generates functions, classes, and statements. It has '
        'no structured access to the architectural constraints that should guide its output. '
        'The result is code that may be syntactically correct and even functionally adequate '
        'for the immediate prompt, but architecturally inconsistent with the broader system. '
        'The AI cannot reason about risks, recovery strategies, or validation criteria because '
        'the programming language provides no vocabulary for these concepts. The implementation-'
        'centric paradigm thus leaves AI-assisted development operating at a severe information '
        'deficit, generating code without understanding the architectural context that gives '
        'that code its correctness and robustness.'
    ))

    story.append(h2('2.3 The Gap Between Design and Code'))
    story.append(p(
        'Perhaps the most pernicious consequence of the current paradigm is the structural '
        'gap between design and code. Software architecture is typically expressed in terms '
        'of components, connectors, constraints, and qualities. Source code is expressed in '
        'terms of variables, functions, classes, and modules. The mapping between these two '
        'representations is neither automatic nor deterministic: the same architectural design '
        'can be implemented in countless ways, and different implementations may vary '
        'dramatically in their fidelity to the original intent. This gap is where architectural '
        'erosion occurs -- the gradual divergence between the intended architecture and the '
        'implemented system that is one of the most persistent problems in software engineering.'
    ))
    story.append(p(
        'AICL addresses this gap by eliminating it entirely. In AICL, the architectural '
        'specification is the source code. There is no gap to bridge because there is no '
        'separate representation: the goals, constraints, layers, risks, recoveries, and '
        'validations that constitute the architecture are expressed directly in the AICL '
        'source, using a formal grammar that the compiler can parse, validate, and reason '
        'about. The compiler is responsible for transforming this architectural specification '
        'into an implementation, and every element of the specification contributes to the '
        'generated code. Risks produce error-handling logic; validations produce test cases; '
        'constraints produce runtime checks; layers produce module boundaries. The gap between '
        'design and code closes not because we have found a better way to maintain two '
        'representations in sync, but because we have recognized that there should only be one.'
    ))
    story.append(p(
        'This single-representation approach has profound implications for software quality '
        'and developer productivity. When the architecture is the program, architectural '
        'erosion becomes impossible by construction: the architecture cannot drift from the '
        'code because they are the same artifact. When risks and recoveries are syntactic '
        'elements, unhandled failure modes become compiler warnings rather than production '
        'incidents. When validations are part of the language, the test suite is always '
        'consistent with the requirements because they share the same source of truth. These '
        'are not incremental improvements; they represent a categorical shift in how we think '
        'about the relationship between software design and software implementation.'
    ))

    story.append(PageBreak())

    # ── 3. CORE PHILOSOPHY ──────────────────────────────────────────────
    story.append(h1('3. Core Philosophy'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(h2('3.1 The Architecture Is the Program'))
    story.append(p(
        'The central thesis of AICL is deceptively simple: the architecture of a software '
        'system should be its program. In conventional development, architecture is a pre-code '
        'activity -- something that happens in whiteboard sessions and design documents before '
        'the first line of code is written. Once coding begins, the architecture becomes a '
        'reference document that may or may not be consulted, may or may not be updated, and '
        'may or may not bear any resemblance to the system that actually gets built. AICL '
        'inverts this relationship by making the architecture the primary artifact that the '
        'compiler processes. The developer\'s job is not to write code that implements the '
        'architecture; it is to write the architecture itself, using a formal language that '
        'captures goals, constraints, risks, recoveries, layers, and validations as structured, '
        'machine-processable specifications.'
    ))
    story.append(p(
        'This architectural specification is not merely a documentation format dressed in '
        'syntax. It is a complete, formally defined language with a precise grammar, a type '
        'system, and a compilation pipeline that transforms it into executable software. Every '
        'element of an AICL program serves a specific purpose in the compilation process: '
        'goals establish the system\'s objectives and guide the compiler\'s code generation '
        'strategy; constraints define the boundaries within which the compiler must operate; '
        'risks identify failure modes that the compiler must address with error-handling logic; '
        'recovery procedures specify how the system should respond when those failures occur; '
        'layers define the modular structure of the generated code; and validations provide '
        'the criteria against which the generated system will be tested. None of these elements '
        'are optional; they are the mandatory building blocks of every AICL program.'
    ))

    story.append(h2('3.2 A Paradigm Shift from Instructions to Architecture'))
    story.append(p(
        'Traditional programming languages are built on the paradigm of instruction: the '
        'programmer tells the computer what to do, step by step, and the computer faithfully '
        'executes those instructions. Higher-level languages reduce the number of steps '
        'required, but the fundamental relationship remains instructional. Even declarative '
        'languages, which specify what the computer should compute rather than how, ultimately '
        'produce implementations that execute instructions. AICL represents a paradigm shift '
        'from instruction-based to architecture-based programming, where the programmer '
        'specifies the structure, constraints, and qualities of the desired system, and the '
        'compiler is responsible for determining the specific instructions that realize that '
        'architecture.'
    ))
    story.append(p(
        'This shift has several important consequences. First, it elevates the level of '
        'abstraction at which developers operate from the algorithmic to the architectural. '
        'Developers reason about layers, dependencies, failure modes, and validation criteria '
        'rather than loops, conditionals, and variable assignments. Second, it makes the '
        'compiler an active participant in the development process rather than a passive '
        'translator. The AICL compiler must understand the relationships between architectural '
        'elements, reason about the implications of risks and constraints, and generate code '
        'that faithfully implements the specified architecture. Third, it creates a natural '
        'interface for AI-assisted development: the structured, formal specification of AICL '
        'provides exactly the kind of unambiguous input that AI systems need to generate '
        'correct, architecturally consistent code.'
    ))
    story.append(p(
        'The philosophical foundation of AICL rests on five design principles that flow '
        'directly from this paradigm shift. First, the architecture is the program: the '
        'specification IS the source code, not a precursor to it. Second, risks are first-'
        'class: failure modeling is mandatory, not optional, because every system must contend '
        'with the possibility of failure. Third, validation is built-in: success criteria are '
        'part of the language, not afterthoughts added in testing. Fourth, the grammar is '
        'strict: deterministic parsing ensures that the compiler can reliably process every '
        'valid AICL program. Fifth, compilation is AI-native: the compiler reasons about '
        'architecture, not just translates it, leveraging structured specifications to produce '
        'implementations that would be impractical to write by hand.'
    ))

    story.append(PageBreak())

    # ── 4. LANGUAGE DESIGN ──────────────────────────────────────────────
    story.append(h1('4. Language Design'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'AICL is organized into ten hierarchical levels, each adding a layer of expressiveness '
        'to the language. Level 1 (Architecture) is mandatory for all AICL programs and '
        'defines the core structural elements. Levels 2 through 10 are optional and can be '
        'added incrementally as the specification requires more detail. This layered design '
        'allows developers to start with a minimal architectural specification and progressively '
        'enrich it with entities, behaviors, conditions, events, concurrency directives, '
        'optimization targets, learning objectives, security requirements, and native code '
        'escapes. The following subsections describe each level in detail with illustrative '
        'examples drawn from the AICL specification.'
    ))

    # Level 1
    story.append(h2('4.1 Level 1: Architecture (Mandatory)'))
    story.append(p(
        'Level 1 is the foundation of every AICL program. It provides six core constructs -- '
        'Goal, Constraint, Risk, Recovery, Layer, and Validation -- that define the '
        'architectural intent of the system. No AICL program is valid without at least one '
        'Goal, one Layer, and one Validation. This requirement ensures that every AICL '
        'program explicitly states what it aims to achieve, how it is structured, and how '
        'its success will be measured. The architectural level is not merely a header or a '
        'preamble; it is the substantive core of the specification that drives all subsequent '
        'compilation stages.'
    ))

    story.append(h3('Goal'))
    story.append(p(
        'The Goal section defines the primary objective of the system. It answers the question: '
        '"What is this system supposed to accomplish?" Goals are stated in structured natural '
        'language and serve as the top-level directive that guides the compiler\'s code '
        'generation strategy. Every decision the compiler makes -- from module structure to '
        'error handling to test generation -- is ultimately traceable to the goals defined at '
        'this level. A well-specified goal is concrete enough to be testable but abstract '
        'enough to allow the compiler flexibility in how it achieves the objective.'
    ))
    story.append(code_label('Example: Goal specification'))
    story.append(code('Goal:\nDisplay a blue square on screen'))

    story.append(h3('Constraint'))
    story.append(p(
        'Constraints define the boundaries within which the system must operate. They express '
        'limitations, requirements, and non-negotiable conditions that the generated code must '
        'respect. Constraints can address performance requirements (such as minimum frame rates '
        'or maximum memory usage), platform restrictions, regulatory compliance, or any other '
        'bounded condition that constrains the solution space. The compiler treats constraints '
        'as hard boundaries: generated code that violates a constraint is considered incorrect, '
        'and the compiler will generate runtime checks and assertions to enforce them.'
    ))
    story.append(code_label('Example: Constraint specifications'))
    story.append(code('Constraint:\nMust run at 60 FPS minimum\n\nConstraint:\nMaximum memory usage 512 MB'))

    story.append(h3('Risk'))
    story.append(p(
        'Risk sections identify anticipated failure modes that the system may encounter during '
        'operation. Unlike traditional programming where error handling is an implementation '
        'detail, AICL requires that known risks be declared at the architectural level. This '
        'ensures that failure modeling is an integral part of the system design rather than an '
        'afterthought. Each risk declaration describes a specific condition that could cause '
        'the system to fail or degrade, and the compiler uses these declarations to generate '
        'appropriate defensive code, monitoring logic, and alerting mechanisms. Risks are '
        'paired with Recovery sections that specify corrective actions.'
    ))
    story.append(code_label('Example: Risk declarations'))
    story.append(code('Risk:\nServer becomes unavailable\n\nRisk:\nNetwork latency exceeds threshold'))

    story.append(h3('Recovery'))
    story.append(p(
        'Recovery sections define the corrective actions to be taken when a corresponding Risk '
        'materializes. They are the architectural counterpart to exception handlers, but unlike '
        'try-catch blocks in traditional languages, recoveries are specified at the design level '
        'and are automatically integrated into the generated code by the compiler. The pairing '
        'of risks and recoveries ensures that every identified failure mode has an explicit '
        'mitigation strategy. The compiler enforces this pairing during the risk analysis stage, '
        'generating warnings for any risk that lacks a corresponding recovery procedure.'
    ))
    story.append(code_label('Example: Recovery procedures'))
    story.append(code('Recovery:\nReconnect automatically with exponential backoff\n\nRecovery:\nEnable offline mode with message queue'))

    story.append(h3('Layer'))
    story.append(p(
        'Layer sections define the modular structure of the system. Each Layer represents a '
        'logical component or subsystem, and layers can contain Sublayers that further decompose '
        'the architecture. The layer hierarchy directly maps to the module structure of the '
        'generated code: each top-level layer becomes a module or package, and sublayers become '
        'submodules or classes within that package. The compiler uses the layer structure to '
        'determine dependency relationships, generate import statements, and organize the '
        'output codebase. Layers also serve as the unit of concurrency: the Parallel construct '
        'at Level 6 operates on named layers, instructing the compiler to generate concurrent '
        'execution for the specified layers.'
    ))
    story.append(code_label('Example: Layer with sublayers'))
    story.append(code(
        'Layer:\nRendering System\n'
        '    Sublayer:\n    Sprite rendering\n'
        '    Sublayer:\n    Text rendering\n'
        '    Sublayer:\n    Background rendering'
    ))

    story.append(h3('Validation'))
    story.append(p(
        'Validation sections define measurable success criteria for the system. They answer the '
        'question: "How do we know the system is working correctly?" Validations are not test '
        'implementations; they are architectural specifications of what constitutes success, '
        'expressed in structured natural language. The compiler uses these specifications to '
        'generate concrete test cases during the test generation stage. This ensures that the '
        'test suite is always derived from and consistent with the architectural specification, '
        'eliminating the common problem of tests that verify implementation details rather than '
        'requirements.'
    ))
    story.append(code_label('Example: Validation criteria'))
    story.append(code(
        'Validation:\nComplete one playable match\n\n'
        'Validation:\nMaintain 60 FPS during gameplay\n\n'
        'Validation:\nScore increments correctly on point'
    ))

    # Level 2
    story.append(h2('4.2 Level 2: Entities'))
    story.append(p(
        'Entities define the data structures of the system. Each Entity has a name and a set of '
        'typed fields, similar to structs in C or classes in object-oriented languages, but with '
        'an important distinction: AICL entities are purely declarative. They specify what data '
        'exists, not how it is stored, accessed, or manipulated. The compiler determines the '
        'appropriate representation based on the target language and the constraints specified '
        'at Level 1. Entity fields are typed using AICL\'s built-in type system, which includes '
        'primitive types (string, integer, float, boolean), temporal types (datetime), collection '
        'types (list, dict, set), and special types (any, void, bytes). Additionally, fields can '
        'reference other entities by name, establishing the data relationships that the compiler '
        'uses to generate appropriate data structures and serialization logic.'
    ))
    story.append(code_label('Example: Entity definitions'))
    story.append(code(
        'Entity Player\n'
        '    name: string\n'
        '    score: integer\n'
        '    paddle_position: float\n\n'
        'Entity Ball\n'
        '    x: float\n'
        '    y: float\n'
        '    velocity_x: float\n'
        '    velocity_y: float'
    ))
    story.append(p(
        'The entity system in AICL is deliberately simple compared to the type systems of '
        'general-purpose programming languages. There are no visibility modifiers, no inheritance '
        'hierarchies, and no generic type parameters. This simplicity is intentional: AICL '
        'entities capture the what of data, not the how. The compiler is free to add accessors, '
        'mutators, serialization methods, equality checks, and any other implementation details '
        'that the target language and the architectural constraints require. By keeping entities '
        'declarative, AICL ensures that the data model remains a clean architectural artifact '
        'that does not prematurely constrain the implementation.'
    ))

    # Level 3
    story.append(h2('4.3 Level 3: Behaviors'))
    story.append(p(
        'Behaviors define what entities do. Each Behavior has a name, a set of inputs, an '
        'optional output, and an action description. Like entities, behaviors are declarative: '
        'they specify the intent of the operation rather than its implementation. The Input '
        'section lists the entities and values that the behavior consumes; the Output section '
        'specifies what the behavior produces; and the Action section describes, in structured '
        'natural language, what the behavior does. The compiler uses these specifications to '
        'generate function signatures, implementation logic, and integration code that connects '
        'behaviors to the entities they operate on.'
    ))
    story.append(code_label('Example: Behavior definitions'))
    story.append(code(
        'Behavior SendMessage\n\n'
        'Input:\n    User Message\n\n'
        'Output:\n    DeliveredMessage\n\n'
        'Action:\n    transmit message to server and broadcast to channel'
    ))
    story.append(p(
        'The separation of inputs, outputs, and actions in AICL behaviors serves a specific '
        'architectural purpose. By explicitly declaring what goes in and what comes out, '
        'behaviors establish clear contracts that the compiler can verify against the entity '
        'definitions. If a behavior references an entity that does not exist, the compiler '
        'will generate a warning during the architecture validation stage. If a behavior\'s '
        'action description is inconsistent with its inputs and outputs, the compiler can flag '
        'this as a potential specification error. This contract-based approach to behavior '
        'specification ensures that the system\'s operational logic is internally consistent '
        'before any code is generated.'
    ))

    # Level 4
    story.append(h2('4.4 Level 4: Conditions'))
    story.append(p(
        'Conditions replace traditional if/else constructs with When/Then clauses that specify '
        'conditional behavior at the architectural level. A Condition consists of a When clause '
        'that describes the triggering circumstance and a Then clause that describes the '
        'consequence. This formulation is more expressive than a simple if/else because it '
        'focuses on the relationship between a situation and a response rather than on the '
        'control flow of the implementation. The compiler generates appropriate conditional '
        'logic from these specifications, determining where and how to implement the checks '
        'based on the system\'s layer structure and the entities involved.'
    ))
    story.append(code_label('Example: Condition specifications'))
    story.append(code(
        'Condition:\n\n'
        'When king in check\n\n'
        'Then highlight threatened squares\n\n'
        'Condition:\n\n'
        'When checkmate detected\n\n'
        'Then end game and declare winner'
    ))
    story.append(p(
        'The When/Then formulation of conditions is inspired by rule-based systems and event-'
        'condition-action patterns from active database research. Unlike imperative conditionals, '
        'which are bound to a specific point in the execution flow, AICL conditions are '
        'architectural declarations that apply wherever the specified circumstance arises. The '
        'compiler is responsible for determining the appropriate points in the generated code '
        'to check the When clause and execute the Then clause. This decoupling of specification '
        'from execution order is a key aspect of AICL\'s architecture-first philosophy: the '
        'developer specifies what must happen under what conditions, and the compiler determines '
        'how and where to implement those conditional behaviors.'
    ))

    # Level 5
    story.append(h2('4.5 Level 5: Events'))
    story.append(p(
        'Events define event-driven behaviors using On/Action pairs. An Event consists of an '
        'On clause that specifies the triggering event and an Action clause that specifies the '
        'response. Events are similar to Conditions but differ in their semantic orientation: '
        'Conditions specify state-based triggers (When some state holds), while Events specify '
        'occurrence-based triggers (On some event happens). This distinction mirrors the '
        'difference between polling and interrupt-driven architectures, and the compiler uses '
        'it to generate appropriate event-handling mechanisms in the target language.'
    ))
    story.append(code_label('Example: Event specifications'))
    story.append(code(
        'Event:\n\n'
        'On message received\n\n'
        'Action:\n    display message in channel\n\n'
        'Event:\n\n'
        'On user join\n\n'
        'Action:\n    update user list'
    ))
    story.append(p(
        'The event system in AICL provides a natural way to specify reactive behaviors that '
        'respond to external stimuli, user interactions, system notifications, or inter-component '
        'messages. In the generated code, events translate to callback registrations, event '
        'listener bindings, or message handler invocations, depending on the target language '
        'and the architectural layer in which the event occurs. The compiler also generates '
        'the necessary event dispatch infrastructure, ensuring that events are properly routed '
        'to their handlers and that event processing does not block the main execution flow when '
        'the architecture specifies concurrent execution.'
    ))

    # Level 6
    story.append(h2('4.6 Level 6: Concurrency'))
    story.append(p(
        'The Parallel construct specifies that named layers should execute concurrently. Rather '
        'than requiring developers to manage threads, locks, and synchronization primitives '
        'directly, AICL allows them to declare which architectural layers can operate '
        'independently, leaving the specific concurrency implementation to the compiler. The '
        'compiler determines the appropriate threading strategy -- whether to use threads, '
        'async tasks, processes, or some combination -- based on the target language, the '
        'constraints specified at Level 1, and the dependency relationships between layers.'
    ))
    story.append(code_label('Example: Parallel execution'))
    story.append(code(
        'Parallel:\n\n'
        'Rendering System\n'
        'Input System\n'
        'Physics Engine'
    ))
    story.append(p(
        'The Parallel construct exemplifies AICL\'s principle of architectural specification '
        'over implementation detail. Concurrency is one of the most error-prone aspects of '
        'software development, and a significant portion of concurrency bugs arise from '
        'mismatches between the intended concurrency model and its implementation. By specifying '
        'concurrency at the architectural level, AICL ensures that the concurrency model is '
        'always consistent with the layer structure, and the compiler can generate '
        'synchronization code that respects the dependencies identified during the dependency '
        'analysis stage. This approach does not eliminate all concurrency challenges, but it '
        'provides a structurally sound foundation that avoids many common pitfalls.'
    ))

    # Level 7
    story.append(h2('4.7 Level 7: Optimization'))
    story.append(p(
        'The Optimize and Priority constructs specify performance optimization targets and '
        'their relative importance. Optimization in AICL is not about writing faster code; '
        'it is about telling the compiler which qualities of the system matter most so that '
        'it can make informed trade-offs during code generation. For example, a system that '
        'optimizes for latency will generate different code than one that optimizes for '
        'throughput, even if both systems have the same architecture. The Priority keyword '
        'allows developers to rank optimization targets when multiple, potentially conflicting '
        'targets are specified.'
    ))
    story.append(code_label('Example: Optimization specifications'))
    story.append(code(
        'Optimize:\nMemory usage\n\n'
        'Optimize:\nNetwork latency'
    ))
    story.append(p(
        'The optimization level reflects a key insight about software performance: optimization '
        'is an architectural concern, not just an implementation technique. When performance '
        'targets are specified alongside the architecture, the compiler can make optimization '
        'decisions that are globally consistent rather than locally optimal. A traditional '
        'developer might optimize a hot loop without realizing that the architectural bottleneck '
        'lies elsewhere; an AICL compiler, armed with both the architectural structure and the '
        'optimization targets, can allocate optimization effort where it will have the greatest '
        'system-level impact. This architectural approach to optimization also makes it '
        'possible to re-optimize the system for different targets without changing the '
        'specification, simply by adjusting the optimization directives and recompiling.'
    ))

    # Level 8
    story.append(h2('4.8 Level 8: Learning'))
    story.append(p(
        'The Learn and Adapt constructs specify machine learning integration and adaptive '
        'behavior. The Learn section declares what the system should learn and provides a '
        'goal for the learning process. The Adapt section declares what aspect of the system '
        'should adapt and specifies the basis for adaptation. These constructs are unique to '
        'AICL and reflect its AI-native design philosophy: rather than treating machine learning '
        'as an external component to be integrated through APIs and libraries, AICL makes '
        'learning and adaptation first-class language features that the compiler can reason '
        'about and generate infrastructure for.'
    ))
    story.append(code_label('Example: Learning and adaptation'))
    story.append(code(
        'Learn:\n    User behavior\n\n'
        'Goal:\n    improve message suggestions\n\n'
        'Adapt:\n    Graphics quality\n\n'
        'Based:\n    device performance'
    ))
    story.append(p(
        'The learning level opens a new dimension in programming language design. Traditional '
        'languages assume that program behavior is fully determined by the code; AICL '
        'acknowledges that some behaviors should be learned from data and adapted over time. '
        'The compiler generates the necessary training infrastructure, inference pipelines, '
        'and feedback loops based on these specifications. For the Learn construct, the '
        'compiler generates data collection, model training, and prediction serving code. For '
        'the Adapt construct, the compiler generates monitoring, evaluation, and dynamic '
        'reconfiguration logic. The specific ML techniques used are determined by the compiler '
        'based on the learning goal, the available data, and the system constraints.'
    ))

    # Level 9
    story.append(h2('4.9 Level 9: Security'))
    story.append(p(
        'The Security construct specifies security requirements using Encrypt and Protect '
        'directives. The Encrypt directive indicates that specific data must be encrypted, '
        'while the Protect directive indicates that specific assets must be access-controlled. '
        'Like other AICL constructs, security specifications are architectural declarations '
        'that the compiler translates into concrete security implementations. This approach '
        'ensures that security is not an afterthought applied to existing code, but a '
        'structural property of the system that is built into the architecture from the start.'
    ))
    story.append(code_label('Example: Security specifications'))
    story.append(code(
        'Security:\n\n'
        'Encrypt:\n    message content\n\n'
        'Protect:\n    user credentials'
    ))
    story.append(p(
        'The security level of AICL addresses a well-known problem in software security: '
        'the gap between security policies and security implementations. Security policies '
        'are typically defined in compliance documents and threat models, while security '
        'implementations are scattered across the codebase in the form of encryption calls, '
        'access control checks, and authentication middleware. This fragmentation makes it '
        'difficult to verify that the implementation faithfully reflects the policy, and '
        'security vulnerabilities often arise from this gap. AICL\'s approach of specifying '
        'security requirements as architectural elements ensures that the compiler generates '
        'consistent, comprehensive security implementations that are traceable to the '
        'architectural specification.'
    ))

    # Level 10
    story.append(h2('4.10 Level 10: Native Code'))
    story.append(p(
        'The Native construct provides an escape hatch for low-level implementation in any '
        'programming language. It consists of a language identifier and a code block containing '
        'raw source code in the specified language. The Native construct is AICL\'s '
        'acknowledgment that some problems require hand-written, performance-critical, or '
        'platform-specific code that cannot be adequately expressed at the architectural level. '
        'It serves a similar role to inline assembly in C or foreign function interfaces in '
        'higher-level languages, but it is more general: any programming language can be '
        'embedded within a Native block.'
    ))
    story.append(code_label('Example: Native code block'))
    story.append(code(
        'Native: python {\n'
        '    import numpy as np\n'
        '    def compute_fft(signal):\n'
        '        return np.fft.fft(signal)\n'
        '}'
    ))
    story.append(p(
        'The Native construct is deliberately positioned as the highest and most optional level '
        'of AICL. Its placement at Level 10 reflects the design philosophy that native code '
        'should be a last resort, used only when the architectural specification cannot '
        'adequately capture the required behavior. In a mature AICL ecosystem, the need for '
        'Native blocks should diminish as the compiler\'s code generation capabilities improve '
        'and as higher-level AICL constructs are added to cover more implementation domains. '
        'The Native construct ensures that AICL remains practically useful even in its early '
        'stages, when the compiler cannot yet generate code for every possible architectural '
        'pattern.'
    ))

    story.append(PageBreak())

    # ── 5. FORMAL GRAMMAR ───────────────────────────────────────────────
    story.append(h1('5. Formal Grammar'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(h2('5.1 BNF Grammar'))
    story.append(p(
        'The syntax of AICL is defined by the following Backus-Naur Form (BNF) grammar. The '
        'grammar is designed for deterministic, line-based parsing: each non-blank line begins '
        'with a keyword, and indentation denotes structural nesting. This design ensures that '
        'every valid AICL program can be parsed unambiguously without lookahead beyond the '
        'current line and its indentation level. The grammar is intentionally simple, reflecting '
        'the language\'s philosophy that the structure of a specification should be immediately '
        'clear to both human readers and machine parsers.'
    ))
    story.append(code(
        '<program>       ::= <section>*\n'
        '<section>       ::= <goal-section> | <constraint-section>\n'
        '                  | <risk-section> | <recovery-section>\n'
        '                  | <layer-section> | <validation-section>\n'
        '                  | <entity-section> | <behavior-section>\n'
        '                  | <condition-section> | <event-section>\n'
        '                  | <parallel-section> | <optimize-section>\n'
        '                  | <learn-section> | <adapt-section>\n'
        '                  | <security-section> | <native-section>\n\n'
        '<goal-section>      ::= "Goal:" <text>\n'
        '<constraint-section>::= "Constraint:" <text>\n'
        '<risk-section>      ::= "Risk:" <text>\n'
        '<recovery-section>  ::= "Recovery:" <text>\n'
        '<validation-section>::= "Validation:" <text>\n'
        '<optimize-section>  ::= "Optimize:" <text>\n'
        '<priority-section>  ::= "Priority:" <text>\n\n'
        '<layer-section>     ::= "Layer:" <text> <sublayer-section>*\n'
        '<sublayer-section>  ::= "Sublayer:" <text>\n\n'
        '<entity-section>    ::= "Entity" <identifier> <entity-body>\n'
        '<entity-body>       ::= INDENT <field-def>+ DEDENT\n'
        '<field-def>         ::= <identifier> ":" <type-name>\n\n'
        '<behavior-section>  ::= "Behavior" <identifier> <behavior-body>\n'
        '<behavior-body>     ::= INDENT (<input-section> | <output-section>\n'
        '                  | <action-section>)+ DEDENT\n'
        '<input-section>     ::= "Input:" <text>\n'
        '<output-section>    ::= "Output:" <text>\n'
        '<action-section>    ::= "Action:" <text>\n\n'
        '<condition-section> ::= "Condition:" <condition-body>\n'
        '<condition-body>    ::= INDENT <when-clause> <then-clause> DEDENT\n'
        '<when-clause>       ::= "When" <text>\n'
        '<then-clause>       ::= "Then" <text>\n\n'
        '<event-section>     ::= "Event:" <event-body>\n'
        '<event-body>        ::= INDENT <on-clause> <action-section> DEDENT\n'
        '<on-clause>         ::= "On" <text>\n\n'
        '<parallel-section>  ::= "Parallel:" <layer-list>\n'
        '<layer-list>        ::= INDENT <text>+ DEDENT\n\n'
        '<learn-section>     ::= "Learn:" <text> <learn-goal>\n'
        '<learn-goal>        ::= INDENT "Goal:" <text> DEDENT\n\n'
        '<adapt-section>     ::= "Adapt:" <text> <adapt-based>\n'
        '<adapt-based>       ::= INDENT "Based:" <text> DEDENT\n\n'
        '<security-section>  ::= "Security:" <security-body>\n'
        '<security-body>     ::= INDENT (<encrypt-action>\n'
        '                  | <protect-action>)* DEDENT\n'
        '<encrypt-action>    ::= "Encrypt:" <text>\n'
        '<protect-action>    ::= "Protect:" <text>\n\n'
        '<native-section>    ::= "Native:" <language-name> <native-block>\n'
        '<native-block>      ::= "{" <raw-code> "}"\n\n'
        '<type-name>     ::= "string" | "integer" | "float" | "boolean"\n'
        '                  | "datetime" | "list" | "dict" | "set" | "any"\n'
        '                  | "void" | "bytes" | <identifier>\n'
        '<identifier>    ::= <letter> (<letter> | <digit> | "_")*\n'
        '<text>          ::= <any printable text until end of line>\n'
        '<language-name> ::= <identifier>\n'
        '<raw-code>      ::= <any text between braces>'
    ))

    story.append(h2('5.2 Keyword Table'))
    story.append(p(
        'AICL has 27 reserved keywords, organized by language level. Each keyword serves a '
        'specific purpose in the architectural specification and is recognized by the parser '
        'as a section header. Keywords are case-sensitive and must appear exactly as specified. '
        'The following table lists all AICL keywords along with their level and purpose.'
    ))

    kw_data = [
        ['Goal', '1', 'Define system objective'],
        ['Constraint', '1', 'Define system limitation'],
        ['Risk', '1', 'Define failure condition'],
        ['Recovery', '1', 'Define corrective action'],
        ['Layer', '1', 'Define architectural layer'],
        ['Sublayer', '1', 'Define sub-layer within a layer'],
        ['Validation', '1', 'Define success criterion'],
        ['Entity', '2', 'Define data entity'],
        ['Behavior', '3', 'Define entity behavior'],
        ['Input', '3', 'Define behavior input'],
        ['Output', '3', 'Define behavior output'],
        ['Action', '3/5', 'Define action to perform'],
        ['Condition', '4', 'Define conditional behavior'],
        ['When', '4', 'Condition trigger'],
        ['Then', '4', 'Condition consequence'],
        ['Event', '5', 'Define event-driven behavior'],
        ['On', '5', 'Event trigger'],
        ['Parallel', '6', 'Define concurrent execution'],
        ['Optimize', '7', 'Define optimization target'],
        ['Priority', '7', 'Define optimization priority'],
        ['Learn', '8', 'Define learning objective'],
        ['Adapt', '8', 'Define adaptive behavior'],
        ['Based', '8', 'Adaptation criterion'],
        ['Security', '9', 'Define security requirements'],
        ['Encrypt', '9', 'Encryption directive'],
        ['Protect', '9', 'Protection directive'],
        ['Native', '10', 'Inline native code'],
    ]
    story.append(make_table(
        ['Keyword', 'Level', 'Purpose'],
        kw_data,
        col_widths=[3.5*cm, 2*cm, CONTENT_W - 5.5*cm]
    ))
    story.append(caption('Table 1: AICL reserved keywords by level and purpose'))

    story.append(h2('5.3 Type System'))
    story.append(p(
        'AICL provides a built-in type system with eleven types that cover the common data '
        'categories needed in architectural specifications. The type system is deliberately '
        'minimal: it provides enough expressiveness to define entity fields and behavior '
        'signatures without introducing the complexity of a full type system with generics, '
        'type functions, or dependent types. The compiler maps AICL types to appropriate types '
        'in the target language during code generation. The following table shows the mapping '
        'from AICL types to Python target types.'
    ))

    type_data = [
        ['string', 'str', 'Text data'],
        ['integer', 'int', 'Whole numbers'],
        ['float', 'float', 'Floating-point numbers'],
        ['boolean', 'bool', 'True/False values'],
        ['datetime', 'datetime', 'Date and time'],
        ['list', 'List[Any]', 'Ordered collection'],
        ['dict', 'Dict[str, Any]', 'Key-value mapping'],
        ['set', 'set', 'Unique collection'],
        ['any', 'Any', 'Dynamic type'],
        ['void', 'None', 'No return value'],
        ['bytes', 'bytes', 'Binary data'],
    ]
    story.append(make_table(
        ['AICL Type', 'Python Target', 'Description'],
        type_data,
        col_widths=[3.5*cm, 4*cm, CONTENT_W - 7.5*cm]
    ))
    story.append(caption('Table 2: AICL type system with Python target mapping'))

    story.append(PageBreak())

    # ── 6. OPERATIONAL SEMANTICS ─────────────────────────────────────────
    story.append(h1('6. Operational Semantics'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'This section provides a formal definition of the operational semantics of AICL, '
        'describing the stages through which an AICL specification is transformed into '
        'executable software. The operational semantics define not only what each compilation '
        'stage does, but how the artifacts produced by one stage are consumed by the next. '
        'This formal treatment ensures that the behavior of the AICL compiler is well-defined '
        'and predictable, providing a foundation for verification, optimization, and future '
        'language extensions.'
    ))

    story.append(h2('6.1 Compilation Stages'))
    story.append(p(
        'The AICL compilation process consists of nine sequential stages, each producing a '
        'well-defined intermediate artifact. The stages are: (1) Specification Parsing, which '
        'transforms AICL source text into an Abstract Syntax Tree (AST); (2) Architecture '
        'Validation, which checks the AST for structural completeness and consistency; '
        '(3) Dependency Analysis, which determines the relationships between architectural '
        'layers; (4) Risk Analysis, which pairs identified risks with recovery procedures; '
        '(5) Recovery Synthesis, which generates concrete recovery logic from the risk-recovery '
        'pairs; (6) Code Generation, which produces executable source code in the target '
        'language; (7) Test Generation, which derives test cases from validation specifications; '
        '(8) Optimization, which applies performance improvements guided by the optimization '
        'directives; and (9) Final Construction, which assembles the complete output including '
        'source code, tests, and configuration files.'
    ))
    story.append(p(
        'Formally, the compilation pipeline can be expressed as a sequence of transformation '
        'functions. Let S denote the AICL source text, A the AST, V the set of validation '
        'warnings, D the dependency order, R the risk-recovery pairs, M the recovery map, '
        'C the generated source code, T the generated test code, and O the final output. The '
        'pipeline is then: A = parse(S), (V) = validate(A), D = analyze_deps(A), R = '
        'analyze_risks(A), M = synthesize_recoveries(R), C = generate_code(A, D, R, M), '
        'T = generate_tests(A, D), C = optimize(C, A), O = construct(C, T). Each transformation '
        'is deterministic given its inputs, ensuring reproducible compilation results.'
    ))

    story.append(h2('6.2 Architecture Tree IR'))
    story.append(p(
        'The Architecture Tree is the central Intermediate Representation (IR) of the AICL '
        'compiler. It is constructed from the AST after the parsing and validation stages and '
        'serves as the primary data structure for all subsequent compilation stages. The '
        'Architecture Tree transforms the flat list of AST sections into a hierarchical tree '
        'structure that represents the system\'s architecture, with risk-recovery pairs and '
        'validation criteria attached to the appropriate nodes. Each node in the tree '
        'represents an architectural layer and contains references to its associated risks, '
        'recoveries, validations, constraints, behaviors, conditions, events, optimization '
        'targets, and security actions.'
    ))
    story.append(p(
        'The Architecture Tree is rooted at a System node that represents the entire '
        'application. The root node\'s children are the top-level layers, entities, and '
        'behaviors defined in the AICL source. Layer nodes can contain sublayer children, '
        'forming a hierarchical decomposition of the system\'s modular structure. The tree '
        'provides several important operations: dependency ordering via topological sort, '
        'risk propagation from parent nodes to children, and layer lookup by name for the '
        'Parallel construct. The Architecture Tree IR is the single source of truth for all '
        'downstream compilation stages, ensuring that code generation, test generation, and '
        'optimization all operate on a consistent view of the architecture.'
    ))
    story.append(code_label('Architecture Tree Node Structure'))
    story.append(code(
        'ArchitectureNode:\n'
        '  name: str\n'
        '  node_type: layer | entity | behavior | root\n'
        '  goal: str\n'
        '  risks: List[str]\n'
        '  recoveries: List[str]\n'
        '  validations: List[str]\n'
        '  constraints: List[str]\n'
        '  behaviors: List[str]\n'
        '  conditions: List[str]\n'
        '  events: List[str]\n'
        '  optimization_targets: List[str]\n'
        '  security_actions: List[str]\n'
        '  children: List[ArchitectureNode]\n'
        '  parent: ArchitectureNode | None'
    ))

    story.append(h2('6.3 Transformation Rules'))
    story.append(p(
        'The transformation from AICL specifications to executable code follows a set of '
        'well-defined rules that map each AICL construct to its generated output. Goal '
        'sections produce top-level docstrings and configuration constants that guide runtime '
        'behavior. Constraint sections generate assertion functions and runtime checks that '
        'verify the constraints hold during execution. Risk-Recovery pairs produce try-except '
        'blocks with specific exception handlers and recovery logic. Layer sections generate '
        'module structures with appropriate imports and class hierarchies. Validation sections '
        'produce test functions that verify the specified success criteria.'
    ))
    story.append(p(
        'Entity sections generate data classes with typed fields, constructors, and '
        'serialization methods. Behavior sections generate function signatures with parameter '
        'validation and return type enforcement. Condition sections generate conditional logic '
        'that checks the When clause and executes the Then clause, placed at the appropriate '
        'location in the control flow based on the dependency analysis. Event sections generate '
        'event handler registrations and callback functions. Parallel sections generate '
        'concurrent execution scaffolding using the target language\'s concurrency primitives. '
        'Optimize sections influence code generation choices, such as data structure selection '
        'and algorithm choice, based on the specified optimization targets.'
    ))
    story.append(p(
        'Learn sections generate data collection pipelines, model training infrastructure, '
        'and inference serving code. Adapt sections generate monitoring and dynamic '
        'reconfiguration logic that adjusts system behavior based on the specified criteria. '
        'Security sections generate encryption and access control code, including key '
        'management and permission checking. Native sections are passed through verbatim to '
        'the output, with appropriate integration code generated to connect the native block '
        'to the surrounding AICL-generated code. These transformation rules are not arbitrary; '
        'they are derived from the principle that every architectural element must contribute '
        'to the generated code, ensuring that the implementation is a faithful realization of '
        'the specification.'
    ))

    story.append(PageBreak())

    # ── 7. AI-NATIVE COMPILATION PIPELINE ────────────────────────────────
    story.append(h1('7. AI-Native Compilation Pipeline'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'The AICL compilation pipeline is designed from the ground up to be AI-native, meaning '
        'that the compiler reasons about the architecture rather than merely translating it. '
        'Unlike conventional compilers that perform syntactic transformations on a fixed IR, the '
        'AICL compiler uses the rich semantic information encoded in the specification -- goals, '
        'constraints, risks, recoveries, and validations -- to guide every stage of code '
        'generation. This section describes each of the nine compilation stages in detail, '
        'explaining how architectural information flows through the pipeline and shapes the '
        'generated output.'
    ))

    stages = [
        ('7.1 Stage 1: Specification Parsing',
         'The first stage transforms AICL source text into an Abstract Syntax Tree (AST) using '
         'a line-based parser. The parser reads the source code line by line, identifying '
         'keywords, extracting values, and building the hierarchical AST structure that '
         'represents the program. AICL\'s line-based grammar makes parsing straightforward: '
         'each non-blank, non-comment line begins with a recognized keyword, and indentation '
         'levels indicate structural nesting. The parser handles both same-line values '
         '(e.g., "Goal: Display a blue square") and next-line values (e.g., "Goal:" followed '
         'by the value on the next line). The output of this stage is a complete AICLProgram '
         'AST node containing all goals, constraints, risks, recoveries, layers, validations, '
         'entities, behaviors, conditions, events, parallels, optimizations, learning '
         'directives, security sections, and native code blocks found in the source.'),

        ('7.2 Stage 2: Architecture Validation',
         'The architecture validation stage checks the AST for structural completeness and '
         'consistency. It enforces the mandatory elements: every valid AICL program must have '
         'at least one Goal, one Layer, and one Validation section. It also checks for common '
         'specification errors such as duplicate layer names, entity field references to '
         'undefined types, risks without corresponding recoveries, and recoveries without '
         'corresponding risks. The output of this stage is a list of warnings and errors that '
         'inform the developer of any structural issues in the specification. Unlike many '
         'compilers that treat warnings as optional, AICL\'s validation warnings are '
         'architecturally significant because they indicate potential gaps between the '
         'developer\'s intent and the specification\'s expressiveness.'),

        ('7.3 Stage 3: Dependency Analysis',
         'The dependency analysis stage determines the relationships between architectural '
         'layers. It constructs the layer hierarchy from the AST, identifies which layers '
         'depend on which other layers based on entity references and behavior interactions, '
         'and computes a topological ordering that respects these dependencies. This ordering '
         'is critical for code generation: layers must be initialized in dependency order, and '
         'the generated code must ensure that a layer\'s dependencies are available before it '
         'is used. The dependency analysis also identifies layers that can execute concurrently '
         '(those with no mutual dependencies), providing the information needed to implement '
         'Parallel directives.'),

        ('7.4 Stage 4: Risk Analysis',
         'The risk analysis stage examines the declared risks and pairs each risk with its '
         'corresponding recovery procedure. Risks and recoveries are paired sequentially: the '
         'first Risk is paired with the first Recovery, the second with the second, and so on. '
         'If there are more risks than recoveries, unpaired risks are flagged as warnings. If '
         'there are more recoveries than risks, the excess recoveries are treated as general '
         'fallback strategies. The compiler also attempts to distribute risks to specific '
         'architectural layers based on keyword matching between risk descriptions and layer '
         'names, enabling more targeted error handling in the generated code.'),

        ('7.5 Stage 5: Recovery Synthesis',
         'The recovery synthesis stage generates concrete recovery logic from the risk-recovery '
         'pairs identified in the previous stage. For each pair, the compiler produces a '
         'recovery function that implements the specified corrective action, wrapped in '
         'appropriate error-handling constructs. The synthesis process takes into account the '
         'target language\'s error-handling idioms (e.g., try-except in Python, try-catch in '
         'Java, Result types in Rust) and generates code that integrates seamlessly with the '
         'layer structure. The output of this stage is a recovery map that associates each '
         'risk-recovery pair with the generated recovery function and its location in the '
         'codebase.'),

        ('7.6 Stage 6: Code Generation',
         'The code generation stage is the core of the AICL compiler. It produces executable '
         'source code in the target language from the validated AST, the dependency order, the '
         'risk-recovery pairs, and the recovery map. Code generation follows the layer '
         'hierarchy: each top-level layer becomes a module, and each sublayer becomes a class '
         'or function within that module. Entities generate data classes, behaviors generate '
         'functions, conditions generate conditional logic, and events generate event handlers. '
         'Risk-recovery pairs are woven into the generated code as error-handling blocks. '
         'Constraints generate assertion functions and runtime checks. The current v0.1 '
         'implementation targets Python as the output language.'),

        ('7.7 Stage 7: Test Generation',
         'The test generation stage derives test cases from the Validation specifications '
         'defined in the AICL source. Each Validation section produces one or more test '
         'functions that verify the specified success criterion. The test generator creates '
         'test setup code that initializes the system in a known state, test execution code '
         'that exercises the relevant behaviors, and test assertion code that checks the '
         'validation criterion. The generated tests are organized by layer, mirroring the '
         'architectural structure of the system. This ensures that the test suite provides '
         'coverage at every level of the architecture, from individual behaviors to system-'
         'wide validations.'),

        ('7.8 Stage 8: Optimization',
         'The optimization stage applies performance improvements to the generated code, '
         'guided by the Optimize and Priority directives specified in the AICL source. The '
         'optimizer can apply a range of techniques including loop optimization, data structure '
         'selection, caching strategy insertion, and algorithm substitution. The specific '
         'optimizations applied depend on the optimization targets: a system that optimizes for '
         'latency may use different data structures and algorithms than one that optimizes for '
         'memory usage. The optimizer operates on the generated code rather than on a separate '
         'IR, allowing it to leverage target-language-specific optimization techniques.'),

        ('7.9 Stage 9: Final Construction',
         'The final construction stage assembles the complete output from the generated source '
         'code, test code, and any configuration files or auxiliary artifacts. It produces a '
         'directory structure that mirrors the layer hierarchy, generates a main entry point '
         'that initializes the system in dependency order and starts execution, and writes all '
         'output files to the specified directory. The final output also includes the '
         'Architecture Tree as a human-readable text file, providing developers with a '
         'visualization of the system\'s architecture as understood by the compiler.'),
    ]

    for title, body_text in stages:
        story.append(h2(title))
        story.append(p(body_text))

    story.append(p(
        'The multi-stage pipeline architecture of the AICL compiler provides several important '
        'properties. First, it ensures separation of concerns: each stage has a well-defined '
        'input and output, making it possible to verify, debug, and optimize each stage '
        'independently. Second, it enables incremental compilation: if only the optimization '
        'directives change, the compiler can re-run only the optimization stage and subsequent '
        'stages, avoiding the cost of re-parsing and re-generating the entire program. Third, '
        'it provides natural extension points for future language features: new constructs can '
        'be added by extending the parser, adding new AST nodes, and defining their '
        'transformation rules in the code generation stage without modifying the other stages.'
    ))

    story.append(PageBreak())

    # ── 8. COMPARATIVE ANALYSIS ─────────────────────────────────────────
    story.append(h1('8. Comparative Analysis'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'To understand AICL\'s position in the programming language landscape, it is essential '
        'to compare it with existing approaches across several dimensions: expressiveness, '
        'compilation model, risk handling, validation support, AI integration, and architectural '
        'fidelity. This section provides a detailed comparison with traditional programming '
        'languages, domain-specific languages and model-driven engineering tools, formal '
        'specification languages, LLM code generation tools, and intentional programming systems.'
    ))

    story.append(h2('8.1 Traditional Programming Languages'))
    story.append(p(
        'Traditional programming languages such as Java, Python, and Rust are fundamentally '
        'instruction-centric. Developers write code that specifies what the computer should do '
        'step by step, and the compiler or interpreter translates these instructions into '
        'machine-executable form. Architectural concerns -- goals, constraints, risks, '
        'recoveries, and validation criteria -- are expressed through external mechanisms such as '
        'comments, documentation, design patterns, and testing frameworks. Java provides '
        'annotations and exception hierarchies that partially capture constraints and error '
        'handling, but these are optional and inconsistently applied. Python\'s dynamic type '
        'system and lack of formal interface specifications make architectural intent even '
        'harder to express within the code. Rust\'s type system and ownership model provide '
        'strong compile-time guarantees about memory safety, but they do not address '
        'architectural concerns such as risk modeling or validation criteria. None of these '
        'languages treat risks, recoveries, or validations as syntactic elements; they are '
        'always implementation details that the developer must remember to include.'
    ))
    story.append(p(
        'The key difference between AICL and traditional languages is not the level of '
        'abstraction but the nature of the abstraction. Traditional languages abstract over '
        'machine instructions; AICL abstracts over architectural specifications. A Java '
        'developer writes a class that implements an interface; an AICL developer writes a '
        'layer that has a goal, risks, and validations. The Java class may or may not handle '
        'errors correctly; the AICL layer must specify its risks and recoveries or the compiler '
        'will warn about the omission. The Java class may or may not have tests; the AICL '
        'layer must specify its validations, and the compiler generates the tests automatically.'
    ))

    story.append(h2('8.2 DSLs and Model-Driven Engineering'))
    story.append(p(
        'Domain-specific languages (DSLs) and model-driven engineering (MDE) approaches share '
        'AICL\'s goal of raising the level of abstraction at which developers specify software. '
        'DSLs like SQL, HTML, and regular expressions provide tailored vocabularies for specific '
        'problem domains, while MDE tools like Eclipse Modeling Framework (EMF) and MetaEdit+ '
        'allow developers to define domain models and generate code from them. However, DSLs '
        'and MDE tools typically focus on structural modeling rather than architectural '
        'specification. A UML model may define class hierarchies and relationships, but it does '
        'not specify failure modes, recovery procedures, or validation criteria. A DSL may '
        'express queries or user interfaces concisely, but it does not provide a vocabulary for '
        'risks, constraints, or architectural goals.'
    ))
    story.append(p(
        'AICL differs from DSLs and MDE in three important ways. First, AICL is a general-'
        'purpose specification language, not a domain-specific one: it can express the '
        'architecture of any software system, not just systems in a particular domain. Second, '
        'AICL includes risk, recovery, and validation as first-class constructs, which are '
        'absent from most DSLs and modeling languages. Third, AICL\'s compilation pipeline is '
        'designed to be AI-native, leveraging the structured specification to enable intelligent '
        'code generation that goes beyond the template-based code generation used by most MDE '
        'tools. While MDE tools generate code by filling in templates, AICL generates code by '
        'reasoning about the architecture, producing error-handling logic, test cases, and '
        'security implementations that template-based approaches cannot provide.'
    ))

    story.append(h2('8.3 Specification Languages'))
    story.append(p(
        'Formal specification languages such as TLA+, Alloy, and Z notation provide rigorous '
        'mathematical frameworks for specifying system behavior and proving correctness '
        'properties. TLA+ allows developers to write temporal logic specifications of '
        'concurrent systems and verify them with the TLC model checker. Alloy provides a '
        'relational specification language with automatic analysis through bounded model '
        'checking. Z notation offers a mathematical notation based on set theory and predicate '
        'logic for specifying system state and operations. These languages are powerful tools '
        'for formal verification, but they operate in a different domain than AICL.'
    ))
    story.append(p(
        'The fundamental difference is that specification languages are designed for analysis, '
        'not compilation. A TLA+ specification can be model-checked to verify safety and '
        'liveness properties, but it cannot be compiled into executable software. An Alloy '
        'model can be analyzed for counterexamples, but it does not generate a running system. '
        'A Z specification can be refined into an implementation, but the refinement is a '
        'manual process that requires significant mathematical expertise. AICL, by contrast, '
        'is designed for compilation: every AICL specification can be compiled into executable '
        'software through the multi-stage pipeline. AICL sacrifices some of the mathematical '
        'rigor of formal specification languages in exchange for practical compilability, but '
        'it retains the key insight that specifications should be precise, structured, and '
        'machine-processable.'
    ))

    story.append(h2('8.4 LLM Code Generation Tools'))
    story.append(p(
        'Large language model code generation tools such as GitHub Copilot, ChatGPT, and '
        'Claude have transformed the way many developers write code. These tools accept natural '
        'language prompts and generate code that attempts to satisfy the prompt\'s intent. While '
        'impressive in their ability to produce syntactically correct and often functionally '
        'adequate code, these tools suffer from a fundamental limitation: they have no '
        'structured understanding of the architecture they are implementing. A Copilot suggestion '
        'may implement a function correctly in isolation but violate the system\'s architectural '
        'constraints, ignore known failure modes, or omit required validation checks. The '
        'natural language prompts that drive these tools are inherently ambiguous, and the '
        'generated code reflects this ambiguity.'
    ))
    story.append(p(
        'AICL provides a natural interface for LLM-assisted development that addresses these '
        'limitations. Because AICL specifications are structured, formal, and unambiguous, an '
        'LLM can parse them to understand the complete architectural context before generating '
        'code. The LLM can see the system\'s goals, constraints, risks, and validations, and '
        'generate code that is consistent with all of them. Moreover, the AICL compilation '
        'pipeline provides multiple checkpoints where LLM-generated code can be validated '
        'against the specification: architecture validation checks structural completeness, '
        'risk analysis ensures that failure modes are addressed, and test generation provides '
        'automated verification. AICL thus transforms the LLM from an unguided code generator '
        'into an architecturally aware code synthesis engine.'
    ))

    story.append(h2('8.5 Intentional Programming'))
    story.append(p(
        'Intentional programming (IP), proposed by Charles Simonyi in the 1990s, shares AICL\'s '
        'vision of elevating programming from instruction-writing to intent-expression. IP '
        'allows developers to define "intentions" -- high-level programming constructs that '
        'capture the developer\'s purpose -- and provides an environment for composing and '
        'transforming these intentions into executable code. The key insight of IP is that '
        'programming should be about capturing intent rather than specifying implementation, '
        'an insight that AICL shares and extends.'
    ))
    story.append(p(
        'However, intentional programming and AICL differ significantly in their approach and '
        'scope. IP focuses on the extensibility of programming constructs: developers can '
        'define new intentions and customize how they are rendered and compiled. AICL focuses '
        'on the completeness of architectural specification: developers must specify not only '
        'what the system should do (the "intention") but also what could go wrong (risks), '
        'how to recover from failures (recoveries), what the boundaries are (constraints), and '
        'how success is measured (validations). IP does not provide constructs for these '
        'architectural concerns; they would need to be added as custom intentions, which '
        'defeats the purpose of having a standardized vocabulary. AICL\'s built-in support for '
        'risks, recoveries, constraints, and validations ensures that these concerns are always '
        'addressed, not just when developers remember to define the appropriate intentions.'
    ))

    story.append(h2('8.6 Comparison Table'))
    story.append(p(
        'The following table provides a structured comparison of AICL with the approaches '
        'discussed above, across several key dimensions that capture the essential differences '
        'in philosophy, expressiveness, and practical utility.'
    ))

    comp_data = [
        ['AICL', 'Arch. Spec.', 'Multi-stage AI', 'Mandatory', 'Auto-gen', 'Native'],
        ['Java', 'Imperative', 'Standard', 'Optional', 'Manual', 'None'],
        ['Python', 'Imperative', 'Interpreted', 'Optional', 'Manual', 'None'],
        ['Rust', 'Imperative', 'Standard', 'Partial', 'Manual', 'None'],
        ['TLA+', 'Formal Spec.', 'Model Check', 'N/A', 'N/A', 'None'],
        ['Alloy', 'Formal Spec.', 'Analysis', 'N/A', 'N/A', 'None'],
        ['SQL (DSL)', 'Declarative', 'Query Eng.', 'Optional', 'Manual', 'None'],
        ['EMF/MDE', 'Model-Based', 'Template', 'Optional', 'Template', 'None'],
        ['Copilot', 'NLP Prompt', 'LLM Gen.', 'None', 'None', 'LLM'],
        ['Intentional', 'Intent-Based', 'IP Env.', 'Optional', 'Custom', 'None'],
    ]
    story.append(make_table(
        ['Language', 'Paradigm', 'Compilation', 'Risk Handling', 'Validation', 'AI Integ.'],
        comp_data,
        col_widths=[2.3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.2*cm]
    ))
    story.append(caption(
        'Table 3: Comparative analysis across key dimensions'
    ))

    story.append(PageBreak())

    # ── 9. EXAMPLE PROGRAMS ─────────────────────────────────────────────
    story.append(h1('9. Example Programs'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'This section presents four complete AICL programs that demonstrate the language\'s '
        'expressive range, from a minimal graphical application to a complex networked game. '
        'Each example shows how AICL\'s layered architecture, risk-recovery pairing, and '
        'validation specifications combine to create comprehensive software specifications '
        'that the compiler can transform into executable systems.'
    ))

    # Blue Square
    story.append(h2('9.1 Blue Square'))
    story.append(p(
        'The Blue Square program is the simplest non-trivial AICL application. It demonstrates '
        'the mandatory Level 1 constructs (Goal, Constraint, Risk, Recovery, Layer, Validation) '
        'in a minimal configuration. The specification defines a system that displays a blue '
        'square on screen, handles the risk of graphics device unavailability and shader '
        'compilation failure, organizes the rendering pipeline into layers, and specifies '
        'validation criteria that ensure the square is visible and the application remains '
        'responsive. Despite its simplicity, this example illustrates several key AICL '
        'principles: risks are explicitly declared and paired with recoveries, the architecture '
        'is decomposed into layers with clear responsibilities, and success criteria are '
        'specified as part of the program.'
    ))
    story.append(code(
        'Goal:\nDisplay a blue square on screen\n\n'
        'Constraint:\nMust use hardware acceleration when available\n\n'
        'Risk:\nGraphics device unavailable\n\n'
        'Recovery:\nUse software renderer\n\n'
        'Risk:\nShader compilation failure\n\n'
        'Recovery:\nLoad fallback shader\n\n'
        'Layer:\nApplication Window\n\n'
        'Layer:\nRenderer\n'
        '    Sublayer:\n    Device creation\n'
        '    Sublayer:\n    Resource management\n'
        '    Sublayer:\n    Shader system\n\n'
        'Layer:\nBlue Square\n\n'
        'Layer:\nBlue Shader\n\n'
        'Validation:\nBlue square is visible on screen\n\n'
        'Validation:\nApplication remains responsive for 60 seconds'
    ))

    # Pong Game
    story.append(h2('9.2 Pong Game'))
    story.append(p(
        'The Pong Game example extends the architectural specification with Levels 2 through 6, '
        'demonstrating entities, behaviors, conditions, events, and concurrency. The '
        'specification defines Player and Ball entities, MovePaddle and UpdateBall behaviors, '
        'conditions for paddle collision and score thresholds, events for key presses and '
        'collisions, and a Parallel directive that executes the rendering, input, and physics '
        'layers concurrently. This example shows how AICL scales from simple to complex '
        'applications: the same architectural framework that describes a blue square also '
        'describes a real-time game with physics, input handling, and concurrent execution.'
    ))
    story.append(code(
        'Goal:\nBuild a Pong game\n\n'
        'Constraint:\nMust run at 60 FPS minimum\n\n'
        'Risk:\nBall leaves play area\n'
        'Recovery:\nClamp ball position to boundaries\n\n'
        'Risk:\nScore not displayed correctly\n'
        'Recovery:\nReinitialize score display\n\n'
        'Risk:\nInput lag detected\n'
        'Recovery:\nEnable input buffering\n\n'
        'Layer:\nWindow Manager\n\n'
        'Layer:\nRendering System\n'
        '    Sublayer:\n    Sprite rendering\n'
        '    Sublayer:\n    Text rendering\n'
        '    Sublayer:\n    Background rendering\n\n'
        'Layer:\nInput System\n\n'
        'Layer:\nPhysics Engine\n'
        '    Sublayer:\n    Ball movement\n'
        '    Sublayer:\n    Collision detection\n'
        '    Sublayer:\n    Paddle movement\n\n'
        'Layer:\nGame Logic\n'
        '    Sublayer:\n    Score tracking\n'
        '    Sublayer:\n    Game state management\n'
        '    Sublayer:\n    Round management\n\n'
        'Entity Player\n'
        '    name: string\n'
        '    score: integer\n'
        '    paddle_position: float\n\n'
        'Entity Ball\n'
        '    x: float\n'
        '    y: float\n'
        '    velocity_x: float\n'
        '    velocity_y: float\n\n'
        'Behavior MovePaddle\n'
        'Input:\n    Player direction string\n'
        'Action:\n    Update paddle position based on direction\n\n'
        'Condition:\n'
        'When ball hits paddle\n'
        'Then reflect ball velocity\n\n'
        'Event:\n'
        'On key press\n'
        'Action:\n    move corresponding paddle\n\n'
        'Parallel:\n'
        'Rendering System\n'
        'Input System\n'
        'Physics Engine'
    ))

    # Chat Application
    story.append(h2('9.3 Chat Application'))
    story.append(p(
        'The Chat Application example demonstrates AICL\'s ability to specify a networked, '
        'concurrent application with multiple constraints, complex risk-recovery pairs, and '
        'security requirements. It uses Levels 1 through 9, including Optimization (Level 7), '
        'Learning (Level 8), and Security (Level 9). The specification addresses network '
        'unavailability, latency thresholds, and message delivery failures with specific '
        'recovery strategies including exponential backoff, offline mode, and local storage '
        'with retry. The Security section mandates encryption of message content and protection '
        'of user credentials, while the Learn section specifies that the system should learn '
        'from user behavior to improve message suggestions.'
    ))
    story.append(code(
        'Goal:\nCreate a multiplayer chat application\n\n'
        'Constraint:\nMust support at least 100 concurrent users\n\n'
        'Constraint:\nMaximum memory usage 512 MB\n\n'
        'Risk:\nServer becomes unavailable\n'
        'Recovery:\nReconnect automatically with exponential backoff\n\n'
        'Risk:\nNetwork latency exceeds threshold\n'
        'Recovery:\nEnable offline mode with message queue\n\n'
        'Entity User\n'
        '    name: string\n'
        '    id: integer\n'
        '    status: string\n\n'
        'Entity Message\n'
        '    content: string\n'
        '    timestamp: datetime\n'
        '    sender: User\n\n'
        'Optimize:\nMemory usage\n\n'
        'Security:\n'
        'Encrypt:\n    message content\n'
        'Protect:\n    user credentials\n\n'
        'Learn:\n    User behavior\n'
        'Goal:\n    improve message suggestions\n\n'
        'Validation:\nSend and receive messages successfully\n\n'
        'Validation:\nAverage latency below 100 ms'
    ))

    # Chess Game
    story.append(h2('9.4 Chess Game'))
    story.append(p(
        'The Chess Game example represents the most complex AICL specification in this paper, '
        'demonstrating all ten language levels including the Native code escape hatch. It '
        'specifies a multiplayer chess game with network support, move validation, check and '
        'checkmate detection, and adaptive graphics quality. The specification defines Player, '
        'ChessPiece, and GameState entities, MakeMove and ValidateMove behaviors, conditions '
        'for check, checkmate, and stalemate, events for piece selection and move submission, '
        'and an Adapt directive that adjusts graphics quality based on device performance. '
        'This example demonstrates that AICL can express the full complexity of a real-world '
        'application, from high-level architectural goals to low-level implementation details.'
    ))
    story.append(code(
        'Goal:\nCreate a multiplayer chess game\n\n'
        'Constraint:\nMust run on mobile devices\n\n'
        'Constraint:\nMove validation must be under 10 ms\n\n'
        'Risk:\nInvalid move received\n'
        'Recovery:\nReject move and request resend\n\n'
        'Entity ChessPiece\n'
        '    type: string\n'
        '    color: string\n'
        '    position: string\n'
        '    has_moved: boolean\n\n'
        'Entity GameState\n'
        '    board: list\n'
        '    current_turn: string\n'
        '    move_count: integer\n'
        '    status: string\n\n'
        'Condition:\n'
        'When checkmate detected\n'
        'Then end game and declare winner\n\n'
        'Adapt:\n    Graphics quality\n'
        'Based:\n    device performance\n\n'
        'Security:\n'
        'Encrypt:\n    game state\n'
        'Protect:\n    player credentials\n\n'
        'Validation:\nTwo players complete a full game\n\n'
        'Validation:\nMove validation completes in under 10 ms'
    ))

    story.append(PageBreak())

    # ── 10. RESEARCH HYPOTHESES ──────────────────────────────────────────
    story.append(h1('10. Research Hypotheses'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'AICL is grounded in a set of research hypotheses that motivate its design and define '
        'the empirical questions that future work must address. Each hypothesis represents a '
        'testable claim about the relationship between specification-first programming and '
        'software quality, developer productivity, or system reliability. These hypotheses are '
        'not assertions of fact; they are conjectures that the AICL project aims to validate '
        'or refute through controlled experiments, case studies, and real-world deployments.'
    ))

    story.append(h2('H1: Architecture-Code Consistency'))
    story.append(p(
        'Software systems specified in AICL will exhibit higher consistency between their '
        'documented architecture and their implementation compared to systems developed using '
        'traditional programming languages. This hypothesis follows directly from AICL\'s core '
        'principle that the architecture is the program: because there is only one artifact, '
        'architectural drift is impossible by construction. Testing this hypothesis requires '
        'comparing the architectural fidelity of systems built with and without AICL over '
        'extended development periods, measuring the degree to which implementation diverges '
        'from the documented architecture.'
    ))

    story.append(h2('H2: Failure Coverage'))
    story.append(p(
        'AICL\'s mandatory risk-recovery specification will result in higher coverage of known '
        'failure modes compared to traditional error-handling approaches. In conventional '
        'development, error handling is an implementation detail that developers may forget, '
        'deprioritize, or implement inconsistently. In AICL, every risk must have a '
        'corresponding recovery, and the compiler enforces this pairing during the risk '
        'analysis stage. This hypothesis can be tested by comparing the ratio of handled to '
        'unhandled failure modes in AICL-specified systems versus traditionally developed '
        'systems of similar complexity.'
    ))

    story.append(h2('H3: Specification-to-Test Traceability'))
    story.append(p(
        'AICL\'s validation-driven test generation will produce test suites with higher '
        'traceability to system requirements compared to manually written test suites. '
        'Traditional test suites often verify implementation details rather than requirements, '
        'and the mapping between test cases and requirements is frequently implicit or '
        'undocumented. AICL generates tests directly from validation specifications, creating '
        'an explicit, one-to-one mapping between requirements and test cases. This hypothesis '
        'can be tested by measuring the traceability of test suites in AICL projects versus '
        'conventional projects, using coverage of requirements as the primary metric.'
    ))

    story.append(h2('H4: AI-Assisted Code Quality'))
    story.append(p(
        'LLM-assisted code generation guided by AICL specifications will produce higher-quality '
        'code compared to LLM-assisted generation from natural language prompts. The structured, '
        'formal nature of AICL specifications provides LLMs with unambiguous information about '
        'goals, constraints, risks, and validations, enabling them to generate code that is '
        'architecturally consistent and failure-aware. This hypothesis can be tested through '
        'controlled experiments where the same development tasks are performed using AICL '
        'specifications and natural language prompts, with code quality measured across '
        'dimensions including correctness, robustness, security, and adherence to architectural '
        'constraints.'
    ))

    story.append(h2('H5: Developer Productivity'))
    story.append(p(
        'For systems of sufficient complexity, AICL will improve developer productivity by '
        'reducing the total effort required to produce a correctly functioning system. While '
        'writing AICL specifications requires upfront investment in architectural thinking, '
        'this investment is expected to pay off through reduced debugging, fewer production '
        'incidents, and less time spent maintaining consistency between design documents and '
        'code. This hypothesis can be tested through longitudinal studies that measure the '
        'total development time, defect rate, and maintenance effort for AICL-specified '
        'systems versus traditionally developed systems of comparable scope and complexity.'
    ))

    story.append(PageBreak())

    # ── 11. IMPLEMENTATION ──────────────────────────────────────────────
    story.append(h1('11. Implementation'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'The current AICL implementation, version 0.1, provides a complete parser, a '
        'multi-stage compiler targeting Python, and an Architecture Tree intermediate '
        'representation. The implementation is written in Python and consists of approximately '
        '2,500 lines of code distributed across six modules: tokenizer, parser, AST nodes, '
        'architecture tree, compiler, and CLI. This section describes the key architectural '
        'decisions and implementation details of each component.'
    ))

    story.append(h2('11.1 Parser Architecture'))
    story.append(p(
        'The AICL parser uses a line-based parsing strategy that reads source code line by '
        'line, identifying keywords at the start of each line and extracting their values. '
        'This approach is well-suited to AICL\'s grammar, where each non-blank line begins '
        'with a keyword and indentation indicates structural nesting. The parser maintains a '
        'current position in the source and advances through the lines sequentially, building '
        'the AST incrementally. It supports both same-line values (e.g., "Goal: Display a '
        'blue square") and next-line values (e.g., "Goal:" followed by the value on the next '
        'line), handling the flexibility that AICL\'s grammar allows while maintaining '
        'deterministic parsing behavior.'
    ))
    story.append(p(
        'The parser identifies 27 reserved keywords and dispatches each recognized keyword '
        'to a specialized parsing method. Simple value keywords (Goal, Constraint, Risk, '
        'Recovery, Validation, Optimize, Priority) are handled directly by extracting the '
        'value text. Structured keywords (Layer, Entity, Behavior, Condition, Event, '
        'Parallel, Learn, Adapt, Security, Native) require reading an indented block of '
        'sub-keywords and values. The parser uses indentation counting to determine block '
        'boundaries, supporting both space and tab indentation. Error handling is implemented '
        'through a ParseError exception that includes the line number where the error was '
        'detected, providing developers with precise feedback about specification errors.'
    ))

    story.append(h2('11.2 Compiler Pipeline'))
    story.append(p(
        'The compiler implements the nine-stage compilation pipeline described in Section 7. '
        'Each stage is implemented as a method on the Compiler class, taking the output of '
        'the previous stage as input and producing the input for the next stage. The compiler '
        'maintains a list of warnings and errors that accumulate through the pipeline, and a '
        'list of completed stages that enables partial compilation and progress reporting. '
        'The current implementation targets Python as the output language, generating Python '
        'source code with dataclasses for entities, functions for behaviors, and try-except '
        'blocks for risk-recovery pairs.'
    ))
    story.append(p(
        'Code generation in the v0.1 compiler follows a template-based approach where each '
        'AICL construct maps to a Python code template. Entity sections generate dataclass '
        'definitions. Behavior sections generate function definitions with parameter validation. '
        'Risk-recovery pairs generate try-except blocks with specific exception handlers. '
        'Validation sections generate test functions using Python\'s unittest framework. '
        'Layer sections generate module-level organization with appropriate imports. While '
        'template-based generation limits the sophistication of the output, it provides a '
        'reliable foundation that can be extended with more intelligent generation strategies '
        'in future versions. The compiler also produces an Architecture Tree visualization '
        'that shows the hierarchical structure of the specification with associated risks, '
        'recoveries, validations, and constraints.'
    ))

    story.append(h2('11.3 Architecture Tree IR'))
    story.append(p(
        'The Architecture Tree intermediate representation is implemented as a tree data '
        'structure with ArchitectureNode objects that can have children, forming a hierarchical '
        'representation of the system\'s architecture. Each node stores its name, type (root, '
        'layer, entity, or behavior), and lists of associated architectural elements including '
        'risks, recoveries, validations, constraints, behaviors, conditions, events, '
        'optimization targets, and security actions. The tree provides methods for finding '
        'nodes by name, computing dependency order through topological sort, and rendering '
        'the tree as a human-readable string with Unicode box-drawing characters.'
    ))
    story.append(p(
        'The Architecture Tree is constructed from the AST after parsing by iterating through '
        'the program\'s sections and creating appropriate nodes. Global risks, recoveries, '
        'validations, and constraints are attached to the root node. Layer nodes are created '
        'with their sublayer children. Entity and behavior nodes are added as children of the '
        'root. Conditions and events are attached to the root for later distribution by the '
        'compiler. The tree also implements a risk distribution algorithm that attempts to '
        'match global risks to specific layers based on keyword overlap between risk '
        'descriptions and layer names. This distribution enables more targeted error handling '
        'in the generated code, as the compiler can place recovery logic in the layers most '
        'likely to encounter the corresponding failures.'
    ))

    story.append(PageBreak())

    # ── 12. ROADMAP ─────────────────────────────────────────────────────
    story.append(h1('12. Roadmap'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'The AICL project follows an incremental development roadmap that gradually expands '
        'the language\'s capabilities, the compiler\'s intelligence, and the ecosystem\'s '
        'tooling. Each version adds functionality while maintaining backward compatibility '
        'with existing AICL specifications. The roadmap is organized into four major releases, '
        'each building on the foundation established by its predecessor.'
    ))

    roadmap_data = [
        ['v0.1', 'Current', 'Core parser, 9-stage compiler, Architecture Tree IR, Python code '
         'generation, test generation, CLI tool. Supports all 10 language levels with '
         'template-based code generation.'],
        ['v0.2', 'Q3 2026', 'Enhanced code generation with pattern-based templates, '
         'multi-language targets (Rust, TypeScript), improved risk distribution, '
         'validation-to-test traceability, and interactive specification validation.'],
        ['v0.3', 'Q1 2027', 'LLM-integrated compilation: AI-assisted code generation that '
         'uses the structured specification to guide LLM output, automatic specification '
         'completion, and specification quality scoring. Support for compilation caching '
         'and incremental builds.'],
        ['v1.0', 'Q3 2027', 'Production release: stable grammar, comprehensive documentation, '
         'IDE integration (VS Code, JetBrains), formal verification of critical compilation '
         'stages, and performance benchmarks against hand-written code.'],
        ['v2.0', '2028', 'Multi-agent compilation: specialized AI agents for different '
         'compilation stages, collaborative specification editing, real-time architectural '
         'feedback, and automatic architectural pattern recognition.'],
        ['v3.0', '2029', 'Self-evolving compiler: the compiler learns from compilation '
         'history to improve code generation quality, adapts to project-specific patterns, '
         'and suggests specification improvements based on runtime behavior.'],
        ['v4.0', '2030', 'Full AI-native platform: AICL as the foundation of an AI-native '
         'software development ecosystem, with specification-first development as the default '
         'paradigm for AI-assisted programming.'],
    ]
    story.append(make_table(
        ['Version', 'Timeline', 'Description'],
        roadmap_data,
        col_widths=[1.8*cm, 2.2*cm, CONTENT_W - 4*cm]
    ))
    story.append(caption('Table 4: AICL development roadmap'))

    story.append(p(
        'The roadmap reflects AICL\'s long-term vision of transforming software development '
        'from an instruction-writing activity to an architecture-specifying one. Each version '
        'brings this vision closer to reality by improving the compiler\'s ability to reason '
        'about specifications and generate high-quality code. The v0.1 release establishes the '
        'foundational language and compilation infrastructure. Subsequent versions enhance the '
        'compiler with AI integration, formal verification, and multi-agent capabilities, '
        'culminating in a v4.0 platform where specification-first development is the natural '
        'and preferred way to build software with AI assistance.'
    ))

    story.append(PageBreak())

    # ── 13. RELATED WORK ────────────────────────────────────────────────
    story.append(h1('13. Related Work'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'AICL sits at the intersection of several research traditions in programming languages, '
        'software architecture, formal methods, and artificial intelligence. This section '
        'surveys the academic context that informs AICL\'s design and positions it relative to '
        'prior work in each of these areas.'
    ))

    story.append(h2('13.1 Programming Language Design'))
    story.append(p(
        'The design of AICL draws on decades of research in programming language theory, '
        'particularly the tradition of raising the level of abstraction at which programmers '
        'express their intent. The progression from machine code to assembly language to '
        'high-level languages to domain-specific languages is well-documented in the '
        'programming language literature. AICL extends this progression by introducing a new '
        'abstraction level -- the architectural specification -- that encompasses not only what '
        'the system should compute but how it should handle failures, what constraints it must '
        'respect, and how its success should be validated. This holistic approach to language '
        'design is informed by the work of Sebesta on programming language concepts and by '
        'the design principles of declarative languages such as Prolog and SQL, which '
        'demonstrated that specifying what rather than how can dramatically improve developer '
        'productivity and code correctness.'
    ))

    story.append(h2('13.2 Software Architecture'))
    story.append(p(
        'AICL\'s emphasis on architectural specification as the primary programming artifact '
        'is deeply informed by research in software architecture. The concept of architectural '
        'styles, as formalized by Perry and Wolf and extended by Shaw and Garlan, provides the '
        'theoretical foundation for AICL\'s layer-based decomposition. The Architecture Tree '
        'IR in AICL is analogous to the architectural views described in Kruchten\'s 4+1 view '
        'model, but it integrates these views into a single, compilable representation. '
        'Research on architectural erosion by Perry, German, and others motivates AICL\'s '
        'core principle that the architecture is the program: if the architecture and the code '
        'are the same artifact, erosion becomes impossible by construction. The concept of '
        'architectural tactics -- reusable solutions for achieving quality attributes such as '
        'reliability and performance -- informs AICL\'s risk-recovery and optimization '
        'constructs, which provide a vocabulary for specifying these tactics at the '
        'architectural level.'
    ))

    story.append(h2('13.3 Formal Methods'))
    story.append(p(
        'Formal methods research has produced specification languages and verification tools '
        'that provide rigorous mathematical frameworks for reasoning about software correctness. '
        'TLA+, developed by Lamport, combines temporal logic with set theory to specify and '
        'verify concurrent systems. Alloy, developed by Jackson, provides a lightweight '
        'relational specification language with automatic analysis. The Z notation, developed '
        'at Oxford, offers a mathematical specification language based on Zermelo-Fraenkel set '
        'theory. While these formalisms provide stronger verification guarantees than AICL, '
        'they are not designed for compilation into executable software. AICL occupies a middle '
        'ground between formal specification and implementation: it provides structured, '
        'machine-processable specifications that can be compiled, sacrificing some mathematical '
        'rigor in exchange for practical compilability. The B-method, developed by Abrial, is '
        'perhaps the closest formal method to AICL in that it supports refinement from '
        'specification to implementation, but B-method refinement is a manual, mathematically '
        'intensive process, whereas AICL compilation is automated.'
    ))

    story.append(h2('13.4 AI-Assisted Software Development'))
    story.append(p(
        'The emergence of large language models for code generation has created new possibilities '
        'and challenges for programming language design. Research by Chen et al. on Codex and '
        'by Li et al. on AlphaCode has demonstrated that LLMs can generate functionally correct '
        'code from natural language descriptions, but these systems lack architectural awareness. '
        'The work of Jiang et al. on self-debugging and Shinn et al. on reflexion shows that '
        'LLM performance improves when feedback loops are introduced, suggesting that structured '
        'specifications like AICL could significantly improve LLM-assisted code quality. AICL\'s '
        'contribution to this line of research is the provision of a formal, structured input '
        'format that enables LLMs to understand and respect architectural constraints during '
        'code generation, transforming them from unguided generators into architecturally aware '
        'code synthesis tools.'
    ))

    story.append(h2('13.5 Model-Driven Engineering'))
    story.append(p(
        'Model-driven engineering (MDE) research provides important precedents for AICL\'s '
        'approach to generating code from abstract specifications. The Model-Driven Architecture '
        '(MDA) initiative, standardized by the Object Management Group, defines a framework for '
        'transforming platform-independent models into platform-specific implementations. '
        'Research by Schmidt on model-driven software engineering and by Voelter on '
        'domain-specific modeling languages has demonstrated the viability of generating code '
        'from abstract models, but MDE tools typically focus on structural modeling rather '
        'than architectural specification. AICL extends the MDE approach by incorporating '
        'risks, recoveries, constraints, and validations as first-class modeling elements, '
        'and by designing the compilation pipeline to be AI-native rather than template-based. '
        'The Eclipse Modeling Framework and tools like MetaEdit+ provide mature infrastructure '
        'for model-driven development, and future versions of AICL may leverage these '
        'platforms for specification editing and visualization.'
    ))

    story.append(PageBreak())

    # ── 14. CONCLUSION ──────────────────────────────────────────────────
    story.append(h1('14. Conclusion'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    story.append(p(
        'AICL represents a fundamental rethinking of the relationship between software '
        'architecture and software implementation. By making the architectural specification '
        'the primary artifact that the compiler processes, AICL eliminates the gap between '
        'design and code that has plagued software engineering for decades. By mandating '
        'risks, recoveries, and validations as syntactic elements, AICL ensures that failure '
        'modeling and verification are integral parts of every software system, not optional '
        'afterthoughts. By designing the compilation pipeline to be AI-native, AICL provides '
        'a natural interface for AI-assisted development that enables architecturally aware '
        'code generation rather than unguided code synthesis.'
    ))
    story.append(p(
        'The language design presented in this white paper -- ten hierarchical levels, 27 '
        'reserved keywords, a formal BNF grammar, and a nine-stage compilation pipeline -- '
        'provides a complete specification of AICL v0.1. The implementation demonstrates that '
        'the core concepts are practically realizable: the parser correctly handles all '
        'language levels, the compiler generates executable Python code from architectural '
        'specifications, and the Architecture Tree IR provides a rich intermediate '
        'representation that supports dependency analysis, risk propagation, and code '
        'generation. The four example programs -- Blue Square, Pong, Chat, and Chess -- '
        'demonstrate that AICL can express systems of varying complexity, from simple '
        'graphical applications to networked multiplayer games.'
    ))
    story.append(p(
        'The research hypotheses presented in Section 10 define the empirical program that '
        'will determine whether AICL\'s theoretical advantages translate into practical '
        'benefits. If these hypotheses are validated, AICL could represent a paradigm shift '
        'in how we develop software: from writing instructions that computers execute, to '
        'specifying architectures that compilers realize. This shift would not eliminate the '
        'need for human expertise in software development, but it would redirect that '
        'expertise from low-level implementation details to high-level architectural thinking, '
        'which is precisely where human judgment and creativity add the most value.'
    ))
    story.append(p(
        'The roadmap from v0.1 to v4.0 charts an ambitious but achievable path from the '
        'current prototype to a mature, AI-native development platform. Each version adds '
        'capabilities that build on the foundation established by its predecessor, and the '
        'incremental approach ensures that the language and compiler evolve in response to '
        'real-world usage and empirical evidence. We believe that specification-first '
        'programming, as embodied by AICL, represents the natural next step in the evolution '
        'of programming languages -- a step that is both enabled and necessitated by the rise '
        'of AI-assisted software development.'
    ))

    story.append(PageBreak())

    # ── REFERENCES ──────────────────────────────────────────────────────
    story.append(h1('References'))
    story.append(AccentRule(CONTENT_W, 1.5))
    story.append(spacer(0.3))

    refs = [
        '[1] R. Sebesta, <i>Concepts of Programming Languages</i>, 12th ed. Pearson, 2019.',
        '[2] D. Perry and A. Wolf, "Foundations for the Study of Software Architecture," '
        '<i>ACM SIGSOFT Software Engineering Notes</i>, vol. 17, no. 4, pp. 40-52, 1992.',
        '[3] M. Shaw and D. Garlan, <i>Software Architecture: Perspectives on an Emerging '
        'Discipline</i>. Prentice Hall, 1996.',
        '[4] P. Kruchten, "The 4+1 View Model of Architecture," <i>IEEE Software</i>, '
        'vol. 12, no. 6, pp. 42-50, 1995.',
        '[5] L. Bass, P. Clements, and R. Kazman, <i>Software Architecture in Practice</i>, '
        '4th ed. Addison-Wesley, 2021.',
        '[6] L. Lamport, "Specifying Systems: The TLA+ Language and Tools for Hardware '
        'and Software Engineers," Addison-Wesley, 2002.',
        '[7] D. Jackson, <i>Software Abstractions: Logic, Language, and Analysis</i>, '
        'revised ed. MIT Press, 2012.',
        '[8] J.-R. Abrial, <i>The B-Book: Assigning Programs to Meanings</i>. Cambridge '
        'University Press, 1996.',
        '[9] M. Chen, J. Tworek, H. Jun, et al., "Evaluating Large Language Models Trained '
        'on Code," <i>arXiv preprint arXiv:2107.03374</i>, 2021.',
        '[10] Y. Li, D. Choi, J. Chung, et al., "Competition-Level Code Generation with '
        'AlphaCode," <i>Science</i>, vol. 378, no. 6624, pp. 1092-1097, 2022.',
        '[11] X. Jiang, M. Ibrahim, and A. Ou, "Self-Debugging: Teaching LLMs to Debug Their '
        'Own Code," <i>arXiv preprint arXiv:2304.05128</i>, 2023.',
        '[12] N. Shinn, F. Cassano, A. Gopinath, K. Narasimhan, and S. Yao, "Reflexion: '
        'Language Agents with Verbal Reinforcement Learning," <i>NeurIPS</i>, 2023.',
        '[13] C. Simonyi, "Intentional Programming: Innovation in the Modeling Age," '
        '<i>Proceedings of the Technology of Object-Oriented Languages and Systems</i>, 1998.',
        '[14] D. Schmidt, "Model-Driven Software Engineering," <i>IEEE Computer</i>, '
        'vol. 39, no. 2, pp. 25-31, 2006.',
        '[15] M. Voelter, <i>DSL Engineering: Designing, Implementing and Using '
        'Domain-Specific Languages</i>. CreateSpace, 2013.',
        '[16] Object Management Group, "MDA Guide Version 2.0," OMG Document ormsc/2014-06-01, 2014.',
        '[17] E. Evans, <i>Domain-Driven Design: Tackling Complexity in the Heart of '
        'Software</i>. Addison-Wesley, 2003.',
        '[18] A. van Deursen, P. Klint, and J. Visser, "Domain-Specific Languages: An '
        'Annotated Bibliography," <i>ACM SIGPLAN Notices</i>, vol. 35, no. 6, pp. 26-36, 2000.',
        '[19] J. Spivey, <i>The Z Notation: A Reference Manual</i>, 2nd ed. Prentice Hall, 1992.',
        '[20] F. Buschmann, R. Meunier, H. Rohnert, P. Sommerlad, and M. Stal, '
        '<i>Pattern-Oriented Software Architecture: A System of Patterns</i>. Wiley, 1996.',
        '[21] D. Garlan, "Software Architecture: A Travel Guide," in <i>Software '
        'Engineering: International Summer Schools, ISSSE 2006-2008</i>. Springer, 2008.',
        '[22] K. Czarnecki and U. Eisenecker, <i>Generative Programming: Methods, Tools, '
        'and Applications</i>. Addison-Wesley, 2000.',
        '[23] B. Pierce, <i>Types and Programming Languages</i>. MIT Press, 2002.',
        '[24] A. Appel, <i>Modern Compiler Implementation in ML</i>. Cambridge University '
        'Press, 2004.',
        '[25] S. Ghosh, <i>DSLs in Action</i>. Manning Publications, 2010.',
    ]

    for ref in refs:
        story.append(Paragraph(ref, sRef))

    return story


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, 'whitepaper.pdf')

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title='AICL: AI-Centric Language',
        author='Philippe-Antoine',
        subject='A Specification-First Programming Language for AI-Native Software Development',
    )

    story = build_document()
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    # Report
    size = os.path.getsize(output_path)
    print(f"PDF generated: {output_path}")
    print(f"File size: {size:,} bytes ({size/1024:.1f} KB)")

    # Count pages
    from reportlab.lib.utils import open_for_read
    from reportlab.pdfbase.pdfmetrics import _fonts
    # Use a simpler page count method
    from PyPDF2 import PdfReader
    try:
        reader = PdfReader(output_path)
        page_count = len(reader.pages)
        print(f"Page count: {page_count}")
    except ImportError:
        # Fallback: count page markers in the PDF
        with open(output_path, 'rb') as f:
            content = f.read()
        page_count = content.count(b'/Type /Page') - content.count(b'/Type /Pages')
        print(f"Page count (approximate): {page_count}")

if __name__ == '__main__':
    main()
