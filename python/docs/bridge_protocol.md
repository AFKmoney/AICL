# AICL ↔ Editor Bridge Protocol

**Version:** 1.0
**Status:** Stable
**Last updated:** 2026-06-18

This document specifies the JSON-over-stdio protocol used by the AICL web
editor (Next.js) to invoke the AICL Python compiler through
[`scripts/aicl_helper.py`](../scripts/aicl_helper.py).

## Transport

- **Invocation:** `python3 aicl_helper.py <subcommand> [args...]`
- **Request payload:** AICL source code piped to **stdin** (UTF-8). Some
  subcommands take no stdin (see below).
- **Response payload:** A single JSON object written to **stdout** (UTF-8).
  The object always contains a top-level field indicating success or failure.
- **Errors:** Python tracebacks are written to **stderr** and the process
  exits non-zero. The bridge client (`editor/src/lib/aicl-bridge.ts`) wraps
  these into a JSON error envelope.
- **Timeout:** 30 seconds default (configurable per-route).
- **Max buffer:** 50 MB (large programs produce large outputs).

## Common response envelope

Every successful response is a JSON object whose shape is subcommand-specific
but always includes:

```json
{
  "success": true,
  "warnings": ["..."],
  "errors": []
}
```

On failure:

```json
{
  "success": false,
  "warnings": [],
  "errors": ["Detailed error message", "Second error line"]
}
```

## Subcommands

### `compile`
**stdin:** AICL source code
**Args:** `--target <python|rust|javascript|go>` (default: `python`)
**Response:**
```json
{
  "success": true,
  "main_code": "def main():\n    ...",
  "test_code": "def test_main():\n    ...",
  "warnings": [],
  "errors": [],
  "todos_remaining": 0,
  "stages_completed": ["Specification Parsing", "...", "Final Construction"],
  "fully_compiled": true,
  "audit_coverage": 1.0,
  "audit_total": 35,
  "audit_with_provenance": 35,
  "proof_valid": true,
  "proof_path": "output/main.aicl-proof",
  "target_language": "python"
}
```

### `parse`
**stdin:** AICL source code
**Response:** `{ "success": true, "ast": { ... }, "errors": [] }`

### `tree`
**stdin:** AICL source code
**Response:** `{ "success": true, "tree": "Renderer\n├── ...", "errors": [] }`

### `verify`
**stdin:** AICL source code
**Response:**
```json
{
  "success": true,
  "overall": "PASS|FAIL|WARNING",
  "checks": [
    { "name": "Goal present", "status": "PASS|FAIL|WARN", "message": "...", "details": [] }
  ],
  "errors": []
}
```

### `audit`
**stdin:** AICL source code
**Response:**
```json
{
  "success": true,
  "total_artifacts": 35,
  "artifacts_with_provenance": 35,
  "coverage": 1.0,
  "artifacts": [
    { "name": "main.py:L10", "type": "function", "provenance": "Behavior:RenderFrame" }
  ],
  "errors": []
}
```

### `explain`
**stdin:** AICL source code
**Response:**
```json
{
  "success": true,
  "decisions": [
    { "line": "def render_frame(frame):", "reason": "Generated from Behavior:RenderFrame", "source_span": "L12-L18" }
  ],
  "errors": []
}
```

### `optimize`
**stdin:** AICL source code
**Response:**
```json
{
  "success": true,
  "actions": [
    { "type": "inline_constant", "target": "MAX_RETRIES", "improvement": 0.05 }
  ],
  "improvement_score": 0.42,
  "optimized_source": "Goal: ...",
  "errors": []
}
```

### `exercises`
**stdin:** none
**Response:** `{ "exercises": [ { "id": 1, "title": "...", "description": "...", "template": "..." } ] }`

## Versioning

The protocol follows semver. Bumping behavior:

- **PATCH:** Add a new optional field to a response (clients must ignore
  unknown fields). No client breakage.
- **MINOR:** Add a new subcommand. Existing subcommands unchanged.
- **MAJOR:** Remove or rename a subcommand; change the meaning of an existing
  field; change the request transport.

The protocol version is exposed in `aicl_helper.py --version`:

```
aicl_helper.py 1.0 (bridge protocol v1.0)
```

## Client implementation

The reference client is [`editor/src/lib/aicl-bridge.ts`](../../editor/src/lib/aicl-bridge.ts).
It exposes a single `callAicl(subcommand, args?, stdin?)` function that
returns the parsed JSON response.

## Configuration

| Env var           | Purpose                                      | Default                                          |
|-------------------|----------------------------------------------|--------------------------------------------------|
| `AICL_HELPER_PATH`| Absolute path to `aicl_helper.py`            | `<repo>/python/scripts/aicl_helper.py`           |
| `AICL_PYTHON`     | Python interpreter to use                    | `python3`                                        |

## Security considerations

- The helper executes the AICL compiler, which parses untrusted source. The
  compiler itself does not execute generated code — only the user does, by
  running `output/main.py` themselves.
- The `evolve` subcommand in the editor additionally calls an LLM (ZAI SDK)
  to repair specifications. LLM output is parsed but treated as untrusted
  AICL source and re-compiled before being shown to the user.
- Inputs larger than 50 MB are rejected by the buffer cap. Inputs larger
  than ~5 MB will likely time out at the default 30s budget; raise per-route
  if needed.
