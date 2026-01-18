import streamlit as st
import requests
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CropGuard AI", layout="centered")

st.title("🌱 CropGuard AI")
st.subheader("Intelligent Crop Disease Detection Platform")

st.markdown("""
This system provides **AI-driven crop disease detection**
and **context-aware treatment recommendations**.
You can analyze crops **with or without uploading an image**.
""")

# ---------------- LOAD CROPS FROM CNN LABELS ----------------
LABELS_PATH = "../backend/model/class_labels.json"

def load_crops():
    if not os.path.exists(LABELS_PATH):
        return ["Tomato"]

    with open(LABELS_PATH, "r") as f:
        labels = json.load(f)

    crops = set()
    for label in labels.values():
        if "___" in label:
            crop = label.split("___")[0]
            crop = crop.replace("_", " ")
            crop = crop.replace("(maize)", "")
            crop = crop.replace(",", "")
            crop = crop.strip()
            crops.add(crop)

    return sorted(crops)

# ---------------- USER INPUTS ----------------
CROP_OPTIONS = load_crops()
crop = st.selectbox("Select Crop", CROP_OPTIONS)

humidity = st.slider("Humidity (%)", 30, 100, 70)
temperature = st.slider("Temperature (°C)", 15, 45, 30)

st.markdown("### 📸 Crop Image (Optional)")
uploaded_image = st.file_uploader(
    "Upload Crop Image",
    type=["jpg", "jpeg", "png"]
)
camera_image = st.camera_input("Or Capture Image Using Camera")

image_file = uploaded_image if uploaded_image else camera_image

if image_file:
    st.image(image_file, caption="Selected Crop Image", use_column_width=True)
    st.info("Image-based CNN analysis will be used.")
else:
    st.info("No image uploaded. Rule-based + environment analysis will be used.")

# ---------------- PDF GENERATOR ----------------
def generate_pdf(result, crop):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "CropGuard AI – Disease Analysis Report")

    c.setFont("Helvetica", 12)
    y = height - 100

    c.drawString(50, y, f"Crop: {crop}")
    y -= 25
    c.drawString(50, y, f"Disease Detected: {result.get('disease_detected')}")
    y -= 25
    c.drawString(50, y, f"Severity: {result.get('severity')}")
    y -= 25
    c.drawString(50, y, f"Confidence: {result.get('confidence')}")
    y -= 40

    reasoning = result.get("reasoning_clues", [])
    if reasoning:
        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, "Explainable AI – Reasoning:")
        y -= 25
        c.setFont("Helvetica", 11)
        for clue in reasoning:
            c.drawString(60, y, f"- {clue}")
            y -= 18
        y -= 15

    advisory = result.get("advisory", {})
    treatment = advisory.get("treatment", {})

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Treatment Recommendations:")
    y -= 25

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Chemical Treatment: {treatment.get('chemical', 'N/A')}")
    y -= 20
    c.drawString(50, y, f"Organic Treatment: {treatment.get('organic', 'N/A')}")
    y -= 20
    c.drawString(50, y, f"Prevention: {treatment.get('prevention', 'N/A')}")
    y -= 30

    c.drawString(50, y, f"Pesticide Strategy: {advisory.get('pesticide_strategy', 'N/A')}")
    y -= 20
    c.drawString(50, y, f"Yield Impact: {advisory.get('yield_impact', 'N/A')}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ---------------- ANALYZE ----------------
if st.button("Analyze Crop"):
    with st.spinner("Contacting AI Engine..."):
        try:
            data = {
                "crop": crop,
                "humidity": humidity,
                "temperature": temperature
            }

            files = {"image": image_file} if image_file else None

            response = requests.post(
                "http://127.0.0.1:5000/analyze",
                data=data,
                files=files,
                timeout=30
            )

            result = response.json()

            if "error" in result:
                st.error(result["error"])
            else:
                st.success("AI Analysis Completed")

                st.markdown("### 🧠 AI Detection Result")
                st.write("**Crop Selected:**", crop)
                st.write("**Disease Detected:**", result.get("disease_detected"))
                st.write("**Severity:**", result.get("severity"))
                st.write("**Confidence:**", result.get("confidence"))

                # ---------- EXPLAINABLE AI ----------
                reasoning = result.get("reasoning_clues", [])
                if reasoning:
                    st.markdown("### 🧩 Explainable AI – Reasoning")
                    for clue in reasoning:
                        st.markdown(f"- {clue}")

                # ---------- CONFIDENCE BAR ----------
                confidence_value = result.get("confidence", "")
                if isinstance(confidence_value, str) and "%" in confidence_value:
                    conf_percent = float(confidence_value.replace("%", ""))
                    st.markdown("#### 🔍 Prediction Confidence")
                    st.progress(conf_percent / 100)

                # ---------- RISK SCORE ----------
                risk_score = result.get("risk_score")
                if isinstance(risk_score, (int, float)):
                    st.markdown("#### ⚠️ Risk Score")
                    st.progress(risk_score)

                # ---------- GRAD-CAM ----------
                explain_img_path = result.get("explainability_image")
                if explain_img_path:
                    st.markdown("### 🔍 Visual Explainability (Grad-CAM)")
                    st.image(
                        explain_img_path,
                        caption="Disease-affected regions",
                        use_column_width=True
                    )

                # ---------- TREATMENT ----------
                st.markdown("### 💊 Treatment & Advisory")
                advisory = result.get("advisory", {})
                treatment = advisory.get("treatment", {})

                st.write("**Chemical Treatment:**", treatment.get("chemical", "N/A"))
                st.write("**Organic Treatment:**", treatment.get("organic", "N/A"))
                st.write("**Prevention:**", treatment.get("prevention", "N/A"))

                st.markdown("### 🌾 Optimization Strategy")
                st.write("**Pesticide Strategy:**", advisory.get("pesticide_strategy", "N/A"))
                st.write("**Yield Impact:**", advisory.get("yield_impact", "N/A"))

                # ---------- PDF ----------
                pdf_buffer = generate_pdf(result, crop)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer,
                    file_name="CropGuard_AI_Report.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error("Failed to connect to backend.")
            st.text(str(e))
