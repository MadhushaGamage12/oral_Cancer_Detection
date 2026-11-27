# =========================================================
# ORALAI - EFFICIENTNETB0 AI PREDICTION
# =========================================================
#
# This module:
#
# 1. Loads the trained EfficientNetB0 model.
# 2. Loads a patient's uploaded oral image.
# 3. Prepares the image for the model.
# 4. Runs the AI prediction.
# 5. Converts the model output into:
#       - Cancer / Not Cancer
#       - Confidence
#       - Risk Status
#
# IMPORTANT:
# This system is a screening support system.
# The AI result is NOT a medical diagnosis.
# =========================================================


# =========================================================
# IMPORT LIBRARIES
# =========================================================

import os

import numpy as np

from tensorflow import keras

from tensorflow.keras.preprocessing.image import (
    load_img,
    img_to_array
)


# =========================================================
# PROJECT BASE DIRECTORY
# =========================================================
#
# Current file:
#
# D:\FYP\backend\ai\efficientnet_predict.py
#
# Going up:
#
# efficientnet_predict.py
#       ↓
# ai
#       ↓
# backend
#       ↓
# FYP
#
# Therefore BASE_DIR = D:\FYP
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# =========================================================
# EFFICIENTNETB0 MODEL PATH
# =========================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "training",
    "results_efficientnet",
    "efficientnetb0_best.keras"
)


# =========================================================
# IMAGE SIZE
# =========================================================
#
# The EfficientNetB0 model was trained using:
#
# 224 x 224
#
# Therefore inference must use the same input size.
# =========================================================

IMAGE_SIZE = (224, 224)


# =========================================================
# LOAD MODEL
# =========================================================
#
# The model is loaded once when Flask starts.
#
# We do NOT load the model for every prediction because
# loading the model repeatedly would be slow.
# =========================================================

print("Loading EfficientNetB0 model...")

if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"EfficientNetB0 model not found at: {MODEL_PATH}"
    )


model = keras.models.load_model(MODEL_PATH)


print("✅ EfficientNetB0 model loaded successfully.")


# =========================================================
# PREDICT IMAGE
# =========================================================

def predict_image(image_path):

    """
    Run EfficientNetB0 prediction on one uploaded image.

    Parameters:
        image_path:
            Full path to the uploaded image.

    Returns:
        Dictionary containing:

        prediction
        confidence
        cancer_probability
        not_cancer_probability
        risk_status
    """


    # =====================================================
    # CHECK IMAGE
    # =====================================================

    if not os.path.exists(image_path):

        raise FileNotFoundError(
            f"Image not found at: {image_path}"
        )


    # =====================================================
    # LOAD IMAGE
    # =====================================================

    image = load_img(
        image_path,
        target_size=IMAGE_SIZE
    )


    # =====================================================
    # CONVERT IMAGE TO NUMPY ARRAY
    # =====================================================

    image_array = img_to_array(image)


    # =====================================================
    # ADD BATCH DIMENSION
    # =====================================================
    #
    # Before:
    #
    # (224, 224, 3)
    #
    # After:
    #
    # (1, 224, 224, 3)
    #
    # The model expects a batch dimension.
    # =====================================================

    image_array = np.expand_dims(
        image_array,
        axis=0
    )


    # =====================================================
    # IMPORTANT: DO NOT USE /255
    # =====================================================
    #
    # During EfficientNetB0 training, we did NOT manually
    # use:
    #
    # image / 255
    #
    # EfficientNetB0 handles its preprocessing internally.
    #
    # Therefore inference must follow the same setup.
    # =====================================================


    # =====================================================
    # RUN MODEL PREDICTION
    # =====================================================

    model_output = model.predict(
        image_array,
        verbose=0
    )


    # =====================================================
    # UNDERSTAND THE MODEL OUTPUT
    # =====================================================
    #
    # Training class order:
    #
    # cancer     = class 0
    # not_cancer = class 1
    #
    # The Dense layer is:
    #
    # Dense(1, activation="sigmoid")
    #
    # Therefore sigmoid output represents:
    #
    # NOT CANCER probability
    #
    # So:
    #
    # not_cancer_probability = model output
    #
    # cancer_probability =
    #     1 - not_cancer_probability
    # =====================================================

    not_cancer_probability = float(
        model_output[0][0]
    )


    cancer_probability = (
        1.0 - not_cancer_probability
    )


    # =====================================================
    # DETERMINE FINAL PREDICTION
    # =====================================================
    #
    # Threshold = 0.50
    #
    # Cancer probability >= 50%
    #       → Cancer
    #
    # Otherwise
    #       → Not Cancer
    # =====================================================

    if cancer_probability >= 0.50:

        prediction = "Cancer"

        confidence = (
            cancer_probability * 100
        )

        risk_status = "High Risk"

    else:

        prediction = "Not Cancer"

        confidence = (
            not_cancer_probability * 100
        )

        risk_status = "Low Risk"


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "prediction": prediction,

        "confidence": round(
            confidence,
            2
        ),

        "cancer_probability": round(
            cancer_probability * 100,
            2
        ),

        "not_cancer_probability": round(
            not_cancer_probability * 100,
            2
        ),

        "risk_status": risk_status
    }
