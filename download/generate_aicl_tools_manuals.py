#!/usr/bin/env python3
"""Generate AICL CLI TUI + Editor User Manuals as PDF"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.colors import HexColor
import os

# ━━ Font Registration ━━
pdfmetrics.registerFont(TTFont('NotoSerifSC', '/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('SarasaMonoSC', '/usr/share/fonts/truetype/chinese/SarasaMonoSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif', '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSerif', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSerifBold', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'))

registerFontFamily('DejaVuSerif', normal='DejaVuSerif', bold='DejaVuSerifBold')
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSansBold')

# ━━ Colors ━━
ACCENT = HexColor('#cd2d48')
TEXT_PRIMARY = HexColor('#141516')
TEXT_MUTED = HexColor('#838a8d')
HEADER_FILL = HexColor('#35444b')
TABLE_STRIPE = HexColor('#f3f4f4')
BORDER = HexColor('#b2bcc1')
SEM_INFO = HexColor('#547ca4')

# ━━ Page Setup ━━
PAGE_W, PAGE_H = A4
LEFT_M = 22*mm; RIGHT_M = 22*mm; TOP_M = 20*mm; BOTTOM_M = 20*mm
CONTENT_W = PAGE_W - LEFT_M - RIGHT_M

# ━━ Styles ━━
sH1 = ParagraphStyle('H1', fontName='DejaVuSerif', fontSize=20, leading=26, textColor=ACCENT, spaceAfter=6, spaceBefore=16)
sH2 = ParagraphStyle('H2', fontName='DejaVuSerif', fontSize=15, leading=20, textColor=HEADER_FILL, spaceAfter=5, spaceBefore=12)
sH3 = ParagraphStyle('H3', fontName='DejaVuSerif', fontSize=12, leading=17, textColor=SEM_INFO, spaceAfter=4, spaceBefore=8)
sBody = ParagraphStyle('Body', fontName='DejaVuSerif', fontSize=10, leading=16, textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=5)
sCode = ParagraphStyle('Code', fontName='DejaVuSans', fontSize=8, leading=12, textColor=HexColor('#1a1a2e'), backColor=HexColor('#f4f4f8'), leftIndent=10, rightIndent=10, spaceBefore=3, spaceAfter=3, borderPadding=(5,5,5,5))
sBullet = ParagraphStyle('Bullet', fontName='DejaVuSerif', fontSize=10, leading=16, textColor=TEXT_PRIMARY, leftIndent=22, bulletIndent=10, spaceAfter=2)
sTH = ParagraphStyle('TH', fontName='DejaVuSerif', fontSize=9, leading=13, textColor=colors.white, alignment=TA_CENTER)
sTC = ParagraphStyle('TC', fontName='DejaVuSerif', fontSize=8.5, leading=13, textColor=TEXT_PRIMARY, alignment=TA_LEFT)

def h1(t): return Paragraph(t, sH1)
def h2(t): return Paragraph(t, sH2)
def h3(t): return Paragraph(t, sH3)
def p(t): return Paragraph(t, sBody)
def code(t): return Paragraph(t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('\n','<br/>'), sCode)
def bullet(t): return Paragraph(t, sBullet)
def hr(): return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6, spaceBefore=6)
def sp(h=5): return Spacer(1, h)

def make_table(headers, rows, col_widths=None):
    cw = col_widths or [CONTENT_W / len(headers)] * len(headers)
    header_row = [Paragraph(h, sTH) for h in headers]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(str(c), sTC) for c in row])
    t = Table(data, colWidths=cw, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0,i), (-1,i), TABLE_STRIPE))
    t.setStyle(TableStyle(style_cmds))
    return t

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVuSerif', 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawCentredString(PAGE_W/2, 12*mm, f"AICL User Manual  |  Page {doc.page}")
    canvas.restoreState()

def add_page_number2(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVuSerif', 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawCentredString(PAGE_W/2, 12*mm, f"AICL Editor Manual  |  Page {doc.page}")
    canvas.restoreState()

# ══════════════════════════════════════════════════════════════
# MANUAL 1: CLI TUI
# ══════════════════════════════════════════════════════════════
output1 = '/home/z/my-project/download/AICL_CLI_TUI_Manual.pdf'
doc1 = SimpleDocTemplate(output1, pagesize=A4, leftMargin=LEFT_M, rightMargin=RIGHT_M,
    topMargin=TOP_M, bottomMargin=BOTTOM_M, title="AICL CLI TUI Manual",
    author="Philippe-Antoine", subject="AICL Terminal User Interface Manual")

s = []

# Cover
s.append(Spacer(1, 50*mm))
s.append(Paragraph("AICL CLI TUI", ParagraphStyle('CT', fontName='DejaVuSerif', fontSize=52, leading=60, textColor=ACCENT, alignment=TA_CENTER)))
s.append(Spacer(1, 6*mm))
s.append(Paragraph("Interactive Terminal Interface", ParagraphStyle('CS', fontName='DejaVuSerif', fontSize=16, leading=22, textColor=HEADER_FILL, alignment=TA_CENTER)))
s.append(Spacer(1, 12*mm))
s.append(HRFlowable(width="40%", thickness=2, color=ACCENT, spaceAfter=12))
s.append(Paragraph("User Manual", ParagraphStyle('CD', fontName='DejaVuSerif', fontSize=14, leading=20, textColor=TEXT_PRIMARY, alignment=TA_CENTER)))
s.append(Spacer(1, 6*mm))
s.append(Paragraph("Version 1.0.0", ParagraphStyle('CV', fontName='DejaVuSerif', fontSize=11, leading=16, textColor=TEXT_MUTED, alignment=TA_CENTER)))
s.append(Spacer(1, 30*mm))
s.append(Paragraph("Philippe-Antoine  |  June 2026", ParagraphStyle('CA', fontName='DejaVuSerif', fontSize=10, leading=14, textColor=TEXT_MUTED, alignment=TA_CENTER)))
s.append(PageBreak())

s.append(h1("1. Introduction"))
s.append(p("The AICL TUI (Terminal User Interface) is an interactive command-line interface inspired by Claude Code. It provides a rich, intuitive terminal experience for writing, compiling, verifying, and auditing AICL programs without leaving the terminal. Unlike the basic CLI which operates on individual commands, the TUI provides a persistent, interactive environment with a file browser, code viewer, output panel, and command input, all within a single terminal window."))
s.append(p("The TUI is built with Textual, a Python framework for building sophisticated terminal applications. It features a dark theme optimized for long coding sessions, syntax highlighting for AICL source code, and a command-driven interface that feels natural to developers familiar with modern terminal tools like Vim, Emacs, or Claude Code."))

s.append(h1("2. Installation and Launch"))
s.append(code("pip install aicl\npip install textual rich"))
s.append(sp(3))
s.append(p("Launch the TUI:"))
s.append(code("aicl tui"))
s.append(sp(3))
s.append(p("This opens the interactive terminal interface with a sidebar file browser, main editor area, output panel, and command input bar. The TUI requires a terminal that supports 256 colors or true color. Most modern terminals (iTerm2, Windows Terminal, Alacritty, Kitty, GNOME Terminal) are compatible."))

s.append(h1("3. Interface Layout"))
s.append(p("The TUI interface consists of four main areas, each serving a distinct purpose in the development workflow:"))
s.append(bullet("<b>Header</b> (top) - Shows the application title and current time."))
s.append(bullet("<b>File Explorer</b> (left sidebar) - Directory tree for browsing and opening .aicl files. Click any .aicl file to load it into the editor. Toggle visibility with Ctrl+E."))
s.append(bullet("<b>Editor Area</b> (center) - Displays the current AICL source code with syntax highlighting. Keywords appear in cyan, types in green, and comments in gray."))
s.append(bullet("<b>Output Panel</b> (bottom) - Shows compilation results, verification reports, audit summaries, and command responses."))
s.append(bullet("<b>Command Input</b> (bottom bar) - Type commands starting with : or AICL code to interact. This is your primary interface to the TUI."))

s.append(h1("4. Commands"))
s.append(p("All TUI commands start with a colon (:). Type :help at any time to see the full list. Here is the complete command reference:"))

s.append(make_table(
    ["Command", "Description", "Usage"],
    [
        [":help", "Show all available commands", ":help"],
        [":open", "Open an AICL file", ":open path/to/file.aicl"],
        [":save", "Save current file", ":save"],
        [":new", "Create new untitled file", ":new"],
        [":compile", "Compile current file", ":compile [python|rust|js|go]"],
        [":verify", "Verify specification quality", ":verify"],
        [":audit", "Audit compilation", ":audit"],
        [":proof", "View Proof of Origin", ":proof"],
        [":explain", "Explain compilation provenance", ":explain"],
        [":tree", "Show architecture tree", ":tree"],
        [":optimize", "Optimize architecture", ":optimize"],
        [":run", "Run self-healing runtime", ":run"],
        [":sign", "Cryptographically sign proof", ":sign"],
        [":verify-proof", "Independent proof verification", ":verify-proof"],
        [":ownership", "Show ownership model", ":ownership"],
        [":targets", "List compilation targets", ":targets"],
        [":examples", "Browse built-in examples", ":examples"],
        [":exercise", "Start an exercise", ":exercise [1-5]"],
        [":clear", "Clear output panel", ":clear"],
        [":version", "Show AICL version", ":version"],
    ],
    col_widths=[65, 155, CONTENT_W-220]
))
s.append(sp(6))

s.append(h1("5. Keyboard Shortcuts"))
s.append(make_table(
    ["Shortcut", "Action"],
    [
        ["Ctrl+O", "Open file (prefills :open)"],
        ["Ctrl+S", "Save current file"],
        ["Ctrl+K", "Command palette (prefills :)"],
        ["Ctrl+E", "Toggle sidebar visibility"],
        ["Ctrl+Q", "Quit TUI"],
        ["Tab", "Auto-complete keywords"],
    ],
    col_widths=[80, CONTENT_W-80]
))
s.append(sp(6))

s.append(h1("6. Workflow Examples"))
s.append(h2("6.1 Compile and Verify"))
s.append(code(":open examples/02_pong.aicl\n:compile\n:verify\n:proof"))
s.append(sp(3))
s.append(p("This opens the Pong example, compiles it to Python, verifies the specification quality, and displays the Proof of Origin. The output panel shows each step's results incrementally."))

s.append(h2("6.2 Multi-Language Compilation"))
s.append(code(":compile rust      # Compile to Rust\n:compile js       # Compile to JavaScript\n:compile go       # Compile to Go"))
s.append(sp(3))

s.append(h2("6.3 Exercises"))
s.append(code(":exercise          # List all exercises\n:exercise 1        # Load Exercise 1: Hello World\n:compile           # Test your solution\n:verify            # Check specification quality"))
s.append(sp(3))

s.append(h1("7. Exercises"))
s.append(p("The TUI includes 5 progressive exercises designed to teach AICL from basic to advanced:"))

s.append(make_table(
    ["#", "Title", "Skills Practiced"],
    [
        ["1", "Hello World", "Goal, Layer, Validation (Level 1)"],
        ["2", "Risk and Recovery", "Risk/Recovery pairs, error handling"],
        ["3", "Entities and Behaviors", "Entity definitions, Behavior actions (Levels 2-3)"],
        ["4", "Conditions and Events", "When/Then rules, On/Action handlers (Levels 4-5)"],
        ["5", "Full Application", "Complete chat app using all 9 levels"],
    ],
    col_widths=[20, 100, CONTENT_W-120]
))
s.append(sp(3))
s.append(p("Each exercise loads a starter template with TODO markers. Complete the TODOs and use :compile to test your solution. Use :verify to check specification quality before compiling."))

s.append(h1("8. Troubleshooting"))
s.append(bullet("<b>Display issues</b> - Ensure your terminal supports 256 colors. Try setting TERM=xterm-256color."))
s.append(bullet("<b>Import errors</b> - Install textual and rich: pip install textual rich"))
s.append(bullet("<b>File not found</b> - Use absolute paths or run the TUI from the project directory."))
s.append(bullet("<b>Compilation errors</b> - Use :verify to check specification quality before compiling."))

doc1.build(s, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"Generated: {output1} ({os.path.getsize(output1)/1024:.0f} KB)")

# ══════════════════════════════════════════════════════════════
# MANUAL 2: WEB EDITOR
# ══════════════════════════════════════════════════════════════
output2 = '/home/z/my-project/download/AICL_Editor_Manual.pdf'
doc2 = SimpleDocTemplate(output2, pagesize=A4, leftMargin=LEFT_M, rightMargin=RIGHT_M,
    topMargin=TOP_M, bottomMargin=BOTTOM_M, title="AICL Web Editor Manual",
    author="Philippe-Antoine", subject="AICL Web Editor Manual")

s = []

# Cover
s.append(Spacer(1, 50*mm))
s.append(Paragraph("AICL Editor", ParagraphStyle('CT2', fontName='DejaVuSerif', fontSize=52, leading=60, textColor=ACCENT, alignment=TA_CENTER)))
s.append(Spacer(1, 6*mm))
s.append(Paragraph("Web-Based Development Environment", ParagraphStyle('CS2', fontName='DejaVuSerif', fontSize=16, leading=22, textColor=HEADER_FILL, alignment=TA_CENTER)))
s.append(Spacer(1, 12*mm))
s.append(HRFlowable(width="40%", thickness=2, color=ACCENT, spaceAfter=12))
s.append(Paragraph("User Manual", ParagraphStyle('CD2', fontName='DejaVuSerif', fontSize=14, leading=20, textColor=TEXT_PRIMARY, alignment=TA_CENTER)))
s.append(Spacer(1, 6*mm))
s.append(Paragraph("Version 1.0.0", ParagraphStyle('CV2', fontName='DejaVuSerif', fontSize=11, leading=16, textColor=TEXT_MUTED, alignment=TA_CENTER)))
s.append(Spacer(1, 30*mm))
s.append(Paragraph("Philippe-Antoine  |  June 2026", ParagraphStyle('CA2', fontName='DejaVuSerif', fontSize=10, leading=14, textColor=TEXT_MUTED, alignment=TA_CENTER)))
s.append(PageBreak())

s.append(h1("1. Introduction"))
s.append(p("The AICL Web Editor is a browser-based development environment for the Architecture Compilation Language, inspired by Python's IDLE but designed specifically for AICL's unique workflow. Like IDLE provides an integrated editor, shell, and debugger for Python, the AICL Editor provides a specification editor, compilation engine, proof viewer, and interactive REPL for AICL. The editor features a dark theme, AICL syntax highlighting, multi-file tabs, and one-click access to all AICL compilation, verification, and audit features."))
s.append(p("The editor is organized into four main areas: the toolbar at the top for actions, the left panel for examples and exercises, the center panel for code editing, and the right panel for output and generated code. An interactive REPL at the bottom provides a command-line interface similar to the TUI, allowing you to type commands and AICL code directly."))

s.append(h1("2. Interface Layout"))
s.append(h2("2.1 Toolbar"))
s.append(p("The toolbar provides one-click access to all AICL operations, organized from left to right:"))
s.append(bullet("<b>New</b> - Create a new untitled .aicl file in a new tab"))
s.append(bullet("<b>Open</b> - Open a .aicl file from your local filesystem"))
s.append(bullet("<b>Save</b> - Download the current file as .aicl"))
s.append(bullet("<b>Target selector</b> - Choose compilation target (Python, Rust, JavaScript, Go)"))
s.append(bullet("<b>Compile</b> - Compile the current AICL source to the selected target"))
s.append(bullet("<b>Verify</b> - Check specification completeness, coherence, and satisfaction"))
s.append(bullet("<b>Audit</b> - Run audit on compiled output (coverage, orphan detection)"))
s.append(bullet("<b>Explain</b> - Show provenance explanation for each compilation decision"))
s.append(bullet("<b>Tree</b> - Display the architecture tree of the current specification"))
s.append(bullet("<b>Optimize</b> - Suggest architectural optimizations"))
s.append(bullet("<b>Clear</b> - Clear the output panel"))
s.append(bullet("<b>Find</b> - Search and replace within the editor"))

s.append(h2("2.2 Left Panel: Examples and Exercises"))
s.append(p("The left panel has two tabs: Examples and Exercises. The Examples tab lists four built-in AICL programs ranging from simple (Blue Square, Level 1) to complex (Chess, Level 9). Click any example to load it into the editor. The Exercises tab lists five progressive exercises with descriptions and starter templates. Click an exercise to load its template with TODO markers."))

s.append(h2("2.3 Center Panel: Code Editor"))
s.append(p("The code editor supports AICL syntax highlighting with keywords in cyan, types in green, and comments in gray. It includes line numbers, auto-indentation (4 spaces after colons), Tab/Shift+Tab for indent/outdent, and Ctrl+F for find and replace. Multiple files can be open simultaneously in tabs at the top of the editor. Each tab shows the filename and a close button. The current file is highlighted."))

s.append(h2("2.4 Right Panel: Output and Generated Code"))
s.append(p("The right panel has three tabs: Output, Tree, and Code. The Output tab shows compilation results, verification reports, and audit summaries in a log format with timestamps. The Tree tab displays the architecture tree visualization. The Code tab shows the generated source code and test code with copy buttons for easy extraction."))

s.append(h2("2.5 Bottom Panel: REPL and Exercises"))
s.append(p("The bottom panel has three tabs: Output (duplicate of right panel output for convenience), REPL (an interactive command shell), and Exercises (exercise details and starter templates). The REPL supports colon-prefixed commands just like the TUI (:compile, :verify, :help, etc.) and can also accept AICL code directly."))

s.append(h2("2.6 Status Bar"))
s.append(p("The status bar at the very bottom shows: current filename, cursor position (line:column), selected target language, and AICL version number."))

s.append(h1("3. Editor Features"))
s.append(p("The AICL Editor provides a complete set of editing features comparable to Python's IDLE, adapted for the AICL language:"))

s.append(make_table(
    ["Feature", "Description", "Shortcut"],
    [
        ["Syntax Highlighting", "Keywords (cyan), Types (green), Comments (gray)", "Automatic"],
        ["Auto-indentation", "4 spaces after colons, extra indent for sub-sections", "Automatic"],
        ["Line Numbers", "Displayed on the left side of the editor", "Always visible"],
        ["Tab/Shift+Tab", "Indent or outdent selected lines", "Tab / Shift+Tab"],
        ["Find and Replace", "Search within the current file", "Ctrl+F"],
        ["Multiple File Tabs", "Open and edit multiple files simultaneously", "Click tabs"],
        ["New File", "Create a new untitled .aicl file", "New button"],
        ["Open File", "Load a .aicl file from your computer", "Open button"],
        ["Save/Download", "Download the current file as .aicl", "Save button"],
        ["Auto-complete", "Suggests AICL keywords as you type", "Tab"],
        ["Copy Generated Code", "Copy compiled source or tests to clipboard", "Copy button"],
    ],
    col_widths=[80, 200, CONTENT_W-280]
))
s.append(sp(6))

s.append(h1("4. Compilation and Verification"))
s.append(h2("4.1 Compiling"))
s.append(p("Click the <b>Compile</b> button or use the REPL command :compile to compile the current AICL source. Select the target language from the dropdown (Python, Rust, JavaScript, Go) before compiling. The output panel shows the compilation result including audit coverage, TODO count, and proof validity. The Code tab displays the generated source and test files."))
s.append(h2("4.2 Verifying"))
s.append(p("Click <b>Verify</b> to check specification quality before compiling. The verifier runs three levels of checks: Completeness (all required elements present), Coherence (no contradictions), and Satisfaction (implementable and testable). Each check shows PASS, WARN, or FAIL status."))
s.append(h2("4.3 Auditing"))
s.append(p("Click <b>Audit</b> after compiling to see the audit report. The report shows total artifacts, artifacts with provenance, orphan count, and coverage percentage. The target is always 100% coverage with zero orphans."))
s.append(h2("4.4 Provenance Explanation"))
s.append(p("Click <b>Explain</b> to see why each line of generated code was produced. The explanation shows the provenance decision type, the source specification element, and the confidence level. All decisions are deterministic and fully auditable."))

s.append(h1("5. Examples"))
s.append(p("Four built-in examples demonstrate progressively more advanced AICL features:"))

s.append(make_table(
    ["Example", "Levels", "Description", "Artifacts"],
    [
        ["Blue Square", "1", "Simple graphics application", "35 artifacts, 100% audit"],
        ["Pong Game", "1-6", "Game with entities, behaviors, conditions, events, parallelism", "52 artifacts, 100% audit"],
        ["Chat App", "1-9", "Full chat with security, optimization, learning", "58 artifacts, 100% audit"],
        ["Chess Game", "1-9", "Complex state management with network", "59 artifacts, 100% audit"],
    ],
    col_widths=[60, 35, 230, CONTENT_W-325]
))
s.append(sp(6))

s.append(h1("6. Exercises"))
s.append(p("Five progressive exercises teach AICL from basics to advanced. Each loads a starter template with TODO markers that you complete:"))

s.append(make_table(
    ["#", "Title", "Description", "What You Learn"],
    [
        ["1", "Hello World", "Create a minimal AICL program", "Goal, Layer, Validation"],
        ["2", "Risk and Recovery", "Add error handling to a file reader", "Risk/Recovery pairs"],
        ["3", "Entities and Behaviors", "Define data structures with actions", "Entity, Behavior, Action"],
        ["4", "Conditions and Events", "Add rules and event handlers", "When/Then, On/Action"],
        ["5", "Full Application", "Build a complete chat application", "All 9 levels combined"],
    ],
    col_widths=[15, 75, 175, CONTENT_W-265]
))
s.append(sp(3))
s.append(p("To start an exercise, click the Exercises tab in the left panel, then click the exercise title. The starter template loads in the editor with TODO markers showing where to add code. Complete the TODOs and click Compile to test your solution. Click Verify to check specification quality."))

s.append(h1("7. Interactive REPL"))
s.append(p("The REPL (Read-Eval-Print Loop) at the bottom of the editor provides an interactive command interface. Type colon-prefixed commands for actions, or type AICL code directly to add it to the current file. The REPL supports the same commands as the CLI TUI:"))
s.append(code(":help       Show all REPL commands\n:compile    Compile current file\n:verify     Verify specification\n:audit      Audit compilation\n:explain    Explain provenance\n:tree       Architecture tree\n:optimize   Optimize architecture\n:clear      Clear output\n:load       Load an example\n:exercises  List exercises"))

s.append(h1("8. Keyboard Shortcuts"))
s.append(make_table(
    ["Shortcut", "Action"],
    [
        ["Ctrl+F", "Find and Replace"],
        ["Tab", "Indent / Auto-complete"],
        ["Shift+Tab", "Outdent"],
        ["Ctrl+S", "Save/Download file"],
    ],
    col_widths=[80, CONTENT_W-80]
))
s.append(sp(6))

s.append(h1("9. Troubleshooting"))
s.append(bullet("<b>Compilation errors</b> - Use Verify before Compile to catch specification issues early."))
s.append(bullet("<b>Empty output</b> - Make sure you clicked Compile first. Audit and Explain require a compilation result."))
s.append(bullet("<b>File not loading</b> - Ensure the file has a .aicl extension and valid UTF-8 encoding."))
s.append(bullet("<b>REPL not responding</b> - Click inside the REPL input field to focus it."))
s.append(bullet("<b>Copy button not working</b> - Your browser may block clipboard access. Use Ctrl+C manually."))

doc2.build(s, onFirstPage=add_page_number2, onLaterPages=add_page_number2)
print(f"Generated: {output2} ({os.path.getsize(output2)/1024:.0f} KB)")
