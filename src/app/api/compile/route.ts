import { NextRequest, NextResponse } from 'next/server';
import { execFileSync } from 'child_process';
import path from 'path';

const HELPER_PATH = path.join(process.cwd(), 'scripts', 'aicl_helper.py');
const PYTHON_PATH = '/usr/bin/python3.13';

/**
 * Add helpful suggestions to raw error messages from the AICL compiler.
 */
function enhanceErrors(errors: string[]): string[] {
  return errors.map(err => {
    const lower = err.toLowerCase();

    if (lower.includes('missing') && lower.includes('goal')) {
      return `${err}\n  → Fix: Add a "Goal:" section at the top of your AICL file with the system objective.`;
    }
    if (lower.includes('missing') && lower.includes('layer')) {
      return `${err}\n  → Fix: Add a "Layer:" section defining the main architectural layer.`;
    }
    if (lower.includes('missing') && lower.includes('validation')) {
      return `${err}\n  → Fix: Add a "Validation:" section defining the success criterion.`;
    }
    if (lower.includes('syntax') || lower.includes('parse')) {
      return `${err}\n  → Fix: Check that AICL keywords are capitalized correctly (Goal, Layer, Entity, etc.) and followed by a colon.`;
    }
    if (lower.includes('indent') || lower.includes('whitespace')) {
      return `${err}\n  → Fix: AICL uses consistent indentation (4 spaces) for nested content under keywords.`;
    }
    if (lower.includes('unknown keyword') || lower.includes('unrecognized')) {
      return `${err}\n  → Fix: AICL has 27 reserved keywords. Check spelling — keywords are case-sensitive (Goal, not goal).`;
    }
    if (lower.includes('risk') && lower.includes('recovery')) {
      return `${err}\n  → Fix: Every Risk must have a paired Recovery. Add a Recovery section after each Risk.`;
    }
    if (lower.includes('orphan')) {
      return `${err}\n  → Fix: The No-Orphan Property requires every generated artifact to trace back to source spec. Add more specific Entity/Behavior sections.`;
    }
    if (lower.includes('type') || lower.includes('invalid type')) {
      return `${err}\n  → Fix: AICL types are: string, integer, float, boolean, datetime, list, dict, set, any, void, bytes.`;
    }
    if (lower.includes('timeout') || lower.includes('timed out')) {
      return `${err}\n  → Fix: The compilation timed out. Try simplifying your specification or reducing the number of layers.`;
    }
    // No specific match — return as-is with generic help
    return `${err}\n  → Tip: Use the Verify button first to check your specification before compiling.`;
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { source, target = 'python' } = body;

    if (!source || typeof source !== 'string') {
      return NextResponse.json({
        success: false,
        errors: ['Source code is required. Please write some AICL code before compiling.'],
      }, { status: 400 });
    }

    if (source.trim().length < 10) {
      return NextResponse.json({
        success: false,
        errors: [
          'AICL code is too short to compile. A valid AICL specification needs at minimum: Goal, Layer, and Validation sections.',
          'Example minimal program:\n\nGoal:\nHello World\n\nLayer:\nCore\n\nValidation:\nOutput is produced',
        ],
      }, { status: 400 });
    }

    const result = execFileSync(PYTHON_PATH, [HELPER_PATH, 'compile', '--target', target], {
      input: source,
      timeout: 30000,
      maxBuffer: 5 * 1024 * 1024,
      encoding: 'utf-8',
    });

    const data = JSON.parse(result);
    return NextResponse.json(data);
  } catch (error: unknown) {
    let rawMessage = error instanceof Error ? error.message : 'Compilation failed';

    // Try to extract the actual Python error from the stderr
    const stderrMatch = rawMessage.match(/Command failed.*?\n([\s\S]*)/);
    if (stderrMatch) {
      rawMessage = stderrMatch[1].trim();
    }

    // Split multi-line errors
    const errorLines = rawMessage
      .split('\n')
      .map(l => l.trim())
      .filter(l => l.length > 0);

    const enhancedErrors = enhanceErrors(
      errorLines.length > 0 ? errorLines : [rawMessage]
    );

    return NextResponse.json({
      success: false,
      errors: enhancedErrors,
    }, { status: 500 });
  }
}
