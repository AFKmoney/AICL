//! AICL Inference Market program husk.
//! Spec: python/examples/showcase/90_inference_market.aicl
//! Executable twin: python/src/aicl/market/
//!
//! Compile path today: `aicl compile ... --target rust` then keep this crate
//! as the Solana-shaped account/instruction shell. No ticker mint here.

#[derive(Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum JobStatus {
    Posted = 0,
    Accepted = 1,
    Proven = 2,
    Settled = 3,
    Slashed = 4,
    Refunded = 5,
}

#[derive(Clone, Copy)]
pub struct JobAccount {
    pub job_nonce: u64,
    pub class_id: u64,
    pub spec_hash: [u8; 32],
    pub proof_hash: [u8; 32],
    pub model_hash: [u8; 32],
    pub escrow: u64,
    pub bond: u64,
    pub deadline_slot: u64,
    pub token_out: u64,
    pub latency_ms: u64,
    pub status: u8,
}

pub fn billable_tokens(token_out: i64, budget_out: i64) -> i64 {
    let mut billed = token_out;
    if billed > budget_out {
        billed = budget_out;
    }
    if billed < 0 {
        billed = 0;
    }
    billed
}

pub fn bond_amount(escrow: i64, multiple_times_10: i64) -> i64 {
    (escrow * multiple_times_10) / 10
}

pub fn epoch_budget(initial_budget: i64, normalized_total: i64, halving_interval: i64) -> i64 {
    if halving_interval < 1 {
        return 0;
    }
    let era = normalized_total / halving_interval;
    let mut budget = initial_budget;
    let mut i = 0;
    while i < era {
        budget /= 2;
        i += 1;
    }
    budget
}

pub fn miner_pay(emission: i64, miner_score: i64, total_score: i64) -> i64 {
    let pool = (emission * 70) / 100;
    if total_score < 1 {
        return 0;
    }
    (pool * miner_score) / total_score
}

pub fn can_settle(status: i64, proof_ok: i64, deadline_ok: i64, replay: i64) -> i64 {
    if replay > 0 {
        return 0;
    }
    if proof_ok < 1 {
        return 0;
    }
    if deadline_ok < 1 {
        return 0;
    }
    if status < 2 {
        return 0;
    }
    1
}

pub fn settle_guard(proof_ok: bool, replay: bool, past_deadline: bool) -> bool {
    proof_ok && !replay && !past_deadline
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_score_mints_zero() {
        assert_eq!(miner_pay(1000, 1, 0), 0);
    }

    #[test]
    fn halving_and_bond() {
        assert_eq!(epoch_budget(1000, 210_000, 210_000), 500);
        assert_eq!(bond_amount(100, 15), 150);
        assert_eq!(billable_tokens(5000, 2048), 2048);
    }

    #[test]
    fn settle_requires_proof() {
        assert!(!settle_guard(false, false, false));
        assert_eq!(can_settle(2, 1, 1, 0), 1);
    }
}
