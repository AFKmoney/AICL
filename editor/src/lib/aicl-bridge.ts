/**
 * AICL — Python bridge
 *
 * Shared helper for invoking the AICL Python package from Next.js API routes.
 * The bridge is a small JSON-over-stdio protocol documented in
 * `python/docs/bridge_protocol.md`.
 *
 * Configuration (env vars):
 *   AICL_HELPER_PATH  Absolute path to aicl_helper.py.
 *                     Defaults to <repo>/python/scripts/aicl_helper.py.
 *   AICL_PYTHON       Python interpreter to use. Defaults to "python3".
 *
 * See `python/docs/bridge_protocol.md` for the request/response schema.
 */
import { execFileSync, type ExecFileSyncOptions } from "child_process";
import path from "path";
import fs from "fs";

const REPO_ROOT = path.resolve(__dirname, "..", "..", "..", "..");

function resolveHelperPath(): string {
  const fromEnv = process.env.AICL_HELPER_PATH;
  if (fromEnv && fs.existsSync(fromEnv)) return fromEnv;
  const candidate = path.join(REPO_ROOT, "python", "scripts", "aicl_helper.py");
  if (fs.existsSync(candidate)) return candidate;
  throw new Error(
    `aicl_helper.py not found. Set AICL_HELPER_PATH or run from the repo root. Looked at: ${candidate}`,
  );
}

function resolvePythonPath(): string {
  return process.env.AICL_PYTHON || "python3";
}

export const HELPER_PATH = resolveHelperPath();
export const PYTHON_PATH = resolvePythonPath();

/**
 * Invoke the AICL helper with the given subcommand. Source code (if any) is
 * piped to stdin; the helper writes a JSON object to stdout.
 *
 * @param subcommand  One of: compile | parse | tree | check | explain |
 *                    audit | verify | optimize | exercises
 * @param args        Extra CLI args (e.g. ["--target", "rust"] for compile)
 * @param stdin       Optional source code piped to stdin
 * @returns Parsed JSON response
 */
export function callAicl<T = unknown>(
  subcommand: string,
  args: string[] = [],
  stdin?: string,
): T {
  const opts: ExecFileSyncOptions = {
    encoding: "utf-8",
    maxBuffer: 50 * 1024 * 1024, // 50 MB — large specs produce large output
    timeout: 30_000, // 30s hard cap; raise per-route if needed
  };
  if (stdin !== undefined) opts.input = stdin;

  const stdout = execFileSync(PYTHON_PATH, [HELPER_PATH, subcommand, ...args], opts);
  try {
    return JSON.parse(stdout) as T;
  } catch (err) {
    throw new Error(
      `aicl_helper.py returned non-JSON output for "${subcommand}":\n${stdout.slice(0, 500)}`,
    );
  }
}
