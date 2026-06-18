#!/usr/bin/env python3
"""
AICL Helper Script - JSON interface for the AICL Python library.
Called by Next.js API routes to perform AICL operations.

Usage:
    python3 aicl_helper.py compile --target python < source.aicl
    python3 aicl_helper.py verify < source.aicl
    python3 aicl_helper.py audit < source.aicl
    python3 aicl_helper.py explain < source.aicl
    python3 aicl_helper.py tree < source.aicl
    python3 aicl_helper.py optimize < source.aicl
    python3 aicl_helper.py exercises

Requires the `aicl` package to be installed (`pip install -e .` from the
repo root, or `pip install aicl` once published).
"""

import os
import sys
import json
import argparse

# Allow running directly from a source checkout without installing.
_REPO_SRC = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src"))
if os.path.isdir(_REPO_SRC):
    sys.path.insert(0, _REPO_SRC)

from aicl import (
    Parser, ParseError, Compiler, CompilationResult,
    ArchitectureTree, ArchitectureNode,
    SpecificationVerifier, VerificationReport, CheckStatus,
    ArchitectureOptimizer, OptimizationResult, OptimizationStrategy,
)
from aicl.provenance import CompilationProvenance, ProvenanceType, ProofOfOrigin
from aicl.auto_optimizer import OptimizationAction


def read_source():
    """Read AICL source from stdin."""
    return sys.stdin.read()


def cmd_compile(source, target="python"):
    """Compile AICL source code."""
    try:
        compiler = Compiler(target_language=target)
        result = compiler.compile(source)

        response = {
            "success": result.success,
            "main_code": result.source_code,
            "test_code": result.test_code,
            "warnings": result.warnings,
            "errors": result.errors,
            "todos_remaining": result.todo_count,
            "stages_completed": result.stages_completed,
            "fully_compiled": result.fully_compiled,
            "tree": result.architecture_tree_str,
        }

        # Add audit coverage if provenance available
        if result.provenance:
            artifacts = result.provenance.artifacts if hasattr(result.provenance, 'artifacts') else []
            total = len(artifacts)
            with_prov = sum(1 for a in artifacts if a.has_provenance)
            orphans = sum(1 for a in artifacts if a.is_orphan)
            response["audit_coverage"] = round(with_prov / total, 2) if total > 0 else 0.0
            response["total_artifacts"] = total
            response["orphan_count"] = orphans
        else:
            response["audit_coverage"] = 0.0
            response["total_artifacts"] = 0
            response["orphan_count"] = 0

        # Add proof info if available
        if result.proof:
            proof = result.proof
            response["proof_valid"] = True
            response["proof"] = {
                "version": proof.version if hasattr(proof, 'version') else "2.0",
                "source_hash": proof.source_hash if hasattr(proof, 'source_hash') else "",
            }
        else:
            response["proof_valid"] = False
            response["proof"] = None

        return response
    except Exception as e:
        return {"success": False, "errors": [str(e)], "main_code": "", "test_code": ""}


def cmd_verify(source):
    """Verify specification quality."""
    try:
        parser = Parser(source)
        program = parser.parse()
        verifier = SpecificationVerifier(program)
        report = verifier.verify()

        checks = []
        for result in report.all_results:
            checks.append({
                "name": result.name,
                "status": result.status.value,
                "message": result.message,
                "details": result.details,
            })

        return {
            "overall": "PASS" if report.passed else "FAIL",
            "checks": checks,
            "total": len(report.all_results),
            "passed": sum(1 for r in report.all_results if r.status == CheckStatus.PASS),
            "warnings": sum(1 for r in report.all_results if r.status == CheckStatus.WARN),
            "failed": sum(1 for r in report.all_results if r.status == CheckStatus.FAIL),
        }
    except ParseError as e:
        return {"overall": "ERROR", "checks": [{"name": "parse", "status": "FAIL", "message": str(e), "details": []}]}
    except Exception as e:
        return {"overall": "ERROR", "checks": [{"name": "error", "status": "FAIL", "message": str(e), "details": []}]}


