"""AX economics from 90_inference_market.aicl, as executable Python.

Integer division matches the AICL/AX behaviors so Rust and Python agree.
"""

from __future__ import annotations


def normalized_units(weight: int, quality: int) -> int:
    if quality < 0:
        quality = 0
    if quality > 1:
        quality = 1
    return weight * quality


def billable_tokens(token_out: int, budget_out: int) -> int:
    billed = token_out
    if billed > budget_out:
        billed = budget_out
    if billed < 0:
        billed = 0
    return billed


def quality_factor(
    token_out: int,
    budget_out: int,
    latency_ms: int,
    sla_ms: int,
    challenge_won_by_watcher: int = 0,
) -> int:
    if token_out > budget_out:
        return 0
    if challenge_won_by_watcher > 0:
        return 0
    quality = 1
    if latency_ms > sla_ms:
        quality = quality // 2
    return quality


def epoch_budget(initial_budget: int, normalized_total: int, halving_interval: int) -> int:
    if halving_interval < 1:
        raise ValueError("halving_interval must be >= 1")
    era = normalized_total // halving_interval
    budget = initial_budget
    i = 0
    while i < era:
        budget = budget // 2
        i += 1
    return budget


def miner_pay(emission: int, miner_score: int, total_score: int) -> int:
    pool = (emission * 70) // 100
    if total_score < 1:
        return 0
    return (pool * miner_score) // total_score


def bond_amount(escrow: int, multiple_times_10: int) -> int:
    return (escrow * multiple_times_10) // 10


def can_settle(status: int, proof_ok: int, deadline_ok: int, replay: int) -> int:
    if replay > 0:
        return 0
    if proof_ok < 1:
        return 0
    if deadline_ok < 1:
        return 0
    if status < 2:
        return 0
    return 1
