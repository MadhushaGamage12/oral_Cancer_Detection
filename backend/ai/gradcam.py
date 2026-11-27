# ============================================================
# OralAI - Grad-CAM
# ============================================================
#
# Purpose:
# Generate a Grad-CAM heatmap for an uploaded oral image
# using the trained EfficientNetB0 model.
#
# The heatmap shows image regions that contributed most
# strongly to the model's predicted class.
#
# IMPORTANT:
# Grad-CAM is an explainability technique.
# It does NOT provide a medical diagnosis.
# Final diagnosis must be performed by a qualified clinician.
# ============================================================


import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = (
    r"D:\FYP\training\results_efficientnet"
    r"\efficientnetb0_best.keras"
)


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMG_HEIGHT = 224
IMG_WIDTH = 224


# ============================================================
# CLASS SETTINGS
# ============================================================
#
# Model classes:
#
# cancer     -> 0
# not_cancer -> 1
#
# The model uses sigmoid output.
#
# probability >= 0.5 -> not_cancer
# probability <  0.5 -> cancer
#
# ============================================================

CANCER_INDEX = 0
NOT_CANCER_INDEX = 1


# ============================================================
# LOAD MODEL
# ============================================================

print("========================================")
print("Loading EfficientNetB0 model...")
print("========================================")

model = keras.models.load_model(
    MODEL_PATH
)

print(
    "✅ EfficientNetB0 model loaded successfully."
)


# ============================================================
# FIND FINAL CONVOLUTIONAL LAYER
# ============================================================

def find_last_conv_layer():

    # The EfficientNetB0 base model is the first layer
    # inside the loaded Sequential model.

    base_model = model.layers[0]

    print(
        "\nSearching for Grad-CAM target layer..."
    )

    # --------------------------------------------------------
    # Try to find the standard EfficientNetB0 final
    # convolutional layer.
    # --------------------------------------------------------

    try:

        target_layer = base_model.get_layer(
            "top_conv"
        )

        print(
            "✅ Grad-CAM target layer:",
            target_layer.name
        )

        return target_layer

    except Exception:

        print(
            "⚠️ top_conv layer was not found."
        )

        # ----------------------------------------------------
        # Fallback:
        # Search backwards for a layer producing
        # a 4-dimensional feature map.
        # ----------------------------------------------------

        for layer in reversed(
            base_model.layers
        ):

            try:

                output_shape = layer.output.shape

                if len(output_shape) == 4:

                    print(
                        "✅ Fallback Grad-CAM layer:",
                        layer.name
                    )

                    return layer

            except Exception:

                continue

    raise ValueError(
        "Could not find a suitable convolutional "
        "layer for Grad-CAM."
    )


# ============================================================
# SET TARGET LAYER
# ============================================================

TARGET_LAYER = find_last_conv_layer()


# ============================================================
# GENERATE GRAD-CAM
# ============================================================

