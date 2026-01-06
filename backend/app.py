from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from backend.cnn_model import predict_disease

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze_crop():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    crop_type = request.form.get("crop_type")
    location = request.form.get("location")

    filename = secure_filename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    result = predict_disease(image_path, crop_type)

    response = {
        "crop": crop_type,
        "location": location,
        "disease_detected": result["disease"],
        "severity": result["severity"],
        "recommendation": result["recommendation"],
        "confidence": result["confidence"]
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
