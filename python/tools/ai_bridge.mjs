#!/usr/bin/env node
/**
 * AICL AI Bridge — Node.js bridge for z-ai-web-dev-sdk
 *
 * Usage:
 *   node ai_bridge.mjs --mode generate --task "Create a banking system"
 *   node ai_bridge.mjs --mode diagnose --error "..." --source "..."
 *   node ai_bridge.mjs --mode fix --error "..." --source "..." --code "..."
 *   node ai_bridge.mjs --mode enhance --source "..."
 *   node ai_bridge.mjs --mode chat --message "..."
 *
 * Output: JSON to stdout
 *
 * The SDK is resolved relative to the repo root, or from $AICL_EDITOR_NODE_MODULES
 * if set, or from a plain `import` if installed in the editor's node_modules.
 */

import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Candidate locations for z-ai-web-dev-sdk:
let ZAI;
try {
  // 1. Editor's node_modules (when this script is invoked from the editor)
  ZAI = (await import(path.resolve(__dirname, '..', '..', 'editor', 'node_modules', 'z-ai-web-dev-sdk', 'dist', 'index.js'))).default;
} catch {
  try {
    // 2. Explicit override via env var
    if (process.env.AICL_EDITOR_NODE_MODULES) {
      ZAI = (await import(path.resolve(process.env.AICL_EDITOR_NODE_MODULES, 'z-ai-web-dev-sdk', 'dist', 'index.js'))).default;
    } else {
      throw new Error('skip');
    }
  } catch {
    try {
      // 3. Plain bare import (let Node resolve from cwd's node_modules)
      ZAI = (await import('z-ai-web-dev-sdk')).default;
    } catch (err) {
      console.error(JSON.stringify({
        success: false,
        error: 'z-ai-web-dev-sdk not found. Install it in editor/ or set AICL_EDITOR_NODE_MODULES.',
        detail: err.message,
      }));
      process.exit(2);
    }
  }
}

const args = process.argv.slice(2);

function parseArgs() {
    const parsed = {};
    for (let i = 0; i < args.length; i++) {
        if (args[i].startsWith('--')) {
            const key = args[i].slice(2);
            if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
                parsed[key] = args[i + 1];
                i++;
            } else {
                parsed[key] = true;
            }
        }
    }
    return parsed;
}

async function chat(messages, temperature = 0.7) {
    try {
        const zai = await ZAI.create();
        const completion = await zai.chat.completions.create({
            messages: messages,
            temperature: temperature,
            max_tokens: 8192,
        });
        return completion.choices[0]?.message?.content || '';
    } catch (error) {
        return JSON.stringify({ error: error.message });
    }
}

const AICL_SYSTEM_PROMPT = `You are an expert AICL (Architecture Compilation Language) specification writer.

AICL is a specification-driven language where you describe WHAT a system should do, and the compiler generates the code. The compiler guarantees that every generated line has a traceable provenance chain.

AICL has 10 language levels:

Level 1 — Architecture (MANDATORY):
  Goal: <description>
  Constraint: <requirement>
  Risk: <what can go wrong>
  Recovery: <how to recover>
  Layer: <name>
      Sublayer: <name>
  Validation: <testable assertion>

Level 2 — Entities:
  Entity <Name>
      field_name: type  (types: string, integer, float, boolean, datetime, list, dict, set, any, void, bytes)

Level 3 — Behaviors:
  Behavior <Name>
  Input: <entity list>
  Output: <type>
  Action: <natural language description of what it does>

Level 4 — Conditions:
  Condition:
  When <situation>
  Then <action>

Level 5 — Events:
  Event:
  On <trigger>
  Action: <what to do>

Level 6 — Concurrency:
  Parallel:
  <layer name 1>
  <layer name 2>

Level 7 — Optimization:
  Optimize: <target>
  Priority: <what takes precedence>

Level 8 — Learning:
  Learn: <what to learn>
  Goal: <learning objective>
  Adapt: <what to adapt>
  Based on: <adaptation criteria>

Level 9 — Security:
  Security:
  Encrypt: <what to encrypt>
  Protect: <what to protect>

Level 10 — Native Code:
  Native: <language>
  { <raw code> }

RULES:
1. Every program MUST have at least: Goal, Layer, Validation
2. Every Risk SHOULD have a matching Recovery
3. Entity fields use types: string, integer, float, boolean, datetime, list, dict, set, any, void, bytes
4. Behavior Actions should be clear natural language descriptions
5. Validations must be testable assertions
6. Use # for comments
7. The more complete the spec, the better the generated code
8. Always include multiple Risks with Recoveries for robustness
9. Use meaningful, descriptive names for entities and behaviors
10. Structure layers logically from presentation to data

OUTPUT FORMAT:
Return ONLY valid AICL code. No markdown fences, no explanations before/after.
Start directly with # AICL comment and Goal: section.`;

