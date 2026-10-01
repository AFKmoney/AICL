from aicl.market import CLASS_TINY, InferenceMarket, JobStatus
from aicl.market.economy import (
    billable_tokens,
    bond_amount,
    can_settle,
    epoch_budget,
    miner_pay,
    quality_factor,
)


def test_ax_billable_and_bond():
    assert billable_tokens(5000, 2048) == 2048
    assert bond_amount(100, 15) == 150


def test_empty_epoch_mints_zero():
    m = InferenceMarket()
    assert m.close_epoch() == 0


def test_happy_path_settle():
    m = InferenceMarket()
    m.post_job(1, "payer", CLASS_TINY.class_id, 100, deadline=1000)
    m.accept_job(1, "miner", CLASS_TINY.model_hash)
    m.post_proof(1, "proof-a", "out-a", 10, 20, 100, now=10)
    job = m.settle(1, proof_ok=True, now=20)
    assert job.status == JobStatus.SETTLED
    assert m.balances["miner"] == 100
    minted = m.close_epoch()
    assert minted > 0
    assert m.origin_balances["miner"] == minted


def test_model_substitution_rejected():
    m = InferenceMarket()
    m.post_job(2, "payer", CLASS_TINY.class_id, 100, deadline=1000)
    try:
        m.accept_job(2, "miner", "wrong-model")
        assert False, "should reject"
    except ValueError as exc:
        assert "substitution" in str(exc)


def test_proof_replay_rejected():
    m = InferenceMarket()
    m.post_job(3, "payer", CLASS_TINY.class_id, 100, deadline=1000)
    m.accept_job(3, "miner", CLASS_TINY.model_hash)
    m.post_proof(3, "proof-b", "out-b", 10, 20, 100, now=10)
    m.post_job(4, "payer", CLASS_TINY.class_id, 100, deadline=1000)
    m.accept_job(4, "miner", CLASS_TINY.model_hash)
    try:
        m.post_proof(4, "proof-b", "out-c", 10, 20, 100, now=11)
        assert False, "should reject replay"
    except ValueError as exc:
        assert "replay" in str(exc)


def test_expire_refunds_payer():
    m = InferenceMarket()
    m.post_job(5, "payer", CLASS_TINY.class_id, 80, deadline=50)
    job = m.expire(5, now=51)
    assert job.status == JobStatus.REFUNDED
    assert m.balances["payer"] == 80


def test_bad_proof_slashes_to_payer():
    m = InferenceMarket()
    m.post_job(6, "payer", CLASS_TINY.class_id, 100, deadline=1000)
    m.accept_job(6, "miner", CLASS_TINY.model_hash)
    m.post_proof(6, "proof-c", "out-c", 10, 20, 100, now=10)
    job = m.settle(6, proof_ok=False, now=20)
    assert job.status == JobStatus.SLASHED
    assert m.balances["payer"] == 250


def test_false_challenge_pays_miner():
    m = InferenceMarket()
    m.post_job(7, "payer", CLASS_TINY.class_id, 100, deadline=1000)
    m.accept_job(7, "miner", CLASS_TINY.model_hash)
    m.post_proof(7, "proof-d", "out-d", 10, 20, 100, now=10)
    job = m.challenge(7, "watcher", 25, watcher_wins=False)
    assert job.status == JobStatus.SETTLED
    assert m.balances["miner"] == 125


def test_can_settle_requires_proven():
    assert can_settle(1, 1, 1, 0) == 0
    assert can_settle(2, 1, 1, 0) == 1
    assert can_settle(2, 1, 1, 1) == 0


def test_halving_and_quality():
    assert epoch_budget(1000, 0, 210_000) == 1000
    assert epoch_budget(1000, 210_000, 210_000) == 500
    assert quality_factor(3000, 2048, 100, 2000) == 0
    assert quality_factor(20, 2048, 5000, 2000) == 0
    assert miner_pay(1000, 1, 1) == 700
