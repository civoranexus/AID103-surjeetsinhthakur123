import streamlit as st
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# ================= LANGUAGE DICTIONARY =================
LANG = {
    "English": {
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
def generate_pdf(result):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "CropGuard AI Report")
    c.setFont("Helvetica", 12)
    c.drawString(50, 760, f"{t('disease')}: {result.get('disease_detected')}")
    c.drawString(50, 740, f"{t('severity')}: {result.get('severity')}")
    c.drawString(50, 720, f"{t('confidence')}: {result.get('confidence')}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ================= ANALYZE =================
st.markdown("---")

if st.button(f"🔍 {t('analyze')}", use_container_width=True):
    with st.spinner("AI Processing..."):
        response = requests.post(
            "http://127.0.0.1:5000/analyze",
            data={"crop": crop, "humidity": humidity, "temperature": temperature},
            files={"image": image_file} if image_file else None
        )

        result = response.json()

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
        st.metric(t("confidence"), result.get("confidence"))

        reasoning = result.get("reasoning_clues", [])
        if reasoning:
            st.markdown(f"### 🧩 {t('reasoning')}")
            for r in reasoning:
                st.markdown(f"- {r}")

        explain_img = result.get("explainability_image")
        if explain_img:
            st.markdown(f"### 🔍 {t('gradcam')}")
            st.image(explain_img, use_column_width=True)

        treatment = result.get("advisory", {}).get("treatment", {})
        st.markdown(f"### 💊 {t('treatment')}")
        st.write(f"**{t('chemical')}:** {treatment.get('chemical', 'N/A')}")
        st.write(f"**{t('organic')}:** {treatment.get('organic', 'N/A')}")
        st.write(f"**{t('prevention')}:** {treatment.get('prevention', 'N/A')}")

        pdf = generate_pdf(result)
        st.download_button(
            t("download"),
            pdf,
            "CropGuard_AI_Report.pdf",
            "application/pdf"
        )
