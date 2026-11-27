# This file contains all API endpoints of the OralAI system.
# Main responsibilities:
#   1. User Signup
#   2. User Login
#   3. User Profile
#   4. Change User Name
#   5. Change User Password
#   6. Upload Profile Photo
#   7. Remove Profile Photo
#   8. Create New Screening
#   9. Get Patient Screening History
#   10. Get One Screening Result
#   11. Update Screening Result
#   12. Run EfficientNetB0 AI Prediction

# IMPORT REQUIRED LIBRARIES

from flask import Blueprint, request, jsonify, send_from_directory, send_file
import bcrypt
import os
import uuid

from database import get_connection
from ai.efficientnet_predict import predict_image
from services.gradcam_service import generate_screening_gradcam
from services.nlp_explanation import generate_screening_explanation
from services.report_service import generate_screening_report


# CREATE BLUEPRINT
api = Blueprint("api", __name__)

# BASE DIRECTORY

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# UPLOAD FOLDER
# Screening images: D:\FYP\backend\uploads

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)


# PROFILE PHOTO FOLDER
# Profile photos: D:\FYP\backend\uploads\profiles

PROFILE_UPLOAD_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "profiles"
)

# CREATE REQUIRED FOLDERS

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROFILE_UPLOAD_FOLDER):
    os.makedirs(PROFILE_UPLOAD_FOLDER)

# SERVE UPLOADED SCREENING IMAGES Example:http://127.0.0.1:5000/uploads/user_6_02.jpeg

@api.route(
    "/uploads/<path:filename>",
    methods=["GET"]
)
def serve_uploaded_image(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )

# SERVE PROFILE PHOTOS: Example:http://127.0.0.1:5000/profile-photos/profile_6_xxx.jpg

@api.route(
    "/profile-photos/<path:filename>",
    methods=["GET"]
)
def serve_profile_photo(filename):
    return send_from_directory(
        PROFILE_UPLOAD_FOLDER,
        filename
    )

# HOME / TEST ROUTE

@api.route("/", methods=["GET"])
def home():
    return "✅ Flask connected to MySQL successfully!"

# SIGNUP
@api.route( "/signup", methods=["POST"])
def signup():
    connection = None
    cursor = None
    try:
        data = request.get_json()
        # Check whether data was received.

        if not data:
            return jsonify({ "success": False,"message":  "No data received."  }), 400
        fullname = data.get("fullname")
        email = data.get("email")
        password = data.get("password")

        # Validate required fields.

        if not fullname or not email or not password:
            return jsonify({ "success": False, "message": "Full name, email and password are required."  }), 400

        # Hash password using bcrypt.

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )
        # Connect to MySQL.
        connection = get_connection()
        cursor = connection.cursor()

        # Insert new user.
        # first_login_at is NOT inserted here.It will be automatically saved when the user. successfully logs in for the first time.
     
        query = """
        INSERT INTO users( fullname, email, password ) VALUES ( %s,%s,%s) """

        cursor.execute(
            query,
            (
                fullname.strip(),
                email.strip(),
                hashed_password.decode("utf-8")
            )
        )
        connection.commit()
        return jsonify({ "success": True,"message":"User registered successfully!"}), 201

    except Exception as e:
        print("Signup error:", e )
        if connection:
            connection.rollback()
        return jsonify({
            "success": False,
            "message":
                str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ============================================================
# LOGIN - ADMIN + PATIENT
# ============================================================

@api.route("/login", methods=["POST"])
def login():
    connection = None
    cursor = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400

        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password are required."
            }), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # 1. CHECK ADMIN TABLE FIRST
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM admins
            WHERE email = %s
            """,
            (email,)
        )

        admin = cursor.fetchone()

        if admin:
            stored_hash = admin.get("password")

            if not stored_hash or not bcrypt.checkpw(
                password.encode("utf-8"),
                stored_hash.encode("utf-8")
            ):
                return jsonify({
                    "success": False,
                    "message": "Incorrect password."
                }), 401

            # ADMIN LOGIN SUCCESS
            # Do not return the password/hash.

            return jsonify({
                "success": True,
                "message": "Admin login successful!",
                "role": "admin",
                "admin": {
                    "id": admin["id"],
                    "fullname": admin.get(
                        "fullname",
                        admin.get("name", "Admin")
                    ),
                    "email": admin["email"]
                }
            }), 200

        # ----------------------------------------------------
        # 2. CHECK PATIENT TABLE
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Email not found."
            }), 404

        stored_hash = user.get("password")

        if not stored_hash or not bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        ):
            return jsonify({
                "success": False,
                "message": "Incorrect password."
            }), 401

        # Record the patient's first successful login.

        cursor.execute(
            """
            UPDATE users
            SET first_login_at = COALESCE(first_login_at, NOW())
            WHERE id = %s
            """,
            (user["id"],)
        )

        connection.commit()

        # Return patient details.

        cursor.execute(
            """
            SELECT
                id,
                fullname,
                email,
                first_login_at,
                profile_photo
            FROM users
            WHERE id = %s
            """,
            (user["id"],)
        )

        updated_user = cursor.fetchone()

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "role": "patient",
            "user": {
                "id": updated_user["id"],
                "fullname": updated_user["fullname"],
                "email": updated_user["email"],
                "first_login_at": updated_user["first_login_at"],
                "profile_photo": updated_user["profile_photo"]
            }
        }), 200

    except Exception as e:
        print("Login error:", repr(e))

        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Login failed due to a server error."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# GET USER PROFILE
# URL: GET /users/<user_id> Returns: id, fullname, email,  first_login_at,  profile_photo, profile_photo_url

@api.route( "/users/<int:user_id>", methods=["GET"])

def get_user_profile(user_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT
            id,
            fullname,
            email,
            first_login_at,
            profile_photo
        FROM users
        WHERE id = %s
        """

        cursor.execute( query, (user_id,) )
        user = cursor.fetchone()

         # Check user.

        if not user:
            return jsonify({
                "success": False,
                "message":  "User not found." }), 404

         # Create profile photo URL.

        if user["profile_photo"]:
            user["profile_photo_url"] = (
                "/profile-photos/"
                + user["profile_photo"] )

        else:
            user["profile_photo_url"] = None

        return jsonify({
            "success": True,
            "user": user }), 200

    except Exception as e:
        print("Get user profile error:", e  )

        return jsonify({
            "success": False,
            "message": "Failed to retrieve user profile.",
            "error": str(e)
        }), 500


    finally:
        if cursor: cursor.close()
        if connection: connection.close()


