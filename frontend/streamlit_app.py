from unittest import result
import streamlit as st
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import os
import io

# ================= LANGUAGE DICTIONARY =================
LANG = {
    "English": {
        "lang_code": "en",
        "title": "CropGuard AI",
        "subtitle": "Intelligent Crop Disease Detection Platform",
        "input_params": "Input Parameters",
        "select_crop": "Select Crop (used only if no image uploaded)",
        "humidity": "Humidity (%)",
        "temperature": "Temperature (°C)",
        "upload_image": "Upload Image",
        "camera": "Or capture using camera",
        "image_auto": "Image detected → Crop will be auto-identified",
        "no_image": "No image uploaded → Crop selection will be used",
        "analyze": "Analyze Crop",
        "result": "AI Analysis Result",
        "crop_detected": "Crop Detected from Image",
        "crop_selected": "Crop Selected",
        "mismatch": "Selected crop does not match AI-detected crop. Results are based on image analysis.",
        "disease": "Disease",
        "severity": "Severity",
        "confidence": "Confidence",
        "risk": "Risk Score",
        "reasoning": "Explainable AI – Reasoning",
        "treatment": "Treatment & Advisory",
        "chemical": "Chemical Treatment",
        "organic": "Organic Treatment",
        "prevention": "Prevention",
        "download": "Download PDF Report",
        "gradcam": "Grad-CAM Visualization"
    },
    "Hindi": {
        "lang_code": "hi",
        "title": "क्रॉपगार्ड एआई",
        "subtitle": "बुद्धिमान फसल रोग पहचान प्रणाली",
        "input_params": "इनपुट पैरामीटर",
        "select_crop": "फसल चुनें (यदि छवि अपलोड नहीं की गई है)",
        "humidity": "नमी (%)",
        "temperature": "तापमान (°C)",
        "upload_image": "छवि अपलोड करें",
        "camera": "या कैमरे से फोटो लें",
        "image_auto": "छवि मिली → फसल स्वतः पहचानी जाएगी",
        "no_image": "कोई छवि नहीं → चयनित फसल उपयोग होगी",
        "analyze": "फसल का विश्लेषण करें",
        "result": "एआई विश्लेषण परिणाम",
        "crop_detected": "छवि से पहचानी गई फसल",
        "crop_selected": "चयनित फसल",
        "mismatch": "चयनित फसल एआई द्वारा पहचानी गई फसल से मेल नहीं खाती।",
        "disease": "रोग",
        "severity": "गंभीरता",
        "confidence": "विश्वास स्तर",
        "risk": "जोखिम स्तर",
        "reasoning": "एआई कारण विश्लेषण",
        "treatment": "उपचार और सलाह",
        "chemical": "रासायनिक उपचार",
        "organic": "जैविक उपचार",
        "prevention": "रोकथाम",
        "download": "पीडीएफ रिपोर्ट डाउनलोड करें",
        "gradcam": "ग्रैड-कैम दृश्य"
    },
    "Marathi": {
        "lang_code": "mr",
        "title": "क्रॉपगार्ड एआय",
        "subtitle": "बुद्धिमान पीक रोग ओळख प्रणाली",
        "input_params": "इनपुट घटक",
        "select_crop": "पीक निवडा (फोटो नसेल तर)",
        "humidity": "आर्द्रता (%)",
        "temperature": "तापमान (°C)",
        "upload_image": "फोटो अपलोड करा",
        "camera": "किंवा कॅमेऱ्याने फोटो घ्या",
        "image_auto": "फोटो सापडला → पीक आपोआप ओळखले जाईल",
        "no_image": "फोटो नाही → निवडलेले पीक वापरले जाईल",
        "analyze": "पीक विश्लेषण करा",
        "result": "एआय विश्लेषण निकाल",
        "crop_detected": "फोटोवरून ओळखलेले पीक",
        "crop_selected": "निवडलेले पीक",
        "mismatch": "निवडलेले पीक आणि एआयने ओळखलेले पीक वेगळे आहे.",
        "disease": "रोग",
        "severity": "तीव्रता",
        "confidence": "विश्वास पातळी",
        "risk": "जोखीम पातळी",
        "reasoning": "एआय कारण विश्लेषण",
        "treatment": "उपचार व सल्ला",
        "chemical": "रासायनिक उपचार",
        "organic": "सेंद्रिय उपचार",
        "prevention": "प्रतिबंध",
        "download": "पीडीएफ अहवाल डाउनलोड करा",
        "gradcam": "ग्रॅड-कॅम दृश्य"
    }
}

# ================= PAGE CONFIG =================
st.set_page_config(page_title="CropGuard AI", layout="wide", page_icon="🌱")

# ================= LANGUAGE SELECT =================
language = st.sidebar.selectbox("🌍 Language / भाषा", ["English", "Hindi", "Marathi"])
T = LANG[language]
t = lambda k: T[k]

