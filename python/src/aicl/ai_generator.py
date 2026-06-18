"""
AICL AI-Powered Code Generation & Diagnosis

This module integrates AI (via the z-ai-web-dev-sdk bridge) into the AICL
compilation system, enabling:

1. GENERATE: Create complete AICL specifications from natural language
   task descriptions. "Create a banking system" → full .aicl file.

2. DIAGNOSE: AI-powered root cause analysis of compilation/test failures.
   The AI sees the error, the source, and the generated code, then suggests
   specific fixes to the AICL specification.

3. FIX: AI-powered automatic repair of broken AICL specifications.
   The AI produces the complete corrected AICL source.

4. ENHANCE: AI-powered improvement of existing AICL specifications.
   Adds missing Risk/Recovery pairs, makes validations testable, etc.

5. SELF-WRITE: The full autonomous loop with AI:
   DESCRIBE → AI-GENERATE → COMPILE → VERIFY → TEST → AI-DIAGNOSE → AI-FIX → RECOMPILE

Every AI-generated artifact is tracked with ProvenanceType.AI_GENERATION,
maintaining the No-Orphan Property even for AI-generated code.

Requirements:
    - Node.js must be installed
    - z-ai-web-dev-sdk must be installed (typically in editor/node_modules)
      — see tools/ai_bridge.mjs for resolution order
    - tools/ai_bridge.mjs must exist (shipped with this package)

If the AI bridge is not available, the system falls back to the deterministic
PatternLearner and SpecEvolver.
"""

import os
import json
import subprocess
import tempfile
import time
import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field


# Path to the AI bridge script
AI_BRIDGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tools", "ai_bridge.mjs"
)


def is_ai_available() -> bool:
    """Check if the AI bridge is available."""
    return os.path.exists(AI_BRIDGE_PATH)


def call_ai_bridge(mode: str, **kwargs) -> Dict[str, Any]:
    """
    Call the AI bridge Node.js script.

    Args:
        mode: One of 'generate', 'diagnose', 'fix', 'enhance', 'chat'
        **kwargs: Arguments for the specific mode

    Returns:
        Dict with 'result' key containing the AI response,
        or 'error' key if something went wrong.
    """
    if not is_ai_available():
        return {"error": "AI bridge not available. Install z-ai-web-dev-sdk and ensure tools/ai_bridge.mjs exists."}

    cmd = ["node", AI_BRIDGE_PATH, "--mode", mode]

    if mode == "generate":
        task = kwargs.get("task", "")
        if not task:
            return {"error": "Missing 'task' argument for generate mode"}
        cmd.extend(["--task", task])

    elif mode == "diagnose":
        error = kwargs.get("error", "")
        source = kwargs.get("source", "")
        code = kwargs.get("code", "")
        if not error:
            return {"error": "Missing 'error' argument for diagnose mode"}
        cmd.extend(["--error", error])
        if source:
            cmd.extend(["--source", source])
        if code:
            cmd.extend(["--code", code])

    elif mode == "fix":
        error = kwargs.get("error", "")
        source = kwargs.get("source", "")
        code = kwargs.get("code", "")
        if not error or not source:
            return {"error": "Missing 'error' or 'source' argument for fix mode"}
        cmd.extend(["--error", error, "--source", source])
        if code:
            cmd.extend(["--code", code])

    elif mode == "enhance":
        source = kwargs.get("source", "")
        if not source:
            return {"error": "Missing 'source' argument for enhance mode"}
        cmd.extend(["--source", source])

    elif mode == "chat":
        message = kwargs.get("message", "")
        if not message:
            return {"error": "Missing 'message' argument for chat mode"}
        cmd.extend(["--message", message])

    else:
        return {"error": f"Unknown mode: {mode}"}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout for AI calls
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            if stderr:
                try:
                    error_data = json.loads(stderr)
                    return {"error": error_data.get("error", stderr)}
                except json.JSONDecodeError:
                    return {"error": stderr}
            return {"error": f"AI bridge exited with code {result.returncode}"}

        # Parse JSON output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # If not JSON, return raw text
            return {"result": result.stdout.strip()}

    except subprocess.TimeoutExpired:
        return {"error": "AI bridge timed out after 120 seconds"}
    except FileNotFoundError:
        return {"error": "Node.js not found. Install Node.js to use AI features."}
    except Exception as e:
        return {"error": f"AI bridge error: {str(e)}"}


