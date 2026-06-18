"""
AICL ↔ CogNet integration (placeholder).

This subpackage is reserved for the upcoming bidirectional bridge between
AICL specifications and the CogNet cognitive engine. The full integration
plan is documented in `python/docs/cognet_integration_plan.md`.

Today this module is intentionally empty — importing it succeeds but
exposes no public symbols. This keeps the import path stable across the
rollout so downstream code can write `from aicl.cognet import ...` once
the integration ships.

Planned public API (subject to change before v2.2):

    from aicl.cognet import AICLCognetBridge
    bridge = AICLCognetBridge()
    graph = bridge.spec_to_graph(source)
    new_source = bridge.graph_to_spec(graph)

See: python/docs/cognet_integration_plan.md
"""

__all__: list[str] = []
