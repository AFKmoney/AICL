import { NextRequest, NextResponse } from 'next/server';
import ZAI from 'z-ai-web-dev-sdk';

/**
 * AICL Fix-Spec API Endpoint
 *
 * Implements the SpecEvolver concept from the README:
 * "Fixes verification failures, test failures, and audit gaps automatically"
 *
 * This endpoint:
 * 1. Takes the current AICL source + errors (from compile/verify/audit)
 * 2. Sends them to the AI with instructions to produce corrected AICL code
 * 3. Returns the fixed AICL code that can replace the editor content
 */

const FIX_SYSTEM_PROMPT = `You are the AICL SpecEvolver — an autonomous specification repair agent.

Your job is to FIX AICL specifications that have errors. You receive the current AICL code and a list of errors/failures, and you must output the CORRECTED AICL code.

## RULES (CRITICAL — FOLLOW EXACTLY):

1. You MUST output the ENTIRE corrected AICL file wrapped in the :::AICL_FILE protocol:
   :::AICL_FILE filename.aicl
   (full corrected AICL code here)
   :::END_FILE

2. The filename should be the same as the original if known, otherwise use "fixed.aicl"

3. You MUST fix ALL the errors listed. Do not partially fix — address every single error.

4. Your output AICL code must be COMPLETE and VALID — it must have at minimum: Goal, Layer, Validation

5. PRESERVE the user's original intent. Do not rewrite their specification from scratch unless it's fundamentally broken. Fix only what's wrong.

6. Common fixes you should apply:
   - Missing Goal → Add Goal section matching user's intent
   - Missing Layer → Add Layer section
   - Missing Validation → Add Validation section
   - Missing Risk/Recovery pairs → Add Recovery for each Risk (and vice versa)
   - Syntax errors → Fix capitalization, indentation, colons
   - Unknown keywords → Replace with valid AICL keyword
   - Incomplete Entity → Add missing field types
   - Incomplete Behavior → Add Input/Output/Action sections
   - Missing Condition → Add When/Then pairs
   - Missing Event → Add On/Action pairs
   - Orphan artifacts → Add more specific specification elements

7. After fixing, briefly explain WHAT you fixed and WHY (before the :::AICL_FILE block)

8. Do NOT remove features that are working — only add or fix what's broken

9. Maintain the No-Orphan Property: every generated artifact should trace back to source spec

## AICL REFERENCE:

27 Reserved Keywords: Goal, Constraint, Risk, Recovery, Layer, Sublayer, Validation, Entity, Behavior, Input, Output, Action, Condition, When, Then, Event, On, Parallel, Optimize, Priority, Learn, Adapt, Based, Security, Encrypt, Protect, Native

Types: string, integer, float, boolean, datetime, list, dict, set, any, void, bytes

Minimal valid program:
Goal:
Hello World

Layer:
Core

Validation:
Output is produced`;

interface FixRequest {
  source: string;
  filename?: string;
  errors?: string[];
  verifyResult?: { overall: string; checks: { name: string; status: string; message: string }[] };
  compileErrors?: string[];
  auditResult?: { coverage: number; orphan_count: number; orphan_names: string[] };
  operation?: string;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as FixRequest;
    const { source, filename, errors, verifyResult, compileErrors, auditResult, operation } = body;

    if (!source || typeof source !== 'string') {
      return NextResponse.json({ error: 'Source code is required' }, { status: 400 });
    }

    // Build error context
    const errorParts: string[] = [];

    if (compileErrors && compileErrors.length > 0) {
      errorParts.push('## Compilation Errors:');
      compileErrors.forEach((e, i) => errorParts.push(`${i + 1}. ${e}`));
    }

    if (verifyResult && verifyResult.overall !== 'PASS') {
      errorParts.push('## Verification Result: ' + verifyResult.overall);
      if (verifyResult.checks) {
        verifyResult.checks.forEach(c => {
          if (c.status === 'FAIL' || c.status === 'WARN') {
            errorParts.push(`- [${c.status}] ${c.name}: ${c.message}`);
          }
        });
      }
    }

    if (auditResult && auditResult.coverage < 1.0) {
      errorParts.push(`## Audit Issues:`);
      errorParts.push(`- Coverage: ${(auditResult.coverage * 100).toFixed(1)}% (target: 100%)`);
      errorParts.push(`- Orphan artifacts: ${auditResult.orphan_count}`);
      if (auditResult.orphan_names && auditResult.orphan_names.length > 0) {
        errorParts.push(`- Orphan names: ${auditResult.orphan_names.join(', ')}`);
      }
    }

    if (errors && errors.length > 0) {
      errorParts.push('## Errors:');
      errors.forEach((e, i) => errorParts.push(`${i + 1}. ${e}`));
    }

    if (errorParts.length === 0) {
      return NextResponse.json({
        fixed: false,
        message: 'No errors to fix. The specification appears to be valid.',
      });
    }

    const errorContext = errorParts.join('\n');

    // Call AI to fix the specification
    const zai = await ZAI.create();

    const completion = await zai.chat.completions.create({
      messages: [
        { role: 'system', content: FIX_SYSTEM_PROMPT },
        {
          role: 'user',
          content: `Fix this AICL specification. Here is the current code:\n\n\`\`\`aicl\n${source}\n\`\`\`\n\nFilename: ${filename || 'untitled.aicl'}\n\n${errorContext}\n\nProduce the COMPLETE fixed AICL specification using the :::AICL_FILE protocol.`,
        },
      ],
      temperature: 0.3,
      max_tokens: 4096,
    });

    const assistantMessage = completion.choices?.[0]?.message?.content || '';

    // Parse the :::AICL_FILE block from the response
    const fileMatch = assistantMessage.match(/:::AICL_FILE\s+(\S+)\n([\s\S]*?):::END_FILE/);
    if (!fileMatch) {
      return NextResponse.json({
        fixed: false,
        message: assistantMessage,
        explanation: 'The AI could not produce a valid fix. See the message for details.',
      });
    }

    const fixedFilename = fileMatch[1];
    const fixedCode = fileMatch[2].trim();

    // Extract explanation (text before the :::AICL_FILE block)
    const explanation = assistantMessage.split(':::AICL_FILE')[0].trim();

    return NextResponse.json({
      fixed: true,
      filename: fixedFilename,
      code: fixedCode,
      explanation: explanation || `Fixed ${errorParts.length} issue(s) in the AICL specification.`,
      original_source: source,
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Fix request failed';
    return NextResponse.json({
      fixed: false,
      error: errorMessage,
      message: 'The auto-fix service is currently unavailable. Try using the AI Chat to get help with your errors.',
    }, { status: 500 });
  }
}
