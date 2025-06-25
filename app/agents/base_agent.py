import time
import traceback
from abc import ABC, abstractmethod
from typing import Any, Optional, TypedDict, Dict
from enum import Enum
from app.utils.logger import logger

# ---------------- Enums for Type Safety ----------------

class PriorityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class CategoryType(str, Enum):
    BILLING = "Billing Support"
    DISPATCH = "Dispatch Communication"
    SENSOR = "Sensor Alert"
    MARKETING = "Marketing"
    GENERAL = "General Inquiry"

class QueueType(str, Enum):
    FINANCE = "Finance Support"
    DISPATCH = "Dispatch Team"
    OPS = "Ops Team"
    AUTOMATION = "Automation"
    SUPPORT = "Customer Support"

# ---------------- TypedDicts for I/O ----------------

class AgentInput(TypedDict, total=False):
    sender: str
    content: str
    classification: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]

class AgentOutput(TypedDict):
    category: str
    priority: str
    intent: str
    recommended_queue: str
    confidence: float
    fallback_used: bool
    error: Optional[str]
    _agent: str
    _version: str
    _latency_ms: float

# ---------------- Timing Context ----------------

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.latency_ms = round((self.end - self.start) * 1000, 2)

# ---------------- Base Agent ----------------

class BaseAgent(ABC):
    """
    The foundational class for all intelligent agents in the Triage system.

    Responsibilities:
    - Enforces a consistent interface across agents
    - Handles fallback and error resilience
    - Captures runtime and structured output
    - Validates I/O types and confidence
    - Supports lifecycle hooks and extensibility
    """

    name: str = "BaseAgent"
    version: str = "1.0"
    fallback_config: Dict[str, Any] = {
        "category": CategoryType.GENERAL,
        "priority": PriorityLevel.MEDIUM,
        "intent": "Unknown",
        "recommended_queue": QueueType.SUPPORT,
        "confidence": 0.0
    }

    def __init__(self, metadata: Optional[Dict[str, Any]] = None):
        self.metadata = metadata or {}

    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Run the agent with error handling and timing.

        Args:
            input_data: Dict with keys sender, content, classification (optional)

        Returns:
            AgentOutput: structured classification or draft result
        """
        self._validate_input(input_data)

        with Timer() as timer:
            try:
                self.preprocess(input_data)
                result = self.run(input_data)
                self.postprocess(result)

                # Ensure confidence is valid
                result["confidence"] = min(max(result.get("confidence", 0.0), 0.0), 1.0)
                result.update({
                    "_agent": self.name,
                    "_version": self.version,
                    "_latency_ms": timer.latency_ms,
                    "fallback_used": result.get("fallback_used", False),
                    "error": result.get("error")
                })
                return result  # type: ignore

            except Exception as e:
                logger.exception(f"[{self.name}] Unhandled error during execution")
                return self.fallback(str(e), timer.latency_ms)

    @abstractmethod
    def run(self, input_data: AgentInput) -> AgentOutput:
        """
        Core agent logic implemented by all subclasses.
        Must return a valid AgentOutput.
        """
        pass

    def fallback(self, reason: str, latency: float = 0.0) -> AgentOutput:
        """
        Default fallback response structure with error context.
        """
        logger.warning(f"[{self.name}] Using fallback due to: {reason}")

        return {
            "category": self.fallback_config["category"],
            "priority": self.fallback_config["priority"],
            "intent": self.fallback_config["intent"],
            "recommended_queue": self.fallback_config["recommended_queue"],
            "confidence": self.fallback_config["confidence"],
            "fallback_used": True,
            "error": reason,
            "_agent": self.name,
            "_version": self.version,
            "_latency_ms": latency
        }

    def preprocess(self, input_data: AgentInput) -> None:
        """
        Optional hook: Normalize or augment input before running.
        """
        pass

    def postprocess(self, result: Dict[str, Any]) -> None:
        """
        Optional hook: Cleanup or enrich result before returning.
        """
        pass

    def _validate_input(self, input_data: AgentInput) -> None:
        if not input_data.get("content"):
            raise ValueError("Missing required field: content")
        if not input_data.get("sender"):
            raise ValueError("Missing required field: sender")
