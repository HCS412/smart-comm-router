import time
import traceback
from abc import ABC, abstractmethod
from typing import Any, Optional, TypedDict, Dict
from enum import Enum
from uuid import uuid4
from app.utils.logger import logger
from app.utils.agent_logger import log_agent_event

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
        self._validate_input(input_data)
        request_id = str(uuid4())

        with Timer() as timer:
            try:
                self.preprocess(input_data)
                result = self.run(input_data)
                self.postprocess(result)

                result["confidence"] = min(max(result.get("confidence", 0.0), 0.0), 1.0)
                result.update({
                    "_agent": self.name,
                    "_version": self.version,
                    "_latency_ms": timer.latency_ms,
                    "fallback_used": result.get("fallback_used", False),
                    "error": result.get("error")
                })

                log_agent_event(
                    agent_name=self.name,
                    input_data=input_data,
                    output_data=result,
                    fallback_used=False,
                    request_id=request_id
                )

                return result  # type: ignore

            except Exception as e:
                logger.exception(f"[{self.name}] Unhandled error during execution")
                fallback = self.fallback(str(e), timer.latency_ms)

                log_agent_event(
                    agent_name=self.name,
                    input_data=input_data,
                    output_data=fallback,
                    fallback_used=True,
                    error=str(e),
                    request_id=request_id
                )

                return fallback

    @abstractmethod
    def run(self, input_data: AgentInput) -> AgentOutput:
        pass

    def fallback(self, reason: str, latency: float = 0.0) -> AgentOutput:
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
        pass

    def postprocess(self, result: Dict[str, Any]) -> None:
        pass

    def _validate_input(self, input_data: AgentInput) -> None:
        if not input_data.get("content"):
            raise ValueError("Missing required field: content")
        if not input_data.get("sender"):
            raise ValueError("Missing required field: sender")