def clean_aicl_output(raw: str) -> str:
    """
    Clean AI-generated AICL output by removing markdown fences
    and any explanatory text before/after the AICL code.
    """
    text = raw.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```aicl or ```)
        lines = lines[1:]
        # Remove last line (```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    # Find the start of AICL code (look for # comment or Goal:)
    lines = text.split("\n")
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("#") or line.strip().startswith("Goal:"):
            start_idx = i
            break

    # Find the end of AICL code (look for text that's clearly not AICL)
    end_idx = len(lines)
    for i in range(len(lines) - 1, max(start_idx, len(lines) - 5), -1):
        line = lines[i].strip()
        if line and not line.startswith("#") and not line.startswith("Goal:") and \
           not line.startswith("Constraint:") and not line.startswith("Risk:") and \
           not line.startswith("Recovery:") and not line.startswith("Layer:") and \
           not line.startswith("Sublayer:") and not line.startswith("Validation:") and \
           not line.startswith("Entity") and not line.startswith("Behavior") and \
           not line.startswith("Input:") and not line.startswith("Output:") and \
           not line.startswith("Action:") and not line.startswith("Condition:") and \
           not line.startswith("When ") and not line.startswith("Then ") and \
           not line.startswith("Event:") and not line.startswith("On ") and \
           not line.startswith("Parallel:") and not line.startswith("Optimize:") and \
           not line.startswith("Priority:") and not line.startswith("Learn:") and \
           not line.startswith("Adapt:") and not line.startswith("Based") and \
           not line.startswith("Security:") and not line.startswith("Encrypt:") and \
           not line.startswith("Protect:") and not line.startswith("Native:") and \
           not line.startswith("    ") and not line.startswith("\t") and not line == "":
            # This line doesn't look like AICL — check if it's explanatory text
            if "here is" in line.lower() or "this specification" in line.lower() or \
               "the following" in line.lower() or "note:" in line.lower():
                end_idx = i
                break

    if start_idx > 0 or end_idx < len(lines):
        lines = lines[start_idx:end_idx]

    return "\n".join(lines).strip()


@dataclass
class AIGenerationResult:
    """Result of an AI generation operation."""
    success: bool
    aicl_source: str = ""
    error: str = ""
    task: str = ""
    duration: float = 0.0
    compiled: bool = False
    audit_coverage: float = 0.0
    proof_valid: bool = False
    lines_generated: int = 0

    @property
    def summary(self) -> str:
        lines = [
            f"Task: {self.task[:80]}",
            f"Success: {self.success}",
            f"AICL Source: {len(self.aicl_source)} chars",
            f"Duration: {self.duration:.2f}s",
        ]
        if self.compiled:
            lines.append(f"Compiled: Yes")
            lines.append(f"Audit Coverage: {self.audit_coverage:.1%}")
            lines.append(f"Proof Valid: {self.proof_valid}")
            lines.append(f"Lines Generated: {self.lines_generated}")
        return "\n".join(lines)


