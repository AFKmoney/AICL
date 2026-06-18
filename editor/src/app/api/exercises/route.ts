import { NextResponse } from 'next/server';
import { callAicl } from '@/lib/aicl-bridge';

export async function GET() {
  try {
    const data = callAicl('exercises');
    return NextResponse.json(data);
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Failed to load exercises';
    return NextResponse.json({ error: message, exercises: [] }, { status: 500 });
  }
}
