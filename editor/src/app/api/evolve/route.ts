import { NextRequest, NextResponse } from 'next/server';
import ZAI from 'z-ai-web-dev-sdk';
import { callAicl } from '@/lib/aicl-bridge';

/**
 * AICL Evolve API Endpoint
 *
 * Implements the Autonomous Compilation Loop from the README:
 * "a self-writing, self-validating loop where the compiler diagnoses
 *  its own failures, fixes its own specifications, learns new patterns,
 *  and iterates until convergence."
 *
 * Loop: SPEC → COMPILE → VERIFY → TEST → DIAGNOSE → FIX → RECOMPILE
 * Converges when: audit=100%, tests pass, verification passes, no fallbacks
 */

const EVOLVE_SYSTEM_PROMPT = `You are the AICL SpecEvolver, part of the Autonomous Compilation Loop.

Given an AICL specification and its error diagnosis, you must produce a FIXED version that addresses ALL errors.

Rules:
1. Output the ENTIRE fixed AICL code wrapped in :::AICL_FILE filename.aicl ... :::END_FILE
2. Fix ALL errors — do not partially fix
3. Preserve the user's original intent
4. The fixed code must be valid AICL (Goal, Layer, Validation at minimum)
5. Every Risk must have a paired Recovery
6. Every Behavior should have Input, Output, Action
7. Maintain the No-Orphan Property

AICL Keywords: Goal, Constraint, Risk, Recovery, Layer, Sublayer, Validation, Entity, Behavior, Input, Output, Action, Condition, When, Then, Event, On, Parallel, Optimize, Priority, Learn, Adapt, Based, Security, Encrypt, Protect, Native
Types: string, integer, float, boolean, datetime, list, dict, set, any, void, bytes`;

interface EvolveRequest {
  source: string;
  target?: string;
  maxIterations?: number;
}

interface EvolveIteration {
  iteration: number;
  compiled: boolean;
  verified: string;
  audit_coverage: number;
  errors: string[];
  fixed: boolean;
  fix_explanation?: string;
}

function runHelper(command: string, source: string, target?: string): any {
  const args = target && command === 'compile' ? ['--target', target] : [];
  return callAicl(command, args, source);
}

async function fixWithAI(source: string, filename: string, errors: string[]): Promise<{ code: string; explanation: string } | null> {
  try {
    const zai = await ZAI.create();
    const completion = await zai.chat.completions.create({
      messages: [
        { role: 'system', content: EVOLVE_SYSTEM_PROMPT },
        {
          role: 'user',
          content: `Fix this AICL specification.\n\nCurrent code:\n\`\`\`aicl\n${source}\n\`\`\`\n\nFilename: ${filename}\n\nErrors:\n${errors.map((e, i) => `${i + 1}. ${e}`).join('\n')}\n\nProduce the COMPLETE fixed AICL specification using the :::AICL_FILE protocol.`,
        },
      ],
      temperature: 0.3,
      max_tokens: 4096,
    });

    const message = completion.choices?.[0]?.message?.content || '';
    const fileMatch = message.match(/:::AICL_FILE\s+(\S+)\n([\s\S]*?):::END_FILE/);
    if (!fileMatch) return null;

    const explanation = message.split(':::AICL_FILE')[0].trim();
    return { code: fileMatch[2].trim(), explanation: explanation || 'Fixed by SpecEvolver' };
  } catch {
    return null;
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as EvolveRequest;
    const { source, target = 'python', maxIterations = 5 } = body;

    if (!source || typeof source !== 'string') {
      return NextResponse.json({ error: 'Source code is required' }, { status: 400 });
    }

    let currentSource = source;
    const iterations: EvolveIteration[] = [];
    let converged = false;
    let finalCode = '';
    let finalTestCode = '';
    let finalProof = false;
    let finalAuditCoverage = 0;

    for (let i = 0; i < maxIterations; i++) {
      const iter: EvolveIteration = {
        iteration: i + 1,
        compiled: false,
        verified: 'UNKNOWN',
        audit_coverage: 0,
        errors: [],
        fixed: false,
      };

      // Step 1: COMPILE
      const compileResult = runHelper('compile', currentSource, target);
      iter.compiled = compileResult.success;

      if (!compileResult.success) {
        iter.errors = compileResult.errors || ['Compilation failed'];

        // Step: DIAGNOSE + FIX
        const fix = await fixWithAI(currentSource, 'evolving.aicl', iter.errors);
        if (fix) {
          currentSource = fix.code;
          iter.fixed = true;
          iter.fix_explanation = fix.explanation;
        } else {
          iter.fixed = false;
          iter.fix_explanation = 'AI fix unavailable — cannot continue evolution';
          iterations.push(iter);
          break;
        }

        iterations.push(iter);
        continue;
      }

      // Compilation succeeded — store results
      finalCode = compileResult.main_code || '';
      finalTestCode = compileResult.test_code || '';
      finalProof = compileResult.proof_valid || false;
      finalAuditCoverage = compileResult.audit_coverage || 0;

      // Step 2: VERIFY
      const verifyResult = runHelper('verify', currentSource);
      iter.verified = verifyResult.overall || 'UNKNOWN';

      // Step 3: AUDIT (from compile result)
      iter.audit_coverage = finalAuditCoverage;

      // Collect remaining issues
      const remainingErrors: string[] = [];
      if (verifyResult.overall !== 'PASS') {
        (verifyResult.checks || []).forEach((c: { status: string; name: string; message: string }) => {
          if (c.status === 'FAIL') {
            remainingErrors.push(`VERIFY FAIL — ${c.name}: ${c.message}`);
          }
        });
      }
      if (finalAuditCoverage < 1.0) {
        remainingErrors.push(`AUDIT — Coverage ${(finalAuditCoverage * 100).toFixed(0)}% (target: 100%)`);
      }
      if (compileResult.warnings?.length) {
        compileResult.warnings.forEach((w: string) => remainingErrors.push(`WARNING — ${w}`));
      }

      iter.errors = remainingErrors;

      // Check convergence: all pass, 100% audit, no errors
      if (verifyResult.overall === 'PASS' && finalAuditCoverage >= 1.0 && remainingErrors.length === 0) {
        converged = true;
        iterations.push(iter);
        break;
      }

      // Step: FIX remaining issues with AI
      if (remainingErrors.length > 0 && i < maxIterations - 1) {
        const fix = await fixWithAI(currentSource, 'evolving.aicl', remainingErrors);
        if (fix) {
          currentSource = fix.code;
          iter.fixed = true;
          iter.fix_explanation = fix.explanation;
        } else {
          iter.fixed = false;
        }
      }

      iterations.push(iter);
    }

    // If we didn't converge but have a compiled version, do one final compile
    if (!converged && finalCode) {
      // Already have compiled results
    } else if (!converged) {
      // Try one last compile
      const lastResult = runHelper('compile', currentSource, target);
      if (lastResult.success) {
        finalCode = lastResult.main_code || '';
        finalTestCode = lastResult.test_code || '';
        finalProof = lastResult.proof_valid || false;
        finalAuditCoverage = lastResult.audit_coverage || 0;
      }
    }

    return NextResponse.json({
      converged,
      iterations,
      total_iterations: iterations.length,
      evolved_source: currentSource,
      main_code: finalCode,
      test_code: finalTestCode,
      proof_valid: finalProof,
      audit_coverage: finalAuditCoverage,
      source_changed: currentSource !== source,
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Evolve failed';
    return NextResponse.json({
      converged: false,
      error: errorMessage,
      iterations: [],
      total_iterations: 0,
    }, { status: 500 });
  }
}