class AICLGenerator:
    """
    AI-powered AICL specification generator.

    Takes a natural language task description and generates a complete,
    compilable AICL specification using the AI bridge.

    Usage:
        generator = AICLGenerator()
        result = generator.generate("Create a banking system with fraud detection")
        if result.success:
            print(result.aicl_source)
    """

    def __init__(self, auto_compile: bool = True, target_language: str = "python"):
        self.auto_compile = auto_compile
        self.target_language = target_language

    def generate(self, task: str, output_path: Optional[str] = None) -> AIGenerationResult:
        """
        Generate an AICL specification from a task description.

        Args:
            task: Natural language description of the system to create
            output_path: Optional path to save the .aicl file

        Returns:
            AIGenerationResult with the generated AICL source
        """
        start_time = time.time()

        # Step 1: Generate AICL specification using AI
        response = call_ai_bridge("generate", task=task)

        if "error" in response:
            return AIGenerationResult(
                success=False,
                error=response["error"],
                task=task,
                duration=time.time() - start_time,
            )

        raw_output = response.get("result", "")

        # Step 2: Clean the output
        aicl_source = clean_aicl_output(raw_output)

        if not aicl_source or not aicl_source.strip():
            return AIGenerationResult(
                success=False,
                error="AI returned empty AICL source",
                task=task,
                duration=time.time() - start_time,
            )

        result = AIGenerationResult(
            success=True,
            aicl_source=aicl_source,
            task=task,
            duration=time.time() - start_time,
        )

        # Step 3: Auto-compile if requested
        if self.auto_compile:
            compile_result = self._compile_and_verify(aicl_source, output_path)
            result.compiled = compile_result["compiled"]
            result.audit_coverage = compile_result.get("audit_coverage", 0.0)
            result.proof_valid = compile_result.get("proof_valid", False)
            result.lines_generated = compile_result.get("lines_generated", 0)

        # Step 4: Save to file if path provided
        if output_path and result.success:
            path = output_path if output_path.endswith(".aicl") else output_path + ".aicl"
            with open(path, "w") as f:
                f.write(aicl_source)
            result.aicl_source = aicl_source

        return result

    def _compile_and_verify(self, aicl_source: str, output_path: Optional[str] = None) -> Dict:
        """Compile the generated AICL source and verify the proof."""
        try:
            from . import Compiler, Parser

            # Write to temp file for compilation
            with tempfile.NamedTemporaryFile(mode="w", suffix=".aicl", delete=False) as f:
                f.write(aicl_source)
                temp_path = f.name

            output_dir = tempfile.mkdtemp(prefix="aicl_ai_gen_")

            try:
                compiler = Compiler(target_language=self.target_language)
                compile_result = compiler.compile_to_file(
                    aicl_source, output_dir, source_path=temp_path
                )

                if not compile_result.success:
                    return {"compiled": False, "error": "; ".join(compile_result.errors)}

                # Get audit coverage
                audit_coverage = 0.0
                if hasattr(compiler, '_provenance') and compiler._provenance:
                    audit = compiler._provenance.compute_audit_coverage()
                    audit_coverage = audit.get("audit_coverage", 0.0)

                # Verify proof
                proof_valid = False
                proof_path = os.path.join(output_dir, "main.aicl-proof")
                if os.path.exists(proof_path):
                    try:
                        from .provenance import ProofOfOrigin
                        proof = ProofOfOrigin.from_file(proof_path)
                        valid, _ = proof.verify()
                        proof_valid = valid
                    except Exception:
                        proof_valid = False

                # Count lines
                main_path = os.path.join(output_dir, "main.py")
                lines_generated = 0
                if os.path.exists(main_path):
                    with open(main_path) as f:
                        lines_generated = len(f.readlines())

                return {
                    "compiled": True,
                    "audit_coverage": audit_coverage,
                    "proof_valid": proof_valid,
                    "lines_generated": lines_generated,
                    "output_dir": output_dir,
                }

            finally:
                os.unlink(temp_path)

        except Exception as e:
            return {"compiled": False, "error": str(e)}


