# AICL Inference Market

**Proof-of-Origin as the settlement layer for useful inference**

Version 0.1 — 2026-09-30  
Author: Philippe-Antoine Robert (@AFKmoney)  
Language of implementation: AICL  
Intended compile targets: Rust (Solana / Anchor), later Solidity / Move

---

## Abstract

Large language model *tokens* and cryptocurrency *tokens* are not the same object. One is a unit of model work. The other is a unit of transferable claim. Markets that pretend they are identical misprice compute, invite cheap-model substitution, and collapse when the coin pumps or dumps.

AICL already treats work as a specification: Goal, Constraint, Risk, Recovery, and Validation are mandatory. Every compilation emits a cryptographic Proof of Origin. The Inference Market uses that proof as the only thing the chain is allowed to settle.

A miner is not hashing empty nonces. A miner is a node that accepts a compiled inference spec, runs the declared model class, posts a Proof of Origin, and is paid only if `aicl verify` plus the proof verifier pass. Failed Risk bindings slash the bond. The unit of account on-chain is a **voucher for a spec class**, not a raw LLM token.

This paper specifies the economic object, the on-chain state machine, the mining schedule, and the AICL-to-blockchain compilation path.

---

## 1. Problem

1. **Non-fungibility of inference.** One output token from an 8B local model is not one output token from a frontier model with tools and a 128k context. Pricing “per token” without a spec is a lie.
2. **Unverified work.** Decentralized GPU networks can bill for GPU-seconds. They rarely prove *which* model ran, *which* checkpoint, *which* budget, *which* recovery fired.
3. **Speculative coupon vs voucher.** If the market token is the unit of payment *and* the speculative asset, usage creates sell pressure on the same asset that is supposed to store value. Operators leave when price falls; users leave when price rises.
4. **Orphan jobs.** A request with no success condition, no fallback, and no budget is not a contract. Conventional APIs allow it. AICL does not compile it.

## 2. Thesis

**Settle attested specifications, not raw tokens.**

The chain stores hashes. Off-chain nodes run models. AICL is the language in which the job, the bond, the slash, and the payout are written. The compiler emits blockchain code (first: Rust for Solana programs) plus a target-independent `.aicl-proof`.

If the compiler cannot explain why a line exists, it does not generate. If the proof does not verify, the voucher does not burn and the miner is not paid.

## 3. Objects

### 3.1 Spec class

A *spec class* is a frozen AICL program that defines a family of jobs:

- declared model hash or model class
- max input / output tokens (the LLM kind)
- latency SLA
- Risk / Recovery pairs
- Validation predicates that a verifier can check without re-running the full model when a challenge is not raised

Two jobs in the same class are fungible *as vouchers*. Two jobs in different classes are not.

### 3.2 Voucher (the crypto token)

`VOUCHER[class_id]` is a claim to have one job of that class executed, or a receipt that one such job was executed.

- Mint: collateral posted against a class.
- Burn: successful settlement (proof + validation).
- Slash: declared Risk fires and Recovery says the bond is forfeit.

The ticker that trades on an AMM, if any, is a separate coordination token (`ORIGIN`). Origin is not 1:1 with LLM tokens. Origin buys class vouchers at a market price denominated in a stable unit (USD or a stablecoin).

### 3.3 Proof of Origin (the receipt)

Reuse AICL's existing sidecar:

- source span
- compilation stage
- SHA-256 of artifacts
- optional Ed25519 signature over the chain

Market extras anchored in the same proof JSON:

- `spec_hash`
- `prompt_hash` (not the prompt)
- `output_hash` (not the output)
- `model_hash`
- `token_in`, `token_out` (LLM tokens, integers)
- `latency_ms`
- `worker_pubkey`
- `job_nonce`

The chain never stores the prompt or the completion.

## 4. State machine

```
Posted → Accepted → Proven → Settled
                 \-> Challenged → Settled | Slashed
                 \-> Expired    → Refunded
```

| State | Who acts | What must be true |
|-------|----------|-------------------|
| Posted | Payer | Escrow ≥ class price, spec_hash known |
| Accepted | Miner | Bond posted, model_hash matches class |
| Proven | Miner | Proof hash posted before deadline |
| Challenged | Watcher | Bond of watcher posted within window |
| Settled | Program | Verifier exit 0, voucher burned, miner paid |
| Slashed | Program | Challenge wins or Risk Recovery fires |
| Refunded | Program | Deadline missed, payer made whole |

Optimistic verification: settle after a challenge window unless a watcher posts a fraud proof. Full re-execution is the expensive path, not the default path.

## 5. Mining (useful work)

Mining here means **producing settled proofs**, not finding a nonce.

### 5.1 Block of work

A *work block* is a batch of accepted jobs whose proofs are committed in one Merkle root. The on-chain program stores the root, not the leaves.

### 5.2 Reward

