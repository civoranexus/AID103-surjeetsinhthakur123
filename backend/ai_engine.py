import json
from decision_logic import assess_severity, pesticide_optimization

with open("disease_knowledge_base.json") as f:
    DB = json.load(f)

CONFIDENCE_THRESHOLD = 70.0  # percent

SEVERITY_RISK_MAP = {
    "Low": 0.2,
    "Medium": 0.5,
    "High": 0.8
}

def analyze_crop(image_features, crop_type, environment):

    if crop_type not in DB:
        return {"status": "FAILED", "error": "Crop not supported"}

    severity = assess_severity(
        environment["humidity"],
        environment["temperature"]
    )
    risk_score = SEVERITY_RISK_MAP.get(severity, 0.0)

    # ---------- CNN VALIDATION ----------
    use_cnn = False
    decision_reason = "Rule-based inference applied"

    if image_features:
        disease_from_cnn = image_features.get("disease")

        try:
            cnn_conf = float(image_features.get("confidence", "0").replace("%", ""))
        except:
            cnn_conf = 0.0

        if disease_from_cnn != "Uncertain" and cnn_conf >= CONFIDENCE_THRESHOLD:
            use_cnn = True
            decision_reason = "CNN prediction accepted (high confidence)"
        else:
            decision_reason = "CNN uncertain or low confidence → rule-based fallback"

    # ---------- INFERENCE ----------
    if use_cnn:
        disease = image_features["disease"]
        confidence = image_features["confidence"]
        inference_mode = "CNN_IMAGE_BASED"
        model_source = image_features.get("source", "cnn")
    else:
        crop_diseases = [d for d in DB[crop_type] if d != "Healthy"]

        if severity == "High" and crop_diseases:
            disease = crop_diseases[0]
        elif severity == "Medium" and len(crop_diseases) > 1:
            disease = crop_diseases[1]
        else:
            disease = "Healthy"

        confidence = "RULE_BASED"
        inference_mode = "ENVIRONMENT_RULE_BASED"
        model_source = "rule_engine"

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
