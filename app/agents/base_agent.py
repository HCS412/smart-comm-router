from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """
    Abstract base class for all agents. Enforces consistency across message handling agents.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses must implement this method.
        Should return a structured dictionary result.
        """
        pass

    def fallback(self, reason: str = "Unknown error") -> Dict[str, Any]:
        return {
            "category": "General Inquiry",
            "priority": "Medium",
            "intent": "Unclear",
            "recommended_queue": "Customer Support",
            "confidence": 0.0,
            "error": reason,
            "fallback_used": True
        }
