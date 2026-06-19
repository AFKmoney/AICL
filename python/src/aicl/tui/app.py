#!/usr/bin/env python3
"""
AICL TUI — Interactive Terminal Interface v3.0
Style: Claude Code — chat-driven, command palette, intuitive navigation
Features: 85 categorized examples, guided tutorials, LLM chat (ONNX/GGUF)

Usage: aicl tui
"""

import os
import sys
import time
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Optional

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical, VerticalScroll
    from textual.widgets import (
        Header, Footer, Static, Input, Button, Tree,
        DataTable, TabbedContent, TabPane, RichLog, DirectoryTree,
        Label, Select, TextArea
    )
    from textual.widgets.tree import TreeNode
    from textual.reactive import reactive
    from textual import work
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.panel import Panel
    from rich.table import Table as RichTable
    from rich import box
except ImportError:
    print("AICL TUI requires 'textual' and 'rich'. Install with: pip install textual rich")
    sys.exit(1)

# Import AICL compiler — adapt to the real API
try:
    from aicl.compiler import Compiler
    from aicl.spec_verify import verify_source
    from aicl.auto_optimizer import ArchitectureOptimizer
    from aicl.runtime import RuntimeEnvironment


    class AICLCompiler:
        """Thin wrapper adapting the real Compiler to the TUI's expected API.

        The TUI calls compiler.compile(filepath, target=) and expects a dict;
        the real Compiler.compile(source_str) returns a CompilationResult.
        This bridges the two.
        """
        def compile(self, filepath: str, target: str = "python") -> dict:
            with open(filepath) as f:
                source = f.read()
            import tempfile
            c = Compiler(target_language=target)
            result = c.compile(source)
            return {
                "success": result.success,
                "output_dir": "",
                "audit_coverage": (result.provenance.compute_audit_coverage()["audit_coverage"]
                                   if result.provenance else 0.0),
                "todos_remaining": result.todo_count,
                "proof_valid": (result.proof.verify()["valid"] if result.proof else False),
                "ax_behaviors": list(result.ax_sources.keys()) if hasattr(result, "ax_sources") else [],
            }

        def parse(self, filepath: str):
            with open(filepath) as f:
                source = f.read()
            from aicl.parser import Parser
            return Parser(source).parse()

        def get_architecture_tree(self, filepath: str) -> str:
            program = self.parse(filepath)
            lines = []
            for g in program.goals:
                lines.append(f"Goal: {g.description}")
            for l in program.layers:
                lines.append(f"Layer: {l.name}")
                for s in l.sublayers:
                    lines.append(f"  └── {s.name}")
            for b in program.behaviors:
                lines.append(f"Behavior: {b.name}")
            return "\n".join(lines)


    class ProvenanceTracker:
        """Stub — provenance is now handled by Compiler internally."""
        pass


    class OwnershipModel:
        """Stub — ownership analysis is handled by ArchitectureOptimizer."""
        pass
    from aicl.crypto_signing import create_signed_proof, verify_signed_proof
    from aicl import __version__ as AICL_VERSION
except ImportError:
    AICL_VERSION = "2.0.0"

# Optional LLM imports
_ONNX_AVAILABLE = False
_LLAMA_AVAILABLE = False
try:
    import onnxruntime as ort
    _ONNX_AVAILABLE = True
except ImportError:
    pass
try:
    from llama_cpp import Llama
    _LLAMA_AVAILABLE = True
except ImportError:
    pass


# ──────────────────────────────────────────────────────────────
# Syntax highlighting for AICL
# ──────────────────────────────────────────────────────────────
AICL_KEYWORDS = [
    "Goal", "Layer", "Sublayer", "SubLayer", "Validation", "Risk", "Recovery",
    "Constraint", "Entity", "Behavior", "Input", "Output", "Action",
    "Condition", "When", "Then", "Event", "On", "Parallel",
    "Optimize", "Priority", "Learn", "Adapt", "Based",
    "Security", "Encrypt", "Protect", "Native", "Import"
]

AICL_TYPES = [
    "string", "integer", "float", "boolean", "datetime",
    "list", "dict", "set", "any", "void", "bytes"
]


def highlight_aicl(source: str) -> Text:
    """Apply basic syntax highlighting to AICL source."""
    text = Text()
    for line in source.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            text.append(line, style="dim italic")
        elif any(stripped.startswith(kw + ":") or stripped.startswith(kw + " ") for kw in AICL_KEYWORDS):
            for kw in AICL_KEYWORDS:
                if stripped.startswith(kw + ":") or stripped.startswith(kw + " "):
                    indent = len(line) - len(stripped)
                    text.append(" " * indent)
                    text.append(kw, style="bold cyan")
                    rest = stripped[len(kw):]
                    if rest.startswith(":"):
                        text.append(":", style="bold cyan")
                        rest = rest[1:]
                    text.append(rest, style="white")
                    break
            else:
                text.append(line, style="white")
        elif any(stripped.startswith(t + " ") or stripped == t for t in AICL_TYPES):
            text.append(line, style="green")
        else:
            text.append(line, style="white")
        text.append("\n")
    return text


# ──────────────────────────────────────────────────────────────
# Example & Tutorial Registry
# ──────────────────────────────────────────────────────────────

