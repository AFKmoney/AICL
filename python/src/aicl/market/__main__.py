"""Play one tiny-class job end to end.

    cd python && python -m aicl.market
    python -m aicl.market empty
    python -m aicl.market slash
    python -m aicl.market expire
"""

from __future__ import annotations

import json
import sys

from .engine import CLASS_TINY, InferenceMarket, JobStatus


def _dump(m: InferenceMarket, job_id: int | None) -> None:
    payload = {
        "job": None if job_id is None else {
            "nonce": job_id,
            "status": JobStatus(m.jobs[job_id].status).name if job_id in m.jobs else None,
        },
        "escrow_balances": m.balances,
        "origin_balances": m.origin_balances,
        "epoch_minted": None,
    }
    print(json.dumps(payload, indent=2))


def run_happy() -> int:
    m = InferenceMarket()
    m.post_job(1, "payer", CLASS_TINY.class_id, 100, deadline=1000)
    m.accept_job(1, "miner", CLASS_TINY.model_hash)
    m.post_proof(1, "proof-tiny-1", "out-tiny-1", 12, 40, 180, now=10)
    m.settle(1, proof_ok=True, now=20)
    minted = m.close_epoch()
    print(json.dumps({
        "path": "happy",
        "class": "tiny",
        "status": JobStatus.SETTLED.name,
        "escrow_to_miner": m.balances.get("miner", 0),
        "origin_minted": minted,
        "origin_to_miner": m.origin_balances.get("miner", 0),
        "empty_epoch_would_mint": 0,
    }, indent=2))
    return 0


def run_empty() -> int:
    m = InferenceMarket()
    minted = m.close_epoch()
    print(json.dumps({"path": "empty", "origin_minted": minted}, indent=2))
    return 0 if minted == 0 else 1


def run_slash() -> int:
    m = InferenceMarket()
    m.post_job(1, "payer", CLASS_TINY.class_id, 100, deadline=1000)
    m.accept_job(1, "miner", CLASS_TINY.model_hash)
    m.post_proof(1, "proof-bad", "out-bad", 12, 40, 180, now=10)
    job = m.settle(1, proof_ok=False, now=20)
    print(json.dumps({
        "path": "slash",
        "status": JobStatus(job.status).name,
        "payer_escrow_plus_bond": m.balances.get("payer", 0),
        "origin_minted": m.close_epoch(),
    }, indent=2))
    return 0


def run_expire() -> int:
    m = InferenceMarket()
    m.post_job(1, "payer", CLASS_TINY.class_id, 80, deadline=50)
    job = m.expire(1, now=51)
    print(json.dumps({
        "path": "expire",
        "status": JobStatus(job.status).name,
        "payer_refund": m.balances.get("payer", 0),
        "origin_minted": m.close_epoch(),
    }, indent=2))
    return 0


def main(argv: list[str]) -> int:
    path = argv[1] if len(argv) > 1 else "happy"
    if path in ("happy", "tiny"):
        return run_happy()
    if path == "empty":
        return run_empty()
    if path == "slash":
        return run_slash()
    if path == "expire":
        return run_expire()
    print("usage: python -m aicl.market [happy|empty|slash|expire]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
