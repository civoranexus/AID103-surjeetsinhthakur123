from flask import Flask, request, jsonify
import os
import traceback

from cnn_model import extract_image_features, generate_explainability
from ai_engine import analyze_with_image, analyze_without_image

app = Flask(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        humidity = float(request.form.get("humidity", 0))
        temperature = float(request.form.get("temperature", 0))
        crop = request.form.get("crop")  # used ONLY if no image

        image_features = None
        explain_image = None

        # =================================================
        # 🖼️ IMAGE-BASED ANALYSIS (CNN ONLY)
        # =================================================
        if "image" in request.files and request.files["image"].filename:
            image = request.files["image"]
            image_path = os.path.join(UPLOAD_DIR, image.filename)
            image.save(image_path)

            image_features = extract_image_features(image_path)

            # Grad-CAM (safe)
            try:
                explain_image = generate_explainability(image_path)
            except Exception:
                explain_image = None

            result = analyze_with_image(image_features)

        # =================================================
        # 🌱 CROP + ENVIRONMENT ANALYSIS (NO IMAGE)
        # =================================================
        else:
            if not crop:
                return jsonify({
                    "status": "FAILED",
                    "error": "Crop must be selected when no image is uploaded"
                }), 400

            result = analyze_without_image(
                crop_type=crop,
                environment={
                    "humidity": humidity,
                    "temperature": temperature
                }
            )

        # Attach explainability image path if available
        if explain_image:
            result["explainability_image"] = os.path.abspath(
                explain_image
            ).replace("\\", "/")

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "FAILED",
            "error": "Backend exception",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
