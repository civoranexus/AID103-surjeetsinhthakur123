import cv2
import numpy as np

def preprocess_image(image_path, target_size=(28, 28)):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image could not be read")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, target_size)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    return img