async function generateSpec(task) {
    const messages = [
        { role: 'system', content: AICL_SYSTEM_PROMPT },
        { role: 'user', content: `Create a complete AICL specification for the following task:\n\n${task}\n\nGenerate a thorough, production-quality AICL specification that uses as many language levels as appropriate. Include multiple entities, behaviors, conditions, events, and validations. Make it comprehensive.` }
    ];
    return await chat(messages, 0.7);
}

async function diagnoseError(error, source, generatedCode) {
    const messages = [
        { role: 'system', content: AICL_SYSTEM_PROMPT + '\n\nYou are also an expert at diagnosing AICL compilation and runtime errors. Analyze the error and suggest specific fixes to the AICL specification.' },
        { role: 'user', content: `An AICL specification produced the following error during compilation/execution:\n\nERROR:\n${error}\n\nAICL SOURCE:\n${source}\n\nGENERATED CODE (first 2000 chars):\n${(generatedCode || '').substring(0, 2000)}\n\nDiagnose the root cause and suggest specific fixes to the AICL source. Output a JSON object with:\n- "diagnosis": string (what went wrong)\n- "root_cause": string (why it went wrong)\n- "fix_type": one of "add_entity", "add_behavior", "add_validation", "add_recovery", "fix_action", "add_field", "other"\n- "fix_description": string (specific change to make)\n- "fixed_source": string (complete corrected AICL source, or empty if you can't fix it)` }
    ];
    return await chat(messages, 0.3);
}

async function fixSpec(error, source, generatedCode) {
    const messages = [
        { role: 'system', content: AICL_SYSTEM_PROMPT + '\n\nYou are also an expert at fixing AICL specifications. When given an error and the source, produce the COMPLETE corrected AICL source.' },
        { role: 'user', content: `Fix the following AICL specification that has an error:\n\nERROR:\n${error}\n\nCURRENT AICL SOURCE:\n${source}\n\nGENERATED CODE (first 2000 chars):\n${(generatedCode || '').substring(0, 2000)}\n\nProduce the COMPLETE corrected AICL specification. Return ONLY the AICL code, no explanations.` }
    ];
    return await chat(messages, 0.3);
}

async function enhanceSpec(source) {
    const messages = [
        { role: 'system', content: AICL_SYSTEM_PROMPT + '\n\nYou enhance existing AICL specifications by adding missing elements, improving coverage, and making validations more specific and testable.' },
        { role: 'user', content: `Enhance the following AICL specification:\n\n${source}\n\nImprove it by:\n1. Adding any missing Risk/Recovery pairs\n2. Making validations more specific and testable\n3. Adding any missing entity fields\n4. Improving behavior action descriptions\n5. Adding Security sections where appropriate\n\nReturn the COMPLETE enhanced AICL specification. Return ONLY AICL code.` }
    ];
    return await chat(messages, 0.5);
}

async function genericChat(message) {
    const messages = [
        { role: 'system', content: AICL_SYSTEM_PROMPT },
        { role: 'user', content: message }
    ];
    return await chat(messages, 0.7);
}

async function main() {
    const opts = parseArgs();
    const mode = opts.mode || 'chat';

    let result;

    switch (mode) {
        case 'generate':
            if (!opts.task) {
                process.stderr.write(JSON.stringify({ error: 'Missing --task argument' }));
                process.exit(1);
            }
            result = await generateSpec(opts.task);
            break;

        case 'diagnose':
            if (!opts.error) {
                process.stderr.write(JSON.stringify({ error: 'Missing --error argument' }));
                process.exit(1);
            }
            result = await diagnoseError(opts.error, opts.source || '', opts.code || '');
            break;

        case 'fix':
            if (!opts.error || !opts.source) {
                process.stderr.write(JSON.stringify({ error: 'Missing --error or --source argument' }));
                process.exit(1);
            }
            result = await fixSpec(opts.error, opts.source, opts.code || '');
            break;

        case 'enhance':
            if (!opts.source) {
                process.stderr.write(JSON.stringify({ error: 'Missing --source argument' }));
                process.exit(1);
            }
            result = await enhanceSpec(opts.source);
            break;

        case 'chat':
            if (!opts.message) {
                process.stderr.write(JSON.stringify({ error: 'Missing --message argument' }));
                process.exit(1);
            }
            result = await genericChat(opts.message);
            break;

        default:
            process.stderr.write(JSON.stringify({ error: `Unknown mode: ${mode}` }));
            process.exit(1);
    }

    process.stdout.write(JSON.stringify({ result: result }));
}

main().catch(err => {
    process.stderr.write(JSON.stringify({ error: err.message }));
    process.exit(1);
});
