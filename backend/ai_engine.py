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

    # ---------- VALIDATION ----------
    if crop_type not in DB:
        return {
            "status": "FAILED",
            "error": "Crop not supported"
        }

    humidity = environment.get("humidity", 0)
    temperature = environment.get("temperature", 0)

    env_severity = assess_severity(humidity, temperature)
    risk_score = SEVERITY_RISK_MAP.get(env_severity, 0.0)

    # ---------- CNN CONFIDENCE CHECK ----------
    use_cnn = False
    decision_reason = "Rule-based inference applied"

    if image_features:
        disease_from_cnn = image_features.get("disease", "Uncertain")

        try:
            cnn_conf = float(image_features.get("confidence", "0").replace("%", ""))
        except:
            cnn_conf = 0.0

        if disease_from_cnn != "Uncertain" and cnn_conf >= CONFIDENCE_THRESHOLD:
            use_cnn = True
            decision_reason = "CNN prediction accepted (high confidence)"
        else:
            decision_reason = "CNN low confidence → rule-based fallback"

    # ---------- DISEASE INFERENCE ----------
    reasoning_clues = []

    if use_cnn:
        disease = disease_from_cnn
        confidence = image_features["confidence"]
        inference_mode = "CNN_IMAGE_BASED"
        model_source = image_features.get("source", "cnn")
        reasoning_clues.append("Visual symptoms detected from leaf image")

    else:
        # Knowledge-aware rule-based inference
        candidate_diseases = []

        for d_name, d_info in DB[crop_type].items():
            if d_name == "Healthy":
                continue

            risk_cond = d_info.get("risk_conditions", {})
            risk_h = risk_cond.get("humidity", "")
            risk_t = risk_cond.get("temperature", "")

            if (">" in risk_h and humidity >= int(risk_h.replace(">", ""))) or \
               (">" in risk_t and temperature >= int(risk_t.replace(">", ""))):
                candidate_diseases.append(d_name)

        if candidate_diseases:
            disease = candidate_diseases[0]
            reasoning_clues.append("Environmental conditions favor this disease")
        else:
            disease = "Healthy"
            reasoning_clues.append("No strong disease-favoring conditions detected")

        confidence = "RULE_BASED"
        inference_mode = "ENVIRONMENT_RULE_BASED"
        model_source = "rule_engine"

    # ---------- KNOWLEDGE BASE CHECK ----------
    if disease not in DB[crop_type]:
        return {
            "status": "PARTIAL",
            "crop_type": crop_type,
            "disease_detected": disease,
            "severity": env_severity,
            "risk_score": risk_score,
            "confidence": confidence,
            "inference_mode": inference_mode,
            "decision_reason": decision_reason,
            "reasoning_clues": reasoning_clues,
            "treatment_available": False
        }

    disease_info = DB[crop_type][disease]
    treatment = disease_info.get("treatment", {})
    final_severity = disease_info.get("severity_level", env_severity)

    return {
        "status": "SUCCESS",
        "crop_type": crop_type,
        "disease_detected": disease,
        "severity": final_severity,
        "risk_score": risk_score,
        "confidence": confidence,
        "inference_mode": inference_mode,
        "model_source": model_source,
        "decision_reason": decision_reason,
        "reasoning_clues": reasoning_clues,
        "advisory": {
            "treatment": treatment,
            "pesticide_strategy": pesticide_optimization(final_severity),
            "yield_impact": "Early intervention improves yield"
        }
    }
