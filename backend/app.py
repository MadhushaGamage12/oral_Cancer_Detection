# This file is responsible ONLY for:
#   1. Creating the Flask application
#   2. Enabling CORS
#   3. Registering API routes
#   4. Creating database tables
#   5. Starting the Flask server

# All API route logic is stored in routes.py.

from flask import Flask
from flask_cors import CORS
from database import (
    create_user_table,
    create_screenings_table,
    create_admin_table
)
from routes import api
# CREATE FLASK APPLICATION
app = Flask(__name__)

# ENABLE CORS
# This allows the frontend application to communicate with the Flask backend.
# Frontend:http://127.0.0.1:5500
# Backend: http://127.0.0.1:5000
CORS(app)

# REGISTER API ROUTES
# The actual routes are defined inside routes.py.
# We register the Blueprint here so Flask knows about them.
# IMPORTANT: No URL prefix is used.
# Therefore the existing URLs remain unchanged:/signup/login/screenings/screenings/6  /screenings/result/10 /screenings/10/predict

app.register_blueprint(api)

# MAIN
# When this file is executed:
#   1. Users table is checked/created
#   2. Screenings table is checked/created
#   3. Flask server starts

if __name__ == "__main__":
    print( "\n========================================"  )
    print( "Starting OralAI Backend" )
    print( "========================================\n" )
    
# Create users table if it does not exist
    create_user_table()

# Create screenings table if it does not exist
    create_screenings_table()

# Create admins table if it does not exist
    create_admin_table()


    print( "\n========================================" )
    print( "Flask server starting..." )
    print( "========================================\n" )
   
    # Start Flask development server
    app.run(
        debug=True
    )
