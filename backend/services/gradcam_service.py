# routes.py
#     ↓
# gradcam_service.py
#     ↓
# ai/gradcam.py
#
import os
from ai.gradcam import generate_gradcam

# GRAD-CAM OUTPUT FOLDER

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_FOLDER = os.path.join( BASE_DIR, "uploads")
GRADCAM_UPLOAD_FOLDER = os.path.join( UPLOAD_FOLDER, "gradcam")

# Create folder if it does not exist
os.makedirs( GRADCAM_UPLOAD_FOLDER, exist_ok=True )

# GENERATE SCREENING GRAD-CAM

def generate_screening_gradcam(
    screening_id,
    image_path
):
    """
    Generate Grad-CAM for a screening image.
    Parameters
    ----------
    screening_id : int
        ID of the screening record.
    image_path : str
        Full physical path of the uploaded image.
    Returns
    -------
    str
        Relative Grad-CAM path to store in database.
    """

    # Check original image
    if not os.path.exists(image_path):
        raise FileNotFoundError( f"Screening image not found: {image_path}")
    
    # Grad-CAM filename
    gradcam_filename = ( f"screening_{screening_id}_gradcam.png")

    # Full physical output path

    gradcam_full_path = os.path.join( GRADCAM_UPLOAD_FOLDER,  gradcam_filename )

    print("\n========================================" )
    print( "Generating Grad-CAM")
    print(f"Screening ID : {screening_id}")
    print(f"Input image  : {image_path}")
    print(f"Output image : {gradcam_full_path}")
    print( "========================================")

    # Call actual Grad-CAM AI function

    result = generate_gradcam( image_path, gradcam_full_path)

    # Make sure Grad-CAM file was created

    if not os.path.exists( gradcam_full_path):
        raise Exception(
            "Grad-CAM generation completed "
            "but output image was not created."
        )

    # Database path
    # We store a relative path in MySQL.
    # Example:uploads/gradcam/screening_5_gradcam.png

    gradcam_path = os.path.join(
        "uploads",
        "gradcam",
        gradcam_filename
    ).replace("\\", "/")

    print( "\n✅ Grad-CAM generated successfully.")

    print( "Database path:", gradcam_path )

    # Return useful information
    return {
        "path": gradcam_path,
        "full_path": gradcam_full_path,
        "prediction": result.get(
            "prediction"
        ) if result else None,
        "confidence": result.get(
            "confidence"
        ) if result else None
    }
