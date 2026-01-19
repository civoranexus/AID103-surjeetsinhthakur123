import tensorflow as tf
import numpy as np
import json
import os
import cv2

from image_preprocessing import preprocess_image
from gradcam_utils import generate_gradcam

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "crop_disease_cnn.h5")
LABELS_PATH = os.path.join(BASE_DIR, "model", "class_labels.json")

with open(LABELS_PATH) as f:
    LABELS = json.load(f)

CLASS_LABELS = [LABELS[str(i)] for i in range(len(LABELS))]

model = tf.keras.models.load_model(MODEL_PATH)


def extract_image_features(image_path):
    img = preprocess_image(image_path)
    preds = model.predict(img)

    idx = int(np.argmax(preds))
    confidence = float(np.max(preds)) * 100

    return {
        "disease": CLASS_LABELS[idx],
        "confidence": f"{confidence:.2f}%",
        "source": "cnn"
    }


def generate_explainability(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (28, 28))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    input_img = np.expand_dims(img_rgb / 255.0, axis=0)

    last_conv = next(
        layer.name for layer in reversed(model.layers)
        if "conv" in layer.name.lower()
    )

    heatmap = generate_gradcam(model, input_img, last_conv)
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap = np.uint8(255 * heatmap)

    overlay = cv2.addWeighted(
        cv2.applyColorMap(heatmap, cv2.COLORMAP_JET),
        0.5, img, 0.5, 0
    )

    out_path = image_path.replace(".jpg", "_gradcam.jpg")
    cv2.imwrite(out_path, overlay)
    return out_path
