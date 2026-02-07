import json
from decision_logic import assess_severity, pesticide_optimization

# ---------- LOAD KNOWLEDGE BASE ----------
with open("disease_knowledge_base.json") as f:
    DB = json.load(f)

SEVERITY_RISK_MAP = {
    "Low": 0.2,
    "Medium": 0.5,
    "High": 0.8
}

DEFAULT_TREATMENT = {
    "chemical": "Consult local agriculture expert before chemical use",
    "organic": "Neem oil or bio-fungicide spray",
    "prevention": "Regular monitoring and field hygiene"
}

# ---------- PARSE CNN LABEL ----------
def parse_crop_and_disease(label):
    if not label or "___" not in label:
        return "Unknown Crop", label

    crop, disease = label.split("___", 1)
    crop = crop.replace("_", " ").replace("(including sour)", "").title()
    disease = disease.replace("_", " ").title()
    return crop, disease


# =====================================================
# 🖼️ IMAGE-BASED ANALYSIS (AUTO CROP DETECTION)
# =====================================================
def analyze_with_image(image_features):
    disease_label = image_features.get("disease", "Uncertain")
    confidence = image_features.get("confidence", "N/A")

    crop, disease = parse_crop_and_disease(disease_label)

    reasoning_clues = [
        "Crop automatically detected from image",
        "Disease identified using CNN visual patterns"
    ]

    try:
        conf_val = float(confidence.replace("%", ""))
        severity = "High" if conf_val >= 85 else "Medium"
    except:
        severity = "Medium"

    risk_score = SEVERITY_RISK_MAP.get(severity, 0.5)

    if crop in DB and disease in DB[crop]:
        treatment = DB[crop][disease]["treatment"]
        decision_reason = "Disease matched with knowledge base"
    else:
        treatment = DEFAULT_TREATMENT
        decision_reason = "Generic advisory applied (unknown crop/disease)"
        reasoning_clues.append("No exact match found in knowledge base")

    return {
        "status": "SUCCESS",
        "crop_type": crop,
        "disease_detected": disease,
        "severity": severity,
        "risk_score": risk_score,
        "confidence": confidence,
        "inference_mode": "CNN_IMAGE_BASED",
        "model_source": "cnn",
        "decision_reason": decision_reason,
        "reasoning_clues": reasoning_clues,
        "advisory": {
            "treatment": treatment,
            "pesticide_strategy": pesticide_optimization(severity),
            "yield_impact": "Early detection improves yield and reduces losses"
        }
    }


# =====================================================
# 🌱 NO IMAGE → CROP + ENVIRONMENT
# =====================================================
def analyze_without_image(crop_type, environment):
    humidity = environment.get("humidity", 0)
    temperature = environment.get("temperature", 0)

    severity = assess_severity(humidity, temperature)
    risk_score = SEVERITY_RISK_MAP.get(severity, 0.5)

    reasoning_clues = [
        "No image uploaded",
        "Environmental conditions analyzed"
    ]

    if crop_type not in DB:
        reasoning_clues.append("Crop not present in knowledge base")

        return {
            "status": "SUCCESS",
            "crop_type": crop_type,
            "disease_detected": "Unknown",
            "severity": severity,
            "risk_score": risk_score,
            "confidence": "RULE_BASED",
            "inference_mode": "ENVIRONMENT_RULE_BASED",
            "decision_reason": "Generic advisory applied",
            "reasoning_clues": reasoning_clues,
            "advisory": {
                "treatment": DEFAULT_TREATMENT,
                "pesticide_strategy": pesticide_optimization(severity),
                "yield_impact": "Preventive care reduces risk"
            }
        }

    diseases = [d for d in DB[crop_type] if d != "Healthy"]

    if severity == "High" and diseases:
        disease = diseases[0]
    elif severity == "Medium" and len(diseases) > 1:
        disease = diseases[1]
    else:
        disease = "Healthy"

    treatment = DB[crop_type].get(disease, {}).get("treatment", DEFAULT_TREATMENT)

    return {
        "status": "SUCCESS",
        "crop_type": crop_type,
        "disease_detected": disease,
        "severity": severity,
        "risk_score": risk_score,
        "confidence": "RULE_BASED",
        "inference_mode": "ENVIRONMENT_RULE_BASED",
        "decision_reason": "Rule-based crop and environment analysis",
        "reasoning_clues": reasoning_clues,
        "advisory": {
            "treatment": treatment,
            "pesticide_strategy": pesticide_optimization(severity),
            "yield_impact": "Early intervention improves yield"
        }
    }