# ================= HEADER =================
st.markdown(
    f"""
    <h1 style="text-align:center;">🌱 {t('title')}</h1>
    <h4 style="text-align:center;color:gray;">{t('subtitle')}</h4>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# ================= SIDEBAR =================
st.sidebar.header(f"🧪 {t('input_params')}")

CROP_OPTIONS = [
    "Tomato", "Potato", "Wheat", "Rice", "Maize",
    "Apple", "Grape", "Orange", "Peach", "Cherry", "Strawberry"
]

crop = st.sidebar.selectbox(t("select_crop"), CROP_OPTIONS)
humidity = st.sidebar.slider(t("humidity"), 30, 100, 70)
temperature = st.sidebar.slider(t("temperature"), 15, 45, 30)

st.sidebar.markdown("---")
uploaded_image = st.sidebar.file_uploader(t("upload_image"), type=["jpg", "jpeg", "png"])
camera_image = st.sidebar.camera_input(t("camera"))
image_file = uploaded_image if uploaded_image else camera_image

# ================= MAIN =================
left, right = st.columns([1.1, 1.4])

with left:
    if image_file:
        st.image(image_file, use_column_width=True)
        st.success(t("image_auto"))
    else:
        st.info(t("no_image"))

# ================= PDF =================
def generate_pdf(result, t):
    buffer = io.BytesIO()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(BASE_DIR, "fonts", "NotoSansDevanagari-Regular.ttf")

    pdfmetrics.registerFont(TTFont("Deva", font_path))

    # -------- QR CODE DATA --------
    qr_text = result.get("report_url")


    qr = qrcode.make(qr_text)
    qr_path = os.path.join(BASE_DIR, "temp_qr.png")
    qr.save(qr_path)

    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Deva", 16)
    c.drawString(50, height - 50, f"{t('title')} – Report")

    c.setFont("Deva", 12)
    y = height - 100

    c.drawString(50, y, f"{t('crop_detected')}: {result.get('crop_type')}")
    y -= 25
    c.drawString(50, y, f"{t('disease')}: {result.get('disease_detected')}")
    y -= 25
    c.drawString(50, y, f"{t('severity')}: {result.get('severity')}")
    y -= 25
    c.drawString(50, y, f"{t('confidence')}: {result.get('confidence')}")
    y -= 40

    treatment = result.get("advisory", {}).get("treatment", {})
    c.drawString(50, y, f"{t('chemical')}: {treatment.get('chemical', 'N/A')}")
    y -= 25
    c.drawString(50, y, f"{t('organic')}: {treatment.get('organic', 'N/A')}")
    y -= 25
    c.drawString(50, y, f"{t('prevention')}: {treatment.get('prevention', 'N/A')}")

    # -------- QR CODE ON PDF --------
    c.drawImage(qr_path, width - 160, 60, 100, 100)
    c.setFont("Deva", 9)
    c.drawString(width - 170, 45, "Scan QR for summary")

    c.showPage()
    c.save()
    buffer.seek(0)

    os.remove(qr_path)
    return buffer

# ================= ANALYZE =================
st.markdown("---")

if st.button(f"🔍 {t('analyze')}", use_container_width=True):
    with st.spinner("AI Processing..."):

        # >>> ADDED: SAFE API CALL
        try:
            response = requests.post(
                "http://127.0.0.1:5000/analyze",
                data={
                    "crop": crop,
                    "humidity": humidity,
                    "temperature": temperature,
                    "language": T["lang_code"]
                },
                files={"image": image_file} if image_file else None,
                timeout=60
            )

            if response.status_code != 200:
                st.error("⚠️ Server error. Please try again.")
                st.stop()

            result = response.json()
            st.session_state.analysis_result = result

        except requests.exceptions.RequestException:
            st.error("🚫 Unable to connect to AI server.")
            st.stop()

        st.toast("Analysis completed ✅")  

        st.markdown(f"## 🧠 {t('result')}")

        detected_crop = result.get("crop_type")

        if image_file:
            st.info(f"🌾 **{t('crop_detected')}:** {detected_crop}")
            if crop != detected_crop:
                st.warning(t("mismatch"))
        else:
            st.info(f"🌾 **{t('crop_selected')}:** {crop}")

        st.metric(t("disease"), result.get("disease_detected"))
        st.metric(t("severity"), result.get("severity"))
        
        # ================= SEVERITY COLOR CODING =================
        severity = str(result.get("severity", "")).lower()

        if "low" in severity:
            st.success("🟢 Low Risk – Crop condition is stable")
        elif "medium" in severity or "moderate" in severity:
            st.warning("🟡 Moderate Risk – Monitor crop closely")
        elif "high" in severity or "severe" in severity:
            st.error("🔴 High Risk – Immediate action required")
        else:
            st.info("ℹ️ Severity level unavailable")

        st.metric(t("confidence"), result.get("confidence"))

        # >>> ADDED: CONFIDENCE VISUALIZATION
        conf = result.get("confidence", 0)
        try:
            st.progress(int(float(conf) * 100))
            st.caption("Model confidence based on CNN + environmental features")
        except:
            st.info("Confidence calculated using rule-based logic")

        # ================= 🔊 VOICE SUMMARY =================
        voice_file = result.get("voice_summary")
        if voice_file:
            st.markdown("### 🔊 Voice Summary")
            st.audio(voice_file, format="audio/mp3")

        # ================= EXPLAINABLE AI =================
        reasoning = result.get("reasoning_clues", [])
        if reasoning:
            with st.expander(f"🧩 {t('reasoning')}"):
                for r in reasoning:
                    st.markdown(f"- {r}")

        # ================= GRAD-CAM =================
        explain_img = result.get("explainability_image")
        if explain_img:
            with st.expander(f"🔍 {t('gradcam')}"):
                st.image(explain_img, use_column_width=True)

        # ================= TREATMENT ADVISORY =================
        treatment = result.get("advisory", {}).get("treatment", {})
        with st.expander(f"💊 {t('treatment')}"):
            st.write(f"**{t('chemical')}:** {treatment.get('chemical', 'N/A')}")
            st.write(f"**{t('organic')}:** {treatment.get('organic', 'N/A')}")
            st.write(f"**{t('prevention')}:** {treatment.get('prevention', 'N/A')}")

        # ================= EXPERT CONNECT =================
        expert = result.get("expert_connect")
        if expert and expert.get("enabled"):
            st.warning("⚠️ High severity detected. Expert consultation recommended.")
            st.markdown(f"[💬 WhatsApp Expert]({expert['whatsapp']})")
            st.write(f"📞 Helpline: {expert['helpline']}")

        # ================= DOWNLOAD PDF =================
        pdf = generate_pdf(result, t)
        st.download_button(
            t("download"),
            pdf,
            "CropGuard_AI_Report.pdf",
            "application/pdf"
        )

        # ================= AI TRANSPARENCY =================
        st.caption("⚙️ Powered by CNN + Explainable AI + Environmental Context")

# ================= FEEDBACK =================
st.markdown("---")
st.markdown("### 📝 Farmer Feedback")

result = st.session_state.get("analysis_result")

if result is None:
    st.info("ℹ️ Analyze a crop to give feedback")
else:
    col1, col2, col3 = st.columns(3)

    # ---------- ✅ CORRECT ----------
    with col1:
        if st.button("👍 Correct"):
            feedback_payload = {
                "crop": result.get("crop_type"),
                "disease": result.get("disease_detected"),
                "confidence": result.get("confidence"),
                "correct": True,
                "comment": "Prediction is correct"
            }

            requests.post(
                "http://127.0.0.1:5000/feedback",
                json=feedback_payload
            )

            st.success("✅ Thank you! Feedback recorded.")

    # ---------- ❌ INCORRECT ----------
    with col2:
        if st.button("👎 Incorrect"):
            feedback_payload = {
                "crop": result.get("crop_type"),
                "disease": result.get("disease_detected"),
                "confidence": result.get("confidence"),
                "correct": False,
                "comment": "Prediction is incorrect"
            }

            requests.post(
                "http://127.0.0.1:5000/feedback",
                json=feedback_payload
            )

            st.warning("❌ Feedback recorded as incorrect.")

    # ---------- ❓ OTHER QUERY ----------
    with col3:
        other_comment = st.text_input("❓ Other issue / suggestion")

        if st.button("📩 Submit Query"):
            if other_comment.strip() == "":
                st.warning("Please enter your query")
            else:
                feedback_payload = {
                    "crop": result.get("crop_type"),
                    "disease": result.get("disease_detected"),
                    "confidence": result.get("confidence"),
                    "correct": None,
                    "comment": other_comment
                }

                requests.post(
                    "http://127.0.0.1:5000/feedback",
                    json=feedback_payload
                )

                st.success("📩 Query submitted successfully")

    st.markdown("## 📋 Post-Treatment Feedback")

    outcome = st.selectbox(
        "What happened after treatment?",
        ["Recovered", "No Change", "Condition Worsened"]
    )

    yield_change = st.selectbox(
        "Yield impact",
        ["Improved", "Same", "Reduced"]
    )

    days = st.number_input("Days after treatment", min_value=1, max_value=30)

    comment = st.text_area("Additional comments (optional)")

    if st.button("📨 Submit Outcome Feedback"):
        feedback_payload = {
            "crop": result.get("crop_type"),
            "disease": result.get("disease_detected"),
            "confidence": result.get("confidence"),
            "correct": True,
            "outcome": outcome,
            "yield_change": yield_change,
            "days_after_treatment": days,
            "comment": comment
        }

        requests.post("http://127.0.0.1:5000/feedback", json=feedback_payload)
        st.success("✅ Thank you! Your feedback helps improve the AI.")
