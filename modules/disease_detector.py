import os
import numpy as np
from PIL import Image

IMG_SIZE   = (224, 224)
CLASSES = ["BacterialBlights", "Healthy", "Mosaic", "RedRot", "Rust", "Yellow"]
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "model", "caneguard_v2_best.keras"
)

_CACHED_MODEL = None


def load_model():
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        print("Model already loaded — returning cached!")
        return _CACHED_MODEL

    print("=" * 50)
    print(f"Model path : {MODEL_PATH}")
    print(f"File exists: {os.path.exists(MODEL_PATH)}")

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

    import tensorflow as tf
    _CACHED_MODEL = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
    print("=" * 50)
    return _CACHED_MODEL


def predict_image(img_path, model=None):
    if model is None:
        model = load_model()

    img       = Image.open(img_path).convert("RGB").resize(IMG_SIZE)
    img_array = np.array(img, dtype=np.float32) / 255.0  # ← yeh add karo
    img_array = np.expand_dims(img_array, axis=0)

    predictions   = model.predict(img_array, verbose=0)
    predicted_idx = int(np.argmax(predictions[0]))
    confidence    = float(np.max(predictions[0])) * 100

    if confidence < 40.0:
        return {
            "disease":    "unknown",
            "confidence": round(confidence, 2),
            "all_scores": {
                cls.lower(): round(float(predictions[0][i]) * 100, 2)
                for i, cls in enumerate(CLASSES)
            },
        }

    return {
        "disease":    CLASSES[predicted_idx].lower(),
        "confidence": round(confidence, 2),
        "all_scores": {
            cls.lower(): round(float(predictions[0][i]) * 100, 2)
            for i, cls in enumerate(CLASSES)
        },
    }