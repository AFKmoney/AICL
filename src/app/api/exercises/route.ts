import { NextResponse } from 'next/server';
import { execFileSync } from 'child_process';
import path from 'path';

const HELPER_PATH = path.join(process.cwd(), 'scripts', 'aicl_helper.py');
const PYTHON_PATH = '/usr/bin/python3.13';

export async function GET() {
  try {
    const result = execFileSync(PYTHON_PATH, [HELPER_PATH, 'exercises'], {
      timeout: 10000,
      maxBuffer: 1024 * 1024,
      encoding: 'utf-8',
    });

    const data = JSON.parse(result);
    return NextResponse.json(data);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Failed to load exercises';
    return NextResponse.json({ error: message, exercises: [] }, { status: 500 });
  }
}
