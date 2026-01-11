import json
from decision_logic import assess_severity, pesticide_optimization

with open("disease_knowledge_base.json") as f:
    DB = json.load(f)

CONFIDENCE_THRESHOLD = 70.0  # CNN confidence cutoff (percentage)

SEVERITY_RISK_MAP = {
    "Low": 0.2,
    "Medium": 0.5,
    "High": 0.8
}

def analyze_crop(image_features, crop_type, environment):
    """
    Final AI Decision Engine (Best Version)

    Logic:
    - CNN predicts disease if confidence is reliable
    - Otherwise fallback to rule-based inference
    - Environment determines severity
    - Knowledge base maps treatment
    """

    # -------- VALIDATION --------
    if crop_type not in DB:
        return {
            "status": "FAILED",
            "error": "Crop not supported"
        }

    # -------- SEVERITY & RISK --------
    severity = assess_severity(
        environment["humidity"],
        environment["temperature"]
    )
    risk_score = SEVERITY_RISK_MAP.get(severity, 0.0)

    # -------- CNN CONFIDENCE CHECK --------
    use_cnn = False
    decision_reason = "Rule-based inference applied"

    if image_features:
        try:
            cnn_conf = float(
                image_features.get("confidence", "0").replace("%", "")
            )
        except:
            cnn_conf = 0.0

        if cnn_conf >= CONFIDENCE_THRESHOLD:
            use_cnn = True
            decision_reason = "CNN prediction accepted (high confidence)"
        else:
            decision_reason = "CNN confidence low, fallback to rule-based logic"

    # -------- DISEASE INFERENCE --------
    if use_cnn:
        disease = image_features.get("disease", "Unknown")
        confidence = image_features.get("confidence", "N/A")
        inference_mode = "CNN_IMAGE_BASED"
        model_source = image_features.get("source", "cnn")

    else:
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

    # -------- KNOWLEDGE BASE MATCH --------
    if disease not in DB[crop_type]:
        return {
            "status": "PARTIAL",
            "crop_type": crop_type,
            "disease_detected": disease,
            "severity": severity,
            "risk_score": risk_score,
            "confidence": confidence,
            "inference_mode": inference_mode,
            "decision_reason": decision_reason,
            "treatment_available": False
        }

    treatment = DB[crop_type][disease]["treatment"]

    # -------- FINAL OUTPUT --------
    return {
        "status": "SUCCESS",
        "crop_type": crop_type,
        "disease_detected": disease,
        "severity": severity,
        "risk_score": risk_score,
        "confidence": confidence,
        "inference_mode": inference_mode,
        "model_source": model_source,
        "decision_reason": decision_reason,
        "advisory": {
            "treatment": treatment,
            "pesticide_strategy": pesticide_optimization(severity),
            "yield_impact": "Early intervention improves yield"
        }
    }
