import { NextRequest, NextResponse } from 'next/server';
import { callAicl } from '@/lib/aicl-bridge';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { source } = body;

    if (!source || typeof source !== 'string') {
      return NextResponse.json({ error: 'Source code is required' }, { status: 400 });
    }

    const data = callAicl('optimize', [], source);
    return NextResponse.json(data);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Optimization failed';
    return NextResponse.json({ error: message, actions: [], improvement_score: 0 }, { status: 500 });
  }
}
