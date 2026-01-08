import tensorflow as tf
import numpy as np
import os
from image_preprocessing import preprocess_image

MODEL_PATH = "../model/crop_disease_cnn.h5"

CLASS_LABELS = ["Early Blight", "Leaf Curl Virus", "Healthy"]

model = None
if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
    except Exception as e:
        print("Model load error:", e)

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
    conf = float(np.max(preds))

    return {
        "disease": CLASS_LABELS[idx],
        "confidence": f"{conf * 100:.2f}%",
        "source": "cnn"
    }