def generate_gradcam(
    image_path,
    output_path
):
    """
    Generate Grad-CAM heatmap for one image.

    Parameters
    ----------
    image_path : str
        Full path of the uploaded image.

    output_path : str
        Full path where the Grad-CAM image
        will be saved.

    Returns
    -------
    dict
        Prediction information and Grad-CAM data.
    """

    print(
        "\n========================================"
    )

    print(
        "Grad-CAM started"
    )

    print(
        "========================================"
    )

    print(
        "Image:",
        image_path
    )


    # ========================================================
    # CHECK IMAGE
    # ========================================================

    if not os.path.exists(
        image_path
    ):

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    # ========================================================
    # LOAD ORIGINAL IMAGE
    # ========================================================

    original_image = Image.open(
        image_path
    ).convert(
        "RGB"
    )

    original_width, original_height = (
        original_image.size
    )


    # ========================================================
    # PREPARE IMAGE
    # ========================================================

    resized_image = original_image.resize(
        (
            IMG_WIDTH,
            IMG_HEIGHT
        )
    )

    image_array = np.array(
        resized_image,
        dtype=np.float32
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )


    # ========================================================
    # GET EFFICIENTNETB0 BASE MODEL
    # ========================================================

    base_model = model.layers[0]


    # ========================================================
    # CREATE GRAD-CAM MODEL
    # ========================================================
    #
    # The loaded model is a Sequential model.
    #
    # Directly using:
    #
    #     model.output
    #
    # can produce:
    #
    # "The layer sequential has never been called..."
    #
    # Therefore, we use the EfficientNetB0 base model
    # and then manually pass its output through the
    # remaining layers.
    #
    # ========================================================

    grad_model = keras.models.Model(
        inputs=base_model.input,
        outputs=[
            TARGET_LAYER.output,
            base_model.output
        ]
    )


    # ========================================================
    # CALCULATE GRADIENTS
    # ========================================================

    with tf.GradientTape() as tape:

        # ----------------------------------------------------
        # Run EfficientNetB0 base model.
        # ----------------------------------------------------

        conv_outputs, base_output = grad_model(
            image_array,
            training=False
        )


        # ----------------------------------------------------
        # Pass the EfficientNetB0 output through the
        # remaining layers of the original model.
        # ----------------------------------------------------

        x = base_output

        for layer in model.layers[1:]:

            x = layer(
                x,
                training=False
            )

        predictions = x


        # ====================================================
        # GET NOT-CANCER PROBABILITY
        # ====================================================

        probability_not_cancer = (
            predictions[:, 0]
        )


        # ====================================================
        # DETERMINE PREDICTED CLASS
        # ====================================================

        predicted_index = tf.where(
            probability_not_cancer >= 0.5,
            NOT_CANCER_INDEX,
            CANCER_INDEX
        )


        # ====================================================
        # SELECT CLASS SCORE
        # ====================================================
        #
        # NOT CANCER:
        #     score = probability_not_cancer
        #
        # CANCER:
        #     score = 1 - probability_not_cancer
        #
        # This makes Grad-CAM correspond to the predicted
        # class rather than always explaining not-cancer.
        #
        # ====================================================

        class_score = tf.where(
            probability_not_cancer >= 0.5,
            probability_not_cancer,
            1.0 - probability_not_cancer
        )


    # ========================================================
    # CALCULATE GRADIENT
    # ========================================================

    gradients = tape.gradient(
        class_score,
        conv_outputs
    )

    if gradients is None:

        raise ValueError(
            "Gradients could not be calculated for "
            "the selected Grad-CAM layer."
        )


    # ========================================================
    # GLOBAL AVERAGE POOLING
    # ========================================================

    pooled_gradients = tf.reduce_mean(
        gradients,
        axis=(1, 2)
    )


    # ========================================================
    # REMOVE BATCH DIMENSION
    # ========================================================

    conv_outputs = conv_outputs[0]

    pooled_gradients = pooled_gradients[0]


    # ========================================================
    # WEIGHT FEATURE MAPS
    # ========================================================

    heatmap = tf.reduce_sum(
        conv_outputs * pooled_gradients,
        axis=-1
    )


    # ========================================================
    # APPLY RELU
    # ========================================================

    heatmap = tf.maximum(
        heatmap,
        0
    )


    # ========================================================
    # NORMALIZE HEATMAP
    # ========================================================

    max_value = tf.reduce_max(
        heatmap
    )

    heatmap = heatmap / (
        max_value + 1e-8
    )

    heatmap = heatmap.numpy()


    # ========================================================
    # CONVERT HEATMAP TO IMAGE
    # ========================================================

    heatmap_image = Image.fromarray(
        np.uint8(
            heatmap * 255
        )
    )

    heatmap_image = heatmap_image.resize(
        (
            original_width,
            original_height
        ),
        Image.Resampling.BILINEAR
    )


    # ========================================================
    # CREATE COLOUR HEATMAP
    # ========================================================

    heatmap_array = np.array(
        heatmap_image,
        dtype=np.float32
    ) / 255.0


    # --------------------------------------------------------
    # Red channel
    # --------------------------------------------------------

    red = np.clip(
        2.0 * heatmap_array,
        0,
        1
    )


    # --------------------------------------------------------
    # Green channel
    # --------------------------------------------------------

    green = np.clip(
        2.0 * (
            1.0 -
            np.abs(
                heatmap_array - 0.5
            )
        ),
        0,
        1
    )


    # --------------------------------------------------------
    # Blue channel
    # --------------------------------------------------------

    blue = np.clip(
        2.0 * (
            1.0 -
            heatmap_array
        ),
        0,
        1
    )


    # ========================================================
    # COMBINE RGB CHANNELS
    # ========================================================

    colour_heatmap = np.stack(
        [
            red,
            green,
            blue
        ],
        axis=-1
    )

    colour_heatmap = np.uint8(
        colour_heatmap * 255
    )


    colour_heatmap_image = Image.fromarray(
        colour_heatmap
    ).convert(
        "RGBA"
    )


    # ========================================================
    # ORIGINAL IMAGE RGBA
    # ========================================================

    original_rgba = original_image.convert(
        "RGBA"
    )


    # ========================================================
    # OVERLAY HEATMAP
    # ========================================================

    overlay_image = Image.blend(
        original_rgba,
        colour_heatmap_image,
        alpha=0.40
    )


    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:

        os.makedirs(
            output_directory,
            exist_ok=True
        )


    # ========================================================
    # SAVE GRAD-CAM IMAGE
    # ========================================================

    overlay_image.save(
        output_path
    )


    # ========================================================
    # GET FINAL PREDICTION INFORMATION
    # ========================================================

    probability_value = float(
        probability_not_cancer.numpy()[0]
    )


    if probability_value >= 0.5:

        prediction = "not cancer"

        confidence = (
            probability_value * 100
        )

    else:

        prediction = "cancer"

        confidence = (
            (1.0 - probability_value) * 100
        )


    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        "Grad-CAM COMPLETED"
    )

    print(
        "========================================"
    )

    print(
        "Prediction:",
        prediction
    )

    print(
        "Confidence:",
        round(
            confidence,
            2
        ),
        "%"
    )

    print(
        "Heatmap saved:",
        output_path
    )

    print(
        "========================================\n"
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "prediction":
            prediction,

        "confidence":
            round(
                confidence,
                2
            ),

        "heatmap_path":
            output_path,

        "heatmap":
            heatmap
    }