EXAMPLE_CATEGORIES = {
    "basics": {
        "label": "Basics",
        "icon": "📐",
        "color": "blue",
        "files": ["01_blue_square.aicl", "02_pong.aicl", "03_chat.aicl", "04_chess.aicl", "05_banking.aicl"],
        "descriptions": {
            "01_blue_square.aicl": "Simple graphics — Level 1",
            "02_pong.aicl": "Pong game — Levels 1-6",
            "03_chat.aicl": "Chat app — Levels 1-9",
            "04_chess.aicl": "Chess game — Levels 1-9",
            "05_banking.aicl": "Banking system — All 10 levels",
        }
    },
    "crypto": {
        "label": "Crypto & Blockchain",
        "icon": "🔐",
        "color": "yellow",
        "files": [
            "06_blockchain_core.aicl", "07_crypto_wallet.aicl", "08_defi_platform.aicl",
            "09_nft_marketplace.aicl", "10_smart_contract.aicl", "11_pki_authority.aicl",
            "12_zkp_system.aicl", "13_key_management.aicl", "14_secure_messaging.aicl",
            "15_homomorphic_enc.aicl"
        ],
        "descriptions": {
            "06_blockchain_core.aicl": "PoW/PoS consensus, block validation, mempool",
            "07_crypto_wallet.aicl": "HD keys, transaction signing, UTXO, DeFi",
            "08_defi_platform.aicl": "AMM, liquidity pools, flash loans, governance",
            "09_nft_marketplace.aicl": "Minting, auctions, royalties, IPFS",
            "10_smart_contract.aicl": "Contract compilation, gas optimization, VM",
            "11_pki_authority.aicl": "X.509, OCSP, CRL, chain validation",
            "12_zkp_system.aicl": "Groth16/PLONK proofs, circuit compilation",
            "13_key_management.aicl": "HSM, key rotation, escrow, audit",
            "14_secure_messaging.aicl": "E2EE, X3DH, double ratchet, forward secrecy",
            "15_homomorphic_enc.aicl": "CKKS/BFV FHE, encrypted analytics, MPC",
        }
    },
    "patterns": {
        "label": "Design Patterns",
        "icon": "🏗️",
        "color": "magenta",
        "files": [
            "16_microservices.aicl", "17_cqrs_event_sourcing.aicl", "18_mvc_webapp.aicl",
            "19_observer_system.aicl", "20_repository_pattern.aicl", "21_strategy_engine.aicl",
            "22_factory_system.aicl", "23_decorator_pipeline.aicl", "24_plugin_architecture.aicl",
            "25_hexagonal_arch.aicl"
        ],
        "descriptions": {
            "16_microservices.aicl": "Service discovery, circuit breaker, saga",
            "17_cqrs_event_sourcing.aicl": "Command/query bus, event store, projections",
            "18_mvc_webapp.aicl": "Routing, controllers, views, middleware",
            "19_observer_system.aicl": "Pub/sub, backpressure, dead letter queue",
            "20_repository_pattern.aicl": "Abstract data access, unit of work, caching",
            "21_strategy_engine.aicl": "Algorithm selection, runtime switching",
            "22_factory_system.aicl": "Abstract factory, builder, DI container",
            "23_decorator_pipeline.aicl": "Middleware chain, cross-cutting concerns",
            "24_plugin_architecture.aicl": "Dynamic loading, sandboxing, hot reload",
            "25_hexagonal_arch.aicl": "Ports, adapters, domain core isolation",
        }
    },
    "distributed": {
        "label": "Distributed Systems",
        "icon": "☁️",
        "color": "cyan",
        "files": [
            "26_distributed_consensus.aicl", "27_service_mesh.aicl", "28_message_broker.aicl",
            "29_distributed_cache.aicl", "30_cdn_system.aicl", "31_load_balancer.aicl",
            "32_service_registry.aicl", "33_container_orchestrator.aicl",
            "34_serverless_platform.aicl", "35_multi_cloud_manager.aicl"
        ],
        "descriptions": {
            "26_distributed_consensus.aicl": "Raft protocol, leader election, log replication",
            "27_service_mesh.aicl": "Sidecar proxy, mTLS, traffic management",
            "28_message_broker.aicl": "Pub/sub, exactly-once, consumer groups",
            "29_distributed_cache.aicl": "Consistent hashing, replication, eviction",
            "30_cdn_system.aicl": "Edge caching, geo-routing, DDoS mitigation",
            "31_load_balancer.aicl": "L4/L7 balancing, health checks, SSL termination",
            "32_service_registry.aicl": "Health checking, DNS, multi-datacenter",
            "33_container_orchestrator.aicl": "Scheduling, scaling, rolling updates",
            "34_serverless_platform.aicl": "Function runtime, cold start, auto-scaling",
            "35_multi_cloud_manager.aicl": "Cloud abstraction, cost optimization, failover",
        }
    },
    "enterprise": {
        "label": "Enterprise & Business",
        "icon": "🏢",
        "color": "green",
        "files": [
            "36_erp_system.aicl", "37_crm_platform.aicl", "38_hr_management.aicl",
            "39_supply_chain.aicl", "40_fleet_management.aicl", "41_warehouse_mgmt.aicl",
            "42_insurance_claims.aicl", "43_tax_processing.aicl",
            "44_portfolio_mgmt.aicl", "45_algo_trading.aicl"
        ],
        "descriptions": {
            "36_erp_system.aicl": "Finance, procurement, manufacturing, HR modules",
            "37_crm_platform.aicl": "Sales pipeline, marketing automation, analytics",
            "38_hr_management.aicl": "Employee lifecycle, payroll, recruitment",
            "39_supply_chain.aicl": "Procurement, logistics, demand forecasting",
            "40_fleet_management.aicl": "Vehicle tracking, route optimization",
            "41_warehouse_mgmt.aicl": "Inventory, picking, packing, slotting",
            "42_insurance_claims.aicl": "Claims, fraud detection, payout",
            "43_tax_processing.aicl": "Tax calculation, filing, multi-jurisdiction",
            "44_portfolio_mgmt.aicl": "Asset allocation, risk analysis, rebalancing",
            "45_algo_trading.aicl": "Strategy engine, order management, backtesting",
        }
    },
    "aiml": {
        "label": "AI & Machine Learning",
        "icon": "🤖",
        "color": "bright_magenta",
        "files": [
            "46_ml_pipeline.aicl", "47_recommendation_engine.aicl", "48_nlp_system.aicl",
            "49_cv_pipeline.aicl", "50_rl_agent.aicl", "51_llm_gateway.aicl",
            "52_data_lakehouse.aicl", "53_feature_store.aicl",
            "54_mlops_platform.aicl", "55_autonomous_agent.aicl"
        ],
        "descriptions": {
            "46_ml_pipeline.aicl": "Training, evaluation, deployment, drift detection",
            "47_recommendation_engine.aicl": "Collaborative filtering, cold start, A/B testing",
            "48_nlp_system.aicl": "NER, sentiment, translation, summarization",
            "49_cv_pipeline.aicl": "Classification, detection, segmentation",
            "50_rl_agent.aicl": "Policy learning, reward shaping, multi-agent",
            "51_llm_gateway.aicl": "Model routing, prompt management, rate limiting",
            "52_data_lakehouse.aicl": "Batch/streaming, schema evolution, ACID",
            "53_feature_store.aicl": "Online/offline serving, point-in-time correctness",
            "54_mlops_platform.aicl": "Experiment tracking, model registry, CI/CD for ML",
            "55_autonomous_agent.aicl": "Planning, tool use, memory, self-reflection",
        }
    },
    "iot": {
        "label": "IoT & Real-Time",
        "icon": "📡",
        "color": "bright_cyan",
        "files": [
            "56_iot_sensor_network.aicl", "57_smart_home_hub.aicl", "58_realtime_analytics.aicl",
            "59_streaming_pipeline.aicl", "60_telemetry_system.aicl", "61_edge_computing.aicl",
            "62_industrial_iot.aicl", "63_autonomous_vehicle.aicl",
            "64_drone_fleet.aicl", "65_robotics_controller.aicl"
        ],
        "descriptions": {
            "56_iot_sensor_network.aicl": "Device management, edge processing, OTA",
            "57_smart_home_hub.aicl": "Automation, voice assistant, energy",
            "58_realtime_analytics.aicl": "Stream processing, anomaly detection",
            "59_streaming_pipeline.aicl": "Exactly-once, schema registry, watermarking",
            "60_telemetry_system.aicl": "Metrics, tracing, logging, alerting",
            "61_edge_computing.aicl": "Workload offloading, edge model deployment",
            "62_industrial_iot.aicl": "SCADA, predictive maintenance, digital twin",
            "63_autonomous_vehicle.aicl": "Perception, planning, V2X, safety",
            "64_drone_fleet.aicl": "Flight planning, swarm, compliance",
            "65_robotics_controller.aicl": "Motion planning, sensor fusion, IK",
        }
    },
    "gaming": {
        "label": "Gaming & Media",
        "icon": "🎮",
        "color": "bright_green",
        "files": [
            "66_mmo_server.aicl", "67_matchmaking_system.aicl", "68_game_economy.aicl",
            "69_leaderboard_system.aicl", "70_video_streaming.aicl", "71_music_streaming.aicl",
            "72_social_media.aicl", "73_content_cms.aicl",
            "74_live_auction.aicl", "75_podcast_platform.aicl"
        ],
        "descriptions": {
            "66_mmo_server.aicl": "World management, combat, guilds, sharding",
            "67_matchmaking_system.aicl": "ELO rating, queue management, parties",
            "68_game_economy.aicl": "Currency, trading, auction house, crafting",
            "69_leaderboard_system.aicl": "Rankings, seasonal resets, anti-cheat",
            "70_video_streaming.aicl": "Transcoding, ABR, CDN, DRM, live",
            "71_music_streaming.aicl": "Audio processing, playlists, licensing",
            "72_social_media.aicl": "Feeds, moderation, graph storage, privacy",
            "73_content_cms.aicl": "Authoring, workflow, versioning, SEO",
            "74_live_auction.aicl": "Real-time bidding, anti-sniping, escrow",
            "75_podcast_platform.aicl": "RSS, transcription, ad insertion, discovery",
        }
    },
    "specialized": {
        "label": "Healthcare, Education, Energy & Transport",
        "icon": "🏥",
        "color": "bright_yellow",
        "files": [
            "76_hospital_mgmt.aicl", "77_ehr_system.aicl", "78_telemedicine.aicl",
            "79_clinical_trials.aicl", "80_lms_platform.aicl", "81_exam_system.aicl",
            "82_smart_grid.aicl", "83_energy_trading.aicl",
            "84_rideshare.aicl", "85_flight_booking.aicl"
        ],
        "descriptions": {
            "76_hospital_mgmt.aicl": "Patient records, appointments, billing, pharmacy",
            "77_ehr_system.aicl": "FHIR, interoperability, clinical workflows",
            "78_telemedicine.aicl": "Video consults, scheduling, remote monitoring",
            "79_clinical_trials.aicl": "Protocol design, enrollment, adverse events",
            "80_lms_platform.aicl": "Courses, assessments, progress, certificates",
            "81_exam_system.aicl": "Question bank, proctoring, auto-grading",
            "82_smart_grid.aicl": "Demand response, renewables, outage management",
            "83_energy_trading.aicl": "Spot/futures, settlement, grid balancing",
            "84_rideshare.aicl": "Driver matching, surge pricing, safety",
            "85_flight_booking.aicl": "Search/booking, seat management, loyalty",
        }
    },
}

# ──────────────────────────────────────────────────────────────
# Tutorial System
# ──────────────────────────────────────────────────────────────

