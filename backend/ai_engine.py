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

def _normalize_disease_name(raw_name: str) -> str:
    """
    Converts CNN disease part to KB-compatible format
    Example:
    Early_blight -> Early Blight
    Tomato_Yellow_Leaf_Curl_Virus -> Tomato Yellow Leaf Curl Virus
    """
    return raw_name.replace("_", " ").title().strip()


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

    use_cnn = False
    decision_reason = "Rule-based inference applied"
    reasoning_clues = []

    disease = None
    confidence = None
    inference_mode = None
    model_source = None

    # ---------- CNN-BASED INFERENCE ----------
    if image_features:
        raw_label = image_features.get("disease", "")
        confidence_str = image_features.get("confidence", "0")

        try:
            cnn_conf = float(confidence_str.replace("%", ""))
        except:
            cnn_conf = 0.0

        # Expecting format: Crop___Disease
        if "___" in raw_label:
            cnn_crop, cnn_disease_raw = raw_label.split("___", 1)
            cnn_disease = _normalize_disease_name(cnn_disease_raw)
        else:
            cnn_crop = None
            cnn_disease = None

        if cnn_crop == crop_type and cnn_conf >= CONFIDENCE_THRESHOLD:
            use_cnn = True
            disease = cnn_disease
            confidence = confidence_str
            inference_mode = "CNN_IMAGE_BASED"
            model_source = image_features.get("source", "cnn")

            decision_reason = "CNN prediction accepted (high confidence)"
            reasoning_clues.append("Visual disease patterns detected from leaf image")
        else:
            reasoning_clues.append(
                "CNN confidence low or crop mismatch → rule-based fallback"
            )

    # ---------- RULE-BASED FALLBACK ----------
    if not use_cnn:
        candidate_diseases = []

        for d_name, d_info in DB[crop_type].items():
            if d_name == "Healthy":
                continue

            risk_cond = d_info.get("risk_conditions", {})
            risk_h = risk_cond.get("humidity", "")
            risk_t = risk_cond.get("temperature", "")

            h_match = (">" in risk_h and humidity >= int(risk_h.replace(">", "")))
            t_match = (">" in risk_t and temperature >= int(risk_t.replace(">", "")))

            if h_match or t_match:
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
