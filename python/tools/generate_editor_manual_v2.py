#!/usr/bin/env python3
"""Generate AICL Editor Manual v2.0 PDF — Updated with AI Chat, Agentic Actions, Error Display."""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import HexColor

# ── Palette ──
PAGE_BG       = colors.HexColor('#f5f6f6')
SECTION_BG    = colors.HexColor('#f1f2f2')
CARD_BG       = colors.HexColor('#e5e8ea')
TABLE_STRIPE  = colors.HexColor('#f2f3f4')
HEADER_FILL   = colors.HexColor('#476372')
BORDER        = colors.HexColor('#a6b7c0')
ACCENT        = colors.HexColor('#b85838')
TEXT_PRIMARY   = colors.HexColor('#232526')
TEXT_MUTED     = colors.HexColor('#7b8185')
SEM_SUCCESS   = colors.HexColor('#4f9165')
SEM_ERROR     = colors.HexColor('#8d4b45')
SEM_INFO      = colors.HexColor('#4b77a3')

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'AICL_Editor_Manual.pdf')

# ── Styles ──
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name='CoverTitle',
    fontName='Helvetica-Bold',
    fontSize=28,
    leading=34,
    textColor=colors.white,
    alignment=TA_CENTER,
    spaceAfter=12,
))

styles.add(ParagraphStyle(
    name='CoverSubtitle',
    fontName='Helvetica',
    fontSize=14,
    leading=20,
    textColor=colors.HexColor('#d0d8dc'),
    alignment=TA_CENTER,
    spaceAfter=6,
))

styles.add(ParagraphStyle(
    name='CoverMeta',
    fontName='Helvetica',
    fontSize=11,
    leading=16,
    textColor=colors.HexColor('#a0acb4'),
    alignment=TA_CENTER,
    spaceAfter=4,
))

styles.add(ParagraphStyle(
    name='H1',
    fontName='Helvetica-Bold',
    fontSize=20,
    leading=26,
    textColor=HEADER_FILL,
    spaceBefore=24,
    spaceAfter=10,
    borderPadding=(0, 0, 4, 0),
))

styles.add(ParagraphStyle(
    name='H2',
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=20,
    textColor=colors.HexColor('#3a5563'),
    spaceBefore=16,
    spaceAfter=6,
))

styles.add(ParagraphStyle(
    name='H3',
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=16,
    textColor=colors.HexColor('#466879'),
    spaceBefore=10,
    spaceAfter=4,
))

styles.add(ParagraphStyle(
    name='Body2',
    fontName='Helvetica',
    fontSize=10,
    leading=15,
    textColor=TEXT_PRIMARY,
    alignment=TA_JUSTIFY,
    spaceAfter=6,
))

styles.add(ParagraphStyle(
    name='BodyLeft',
    fontName='Helvetica',
    fontSize=10,
    leading=15,
    textColor=TEXT_PRIMARY,
    alignment=TA_LEFT,
    spaceAfter=6,
))

styles.add(ParagraphStyle(
    name='Bullet2',
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=TEXT_PRIMARY,
    leftIndent=20,
    spaceAfter=3,
    bulletIndent=8,
))

styles.add(ParagraphStyle(
    name='CodeBlock',
    fontName='Courier',
    fontSize=9,
    leading=13,
    textColor=colors.HexColor('#c8d0d4'),
    backColor=colors.HexColor('#1e2a30'),
    leftIndent=12,
    rightIndent=12,
    spaceBefore=4,
    spaceAfter=4,
    borderPadding=(6, 6, 6, 6),
))

styles.add(ParagraphStyle(
    name='Note',
    fontName='Helvetica-Oblique',
    fontSize=9,
    leading=13,
    textColor=SEM_INFO,
    leftIndent=16,
    rightIndent=16,
    spaceBefore=6,
    spaceAfter=6,
    borderPadding=(6, 6, 6, 6),
    backColor=colors.HexColor('#eaf0f6'),
))