TUTORIALS = {
    "1": {
        "title": "AICL Basics — Your First Specification",
        "level": "Beginner",
        "duration": "5 min",
        "description": "Learn the three mandatory elements of every AICL program: Goal, Layer, and Validation.",
        "steps": [
            "Every AICL program starts with a Goal: — this declares WHAT you want to build.",
            "Next, define your architectural layers with Layer: — these are the building blocks.",
            "Finally, add Validation: — this is how the compiler knows when it's done right.",
            "These three keywords are the MINIMUM valid AICL program. Try compiling it with :compile!",
            "💡 AICL compiles your specification into real Python code + tests + a Proof of Origin.",
        ],
        "template": "# Tutorial 1: AICL Basics\n# Learn Goal, Layer, and Validation\n\nGoal:\nDisplay a greeting message on screen\n\nLayer:\nApplication\n\nValidation:\nGreeting is displayed correctly\n",
    },
    "2": {
        "title": "Risk & Recovery — Failure is Not Optional",
        "level": "Beginner",
        "duration": "8 min",
        "description": "Learn the most important AICL concept: every Risk MUST have a Recovery. No exceptions.",
        "steps": [
            "In AICL, Risk: is a mandatory language element, not an afterthought.",
            "Every Risk: MUST be followed by a Recovery: — this is enforced by the compiler.",
            "Think of real failures that could happen: network drops, data corruption, timeouts...",
            "The compiler generates error handling code from your Risk/Recovery pairs automatically.",
            "💡 If a Risk has no Recovery, the compiler will warn you. In strict mode, it will fail.",
        ],
        "template": "# Tutorial 2: Risk & Recovery\n# Every Risk MUST have a Recovery\n\nGoal:\nRead and process a configuration file\n\nConstraint:\nMust handle missing or corrupted files gracefully\n\nLayer:\nConfiguration\n\nRisk:\nConfiguration file not found\n\nRecovery:\nLoad default configuration and log warning\n\nRisk:\nConfiguration file is corrupted\n\nRecovery:\nValidate schema and repair with defaults for missing fields\n\nValidation:\nApplication starts with valid configuration\n\nValidation:\nDefault config is used when file is missing\n",
    },
    "3": {
        "title": "Entities & Behaviors — Data and Actions",
        "level": "Intermediate",
        "duration": "10 min",
        "description": "Define typed data entities and the behaviors that operate on them.",
        "steps": [
            "Entity defines a data structure with typed fields — like a class or struct.",
            "AICL types: string, integer, float, boolean, datetime, list, dict, set, bytes, any.",
            "Behavior defines what entities DO — with Input, Output, and Action.",
            "The compiler generates classes, methods, and tests from Entity and Behavior definitions.",
            "💡 Every Behavior becomes a method. Every Entity becomes a class. Every Action gets a provenance record.",
        ],
        "template": "# Tutorial 3: Entities & Behaviors\n# Define data and actions\n\nGoal:\nTask management system with assignments and deadlines\n\nLayer:\nTask Manager\n\nEntity Task\n    id: string\n    title: string\n    description: string\n    status: string\n    priority: integer\n    assigned_to: string\n    deadline: datetime\n\nEntity User\n    id: string\n    name: string\n    email: string\n    role: string\n\nBehavior CreateTask\n    Input: User title description priority\n    Output: Task\n    Action: create new task and assign to user\n\nBehavior CompleteTask\n    Input: Task\n    Output: boolean\n    Action: mark task as completed and notify assignee\n\nRisk:\nDuplicate task created\n\nRecovery:\nCheck for existing task with same title and merge if found\n\nValidation:\nTasks can be created and completed\n",
    },
    "4": {
        "title": "Conditions & Events — Reactive Architecture",
        "level": "Intermediate",
        "duration": "10 min",
        "description": "Use When/Then conditions and On/Action events for reactive, event-driven systems.",
        "steps": [
            "Condition: replaces if/else with declarative When/Then rules.",
            "The compiler decides HOW to implement the condition — you just declare WHAT should happen.",
            "Event: defines what happens when something occurs — On [event] → Action: [response].",
            "Events are the backbone of reactive architecture — think webhooks, signals, observers.",
            "💡 Conditions are evaluated continuously. Events fire once. Both generate provenance-tracked code.",
        ],
        "template": "# Tutorial 4: Conditions & Events\n# Reactive architecture with When/Then and On/Action\n\nGoal:\nSmart notification system with priority-based routing\n\nLayer:\nNotification Engine\n\nEntity Notification\n    id: string\n    type: string\n    priority: integer\n    message: string\n    recipient: string\n    created_at: datetime\n\nBehavior SendNotification\n    Input: Notification\n    Output: boolean\n    Action: deliver notification through appropriate channel\n\nCondition:\nWhen notification priority is critical\nThen send through all channels immediately and alert on-call team\n\nCondition:\nWhen recipient has do-not-disturb enabled\nThen queue notification for later delivery unless critical\n\nEvent:\nOn notification delivery failed\nAction: retry with exponential backoff and log failure for audit\n\nEvent:\nOn critical notification received\nAction: escalate to on-call team and page primary responder\n\nRisk:\nNotification channel unavailable\n\nRecovery:\nFall back to alternative channel and queue for retry\n\nValidation:\nNotifications delivered to correct channels\n",
    },
    "5": {
        "title": "Concurrency, Optimization & Learning",
        "level": "Advanced",
        "duration": "12 min",
        "description": "Use Parallel for concurrency, Optimize for performance, and Learn/Adapt for adaptive systems.",
        "steps": [
            "Parallel: tells the compiler which layers can run concurrently — it decides the threading strategy.",
            "Optimize: declares performance targets. Priority: resolves conflicts between targets.",
            "Learn: defines what the system should learn. Adapt: defines what should change based on learning.",
            "These levels make AICL programs adaptive — the generated code improves over time.",
            "💡 The compiler generates concurrent execution, optimization hints, and ML integration scaffolding.",
        ],
        "template": "# Tutorial 5: Concurrency, Optimization & Learning\n# Build an adaptive, high-performance system\n\nGoal:\nReal-time data processing pipeline with adaptive optimization\n\nConstraint:\nProcessing latency must not exceed 100ms\n\nLayer:\nData Ingestion\nLayer:\nProcessing Engine\nLayer:\nOutput Stream\n\nEntity DataPoint\n    id: string\n    value: float\n    source: string\n    timestamp: datetime\n\nBehavior ProcessData\n    Input: DataPoint\n    Output: DataPoint\n    Action: validate and transform data point\n\nParallel:\nData Ingestion\nProcessing Engine\nOutput Stream\n\nOptimize:\nProcessing throughput\n\nOptimize:\nEnd-to-end latency\n\nPriority:\nLatency over throughput\n\nLearn:\nData processing patterns\n\nGoal:\n    identify bottlenecks and optimize processing paths\n\nAdapt:\nProcessing batch size\n\nBased on:\n    current throughput and latency measurements\n\nRisk:\nProcessing queue overflow\n\nRecovery:\nEnable backpressure and shed low-priority data points\n\nValidation:\nData processed within 100ms latency\n",
    },
    "6": {
        "title": "Security & Native Code — Full Power",
        "level": "Advanced",
        "duration": "12 min",
        "description": "Use Security for encryption/protection directives and Native for inline code in any language.",
        "steps": [
            "Security: defines what must be encrypted (Encrypt:) and what must be protected (Protect:).",
            "Encrypt: is for data at rest and in transit — the compiler generates encryption logic.",
            "Protect: is for access control and integrity — the compiler generates authorization checks.",
            "Native: is the escape hatch — inline code in Python, Rust, JavaScript, Go, C++, etc.",
            "💡 Native code is the ONLY way to write implementation details in AICL. Everything else is specification.",
        ],
        "template": "# Tutorial 6: Security & Native Code\n# Encryption, protection, and native implementations\n\nGoal:\nSecure document vault with encryption and access control\n\nConstraint:\nAll documents must be encrypted at rest with AES-256\n\nConstraint:\nAccess logs must be immutable and retained for 5 years\n\nLayer:\nDocument Store\nLayer:\nAccess Control\nLayer:\nAudit Trail\n\nEntity Document\n    id: string\n    title: string\n    content: bytes\n    owner: string\n    classification: string\n    created_at: datetime\n\nEntity AccessLog\n    id: string\n    user: string\n    document: string\n    action: string\n    timestamp: datetime\n\nBehavior StoreDocument\n    Input: Document\n    Output: string\n    Action: encrypt and store document with access control\n\nSecurity:\n    Encrypt: document content and metadata\n    Encrypt: access credentials and API keys\n    Protect: audit trail integrity\n    Protect: document access permissions\n\nNative: python\n{{\nimport hashlib\nfrom cryptography.fernet import Fernet\n\ndef generate_key() -> bytes:\n    return Fernet.generate_key()\n\ndef encrypt_content(content: bytes, key: bytes) -> bytes:\n    f = Fernet(key)\n    return f.encrypt(content)\n\ndef decrypt_content(encrypted: bytes, key: bytes) -> bytes:\n    f = Fernet(key)\n    return f.decrypt(encrypted)\n}}\n\nRisk:\nEncryption key compromised\n\nRecovery:\nRotate keys immediately and re-encrypt all documents\n\nValidation:\nDocuments are encrypted at rest\n\nValidation:\nAccess log is immutable\n",
    },
    "7": {
        "title": "Full Application — All 10 Levels",
        "level": "Expert",
        "duration": "20 min",
        "description": "Build a complete application using all 10 AICL language levels.",
        "steps": [
            "Level 1 (Architecture): Goal, Constraint, Risk/Recovery, Layer, Validation — the foundation.",
            "Level 2 (Entities): Define your data structures with typed fields.",
            "Level 3 (Behaviors): Define what your entities DO with Input/Output/Action.",
            "Level 4 (Conditions): Replace if/else with When/Then declarative rules.",
            "Level 5 (Events): Define reactive behavior with On/Action pairs.",
            "Level 6 (Concurrency): Declare parallel execution with Parallel:.",
            "Level 7 (Optimization): Set performance targets with Optimize:/Priority:.",
            "Level 8 (Learning): Make your system adaptive with Learn:/Adapt:/Based:.",
            "Level 9 (Security): Enforce encryption and protection with Encrypt:/Protect:.",
            "Level 10 (Native): Add implementation details with Native: code blocks.",
        ],
        "template": "# Tutorial 7: Full Application — All 10 Levels\n# A complete order management system\n\nGoal:\nCreate an order management system with inventory tracking, payment processing, fraud detection, and adaptive pricing\n\nConstraint:\nAll payments must be PCI-DSS compliant\n\nConstraint:\nOrder processing must complete within 5 seconds\n\nRisk:\nPayment gateway unavailable\n\nRecovery:\nQueue payment for retry and notify customer of delay\n\nRisk:\nInsufficient inventory for order\n\nRecovery:\nBackorder items and notify customer of expected ship date\n\nRisk:\nFraudulent order detected\n\nRecovery:\nSuspend order and escalate to fraud review team\n\nLayer:\nOrder Service\n    SubLayer:\n    Order placement\n    SubLayer:\n    Order tracking\n\nLayer:\nInventory\n    SubLayer:\n    Stock management\n    SubLayer:\n    Reorder logic\n\nLayer:\nPayment\n    SubLayer:\n    Processing\n    SubLayer:\n    Refunds\n\nEntity Order\n    order_id: string\n    customer_id: string\n    items: list\n    total: float\n    status: string\n    created_at: datetime\n\nEntity InventoryItem\n    sku: string\n    name: string\n    quantity: integer\n    reorder_level: integer\n\nBehavior PlaceOrder\n    Input: Order\n    Output: string\n    Action: validate inventory and process payment and create order\n\nCondition:\nWhen inventory below reorder level\n\nThen trigger automatic reorder from supplier\n\nEvent:\nOn order completed\n\nAction: update inventory and send confirmation and record audit entry\n\nParallel:\nOrder Service\nInventory\nPayment\n\nOptimize:\nOrder processing speed\n\nPriority:\nPayment security over processing speed\n\nLearn:\nCustomer ordering patterns\n\nGoal:\n    predict demand and optimize inventory levels\n\nAdapt:\nPricing strategy\n\nBased on:\n    demand patterns and inventory levels\n\nSecurity:\n    Encrypt: payment card data\n    Encrypt: customer personal information\n    Protect: order audit trail\n\nNative: python\n{{\nimport hashlib\nimport time\n\ndef generate_order_id():\n    ts = str(int(time.time() * 1000))\n    h = hashlib.sha256(ts.encode()).hexdigest()[:6]\n    return f\"ORD-{ts[-8:]}-{h}\"\n}}\n\nValidation:\nOrders placed and processed correctly\n\nValidation:\nInventory updated after each order\n\nValidation:\nFraudulent orders flagged for review\n\nValidation:\nPayments processed securely\n",
    },
}


