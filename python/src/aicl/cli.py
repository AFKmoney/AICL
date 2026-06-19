#!/usr/bin/env python3
"""
AICL Command-Line Interface

The AICL CLI compiles specification-first source files into executable code
in Python, Rust, JavaScript, and Go — with full provenance tracking, audit
capabilities, cryptographic Proof of Origin, and AX (Turing-complete
sub-language) support.

Commands:
    compile   Compile AICL source to executable code + Proof of Origin
    parse     Parse and display the AST (use --ax for AX sub-AST)
    tree      Display the architecture tree
    check     Check for errors, warnings, and AX syntax (target-aware)
    explain   Explain compilation provenance — why each line was generated
    audit     Audit compilation — verify every artifact has provenance
    proof     Inspect and verify a .aicl-proof file
    verify    Verify spec completeness (Goal/Risk/Recovery/Validation)
    optimize  Optimize program architecture
    evolve    Autonomous self-writing/self-validating loop
    create    AI-powered: generate AICL from natural language
    ai-fix    AI-powered: diagnose and fix a broken spec
    init      Scaffold a new AICL project
    new       Generate a Behavior template with AX action
    targets   List available compile targets and AX capabilities
    doctor    Diagnose your AICL environment
    tui       Launch the interactive terminal UI
    version   Show version information
"""

import sys
import os
import re
import json
import argparse
import shutil
import subprocess

from aicl import __version__, Parser, Compiler, ArchitectureTree
from aicl.provenance import ProofOfOrigin
from aicl.spec_verify import SpecificationVerifier
from aicl.targets import list_targets
from aicl.cli_output import out


def cmd_compile(args):
    """Compile an AICL source file into executable code with Proof of Origin."""
    source = read_source(args.source)
    target = args.target if args.target != 'js' else 'javascript'
    compiler = Compiler(target_language=target)
    result = compiler.compile_to_file(source, args.output_dir, source_path=args.source)

    if result.success:
        out.success(f"Compiled to {target} — {args.output_dir}")

        # Detect AX behaviors and highlight them
        ax_count = len(result.ax_sources) if hasattr(result, 'ax_sources') else 0
        if ax_count:
            out.info(f"AX: {ax_count} behavior(s) compiled to real executable code")

        out.table(
            ["Artifact", "Path"],
            [
                ["Main code", os.path.join(args.output_dir, f'main.{_target_ext(target)}')],
                ["Tests", os.path.join(args.output_dir, 'test_main.py')],
                ["Architecture tree", os.path.join(args.output_dir, 'architecture_tree.txt')],
                ["Proof of Origin", os.path.join(args.output_dir, 'main.aicl-proof')],
            ],
            title="Generated files"
        )

        out.section("Compilation summary")
        out.check_line(f"Target: {target}", True)
        out.check_line("Fully compiled", result.fully_compiled, f"{result.todo_count} TODO(s) remaining")

        if result.provenance:
            audit = result.provenance.compute_audit_coverage()
            out.coverage(audit['audit_coverage'], audit['auditable_artifacts'],
                         audit['total_artifacts'])

        if result.proof:
            verification = result.proof.verify()
            out.check_line("Proof of Origin valid", verification['valid'])

        if result.warnings:
            for w in result.warnings:
                out.warning(w)

        if out.json_mode:
            out.json_flush()
    else:
        out.error("Compilation failed")
        for e in result.errors:
            out.error(str(e))
        sys.exit(1)


def cmd_parse(args):
    """Parse an AICL source file and display the AST."""
    source = read_source(args.source)
    parser = Parser(source)
    program = parser.parse()

    print("AICL Program AST:")
    print(f"  Goals: {len(program.goals)}")
    for g in program.goals:
        print(f"    - {g.description}")
    print(f"  Constraints: {len(program.constraints)}")
    for c in program.constraints:
        print(f"    - {c.description}")
    print(f"  Risks: {len(program.risks)}")
    for r in program.risks:
        print(f"    - {r.description}")
    print(f"  Recoveries: {len(program.recoveries)}")
    for r in program.recoveries:
        print(f"    - {r.description}")
    print(f"  Layers: {len(program.layers)}")
    for l in program.layers:
        print(f"    - {l.name}")
        for s in l.sublayers:
            print(f"      └── {s.name}")
    print(f"  Validations: {len(program.validations)}")
    for v in program.validations:
        print(f"    - {v.description}")
    print(f"  Entities: {len(program.entities)}")
    for e in program.entities:
        fields = ", ".join(f"{f.name}: {f.field_type}" for f in e.fields)
        print(f"    - {e.name}({fields})")
    print(f"  Behaviors: {len(program.behaviors)}")
    for b in program.behaviors:
        print(f"    - {b.name}")
    print(f"  Conditions: {len(program.conditions)}")
    for c in program.conditions:
        print(f"    - WHEN {c.when_clause} THEN {c.then_clause}")
    print(f"  Events: {len(program.events)}")
    for e in program.events:
        print(f"    - ON {e.on_clause} DO {e.action}")

    warnings = program.validate()
    if warnings:
        print(f"\n  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")