styles.add(ParagraphStyle(
    name='TableHeader',
    fontName='Helvetica-Bold',
    fontSize=9,
    leading=12,
    textColor=colors.white,
    alignment=TA_CENTER,
))

styles.add(ParagraphStyle(
    name='TableCell',
    fontName='Helvetica',
    fontSize=9,
    leading=12,
    textColor=TEXT_PRIMARY,
))

styles.add(ParagraphStyle(
    name='TOCEntry',
    fontName='Helvetica',
    fontSize=11,
    leading=18,
    textColor=TEXT_PRIMARY,
    leftIndent=20,
    spaceAfter=2,
))

styles.add(ParagraphStyle(
    name='FooterStyle',
    fontName='Helvetica',
    fontSize=8,
    leading=10,
    textColor=TEXT_MUTED,
    alignment=TA_CENTER,
))


def make_cover():
    """Generate cover page elements."""
    elements = []

    # Spacer to push content down
    elements.append(Spacer(1, 1.5 * inch))

    # Title block with background
    cover_data = [[
        Paragraph("AICL Editor", styles['CoverTitle']),
    ], [
        Paragraph("Web-Based Development Environment", styles['CoverSubtitle']),
    ], [
        Spacer(1, 20),
    ], [
        Paragraph("User Manual", styles['CoverSubtitle']),
    ], [
        Paragraph("Version 2.0.0", styles['CoverMeta']),
    ], [
        Spacer(1, 30),
    ], [
        Paragraph("Philippe-Antoine  |  June 2026", styles['CoverMeta']),
    ]]

    cover_table = Table(cover_data, colWidths=[5 * inch])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HEADER_FILL),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
    ]))
    elements.append(cover_table)

    elements.append(Spacer(1, 30))

    # Feature highlights
    highlights = [
        "AI Chat Panel with context-aware AICL assistant",
        "Agentic AI: create, compile, and verify files from chat",
        "Structured error display with Explain Error button",
        "One-click compilation to Python, Rust, JavaScript, Go",
        "Proof of Origin viewer and independent verification",
        "Interactive exercises and REPL",
    ]
    for h in highlights:
        elements.append(Paragraph(
            f'<font color="#466879">&#x2022;</font>  {h}',
            ParagraphStyle('highlight', parent=styles['Body2'], fontSize=10, leading=16, alignment=TA_CENTER)
        ))

    return elements


def make_toc():
    """Generate table of contents."""
    elements = []
    elements.append(Paragraph("Table of Contents", styles['H1']))
    elements.append(Spacer(1, 8))

    toc_items = [
        ("1", "Introduction"),
        ("2", "Interface Layout"),
        ("2.1", "Toolbar"),
        ("2.2", "Left Panel: Examples and Exercises"),
        ("2.3", "Center Panel: Code Editor"),
        ("2.4", "Right Panel: Output, Tree, Code, and Chat"),
        ("2.5", "Bottom Panel: Output, REPL, and Exercises"),
        ("2.6", "Status Bar"),
        ("3", "AI Chat Panel"),
        ("3.1", "Opening the Chat"),
        ("3.2", "Chat Capabilities"),
        ("3.3", "Agentic AI: The :::AICL_FILE Protocol"),
        ("3.4", "Action Buttons: Create, Compile, Verify"),
        ("3.5", "Offline Fallback"),
        ("4", "Error Display and Explanation"),
        ("4.1", "Error Box in Chat"),
        ("4.2", "Explain Error Button"),
        ("4.3", "Try Verify First Button"),
        ("4.4", "Automatic Error Propagation"),
        ("5", "Editor Features"),
        ("6", "Compilation and Verification"),
        ("6.1", "Compiling"),
        ("6.2", "Verifying"),
        ("6.3", "Auditing"),
        ("6.4", "Provenance Explanation"),
        ("7", "Examples"),
        ("8", "Exercises"),
        ("9", "Interactive REPL"),
        ("10", "Keyboard Shortcuts"),
        ("11", "Troubleshooting"),
    ]

    for num, title in toc_items:
        indent = 20 if '.' not in num else 40
        weight = 'Helvetica-Bold' if '.' not in num else 'Helvetica'
        sz = 11 if '.' not in num else 10
        elements.append(Paragraph(
            f'<font face="{weight}" size="{sz}">{num}  {title}</font>',
            ParagraphStyle('tocitem', parent=styles['TOCEntry'], leftIndent=indent,
                           fontName=weight, fontSize=sz, leading=sz + 6)
        ))

    return elements