```
reward = base_emission * class_weight * quality_factor * (1 - slash_rate)
```

- `base_emission` follows a halving schedule on settled work, not on wall-clock time alone. Time is a cap, work is the trigger.
- `class_weight` is governance-set per spec class (frontier > mid > tiny).
- `quality_factor` in [0, 1] from validation: budget respect, latency, challenge survival.
- Unsettled hashes earn zero.

### 5.3 What is *not* mining

- Hashing a header with no spec.
- Serving a cheaper model than the class declares.
- Counting LLM tokens without a validating proof.
- Inflating `token_out` with padding. Validation may cap billed tokens at `min(declared, useful_bound)`.

### 5.4 Emission sketch (parameters, not dogma)

| Parameter | v0 default |
|-----------|------------|
| Unit of account | USDC escrow, ORIGIN rewards |
| ORIGIN max supply | 21_000_000 |
| Epoch | 7 days |
| Work trigger | Merkle root of settled proofs |
| Halving | every 210,000 settled class-normalized jobs |
| Miner share | 70% of epoch emission |
| Watcher / verifier share | 15% |
| Spec-class treasury | 10% |
| Protocol | 5% |
| Challenge window | 30 minutes |
| Job deadline | class SLA + 2x p99 |
| Miner bond | 150% of job escrow |
| Watcher bond | 25% of job escrow |

Class-normalized jobs: a tiny-class settle counts as 1 unit; a mid class as 8; a frontier class as 64. Weights are in the class registry, not hardcoded forever.

## 6. Why AICL is the source language

Conventional contract languages encode *how* to move balances. They do not force the author to declare *why the work is valid*.

AICL forces:

- no Goal → no compile
- Risk without Recovery → no compile
- Validation that cannot trace to Goal → no compile
- generated line without provenance → proof fails

That is the monetary rule. An orphan inference job cannot be listed.

The existing four backends (Python, Rust, JavaScript, Go) already share one proof file. The market program is specified in AICL and compiled first to **Rust**, which is the native language of Solana programs. A later backend emits Solidity or Move from the same spec. The proof stays target-independent.

## 7. Compilation path

```
.aicl spec
    → Parser → AST → Architecture Tree
    → 9-stage compiler
    → Rust program (accounts, instructions, constraints)
    → .aicl-proof (settlement artifact)
```

Near-term: `aicl compile market.aicl --target rust` then wrap the emitted Rust in an Anchor crate (`programs/inference_market`).

Next target flag (planned, not yet in v2.1.0):

```
aicl compile market.aicl --target solana
aicl compile market.aicl --target solidity
```

Until those emitters exist, Native: rust blocks in the spec carry the account layout and instruction handlers. AX blocks carry portable arithmetic (rewards, slashing, supply).

## 8. What the chain is not allowed to do

- Read prompts or completions.
- Re-run a 70B model inside a transaction.
- Treat two spec classes as the same voucher mint.
- Pay a miner on an acknowledgement without a proof hash.
- Mint ORIGIN as a function of GPU-hours with no Validation.

## 9. Attacks and Recoveries (normative)

These must appear in the AICL source or the program does not compile.

| Risk | Recovery |
|------|----------|
| Cheap-model substitution | Class binds `model_hash`; mismatch slashes bond |
| Proof replay | `job_nonce` + payer + spec_hash unique; duplicate rejected |
| Padding output tokens | Bill `min(token_out, budget)` and allow challenge on entropy / spec Validation |
| Watcher griefing | Losing challenger loses watcher bond to miner |
| Deadline griefing | Expired job refunds payer, miner bond released if never Accepted |
| Speculative squeeze | Escrow in stable units; ORIGIN is reward, not gas for the job |
| Compiler / artifact swap | Proof hash must match compiled spec hash on registry |

## 10. Relation to existing networks

Venice-style tokens sell *access*. Bittensor-style tokens sell *ranked intelligence*. GPU DePINs sell *machine time*. AICL Inference Market sells **a compiled, recoverable, auditable job**. Those layers can stack: a DePIN can be the worker backend; AICL remains the settlement language.

## 11. Non-goals (v0)

- Training markets.
- On-chain model weights.
- Governance theater before one spec class settles in production.
- Pegging ORIGIN to a single LLM token price.

## 12. Success conditions

The system works when:

1. A spec without Recovery cannot list.
2. A proof that fails `verify_proof` cannot settle.
3. A miner who swaps the model loses the bond.
4. A payer who never gets a proof in time is refunded.
5. Emission in an epoch with zero settled proofs is zero.

If any of those five fail, the market is not an inference market. It is a ticker.

## 13. Artifacts in this repository

| Path | Role |
|------|------|
| `docs/inference-market-whitepaper.md` | This paper |
| `docs/inference-mining-plan.md` | Epochs, emission, operator runbook |
| `python/examples/showcase/90_inference_market.aicl` | Normative spec compiled toward Rust / chain |
