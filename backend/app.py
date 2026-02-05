from flask import Flask, request, jsonify
import os
import traceback
import json
import uuid
import sqlite3

from voice_summary import generate_voice_summary
from cnn_model import extract_image_features, generate_explainability
from ai_engine import analyze_with_image, analyze_without_image

import requests
from dotenv import load_dotenv

# =========================================================
# ===================== APP SETUP =========================
# =========================================================
app = Flask(__name__)


load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

EXPERTS = {
    "whatsapp": "919876543210",
    "helpline": "+91-1800-123-456"
}

UPLOAD_DIR = "uploads"
FEEDBACK_DIR = "feedback"
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "feedback_data.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# =========================================================
# ===================== SQLITE SETUP ======================
# =========================================================
DB_PATH = "cropguard.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ---------- CREATE TABLE (RUNS ONCE) ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS crop_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE,
    crop TEXT,
    disease TEXT,
    severity TEXT,
    confidence REAL,
    advisory TEXT,
    expert_enabled INTEGER,
    voice_summary TEXT,
    explainability_image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ---------- INIT FEEDBACK STORAGE ----------
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump([], f)

# =========================================================
# ===================== WEATHER API =======================
def get_weather(city):
    if not city or not WEATHER_API_KEY:
        return None

    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )

        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return None

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }

    except Exception:
        return None

# =========================================================
# ===================== ANALYZE API =======================
# =========================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    try:

        city = request.form.get("city")
        weather = get_weather(city)
        humidity = float(request.form.get("humidity", 0))
        temperature = float(request.form.get("temperature", 0))
        language = request.form.get("language", "en")

        explain_image = None

        # ================= IMAGE =================
        if "image" in request.files and request.files["image"].filename:
            image = request.files["image"]
            image_path = os.path.join(
                UPLOAD_DIR, f"{uuid.uuid4().hex}_{image.filename}"
            )
            image.save(image_path)

            image_features = extract_image_features(image_path)

            try:
                explain_image = generate_explainability(image_path)
            except:
                explain_image = None

            result = analyze_with_image(image_features)

        # ================= NO IMAGE =================
        else:
            crop = request.form.get("crop")
            if not crop:
                return jsonify({"error": "Crop required"}), 400

            result = analyze_without_image(
                crop_type=crop,
                environment={
                    "humidity": humidity,
                    "temperature": temperature
                }
            )

        # =================================================
        # ============ CONFIDENCE NORMALIZATION ============
        # =================================================
        raw_confidence = result.get("confidence", 0)

        if isinstance(raw_confidence, (int, float)):
            confidence_value = float(raw_confidence)
        else:
            confidence_value = 50.0
            result["confidence_type"] = str(raw_confidence)

        result["confidence"] = confidence_value

        # ================= EXPERT CONNECT =================
        result["expert_connect"] = {
            "enabled": confidence_value < 60,
            "reason": "Low AI confidence",
            "whatsapp": f"https://wa.me/{EXPERTS['whatsapp']}",
            "helpline": EXPERTS["helpline"]
        }

        result["weather_data"] = weather

        # ================= VOICE =================
        voice_path = generate_voice_summary(result, language)
        result["voice_summary"] = request.host_url + voice_path

        # ================= EXPLAIN IMAGE =================
        if explain_image:
            result["explainability_image"] = os.path.abspath(
                explain_image
            ).replace("\\", "/")

        # =================================================
        # ============== SAVE REPORT TO SQLITE =============
        # =================================================
        report_id = uuid.uuid4().hex
        result["report_id"] = report_id

        cursor.execute("""
        INSERT INTO crop_reports
        (report_id, crop, disease, severity, confidence, advisory,
         expert_enabled, voice_summary, explainability_image)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            report_id,
            result.get("crop_type"),
            result.get("disease_detected"),
            result.get("severity"),
            confidence_value,
            json.dumps(result.get("advisory", {})),
            int(result.get("expert_connect", {}).get("enabled", False)),
            result.get("voice_summary"),
            result.get("explainability_image")
        ))
        conn.commit()

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =========================================================
# ===================== FEEDBACK API ======================
# =========================================================
@app.route("/feedback", methods=["POST"])
def feedback():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No feedback data"}), 400

        with open(FEEDBACK_FILE, "r+") as f:
            existing = json.load(f)
            existing.append(data)
            f.seek(0)
            json.dump(existing, f, indent=2)

        return jsonify({"status": "SUCCESS"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route("/sync-offline", methods=["POST"])
def sync_offline():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data"}), 400

        image_features = {
            "disease": data.get("crop_disease_label"),
            "confidence": data.get("confidence")
        }

        result = analyze_with_image(image_features)

        city = data.get("city")
        weather = get_weather(city)
        result["weather_data"] = weather
        result["offline_mode"] = True

        report_id = uuid.uuid4().hex
        result["report_id"] = report_id

        cursor.execute("""
        INSERT INTO crop_reports
        (report_id, crop, disease, severity, confidence, advisory,
         expert_enabled, voice_summary, explainability_image)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            report_id,
            result.get("crop_type"),
            result.get("disease_detected"),
            result.get("severity"),
            float(result.get("confidence", 50)),
            json.dumps(result.get("advisory", {})),
            0,
            None,
            None
        ))
        conn.commit()

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =========================================================
# ===================== RUN SERVER ========================
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)
