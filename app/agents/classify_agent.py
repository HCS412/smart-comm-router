def classify_message(msg: dict) -> dict:
    content = msg["content"].lower()
    product = msg.get("product", "").lower()
    
    # Pioneer sensor alerts
    if product == "pioneer" or any(kw in content for kw in ["full", "pack-out", "sensor error"]):
        return {
            "category": "Sensor Alert",
            "priority": "High",
            "intent": "Compactor Monitoring",
            "recommended_queue": "Ops Team",
            "confidence": 0.95
        }
    # Hauler dispatch chats
    if product == "hauler" or any(kw in content for kw in ["dispatch", "pickup", "eta", "driver"]):
        return {
            "category": "Dispatch Communication",
            "priority": "Medium",
            "intent": "Schedule/ETA Inquiry",
            "recommended_queue": "Dispatch Team",
            "confidence": 0.90
        }
    # Discovery invoice/support issues
    if product == "discovery" or any(kw in content for kw in ["invoice", "charge", "billing", "surcharge"]):
        return {
            "category": "Billing Support",
            "priority": "High",
            "intent": "Invoice Inquiry",
            "recommended_queue": "Finance Support",
            "confidence": 0.92
        }
    # Unsubscribe or marketing
    if "unsubscribe" in content:
        return {
            "category": "Marketing",
            "priority": "Low",
            "intent": "Unsubscribe",
            "recommended_queue": "Automation",
            "confidence": 0.99
        }
    # Default
    return {
        "category": "General Inquiry",
        "priority": "Medium",
        "intent": "Support",
        "recommended_queue": "Customer Support",
        "confidence": 0.75
    }
