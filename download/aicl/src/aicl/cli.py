#!/usr/bin/env python3
"""
AICL Command-Line Interface

Provides a CLI for compiling AICL source files into executable code.

Usage:
    aicl compile <source.aicl> [--output-dir <dir>] [--target <language>]
    aicl parse <source.aicl>
    aicl tree <source.aicl>
    aicl check <source.aicl>
    aicl version
"""

import sys
import os
import argparse

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aicl import __version__, Parser, Compiler, ArchitectureTree


def cmd_compile(args):
    """Compile an AICL source file into executable code."""
    source = read_source(args.source)
    compiler = Compiler(target_language=args.target)
    result = compiler.compile_to_file(source, args.output_dir)

    if result.success:
        print("Compilation successful")
        print(f"  Stages completed: {', '.join(result.stages_completed)}")
        print(f"  Output directory: {args.output_dir}")
        print(f"  Main file: {os.path.join(args.output_dir, 'main.py')}")
        print(f"  Test file: {os.path.join(args.output_dir, 'test_main.py')}")
        print(f"  Architecture tree: {os.path.join(args.output_dir, 'architecture_tree.txt')}")

        if result.warnings:
            print(f"\n  Warnings ({len(result.warnings)}):")
            for w in result.warnings:
                print(f"    - {w}")
    else:
        print("Compilation failed")
        for e in result.errors:
            print(f"  Error: {e}")
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


def cmd_version(args):
    """Display the AICL version."""
    print(f"AICL v{__version__}")
    print("AI-Centric Language: Specification-First Programming")


def read_source(path: str) -> str:
    """Read source code from a file."""
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)

    with open(path, 'r') as f:
        return f.read()


def main():
    """Main entry point for the AICL CLI."""
    parser = argparse.ArgumentParser(
        prog='aicl',
        description='AICL - AI-Centric Language Compiler'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # compile command
    compile_parser = subparsers.add_parser('compile', help='Compile AICL source code')
    compile_parser.add_argument('source', help='AICL source file (.aicl)')
    compile_parser.add_argument('--output-dir', '-o', default='./output',
                                help='Output directory (default: ./output)')
    compile_parser.add_argument('--target', '-t', default='python',
                                choices=['python'], help='Target language (default: python)')

    # parse command
    parse_parser = subparsers.add_parser('parse', help='Parse and display AST')
    parse_parser.add_argument('source', help='AICL source file (.aicl)')

    # tree command
    tree_parser = subparsers.add_parser('tree', help='Display Architecture Tree')
    tree_parser.add_argument('source', help='AICL source file (.aicl)')

    # check command
    check_parser = subparsers.add_parser('check', help='Check for errors and warnings')
    check_parser.add_argument('source', help='AICL source file (.aicl)')

    # version command
    version_parser = subparsers.add_parser('version', help='Display version')

    args = parser.parse_args()

    if args.command == 'compile':
        cmd_compile(args)
    elif args.command == 'parse':
        cmd_parse(args)
    elif args.command == 'tree':
        cmd_tree(args)
    elif args.command == 'check':
        cmd_check(args)
    elif args.command == 'version':
        cmd_version(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
