import tensorflow as tf
import numpy as np
import os
from image_preprocessing import preprocess_image

MODEL_PATH = "../model/crop_disease_cnn.h5"
CLASS_LABELS = ["Early Blight", "Leaf Curl Virus", "Healthy"]

CONFIDENCE_THRESHOLD = 60.0  # percent

model = None
MODEL_STATUS = "NOT_LOADED"

if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        MODEL_STATUS = "LOADED"
    except Exception as e:
        print("⚠️ CNN model load error:", e)
        MODEL_STATUS = "LOAD_FAILED"
else:
    MODEL_STATUS = "MODEL_NOT_FOUND"


def extract_image_features(image_path):
    if model is None:
        return {
            "disease": "Early Blight",
            "confidence": "90%",
            "source": "fallback",
            "inference_source": "fallback",
            "model_status": MODEL_STATUS
        }

    img = preprocess_image(image_path)
    preds = model.predict(img)

    probs = tf.nn.softmax(preds[0]).numpy()
    idx = int(np.argmax(probs))
    conf_percent = float(probs[idx] * 100)

    if conf_percent < CONFIDENCE_THRESHOLD:
        return {
            "disease": "Uncertain",
            "confidence": f"{conf_percent:.2f}%",
            "source": "cnn",
            "inference_source": "low_confidence",
            "model_status": MODEL_STATUS
        }

    return {
        "disease": CLASS_LABELS[idx],
        "confidence": f"{conf_percent:.2f}%",
        "source": "cnn",
        "inference_source": "cnn",
        "model_status": MODEL_STATUS,
        "top_predictions": [
            {
                "label": CLASS_LABELS[i],
                "probability": f"{probs[i] * 100:.2f}%"
            }
            for i in np.argsort(probs)[::-1][:3]
        ]
    }
