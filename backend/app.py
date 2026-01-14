from flask import Flask, request, jsonify
import os
import traceback

from cnn_model import extract_image_features, generate_explainability
from ai_engine import analyze_crop

app = Flask(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        crop = request.form.get("crop")
        humidity = float(request.form.get("humidity"))
        temperature = float(request.form.get("temperature"))

        image_features = None
        explain_image = None

        if "image" in request.files:
            image = request.files["image"]
            if image and image.filename:
                image_path = os.path.join(UPLOAD_DIR, image.filename)
                image.save(image_path)

                image_features = extract_image_features(image_path)

                # ---- SAFE GRAD-CAM ----
                try:
                    explain_image = generate_explainability(image_path)
                except:
                    explain_image = None

        result = analyze_crop(
            image_features=image_features,
            crop_type=crop,
            environment={
                "humidity": humidity,
                "temperature": temperature
            }
        )

        if explain_image:
            result["explainability_image"] = os.path.abspath(explain_image).replace("\\", "/")

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Backend exception",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