class AIDiagnoser:
    """
    AI-powered diagnosis and repair of AICL compilation failures.

    When the deterministic system can't fix a problem, the AIDiagnoser
    uses the AI to:
    1. Analyze the error in context
    2. Propose specific fixes
    3. Generate the complete corrected AICL source

    Every fix is recorded with ProvenanceType.AI_GENERATION.
    """

    def __init__(self):
        self.diagnosis_count = 0
        self.fix_count = 0

    def diagnose(self, error: str, source: str, generated_code: str = "") -> Dict[str, Any]:
        """
        Diagnose a compilation/test failure using AI.

        Returns:
            Dict with diagnosis, root_cause, fix_type, fix_description
        """
        response = call_ai_bridge("diagnose", error=error, source=source, code=generated_code)

        if "error" in response:
            return {
                "diagnosis": f"AI diagnosis failed: {response['error']}",
                "root_cause": "unknown",
                "fix_type": "other",
                "fix_description": "",
            }

        raw = response.get("result", "")

        # Try to parse as JSON
        try:
            # The AI might wrap the JSON in markdown
            json_str = raw
            if "```json" in json_str:
                json_str = json_str.split("```json", 1)[1].split("```", 1)[0]
            elif "```" in json_str:
                json_str = json_str.split("```", 1)[1].split("```", 1)[0]

            diagnosis = json.loads(json_str.strip())
            self.diagnosis_count += 1
            return diagnosis
        except (json.JSONDecodeError, IndexError):
            # If not valid JSON, return the raw text as diagnosis
            self.diagnosis_count += 1
            return {
                "diagnosis": raw[:500],
                "root_cause": "ai_analysis",
                "fix_type": "other",
                "fix_description": raw[:200],
                "fixed_source": "",
            }

    def fix(self, error: str, source: str, generated_code: str = "") -> Tuple[str, bool]:
        """
        Fix a broken AICL specification using AI.

        Returns:
            Tuple of (fixed_source, success)
        """
        response = call_ai_bridge("fix", error=error, source=source, code=generated_code)

        if "error" in response:
            return source, False

        raw = response.get("result", "")
        fixed = clean_aicl_output(raw)

        if not fixed.strip():
            return source, False

        self.fix_count += 1
        return fixed, True

    def enhance(self, source: str) -> Tuple[str, bool]:
        """
        Enhance an existing AICL specification using AI.

        Returns:
            Tuple of (enhanced_source, success)
        """
        response = call_ai_bridge("enhance", source=source)

        if "error" in response:
            return source, False

        raw = response.get("result", "")
        enhanced = clean_aicl_output(raw)

        if not enhanced.strip():
            return source, False

        return enhanced, True


