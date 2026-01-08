from flask import Flask, request, jsonify
import os
from cnn_model import extract_image_features
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

        # ---- IMAGE OPTIONAL ----
        if "image" in request.files:
            image = request.files["image"]
            if image.filename != "":
                image_path = os.path.join(UPLOAD_DIR, image.filename)
                image.save(image_path)
                image_features = extract_image_features(image_path)

        # ---- AI ANALYSIS ----
        result = analyze_crop(
            image_features=image_features,
            crop_type=crop,
            environment={
                "humidity": humidity,
                "temperature": temperature
            }
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": "Backend exception",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
