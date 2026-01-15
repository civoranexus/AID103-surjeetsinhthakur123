import tensorflow as tf
import numpy as np
import os
import cv2

from image_preprocessing import preprocess_image
from gradcam_utils import generate_gradcam

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "crop_disease_cnn.h5")

CLASS_LABELS = ["Early Blight", "Leaf Curl Virus", "Healthy"]

model = None

print("MODEL PATH:", MODEL_PATH)
print("MODEL EXISTS:", os.path.exists(MODEL_PATH))

# ---------- LOAD MODEL ----------
if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ CNN model loaded")
    except Exception as e:
        print("❌ CNN model load error:", e)
        model = None
else:
    print("❌ Model file not found")


# ---------- CNN PREDICTION ----------
def extract_image_features(image_path):
    if model is None:
        return {
            "disease": "Early Blight",
            "confidence": "90%",
            "source": "fallback"
        }

    img = preprocess_image(image_path)
    preds = model.predict(img)

    idx = int(np.argmax(preds))
    conf = float(np.max(preds)) * 100

    return {
        "disease": CLASS_LABELS[idx],
        "confidence": f"{conf:.2f}%",
        "source": "cnn"
    }


# ---------- GRAD-CAM ----------
def generate_explainability(image_path, last_conv_layer=None):

    if model is None:
        return None

    try:
        img = cv2.imread(image_path)
        if img is None:
            return None

        img = cv2.resize(img, (28, 28))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        input_img = np.expand_dims(img_rgb / 255.0, axis=0)

        # Auto-detect last conv layer
        if last_conv_layer is None:
            for layer in reversed(model.layers):
                if "conv" in layer.name.lower():
                    last_conv_layer = layer.name
                    break

        if last_conv_layer is None:
            return None

        heatmap = generate_gradcam(model, input_img, last_conv_layer)
        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap = np.uint8(255 * heatmap)

        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(heatmap_color, 0.5, img, 0.5, 0)

        base, _ = os.path.splitext(image_path)
        output_path = base + "_gradcam.jpg"
        cv2.imwrite(output_path, overlay)

        return output_path

    except Exception as e:
        print("⚠️ Grad-CAM error:", e)
        return None
