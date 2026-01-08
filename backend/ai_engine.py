import json
from decision_logic import assess_severity, pesticide_optimization

with open("disease_knowledge_base.json") as f:
    DB = json.load(f)

def analyze_crop(image_features, crop_type, environment):
    """
    Dual-mode AI:
    - With image → CNN decides disease
    - Without image → Environment-based risk inference
    """

    if crop_type not in DB:
        return {"error": "Crop not supported"}

    severity = assess_severity(
        environment["humidity"],
        environment["temperature"]
    )

    # ---- MODE 1: IMAGE PRESENT ----
    if image_features is not None:
        disease = image_features.get("disease", "Unknown")
        confidence = image_features.get("confidence", "N/A")

    # ---- MODE 2: NO IMAGE ----
    else:
        # Simple intelligent inference
        if severity == "High":
            disease = list(DB[crop_type].keys())[0]  # most risky disease
        elif severity == "Medium":
            disease = list(DB[crop_type].keys())[1]
        else:
            disease = "Healthy"

        confidence = "Rule-based"

    if disease not in DB[crop_type]:
        return {
            "disease_detected": disease,
            "severity": severity,
            "confidence": confidence,
            "advisory": {
                "message": "No specific treatment data available"
            }
        }

    treatment = DB[crop_type][disease]["treatment"]

    return {
        "disease_detected": disease,
        "severity": severity,
        "confidence": confidence,
        "advisory": {
            "treatment": treatment,
            "pesticide_strategy": pesticide_optimization(severity),
            "yield_impact": "Early intervention improves yield"
        }
    }