# CHANGE USER NAME
# URL:PUT /users/<user_id>/name  - Request JSON:{"fullname": "New Name"}


@api.route( "/users/<int:user_id>/name",  methods=["PUT"])
def change_user_name(user_id):
    connection = None
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No data received." }), 400
        fullname = data.get("fullname")
        if not fullname or not fullname.strip():
            return jsonify({
                "success": False,
                "message":"Full name is required." }), 400
        fullname = fullname.strip()
        connection = get_connection()
        cursor = connection.cursor()

        # Check whether user exists.

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        # Update fullname.

        cursor.execute(
            """
            UPDATE users
            SET fullname = %s
            WHERE id = %s
            """,
            (fullname, user_id )  )

        connection.commit()

        return jsonify({
            "success": True,
            "message":"Full name updated successfully.",
            "fullname": fullname}), 200


    except Exception as e:
        print("Change name error:", e )
        if connection:  connection.rollback()


        return jsonify({
            "success": False,
            "message": "Failed to update full name.",
            "error": str(e)
        }), 500


    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# CHANGE USER PASSWORD
# URL: PUT /users/<user_id>/password
# Request JSON: {"current_password": "...",  "new_password": "..."}

@api.route( "/users/<int:user_id>/password",  methods=["PUT"] )
def change_user_password(user_id):
    connection = None
    cursor = None

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No data received." }), 400


        current_password = data.get( "current_password" )

        new_password = data.get( "new_password")


        if not current_password or not new_password:
            return jsonify({
                "success": False,
                "message": "Current and new passwords are required."  }), 400

        # Minimum password length.

        if len(new_password) < 6:
            return jsonify({
                "success": False,
                "message": "New password must be at least 6 characters." }), 400

        connection = get_connection()
        cursor = connection.cursor( dictionary=True )

        # Get existing password.

        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE id = %s
            """,
            (user_id,) )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message":"User not found." }), 404

         # Verify current password.

        if not bcrypt.checkpw(
            current_password.encode("utf-8"),
            user["password"].encode("utf-8") ):

            return jsonify({
                "success": False,
                "message":"Current password is incorrect." }), 401

        # Hash new password.

        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt() )

        # Update password.

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (hashed_password.decode("utf-8"),user_id ))

        connection.commit()

        return jsonify({
            "success": True,
            "message":"Password changed successfully." }), 200


    except Exception as e:
        print( "Change password error:", e )

        if connection: connection.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to change password.",
            "error": str(e) }), 500


    finally:
        if cursor: cursor.close()
        if connection:connection.close()


# UPLOAD / CHANGE PROFILE PHOTO
# URL: POST /users/<user_id>/profile-photo
# Form-data: photo = image file  Allowed: JPG, JPEG, PNG, WEBP

@api.route("/users/<int:user_id>/profile-photo", methods=["POST"] )
def upload_profile_photo(user_id):
    connection = None
    cursor = None

    try:
        photo = request.files.get("photo")
              # Validate file.

        if not photo:
            return jsonify({
                "success": False,
                "message": "Profile photo is required." }), 400

        if photo.filename == "":
            return jsonify({
                "success": False,
                "message": "No profile photo selected." }), 400

        # Allowed extensions.
        allowed_extensions = { "jpg", "jpeg",  "png","webp" }

        original_filename = photo.filename
        extension = os.path.splitext( original_filename )[1].lower().replace( ".", "" )

        if extension not in allowed_extensions:
            return jsonify({
                "success": False,
                "message": "Only JPG, JPEG, PNG and WEBP images are allowed." }), 400

        connection = get_connection()
        cursor = connection.cursor( dictionary=True)

         # Check user.

        cursor.execute(
            """
            SELECT
                id,
                profile_photo
            FROM users
            WHERE id = %s
            """,
            (user_id,)  )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found."}), 404

        # Generate unique filename.
        unique_name = (
            f"profile_{user_id}_"
            f"{uuid.uuid4().hex}"
            f".{extension}")

        full_photo_path = os.path.join(
            PROFILE_UPLOAD_FOLDER,
            unique_name
        )

        # Save new photo.
        photo.save( full_photo_path )

        # Delete old profile photo if it exists.
        # This prevents unnecessary old profile images from remaining in the folder.
        old_photo = user["profile_photo"]
        if old_photo:
            old_photo_path = os.path.join(
                PROFILE_UPLOAD_FOLDER, old_photo )

            if os.path.exists(old_photo_path):
                try:
                    os.remove(old_photo_path)
                except Exception as delete_error:
                    print(
                        "Old profile photo delete error:",
                        delete_error )

        # Save new filename in database.

        cursor.execute(
            """
            UPDATE users
            SET profile_photo = %s
            WHERE id = %s
            """,
           ( unique_name,  user_id  ) )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Profile photo updated successfully.",
           "profile_photo": unique_name,
            "profile_photo_url": "/profile-photos/" + unique_name }), 200

    except Exception as e:
        print( "Profile photo upload error:", e )

        if connection: connection.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to upload profile photo.",
            "error": str(e) }), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# REMOVE PROFILE PHOTO
# URL: DELETE /users/<user_id>/profile-photo
# After removal: profile_photo = NULL
# Frontend will automatically show the first letter of the patient's name.

@api.route( "/users/<int:user_id>/profile-photo", methods=["DELETE"] )
def remove_profile_photo(user_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(
            dictionary=True
        )

        # Get current profile photo.

        cursor.execute(
            """
            SELECT
                id,
                profile_photo
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found." }), 404

        old_photo = user["profile_photo"]

        # If no photo exists.

        if not old_photo:
            return jsonify({
                "success": True,
                "message": "No profile photo to remove." }), 200

         # Remove physical image.

        old_photo_path = os.path.join(
            PROFILE_UPLOAD_FOLDER,
            old_photo
        )

        if os.path.exists(old_photo_path):
            try:
                os.remove(old_photo_path)
            except Exception as delete_error:
                print(
                    "Profile photo delete error:",
                    delete_error
                )

        # Remove photo reference from database.

        cursor.execute(
            """
            UPDATE users
            SET profile_photo = NULL
           WHERE id = %s
            """,
            (user_id,) )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Profile photo removed successfully." }), 200

    except Exception as e:
        print( "Remove profile photo error:",  e )
        if connection: connection.rollback()

        return jsonify({
            "success": False,
            "message":"Failed to remove profile photo.",
            "error": str(e) }), 500

    finally:
        if cursor:  cursor.close()
        if connection: connection.close()

