"""Off-chain reference state machine for the Inference Market.

This is the executable Recovery table. The Solana program in
`programs/inference_market` is the same machine with hashes on-chain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, Optional

from .economy import bond_amount, can_settle, epoch_budget, quality_factor


class JobStatus(IntEnum):
    POSTED = 0
    ACCEPTED = 1
    PROVEN = 2
    SETTLED = 3
    SLASHED = 4
    REFUNDED = 5


@dataclass(frozen=True)
class SpecClass:
    class_id: int
    spec_hash: str
    model_hash: str
    weight: int
    budget_out: int
    sla_ms: int
    bond_multiple_x10: int


CLASS_TINY = SpecClass(
    class_id=1,
    spec_hash="tiny-v0",
    model_hash="tiny-model-v0",
    weight=1,
    budget_out=2048,
    sla_ms=2000,
    bond_multiple_x10=15,
)


@dataclass
class Job:
    job_nonce: int
    class_id: int
    spec_hash: str
    payer: str
    escrow: int
    deadline: int
    miner: Optional[str] = None
    bond: int = 0
    watcher: Optional[str] = None
    watcher_bond: int = 0
    proof_hash: Optional[str] = None
    output_hash: Optional[str] = None
    model_hash: Optional[str] = None
    token_in: int = 0
    token_out: int = 0
    latency_ms: int = 0
    status: JobStatus = JobStatus.POSTED


@dataclass
class InferenceMarket:
    initial_epoch_budget: int = 1000
    halving_interval: int = 210_000
    challenge_window: int = 30
    classes: Dict[int, SpecClass] = field(default_factory=lambda: {CLASS_TINY.class_id: CLASS_TINY})
    jobs: Dict[int, Job] = field(default_factory=dict)
    used_proofs: set = field(default_factory=set)
    balances: Dict[str, int] = field(default_factory=dict)
    origin_balances: Dict[str, int] = field(default_factory=dict)
    miner_scores: Dict[str, int] = field(default_factory=dict)
    normalized_total: int = 0
    epoch_normalized: int = 0

    def _pay(self, who: str, amount: int) -> None:
        self.balances[who] = self.balances.get(who, 0) + amount

    def _origin(self, who: str, amount: int) -> None:
        self.origin_balances[who] = self.origin_balances.get(who, 0) + amount

    def post_job(self, job_nonce: int, payer: str, class_id: int, escrow: int, deadline: int) -> Job:
        if job_nonce in self.jobs:
            raise ValueError("job nonce replay")
        spec = self.classes[class_id]
        job = Job(
            job_nonce=job_nonce,
            class_id=class_id,
            spec_hash=spec.spec_hash,
            payer=payer,
            escrow=escrow,
            deadline=deadline,
        )
        self.jobs[job_nonce] = job
        return job

    def accept_job(self, job_nonce: int, miner: str, model_hash: str) -> Job:
        job = self.jobs[job_nonce]
        spec = self.classes[job.class_id]
        if job.status != JobStatus.POSTED:
            raise ValueError("job not posted")
        if model_hash != spec.model_hash:
            raise ValueError("model substitution")
        job.miner = miner
        job.model_hash = model_hash
        job.bond = bond_amount(job.escrow, spec.bond_multiple_x10)
        job.status = JobStatus.ACCEPTED
        return job

    def post_proof(
        self,
        job_nonce: int,
        proof_hash: str,
        output_hash: str,
        token_in: int,
        token_out: int,
        latency_ms: int,
        now: int,
    ) -> Job:
        job = self.jobs[job_nonce]
        if job.status != JobStatus.ACCEPTED:
            raise ValueError("job not accepted")
        if now > job.deadline:
            raise ValueError("deadline")
        if proof_hash in self.used_proofs:
            raise ValueError("proof replay")
        job.proof_hash = proof_hash
        job.output_hash = output_hash
        job.token_in = token_in
        job.token_out = token_out
        job.latency_ms = latency_ms
        job.status = JobStatus.PROVEN
        self.used_proofs.add(proof_hash)
        return job

    def expire(self, job_nonce: int, now: int) -> Job:
        job = self.jobs[job_nonce]
        if job.status in (JobStatus.SETTLED, JobStatus.SLASHED, JobStatus.REFUNDED):
            return job
        if now <= job.deadline and job.status == JobStatus.PROVEN:
            return job
        if job.status == JobStatus.PROVEN:
            return job
        if now <= job.deadline:
            raise ValueError("not expired")
        job.status = JobStatus.REFUNDED
        self._pay(job.payer, job.escrow)
        return job

    def slash_model_mismatch(self, job_nonce: int) -> Job:
        job = self.jobs[job_nonce]
        spec = self.classes[job.class_id]
        if job.model_hash != spec.model_hash:
            job.status = JobStatus.SLASHED
            self._pay(job.payer, job.escrow + job.bond)
            return job
        raise ValueError("no mismatch")

    def challenge(self, job_nonce: int, watcher: str, watcher_bond: int, watcher_wins: bool) -> Job:
        job = self.jobs[job_nonce]
        if job.status != JobStatus.PROVEN:
            raise ValueError("not proven")
        job.watcher = watcher
        job.watcher_bond = watcher_bond
        if watcher_wins:
            job.status = JobStatus.SLASHED
            self._pay(job.payer, job.escrow)
            self._pay(watcher, job.bond)
            return job
        job.status = JobStatus.SETTLED
        assert job.miner is not None
        self._pay(job.miner, job.escrow + watcher_bond)
        self._reward(job, challenge_won_by_watcher=0)
        return job

    def settle(self, job_nonce: int, proof_ok: bool, now: int) -> Job:
        job = self.jobs[job_nonce]
        deadline_ok = 1 if now <= job.deadline + self.challenge_window else 0
        allowed = can_settle(int(job.status), 1 if proof_ok else 0, deadline_ok, 0)
        if allowed != 1:
            if not proof_ok and job.miner:
                job.status = JobStatus.SLASHED
                self._pay(job.payer, job.escrow + job.bond)
                return job
            raise ValueError("cannot settle")
        spec = self.classes[job.class_id]
        if job.model_hash != spec.model_hash:
            return self.slash_model_mismatch(job_nonce)
        job.status = JobStatus.SETTLED
        assert job.miner is not None
        self._pay(job.miner, job.escrow)
        self._reward(job, challenge_won_by_watcher=0)
        return job

    def _reward(self, job: Job, challenge_won_by_watcher: int) -> None:
        spec = self.classes[job.class_id]
        q = quality_factor(
            job.token_out,
            spec.budget_out,
            job.latency_ms,
            spec.sla_ms,
            challenge_won_by_watcher,
        )
        units = spec.weight * q
        self.epoch_normalized += units
        self.normalized_total += units
        if job.miner:
            self.miner_scores[job.miner] = self.miner_scores.get(job.miner, 0) + units
        budget = epoch_budget(self.initial_epoch_budget, self.normalized_total, self.halving_interval)
        if self.epoch_normalized < 1:
            return
        if job.miner and units > 0:
            pay = (budget * 70 // 100) * units
            # per-job preview; full epoch split happens in close_epoch
            self._origin(job.miner, 0 if pay < 0 else 0)

    def close_epoch(self) -> int:
        if self.epoch_normalized < 1:
            self.miner_scores.clear()
            return 0
        budget = epoch_budget(self.initial_epoch_budget, self.normalized_total, self.halving_interval)
        minted = 0
        total = sum(self.miner_scores.values())
        if total < 1:
            self.epoch_normalized = 0
            self.miner_scores.clear()
            return 0
        pool = (budget * 70) // 100
        for miner, score in self.miner_scores.items():
            pay = (pool * score) // total
            self._origin(miner, pay)
            minted += pay
        self.epoch_normalized = 0
        self.miner_scores.clear()
        return minted