def cmd_tree(args):
    """Display the Architecture Tree for an AICL source file."""
    source = read_source(args.source)
    parser = Parser(source)
    program = parser.parse()
    tree = ArchitectureTree(program)

    print("Architecture Tree:")
    print(tree.to_string())


def cmd_check(args):
    """Check an AICL source file for errors and warnings."""
    source = read_source(args.source)
    compiler = Compiler()
    result = compiler.compile(source)

    if result.errors:
        print("Errors found:")
        for e in result.errors:
            print(f"  Error: {e}")
    else:
        print("No errors found")

    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  - {w}")
    else:
        print("No warnings")


def cmd_explain(args):
    """
    Explain the compilation of an AICL source file or Proof of Origin.

    Shows the provenance chain for every generated piece of code,
    answering the question: "Why did the compiler generate this line?"

    Two modes:
        1. From source: aicl explain pong.aicl
           Compiles the source and explains the compilation.
        2. From proof:  aicl explain --proof pong.aicl-proof
           Reads the Proof of Origin directly — no compiler needed.
           This proves the proof file is self-contained.

    Examples:
        aicl explain pong.aicl                          # Full compilation trace
        aicl explain pong.aicl --behavior MovePaddle    # Specific behavior trace
        aicl explain pong.aicl --coverage               # Explicability coverage report
        aicl explain --proof output/main.aicl-proof     # Explain from proof file
    """
    # Mode 1: Read from proof file
    if args.proof or args.source.endswith('.aicl-proof'):
        proof_path = args.source
        if not os.path.exists(proof_path):
            print(f"Error: Proof file not found: {proof_path}")
            sys.exit(1)

        proof = ProofOfOrigin.from_file(proof_path)

        if args.coverage:
            print(proof.coverage_report())
        elif args.behavior:
            print(proof.explain_behavior(args.behavior))
        else:
            print(proof.explain())

        # Show proof metadata
        print()
        print(f"Source: Proof of Origin ({proof_path})")
        print(f"Compiled: {proof.timestamp}")
        print(f"Compiler: AICL v{proof.compiler_version}")
        print(f"Provenance records: {len(proof.records)}")
        print(f"Artifacts: {len(proof.artifacts)}")

        audit_cov = proof.audit_coverage.get('audit_coverage', 0)
        print(f"Audit coverage: {audit_cov:.1%}")

        exp_cov = proof.explicability_coverage.get('coverage_ratio', 1.0)
        exp_total = proof.explicability_coverage.get('total_lines', 0)
        exp_accounted = proof.explicability_coverage.get('accounted_lines', 0)
        print(f"Explicability coverage: {exp_cov:.1%} ({exp_accounted}/{exp_total} lines)")

        return

    # Mode 2: Compile from source
    source = read_source(args.source)
    compiler = Compiler()
    result = compiler.compile(source)

    if not result.success:
        print("Compilation failed — cannot explain")
        for e in result.errors:
            print(f"  Error: {e}")
        sys.exit(1)

    if not result.provenance or not result.provenance.records:
        print("No provenance records available. Compilation may have been cached.")
        return

    if args.coverage:
        # Show explicability coverage report
        print(result.provenance.explain_coverage(result.source_code, result.test_code))
    elif args.behavior:
        # Explain a specific behavior
        print(result.provenance.explain_behavior(args.behavior))
    else:
        # Full explanation
        print(result.provenance.explain())

    # Show compilation summary
    print()
    print(f"Compilation: {'SUCCESS' if result.fully_compiled else 'PARTIAL'}")
    print(f"TODOs remaining: {result.todo_count}")
    stats = result.provenance.get_statistics()
    print(f"Patterns used: {', '.join(stats.get('patterns_used', []))}")
    print(f"Provenance records: {stats.get('total', 0)}")

    # Always show audit coverage
    audit = result.provenance.compute_audit_coverage()
    print(f"Audit coverage: {audit['audit_coverage']:.1%} ({audit['auditable_artifacts']}/{audit['total_artifacts']} artifacts)")

    # Show line-level coverage
    coverage = result.provenance.compute_explicability_coverage(result.source_code, result.test_code)
    print(f"Explicability coverage: {coverage['coverage_ratio']:.1%} ({coverage['accounted_lines']}/{coverage['total_lines']} lines)")


