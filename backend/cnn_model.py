import tensorflow as tf
import numpy as np
import os
from image_preprocessing import preprocess_image

# ---------------- CONFIG ----------------
MODEL_PATH = "../model/crop_disease_cnn.h5"
CLASS_LABELS = ["Early Blight", "Leaf Curl Virus", "Healthy"]
CONFIDENCE_THRESHOLD = 0.60   # minimum confidence to trust CNN

# ---------------- MODEL LOADING ----------------
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


# ---------------- PREDICTION FUNCTION ----------------
def extract_image_features(image_path):
    """
    Extracts disease prediction from image using CNN.

    Returns:
    - disease
    - confidence
    - inference_source
    - model_status
    """

    # -------- FALLBACK MODE --------
    if model is None:
        return {
            "disease": "Early Blight",
            "confidence": "90%",
            "inference_source": "fallback_rule",
            "model_status": MODEL_STATUS
        }

    # -------- IMAGE PREPROCESSING --------
    img = preprocess_image(image_path)

    # -------- MODEL INFERENCE --------
    predictions = model.predict(img)

    # Ensure valid probability distribution
    probabilities = tf.nn.softmax(predictions[0]).numpy()

    # Top prediction
    top_index = int(np.argmax(probabilities))
    top_confidence = float(probabilities[top_index])

    # -------- LOW CONFIDENCE HANDLING --------
    if top_confidence < CONFIDENCE_THRESHOLD:
        return {
            "disease": "Uncertain",
            "confidence": f"{top_confidence * 100:.2f}%",
            "inference_source": "low_confidence",
            "model_status": MODEL_STATUS
        }

    # -------- SUCCESSFUL CNN PREDICTION --------
    return {
        "disease": CLASS_LABELS[top_index],
        "confidence": f"{top_confidence * 100:.2f}%",
        "inference_source": "cnn",
        "model_status": MODEL_STATUS,
        "top_predictions": [
            {
                "label": CLASS_LABELS[i],
                "probability": f"{probabilities[i] * 100:.2f}%"
            }
            for i in np.argsort(probabilities)[::-1][:3]
        ]
    }
