from flask import Flask, request, jsonify
from ai_engine import analyze_crop

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    crop = data["crop"]
    humidity = data["humidity"]
    temperature = data["temperature"]

    result = analyze_crop(crop, humidity, temperature)

    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
