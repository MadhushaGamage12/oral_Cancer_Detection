# OralAI - NLP Explanation Generator
# Purpose:Generate a clinician-friendly explanation from the already calculated AI screening results.
# IMPORTANT:
# This module DOES NOT:
#   - classify the image
#   - calculate cancer probability
#   - generate Grad-CAM
#   - make a medical diagnosis

# It only converts existing AI results into a human-readable explanation.


def generate_screening_explanation(
    prediction,
    confidence,
    risk_status,
    gradcam_path=None
):
    """
    Generate a clinician-friendly screening explanation.

    Parameters:
        prediction: AI prediction such as "Cancer" or "Not Cancer"
        confidence: Model confidence percentage
        risk_status: Existing risk status returned by the prediction model
        gradcam_path: Path of the generated Grad-CAM heatmap
    Returns:
        String containing the generated explanation.
    """
# Safely handle missing values

    prediction_text = str(prediction if prediction is not None else "Unknown"
    ).strip()

    risk_text = str(risk_status if risk_status is not None else "Unknown"
    ).strip()

# Convert confidence to a readable percentage.
    try: 
        confidence_value = float(confidence)
        confidence_text = f"{confidence_value:.2f}%"
    except (TypeError, ValueError):
        confidence_value = None
        confidence_text = "an unavailable confidence value"

# Check whether Grad-CAM was generated
    gradcam_available = bool(gradcam_path)

 # Normalize prediction text
    prediction_lower = prediction_text.lower()

# CANCER PREDICTION

    if prediction_lower == "cancer":

        explanation = (
            f"The EfficientNetB0 screening model classified the "
            f"uploaded oral image as Cancer with a model confidence "
            f"of {confidence_text}. "
        )

        explanation += (
            f"The recorded screening risk status is "
            f"'{risk_text}'. "
        )

        if gradcam_available:

            explanation += (
                "A Grad-CAM visualization was generated to indicate "
                "the image regions that contributed to the model's "
                "prediction. "
            )

        else:

            explanation += (
                "A Grad-CAM visualization was not available for "
                "this screening. "
            )

        explanation += (
            "This result represents an AI-generated screening output "
            "and should not be considered a final medical diagnosis. "
            "The result and the associated visualization should be "
            "reviewed by a qualified clinician."
        )

        return explanation

# NOT CANCER PREDICTION

    elif prediction_lower in [
        "not cancer",
        "not_cancer",
        "non-cancer",
        "non cancer"
    ]:

        explanation = (
            f"The EfficientNetB0 screening model classified the "
            f"uploaded oral image as Not Cancer with a model "
            f"confidence of {confidence_text}. "
        )

        explanation += (
            f"The recorded screening risk status is "
            f"'{risk_text}'. "
        )

        if gradcam_available:

            explanation += (
                "A Grad-CAM visualization was generated to provide "
                "visual information about the image regions that "
                "contributed to the model's prediction. "
            )
        else:

            explanation += (
                "A Grad-CAM visualization was not available for "
                "this screening. "
            )
        explanation += (
            "This result represents an AI-generated screening output "
            "and does not exclude the possibility of a clinical "
            "condition. Final assessment should be performed by a "
            "qualified clinician when clinically appropriate."
        )
        return explanation

# UNKNOWN / OTHER PREDICTION
    else:
        explanation = (
            f"The AI screening process produced a prediction of "
            f"'{prediction_text}' with a model confidence of "
            f"{confidence_text}. "
        )
        explanation += (
            f"The recorded screening risk status is "
            f"'{risk_text}'. "
        )
        if gradcam_available:
            explanation += (
                "A Grad-CAM visualization was generated to support "
                "interpretation of the model output. "
            )
        else:
            explanation += (
                "A Grad-CAM visualization was not available. "
            )
        explanation += (
            "The result is an AI-generated screening output and "
            "should be interpreted by a qualified clinician rather "
            "than being treated as a final diagnosis."
        )
        return explanation
