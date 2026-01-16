import streamlit as st
import requests
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

# ---------------- USER INPUTS ----------------
CROP_OPTIONS = ["Tomato", "Potato", "Wheat", "Rice", "Maize"]

crop = st.selectbox("Select Crop", CROP_OPTIONS)

humidity = st.slider("Humidity (%)", 30, 100, 70)
temperature = st.slider("Temperature (°C)", 15, 45, 30)

st.markdown("### 📸 Crop Image (Optional)")
uploaded_image = st.file_uploader(
    "Upload Crop Image",
    type=["jpg", "jpeg", "png"]
)
camera_image = st.camera_input("Or Capture Image Using Camera")

# Choose image if provided
image_file = uploaded_image if uploaded_image else camera_image

if image_file:
    st.image(image_file, caption="Selected Crop Image", use_column_width=True)
    st.info("Image-based analysis will be used (CNN).")
else:
    st.info("No image uploaded. Analysis will be based on crop and environmental data.")

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

    advisory = result.get("advisory", {})
    treatment = advisory.get("treatment", {})

    c.drawString(50, y, f"Chemical Treatment: {treatment.get('chemical', 'N/A')}")
    y -= 25
    c.drawString(50, y, f"Organic Treatment: {treatment.get('organic', 'N/A')}")
    y -= 25
    c.drawString(50, y, f"Prevention: {treatment.get('prevention', 'N/A')}")
    y -= 40

    c.drawString(50, y, f"Pesticide Strategy: {advisory.get('pesticide_strategy', 'N/A')}")
    y -= 25
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

            if response.headers.get("Content-Type") != "application/json":
                st.error("Backend did not return JSON.")
                st.text(response.text)
            else:
                result = response.json()

                if "error" in result:
                    st.error(result.get("error"))
                else:
                    st.success("AI Analysis Completed")

                    st.markdown("### 🧠 AI Detection Result")
                    st.write("**Crop Selected:**", crop)
                    st.write("**Disease Detected:**", result.get("disease_detected"))
                    st.write("**Severity:**", result.get("severity"))
                    st.write("**Confidence:**", result.get("confidence"))

                # ---------- REASONING CLUES ----------
                reasoning = result.get("reasoning_clues", [])

                if reasoning:
                    st.markdown("### 🧩 Explainable AI – Reasoning")
                    for clue in reasoning:
                        st.markdown(f"- {clue}")


                    # ---------- CONFIDENCE BAR ----------
                    confidence_value = result.get("confidence", "0")
                    if isinstance(confidence_value, str) and "%" in confidence_value:
                        try:
                            conf_percent = float(confidence_value.replace("%", ""))
                            st.markdown("#### 🔍 Prediction Confidence")
                            st.progress(conf_percent / 100)
                            st.caption(f"Confidence Level: {conf_percent:.2f}%")
                        except:
                            pass

                    # ---------- RISK SCORE ----------
                    risk_score = result.get("risk_score")
                    if isinstance(risk_score, (int, float)):
                        st.markdown("#### ⚠️ Risk Score")
                        st.progress(risk_score)
                        st.caption(f"Risk Score: {risk_score:.2f} (0 = Low, 1 = High)")

                    # ---------- EXPLAINABILITY IMAGE ----------
                    explain_img_path = result.get("explainability_image")

                    if explain_img_path:
                        try:
                            st.markdown("### 🔍 Explainable AI (Grad-CAM)")
                            st.image(
                                explain_img_path,
                                caption="Highlighted disease-affected regions",
                                use_column_width=True
                            )
                        except Exception as e:
                            st.warning("Explainability image could not be displayed.")
                            st.text(str(e))

                    st.markdown("### 💊 Treatment & Advisory")
                    advisory = result.get("advisory", {})
                    treatment = advisory.get("treatment", {})

                    st.write("**Chemical Treatment:**", treatment.get("chemical", "N/A"))
                    st.write("**Organic Treatment:**", treatment.get("organic", "N/A"))
                    st.write("**Prevention:**", treatment.get("prevention", "N/A"))

                    st.markdown("### 🌾 Optimization Strategy")
                    st.write("**Pesticide Strategy:**", advisory.get("pesticide_strategy", "N/A"))
                    st.write("**Yield Impact:**", advisory.get("yield_impact", "N/A"))

                    # ---------- PDF DOWNLOAD ----------
                    pdf_buffer = generate_pdf(result, crop)
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_buffer,
                        file_name="CropGuard_AI_Report.pdf",
                        mime="application/pdf"
                    )

        except requests.exceptions.RequestException as e:
            st.error("Failed to connect to backend.")
            st.text(str(e))
