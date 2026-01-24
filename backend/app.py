from flask import Flask, request, jsonify
import os
import traceback
import json
import uuid

from voice_summary import generate_voice_summary
from cnn_model import extract_image_features, generate_explainability
from ai_engine import analyze_with_image, analyze_without_image

# =========================================================
# ===================== APP SETUP =========================
# =========================================================
app = Flask(__name__)

UPLOAD_DIR = "uploads"
FEEDBACK_DIR = "feedback"
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "feedback_data.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# ---------- INIT FEEDBACK STORAGE ----------
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump([], f)

# =========================================================
# ===================== ANALYZE API =======================
# =========================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # ---------- COMMON INPUTS ----------
        humidity = float(request.form.get("humidity", 0))
        temperature = float(request.form.get("temperature", 0))
        language = request.form.get("language", "en")  # en / hi / mr

        explain_image = None

        # =================================================
        # ================ IMAGE ANALYSIS =================
        # =================================================
        if "image" in request.files and request.files["image"].filename:
            image = request.files["image"]

            image_path = os.path.join(
                UPLOAD_DIR,
                f"{uuid.uuid4().hex}_{image.filename}"
            )
            image.save(image_path)

            # ---- CNN Prediction ----
            image_features = extract_image_features(image_path)

            # ---- Explainable AI (Grad-CAM) ----
            try:
                explain_image = generate_explainability(image_path)
            except Exception:
                explain_image = None

            # ---- AI Engine (image-based) ----
            result = analyze_with_image(image_features)

        # =================================================
        # ============= NON-IMAGE ANALYSIS ================
        # =================================================
        else:
            crop = request.form.get("crop")

            if not crop:
                return jsonify({
                    "status": "FAILED",
                    "error": "Crop must be provided when no image is uploaded"
                }), 400

            result = analyze_without_image(
                crop_type=crop,
                environment={
                    "humidity": humidity,
                    "temperature": temperature
                }
            )

        # =================================================
        # ================ VOICE SUMMARY ==================
        # =================================================
        voice_path = generate_voice_summary(result, language)
        result["voice_summary"] = request.host_url + voice_path

        # =================================================
        # ============== EXPLAINABILITY IMG ===============
        # =================================================
        if explain_image:
            result["explainability_image"] = os.path.abspath(
                explain_image
            ).replace("\\", "/")

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "FAILED",
            "error": str(e)
        }), 500


# =========================================================
# ===================== FEEDBACK API ======================
# =========================================================
@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Stores farmer feedback for:
    - Model evaluation
    - Dataset improvement
    - Future retraining
    """
    try:
        data = request.json

        if not data:
            return jsonify({
                "status": "FAILED",
                "error": "No feedback data received"
            }), 400

        feedback_entry = {
            "id": uuid.uuid4().hex,
            "crop": data.get("crop"),
            "disease": data.get("disease"),
            "confidence": data.get("confidence"),
            "correct": data.get("correct"),  # True / False
            "comment": data.get("comment", ""),
        }

        # ---------- SAVE FEEDBACK ----------
        with open(FEEDBACK_FILE, "r+") as f:
            existing = json.load(f)
            existing.append(feedback_entry)
            f.seek(0)
            json.dump(existing, f, indent=2)

        return jsonify({
            "status": "SUCCESS",
            "message": "Feedback saved successfully"
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "FAILED",
            "error": str(e)
        }), 500
    
# =========================================================
# ===================== RUN SERVER ========================
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)
