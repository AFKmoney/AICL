import { NextRequest, NextResponse } from 'next/server';
import { callAicl } from '@/lib/aicl-bridge';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { source } = body;

    if (!source || typeof source !== 'string') {
      return NextResponse.json({ error: 'Source code is required' }, { status: 400 });
    }

    const data = callAicl('verify', [], source);
    return NextResponse.json(data);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Verification failed';
    return NextResponse.json({ overall: 'ERROR', checks: [{ name: 'error', status: 'FAIL', message, details: [] }] }, { status: 500 });
  }
}
