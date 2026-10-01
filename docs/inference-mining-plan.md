# AICL Inference Mining Plan

Companion to `docs/inference-market-whitepaper.md`.
Source of truth for parameters: `python/examples/showcase/90_inference_market.aicl`.

---

## 0. One-sentence rule

**No settled Proof of Origin, no emission.**

Wall-clock halvings without work are banned. An empty epoch emits nothing.

---

## 1. Roles

| Role | Off-chain | On-chain |
|------|-----------|----------|
| Payer | Writes / selects AICL spec class, pays escrow in USDC | Posts job |
| Miner | Runs declared model, produces output + `.aicl-proof` | Accepts job, posts proof hash |
| Watcher | Re-runs or fraud-checks a sample of proofs | Challenges |
| Registrar | Publishes spec classes | Updates class registry (timelock) |
| Compiler | `aicl compile --target rust` | Program upgrade via governance |

---

## 2. Job lifecycle (operator view)

1. Payer: `aicl verify job.aicl` must pass locally before broadcast.
2. Payer posts `spec_hash`, `class_id`, escrow, deadline.
3. Miner posts bond (150% of escrow) and `model_hash`.
4. Miner runs inference off-chain. Writes proof sidecar.
5. Miner posts `proof_hash`, `output_hash`, `token_in`, `token_out`, `latency_ms`.
6. Challenge window (30 min default).
7. If quiet: program settles — escrow to miner, ORIGIN reward, voucher burn, bonds released.
8. If challenged: watcher and miner freeze; verifier path runs; winner takes counterparty bond according to Recovery.

CLI sketch (to be bound to the AICL market module later):

```bash
aicl verify examples/showcase/90_inference_market.aicl
aicl compile examples/showcase/90_inference_market.aicl --target rust -o ./chain
aicl proof ./chain/main.aicl-proof
python tools/verify_proof.py ./chain/main.aicl-proof
```

---

## 3. Emission

### 3.1 Supply

- `ORIGIN` max: 21_000_000
- Genesis: 0 circulating except a 5% protocol allocation vested 48 months, no instant dump into the AMM
- Rewards mint only on `Settle` instructions

### 3.2 Epoch

- Length: 7 days
- Score of a miner in epoch t:

```
score_i = sum_over_settled_jobs ( class_weight * quality_factor )
```

- Quality factor:

```
quality = 1
if token_out > budget: quality = 0          # also slash path
if latency_ms > sla_ms: quality *= 0.5
if challenge_survived == 0 and challenged: quality = 0
```

- Miner payout:

```
emission_t = epoch_budget(halving_era)
miner_pool = emission_t * 70 / 100
pay_i = miner_pool * score_i / max(1, sum_scores)
```

### 3.3 Halving

Trigger: `normalized_settled_jobs_total` crosses 210_000, 420_000, …

```
normalized += class_weight   # tiny=1, mid=8, frontier=64
era = floor(normalized / 210000)
epoch_budget = initial_epoch_budget / 2^era
```

`initial_epoch_budget` is chosen so the infinite sum of work-triggered eras respects max supply after protocol + treasury vest. Exact integer schedule lives in the AICL spec as AX so all four current backends (and later Solana) compute the same number.

### 3.4 Split

| Bucket | % |
|--------|---|
| Miners with settled proofs | 70 |
| Watchers who won or correctly attested | 15 |
| Spec-class treasury (bounties for new classes) | 10 |
| Protocol vest | 5 |

---

## 4. Class registry

A class is an AICL file hash plus weights.

| class_id | weight | example SLA | bond multiple |
|----------|--------|-------------|---------------|
| tiny | 1 | 2s, 2k out | 1.5x |
| mid | 8 | 8s, 8k out | 1.5x |
| frontier | 64 | 30s, 16k out | 2.0x |

Adding a class is a governance action with a timelock. Shipping a class whose spec has no Recovery is rejected by `aicl verify` before it can be registered.

---

## 5. Hardware reality (miners)

The protocol does not care if the worker is a 4090, an H100, or a hosted API **as long as `model_hash` matches**. Substitution is a slash, not a pricing debate.

Recommended miner stack for v0:

- AICL CLI + `verify_proof.py`
- Local or rented runtime that can pin a checkpoint hash
- Wallet for bond + rewards
- Watcher client optional but rewarded

The chain is not a GPU scheduler. Akash / io.net / a raw box can all sit under the same spec class.

---

## 6. Security runbook

| Event | Action |
|-------|--------|
| Proof verify fails after Accept | Slash miner bond, refund payer |
| Replay of old proof_hash | Reject, no state change |
| Watcher challenge loses | Watcher bond → miner |
| Registrar posts garbage class | Timelock + `aicl verify` gate |
| Program upgrade | Same AICL source, new compile, proof compared |
| ORIGIN AMM manipulation | Jobs still escrow in USDC; rewards may be ugly, work still settles |

---

## 7. Build sequence

1. Land `90_inference_market.aicl` (this branch).
2. `aicl verify` + `aicl compile --target rust`.
3. Wrap emitted Rust in `programs/inference_market` (Anchor) — next coding pass.
4. Devnet: one spec class `tiny`, fake model hash, human watchers.
5. Only then: emission + AMM.
6. Backend `--target solana` / `--target solidity` when the emitter exists. Until then Native rust in the spec *is* the chain sketch.

## 8. Explicit non-work

Do not ship:

- a fair-launch ticker with no `Settle` instruction
- rewards for GPU heartbeat pings
- a dashboard that counts LLM tokens and calls them minted ORIGIN

If it does not pass Proof of Origin, it is not a block of work.
