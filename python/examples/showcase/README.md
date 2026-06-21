# Showcase examples

These 20 programs are the curated public gallery of architectural demos.
The full dataset of 151 AX-powered algorithm scripts is in
[`../../aicl_dataset/`](../../aicl_dataset/).

## Reference programs (Levels 1–9)

| File | Levels | Domain |
|------|--------|--------|
| `01_blue_square.aicl` | 1 | Minimal graphics — the "hello world" of AICL |
| `02_pong.aicl` | 1–6 | Game with behaviours, conditions, events |
| `03_chat.aicl` | 1–9 | Full chat application |
| `04_chess.aicl` | 1–9 | Complex state machine |

## Domain showcase

| File | Domain |
|------|--------|
| `05_banking.aicl` | Fintech — accounts, loans, fraud detection |
| `10_smart_contract.aicl` | Blockchain |
| `16_microservices.aicl` | Distributed systems |
| `25_hexagonal_arch.aicl` | Software architecture (ports & adapters) |
| `26_distributed_consensus.aicl` | Distributed systems (Raft-style) |
| `33_container_orchestrator.aicl` | Infrastructure (K8s-style) |
| `46_ml_pipeline.aicl` | Machine learning |
| `50_rl_agent.aicl` | Reinforcement learning |
| `51_llm_gateway.aicl` | LLM orchestration |
| `55_autonomous_agent.aicl` | Autonomous systems |
| `56_iot_sensor_network.aicl` | IoT |
| `63_autonomous_vehicle.aicl` | Robotics |
| `66_mmo_server.aicl` | Gaming |
| `76_hospital_mgmt.aicl` | Healthcare |
| `82_smart_grid.aicl` | Energy |
| `84_rideshare.aicl` | Transport |

## CogNet integration specs (`cognet/`)

Six AICL programs that collectively specify the upcoming bidirectional
bridge between AICL and the CogNet cognitive engine. See
[`../../docs/cognet_integration_plan.md`](../../docs/cognet_integration_plan.md)
for the rollout plan.

| File | Purpose |
|------|---------|
| `86_cognet_aicl_bridge.aicl` | Bridge protocol — AICL ↔ CogNet cognitive graph |
| `87_cognet_self_evolution.aicl` | CogNet as AICL's self-modification utility |
| `88_cognet_self_evolution_free.aicl` | Free / uncensored variant of 87 |
| `89_cognet_training_pipeline.aicl` | Training pipeline for CogNet on AICL specs |
| `90_cognet_evaluation.aicl` | Evaluation harness |
| `91_cognet_autonomous_deployment.aicl` | End-to-end autonomous deployment loop |

## Websocket example (`websocket/`)

| File | Purpose |
|------|---------|
| `websocket/server.ts` | Reference Node server for reactive AICL programs |
| `websocket/frontend.tsx` | Reference React frontend |
