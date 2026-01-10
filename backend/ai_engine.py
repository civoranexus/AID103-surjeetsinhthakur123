import json
from decision_logic import assess_severity, pesticide_optimization

with open("disease_knowledge_base.json") as f:
    DB = json.load(f)

SEVERITY_RISK_MAP = {
    "Low": 0.2,
    "Medium": 0.5,
    "High": 0.8
}

def analyze_crop(image_features, crop_type, environment):
    """
    Advanced Dual-Mode AI Engine

    - Image-based (CNN): Disease from image
    - No-image (Rule-based): Disease inferred from environment
    - Adds inference_mode, risk_score, and robust handling
    """

    # ---------- VALIDATION ----------
    if crop_type not in DB:
        return {
            "status": "FAILED",
            "error": "Crop not supported"
        }

    # ---------- SEVERITY ----------
    severity = assess_severity(
        environment["humidity"],
        environment["temperature"]
    )

    risk_score = SEVERITY_RISK_MAP.get(severity, 0.0)

    # ---------- DISEASE INFERENCE ----------
    if image_features:
        disease = image_features.get("disease", "Unknown")
        confidence = image_features.get("confidence", "N/A")
        inference_mode = "CNN_IMAGE_BASED"
        model_source = image_features.get("source", "unknown")

    else:
        # Stable ordering to avoid dict-order issues
        crop_diseases = [
            d for d in DB[crop_type].keys() if d != "Healthy"
        ]

        if severity == "High" and crop_diseases:
            disease = crop_diseases[0]
        elif severity == "Medium" and len(crop_diseases) > 1:
            disease = crop_diseases[1]
        else:
            disease = "Healthy"

        confidence = "RULE_BASED"
        inference_mode = "ENVIRONMENT_RULE_BASED"
        model_source = "rule_engine"

    # ---------- KNOWLEDGE BASE CHECK ----------
    if disease not in DB[crop_type]:
        return {
            "status": "PARTIAL",
            "inference_mode": inference_mode,
            "crop_type": crop_type,
            "disease_detected": disease,
            "severity": severity,
            "risk_score": risk_score,
            "confidence": confidence,
            "treatment_available": False
        }

    treatment = DB[crop_type][disease]["treatment"]

    # ---------- FINAL OUTPUT ----------
    return {
        "status": "SUCCESS",
        "inference_mode": inference_mode,
        "model_source": model_source,
        "crop_type": crop_type,
        "disease_detected": disease,
        "severity": severity,
        "risk_score": risk_score,
        "confidence": confidence,
        "advisory": {
            "treatment": treatment,
            "pesticide_strategy": pesticide_optimization(severity),
            "yield_impact": "Early intervention improves yield"
        }
    }
