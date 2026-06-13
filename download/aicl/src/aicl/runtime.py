"""
AICL Self-Healing Runtime System

Provides a runtime environment that automatically executes recovery
actions when risks materialize, with runtime provenance tracking.

The self-healing runtime is the natural extension of AICL's
compile-time provenance system into the runtime domain. At compile
time, every risk has a recovery. At runtime, when a risk materializes,
the recovery is automatically executed — and this execution is recorded
in a runtime provenance chain.

Architecture:
    RuntimeEnvironment — the container for the running application
    RiskMonitor — monitors for risk conditions
    RecoveryExecutor — executes recovery actions
    RuntimeProvenance — records runtime provenance events

Design Principle:
    The compile-time guarantee "every Risk has a Recovery" becomes
    the runtime guarantee "every failure triggers a Recovery." The
    runtime provenance chain extends the compile-time provenance,
    creating an unbroken chain from specification to execution.
"""

import time
import traceback
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum


class RuntimeEventType(Enum):
    """Types of runtime provenance events."""
    APPLICATION_START = "application_start"
    APPLICATION_END = "application_end"
    RISK_DETECTED = "risk_detected"
    RECOVERY_EXECUTED = "recovery_executed"
    RECOVERY_SUCCESS = "recovery_success"
    RECOVERY_FAILED = "recovery_failed"
    VALIDATION_CHECKED = "validation_checked"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    BEHAVIOR_INVOKED = "behavior_invoked"
    BEHAVIOR_COMPLETED = "behavior_completed"
    BEHAVIOR_FAILED = "behavior_failed"
    STATE_CHANGED = "state_changed"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class RuntimeProvenanceEvent:
    """A single runtime provenance event."""
    event_type: RuntimeEventType
    timestamp: str = ""
    source: str = ""          # What triggered this event
    description: str = ""     # Human-readable description
    risk_name: str = ""       # Associated risk (if any)
    recovery_name: str = ""   # Associated recovery (if any)
    behavior_name: str = ""   # Associated behavior (if any)
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_after: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    recovery_attempts: int = 0
    provenance_chain: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "description": self.description,
            "risk_name": self.risk_name,
            "recovery_name": self.recovery_name,
            "behavior_name": self.behavior_name,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "error_message": self.error_message,
            "recovery_attempts": self.recovery_attempts,
            "provenance_chain": self.provenance_chain,
            "metadata": self.metadata,
        }


@dataclass
class RiskRecoveryBinding:
    """A binding between a risk condition and a recovery action."""
    risk_name: str
    risk_condition: Callable[[], bool]     # Returns True if risk has materialized
    recovery_action: Callable[[], bool]    # Returns True if recovery succeeded
    max_attempts: int = 3
    backoff_seconds: float = 1.0