# ──────────────────────────────────────────────────────────────
# LLM Interface
# ──────────────────────────────────────────────────────────────

AICL_SYSTEM_PROMPT = """You are an AICL (Artificial Intelligence-Centered Language) expert assistant. AICL is a specification-first programming language with 10 levels and 27 keywords:

Level 1 - Architecture: Goal, Constraint, Risk/Recovery, Layer/SubLayer, Validation
Level 2 - Entities: Entity with typed fields
Level 3 - Behaviors: Behavior with Input/Output/Action
Level 4 - Conditions: When/Then rules
Level 5 - Events: On/Action handlers
Level 6 - Concurrency: Parallel execution
Level 7 - Optimization: Optimize/Priority targets
Level 8 - Learning: Learn/Adapt/Based adaptive behavior
Level 9 - Security: Encrypt/Protect directives
Level 10 - Native: Inline code in any language

AX SUB-LANGUAGE: Behavior Action sections can use AX, a Turing-complete
sub-language with if/elif/else, while, for, recursion, arithmetic, list
operations, method calls, and tuple swaps. AX compiles to real executable
code in Python, Rust, JavaScript, and Go — no stubs.

KEY RULES:
- Every Risk MUST have a Recovery
- Validation sections generate tests automatically
- The compiler produces code + Proof of Origin (cryptographic sidecar)
- Provenance is tracked for every generated artifact
- AX behaviors compile to 4 targets with type inference (arrays, ints)

Help the user write, understand, debug, and improve AICL specifications. Provide concrete code examples. If they describe a system, generate the AICL specification for it."""


