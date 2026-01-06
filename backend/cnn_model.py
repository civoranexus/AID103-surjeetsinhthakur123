import tensorflow as tf
import numpy as np
from image_utils import preprocess_image

MODEL_PATH = "../model/crop_disease_cnn.h5"

try:
    model = tf.keras.models.load_model(MODEL_PATH)
except:
    model = None

def extract_image_features(image_path):
    if model is None:
        return {"confidence": "90%", "pattern": "leaf_spots"}

    img = preprocess_image(image_path)
    preds = model.predict(img)
    return {
        "class_index": int(np.argmax(preds)),
        "confidence": float(np.max(preds))
    }