# CREATE NEW SCREENING

@api.route( "/screenings", methods=["POST"] )
def create_screening():
    connection = None
    cursor = None
    try:
        # Get screening form data.
        user_id = request.form.get("user_id")
        image = request.files.get("image")
        age = request.form.get("age")
        tobacco = request.form.get("tobacco")
        alcohol = request.form.get("alcohol")
        lesion_duration = request.form.get( "lesionDuration" )
        previous_lesion = request.form.get( "previousLesion" )

        # Validation.

        if not user_id:
            return jsonify({
                "success": False,
                "message": "User ID is required." }), 400

        if not image:
            return jsonify({
                "success": False,
                "message": "Image is required." }), 400

        if image.filename == "":
            return jsonify({
                "success": False,
                "message": "No image selected." }), 400

        if not age:
            return jsonify({
                "success": False,
                "message": "Age is required." }), 400

        if not tobacco:
            return jsonify({
                "success": False,
                "message": "Tobacco information is required." }), 400

        if not alcohol:
            return jsonify({
                "success": False,
                "message":"Alcohol information is required." }), 400


        if not lesion_duration:
            return jsonify({
                "success": False,
                "message": "Lesion duration is required." }), 400

        if not previous_lesion:
            return jsonify({
                "success": False,
                "message": "Previous lesion information is required." }), 400

        connection = get_connection()
        cursor = connection.cursor()

        # Check user exists.
        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found." }), 404

        # Create screening filename.

        original_filename = image.filename

        filename = (
            f"user_{user_id}_"
            f"{original_filename}" )

        image_path = os.path.join( "uploads", filename)

        full_image_path = os.path.join( BASE_DIR, image_path )

        # Save screening image.

        image.save( full_image_path )

        print( "✅ Image saved:",full_image_path )

        # Insert screening record.
        insert_query = """
        INSERT INTO screenings
        ( user_id, image_path, age, tobacco, alcohol, lesion_duration, previous_lesion,prediction, confidence, risk_score,
            final_score, risk_status, gradcam_path, explanation  )
        VALUES
        ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) """

        cursor.execute(
            insert_query,
            ( user_id,  image_path, age, tobacco,  alcohol, lesion_duration, previous_lesion,
                None, None, None, None, None, None, None ) )

        connection.commit()

        screening_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message":  "Screening image and clinical information uploaded successfully.",
            "screening_id": screening_id,
            "image_path": image_path }), 201

    except Exception as e:
        print( "Create screening error:", e )

        if connection: connection.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to create screening.",
            "error": str(e) }), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# GET PATIENT SCREENING HISTORY