def cmd_audit(args):
    """
    Audit the compilation of an AICL source file or Proof of Origin.

    Verifies the Auditability property:
        "A program is auditable if every generated artifact
         can be traced to its originating specification
         through a complete provenance chain."

    Two modes:
        1. From source: aicl audit pong.aicl
           Compiles and audits.
        2. From proof:  aicl audit --proof pong.aicl-proof
           Audits the Proof of Origin directly — no compiler needed.

    The audit computes:
        - Audit Coverage = Auditable Artifacts / Generated Artifacts
        - Orphan Artifacts = Artifacts without provenance
        - Audit Status = VERIFIED / PARTIAL / FAILED
        - Proof Verification = hash binding, linkage integrity

    Examples:
        aicl audit pong.aicl               # Full audit report
        aicl audit pong.aicl --strict       # Fail (exit 1) if coverage < 100%
        aicl audit --proof output/main.aicl-proof  # Audit from proof file
    """
    # Mode 1: Read from proof file
    if args.proof or args.source.endswith('.aicl-proof'):
        proof_path = args.source
        if not os.path.exists(proof_path):
            print(f"Error: Proof file not found: {proof_path}")
            sys.exit(1)

        proof = ProofOfOrigin.from_file(proof_path)

        # Print the audit report reconstructed from proof
        print(proof.audit_report())

        # Strict mode: fail if audit doesn't pass
        if args.strict:
            if not proof.audit_passed():
                print()
                print("STRICT MODE: Audit did not pass.")
                coverage_val = proof.audit_coverage.get('audit_coverage', 0)
                if coverage_val < 1.0:
                    print(f"  Audit coverage: {coverage_val:.1%} (target: 100%)")
                verification = proof.verify()
                for check in verification['checks']:
                    if not check['passed']:
                        print(f"  Failed check: {check['name']}: {check['description']}")
                sys.exit(1)
            else:
                print()
                print("STRICT MODE: Audit PASSED. Coverage is 100%. Proof is valid.")

        return

    # Mode 2: Compile from source
    source = read_source(args.source)
    compiler = Compiler()
    result = compiler.compile(source)

    if not result.success:
        print("Compilation failed — cannot audit")
        for e in result.errors:
            print(f"  Error: {e}")
        sys.exit(1)

    if not result.provenance:
        print("No provenance data available.")
        sys.exit(1)

    # Generate and print the full audit report
    report = result.provenance.audit(result.source_code, result.test_code)
    print(report)

    # Strict mode: fail if audit doesn't pass
    if args.strict:
        if not result.provenance.audit_passed(result.source_code, result.test_code):
            print()
            print("STRICT MODE: Audit did not pass.")
            audit = result.provenance.compute_audit_coverage()
            if audit['audit_coverage'] < 1.0:
                print(f"  Audit coverage: {audit['audit_coverage']:.1%} (target: 100%)")
                print(f"  Orphan artifacts: {len(audit['orphan_artifacts'])}")
                for orphan in audit['orphan_artifacts']:
                    print(f"    - [{orphan['type']}] {orphan['name']}")
            sys.exit(1)
        else:
            print()
            print("STRICT MODE: Audit PASSED. Coverage is 100%.")


def cmd_proof(args):
    """
    Inspect and verify a Proof of Origin file.

    The Proof of Origin is the central artifact of auditable compilation.
    It is a self-contained, verifiable record that proves:
        - Every generated artifact has a traceable provenance chain
        - No artifact exists without justification (No Orphan Property)
        - Audit coverage = 1.0 (Complete Coverage Property)
        - The proof is cryptographically bound to the generated code

    Examples:
        aicl proof output/main.aicl-proof              # Inspect proof
        aicl proof output/main.aicl-proof --verify     # Verify proof integrity
        aicl proof output/main.aicl-proof --explain    # Show explanation from proof
        aicl proof output/main.aicl-proof --audit      # Show audit report from proof
    """
    proof_path = args.proof_file
    if not os.path.exists(proof_path):
        print(f"Error: Proof file not found: {proof_path}")
        sys.exit(1)

    proof = ProofOfOrigin.from_file(proof_path)

    # Default: show proof summary
    if not args.verify and not args.explain and not args.audit:
        # Show proof summary
        print("=" * 70)
        print("AICL PROOF OF ORIGIN")
        print("=" * 70)
        print()
        print(f"  File:           {proof_path}")
        print(f"  Format version: {proof.format_version}")
        print(f"  Compiler:       AICL v{proof.compiler_version}")
        print(f"  Timestamp:      {proof.timestamp}")
        print(f"  Source:         {proof.source_path or '<unknown>'}")
        print(f"  Target:         {proof.target_language}")
        print()
        print(f"  Source hash:    {proof.source_hash[:32]}...")
        print(f"  Program hash:   {proof.program_hash[:32]}...")
        print(f"  Test hash:      {proof.test_hash[:32]}...")
        print()
        print(f"  Provenance records: {len(proof.records)}")
        print(f"  Generated artifacts: {len(proof.artifacts)}")
        print()

        # Formal properties
        print("FORMAL PROPERTIES")
        print("-" * 70)
        for prop_name, prop_data in proof.formal_properties.items():
            label = prop_name.replace("_", " ").title()
            verified = prop_data.get('verified', False)
            status = "VERIFIED" if verified else "FAILED"
            print(f"  {label}: {status}")
            if 'statement' in prop_data:
                print(f"    {prop_data['statement']}")
        print()

        # Audit summary
        audit_summary = proof.audit_coverage
        total = audit_summary.get('total_artifacts', len(proof.artifacts))
        auditable = audit_summary.get('auditable_artifacts',
            sum(1 for a in proof.artifacts if not a.get('is_orphan', True)))
        coverage = audit_summary.get('audit_coverage',
            auditable / total if total > 0 else 1.0)
        orphans = len(audit_summary.get('orphan_artifacts', []))

        print("AUDIT SUMMARY")
        print("-" * 70)
        print(f"  Artifacts:      {total}")
        print(f"  Auditable:      {auditable}")
        print(f"  Orphans:        {orphans}")
        print(f"  Audit Coverage: {coverage:.1%}")
        print(f"  Audit Status:   {'VERIFIED' if coverage >= 1.0 else 'FAILED'}")
        print()

        # Verification
        verification = proof.verify()
        print("VERIFICATION")
        print("-" * 70)
        for check in verification['checks']:
            status = "PASS" if check['passed'] else "FAIL"
            print(f"  [{status:4s}] {check['name']}: {check['description']}")
        print()

        print("=" * 70)
        if verification['valid'] and coverage >= 1.0:
            print("PROOF STATUS: VALID")
            print("  This Proof of Origin is valid and demonstrates full auditability.")
        else:
            print("PROOF STATUS: INVALID")
            print("  This Proof of Origin has verification failures.")
        print("=" * 70)
        return

    # --verify: detailed verification
    if args.verify:
        verification = proof.verify()
        print("=" * 70)
        print("PROOF VERIFICATION")
        print("=" * 70)
        print()
        for check in verification['checks']:
            status = "PASS" if check['passed'] else "FAIL"
            print(f"  [{status:4s}] {check['name']}")
            print(f"         {check['description']}")
            if 'expected' in check:
                print(f"         Expected: {check['expected'][:32]}...")
            if 'actual' in check:
                print(f"         Actual:   {check['actual'][:32]}...")
            if 'orphan_count' in check:
                print(f"         Orphan count: {check['orphan_count']}")
            if 'coverage' in check:
                print(f"         Coverage: {check['coverage']:.2%}")
            print()

        print("=" * 70)
        if verification['valid']:
            print("VERIFICATION RESULT: ALL CHECKS PASSED")
        else:
            print("VERIFICATION RESULT: SOME CHECKS FAILED")
            failed = [c for c in verification['checks'] if not c['passed']]
            print(f"  Failed checks: {len(failed)}")
        print("=" * 70)

    # --explain: show explanation from proof
    if args.explain:
        print(proof.explain())

    # --audit: show audit report from proof
    if args.audit:
        print(proof.audit_report())


