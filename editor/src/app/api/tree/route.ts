import { NextRequest, NextResponse } from 'next/server';
import { callAicl } from '@/lib/aicl-bridge';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { source } = body;

    if (!source || typeof source !== 'string') {
      return NextResponse.json({ error: 'Source code is required' }, { status: 400 });
    }

    const data = callAicl('tree', [], source);
    return NextResponse.json(data);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Tree generation failed';
    return NextResponse.json({ error: message, tree: '' }, { status: 500 });
  }
}