class LLMInterface:
    """Interface for local LLM models (ONNX and GGUF formats)."""

    def __init__(self):
        self.model = None
        self.model_path: Optional[str] = None
        self.model_type: Optional[str] = None  # "onnx" or "gguf"
        self.tokenizer = None
        self.onnx_session = None

    @property
    def is_loaded(self) -> bool:
        return self.model is not None or self.onnx_session is not None

    @property
    def model_info(self) -> str:
        if not self.is_loaded:
            return "No model loaded"
        type_label = "ONNX" if self.model_type == "onnx" else "GGUF"
        return f"{type_label}: {os.path.basename(self.model_path or '?')}"

    def load_model(self, path: str) -> str:
        """Load a model from a file path. Supports .onnx and .gguf formats."""
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            return f"Error: File not found: {path}"

        ext = os.path.splitext(path)[1].lower()

        if ext == ".onnx":
            return self._load_onnx(path)
        elif ext == ".gguf":
            return self._load_gguf(path)
        else:
            return f"Error: Unsupported format '{ext}'. Supported: .onnx, .gguf"

    def _load_onnx(self, path: str) -> str:
        if not _ONNX_AVAILABLE:
            return "Error: onnxruntime not installed. Run: pip install onnxruntime"
        try:
            self.onnx_session = ort.InferenceSession(path)
            self.model_path = path
            self.model_type = "onnx"
            self.model = None
            inputs = self.onnx_session.get_inputs()
            input_info = ", ".join(f"{i.name} ({i.shape})" for i in inputs)
            return f"ONNX model loaded: {os.path.basename(path)}\nInputs: {input_info}"
        except Exception as e:
            return f"Error loading ONNX model: {e}"

    def _load_gguf(self, path: str) -> str:
        if not _LLAMA_AVAILABLE:
            return "Error: llama-cpp-python not installed. Run: pip install llama-cpp-python"
        try:
            self.model = Llama(
                model_path=path,
                n_ctx=4096,
                n_gpu_layers=-1,  # Use all GPU layers if available
                verbose=False,
            )
            self.model_path = path
            self.model_type = "gguf"
            self.onnx_session = None
            return f"GGUF model loaded: {os.path.basename(path)}"
        except Exception as e:
            return f"Error loading GGUF model: {e}"

    def chat(self, message: str, history: list = None) -> str:
        """Generate a response from the loaded model."""
        if not self.is_loaded:
            return "No model loaded. Use :model load <path> to load an ONNX or GGUF model."

        if self.model_type == "gguf" and self.model is not None:
            return self._chat_gguf(message, history)
        elif self.model_type == "onnx" and self.onnx_session is not None:
            return self._chat_onnx(message, history)
        else:
            return "Model not properly initialized."

    def _chat_gguf(self, message: str, history: list = None) -> str:
        try:
            messages = [{"role": "system", "content": AICL_SYSTEM_PROMPT}]
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": message})

            response = self.model.create_chat_completion(
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=0.9,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"GGUF inference error: {e}"

    def _chat_onnx(self, message: str, history: list = None) -> str:
        try:
            # ONNX models are typically encoder-decoder or encoder-only
            # For text generation ONNX models, we need to handle tokenization
            if self.onnx_session is None:
                return "ONNX session not initialized."

            # Basic approach: try to use the model with simple input
            inputs = self.onnx_session.get_inputs()
            input_name = inputs[0].name

            # Attempt tokenization with a simple approach
            # For proper ONNX text generation, a tokenizer model is needed
            prompt = f"System: {AICL_SYSTEM_PROMPT}\n\nUser: {message}\n\nAssistant:"

            # Try to use tokenizer if available
            try:
                from transformers import AutoTokenizer
                if not self.tokenizer:
                    # Try to find tokenizer in same directory
                    model_dir = os.path.dirname(self.model_path or "")
                    self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
                tokens = self.tokenizer.encode(prompt, return_tensors="np")
            except (ImportError, Exception):
                # Fallback: character-level encoding (very basic)
                import numpy as np
                tokens = np.array([[ord(c) for c in prompt[:512]]], dtype=np.int64)

            outputs = self.onnx_session.run(None, {input_name: tokens})

            # Try to decode output
            try:
                import numpy as np
                output_ids = np.argmax(outputs[0], axis=-1)
                if self.tokenizer:
                    return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
                else:
                    # Fallback: try character decoding
                    chars = [chr(int(i)) if 32 <= int(i) < 127 else '' for i in output_ids[0]]
                    return ''.join(chars)
            except Exception:
                return f"ONNX model output received but decoding not available. Output shape: {outputs[0].shape}"

        except Exception as e:
            return f"ONNX inference error: {e}"

    def unload(self) -> str:
        """Unload the current model to free memory."""
        self.model = None
        self.onnx_session = None
        self.tokenizer = None
        path = self.model_path
        self.model_path = None
        self.model_type = None
        return f"Model unloaded: {os.path.basename(path or '?')}"


# ──────────────────────────────────────────────────────────────
# Welcome screen
# ──────────────────────────────────────────────────────────────
WELCOME = f"""[bold cyan]AICL TUI v{AICL_VERSION}[/] — Artificial Intelligence-Centered Language

[dim]If the compiler cannot explain why it generated a line, it should not generate it.[/]

[bold]Quick Commands:[/]
  [cyan]:help[/]       — Show all commands
  [cyan]:compile[/]    — Compile current file
  [cyan]:verify[/]     — Verify specification
  [cyan]:audit[/]      — Audit compilation
  [cyan]:proof[/]      — View Proof of Origin
  [cyan]:explain[/]    — Explain provenance
  [cyan]:tree[/]       — Architecture tree
  [cyan]:optimize[/]   — Optimize architecture
  [cyan]:examples[/]   — Browse 85 categorized examples
  [cyan]:tutorial[/]   — Start a guided tutorial
  [cyan]:chat[/]       — Chat with LLM assistant
  [cyan]:model[/]      — Manage local LLM models

[bold]Keyboard:[/]
  [cyan]Ctrl+O[/] Open file    [cyan]Ctrl+S[/] Save    [cyan]Ctrl+Q[/] Quit
  [cyan]Ctrl+K[/] Command palette    [cyan]Ctrl+E[/] Toggle sidebar

[dim]Type a command or start writing AICL code below.[/]
"""

# Plain-text version for TextArea (no rich markup)
WELCOME_PLAIN = f"""AICL TUI v{AICL_VERSION} — Artificial Intelligence-Centered Language

If the compiler cannot explain why it generated a line, it should not generate it.

Quick Commands:
  :help       — Show all commands
  :compile    — Compile current file (try :compile rust for 4-target support)
  :verify     — Verify specification
  :audit      — Audit compilation
  :targets    — List compile targets
  :tutorial   — Start a guided tutorial (including AX)
  :chat       — Chat with LLM assistant

Keyboard:
  Ctrl+O Open file    Ctrl+S Save    Ctrl+Q Quit
  Ctrl+K Command palette    Ctrl+E Toggle sidebar

Type a command or start writing AICL code below.
"""


# ──────────────────────────────────────────────────────────────
# Main TUI Application
# ──────────────────────────────────────────────────────────────
class AICLTUI(App):
    """AICL Interactive Terminal Interface v3.0."""

    TITLE = f"AICL TUI v{AICL_VERSION}"

    CSS = """
    Screen {
        background: #0d1117;
    }

    #main-container {
        layout: horizontal;
        height: 100%;
    }

    #sidebar {
        width: 28;
        dock: left;
        background: #161b22;
        border-right: solid #30363d;
    }

    #sidebar-header {
        background: #1f2937;
        padding: 1;
        height: 3;
        border-bottom: solid #30363d;
    }

    #sidebar-header Label {
        color: #58a6ff;
        text-style: bold;
    }

    #editor-area {
        width: 1fr;
    }

    #editor-tabs {
        height: 3;
        background: #161b22;
        border-bottom: solid #30363d;
    }

    #editor-content {
        height: 1fr;
        border: solid #30363d;
    }

    TextArea {
        background: #0d1117;
        color: #c9d1d9;
    }

    .editor-textarea {
        height: 1fr;
    }

    #output-panel {
        height: 14;
        background: #0d1117;
        border-top: solid #30363d;
    }

    #command-input {
        dock: bottom;
        height: 3;
        background: #161b22;
        border-top: solid #30363d;
    }

    #command-input Input {
        background: #0d1117;
        border: solid #30363d;
        color: #c9d1d9;
    }

    #command-input Input:focus {
        border: solid #58a6ff;
    }

    .file-tree {
        background: #161b22;
        color: #8b949e;
        padding: 0;
    }

    RichLog {
        background: #0d1117;
        color: #c9d1d9;
        padding: 0 1;
        scrollbar-size: 1 1;
    }

    .editor-log {
        background: #0d1117;
        color: #c9d1d9;
        padding: 0 1;
    }

    Static {
        color: #c9d1d9;
    }

    .status-bar {
        background: #161b22;
        color: #8b949e;
        padding: 0 1;
    }

    .chat-mode #command-input Input {
        border: solid #f0883e;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=False),
        Binding("ctrl+o", "open_file", "Open", show=False),
        Binding("ctrl+s", "save_file", "Save", show=False),
        Binding("ctrl+k", "command_palette", "Commands", show=False),
        Binding("ctrl+e", "toggle_sidebar", "Sidebar", show=False),
    ]

    current_file: reactive[str] = reactive("")
    compiler: Optional[AICLCompiler] = None
    last_output_dir: str = ""
    chat_mode: bool = False
    chat_history: list = []
    llm: LLMInterface = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-container"):
            # Sidebar
            with Vertical(id="sidebar"):
                with Vertical(id="sidebar-header"):
                    yield Label("AICL Explorer")
                yield DirectoryTree(os.getcwd(), id="file-tree", classes="file-tree")

            # Main area
            with Vertical(id="editor-area"):
                with Horizontal(id="editor-tabs"):
                    yield Static(" untitled.aicl ", id="tab-label", classes="status-bar")
                yield TextArea(
                    "",
                    id="editor-content",
                    language="python",  # closest built-in for AX; custom theme below
                    theme="monokai",
                    soft_wrap=True,
                    tab_behavior="indent",
                    show_line_numbers=True,
                    classes="editor-textarea",
                )
                with Vertical(id="output-panel"):
                    yield RichLog(id="output-log", highlight=True, markup=True)

        # Command input
        with Horizontal(id="command-input"):
            yield Input(placeholder="Type a command or AICL code... (type :help for commands)", id="cmd")

        yield Footer()

    def on_mount(self) -> None:
        # Load welcome text into the TextArea editor
        ta = self.query_one("#editor-content", TextArea)
        ta.text = WELCOME_PLAIN
        self.query_one("#cmd", Input).focus()
        self.compiler = AICLCompiler()
        self.llm = LLMInterface()

        # Load example on start. Try the showcase path first, then a flat
        # examples/ dir (legacy), then a relative path (for development).
        candidates = [
            Path(__file__).parent.parent.parent.parent / "examples" / "showcase" / "01_blue_square.aicl",
            Path(__file__).parent.parent.parent.parent / "examples" / "01_blue_square.aicl",
            Path("examples/showcase/01_blue_square.aicl"),
            Path("examples/01_blue_square.aicl"),
        ]
        for example_path in candidates:
            if example_path.exists():
                self._load_file(str(example_path))
                break

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if not cmd:
            return

        input_widget = self.query_one("#cmd", Input)
        input_widget.value = ""

        output = self.query_one("#output-log", RichLog)
        editor = self.query_one("#editor-content", TextArea)

        # Chat mode: send everything to LLM
        if self.chat_mode and not cmd.startswith(":"):
            output.write(f"[bold bright_yellow]You:[/] {cmd}")
            response = self.llm.chat(cmd, self.chat_history)
            self.chat_history.append({"role": "user", "content": cmd})
            self.chat_history.append({"role": "assistant", "content": response})
            output.write(f"[bold bright_green]AICL AI:[/] {response}")
            return

        # Log command
        output.write(f"[bold cyan]>>>[/] {cmd}")

        if cmd.startswith(":"):
            self._handle_command(cmd[1:], output, editor)
        elif cmd.startswith("Goal") or cmd.startswith("Layer") or cmd.startswith("#") or cmd.startswith("Entity") or cmd.startswith("Behavior") or cmd.startswith("Constraint") or cmd.startswith("Risk"):
            # AICL code — append to the TextArea editor
            ta = self.query_one("#editor-content", TextArea)
            if ta.text and not ta.text.endswith("\n"):
                ta.text += "\n"
            ta.text += cmd + "\n"
            output.write("[dim]Code added to editor. Use :save to save or :compile to compile.[/]")
        else:
            output.write(f"[yellow]Unknown input. Type :help for commands.[/]")

    def _handle_command(self, cmd: str, output: RichLog, editor) -> None:
        """Handle colon-prefixed commands."""
        parts = cmd.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        commands = {
            "help": self._cmd_help,
            "compile": self._cmd_compile,
            "verify": self._cmd_verify,
            "audit": self._cmd_audit,
            "proof": self._cmd_proof,
            "explain": self._cmd_explain,
            "tree": self._cmd_tree,
            "optimize": self._cmd_optimize,
            "run": self._cmd_run,
            "clear": self._cmd_clear,
            "examples": self._cmd_examples,
            "tutorial": self._cmd_tutorial,
            "exercise": self._cmd_tutorial,
            "open": self._cmd_open,
            "save": self._cmd_save,
            "new": self._cmd_new,
            "targets": self._cmd_targets,
            "version": self._cmd_version,
            "ownership": self._cmd_ownership,
            "sign": self._cmd_sign,
            "verify-proof": self._cmd_verify_proof,
            "chat": self._cmd_chat,
            "model": self._cmd_model,
            "exit": self._cmd_exit_chat,
        }

        if command in commands:
            commands[command](args, output, editor)
        else:
            output.write(f"[red]Unknown command: :{command}[/]  Type [cyan]:help[/] for available commands.")

    # ── Help ─────────────────────────────────────────────────

    def _cmd_help(self, args, output, editor):
        help_text = f"""
[bold cyan]AICL TUI v{AICL_VERSION}[/] — Commands Reference

[bold]File Operations:[/]
  [cyan]:open <path>[/]       Open an AICL file
  [cyan]:save[/]              Save current file
  [cyan]:new[/]               Create new file

[bold]Compilation:[/]
  [cyan]:compile[/]           Compile current file (Python)
  [cyan]:compile rust[/]      Compile to Rust
  [cyan]:compile js[/]        Compile to JavaScript
  [cyan]:compile go[/]        Compile to Go
  [cyan]:targets[/]           List available targets

[bold]Verification:[/]
  [cyan]:verify[/]            Verify specification quality
  [cyan]:audit[/]             Audit compilation (needs :compile first)
  [cyan]:proof[/]             View Proof of Origin
  [cyan]:explain[/]           Explain compilation provenance
  [cyan]:verify-proof[/]      Verify proof with independent verifier

[bold]Architecture:[/]
  [cyan]:tree[/]              Show architecture tree
  [cyan]:optimize[/]          Optimize architecture
  [cyan]:ownership[/]         Show ownership model

[bold]Runtime:[/]
  [cyan]:run[/]               Run self-healing runtime

[bold]Security:[/]
  [cyan]:sign[/]              Cryptographically sign the proof

[bold]Examples & Tutorials:[/]
  [cyan]:examples[/]          Browse all 85 categorized examples
  [cyan]:examples crypto[/]   Filter examples by category
  [cyan]:tutorial[/]          Start a guided tutorial (7 levels)
  [cyan]:tutorial 1[/]        Start specific tutorial

[bold]LLM Chat Assistant:[/]
  [cyan]:chat[/]              Enter chat mode (talk to AI about AICL)
  [cyan]:exit[/]              Exit chat mode
  [cyan]:model load <path>[/] Load an ONNX or GGUF model
  [cyan]:model info[/]        Show loaded model info
  [cyan]:model unload[/]      Unload current model
  [cyan]:model scan <dir>[/]  Scan directory for models

[bold]Other:[/]
  [cyan]:clear[/]             Clear output panel
  [cyan]:version[/]           Show AICL version
"""
        output.write(help_text)

    # ── Compilation Commands ─────────────────────────────────

    def _cmd_compile(self, args, output, editor):
        # Read current editor content from the TextArea (not the file on disk,
        # so unsaved edits compile correctly)
        ta = self.query_one("#editor-content", TextArea)
        source = ta.text
        if not source.strip():
            output.write("[red]Editor is empty. Write some AICL code first.[/]")
            return

        arg = args.strip().lower()
        targets = ["python"]
        if arg in ("rust", "javascript", "js", "go"):
            targets = ["javascript" if arg == "js" else arg]
        elif arg in ("all", "4", "targets"):
            targets = ["python", "rust", "javascript", "go"]

        import tempfile
        # Write current editor content to a temp file for compilation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as tmp:
            tmp.write(source)
            tmp_path = tmp.name

        try:
            for target in targets:
                label = target.upper()
                output.write(f"[bold cyan]Compiling[/] → {label}...")
                try:
                    result = self.compiler.compile(tmp_path, target=target)
                    self.last_output_dir = result.get("output_dir", "")
                    coverage = result.get("audit_coverage", 0) * 100
                    todos = result.get("todos_remaining", 0)
                    valid = result.get("proof_valid", False)
                    status = "[green]VALID[/]" if valid else "[red]INVALID[/]"
                    ax_count = len(result.get("ax_behaviors", []))
                    ax_badge = f"  [magenta]AX: {ax_count} behavior(s) real code[/]" if ax_count else ""
                    output.write(f"""  [green]✓ {target}[/]{ax_badge}
    Output: {self.last_output_dir}  TODOs: {todos}  Audit: {coverage:.1f}%  Proof: {status}""")
                except Exception as e:
                    output.write(f"  [red]✗ {target}: {e}[/]")

            if len(targets) == 4:
                output.write("[bold green]All 4 targets compiled. AX behaviors produce real executable code.[/]")
        finally:
            os.unlink(tmp_path)

    def _cmd_verify(self, args, output, editor):
        if not self.current_file:
            output.write("[red]No file loaded. Use :open <path> first.[/]")
            return
        output.write("[bold]Verifying specification...[/]")
        try:
            with open(self.current_file) as f:
                source = f.read()
            result = verify_source(source)
            checks = result.get("checks", [])
            passed = sum(1 for c in checks if c.get("status") == "pass")
            failed = sum(1 for c in checks if c.get("status") == "fail")
            warned = sum(1 for c in checks if c.get("status") == "warn")
            overall = result.get("overall", "UNKNOWN")
            color = "green" if overall == "PASS" else "yellow" if overall == "WARN" else "red"
            output.write(f"[{color}]Overall: {overall}[/]  ({passed} passed, {warned} warnings, {failed} failed)")
            for check in checks:
                icon = {"pass": "[green]PASS[/]", "warn": "[yellow]WARN[/]", "fail": "[red]FAIL[/]"}
                status = icon.get(check["status"], check["status"])
                output.write(f"  {status}  {check.get('name', '')}")
        except Exception as e:
            output.write(f"[red]Verification failed:[/] {e}")

    def _cmd_audit(self, args, output, editor):
        if not self.last_output_dir:
            output.write("[red]Compile first with :compile[/]")
            return
        proof_path = os.path.join(self.last_output_dir, "main.aicl-proof")
        if not os.path.exists(proof_path):
            output.write(f"[red]Proof not found at {proof_path}[/]")
            return
        try:
            from aicl.compiler import AICLCompiler
            comp = AICLCompiler()
            result = comp.audit_proof(proof_path)
            output.write(f"""[bold]Audit Report[/]
  Artifacts:     {result.get('total_artifacts', 0)}
  With provenance: {result.get('artifacts_with_provenance', 0)}
  Orphans:       {result.get('orphan_count', 0)}
  Coverage:      {result.get('coverage', 0):.1f}%""")
        except Exception as e:
            output.write(f"[red]Audit failed:[/] {e}")

    def _cmd_proof(self, args, output, editor):
        if not self.last_output_dir:
            output.write("[red]Compile first with :compile[/]")
            return
        proof_path = os.path.join(self.last_output_dir, "main.aicl-proof")
        if not os.path.exists(proof_path):
            output.write("[red]Proof not found[/]")
            return
        try:
            with open(proof_path) as f:
                proof = json.load(f)
            output.write(f"""[bold cyan]Proof of Origin[/]
  Format:        v{proof.get('format_version', '?')}
  Compiler:      v{proof.get('compiler_version', '?')}
  Timestamp:     {proof.get('timestamp', '?')}
  Source hash:   {proof.get('source_hash', '?')[:24]}...
  Program hash:  {proof.get('program_hash', '?')[:24]}...
  Test hash:     {proof.get('test_hash', '?')[:24]}...
  Records:       {len(proof.get('records', []))}
  Artifacts:     {len(proof.get('artifacts', []))}""")
        except Exception as e:
            output.write(f"[red]Error reading proof:[/] {e}")

    def _cmd_explain(self, args, output, editor):
        if not self.last_output_dir:
            output.write("[red]Compile first with :compile[/]")
            return
        proof_path = os.path.join(self.last_output_dir, "main.aicl-proof")
        if not os.path.exists(proof_path):
            output.write("[red]Proof not found[/]")
            return
        try:
            from aicl.compiler import AICLCompiler
            comp = AICLCompiler()
            result = comp.explain_proof(proof_path)
            decisions = result.get("decisions", [])
            output.write(f"[bold]Provenance Explanation[/] ({len(decisions)} decisions)")
            for d in decisions[:10]:
                output.write(f"  [cyan]{d.get('type', '?')}[/] — {d.get('source', '?')[:60]}")
            if len(decisions) > 10:
                output.write(f"  ... and {len(decisions)-10} more")
        except Exception as e:
            output.write(f"[red]Explain failed:[/] {e}")

    def _cmd_tree(self, args, output, editor):
        if not self.current_file:
            output.write("[red]No file loaded.[/]")
            return
        try:
            result = self.compiler.parse(self.current_file)
            tree_str = self.compiler.get_architecture_tree(self.current_file)
            output.write(f"[bold cyan]Architecture Tree[/]\n{tree_str}")
        except Exception as e:
            output.write(f"[red]Tree failed:[/] {e}")

    def _cmd_optimize(self, args, output, editor):
        if not self.current_file:
            output.write("[red]No file loaded.[/]")
            return
        output.write("[bold]Optimizing architecture...[/]")
        try:
            optimizer = ArchitectureOptimizer()
            result = optimizer.optimize(self.current_file)
            actions = result.get("actions", [])
            score = result.get("improvement_score", 0)
            output.write(f"[bold]Optimization Report[/] (score: {score}%)")
            for i, action in enumerate(actions[:8], 1):
                name = action.get("type", "?")
                desc = action.get("description", "")[:70]
                risk = action.get("risk", "?")
                output.write(f"  [{i}] [cyan]{name}[/] (risk: {risk})\n      {desc}")
        except Exception as e:
            output.write(f"[red]Optimize failed:[/] {e}")

    def _cmd_run(self, args, output, editor):
        output.write("[bold]Self-Healing Runtime[/]")
        output.write("[dim]Runtime environment initialized. Register risk/recovery pairs in your AICL source.[/]")
        try:
            env = RuntimeEnvironment()
            output.write("  RuntimeEnvironment created successfully")
            output.write("  Use :compile first, then import and run the generated application")
        except Exception as e:
            output.write(f"[red]Runtime error:[/] {e}")

    def _cmd_clear(self, args, output, editor):
        output.clear()

    # ── Examples ─────────────────────────────────────────────

    def _cmd_examples(self, args, output, editor):
        """Browse categorized examples."""
        category_filter = args.strip().lower()

        examples_dir = Path(__file__).parent.parent.parent.parent / "examples"
        if not examples_dir.exists():
            examples_dir = Path("examples")

        if not examples_dir.exists():
            output.write("[yellow]Examples directory not found.[/]")
            return

        if category_filter and category_filter in EXAMPLE_CATEGORIES:
            # Show specific category
            cat = EXAMPLE_CATEGORIES[category_filter]
            output.write(f"\n[bold cyan]{cat['icon']} {cat['label']}[/] ({len(cat['files'])} examples)\n")
            for fname in cat["files"]:
                desc = cat["descriptions"].get(fname, "")
                fpath = examples_dir / fname
                exists = "[green]✓[/]" if fpath.exists() else "[red]✗[/]"
                output.write(f"  {exists} [cyan]:open {fpath}[/]")
                output.write(f"      {desc}")
            output.write(f"\n[dim]Use :open <path> to load an example, or :open examples/{cat['files'][0]}[/]")
        else:
            # Show all categories
            total = sum(len(c["files"]) for c in EXAMPLE_CATEGORIES.values())
            output.write(f"\n[bold cyan]AICL Examples Library[/] — {total} programs across {len(EXAMPLE_CATEGORIES)} categories\n")

            for key, cat in EXAMPLE_CATEGORIES.items():
                available = sum(1 for f in cat["files"] if (examples_dir / f).exists())
                output.write(f"  {cat['icon']} [bold {cat['color']}]{cat['label']}[/] ({available}/{len(cat['files'])})")
                output.write(f"      [cyan]:examples {key}[/] to browse")

                # Show first 3 as preview
                for fname in cat["files"][:3]:
                    desc = cat["descriptions"].get(fname, "")
                    output.write(f"        [dim]• {desc}[/]")
                if len(cat["files"]) > 3:
                    output.write(f"        [dim]... and {len(cat['files'])-3} more[/]")
                output.write("")

            output.write("[dim]Use :examples <category> to see all examples in a category.[/]")
            output.write("[dim]Use :open <path> to load any example file.[/]")
            output.write("[dim]Categories: basics, crypto, patterns, distributed, enterprise, aiml, iot, gaming, specialized[/]")

    # ── Tutorials ────────────────────────────────────────────

    def _cmd_tutorial(self, args, output, editor):
        """Start or browse tutorials."""
        num = args.strip()

        if not num:
            # List all tutorials
            output.write("\n[bold cyan]AICL Tutorials[/] — From Zero to Hero\n")
            for tid, tut in TUTORIALS.items():
                level_color = {"Beginner": "green", "Intermediate": "yellow", "Advanced": "bright_red", "Expert": "bold magenta"}
                color = level_color.get(tut["level"], "white")
                output.write(f"  [bold cyan]Tutorial {tid}:[/] {tut['title']}")
                output.write(f"    [{color}]{tut['level']}[/] • {tut['duration']} • {tut['description']}")
                output.write("")
            output.write("[dim]Type :tutorial <number> to start a tutorial (1-7).[/]")
            return

        if num not in TUTORIALS:
            output.write(f"[red]Tutorial {num} not found.[/] Available: 1-{len(TUTORIALS)}")
            return

        tut = TUTORIALS[num]
        output.write(f"\n[bold cyan]{'='*60}[/]")
        output.write(f"[bold cyan]Tutorial {num}: {tut['title']}[/]")
        output.write(f"[bold cyan]{'='*60}[/]")
        output.write(f"  Level: {tut['level']}  |  Duration: {tut['duration']}")
        output.write(f"  {tut['description']}\n")

        # Show steps
        for i, step in enumerate(tut["steps"], 1):
            output.write(f"  [bold]{i}.[/] {step}")
        output.write("")

        # Load template into the TextArea editor
        ta = self.query_one("#editor-content", TextArea)
        template = tut["template"].replace("{{", "{").replace("}}", "}")
        ta.text = template
        output.write("[green]Template loaded into editor! Edit it and use :compile to test.[/]")
        output.write("[dim]Tips: Every Risk needs a Recovery. Every Validation generates a test. Every artifact has provenance.[/]")

    # ── LLM Chat & Model Management ─────────────────────────

    def _cmd_chat(self, args, output, editor):
        """Enter or use chat mode."""
        if not self.chat_mode:
            self.chat_mode = True
            self.chat_history = []
            input_widget = self.query_one("#cmd", Input)
            input_widget.placeholder = "Chat mode — type your message (type :exit to leave)"
            self.query_one("#main-container").add_class("chat-mode")

            model_status = self.llm.model_info if self.llm.is_loaded else "No model loaded (rule-based mode)"
            output.write(f"""[bold bright_yellow]Chat Mode Activated[/]
  Model: {model_status}
  
  [dim]Ask me anything about AICL! I can help you write specifications, explain concepts, or debug your code.[/]
  [dim]Type your message below. Type :exit to leave chat mode.[/]
  [dim]To load a local model: :model load <path-to-onnx-or-gguf>[/]""")

            # If no model loaded, provide rule-based help
            if not self.llm.is_loaded:
                output.write("\n[dim]💡 No local model loaded. To enable AI-powered chat:[/]")
                output.write("[dim]   1. Install: pip install llama-cpp-python (for GGUF) or pip install onnxruntime (for ONNX)[/]")
                output.write("[dim]   2. Load: :model load /path/to/model.gguf[/]")
                output.write("[dim]   3. Chat: just type your question![/]")
                output.write("\n[dim]Without a model, I'll use built-in AICL knowledge to help.[/]")
        else:
            # Already in chat mode, send message
            message = args.strip()
            if message:
                response = self._get_aicl_help(message)
                output.write(f"[bold bright_green]AICL AI:[/] {response}")

    def _cmd_exit_chat(self, args, output, editor):
        """Exit chat mode."""
        self.chat_mode = False
        self.chat_history = []
        input_widget = self.query_one("#cmd", Input)
        input_widget.placeholder = "Type a command or AICL code... (type :help for commands)"
        self.query_one("#main-container").remove_class("chat-mode")
        output.write("[dim]Exited chat mode.[/]")

    def _cmd_model(self, args, output, editor):
        """Manage local LLM models."""
        parts = args.strip().split(maxsplit=1)
        subcmd = parts[0].lower() if parts else ""
        subcmd_args = parts[1] if len(parts) > 1 else ""

        if subcmd == "load":
            if not subcmd_args:
                output.write("[yellow]Usage: :model load <path-to-model.onnx|gguf>[/]")
                return
            result = self.llm.load_model(subcmd_args)
            output.write(f"[bold]Model Loading[/]\n  {result}")

            # Show available backends
            backends = []
            if _ONNX_AVAILABLE:
                backends.append("[green]ONNX ✓[/]")
            else:
                backends.append("[red]ONNX ✗ (pip install onnxruntime)[/]")

            if _LLAMA_AVAILABLE:
                backends.append("[green]GGUF ✓[/]")
            else:
                backends.append("[red]GGUF ✗ (pip install llama-cpp-python)[/]")

            output.write(f"  Backends: {' | '.join(backends)}")

        elif subcmd == "info":
            output.write(f"[bold]Model Information[/]")
            output.write(f"  Status:  {'[green]Loaded[/]' if self.llm.is_loaded else '[yellow]No model loaded[/]'}")
            output.write(f"  Model:   {self.llm.model_info}")
            output.write(f"  Type:    {self.llm.model_type or 'N/A'}")
            backends = []
            if _ONNX_AVAILABLE:
                backends.append("ONNX ✓")
            if _LLAMA_AVAILABLE:
                backends.append("GGUF ✓")
            output.write(f"  Backends: {', '.join(backends) or 'None installed'}")

        elif subcmd == "unload":
            if not self.llm.is_loaded:
                output.write("[yellow]No model currently loaded.[/]")
                return
            result = self.llm.unload()
            output.write(f"[green]{result}[/]")

        elif subcmd == "scan":
            scan_dir = subcmd_args or os.path.expanduser("~")
            output.write(f"[bold]Scanning for models[/] in {scan_dir}...")
            found = []
            try:
                for root, dirs, files in os.walk(scan_dir):
                    for f in files:
                        if f.endswith(('.onnx', '.gguf')):
                            fpath = os.path.join(root, f)
                            size_mb = os.path.getsize(fpath) / (1024 * 1024)
                            found.append((fpath, size_mb))
                    # Limit depth
                    if len(found) > 50:
                        break
                    # Don't recurse too deep
                    dirs[:] = [d for d in dirs if not d.startswith('.')][:5]
            except PermissionError:
                pass

            if found:
                for fpath, size_mb in sorted(found, key=lambda x: -x[1]):
                    ext = os.path.splitext(fpath)[1]
                    icon = "🟢" if ext == ".gguf" else "🔵"
                    output.write(f"  {icon} [cyan]:model load {fpath}[/] ({size_mb:.0f} MB)")
            else:
                output.write("[yellow]No .onnx or .gguf files found.[/]")
                output.write("[dim]Tip: Download GGUF models from huggingface.co (e.g., Llama, Mistral, Phi)[/]")

        else:
            output.write("""[bold cyan]Model Management[/]

  [cyan]:model load <path>[/]   Load an ONNX or GGUF model
  [cyan]:model info[/]          Show loaded model info
  [cyan]:model unload[/]        Unload current model (free memory)
  [cyan]:model scan <dir>[/]    Scan directory for model files

[dim]Supported formats:
  • GGUF — Quantized LLM models (Llama, Mistral, Phi, etc.)
    Install: pip install llama-cpp-python
  • ONNX — Optimized inference models
    Install: pip install onnxruntime

[dim]Download models from:
  • https://huggingface.co (search for .gguf files)
  • Recommended: Phi-3-mini (3.8B), Llama-3.2-1B, Mistral-7B[/]""")

    def _get_aicl_help(self, question: str) -> str:
        """Get AICL help using LLM or rule-based fallback."""
        if self.llm.is_loaded:
            return self.llm.chat(question, self.chat_history)

        # Rule-based fallback when no model is loaded
        q = question.lower()

        if any(kw in q for kw in ["goal", "what is goal"]):
            return """**Goal:** declares WHAT you want to build. It's the first and most important keyword in AICL.

```aicl
Goal:
Create a real-time chat application with message encryption
```

Every AICL program MUST have a Goal. The compiler uses it to understand the system's purpose and generate appropriate architecture."""

        elif any(kw in q for kw in ["risk", "recovery", "error", "failure"]):
            return """**Risk/Recovery** is AICL's most powerful concept. Every Risk MUST have a Recovery.

```aicl
Risk:
Database connection lost

Recovery:
Retry with exponential backoff and switch to read-only mode
```

The compiler generates error handling code from your Risk/Recovery pairs. No more forgotten try/catch blocks!"""

        elif any(kw in q for kw in ["entity", "entities", "data", "struct"]):
            return """**Entity** defines typed data structures:

```aicl
Entity User
    id: string
    name: string
    email: string
    role: string
    created_at: datetime
```

AICL types: string, integer, float, boolean, datetime, list, dict, set, bytes, any, void"""

        elif any(kw in q for kw in ["behavior", "behaviour", "action", "function"]):
            return """**Behavior** defines what entities DO:

```aicl
Behavior CreateUser
    Input: name email role
    Output: User
    Action: validate input and create new user with generated ID
```

The compiler generates methods, error handling, and provenance tracking from behaviors."""

        elif any(kw in q for kw in ["condition", "when", "then", "if"]):
            return """**Condition** replaces if/else with declarative When/Then:

```aicl
Condition:
When user login fails 3 times
Then lock account and send verification email
```

The compiler decides HOW to implement conditions — you just declare WHAT should happen."""

        elif any(kw in q for kw in ["event", "on", "trigger"]):
            return """**Event** defines reactive behavior:

```aicl
Event:
On user registered
Action: send welcome email and create default profile
```

Events drive reactive architecture — webhooks, signals, observers, all generated automatically."""

        elif any(kw in q for kw in ["security", "encrypt", "protect"]):
            return """**Security** defines encryption and protection:

```aicl
Security:
    Encrypt: user passwords and personal data
    Protect: session tokens and API keys
```

The compiler generates encryption logic and access control from these directives."""

        elif any(kw in q for kw in ["parallel", "concurrent", "thread"]):
            return """**Parallel** declares concurrent execution:

```aicl
Parallel:
Data Ingestion
Processing Engine
Output Stream
```

The compiler decides the threading/async strategy — you just declare what can run concurrently."""

        elif any(kw in q for kw in ["learn", "adapt", "ml", "machine learning"]):
            return """**Learn/Adapt** makes your system adaptive:

```aicl
Learn:
User behavior patterns
Goal: predict user preferences

Adapt:
Recommendation algorithm
Based on: user interaction history and similarity scores
```

The compiler generates ML integration scaffolding from these directives."""

        elif any(kw in q for kw in ["native", "inline", "code"]):
            return """**Native** is the escape hatch for implementation details:

```aicl
Native: python
{
import hashlib
def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
}
```

Native code is the ONLY place for implementation details. Everything else is specification."""

        elif any(kw in q for kw in ["proof", "origin", "provenance", "verify"]):
            return """**Proof of Origin** is AICL's central compilation artifact. Every compilation produces a `.aicl-proof` file that:

• Contains the source code, generated code, and tests
• Maps every generated line back to its originating specification
• Can be verified WITHOUT the compiler (independent verifier, ~200 lines, zero deps)
• Is cryptographically signed and hash-bound

```bash
aicl compile app.aicl    # Produces code + proof
aicl proof --verify      # Verify proof integrity
python tools/verify_proof.py output/main.aicl-proof  # Independent verification
```"""

        elif any(kw in q for kw in ["compile", "compilation", "build"]):
            return """**Compilation** transforms AICL specifications into executable code:

```bash
aicl compile app.aicl                # → Python
aicl compile app.aicl --target rust  # → Rust
aicl compile app.aicl --target js    # → JavaScript
aicl compile app.aicl --target go    # → Go
```

Every compilation produces:
• Source code in the target language
• Test suite (from Validation sections)
• Proof of Origin (provenance chain)
• Architecture tree"""

        elif any(kw in q for kw in ["help", "start", "begin", "how"]):
            return """Welcome to AICL! Here's how to get started:

1. **Write a specification** using AICL keywords (Goal, Layer, Validation are minimum)
2. **Add Risk/Recovery** pairs — error handling is mandatory!
3. **Compile** with :compile to generate Python code + tests + proof
4. **Verify** with :verify-proof to independently validate the proof

Try :tutorial 1 for a step-by-step introduction, or :examples to browse 85 real programs!"""

        elif any(kw in q for kw in ["example", "show", "demo", "sample"]):
            return """Here's a complete AICL example using all 10 levels:

```aicl
Goal: Build a secure task manager

Risk: Data loss
Recovery: Auto-save every 30 seconds with backup

Layer: Task Manager
    SubLayer: Task CRUD
    SubLayer: Persistence

Entity Task
    id: string
    title: string
    done: boolean

Behavior CreateTask
    Input: title
    Output: Task
    Action: create new task with unique ID

Condition:
When task count exceeds 100
Then archive oldest completed tasks

Event:
On task completed
Action: update statistics and trigger auto-save

Parallel: Task Manager, Auto-Save

Optimize: Task listing speed

Learn: Task completion patterns
Adapt: Default priority Based on: user habits

Security:
    Encrypt: task content
    Protect: user credentials

Native: python
{ def gen_id(): return str(uuid4()) }

Validation: Tasks CRUD works correctly
```

Use :examples to browse all 85 programs!"""

        else:
            return f"""I understand you're asking about: "{question}"

I'm currently in rule-based mode (no local LLM loaded). For smarter responses, load a model:
  [cyan]:model load /path/to/model.gguf[/]

I can help with: Goal, Risk/Recovery, Entity, Behavior, Condition, Event, Parallel, Optimize, Learn/Adapt, Security, Native, Proof of Origin, compilation, and examples.

Try asking about any AICL concept, or type :tutorial to start learning!"""

    # ── Other Commands ───────────────────────────────────────

    def _cmd_open(self, args, output, editor):
        path = args.strip() or self.current_file
        if not path:
            output.write("[yellow]Usage: :open <file.aicl>[/]")
            return
        self._load_file(path, output, editor)

    def _cmd_save(self, args, output, editor):
        path = args.strip() or self.current_file
        if not path:
            output.write("[red]Usage: :save <filename.aicl> (no file is currently open)[/]")
            return
        try:
            # Read the current editor content from the TextArea
            ta = self.query_one("#editor-content", TextArea)
            with open(path, 'w') as f:
                f.write(ta.text)
            self.current_file = path
            self.query_one("#tab-label", Static).update(f" {os.path.basename(path)} ")
            output.write(f"[green]Saved: {path} ({len(ta.text)} bytes)[/]")
        except Exception as e:
            output.write(f"[red]Cannot save {path}:[/] {e}")

    def _cmd_new(self, args, output, editor):
        self.current_file = ""
        ta = self.query_one("#editor-content", TextArea)
        ta.text = "# New AICL Program\n# Write your specification below.\n\nGoal:\n\nLayer:\n\nValidation:\n\nBehavior MainAction\n    Input: input\n    Output: result\n    Action:\n        # AX: write real compilable logic here\n        return input\n"
        self.query_one("#tab-label", Static).update(" untitled.aicl ")
        output.write("[green]New file created.[/]")

    def _cmd_targets(self, args, output, editor):
        output.write("""[bold cyan]Available Targets[/]
  [green]python[/]      — Python (default, mature)
  [cyan]rust[/]        — Rust (beta)
  [cyan]javascript[/]  — JavaScript (beta)
  [cyan]go[/]          — Go (beta)

[dim]Use: :compile <target>[/]""")

    def _cmd_version(self, args, output, editor):
        output.write(f"[bold cyan]AICL[/] v{AICL_VERSION}")

    def _cmd_ownership(self, args, output, editor):
        if not self.current_file:
            output.write("[red]No file loaded.[/]")
            return
        try:
            model = OwnershipModel()
            result = model.analyze(self.current_file)
            output.write(f"[bold]Ownership Report[/]")
            for layer, entities in result.get("ownership", {}).items():
                entity_list = ", ".join(entities) if entities else "(none)"
                output.write(f"  [cyan]{layer}[/] owns: {entity_list}")
        except Exception as e:
            output.write(f"[yellow]Ownership analysis: {e}[/]")

    def _cmd_sign(self, args, output, editor):
        if not self.last_output_dir:
            output.write("[red]Compile first with :compile[/]")
            return
        proof_path = os.path.join(self.last_output_dir, "main.aicl-proof")
        if not os.path.exists(proof_path):
            output.write("[red]Proof not found[/]")
            return
        try:
            with open(proof_path) as f:
                proof = json.load(f)
            signed = create_signed_proof(proof, key_seed="aicl-compiler")
            result = verify_signed_proof(signed)
            output.write(f"""[bold cyan]Cryptographic Signing[/]
  Signature:     {'Present' if result.get('signature_present') else 'Missing'}
  Hash valid:    {'Yes' if result.get('proof_hash_valid') else 'No'}""")
        except Exception as e:
            output.write(f"[yellow]Signing: {e}[/]")

    def _cmd_verify_proof(self, args, output, editor):
        if not self.last_output_dir:
            output.write("[red]Compile first with :compile[/]")
            return
        proof_path = os.path.join(self.last_output_dir, "main.aicl-proof")
        if not os.path.exists(proof_path):
            output.write("[red]Proof not found[/]")
            return
        try:
            verifier = Path(__file__).parent.parent.parent.parent / "tools" / "verify_proof.py"
            if not verifier.exists():
                verifier = Path("tools/verify_proof.py")
            result = subprocess.run(
                [sys.executable, str(verifier), proof_path, "--verbose"],
                capture_output=True, text=True, timeout=30
            )
            output.write(result.stdout if result.stdout else result.stderr)
        except Exception as e:
            output.write(f"[red]Independent verification failed:[/] {e}")

    # ── Helpers ────────────────────────────────────────────────

    def _load_file(self, path: str, output=None, editor=None):
        if output is None:
            output = self.query_one("#output-log", RichLog)
        if editor is None:
            editor = self.query_one("#editor-content", TextArea)
        try:
            with open(path) as f:
                source = f.read()
            editor.text = source  # TextArea uses .text, not .write()
            self.current_file = path
            self.query_one("#tab-label", Static).update(f" {os.path.basename(path)} ")
            output.write(f"[green]Loaded:[/] {path}")
        except Exception as e:
            output.write(f"[red]Cannot open {path}:[/] {e}")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        if event.path.suffix == ".aicl":
            self._load_file(str(event.path))

    def action_open_file(self):
        self.query_one("#cmd", Input).value = ":open "

    def action_save_file(self):
        if self.current_file:
            try:
                ta = self.query_one("#editor-content", TextArea)
                with open(self.current_file, 'w') as f:
                    f.write(ta.text)
                self.query_one("#output-log", RichLog).write(
                    f"[green]Saved: {self.current_file} ({len(ta.text)} bytes)[/]"
                )
            except Exception as e:
                self.query_one("#output-log", RichLog).write(f"[red]Save failed: {e}[/]")
        else:
            self.query_one("#cmd", Input).value = ":save "

    def action_command_palette(self):
        self.query_one("#cmd", Input).value = ":"

    def action_toggle_sidebar(self):
        sidebar = self.query_one("#sidebar")
        sidebar.display = not sidebar.display


def main():
    """Entry point for AICL TUI."""
    app = AICLTUI()
    app.run()


if __name__ == "__main__":
    main()