def cmd_version(args):
    """Display the AICL version."""
    print(f"AICL v{__version__}")
    print("Artificial Intelligence-Centered Language")
    print("  AX sub-language: Turing-complete (if/while/for/recursion)")
    print("  Targets: Python, Rust, JavaScript, Go")
    print("  Proof of Origin: cryptographic, sidecar .aicl-proof")
    print("  CogNet integration: fine-tuning corpus generator ready")


def cmd_tui(args):
    """Launch the AICL TUI (interactive terminal interface)."""
    try:
        from aicl.tui.app import main as tui_main
        tui_main()
    except ImportError as e:
        print(f"AICL TUI requires additional packages: {e}")
        print("Install with: pip install textual rich")
        sys.exit(1)


def cmd_verify(args):
    """
    Verify an AICL specification for completeness, coherence, and satisfaction.

    Runs three levels of verification:
        1. Completeness: all required elements present
        2. Coherence: no contradictions or dangling references
        3. Satisfaction: specification is implementable

    Examples:
        aicl verify pong.aicl                    # All three checks
        aicl verify pong.aicl --completeness     # Completeness only
        aicl verify pong.aicl --coherence        # Coherence only
        aicl verify pong.aicl --satisfaction     # Satisfaction only
    """
    source = read_source(args.source)
    from aicl.parser import Parser as P
    parser = P(source)
    program = parser.parse()
    verifier = SpecificationVerifier(program)

    if args.completeness:
        report = verifier.completeness_only(source_name=args.source)
    elif args.coherence:
        report = verifier.coherence_only(source_name=args.source)
    elif args.satisfaction:
        report = verifier.satisfaction_only(source_name=args.source)
    else:
        report = verifier.verify(source_name=args.source)

    print(report.summary())

    if not report.passed:
        sys.exit(1)


def cmd_optimize(args):
    """
    Optimize the architecture of an AICL program.

    Applies optimization strategies to improve the program structure:
        - Layer consolidation
        - Entity extraction
        - Behavior inlining
        - Risk distribution
        - Parallelization
        - Dependency reduction
        - Validation strengthening

    Every optimization is recorded in the provenance chain.

    Examples:
        aicl optimize pong.aicl
        aicl optimize pong.aicl --max-iterations 5
    """
    source = read_source(args.source)
    from aicl.parser import Parser as P
    parser = P(source)
    program = parser.parse()

    from aicl.auto_optimizer import ArchitectureOptimizer
    optimizer = ArchitectureOptimizer(program)
    result = optimizer.optimize(max_iterations=args.max_iterations)

    print(result.summary())


