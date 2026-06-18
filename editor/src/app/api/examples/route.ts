import { NextResponse } from 'next/server';
import { readFileSync } from 'fs';
import path from 'path';

// Resolve the examples directory relative to this file so it works regardless
// of where `next dev` is invoked from.
const EXAMPLES_DIR = path.resolve(__dirname, '..', '..', '..', '..', '..', 'python', 'examples');

const EXAMPLE_FILES = [
  { id: '01_blue_square', name: '01_blue_square.aicl', title: 'Blue Square', description: 'Level 1 simple graphics' },
  { id: '02_pong', name: '02_pong.aicl', title: 'Pong Game', description: 'Levels 1-6 game with behaviors' },
  { id: '03_chat', name: '03_chat.aicl', title: 'Chat App', description: 'Levels 1-9 full application' },
  { id: '04_chess', name: '04_chess.aicl', title: 'Chess Game', description: 'Levels 1-9 complex state' },
];

export async function GET() {
  try {
    const examples = EXAMPLE_FILES.map((ex) => {
      try {
        const source = readFileSync(path.join(EXAMPLES_DIR, ex.name), 'utf-8');
        return { ...ex, source };
      } catch {
        return { ...ex, source: `# Error: Could not load ${ex.name}` };
      }
    });
    return NextResponse.json({ examples });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Failed to load examples';
    return NextResponse.json({ error: message, examples: [] }, { status: 500 });
  }
}
