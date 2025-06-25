import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """
    The foundational class for all intelligent agents in the Triage system.

    Responsibilities:
    - Enforces a consistent interface across agents (classifiers, responders, routers, etc.)
    - Handles fallback defaults and error reporting
    - Captures execution time for observability
    - Supports optional metadata injection for agent awareness
    """

    def __init__(self, name: str):
        self.name = name
        self.version = "1.0"
        self.metadata = {}

    def set_metadata(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Inject runtime metadata into the agent (useful for context-aware agents).
        """
        if metadata:
            self.metadata.update(metadata)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates full agent lifecycle:
        - Tracks runtime
        - Handles fallback logic
        - Returns consistent response structure
        """
        start = time.time()

        try:
            result = self.run(input_data)

            # Add diagnostic and agent info
            result.update({
                "_agent": self.name,
                "_version": self.version,
                "_latency_ms": round((time.time() - start) * 1000, 2),
                "_fallback_used": result.get("fallback_used", False)
            })

            return result

        except Exception as e:
            return self.fallback(
                reason=str(e),
                latency_ms=round((time.time() - start) * 1000, 2)
            )

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core agent logic must be implemented by each subclass.
        Should return a structured dict including at minimum:
        - category
        - priority
        - intent
        - recommended_queue
        - confidence
        """
        pass

    def fallback(self, reason: str = "Unhandled agent error", latency_ms: float = 0.0) -> Dict[str, Any]:
        """
        Standard fallback result for failed agent execution.
        """
        return {
            "category": "General Inquiry",
            "priority": "Medium",
            "intent": "Unknown",
            "recommended_queue": "Customer Support",
            "confidence": 0.0,
            "fallback_used": True,
            "error": reason,
            "_agent": self.name,
            "_version": self.version,
            "_latency_ms": latency_ms
        }