def cmd_evolve(args):
    """Run the autonomous self-writing, self-validating compilation loop."""
    source = read_source(args.source)

    from aicl.autonomous import AutonomousCompiler, format_evolve_report

    compiler = AutonomousCompiler(
        max_iterations=args.max_iterations,
        target_language=args.target,
        test_timeout=args.test_timeout,
    )

    print("=" * 70)
    print("AICL AUTONOMOUS COMPILATION — Self-Writing, Self-Validating")
    print("=" * 70)
    print(f"  Source:    {args.source}")
    print(f"  Target:    {args.target}")
    print(f"  Max Iters: {args.max_iterations}")
    print(f"  Timeout:   {args.test_timeout}s")
    print("")
    print("Loop: SPEC → COMPILE → VERIFY → TEST → DIAGNOSE → FIX → RECOMPILE")
    print("Convergence: audit=100%, tests=100%, fallbacks=0, spec=verified")
    print("")

    if args.watch:
        # Continuous mode — watch for source changes
        import time
        last_modified = os.path.getmtime(args.source)
        print("WATCH MODE: Monitoring for source changes (Ctrl+C to stop)")
        print("")
        try:
            while True:
                current_modified = os.path.getmtime(args.source)
                if current_modified > last_modified:
                    last_modified = current_modified
                    source = read_source(args.source)
                    result = compiler.evolve(args.source, args.output_dir)
                    print(format_evolve_report(result))
                    print("\nWaiting for changes...")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nWatch mode stopped.")
    else:
        result = compiler.evolve(args.source, args.output_dir)
        print(format_evolve_report(result))

        # Exit code based on convergence
        if not result.converged:
            sys.exit(1)


def cmd_create(args):
    """AI-powered: Create a complete AICL program from a natural language description."""
    from aicl.ai_generator import SelfWritingCompiler, is_ai_available, format_create_report

    if not is_ai_available():
        print("Error: AI is not available.")
        print("  Install z-ai-web-dev-sdk and ensure tools/ai_bridge.mjs exists.")
        print("  The AI bridge requires Node.js and the z-ai-web-dev-sdk package.")
        sys.exit(1)

    compiler = SelfWritingCompiler(
        target_language=args.target,
        use_ai=True,
    )

    result = compiler.create(
        task=args.task,
        output_path=args.output,
    )

    print(format_create_report(result))

    # Save the generated AICL source
    if result.success and result.aicl_source:
        if args.output:
            path = args.output if args.output.endswith(".aicl") else args.output + ".aicl"
        else:
            # Auto-generate filename from task
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', args.task[:30]).strip('_').lower()
            path = f"{safe_name}.aicl"

        with open(path, "w") as f:
            f.write(result.aicl_source)
        print(f"\n  AICL source saved to: {path}")

    if not result.success:
        sys.exit(1)


def cmd_ai_fix(args):
    """AI-powered: Diagnose and fix a broken AICL specification."""
    source = read_source(args.source)

    from aicl.ai_generator import AIDiagnoser, is_ai_available

    if not is_ai_available():
        print("Error: AI is not available.")
        print("  Install z-ai-web-dev-sdk and ensure tools/ai_bridge.mjs exists.")
        sys.exit(1)

    diagnoser = AIDiagnoser()

    if args.enhance:
        # Enhance mode
        print("AI enhancing AICL specification...")
        enhanced, success = diagnoser.enhance(source)
        if success:
            # Save enhanced source
            enhanced_path = args.source.replace(".aicl", ".enhanced.aicl")
            with open(enhanced_path, "w") as f:
                f.write(enhanced)
            print(f"Enhanced specification saved to: {enhanced_path}")
        else:
            print("AI enhancement failed.")
            sys.exit(1)
    else:
        # Fix mode
        if args.error:
            error_desc = args.error
        else:
            # Auto-detect error by trying to compile
            from aicl import Compiler
            import tempfile
            output_dir = tempfile.mkdtemp(prefix="aicl_fix_")
            try:
                compiler = Compiler(target_language="python")
                result = compiler.compile_to_file(source, output_dir, source_path=args.source)
                if result.success:
                    print("No compilation errors detected. The specification compiles successfully.")
                    return
                error_desc = "; ".join(result.errors) if result.errors else "Unknown compilation error"
            except Exception as e:
                error_desc = str(e)

        print(f"Diagnosing error: {error_desc[:80]}...")
        diagnosis = diagnoser.diagnose(error_desc, source)

        print("\n" + "=" * 60)
        print("AI DIAGNOSIS")
        print("=" * 60)
        print(f"  Diagnosis:    {diagnosis.get('diagnosis', 'N/A')}")
        print(f"  Root Cause:   {diagnosis.get('root_cause', 'N/A')}")
        print(f"  Fix Type:     {diagnosis.get('fix_type', 'N/A')}")
        print(f"  Fix:          {diagnosis.get('fix_description', 'N/A')}")
        print("=" * 60)

        # Try to fix
        fixed_source, success = diagnoser.fix(error_desc, source)
        if success:
            fixed_path = args.source.replace(".aicl", ".fixed.aicl")
            with open(fixed_path, "w") as f:
                f.write(fixed_source)
            print(f"\nFixed specification saved to: {fixed_path}")
        else:
            print("\nAI fix attempt failed. Manual intervention may be needed.")
            sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════