def cmd_audit(source):
    """Audit compilation provenance."""
    try:
        compiler = Compiler()
        result = compiler.compile(source)

        if not result.success:
            return {"error": "Compilation failed", "details": result.errors}

        provenance = result.provenance
        artifacts = provenance.artifacts if hasattr(provenance, 'artifacts') else []
        total = len(artifacts)
        with_prov = sum(1 for a in artifacts if a.has_provenance)
        orphans = [a.name for a in artifacts if a.is_orphan]

        return {
            "total_artifacts": total,
            "artifacts_with_provenance": with_prov,
            "orphan_count": len(orphans),
            "orphan_names": orphans[:20],  # Limit to 20
            "coverage": round(with_prov / total, 4) if total > 0 else 0.0,
            "stages_completed": result.stages_completed,
        }
    except Exception as e:
        return {"error": str(e), "total_artifacts": 0, "coverage": 0.0}


def cmd_explain(source):
    """Explain compilation provenance."""
    try:
        compiler = Compiler()
        result = compiler.compile(source)

        if not result.success:
            return {"error": "Compilation failed", "details": result.errors}

        provenance = result.provenance
        records = provenance.records if hasattr(provenance, 'records') else []

        decisions = []
        for record in records[:50]:  # Limit to 50 records
            decisions.append({
                "type": record.source_type.value if hasattr(record.source_type, 'value') else str(record.source_type),
                "source": record.source_location,
                "confidence": record.confidence,
                "pattern": record.pattern_name,
                "template": record.template_name,
                "resolution_path": record.resolution_path,
                "generated_summary": record.generated_code[:200] if record.generated_code else "",
            })

        return {
            "decisions": decisions,
            "total_records": len(records),
        }
    except Exception as e:
        return {"error": str(e), "decisions": []}


def cmd_tree(source):
    """Get architecture tree."""
    try:
        parser = Parser(source)
        program = parser.parse()
        tree = ArchitectureTree(program)
        tree_str = tree.to_string() if hasattr(tree, 'to_string') else str(tree)

        return {
            "tree": tree_str,
        }
    except ParseError as e:
        return {"error": str(e), "tree": ""}
    except Exception as e:
        return {"error": str(e), "tree": ""}


def cmd_optimize(source):
    """Optimize architecture."""
    try:
        parser = Parser(source)
        program = parser.parse()
        optimizer = ArchitectureOptimizer(program)
        result = optimizer.optimize()

        actions = []
        for action in result.actions:
            actions.append({
                "type": action.strategy.value if hasattr(action.strategy, 'value') else str(action.strategy),
                "description": action.description,
                "risk": action.risk_level,
                "affected_elements": action.affected_elements,
                "before": action.before,
                "after": action.after,
            })

        return {
            "actions": actions,
            "improvement_score": result.improvement_score,
            "iterations": result.iterations,
        }
    except Exception as e:
        return {"error": str(e), "actions": [], "improvement_score": 0.0}