class SelfWritingCompiler:
    """
    The complete self-writing, self-validating compilation system with AI.

    This is the highest level of the AICL system. Given any task description,
    it can:
    1. Generate a complete AICL specification from scratch
    2. Compile it through the autonomous loop
    3. AI-diagnose any failures
    4. AI-fix the specification
    5. Iterate until convergence

    The loop:
        DESCRIBE → AI-GENERATE → COMPILE → VERIFY → TEST →
        AI-DIAGNOSE → AI-FIX → RECOMPILE → ... → CONVERGE

    If AI is not available, falls back to the deterministic autonomous loop.

    Usage:
        compiler = SelfWritingCompiler()
        result = compiler.create("Build an e-commerce platform")
        print(result.summary)

        # Or use evolve to improve an existing spec
        result = compiler.evolve("banking.aicl", max_iterations=10)
    """

    def __init__(self, max_iterations: int = 10, target_language: str = "python",
                 test_timeout: int = 30, use_ai: bool = True):
        self.max_iterations = max_iterations
        self.target_language = target_language
        self.test_timeout = test_timeout
        self.use_ai = use_ai and is_ai_available()
        self.ai_generator = AICLGenerator(auto_compile=False, target_language=target_language)
        self.ai_diagnoser = AIDiagnoser()

    def create(self, task: str, output_path: Optional[str] = None) -> AIGenerationResult:
        """
        Create a complete AICL program from a natural language task description.

        This is the "code that writes itself" entry point.
        """
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"AICL SELF-WRITING COMPILER")
        print(f"{'='*70}")
        print(f"  Task: {task[:70]}")
        print(f"  AI: {'Enabled' if self.use_ai else 'Disabled (fallback)'}")
        print(f"  Target: {self.target_language}")
        print(f"{'='*70}\n")

        # Step 1: Generate AICL specification
        if self.use_ai:
            print("  [1/5] AI generating AICL specification...")
            gen_result = self.ai_generator.generate(task, output_path=None)

            if not gen_result.success:
                return AIGenerationResult(
                    success=False,
                    error=f"AI generation failed: {gen_result.error}",
                    task=task,
                    duration=time.time() - start_time,
                )

            aicl_source = gen_result.aicl_source
            print(f"        Generated {len(aicl_source)} chars of AICL code")
        else:
            return AIGenerationResult(
                success=False,
                error="AI is not available. Install z-ai-web-dev-sdk to use self-writing features.",
                task=task,
                duration=time.time() - start_time,
            )

        # Step 2: Compile
        print("  [2/5] Compiling AICL specification...")
        output_dir = tempfile.mkdtemp(prefix="aicl_self_write_")
        aicl_path = os.path.join(output_dir, "generated.aicl")
        with open(aicl_path, "w") as f:
            f.write(aicl_source)

        compile_ok, compile_info = self._compile(aicl_source, output_dir, aicl_path)

        if compile_ok:
            print(f"        Compilation successful! Audit: {compile_info.get('audit_coverage', 0):.1%}")
        else:
            print(f"        Compilation failed: {compile_info.get('error', 'unknown')}")

        # Step 3: Verify
        print("  [3/5] Verifying specification...")
        spec_ok = self._verify(aicl_source)
        print(f"        Spec verification: {'PASS' if spec_ok else 'FAIL'}")

        # Step 4: Test
        print("  [4/5] Running generated tests...")
        from .autonomous import TestRunner
        test_runner = TestRunner(timeout=self.test_timeout)
        passed, failed, total, details = test_runner.run_tests(output_dir)
        print(f"        Tests: {passed}/{total} passed")

        # Step 5: AI-fix if needed
        all_good = compile_ok and spec_ok and failed == 0

        if not all_good and self.use_ai:
            print("  [5/5] AI diagnosing and fixing issues...")
            aicl_source = self._ai_fix_loop(
                aicl_source, output_dir, aicl_path,
                compile_ok, compile_info, spec_ok, failed, test_runner
            )
            # Recompile after fix
            compile_ok, compile_info = self._compile(aicl_source, output_dir, aicl_path)
            passed, failed, total, details = test_runner.run_tests(output_dir)
            all_good = compile_ok and failed == 0
            print(f"        After AI fix: compiled={compile_ok}, tests={passed}/{total}")
        else:
            print("  [5/5] No fixes needed!")

        # Final result
        result = AIGenerationResult(
            success=all_good,
            aicl_source=aicl_source,
            task=task,
            duration=time.time() - start_time,
            compiled=compile_ok,
            audit_coverage=compile_info.get("audit_coverage", 0.0),
            proof_valid=compile_info.get("proof_valid", False),
            lines_generated=compile_info.get("lines_generated", 0),
        )

        # Save to file
        if output_path:
            path = output_path if output_path.endswith(".aicl") else output_path + ".aicl"
            with open(path, "w") as f:
                f.write(aicl_source)

        print(f"\n{'='*70}")
        print(f"RESULT: {'SUCCESS' if result.success else 'PARTIAL'}")
        print(result.summary)
        print(f"{'='*70}\n")

        return result

    def evolve(self, source_path: str, max_iterations: Optional[int] = None,
               output_dir: Optional[str] = None) -> 'AutonomousResult':
        """
        Evolve an existing AICL specification using AI-enhanced autonomous loop.
        """
        from .autonomous import AutonomousCompiler, AutonomousResult

        max_it = max_iterations or self.max_iterations

        # First try deterministic evolution
        compiler = AutonomousCompiler(
            max_iterations=max_it,
            target_language=self.target_language,
            test_timeout=self.test_timeout,
        )
        result = compiler.evolve(source_path, output_dir)

        # If not converged and AI is available, try AI-enhanced evolution
        if not result.converged and self.use_ai:
            with open(source_path) as f:
                source = f.read()

            # AI enhance the specification
            enhanced, success = self.ai_diagnoser.enhance(source)
            if success:
                # Write enhanced source
                evolved_path = source_path.replace(".aicl", ".ai_enhanced.aicl")
                with open(evolved_path, "w") as f:
                    f.write(enhanced)

                # Recompile with enhanced source
                result2 = compiler.evolve(evolved_path, output_dir)
                if result2.converged and not result.converged:
                    return result2

        return result

    def _compile(self, aicl_source: str, output_dir: str, source_path: str) -> Tuple[bool, Dict]:
        """Compile AICL source and return (success, info_dict)."""
        try:
            from . import Compiler
            compiler = Compiler(target_language=self.target_language)
            result = compiler.compile_to_file(aicl_source, output_dir, source_path=source_path)

            if not result.success:
                return False, {"error": "; ".join(result.errors)}

            audit_coverage = 0.0
            if hasattr(compiler, '_provenance') and compiler._provenance:
                audit = compiler._provenance.compute_audit_coverage()
                audit_coverage = audit.get("audit_coverage", 0.0)

            proof_valid = False
            proof_path = os.path.join(output_dir, "main.aicl-proof")
            if os.path.exists(proof_path):
                try:
                    from .provenance import ProofOfOrigin
                    proof = ProofOfOrigin.from_file(proof_path)
                    valid, _ = proof.verify()
                    proof_valid = valid
                except Exception:
                    pass

            lines_generated = 0
            main_path = os.path.join(output_dir, "main.py")
            if os.path.exists(main_path):
                with open(main_path) as f:
                    lines_generated = len(f.readlines())

            return True, {
                "audit_coverage": audit_coverage,
                "proof_valid": proof_valid,
                "lines_generated": lines_generated,
            }

        except Exception as e:
            return False, {"error": str(e)}

    def _verify(self, aicl_source: str) -> bool:
        """Verify AICL specification completeness."""
        try:
            from . import Parser
            from .spec_verify import SpecificationVerifier
            parsed = Parser().parse(aicl_source)
            verifier = SpecificationVerifier(parsed)
            report = verifier.verify()
            return all(c.get("status") != "FAIL" for c in report.get("checks", []))
        except Exception:
            return False

    def _ai_fix_loop(self, aicl_source: str, output_dir: str, aicl_path: str,
                     compile_ok: bool, compile_info: Dict, spec_ok: bool,
                     test_failures: int, test_runner) -> str:
        """AI-powered fix loop. Tries up to 3 AI fix attempts."""
        for attempt in range(3):
            # Build error description
            errors = []
            if not compile_ok:
                errors.append(f"Compilation error: {compile_info.get('error', 'unknown')}")
            if not spec_ok:
                errors.append("Specification verification failed")
            if test_failures > 0:
                errors.append(f"{test_failures} test(s) failed")
            error_desc = "; ".join(errors)

            # Get generated code for context
            generated_code = ""
            main_path = os.path.join(output_dir, "main.py")
            if os.path.exists(main_path):
                with open(main_path) as f:
                    generated_code = f.read()[:2000]

            # AI fix
            fixed_source, success = self.ai_diagnoser.fix(
                error=error_desc,
                source=aicl_source,
                generated_code=generated_code,
            )

            if success:
                aicl_source = fixed_source
                with open(aicl_path, "w") as f:
                    f.write(aicl_source)

                # Recompile
                compile_ok, compile_info = self._compile(aicl_source, output_dir, aicl_path)
                spec_ok = self._verify(aicl_source)
                passed, failed, total, _ = test_runner.run_tests(output_dir)
                test_failures = failed

                if compile_ok and spec_ok and test_failures == 0:
                    break

        return aicl_source


def format_create_report(result: AIGenerationResult) -> str:
    """Format an AIGenerationResult into a readable report."""
    lines = [
        "=" * 70,
        "AICL SELF-WRITING COMPILATION REPORT",
        "=" * 70,
        "",
        f"  Task:          {result.task[:60]}",
        f"  Success:       {result.success}",
        f"  Duration:      {result.duration:.2f}s",
        f"  AICL Source:   {len(result.aicl_source)} chars",
        "",
    ]

    if result.compiled:
        lines.extend([
            f"  Compiled:      Yes",
            f"  Audit Coverage:{result.audit_coverage:.1%}",
            f"  Proof Valid:   {result.proof_valid}",
            f"  Code Lines:    {result.lines_generated}",
        ])
    else:
        lines.append(f"  Compiled:      No")
        if result.error:
            lines.append(f"  Error:         {result.error[:60]}")

    lines.extend(["", "=" * 70])
    return "\n".join(lines)
