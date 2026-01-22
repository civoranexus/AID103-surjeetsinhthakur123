from gtts import gTTS
import os
import uuid

def generate_voice_summary(result, lang_code="en"):
    """
    lang_code:
    en = English
    hi = Hindi
    mr = Marathi
    """

    # ---------- TEXT BASED ON LANGUAGE ----------
    if lang_code == "hi":
        text = f"""
फसल {result.get('crop_type')} में
{result.get('disease_detected')} रोग पाया गया है।
रोग की गंभीरता {result.get('severity')} है।
उपचार तुरंत करें।
"""
    elif lang_code == "mr":
        text = f"""
{result.get('crop_type')} पिकामध्ये
{result.get('disease_detected')} रोग आढळला आहे.
रोगाची तीव्रता {result.get('severity')} आहे.
त्वरित उपचार करा.
"""
    else:
        text = f"""
Crop {result.get('crop_type')} has
{result.get('disease_detected')} disease.
Severity level is {result.get('severity')}.
Immediate treatment is advised.
"""

    # ---------- AUDIO FILE ----------
    os.makedirs("static/voice", exist_ok=True)
    filename = f"static/voice/{uuid.uuid4().hex}.mp3"

    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(filename)

    return "/" + filename.replace("\\", "/")