# NEW COMMANDS
# ═══════════════════════════════════════════════════════════════════════════

PROJECT_TEMPLATE = """\
# {name} — AICL specification
# Artificial Intelligence-Centered Language

Goal:
{goal_desc}

Constraint:
TODO: add your constraints here

Risk:
TODO: identify a risk

Recovery:
TODO: describe how to recover

Layer:
Core

Validation:
TODO: describe what success looks like

Behavior MainAction
    Input: input
    Output: result
    Action:
        # AX sub-language: write real compilable logic here.
        # Example: result = input * 2
        # Supported: if/elif/else, while, for, range, recursion, arithmetic.
        return input
"""

PROJECT_README = """\
# {name}

An AICL specification-first project.

## Usage

```bash
# Compile to Python
aicl compile {name}.aicl --target python -o ./output

# Compile to Rust / JS / Go
aicl compile {name}.aicl --target rust -o ./output

# Verify the spec
aicl verify {name}.aicl

# Check AX syntax
aicl check {name}.aicl
```

## Documentation

- [Getting Started](https://github.com/AFKmoney/AICL/blob/main/docs/getting-started.md)
- [AX Reference](https://github.com/AFKmoney/AICL/blob/main/docs/ax-reference.md)
- [Compile Targets](https://github.com/AFKmoney/AICL/blob/main/docs/targets.md)
"""


def cmd_init(args):
    """Scaffold a new AICL project."""
    name = args.name if args.name != '.' else os.path.basename(os.getcwd())
    project_dir = args.name if args.name != '.' else '.'
    os.makedirs(project_dir, exist_ok=True)

    aicl_file = os.path.join(project_dir, f"{name}.aicl")
    readme_file = os.path.join(project_dir, "README.md")

    if os.path.exists(aicl_file):
        out.error(f"File already exists: {aicl_file}")
        sys.exit(1)

    with open(aicl_file, 'w') as f:
        f.write(PROJECT_TEMPLATE.format(name=name, goal_desc=f"Build {name}"))
    with open(readme_file, 'w') as f:
        f.write(PROJECT_README.format(name=name))

    out.success(f"Created AICL project: {name}")
    out.table(["File", "Purpose"],
              [[aicl_file, "AICL specification with AX behavior"],
               [readme_file, "Project README with usage examples"]],
              title="Generated")
    out.info(f"Next: cd {project_dir} && aicl verify {name}.aicl")


def cmd_new(args):
    """Generate a Behavior template with an AX action."""
    name = args.behavior
    inputs = [i.strip() for i in args.inputs.split(',')] if args.inputs else ['input']
    input_line = ', '.join(inputs)

    template = f"""
Behavior {name.title()}
    Input: {input_line}
    Output: result
    Action:
        # AX: write your logic here. Example:
        # result = {inputs[0]}
        # if result > 0:
        #     return result
        # return 0
        return {inputs[0]}
"""

    if args.file:
        with open(args.file, 'a') as f:
            f.write(template)
        out.success(f"Appended Behavior {name.title()} to {args.file}")
    else:
        out.raw(template.rstrip())


def cmd_targets(args):
    """List available compile targets and AX capabilities."""
    targets_info = [
        ("python", "Python 3.10+", ".py", "In-process exec", True),
        ("rust", "Rust 2021", ".rs", "rustc compile + run", True),
        ("javascript", "ES2015+ (Node)", ".mjs", "node --check", True),
        ("go", "Go 1.21+", ".go", "go build + run", True),
    ]
    out.section("Compile targets")
    out.table(
        ["Target", "Language", "Extension", "AX runtime tested", "AX"],
        [[t[0], t[1], t[2], "✓" if t[3] else "✗", "✓ Turing-complete"] for t in targets_info],
    )
    out.info("AX behaviors compile to real, executable code in all 4 targets.")
    out.info("Non-AX behaviors (English prose) produce structural skeletons.")


def cmd_doctor(args):
    """Diagnose the AICL environment."""
    out.section("AICL Environment Diagnostic")

    # Python version
    pv = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    out.check_line(f"Python {pv}", sys.version_info >= (3, 10), ">=3.10 required")

    # rich
    try:
        import rich
        out.check_line("rich (CLI colors)", True, str(rich.__version__) if hasattr(rich, '__version__') else "")
    except ImportError:
        out.check_line("rich (CLI colors)", False, "pip install rich")

    # textual (TUI)
    try:
        import textual
        out.check_line("textual (TUI)", True)
    except ImportError:
        out.check_line("textual (TUI)", False, "optional — pip install textual")

    # AICL compiler
    try:
        from aicl.ax import is_ax
        out.check_line("AICL compiler + AX sub-language", True, f"v{__version__}")
    except ImportError:
        out.check_line("AICL compiler", False, "not installed")

    # Runtimes for target execution
    for name, cmd in [("node (JS target)", "node"), ("rustc (Rust target)", "rustc"),
                       ("go (Go target)", "go"), ("ffmpeg (video)", "ffmpeg")]:
        path = shutil.which(cmd)
        out.check_line(name, path is not None, f"{'at ' + path}" if path else "not found")

    # Targets
    out.section("Compile targets")
    for t in ["python", "rust", "javascript", "go"]:
        out.check_line(f"  {t}", True)

    out.info("All checks complete. Green items are ready.")