class RuntimeProvenance:
    """
    Records and reports runtime provenance events.

    The runtime provenance extends the compile-time provenance chain
    into the execution domain. Every risk detection, recovery execution,
    and state change is recorded, creating a complete audit trail from
    specification through execution.
    """

    def __init__(self):
        self._events: List[RuntimeProvenanceEvent] = []

    def record(self, event: RuntimeProvenanceEvent) -> None:
        """Record a runtime provenance event."""
        self._events.append(event)

    @property
    def events(self) -> List[RuntimeProvenanceEvent]:
        """All recorded events."""
        return list(self._events)

    def get_recovery_events(self) -> List[RuntimeProvenanceEvent]:
        """Get all recovery-related events."""
        return [e for e in self._events
                if e.event_type in (RuntimeEventType.RECOVERY_EXECUTED,
                                     RuntimeEventType.RECOVERY_SUCCESS,
                                     RuntimeEventType.RECOVERY_FAILED)]

    def get_risk_events(self) -> List[RuntimeProvenanceEvent]:
        """Get all risk detection events."""
        return [e for e in self._events
                if e.event_type == RuntimeEventType.RISK_DETECTED]

    def compute_runtime_coverage(self) -> Dict[str, Any]:
        """
        Compute runtime coverage metrics.

        Runtime coverage measures what fraction of detected risks
        had successful recoveries.
        """
        risk_events = self.get_risk_events()
        recovery_events = self.get_recovery_events()
        successful_recoveries = [e for e in recovery_events
                                  if e.event_type == RuntimeEventType.RECOVERY_SUCCESS]
        failed_recoveries = [e for e in recovery_events
                              if e.event_type == RuntimeEventType.RECOVERY_FAILED]

        total_risks = len(risk_events)
        total_recoveries = len(recovery_events)
        total_successes = len(successful_recoveries)

        coverage = total_successes / total_risks if total_risks > 0 else 1.0

        return {
            "total_risks_detected": total_risks,
            "total_recovery_attempts": total_recoveries,
            "successful_recoveries": total_successes,
            "failed_recoveries": len(failed_recoveries),
            "runtime_recovery_coverage": coverage,
        }

    def generate_report(self) -> str:
        """Generate a human-readable runtime provenance report."""
        lines = []
        lines.append("=" * 60)
        lines.append("AICL RUNTIME PROVENANCE REPORT")
        lines.append("=" * 60)
        lines.append(f"Total events: {len(self._events)}")
        lines.append("")

        coverage = self.compute_runtime_coverage()
        lines.append("RUNTIME COVERAGE")
        lines.append(f"  Risks detected: {coverage['total_risks_detected']}")
        lines.append(f"  Recovery attempts: {coverage['total_recovery_attempts']}")
        lines.append(f"  Successful: {coverage['successful_recoveries']}")
        lines.append(f"  Failed: {coverage['failed_recoveries']}")
        lines.append(f"  Coverage: {coverage['runtime_recovery_coverage']:.1%}")
        lines.append("")

        lines.append("EVENT CHAIN")
        for event in self._events:
            lines.append(f"  [{event.event_type.value}] {event.description}")
            if event.risk_name:
                lines.append(f"    Risk: {event.risk_name}")
            if event.recovery_name:
                lines.append(f"    Recovery: {event.recovery_name}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def to_json(self) -> str:
        """Serialize all events to JSON."""
        return json.dumps(
            [e.to_dict() for e in self._events],
            indent=2
        )

    def to_file(self, path: str) -> None:
        """Write runtime provenance to a file."""
        with open(path, 'w') as f:
            f.write(self.to_json())


class RecoveryExecutor:
    """
    Executes recovery actions with retry and backoff.

    When a risk condition is detected, the RecoveryExecutor
    attempts the associated recovery action, with configurable
    retry attempts and exponential backoff.
    """

    def __init__(self, provenance: RuntimeProvenance):
        self.provenance = provenance

    def execute(self, binding: RiskRecoveryBinding) -> bool:
        """
        Execute a recovery action with retries.

        Returns True if the recovery succeeded within the
        maximum number of attempts.
        """
        self.provenance.record(RuntimeProvenanceEvent(
            event_type=RuntimeEventType.RISK_DETECTED,
            source="RiskMonitor",
            description=f"Risk materialized: {binding.risk_name}",
            risk_name=binding.risk_name,
        ))

        for attempt in range(1, binding.max_attempts + 1):
            self.provenance.record(RuntimeProvenanceEvent(
                event_type=RuntimeEventType.RECOVERY_EXECUTED,
                source="RecoveryExecutor",
                description=f"Executing recovery for {binding.risk_name} (attempt {attempt}/{binding.max_attempts})",
                risk_name=binding.risk_name,
                recovery_name=binding.risk_name + "_recovery",
                recovery_attempts=attempt,
            ))

            try:
                success = binding.recovery_action()
                if success:
                    self.provenance.record(RuntimeProvenanceEvent(
                        event_type=RuntimeEventType.RECOVERY_SUCCESS,
                        source="RecoveryExecutor",
                        description=f"Recovery succeeded for {binding.risk_name}",
                        risk_name=binding.risk_name,
                        recovery_name=binding.risk_name + "_recovery",
                        recovery_attempts=attempt,
                    ))
                    return True
            except Exception as e:
                self.provenance.record(RuntimeProvenanceEvent(
                    event_type=RuntimeEventType.RECOVERY_FAILED,
                    source="RecoveryExecutor",
                    description=f"Recovery threw exception for {binding.risk_name}: {e}",
                    risk_name=binding.risk_name,
                    recovery_name=binding.risk_name + "_recovery",
                    error_message=str(e),
                    recovery_attempts=attempt,
                ))

            # Backoff before retry
            if attempt < binding.max_attempts:
                time.sleep(binding.backoff_seconds * (2 ** (attempt - 1)))

        return False


class RuntimeEnvironment:
    """
    The AICL self-healing runtime environment.

    Manages the application lifecycle with automatic risk monitoring
    and recovery execution. Every runtime event is recorded in the
    runtime provenance chain.

    Usage:
        env = RuntimeEnvironment()

        env.register_risk_recovery("network_failure",
            risk_condition=lambda: not check_network(),
            recovery_action=lambda: reconnect())

        env.run(application_main)
    """

    def __init__(self):
        self.provenance = RuntimeProvenance()
        self.recovery_executor = RecoveryExecutor(self.provenance)
        self._bindings: List[RiskRecoveryBinding] = []
        self._state: Dict[str, Any] = {}
        self._running = False

    def register_risk_recovery(
        self,
        risk_name: str,
        risk_condition: Callable[[], bool],
        recovery_action: Callable[[], bool],
        max_attempts: int = 3,
        backoff_seconds: float = 1.0,
    ) -> None:
        """
        Register a risk/recovery pair for runtime monitoring.

        Args:
            risk_name: Name identifying the risk
            risk_condition: Function returning True when the risk has materialized
            recovery_action: Function returning True when recovery succeeds
            max_attempts: Maximum recovery attempts before giving up
            backoff_seconds: Initial backoff delay (doubles each retry)
        """
        binding = RiskRecoveryBinding(
            risk_name=risk_name,
            risk_condition=risk_condition,
            recovery_action=recovery_action,
            max_attempts=max_attempts,
            backoff_seconds=backoff_seconds,
        )
        self._bindings.append(binding)

    def set_state(self, key: str, value: Any) -> None:
        """Update the runtime state."""
        old_value = self._state.get(key)
        self._state[key] = value

        if old_value != value:
            self.provenance.record(RuntimeProvenanceEvent(
                event_type=RuntimeEventType.STATE_CHANGED,
                source="RuntimeEnvironment",
                description=f"State changed: {key}",
                state_before={key: old_value},
                state_after={key: value},
            ))

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a runtime state value."""
        return self._state.get(key, default)

    def check_risks(self) -> List[str]:
        """
        Check all registered risk conditions.

        Returns a list of risk names that have materialized.
        """
        materialized = []
        for binding in self._bindings:
            try:
                if binding.risk_condition():
                    materialized.append(binding.risk_name)
            except Exception:
                pass  # Risk check failure is not a risk itself
        return materialized

    def execute_recovery(self, risk_name: str) -> bool:
        """
        Execute the recovery action for a specific risk.

        Returns True if the recovery succeeded.
        """
        for binding in self._bindings:
            if binding.risk_name == risk_name:
                return self.recovery_executor.execute(binding)
        return False

    def run(self, main_fn: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Run the application with self-healing.

        The main function is executed within the runtime environment.
        Risks are monitored before, during, and after execution.
        Any materialized risks trigger automatic recovery.

        Args:
            main_fn: The application's main function

        Returns:
            Runtime result dictionary with status and provenance
        """
        self._running = True

        self.provenance.record(RuntimeProvenanceEvent(
            event_type=RuntimeEventType.APPLICATION_START,
            source="RuntimeEnvironment",
            description="Application starting",
        ))

        # Check risks before starting
        pre_risks = self.check_risks()
        for risk_name in pre_risks:
            self.execute_recovery(risk_name)

        # Run main function
        result = {"success": True, "error": None}
        if main_fn:
            try:
                main_fn()
            except Exception as e:
                result["success"] = False
                result["error"] = str(e)

                self.provenance.record(RuntimeProvenanceEvent(
                    event_type=RuntimeEventType.ERROR_OCCURRED,
                    source="RuntimeEnvironment",
                    description=f"Application error: {e}",
                    error_message=str(e),
                ))

                # Try to recover from the error
                for binding in self._bindings:
                    if binding.risk_condition():
                        self.execute_recovery(binding.risk_name)

        # Check risks after completion
        post_risks = self.check_risks()
        for risk_name in post_risks:
            self.execute_recovery(risk_name)

        self.provenance.record(RuntimeProvenanceEvent(
            event_type=RuntimeEventType.APPLICATION_END,
            source="RuntimeEnvironment",
            description="Application ended",
        ))

        self._running = False

        result["runtime_coverage"] = self.provenance.compute_runtime_coverage()
        result["event_count"] = len(self.provenance.events)

        return result

    def get_runtime_report(self) -> str:
        """Generate the runtime provenance report."""
        return self.provenance.generate_report()
