import streamlit as st
import requests

st.set_page_config(page_title="CropGuard AI", layout="centered")

st.title("🌱 CropGuard AI")
st.subheader("Intelligent Crop Disease Detection Platform")

st.markdown("""
This system provides **AI-driven crop disease detection**
and **context-aware treatment recommendations**.
You can analyze crops **with or without uploading an image**.
""")

# ---------------- USER INPUTS ----------------
CROP_OPTIONS = [
    "Tomato",
    "Potato",
    "Wheat",
    "Rice",
    "Maize"
]

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

                    st.markdown("### 💊 Treatment & Advisory")
                    advisory = result.get("advisory", {})
                    treatment = advisory.get("treatment", {})

                    if isinstance(treatment, dict):
                        st.write("**Chemical Treatment:**", treatment.get("chemical", "N/A"))
                        st.write("**Organic Treatment:**", treatment.get("organic", "N/A"))
                        st.write("**Prevention:**", treatment.get("prevention", "N/A"))
                    else:
                        st.write(treatment)

                    st.markdown("### 🌾 Optimization Strategy")
                    st.write("**Pesticide Strategy:**", advisory.get("pesticide_strategy", "N/A"))
                    st.write("**Yield Impact:**", advisory.get("yield_impact", "N/A"))

        except requests.exceptions.RequestException as e:
            st.error("Failed to connect to backend.")
            st.text(str(e))
