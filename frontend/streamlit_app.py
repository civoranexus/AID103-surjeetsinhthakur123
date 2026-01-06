import streamlit as st
import requests

st.set_page_config(page_title="CropGuard AI", layout="centered")

st.title("🌱 CropGuard AI")
st.subheader("Intelligent Crop Disease Detection Platform")

st.markdown("""
This system provides **AI-driven crop disease detection**
and **context-aware treatment recommendations**
to improve yield and reduce pesticide usage.
""")

# --- USER INPUT ---
crop = st.selectbox("Select Crop", ["Tomato"])
humidity = st.slider("Humidity (%)", 30, 100, 70)
temperature = st.slider("Temperature (°C)", 15, 45, 30)

if st.button("Analyze Crop"):
    payload = {
        "crop": crop,
        "humidity": humidity,
        "temperature": temperature
    }

    with st.spinner("Contacting AI Engine..."):
        response = requests.post(
            "http://127.0.0.1:5000/analyze",
            json=payload
        )

    result = response.json()

    st.success("AI Analysis Completed")

    st.markdown("### 🧠 AI Detection Result")
    st.write("**Disease Detected:**", result["disease_detected"])
    st.write("**Severity:**", result["severity"])
    st.write("**Confidence:**", result["confidence"])

    st.markdown("### 💊 Treatment & Advisory")
    st.write("**Chemical Treatment:**", result["advisory"]["treatment"]["chemical"])
    st.write("**Organic Treatment:**", result["advisory"]["treatment"]["organic"])
    st.write("**Prevention:**", result["advisory"]["treatment"]["prevention"])

    st.markdown("### 🌾 Optimization Strategy")
    st.write("**Pesticide Strategy:**", result["advisory"]["pesticide_strategy"])
    st.write("**Yield Impact:**", result["advisory"]["yield_impact"])
