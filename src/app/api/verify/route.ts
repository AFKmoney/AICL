import { NextRequest, NextResponse } from 'next/server';
import { execFileSync } from 'child_process';
import path from 'path';

const HELPER_PATH = path.join(process.cwd(), 'scripts', 'aicl_helper.py');
const PYTHON_PATH = '/usr/bin/python3.13';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { source } = body;

    if (!source || typeof source !== 'string') {
      return NextResponse.json({ error: 'Source code is required' }, { status: 400 });
    }

    const result = execFileSync(PYTHON_PATH, [HELPER_PATH, 'verify'], {
      input: source,
      timeout: 30000,
      maxBuffer: 5 * 1024 * 1024,
      encoding: 'utf-8',
    });

    const data = JSON.parse(result);
    return NextResponse.json(data);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Verification failed';
    return NextResponse.json({ overall: 'ERROR', checks: [{ name: 'error', status: 'FAIL', message, details: [] }] }, { status: 500 });
  }
}
