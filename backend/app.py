from flask import Flask, request, jsonify
import os, traceback
from voice_summary import generate_voice_summary
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
        language = request.form.get("language", "English")

        explain_image = None

        # ---------- IMAGE UPLOADED ----------
        if "image" in request.files and request.files["image"].filename:
            image = request.files["image"]
            path = os.path.join(UPLOAD_DIR, image.filename)
            image.save(path)

            image_features = extract_image_features(path)
            try:
                explain_image = generate_explainability(path)
            except:
                explain_image = None

            result = analyze_with_image(image_features)

        # ---------- NO IMAGE ----------
        else:
            crop = request.form.get("crop")
            result = analyze_without_image(
                crop_type=crop,
                environment={"humidity": humidity, "temperature": temperature}
            )
        
        # ---------- VOICE SUMMARY ----------
        voice_path = generate_voice_summary(result, language)
        result["voice_summary"] = request.host_url + voice_path

        if explain_image:
            result["explainability_image"] = os.path.abspath(explain_image).replace("\\", "/")

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "FAILED", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
