import json
from decision_logic import assess_severity, pesticide_optimization

with open("disease_knowledge_base.json") as f:
    DB = json.load(f)

SEVERITY_RISK_MAP = {
    "Low": 0.2,
    "Medium": 0.5,
    "High": 0.8
}

# -------------------------------------------------
# 1️⃣ IMAGE-BASED ANALYSIS (CNN ONLY)
# -------------------------------------------------
def analyze_with_image(image_features):
    """
    CNN-based analysis + advisory
    """

    disease_label = image_features.get("disease", "Uncertain")
    confidence = image_features.get("confidence", "N/A")

    crop, disease = parse_crop_and_disease(disease_label)

    reasoning_clues = [
        "Disease detected using CNN image analysis",
        "Visual patterns matched with trained leaf dataset"
    ]

    # Default severity from confidence
    try:
        conf_val = float(confidence.replace("%", ""))
        severity = "High" if conf_val > 85 else "Medium"
    except:
        severity = "Medium"

    # Knowledge base lookup
    if crop in DB and disease in DB[crop]:
        treatment = DB[crop][disease]["treatment"]
    else:
        treatment = {
            "chemical": "Consult local agriculture expert",
            "organic": "Manual inspection recommended",
            "prevention": "Early monitoring advised"
        }

    return {
        "status": "SUCCESS",
        "crop_type": crop,
        "disease_detected": disease,
        "severity": severity,
        "confidence": confidence,
        "inference_mode": "CNN_IMAGE_BASED",
        "model_source": "cnn",
        "decision_reason": "High-confidence CNN prediction",
        "reasoning_clues": reasoning_clues,
        "advisory": {
            "treatment": treatment,
            "pesticide_strategy": pesticide_optimization(severity),
            "yield_impact": "Early detection improves yield and reduces loss"
        }
    }


# -------------------------------------------------
# 2️⃣ CROP + ENVIRONMENT ANALYSIS (RULE ENGINE)
# -------------------------------------------------
def analyze_without_image(crop_type, environment):

    if crop_type not in DB:
        return {
            "status": "FAILED",
            "error": "Crop not supported in knowledge base"
        }

    humidity = environment.get("humidity", 0)
    temperature = environment.get("temperature", 0)

    severity = assess_severity(humidity, temperature)
    risk_score = SEVERITY_RISK_MAP.get(severity, 0.0)

    # Simple deterministic logic
    diseases = [d for d in DB[crop_type] if d != "Healthy"]

    if severity == "High" and diseases:
        disease = diseases[0]
        reason = "High humidity/temperature favors disease outbreak"
    elif severity == "Medium" and len(diseases) > 1:
        disease = diseases[1]
        reason = "Moderate environmental stress detected"
    else:
        disease = "Healthy"
        reason = "No strong disease-favoring conditions"

    treatment = DB[crop_type].get(disease, {}).get("treatment", {})

    return {
        "status": "SUCCESS",
        "analysis_type": "ENVIRONMENT_BASED",
        "crop_type": crop_type,
        "disease_detected": disease,
        "severity": severity,
        "risk_score": risk_score,
        "confidence": "RULE_BASED",
        "reasoning_clues": [
            "Analysis based on crop selection",
            reason
        ],
        "advisory": {
            "treatment": treatment,
            "pesticide_strategy": pesticide_optimization(severity),
            "yield_impact": "Early intervention improves yield"
        }
    }

def parse_crop_and_disease(label: str):
    """
    Converts CNN label into crop + disease
    Example: Tomato___Early_blight → Tomato, Early Blight
    """
    if "___" not in label:
        return None, label

    crop, disease = label.split("___", 1)
    disease = disease.replace("_", " ").title()
    crop = crop.replace("_", " ").title()

    return crop, disease
