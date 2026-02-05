import tensorflow as tf
import numpy as np
import cv2
import json

MODEL_PATH = "model/crop_disease_cnn.tflite"
LABELS_PATH = "model/class_labels.json"

with open(LABELS_PATH) as f:
    LABELS = json.load(f)

CLASS_LABELS = [LABELS[str(i)] for i in range(len(LABELS))]

interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def preprocess(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (28, 28))
    img = img / 255.0
    return np.expand_dims(img, axis=0).astype(np.float32)

def run_offline_inference(image_path):
    input_data = preprocess(image_path)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    preds = interpreter.get_tensor(output_details[0]['index'])[0]
    idx = int(np.argmax(preds))
    confidence = float(preds[idx]) * 100

    return {
        "crop_disease_label": CLASS_LABELS[idx],
        "confidence": f"{confidence:.2f}%",
        "source": "TFLITE_EDGE"
    }