def h1(text):
    return Paragraph(text, styles['H1'])

def h2(text):
    return Paragraph(text, styles['H2'])

def h3(text):
    return Paragraph(text, styles['H3'])

def p(text):
    return Paragraph(text, styles['Body2'])

def bullet(text):
    return Paragraph(f'<bullet>&bull;</bullet>{text}', styles['Bullet2'])

def code(text):
    return Paragraph(text.replace('\n', '<br/>'), styles['CodeBlock'])

def note(text):
    return Paragraph(f'<font color="#4b77a3">Note:</font> {text}', styles['Note'])

def spacer(h=8):
    return Spacer(1, h)

def make_table(headers, rows, col_widths=None):
    """Create a styled table."""
    header_row = [Paragraph(h, styles['TableHeader']) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(cell), styles['TableCell']) for cell in row])

    if col_widths is None:
        col_widths = [6.5 * inch / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_FILL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]
    # Alternate row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), TABLE_STRIPE))
    t.setStyle(TableStyle(style_cmds))
    return t


def build_manual():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        leftMargin=0.9*inch,
        rightMargin=0.9*inch,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch,
        title="AICL Editor Manual",
        author="Philippe-Antoine",
        subject="AICL Web Editor User Manual v2.0",
    )

    story = []

    # ── COVER ──
    story.extend(make_cover())
    story.append(PageBreak())

    # ── TOC ──
    story.extend(make_toc())
    story.append(PageBreak())

    # ── 1. Introduction ──
    story.append(h1("1. Introduction"))
    story.append(p(
        "The AICL Web Editor is a browser-based development environment for the Architecture "
        "Compilation Language, inspired by Python's IDLE but designed specifically for AICL's "
        "unique workflow. Like IDLE provides an integrated editor, shell, and debugger for Python, "
        "the AICL Editor provides a specification editor, compilation engine, proof viewer, and "
        "interactive REPL for AICL. Version 2.0 introduces a major new capability: an integrated "
        "AI Chat panel powered by an LLM with deep AICL domain knowledge, including agentic "
        "capabilities that allow the AI to create files, compile code, and verify specifications "
        "directly from the conversation."
    ))
    story.append(p(
        "The editor features a dark theme, AICL syntax highlighting, multi-file tabs, and one-click "
        "access to all AICL compilation, verification, and audit features. The AI assistant can "
        "understand your current code, write new AICL specifications from natural language descriptions, "
        "and automatically compile and verify them. When errors occur, they are displayed with structured "
        "details and an Explain Error button that provides root-cause analysis with specific fix suggestions."
    ))
    story.append(p(
        "The editor is organized into five main areas: the toolbar at the top for actions, the left panel "
        "for examples and exercises, the center panel for code editing, the right panel for output, tree, "
        "generated code, and AI chat, and the bottom panel for output and REPL. An interactive REPL at the "
        "bottom provides a command-line interface similar to the TUI, allowing you to type commands and AICL "
        "code directly."
    ))

    # ── 2. Interface Layout ──
    story.append(h1("2. Interface Layout"))

    story.append(h2("2.1 Toolbar"))
    story.append(p(
        "The toolbar provides one-click access to all AICL operations, organized from left to right. "
        "Each button triggers an immediate action on the current file. The AI Chat button, new in v2.0, "
        "opens the integrated AI assistant panel."
    ))
    story.append(spacer(4))
    story.append(make_table(
        ["Button", "Description"],
        [
            ["New", "Create a new untitled .aicl file in a new tab"],
            ["Open", "Open a .aicl file from your local filesystem"],
            ["Save", "Download the current file as .aicl"],
            ["Target selector", "Choose compilation target (Python, Rust, JavaScript, Go)"],
            ["Compile", "Compile the current AICL source to the selected target"],
            ["Verify", "Check specification completeness, coherence, and satisfaction"],
            ["Audit", "Run audit on compiled output (coverage, orphan detection)"],
            ["Explain", "Show provenance explanation for each compilation decision"],
            ["Tree", "Display the architecture tree of the current specification"],
            ["Optimize", "Suggest architectural optimizations"],
            ["AI Chat", "Open the AI assistant chat panel (v2.0)"],
            ["Clear", "Clear the output panel"],
            ["Find", "Search and replace within the editor"],
        ],
        col_widths=[1.4*inch, 5.1*inch]
    ))

    story.append(h2("2.2 Left Panel: Examples and Exercises"))
    story.append(p(
        "The left panel has two tabs: Examples and Exercises. The Examples tab lists built-in AICL "
        "programs ranging from simple (Blue Square, Level 1) to complex (Banking, Level 10). Click any "
        "example to load it into the editor. The Exercises tab lists five progressive exercises with "
        "descriptions and starter templates. Click an exercise to load its template with TODO markers."
    ))

    story.append(h2("2.3 Center Panel: Code Editor"))
    story.append(p(
        "The code editor supports AICL syntax highlighting with keywords in cyan, types in green, and "
        "comments in gray. It includes line numbers, auto-indentation (4 spaces after colons), Tab/Shift+Tab "
        "for indent/outdent, and Ctrl+F for find and replace. Multiple files can be open simultaneously in "
        "tabs at the top of the editor. Each tab shows the filename and a close button. The current file is "
        "highlighted. When the AI creates a new file through the agentic protocol, it automatically appears "
        "as a new tab in the editor."
    ))

    story.append(h2("2.4 Right Panel: Output, Tree, Code, and Chat"))
    story.append(p(
        "The right panel has four tabs, one of which is new in v2.0:"
    ))
    story.append(make_table(
        ["Tab", "Description"],
        [
            ["Output", "Compilation results, verification reports, audit summaries with timestamps"],
            ["Tree", "Architecture tree visualization of the current specification"],
            ["Code", "Generated source code and test code with copy buttons"],
            ["Chat", "AI assistant conversation panel (v2.0)"],
        ],
        col_widths=[1.0*inch, 5.5*inch]
    ))
    story.append(p(
        "The Chat tab provides a full conversational AI assistant that understands AICL, can read your "
        "current code, and can take agentic actions like creating files and compiling them. See Section 3 "
        "for the complete chat documentation."
    ))

    story.append(h2("2.5 Bottom Panel: Output, REPL, and Exercises"))
    story.append(p(
        "The bottom panel has three tabs: Output (duplicate of right panel output for convenience), REPL "
        "(an interactive command shell), and Exercises (exercise details and starter templates). The REPL "
        "supports colon-prefixed commands just like the TUI (:compile, :verify, :help, etc.) and can also "
        "accept AICL code directly."
    ))

    story.append(h2("2.6 Status Bar"))
    story.append(p(
        "The status bar at the very bottom shows: current filename, cursor position (line:column), "
        "selected target language, and AICL version number."
    ))

    # ── 3. AI Chat Panel ──
    story.append(h1("3. AI Chat Panel"))
    story.append(p(
        "The AI Chat panel is a full conversational AI assistant embedded directly in the editor. It uses "
        "a large language model with deep AICL domain knowledge to provide context-aware assistance. The "
        "chat is not a simple Q&A bot; it is an agentic system that can understand your code, write new "
        "specifications, create files, compile them, and verify them, all through the conversation interface."
    ))

    story.append(h2("3.1 Opening the Chat"))
    story.append(p(
        "There are two ways to open the AI Chat panel. First, click the purple AI Chat button in the toolbar "
        "(marked with a message square icon). Second, click the Chat tab in the right panel. Both actions "
        "will switch the right panel to the Chat tab and auto-focus the input field. The chat input field "
        "has a placeholder suggesting: \"Try 'Describe a todo app in AICL'...\""
    ))

    story.append(h2("3.2 Chat Capabilities"))
    story.append(p(
        "The AI assistant has comprehensive knowledge of the AICL language and the editor itself. When you "
        "send a message, the current code in your editor is automatically included as context, so the AI "
        "can analyze and respond to the spec you are actively working on. The conversation is multi-turn, "
        "meaning the AI remembers your entire conversation history for the session."
    ))
    story.append(p("The AI assistant can help with:"))
    story.append(bullet("Writing AICL specifications from natural language descriptions"))
    story.append(bullet("Explaining AICL concepts like the No-Orphan Property, Proof of Origin, and provenance types"))
    story.append(bullet("Debugging compilation errors with specific fix suggestions"))
    story.append(bullet("Suggesting improvements to specifications for better audit coverage"))
    story.append(bullet("Guiding you through the editor workflow (how to compile, verify, audit)"))
    story.append(bullet("Providing keyboard shortcuts and REPL commands"))
    story.append(bullet("Generating complete AICL programs that can be compiled and verified"))
    story.append(p(
        "When you ask the AI to write an AICL program, it uses the agentic :::AICL_FILE protocol (described "
        "below) to output code that you can immediately create, compile, and verify with one click."
    ))

    story.append(h2("3.3 Agentic AI: The :::AICL_FILE Protocol"))
    story.append(p(
        "When the AI generates AICL code, it does not output it in plain markdown code blocks. Instead, it "
        "uses a structured format called the :::AICL_FILE protocol. This protocol allows the editor to parse "
        "the AI's output, detect AICL files, and present them as interactive code cards with action buttons."
    ))
    story.append(p("The format is:"))
    story.append(code(":::AICL_FILE filename.aicl\n(Goal Build ...)\n(Layer ...)\n...\n:::END_FILE"))
    story.append(p(
        "The editor parses these blocks and renders each one as a card in the chat showing the filename, a "
        "preview of the code, and three action buttons. The AI is instructed to always use this format when "
        "writing AICL code, ensuring that every code snippet is immediately actionable. Multiple "
        ":::AICL_FILE blocks can appear in a single AI response, and explanatory text can appear before "
        "or after the blocks."
    ))

    story.append(h2("3.4 Action Buttons: Create, Compile, Verify"))
    story.append(p(
        "Each :::AICL_FILE code card renders with three action buttons that let you take immediate action "
        "on the AI-generated code without leaving the chat:"
    ))
    story.append(spacer(4))
    story.append(make_table(
        ["Button", "Color", "Action"],
        [
            ["Create File", "Teal", "Creates a new editor tab with the AI-generated code and switches to it"],
            ["Create + Compile", "Red", "Creates the file AND immediately compiles it; reports results in chat"],
            ["Verify", "Blue", "Creates the file AND immediately runs verification; reports results in chat"],
        ],
        col_widths=[1.4*inch, 0.8*inch, 4.3*inch]
    ))
    story.append(p(
        "When you click Create + Compile, the editor creates the file, selects the current target language "
        "(Python, Rust, JavaScript, or Go), and compiles it. The result is reported back into the chat: on "
        "success, you see a message with the number of compilation stages completed, audit coverage percentage, "
        "and proof validity. On failure, a structured error box appears with details (see Section 4)."
    ))
    story.append(p(
        "When you click Verify, the editor creates the file and runs the three-level verification check "
        "(completeness, coherence, satisfaction). On success, you see a confirmation that all checks passed. "
        "On failure, an error box appears with the specific check that failed and its details."
    ))

    story.append(h2("3.5 Offline Fallback"))
    story.append(p(
        "When the AI service is unavailable (network error, server down, or API failure), the chat API "
        "returns categorized offline responses based on keyword matching of your last message. The responses "
        "cover common topics like compilation workflow, the No-Orphan Property, Proof of Origin, exercises, "
        "and keyboard shortcuts. The response includes a 'connected: false' indicator so you know the AI is "
        "operating in offline mode. The editor remains fully functional even without the AI service."
    ))

    # ── 4. Error Display and Explanation ──
    story.append(h1("4. Error Display and Explanation"))
    story.append(p(
        "Version 2.0 introduces a comprehensive error display system in the chat panel. When any operation "
        "fails (compile, verify, audit, or chat), the error is automatically displayed as a structured error "
        "box in the chat conversation. This is a significant improvement over the previous behavior where "
        "errors only appeared briefly in the output panel."
    ))

    story.append(h2("4.1 Error Box in Chat"))
    story.append(p(
        "The error box is rendered as a dark red card in the chat with the following elements: a red X-circle "
        "icon, the error message in bold, detailed error lines prefixed with arrow symbols, and action buttons "
        "at the bottom. Each error has an operation type (compile, verify, audit, or chat), a human-readable "
        "message, and an optional array of detailed error lines from the underlying system."
    ))
    story.append(p("The ChatError interface that structures these errors:"))
    story.append(code("interface ChatError {\n  operation: string;  // 'compile', 'verify', 'audit', 'chat'\n  message: string;    // Human-readable error summary\n  details?: string[]; // Array of detailed error lines\n}"))
    story.append(p(
        "The compile API enhances raw Python error messages with contextual fix suggestions before they "
        "reach the chat. For example, a 'missing Goal' error will include a 'Fix: Add a Goal section at "
        "the top' suggestion. This enhancement ensures that even before clicking Explain Error, you already "
        "have actionable guidance."
    ))

    story.append(h2("4.2 Explain Error Button"))
    story.append(p(
        "At the bottom of every error box is a red Explain Error button with a bug icon. Clicking it sends "
        "the full error context (operation type, message, and details) to the AI assistant, which then "
        "provides a detailed root-cause analysis. The AI follows a strict WHAT/WHY/FIX pattern:"
    ))
    story.append(bullet("<b>WHAT</b> went wrong, explained in plain language"))
    story.append(bullet("<b>WHY</b> it happened, referencing AICL concepts and the relevant specification elements"))
    story.append(bullet("<b>FIX</b> with specific before/after code examples that you can apply immediately"))
    story.append(p(
        "The AI explanation references the relevant AICL keywords, language levels, and formal properties. "
        "It never just says 'fix the error' but always provides concrete, actionable steps. This turns "
        "compilation failures into learning opportunities."
    ))

    story.append(h2("4.3 Try Verify First Button"))
    story.append(p(
        "When the error comes from a failed compilation, an additional teal button appears: Try Verify First. "
        "This button creates the file and runs the verification check instead of compilation. The reasoning "
        "is that verification catches structural issues (missing Goal, incomplete Risk/Recovery pairs, "
        "dangling references) before compilation attempts code generation, making it easier to diagnose "
        "the root cause. Clicking this button is equivalent to the Verify action button on the code card."
    ))

    story.append(h2("4.4 Automatic Error Propagation"))
    story.append(p(
        "Errors are automatically pushed to the chat panel whenever the chat panel is open and an operation "
        "fails. This applies to all toolbar operations as well as agentic chat actions. Specifically, errors "
        "appear in chat when: compilation fails while the chat panel is open, verification shows FAIL or "
        "WARN while the chat is open, audit finds orphans while the chat is open, a network or server error "
        "occurs during any operation, or the chat API itself fails to connect."
    ))
    story.append(p(
        "This automatic propagation ensures that you never miss an error. Even if you triggered the compile "
        "from the toolbar rather than the chat, the error will still appear in the chat conversation where "
        "you can click Explain Error for a detailed analysis."
    ))

    # ── 5. Editor Features ──
    story.append(h1("5. Editor Features"))
    story.append(p(
        "The AICL Editor provides a complete set of editing features comparable to Python's IDLE, adapted "
        "for the AICL language. These features support both manual editing and AI-assisted development."
    ))
    story.append(spacer(4))
    story.append(make_table(
        ["Feature", "Description", "Shortcut"],
        [
            ["Syntax Highlighting", "Keywords (cyan), Types (green), Comments (gray)", "Always on"],
            ["Auto-indentation", "4 spaces after colons, extra indent for sub-sections", "Automatic"],
            ["Line Numbers", "Displayed on the left side of the editor", "Always visible"],
            ["Indent/Outdent", "Indent or outdent selected lines", "Tab / Shift+Tab"],
            ["Find and Replace", "Search within the current file", "Ctrl+F"],
            ["Multiple File Tabs", "Open and edit multiple files simultaneously", "Click tabs"],
            ["New File", "Create a new untitled .aicl file", "New button"],
            ["Open File", "Load a .aicl file from your computer", "Open button"],
            ["Save/Download", "Download the current file as .aicl", "Save button"],
            ["Auto-complete", "Suggests AICL keywords as you type", "Tab"],
            ["Copy", "Copy compiled source or tests to clipboard", "Copy button"],
            ["Generated Code", "View and copy generated source and test files", "Code tab"],
        ],
        col_widths=[1.5*inch, 3.5*inch, 1.5*inch]
    ))

    # ── 6. Compilation and Verification ──
    story.append(h1("6. Compilation and Verification"))

    story.append(h2("6.1 Compiling"))
    story.append(p(
        "Click the Compile button or use the REPL command :compile to compile the current AICL source. "
        "Select the target language from the dropdown (Python, Rust, JavaScript, Go) before compiling. "
        "The output panel shows the compilation result including audit coverage, TODO count, and proof "
        "validity. The Code tab displays the generated source and test files."
    ))
    story.append(p(
        "If compilation fails and the chat panel is open, a structured error box appears in the chat "
        "with details about the failure. The error box includes an Explain Error button and a Try Verify "
        "First button. See Section 4 for details."
    ))

    story.append(h2("6.2 Verifying"))
    story.append(p(
        "Click Verify to check specification quality before compiling. The verifier runs three levels of "
        "checks: Completeness (all required elements present), Coherence (no contradictions or dangling "
        "references), and Satisfaction (implementable and testable). Each check shows PASS, WARN, or FAIL "
        "status. Running Verify before Compile is recommended to catch structural issues early."
    ))

    story.append(h2("6.3 Auditing"))
    story.append(p(
        "Click Audit after compiling to see the audit report. The report shows total artifacts, artifacts "
        "with provenance, orphan count, and coverage percentage. The target is always 100% coverage with "
        "zero orphans (the No-Orphan Property). If orphans are found and the chat is open, an error box "
        "appears explaining the No-Orphan Property and which artifacts are orphaned."
    ))

    story.append(h2("6.4 Provenance Explanation"))
    story.append(p(
        "Click Explain to see why each line of generated code was produced. The explanation shows the "
        "provenance decision type, the source specification element, and the confidence level. All "
        "decisions are deterministic and fully auditable. AICL tracks 23 provenance types covering "
        "every compilation zone, from PATTERN_MATCH and SUB_LANGUAGE to AI_GENERATION and SPEC_EVOLVED."
    ))

    # ── 7. Examples ──
    story.append(h1("7. Examples"))
    story.append(p(
        "Five built-in examples demonstrate progressively more advanced AICL features, from simple "
        "graphics to a complete banking system with AI self-writing:"
    ))
    story.append(spacer(4))
    story.append(make_table(
        ["Example", "Levels", "Description", "Artifacts"],
        [
            ["Blue Square", "1", "Simple graphics application", "35 artifacts, 100% audit"],
            ["Pong Game", "1-6", "Game with entities, behaviors, conditions, events, parallelism", "52 artifacts, 100% audit"],
            ["Chat App", "1-9", "Full chat with security, optimization, learning", "58 artifacts, 100% audit"],
            ["Chess Game", "1-9", "Complex state management with network", "59 artifacts, 100% audit"],
            ["Banking System", "1-10", "Complete banking with native code", "100% audit"],
        ],
        col_widths=[1.1*inch, 0.7*inch, 3.0*inch, 1.7*inch]
    ))

    # ── 8. Exercises ──
    story.append(h1("8. Exercises"))
    story.append(p(
        "Five progressive exercises teach AICL from basics to advanced. Each loads a starter template with "
        "TODO markers that you complete. You can also ask the AI assistant for hints on any exercise by "
        "describing what you are stuck on in the chat panel."
    ))
    story.append(spacer(4))
    story.append(make_table(
        ["#", "Title", "Description", "What You Learn"],
        [
            ["1", "Hello World", "Create a minimal AICL program", "Goal, Layer, Validation"],
            ["2", "Risk and Recovery", "Add error handling to a file reader", "Risk/Recovery pairs"],
            ["3", "Entities and Behaviors", "Define data structures with actions", "Entity, Behavior, Action"],
            ["4", "Conditions and Events", "Add rules and event handlers", "When/Then, On/Action"],
            ["5", "Full Application", "Build a complete chat application", "All 9 levels combined"],
        ],
        col_widths=[0.4*inch, 1.3*inch, 2.7*inch, 2.1*inch]
    ))
    story.append(p(
        "To start an exercise, click the Exercises tab in the left panel, then click the exercise title. "
        "The starter template loads in the editor with TODO markers showing where to add code. Complete "
        "the TODOs and click Compile to test your solution. Click Verify to check specification quality. "
        "If you get stuck, open the AI Chat and ask for help with the specific exercise."
    ))

    # ── 9. Interactive REPL ──
    story.append(h1("9. Interactive REPL"))
    story.append(p(
        "The REPL (Read-Eval-Print Loop) at the bottom of the editor provides an interactive command "
        "interface. Type colon-prefixed commands for actions, or type AICL code directly to add it to "
        "the current file. The REPL supports the same commands as the CLI TUI:"
    ))
    story.append(spacer(4))
    story.append(make_table(
        ["Command", "Action"],
        [
            [":help", "Show all REPL commands"],
            [":compile", "Compile current file"],
            [":verify", "Verify specification"],
            [":audit", "Audit compilation"],
            [":explain", "Explain provenance"],
            [":tree", "Architecture tree"],
            [":optimize", "Optimize architecture"],
            [":clear", "Clear output"],
            [":load", "Load an example"],
            [":exercises", "List exercises"],
        ],
        col_widths=[1.3*inch, 5.2*inch]
    ))

    # ── 10. Keyboard Shortcuts ──
    story.append(h1("10. Keyboard Shortcuts"))
    story.append(spacer(4))
    story.append(make_table(
        ["Shortcut", "Action"],
        [
            ["Ctrl+F", "Find and Replace"],
            ["Tab", "Indent / Auto-complete"],
            ["Shift+Tab", "Outdent"],
            ["Ctrl+S", "Save/Download file"],
            ["Enter (in chat)", "Send message to AI assistant"],
        ],
        col_widths=[1.5*inch, 5.0*inch]
    ))

    # ── 11. Troubleshooting ──
    story.append(h1("11. Troubleshooting"))
    story.append(spacer(4))
    story.append(make_table(
        ["Issue", "Solution"],
        [
            ["Compilation errors", "Use Verify before Compile to catch specification issues early. If errors appear, click Explain Error in the chat for detailed analysis."],
            ["Empty output", "Make sure you clicked Compile first. Audit and Explain require a compilation result."],
            ["File not loading", "Ensure the file has a .aicl extension and valid UTF-8 encoding."],
            ["REPL not responding", "Click inside the REPL input field to focus it."],
            ["Copy button not working", "Your browser may block clipboard access. Use Ctrl+C manually."],
            ["AI Chat not responding", "Check that the AI service is available. The chat provides offline fallback responses when disconnected."],
            ["Error box in chat", "Click Explain Error for root-cause analysis, or Try Verify First for structural checks before compilation."],
            ["Agentic actions failing", "Ensure the code in the :::AICL_FILE block is valid AICL. Click Verify first to check structural completeness."],
        ],
        col_widths=[1.8*inch, 4.7*inch]
    ))

    # ── Build ──
    doc.build(story)
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == '__main__':
    build_manual()