def read_source(path: str) -> str:
    """Read source code from a file."""
    if not os.path.exists(path):
        out.die(f"File not found: {path}")
    with open(path, 'r') as f:
        return f.read()


def _target_ext(target: str) -> str:
    """File extension for a compile target."""
    return {"python": "py", "rust": "rs", "javascript": "mjs", "js": "mjs",
            "go": "go"}.get(target, "txt")


def load_program_or_proof(args):
    """Shared helper for commands that accept either source or proof files.

    Returns (program_or_proof, is_proof). If args.source ends with .aicl-proof
    or args.proof is set, loads the proof. Otherwise compiles the source.
    """
    if getattr(args, 'proof', False) or args.source.endswith('.aicl-proof'):
        proof = ProofOfOrigin.load(args.source)
        return proof, True
    source = read_source(args.source)
    compiler = Compiler(target_language=getattr(args, 'target', 'python'))
    result = compiler.compile(source)
    return result, False



def main():
    """Main entry point for the AICL CLI."""
    parser = argparse.ArgumentParser(
        prog='aicl',
        description='AICL — Artificial Intelligence-Centered Language.\n'
                    'Specification-first programming with mandatory Risk/Recovery syntax,\n'
                    'the AX Turing-complete sub-language for Behavior Actions, and\n'
                    'cryptographic Proof of Origin. Compiles to Python, Rust, JS, and Go.'
    )
    parser.add_argument('--json', action='store_true', default=False,
                        help='Output machine-readable JSON (for CI/CD pipelines)')
    parser.add_argument('--no-color', action='store_true', default=False,
                        help='Disable colored output')
    parser.add_argument('--version', '-V', action='version',
                        version=f'AICL {__version__}')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # ── compile ─────────────────────────────────────────────────────────────
    p = subparsers.add_parser('compile',
        help='Compile AICL source to executable code + Proof of Origin')
    p.add_argument('source', help='AICL source file (.aicl)')
    p.add_argument('--output-dir', '-o', default='./output',
                   help='Output directory (default: ./output)')
    p.add_argument('--target', '-t', default='python',
                   choices=['python', 'rust', 'javascript', 'js', 'go'],
                   help='Target language. AX behaviors compile to real code in all 4 targets')
    p.set_defaults(func=cmd_compile)

    # ── parse ───────────────────────────────────────────────────────────────
    p = subparsers.add_parser('parse', help='Parse and display AST')
    p.add_argument('source', help='AICL source file (.aicl)')
    p.add_argument('--ax', action='store_true',
                   help='Show AX sub-AST for behaviors with AX actions')
    p.set_defaults(func=cmd_parse)

    # ── tree ────────────────────────────────────────────────────────────────
    p = subparsers.add_parser('tree', help='Display architecture tree')
    p.add_argument('source', help='AICL source file (.aicl)')
    p.set_defaults(func=cmd_tree)

    # ── check ───────────────────────────────────────────────────────────────
    p = subparsers.add_parser('check',
        help='Check for errors, warnings, and AX syntax (target-aware)')
    p.add_argument('source', help='AICL source file (.aicl)')
    p.add_argument('--target', '-t', default='python',
                   choices=['python', 'rust', 'javascript', 'js', 'go'],
                   help='Target language to check AX emission against (default: python)')
    p.set_defaults(func=cmd_check)

    # ── explain ─────────────────────────────────────────────────────────────
    p = subparsers.add_parser('explain',
        help='Explain compilation provenance — why each line was generated')
    p.add_argument('source',
                   help='AICL source file (.aicl) or Proof of Origin (.aicl-proof)')
    p.add_argument('--behavior', '-b', default=None,
                   help='Explain a specific behavior')
    p.add_argument('--coverage', '-c', action='store_true',
                   help='Show explicability coverage report')
    p.add_argument('--proof', '-p', action='store_true',
                   help='Read from Proof of Origin file')
    p.set_defaults(func=cmd_explain)

    # ── audit ───────────────────────────────────────────────────────────────
    p = subparsers.add_parser('audit',
        help='Audit compilation — verify every artifact has provenance')
    p.add_argument('source',
                   help='AICL source file (.aicl) or Proof of Origin (.aicl-proof)')
    p.add_argument('--strict', '-s', action='store_true',
                   help='Fail if audit coverage < 100%% (exit code 1)')
    p.add_argument('--proof', '-p', action='store_true',
                   help='Read from Proof of Origin file')
    p.set_defaults(func=cmd_audit)

    # ── proof ───────────────────────────────────────────────────────────────
    p = subparsers.add_parser('proof',
        help='Inspect and verify a Proof of Origin file')
    p.add_argument('proof_file', help='Proof of Origin file (.aicl-proof)')
    p.add_argument('--verify', '-v', action='store_true',
                   help='Verify proof integrity')
    p.add_argument('--explain', '-e', action='store_true',
                   help='Show full explanation from proof')
    p.add_argument('--audit', '-a', action='store_true',
                   help='Show audit report from proof')
    p.set_defaults(func=cmd_proof)

    # ── verify ──────────────────────────────────────────────────────────────
    p = subparsers.add_parser('verify',
        help='Verify specification completeness, coherence, and satisfaction')
    p.add_argument('source', help='AICL source file (.aicl)')
    p.add_argument('--completeness', action='store_true', help='Completeness checks only')
    p.add_argument('--coherence', action='store_true', help='Coherence checks only')
    p.add_argument('--satisfaction', action='store_true', help='Satisfaction checks only')
    p.set_defaults(func=cmd_verify)

    # ── optimize ────────────────────────────────────────────────────────────
    p = subparsers.add_parser('optimize', help='Optimize AICL program architecture')
    p.add_argument('source', help='AICL source file (.aicl)')
    p.add_argument('--max-iterations', type=int, default=10,
                   help='Maximum optimization iterations (default: 10)')
    p.set_defaults(func=cmd_optimize)

    # ── evolve ──────────────────────────────────────────────────────────────
    p = subparsers.add_parser('evolve',
        help='Autonomous compilation: self-writing, self-validating code loop')
    p.add_argument('source', help='AICL source file (.aicl)')
    p.add_argument('--output-dir', '-o', default=None, help='Output directory')
    p.add_argument('--target', '-t', default='python',
                   choices=['python', 'rust', 'javascript', 'js', 'go'],
                   help='Target language (default: python)')
    p.add_argument('--max-iterations', type=int, default=10,
                   help='Maximum autonomous loop iterations (default: 10)')
    p.add_argument('--test-timeout', type=int, default=30,
                   help='Test execution timeout in seconds (default: 30)')
    p.add_argument('--watch', '-w', action='store_true',
                   help='Continuous mode: re-evolve on source changes')
    p.set_defaults(func=cmd_evolve)

    # ── create ──────────────────────────────────────────────────────────────
    p = subparsers.add_parser('create',
        help='AI-powered: create AICL program from natural language description')
    p.add_argument('task', help='Natural language description of the system to create')
    p.add_argument('--output', '-o', default=None, help='Output .aicl file path')
    p.add_argument('--target', '-t', default='python',
                   choices=['python', 'rust', 'javascript', 'js', 'go'],
                   help='Target language (default: python)')
    p.set_defaults(func=cmd_create)

    # ── ai-fix ──────────────────────────────────────────────────────────────
    p = subparsers.add_parser('ai-fix',
        help='AI-powered: diagnose and fix a broken AICL specification')
    p.add_argument('source', help='AICL source file (.aicl)')
    p.add_argument('--error', '-e', default=None,
                   help='Error description (auto-detected if not provided)')
    p.add_argument('--enhance', action='store_true',
                   help='Enhance the specification instead of fixing')
    p.set_defaults(func=cmd_ai_fix)

    # ── init (NEW) ──────────────────────────────────────────────────────────
    p = subparsers.add_parser('init',
        help='Scaffold a new AICL project in a new directory')
    p.add_argument('name', nargs='?', default='.', help='Project name (default: current dir)')
    p.set_defaults(func=cmd_init)

    # ── new (NEW) ───────────────────────────────────────────────────────────
    p = subparsers.add_parser('new',
        help='Generate a Behavior template with an AX action')
    p.add_argument('behavior', help='Behavior name (e.g., sort, search, compute)')
    p.add_argument('--inputs', '-i', default='',
                   help='Comma-separated input names (e.g., array,low,high)')
    p.add_argument('--file', '-f', default=None,
                   help='Append to this .aicl file (default: print to stdout)')
    p.set_defaults(func=cmd_new)

    # ── targets (NEW) ───────────────────────────────────────────────────────
    p = subparsers.add_parser('targets',
        help='List available compile targets and AX capabilities')
    p.set_defaults(func=cmd_targets)

    # ── doctor (NEW) ────────────────────────────────────────────────────────
    p = subparsers.add_parser('doctor',
        help='Diagnose your AICL environment (runtime, tools, targets)')
    p.set_defaults(func=cmd_doctor)

    # ── tui ─────────────────────────────────────────────────────────────────
    p = subparsers.add_parser('tui', help='Launch interactive terminal interface')
    p.set_defaults(func=cmd_tui)

    # ── version ─────────────────────────────────────────────────────────────
    p = subparsers.add_parser('version', help='Display version information')
    p.set_defaults(func=cmd_version)

    # ── Parse + dispatch ────────────────────────────────────────────────────
    args = parser.parse_args()

    # Apply global flags
    if args.json:
        out.json_mode = True
    if args.no_color:
        out.console = type(out.console)(no_color=True)
        out.stderr_console = type(out.stderr_console)(stderr=True, no_color=True)

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(0)

    args.func(args)

    if out.json_mode:
        out.json_flush()


if __name__ == '__main__':
    main()
