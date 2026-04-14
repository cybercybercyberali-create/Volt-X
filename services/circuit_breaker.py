import logging
import time
from enum import Enum
from typing import Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitStats:
    failures: int = 0
    successes: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    total_calls: int = 0


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
        self._circuits: dict[str, CircuitStats] = {}

    def _get_circuit(self, name: str) -> CircuitStats:
        """Get or create circuit stats."""
        if name not in self._circuits:
            self._circuits[name] = CircuitStats()
        return self._circuits[name]

    def is_available(self, name: str) -> bool:
        """Check if a service is available (circuit not open)."""
        circuit = self._get_circuit(name)
        now = time.monotonic()

        if circuit.state == CircuitState.CLOSED:
            return True

        if circuit.state == CircuitState.OPEN:
            if now - circuit.last_failure_time >= self._recovery_timeout:
                circuit.state = CircuitState.HALF_OPEN
                circuit.consecutive_failures = 0
                logger.info(f"Circuit {name} transitioning to HALF_OPEN")
                return True
            return False

        if circuit.state == CircuitState.HALF_OPEN:
            return circuit.successes < self._half_open_max_calls

        return True

    def record_success(self, name: str) -> None:
        """Record a successful call."""
        circuit = self._get_circuit(name)
        circuit.successes += 1
        circuit.total_calls += 1
        circuit.consecutive_failures = 0
        circuit.last_success_time = time.monotonic()

        if circuit.state == CircuitState.HALF_OPEN:
            if circuit.successes >= self._half_open_max_calls:
                circuit.state = CircuitState.CLOSED
                circuit.failures = 0
                circuit.successes = 0
                logger.info(f"Circuit {name} CLOSED (recovered)")

    def record_failure(self, name: str) -> None:
        """Record a failed call."""
        circuit = self._get_circuit(name)
        circuit.failures += 1
        circuit.total_calls += 1
        circuit.consecutive_failures += 1
        circuit.last_failure_time = time.monotonic()

        if circuit.state == CircuitState.HALF_OPEN:
            circuit.state = CircuitState.OPEN
            logger.warning(f"Circuit {name} OPEN (failed during half-open)")
            return

        if circuit.consecutive_failures >= self._failure_threshold:
            circuit.state = CircuitState.OPEN
            logger.warning(f"Circuit {name} OPEN (threshold {self._failure_threshold} reached)")

    def get_status(self, name: str) -> dict[str, Any]:
        """Get circuit status."""
        circuit = self._get_circuit(name)
        return {
            "name": name,
            "state": circuit.state.value,
            "failures": circuit.failures,
            "successes": circuit.successes,
            "consecutive_failures": circuit.consecutive_failures,
            "total_calls": circuit.total_calls,
        }

    def get_all_statuses(self) -> dict[str, dict[str, Any]]:
        """Get all circuit statuses."""
        return {name: self.get_status(name) for name in self._circuits}

    def reset(self, name: str) -> None:
        """Manually reset a circuit."""
        if name in self._circuits:
            self._circuits[name] = CircuitStats()
            logger.info(f"Circuit {name} manually reset")


# Global circuit breaker instance
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