def cmd_exercises():
    """Return exercise list."""
    exercises = [
        {
            "id": 1,
            "title": "Hello World",
            "description": "Create a minimal AICL specification with a Goal, Layer, and Validation. This is the simplest possible AICL program.",
            "template": '''# Exercise 1: Hello World
# TODO: Add a Goal that describes what this program does

# TODO: Add a Layer named "Main"

# TODO: Add a Validation that checks the program works
''',
        },
        {
            "id": 2,
            "title": "Risk & Recovery",
            "description": "Add error handling to a specification using Risk and Recovery sections. Every Risk should have a corresponding Recovery.",
            "template": '''# Exercise 2: Risk & Recovery
Goal:
Create a file processor application

# TODO: Add a Constraint about maximum file size

# TODO: Add a Risk about file not found

# TODO: Add a Recovery for the file not found risk

# TODO: Add a Risk about permission denied

# TODO: Add a Recovery for the permission denied risk

Layer:
File Reader

Layer:
File Processor

Validation:
Files are processed correctly
''',
        },
        {
            "id": 3,
            "title": "Entities & Behaviors",
            "description": "Define data structures using Entity sections and operations using Behavior sections. Entities define the data, Behaviors define the actions.",
            "template": '''# Exercise 3: Entities & Behaviors
Goal:
Create a task management system

Constraint:
Maximum 1000 tasks per user

Layer:
Task Manager

Layer:
Storage

Validation:
Tasks can be created and completed

# TODO: Define an Entity named "Task" with fields:
#   title: string
#   completed: boolean
#   priority: integer

# TODO: Define an Entity named "User" with fields:
#   name: string
#   email: string
#   tasks: list

# TODO: Define a Behavior named "CreateTask"
#   Input: User, Task
#   Action: add task to user's task list

# TODO: Define a Behavior named "CompleteTask"
#   Input: Task
#   Action: mark task as completed
''',
        },
        {
            "id": 4,
            "title": "Conditions & Events",
            "description": "Add When/Then rules for conditional logic and Event/On handlers for reactive behavior. These make your specification dynamic.",
            "template": '''# Exercise 4: Conditions & Events
Goal:
Create a temperature monitoring system

Constraint:
Temperature readings must be validated

Risk:
Sensor malfunction

Recovery:
Use last known good reading

Layer:
Sensor Input

Layer:
Temperature Monitor

Layer:
Alert System

Entity Reading
    value: float
    timestamp: datetime
    sensor_id: integer

Entity Alert
    level: string
    message: string
    timestamp: datetime

Behavior ReadTemperature

Input:
    Reading

Action:
    Read and validate temperature from sensor

# TODO: Add a Condition:
#   When temperature exceeds threshold
#   Then trigger alert

# TODO: Add a Condition:
#   When sensor is offline for 5 minutes
#   Then notify administrator

# TODO: Add an Event:
#   On temperature alert
#   Action: send notification

# TODO: Add an Event:
#   On sensor reconnection
#   Action: resume normal monitoring

Validation:
Temperature readings are within expected range
''',
        },
        {
            "id": 5,
            "title": "Full Application",
            "description": "Build a complete chat application using all AICL features: Goals, Layers, Entities, Behaviors, Conditions, Events, Parallel execution, Security, and Optimization.",
            "template": '''# Exercise 5: Full Chat Application
# TODO: Add a Goal for a real-time chat application

# TODO: Add Constraints for:
#   - Maximum 200 concurrent users
#   - Messages under 10KB
#   - Latency under 500ms

# TODO: Add Risks and Recoveries for:
#   - Server unavailable
#   - Message delivery failure
#   - User disconnect

# TODO: Add Layers with Sublayers for:
#   - User Interface (message display, input, user list)
#   - Networking (websocket, serialization)
#   - Chat Logic (routing, user management)
#   - Persistence (history, preferences)

# TODO: Define Entities:
#   - User (name, id, status)
#   - Message (content, timestamp, sender)
#   - Channel (name, id, members)

# TODO: Define Behaviors:
#   - SendMessage (Input: User, Message; Output: DeliveredMessage)
#   - JoinChannel (Input: User, Channel)

# TODO: Add Conditions:
#   - When server unavailable, then enable offline mode
#   - When network restored, then sync messages

# TODO: Add Events:
#   - On message received, display in channel
#   - On user join, update user list

# TODO: Add Parallel execution for UI and Networking

# TODO: Add Optimize for latency

# TODO: Add Security with Encrypt and Protect

# TODO: Add Validations for core functionality
''',
        },
    ]

    return {"exercises": exercises}


def main():
    parser = argparse.ArgumentParser(description="AICL Helper")
    parser.add_argument("command", choices=["compile", "verify", "audit", "explain", "tree", "optimize", "exercises"])
    parser.add_argument("--target", default="python", choices=["python", "rust", "javascript", "go"])

    args = parser.parse_args()

    if args.command == "exercises":
        result = cmd_exercises()
    else:
        source = read_source()
        if args.command == "compile":
            result = cmd_compile(source, target=args.target)
        elif args.command == "verify":
            result = cmd_verify(source)
        elif args.command == "audit":
            result = cmd_audit(source)
        elif args.command == "explain":
            result = cmd_explain(source)
        elif args.command == "tree":
            result = cmd_tree(source)
        elif args.command == "optimize":
            result = cmd_optimize(source)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
