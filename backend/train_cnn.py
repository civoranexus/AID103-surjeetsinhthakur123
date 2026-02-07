import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten,
    Dense, Dropout, Input
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os

# ---------------- CONFIG ----------------
IMG_SIZE = (28, 28)
BATCH_SIZE = 32
EPOCHS = 30

TRAIN_DIR = "datasets/train"
VAL_DIR = "datasets/valid"

# ---------------- DATA AUGMENTATION ----------------
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.1,
    brightness_range=[0.8, 1.2],
    horizontal_flip=True
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

val_gen = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

NUM_CLASSES = train_gen.num_classes
print("✅ Number of classes detected:", NUM_CLASSES)
print("✅ Class labels:", train_gen.class_indices)

# ---------------- CNN MODEL ----------------
model = Sequential([
    Input(shape=(28, 28, 3)),

    Conv2D(32, (3, 3), activation="relu", padding="same"),
    MaxPooling2D(2, 2),

    Conv2D(64, (3, 3), activation="relu", padding="same"),
    MaxPooling2D(2, 2),

    Conv2D(128, (3, 3), activation="relu", padding="same"),
    MaxPooling2D(2, 2),

    Flatten(),
    Dense(256, activation="relu"),
    Dropout(0.5),

    Dense(NUM_CLASSES, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ---------------- CALLBACKS ----------------
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

checkpoint = ModelCheckpoint(
    "crop_disease_cnn.h5",
    monitor="val_accuracy",
    save_best_only=True
)

# ---------------- TRAIN ----------------
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=[early_stop, checkpoint]
)

print("✅ Training completed")

# ---------------- SAVE CLASS LABELS ----------------
import json

labels = {v: k for k, v in train_gen.class_indices.items()}
with open("class_labels.json", "w") as f:
    json.dump(labels, f, indent=4)

print("✅ class_labels.json saved")
