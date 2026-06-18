# AICL Editor — Web IDE

Next.js 16 + React 19 + Prisma + shadcn/ui web editor for AICL. See the
[top-level README](../README.md) for project overview.

## What's here

- [`src/app/`](./src/app/) — Next.js app routes (API + page)
- [`src/app/api/`](./src/app/api/) — 11 API routes that wrap the AICL Python package
- [`src/components/ui/`](./src/components/ui/) — shadcn/ui components
- [`src/lib/aicl-bridge.ts`](./src/lib/aicl-bridge.ts) — Shared Python bridge client (DRY)
- [`src/lib/db.ts`](./src/lib/db.ts) — Prisma client
- [`prisma/schema.prisma`](./prisma/schema.prisma) — Database schema (SQLite via Prisma)
- [`public/`](./public/) — Static assets

## Architecture

The editor is a thin UI layer over the Python `aicl` package. Each API route
calls `callAicl()` from `src/lib/aicl-bridge.ts`, which spawns
`python/scripts/aicl_helper.py` as a subprocess and pipes JSON over stdio.
The protocol is documented in
[`python/docs/bridge_protocol.md`](../python/docs/bridge_protocol.md).

```
Browser → Next.js API route → aicl-bridge.ts → aicl_helper.py → aicl package
```

The editor has its own SQLite database (for users / posts / sessions) that
is **independent** of the AICL language itself.

## Install

```bash
cp ../.env.example ../.env   # from repo root
bun install
bun run db:push              # initialise the SQLite database
bun run dev                  # http://localhost:3000
```

The editor requires the AICL Python package to be installed first:

```bash
cd ../python && pip install -e ".[tui]"
```

## Configuration

The bridge client reads two env vars (with sensible defaults):

| Env var           | Purpose                          | Default                                          |
|-------------------|----------------------------------|--------------------------------------------------|
| `AICL_HELPER_PATH`| Path to `aicl_helper.py`         | `<repo>/python/scripts/aicl_helper.py`           |
| `AICL_PYTHON`     | Python interpreter               | `python3`                                        |

## Bun vs npm vs pnpm

Bun is the default (faster install, smaller lockfile). The editor works
with any of them:

```bash
# npm
rm bun.lock && npm install && npm run dev

# pnpm
rm bun.lock && pnpm install && pnpm dev
```

The `package.json` is tool-agnostic.

## Production build

```bash
bun run build
bun run start
```

For reverse-proxy deployment, see [`Caddyfile`](./Caddyfile).