@api.route( "/screenings/<int:user_id>", methods=["GET"])
def get_user_screenings(user_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor( dictionary=True )
        query = """

        SELECT
            id,  user_id, image_path, age, tobacco, alcohol, lesion_duration, previous_lesion,
            prediction, confidence, risk_score,final_score,risk_status, gradcam_path,explanation, created_at

        FROM screenings WHERE user_id = %s ORDER BY created_at DESC """

        cursor.execute(  query, (user_id,))

        screenings = cursor.fetchall()

        return jsonify({
            "success": True,
            "count":
                len(screenings),
            "screenings":
                screenings
        }), 200

    except Exception as e:
        print(
            "Get screenings error:",  e
        )

        return jsonify({
            "success": False,
            "message":
                "Failed to retrieve screening history.",
            "error":
                str(e)
        }), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# GET ONE SCREENING RESULT

@api.route( "/screenings/result/<int:screening_id>", methods=["GET"] )
def get_screening_result(screening_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(
            dictionary=True
        )
        query = """
        SELECT
            id, user_id, image_path, age,tobacco, alcohol,lesion_duration, previous_lesion, prediction, confidence,risk_score,
            final_score, risk_status, gradcam_path, explanation, created_at
        FROM screenings
        WHERE id = %s
        """
        cursor.execute(
            query, (screening_id,) )

        screening = cursor.fetchone()

        if not screening:
            return jsonify({
                "success": False,
                "message":
                    "Screening not found." }), 404

        return jsonify({
            "success": True,
            "screening": screening }), 200

    except Exception as e:
        print(  "Get screening result error:", e )

        return jsonify({
            "success": False,
            "message":"Failed to retrieve screening result.",
            "error": str(e) }), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()



#New edited code : on 13/10/26
# ========================================================
# DOWNLOAD SCREENING REPORT (PDF)
# ========================================================

@api.route(
    "/screenings/<int:screening_id>/report",
    methods=["GET"]
)
def download_screening_report(screening_id):

    connection = None
    cursor = None

    try:
        # Get the patient ID from the request
        user_id = request.args.get("user_id", type=int)

        if not user_id:
            return jsonify({
                "success": False,
                "message": "Patient user ID is required."
            }), 400

        # Connect using the existing database connection function
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Get patient details
        cursor.execute(
            """
            SELECT id, fullname, email
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        patient = cursor.fetchone()

        if not patient:
            return jsonify({
                "success": False,
                "message": "Patient not found."
            }), 404

        # Get the screening record belonging to this patient
        cursor.execute(
            """
            SELECT
                id,
                user_id,
                created_at,
                age,
                tobacco,
                alcohol,
                lesion_duration,
                previous_lesion,
                prediction,
                confidence,
                risk_status,
                image_path,
                gradcam_path,
                explanation
            FROM screenings
            WHERE id = %s AND user_id = %s
            """,
            (screening_id, user_id)
        )

        screening = cursor.fetchone()

        if not screening:
            return jsonify({
                "success": False,
                "message": "Screening not found for this patient."
            }), 404

        # Close the database resources before generating the PDF
        cursor.close()
        cursor = None

        connection.close()
        connection = None

        # Generate the PDF report
        pdf_path = generate_screening_report(
            patient,
            screening
        )

        # Send the PDF to the browser
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=(
                f"OralAI_Screening_Report_{screening_id}.pdf"
            ),
            mimetype="application/pdf"
        )

    except Exception as e:
        print("PDF Report Error:", repr(e))

        return jsonify({
            "success": False,
            "message": "Failed to generate screening report.",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()




# AI PREDICTION

@api.route(  "/screenings/<int:screening_id>/predict",methods=["POST"] )
def predict_screening(screening_id):

    print("🔥🔥🔥 PREDICT ROUTE HIT 🔥🔥🔥")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(
            dictionary=True
        )
        # Get screening image.

        cursor.execute(
            """
            SELECT
                id,
                image_path
            FROM screenings
            WHERE id = %s
            """,
            (screening_id,)
        )

        screening = cursor.fetchone()

        if not screening:
            return jsonify({
                "success": False,
                "message":"Screening not found." }), 404

        image_path = screening["image_path"]

        if not image_path:
            return jsonify({
                "success": False,
                "message": "No image found for this screening." }), 400

        full_image_path = os.path.join(  BASE_DIR, image_path )


        print( "\n========================================" )
        print( f"AI prediction started - Screening {screening_id}" )
        print( f"Image: {full_image_path}" )
        print(  "========================================" )

        # Check physical image exists.

        if not os.path.exists(full_image_path):
            return jsonify({
                "success": False,
                "message":"Screening image file not found.",
                "image_path":full_image_path }), 404

           # Run EfficientNetB0 prediction.

        prediction_result = predict_image( full_image_path )
        prediction = prediction_result[ "prediction" ]
        confidence = prediction_result[ "confidence" ]
        risk_status = prediction_result[ "risk_status" ]
        cancer_probability = prediction_result[
            "cancer_probability"
        ]
        not_cancer_probability = prediction_result[
            "not_cancer_probability"
        ]
        print(
            ">>> PREDICTION FINISHED <<<"
        )

        print(
            f"Prediction: {prediction}"
        )

        print(
            f"Confidence: {confidence}%"
        )

        print(
            f"Risk Status: {risk_status}"
        )

        print(">>> GRAD-CAM STEP REACHED <<<")
        print(">>> ABOUT TO START GRAD-CAM <<<")

        # Generate Grad-CAM heatmap
        gradcam_result = generate_screening_gradcam(
            screening_id,
            full_image_path)
        print(
            "Grad-CAM result:",
            gradcam_result
        )

        # Get Grad-CAM path

        gradcam_path = gradcam_result.get(
            "path"
        )
         # ====================================================
        # STEP 3 - GENERATE NLP EXPLANATION
        # ====================================================

        print(
            ">>> ABOUT TO GENERATE NLP EXPLANATION <<<"
        )
        
        print("🔥🔥🔥 NLP CODE VERSION 1 LOADED 🔥🔥🔥")
        explanation = generate_screening_explanation(
            prediction=prediction,
            confidence=confidence,
            risk_status=risk_status,
            gradcam_path=gradcam_path
        )

        print( ">>> NLP EXPLANATION GENERATED <<<")

        print( "Explanation:", explanation)







              # Save AI result.

        update_query = """
        UPDATE screenings
        SET
            prediction = %s,
            confidence = %s,
            risk_status = %s,
            gradcam_path = %s,
            explanation = %s
        WHERE id = %s
        """

        cursor.execute(
            update_query,
            ( prediction, confidence, risk_status, gradcam_path, explanation, screening_id  ))

        connection.commit()

        print( "\n========================================" )
        print( "AI PREDICTION COMPLETED" )
        print( f"Prediction : {prediction}" )
        print( f"Confidence : {confidence}%" )
        print(f"Risk Status: {risk_status}")
        print(f"Grad-CAM    : {gradcam_path}")
        print("NLP         : Generated" )
        print( "========================================\n" )

        return jsonify({

            "success": True,
            "message": "AI screening completed successfully.",
            "screening_id": screening_id,
            "prediction":  prediction,
            "confidence": confidence,
            "risk_status":risk_status,
            "gradcam_path": gradcam_path,
            "explanation": explanation,
            "cancer_probability":  prediction_result[ "cancer_probability" ],
            "not_cancer_probability": prediction_result[ "not_cancer_probability" ] }), 200
 
  # ERROR HANDLING
    except Exception as e:
        print("AI prediction / NLP error:",  e )
        if connection: connection.rollback()

        return jsonify({
            "success": False,
            "message": "AI screening failed.",
            "error": str(e)  }), 500
  
   # CLOSE DATABASE
    finally:
        if cursor:cursor.close()
        if connection: connection.close()

# UPDATE SCREENING RESULT
# This endpoint can later be used for:

#   - Grad-CAM path
#   - Risk score
#   - Final score
#   - NLP explanation

@api.route( "/screenings/<int:screening_id>", methods=["PUT"])
def update_screening(screening_id):

    connection = None
    cursor = None

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message":  "No data received." }), 400


        prediction = data.get(  "prediction" )
        confidence = data.get(  "confidence" )
        risk_score = data.get( "risk_score" )
        final_score = data.get( "final_score" )
        risk_status = data.get( "risk_status"  )
        gradcam_path = data.get( "gradcam_path" )
        explanation = data.get( "explanation" )

        connection = get_connection()
        cursor = connection.cursor()
        query = """
        UPDATE screenings
        SET
            prediction = %s,
            confidence = %s,
            risk_score = %s,
            final_score = %s,
            risk_status = %s,
            gradcam_path = %s,
            explanation = %s
        WHERE id = %s
        """
        cursor.execute(
            query,
            (
                prediction, confidence, risk_score, final_score, risk_status, gradcam_path, explanation, screening_id
            ) )

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Screening not found."  }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message":
                "Screening result updated successfully."
        }), 200

    except Exception as e:
        print( "Update screening error:",  e )

        if connection: connection.rollback()

        return jsonify({
            "success": False,
            "message":  "Failed to update screening.",
            "error": str(e) }), 500

    finally:
        if cursor:  cursor.close()
        if connection: connection.close()











# =========================================================
# ADMIN DASHBOARD API ROUTES

# IMPORTANT PRIVACY RULE: 
# These admin endpoints are designed only for system-level monitoring and administrative information.
# Patient clinical information such as: age, tobacco usage, alcohol usage, lesion duration,  previous lesion history is NOT returned by these admin dashboard APIs.
# The admin dashboard only receives the minimum information required for system monitoring.

# =========================================================
# ADMIN DASHBOARD SUMMARY
# URL: GET /admin/dashboard
# Purpose: Returns summary information required by the Admin Dashboard.
# Information returned: Total registered users, Total screenings, Screenings with Cancer prediction,Screenings with Not Cancer prediction,  Recent screening records
# Patient clinical information is NOT included.

@api.route( "/admin/dashboard",
    methods=["GET"]
)
def admin_dashboard():
    connection = None
    cursor = None

    try:
        # Connect to MySQL
        connection = get_connection()
        cursor = connection.cursor( dictionary=True )

        # TOTAL REGISTERED USERS

        cursor.execute("""
            SELECT COUNT(*) AS total_users
            FROM users
        """)
        total_users_result = cursor.fetchone()
        total_users = total_users_result["total_users"]

        # TOTAL SCREENINGS
        cursor.execute("""
            SELECT COUNT(*) AS total_screenings
            FROM screenings
        """)
        total_screenings_result = cursor.fetchone()
        total_screenings = (
            total_screenings_result["total_screenings"]
        )

         # CANCER PREDICTIONS
        # This counts screenings where the AI prediction  is recorded as "Cancer". This is a screening result, NOT a medical diagnosis.

        cursor.execute("""
            SELECT COUNT(*) AS cancer_screenings
            FROM screenings
            WHERE LOWER(prediction) = 'cancer'  """)

        cancer_result = cursor.fetchone()
        cancer_screenings = ( cancer_result["cancer_screenings"] )

        # NOT CANCER PREDICTIONS

        cursor.execute("""
            SELECT COUNT(*) AS not_cancer_screenings
            FROM screenings
            WHERE LOWER(prediction) = 'not cancer'
        """)
        not_cancer_result = cursor.fetchone()
        not_cancer_screenings = (
            not_cancer_result["not_cancer_screenings"]
        )

        # PENDING SCREENINGS: Some records may have been uploaded but AI prediction may not have been completed yet.

        cursor.execute("""
            SELECT COUNT(*) AS pending_screenings
            FROM screenings
            WHERE prediction IS NULL
        """)
        pending_result = cursor.fetchone()
        pending_screenings = (
            pending_result["pending_screenings"]
        )

        # RECENT SCREENINGS
       # Only minimum information required by the admin dashboard is returned. IMPORTANT: Clinical information is intentionally excluded.
       
        cursor.execute("""
            SELECT
                s.id AS screening_id,
                s.user_id,
                u.fullname AS patient_name,
                s.prediction,
                s.confidence,
                s.risk_status,
                s.created_at
            FROM screenings s
            INNER JOIN users u
                ON s.user_id = u.id
            ORDER BY s.created_at DESC
            LIMIT 10
        """)
        recent_screenings = cursor.fetchall()

        # RETURN ADMIN DASHBOARD DATA

        return jsonify({
            "success": True,
            "statistics": {
                "total_users": total_users,
                "total_screenings": total_screenings,
                "cancer_screenings": cancer_screenings,
                "not_cancer_screenings":not_cancer_screenings,
                "pending_screenings":pending_screenings
            },
            "recent_screenings": recent_screenings  }), 200

    except Exception as e:
        print(  "Admin dashboard error:", e )

        return jsonify({
            "success": False,
            "message":"Failed to retrieve admin dashboard data.",
            "error": str(e)}), 500

    finally:
        if cursor:cursor.close()
        if connection: connection.close()

# ADMIN - USER MANAGEMENT
# URL: GET /admin/users

# Purpose: Returns registered user information for the Admin User Management page.
# Returned information: User ID, Full name, Email,  Registration date/time, Number of screenings
# IMPORTANT: Password is NEVER returned.Clinical screening information is NOT returned.

@api.route( "/admin/users", methods=["GET"] )
def admin_get_users():
    connection = None
    cursor = None
    try:
        # Connect to database
        connection = get_connection()
        cursor = connection.cursor( dictionary=True )

        # Get all registered users.
        #  A subquery counts the number of screenings belonging to each user.No patient clinical information is selected.

        cursor.execute("""
            SELECT
                u.id,
                u.fullname,
                u.email,
                u.created_at,
                COUNT(s.id) AS screening_count
            FROM users u
            LEFT JOIN screenings s
                ON u.id = s.user_id
            GROUP BY
                u.id,
                u.fullname,
                u.email,
                u.created_at
            ORDER BY
                u.created_at DESC
        """)
        users = cursor.fetchall()

        # Return user list.

        return jsonify({
            "success": True,
            "count": len(users),
            "users": users }), 200

    except Exception as e:
        print( "Admin users error:", e )

        return jsonify({
            "success": False,
            "message": "Failed to retrieve users.",
           "error": str(e) }), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# ADMIN - USER DETAILS

# URL:GET /admin/users/<user_id>
# Purpose: Returns basic information about one registered user.
# Returned: User ID, Full name, Email, Registration date/time, Number of screenings
# Password and clinical information are NOT returned.

@api.route( "/admin/users/<int:user_id>", methods=["GET"])
def admin_get_user_details(user_id):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor( dictionary=True)

        # Get user information.
        cursor.execute("""
            SELECT
                u.id,
                u.fullname,
                u.email,
                u.created_at,
                COUNT(s.id) AS screening_count
            FROM users u
           LEFT JOIN screenings s
                ON u.id = s.user_id
            WHERE u.id = %s
            GROUP BY
               u.id,
                u.fullname,
                u.email,
                u.created_at
        """, (user_id,))

        user = cursor.fetchone()

        # Check whether user exists.

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found."}), 404

        return jsonify({
            "success": True,
            "user": user }), 200

    except Exception as e:
        print( "Admin user details error:", e )
        return jsonify({
            "success": False,
            "message": "Failed to retrieve user details.",
            "error":  str(e) }), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()


# ADMIN - SCREENING RECORDS
# URL: GET /admin/screenings
# Purpose: Returns screening records required by the Admin Screening Records page.
# IMPORTANT PRIVACY RULE: Clinical information is intentionally NOT returned.
# Excluded: Age, Tobacco, Alcohol, Lesion duration, Previous lesion history
# Returned: Screening ID, Patient name, Date/time, AI prediction, Confidence, Risk status

@api.route( "/admin/screenings", methods=["GET"])
def admin_get_screenings():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(
            dictionary=True
        )

        # Retrieve screening records.
        # Only information necessary for administration is returned.

        cursor.execute("""
            SELECT
                s.id AS screening_id,
                s.user_id,
                u.fullname AS patient_name,
                s.prediction,
                s.confidence,
                s.risk_status,
                s.created_at
            FROM screenings s
            INNER JOIN users u
                ON s.user_id = u.id
            ORDER BY
                s.created_at DESC
        """)
        screenings = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(screenings),
            "screenings":  screenings }), 200

    except Exception as e:
        print(
            "Admin screenings error:",  e )

        return jsonify({
            "success": False,
            "message": "Failed to retrieve screening records.",
            "error": str(e) }), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# ADMIN - SCREENING DETAILS

# URL: GET /admin/screenings/<screening_id>
# Purpose: Returns detailed system-level information about a particular screening.
# IMPORTANT: Patient clinical information is NOT returned here.
# Therefore the Admin does not receive:Age,  Tobacco usage, Alcohol usage, Lesion duration Previous lesion history
# Returned information includes: Screening ID, Patient name, Screening date/time,  AI prediction, Confidence, Risk status, Image path, Grad-CAM path, Explanation


@api.route( "/admin/screenings/<int:screening_id>", methods=["GET"])
def admin_get_screening_details(screening_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(
            dictionary=True
        )
        # Retrieve screening details. Clinical patient information is deliberately excluded from this query.

        cursor.execute("""
            SELECT
                s.id AS screening_id,
                s.user_id,
                u.fullname AS patient_name,
                s.image_path,
                s.prediction,
                s.confidence,
                s.risk_score,
                s.final_score,
                s.risk_status,
                s.gradcam_path,
                s.explanation,
                s.created_at
            FROM screenings s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.id = %s
        """, (screening_id,))
        screening = cursor.fetchone()

        # Check whether screening exists
        if not screening:
            return jsonify({
                "success": False,
                "message": "Screening not found."  }), 404

        return jsonify({
            "success": True,
            "screening": screening }), 200

    except Exception as e:
        print(
            "Admin screening details error:", e )

        return jsonify({
            "success": False,
            "message": "Failed to retrieve screening details.",
            "error":  str(e)}), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# ADMIN - MODEL INFORMATION
# URL: GET /admin/model
# Purpose: Provides information about the final selected AI model.This endpoint is READ-ONLY.
# The Admin dashboard does not train or modify the model.
# IMPORTANT:Replace the metric values below with the final experimentally obtained values from the project.

@api.route(  "/admin/model", methods=["GET"])
def admin_get_model_information():
    try:
        # Final selected model; Update these values using the final experiment results.

        model_information = {
            "model_name": "EfficientNetB0",
            "model_version":"v1.0",
            "input_size":"224 x 224",
            "training_epochs": 20,
            "batch_size": 32,
            "optimizer":  "Adam",
            "loss_function":"Binary Crossentropy",
            "pretrained_weights":"ImageNet",
            "accuracy": 0.8789,
            "precision":0.8254,
            "recall":  0.9905,
            "f1_score":  0.9004   }

        return jsonify({
            "success": True,
            "model": model_information  }), 200

    except Exception as e:
        print(
            "Admin model information error:", e )

        return jsonify({
            "success": False,
            "message":"Failed to retrieve model information.",
            "error":str(e) }), 500         # ============================================================


