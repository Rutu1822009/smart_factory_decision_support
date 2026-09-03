import tensorflow as tf
from tensorflow.keras import layers, models
from pathlib import Path

# Dataset path
DATASET_PATH = Path("datasets/dent_detection")

# Image settings
IMG_SIZE = (224, 224)
BATCH_SIZE = 4

# Load training data
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH / "train",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    validation_split=0.2,
    subset="training",
    seed=42
)

# Load validation data
val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH / "train",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    validation_split=0.2,
    subset="validation",
    seed=42
)

# Improve performance
AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.prefetch(AUTOTUNE)
val_ds = val_ds.prefetch(AUTOTUNE)

# Simple CNN model
model = models.Sequential([
    layers.Rescaling(1.0 / 255, input_shape=(224, 224, 3)),

    layers.Conv2D(32, 3, activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(128, 3, activation="relu"),
    layers.MaxPooling2D(),

    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.4),

    layers.Dense(1, activation="sigmoid")
])

# Compile
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# Train
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=20
)

# Save model
model.save("dent_detection_model.keras")

print("\n✅ Model training completed!")
print("✅ Model saved as dent_detection_model.keras")