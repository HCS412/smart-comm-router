def classify_message(content: str) -> dict:
    """
    Placeholder classification logic.
    In the future, this will use an OpenAI agent or LLM model.
    """
    if "schedule" in content.lower():
        return {"category": "Scheduling", "priority": "Medium"}
    elif "investment" in content.lower():
        return {"category": "Investor", "priority": "High"}
    elif "unsubscribe" in content.lower():
        return {"category": "Newsletter", "priority": "Low"}
    else:
        return {"category": "General Inquiry", "priority": "Medium"}
