# app/utils/agent_logger.py

import logging
from typing import Optional
from uuid import uuid4
from datetime import datetime

# Configure the root logger once for the entire app
logger = logging.getLogger("agent")
logger.setLevel(logging.INFO)

# Optional: Console handler for local dev
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def log_agent_event(
    agent_name: str,
    input_data: dict,
    output_data: dict,
    fallback_used: bool = False,
    error: Optional[str] = None,
    request_id: Optional[str] = None,
):
    log_payload = {
        "event_type": "agent_execution",
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "request_id": request_id or str(uuid4()),
        "input": input_data,
        "output": output_data,
        "fallback_used": fallback_used,
        "error": error,
    }
    logger.info(log_payload)
