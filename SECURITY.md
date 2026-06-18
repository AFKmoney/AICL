# Security Policy

## Supported versions

AICL is pre-1.0 research software. Security fixes are applied only to the
latest `main` branch.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security problems.

Instead, email the maintainer directly via the email listed on the GitHub
profile at <https://github.com/AFKmoney> with:

- A description of the issue and its impact
- A minimal reproducible example (an `.aicl` snippet if possible)
- Suggested fix, if any

You should receive an acknowledgement within 72 hours. Please do not
disclose the issue publicly until a fix has been released.

## Scope

In scope:
- The AICL compiler, runtime, and CLI (`src/aicl/`)
- The Proof of Origin signing / verification chain (`crypto_signing.py`)
- The web editor's API routes (`src/app/api/`)

Out of scope:
- Bugs in third-party dependencies (report upstream)
- Self-inflicted issues from running untrusted `.aicl` programs that compile
  to and execute arbitrary Python — AICL is a compiler; treat compiled output
  the same way you would treat any other generated code.

## Hardening checklist for production deployments

- Run the web editor behind a reverse proxy (Caddyfile is included as a
  starting point).
- Restrict the `OPENAI_API_KEY` to the minimum scope required.
- Run the editor process under a dedicated low-privilege user.
- Treat the SQLite database as opaque — do not edit it manually.
- Pin dependency versions in production (`bun install --frozen-lockfile`).
