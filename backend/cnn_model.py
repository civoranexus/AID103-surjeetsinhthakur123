import tensorflow as tf
import numpy as np
import os
import json
import cv2

from image_preprocessing import preprocess_image
from gradcam_utils import generate_gradcam

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "crop_disease_cnn.h5")
LABELS_PATH = os.path.join(BASE_DIR, "model", "class_labels.json")

model = None
CLASS_LABELS = {}

print("MODEL PATH:", MODEL_PATH)
print("MODEL EXISTS:", os.path.exists(MODEL_PATH))
print("LABELS PATH:", LABELS_PATH)

# ---------------- LOAD CLASS LABELS ----------------
if os.path.exists(LABELS_PATH):
    with open(LABELS_PATH, "r") as f:
        CLASS_LABELS = json.load(f)
    print(f"✅ Loaded {len(CLASS_LABELS)} class labels")
else:
    print("❌ class_labels.json not found")

# ---------------- LOAD MODEL ----------------
if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ CNN model loaded")
    except Exception as e:
        print("❌ CNN model load error:", e)
        model = None
else:
    print("❌ Model file not found")

# ---------------- CNN PREDICTION ----------------
def extract_image_features(image_path):
    if model is None or not CLASS_LABELS:
        return {
            "disease": "Unknown",
            "confidence": "0%",
            "source": "fallback"
        }

    img = preprocess_image(image_path)
    preds = model.predict(img)[0]  # shape (38,)

    top_idx = int(np.argmax(preds))
    confidence = float(preds[top_idx]) * 100

    return {
        "disease": CLASS_LABELS[str(top_idx)],
        "confidence": f"{confidence:.2f}%",
        "source": "cnn",
        "top_predictions": [
            {
                "label": CLASS_LABELS[str(i)],
                "probability": f"{preds[i] * 100:.2f}%"
            }
            for i in np.argsort(preds)[::-1][:3]
        ]
    }

# ---------------- GRAD-CAM ----------------
def generate_explainability(image_path, last_conv_layer=None):
    if model is None:
        return None

    try:
        img = cv2.imread(image_path)
        if img is None:
            return None

        img_resized = cv2.resize(img, (28, 28))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        input_img = np.expand_dims(img_rgb / 255.0, axis=0)

        # Auto-detect last conv layer
        if last_conv_layer is None:
            for layer in reversed(model.layers):
                if "conv" in layer.name.lower():
                    last_conv_layer = layer.name
                    break

        if not last_conv_layer:
            return None

        heatmap = generate_gradcam(model, input_img, last_conv_layer)
        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap = np.uint8(255 * heatmap)

        overlay = cv2.addWeighted(
            cv2.applyColorMap(heatmap, cv2.COLORMAP_JET),
            0.5,
            img,
            0.5,
            0
        )

        output_path = image_path.replace(".jpg", "_gradcam.jpg")
        cv2.imwrite(output_path, overlay)

        return output_path

    except Exception as e:
        print("⚠️ Grad-CAM error:", e)
        return None
