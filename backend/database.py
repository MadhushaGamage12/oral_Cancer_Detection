# This file is responsible for:
#   1. Connecting Flask to MySQL
#   2. Creating the users table
#   3. Creating the screenings table
#   4. Creating the admins table
#   5. Adding missing columns safely

# IMPORTANT
# ---------------------------------------------------------
# This version is designed to protect the existing Patient flow.
# Existing patient data will NOT be deleted.
# Existing tables will NOT be dropped.
# Missing columns are added only when necessary.

# IMPORT MYSQL CONNECTOR
import mysql.connector
from config import DB_CONFIG

# GET MYSQL CONNECTION
# This function creates a connection between Flask and the MySQL database.

def get_connection():
    print("Connecting to MySQL...")

    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=3306,
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            connection_timeout=5,
            use_pure=True
        )

        print("✅ Connected!")
        return connection

    except Exception as e:
        print("❌ MySQL Error:", e)
        raise


# CREATE USERS TABLE
# Main purpose: Stores registered patient account information.

# IMPORTANT:
# Password is stored as a bcrypt hash.
# Password is NEVER returned to the frontend.

def create_user_table():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

# Create users table if it does not already exist.

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()

# CHECK OPTIONAL PATIENT PROFILE COLUMNS
# The current patient routes use: first_login_at, profile_photo Older databases may not have these columns.Therefore we check before adding them.
# Check first_login_at column

        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'first_login_at'
        """)

        first_login_exists = cursor.fetchone()[0]

        if first_login_exists == 0:
            print("Adding missing column: first_login_at")

            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN first_login_at
                TIMESTAMP NULL
            """)

# Check profile_photo column

        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'profile_photo'
        """)

        profile_photo_exists = cursor.fetchone()[0]
        if profile_photo_exists == 0:
            print("Adding missing column: profile_photo")

            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN profile_photo
                VARCHAR(255) NULL
            """)

        connection.commit()
        print("✅ Users table ready.")
    except Exception as e:
        print("❌ Create users table error:", e)
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# CREATE SCREENINGS TABLE
# This table stores:
# Patient screening information, Uploaded image path, AI prediction, Confidence, Risk information, Grad-CAM information,NLP explanation, Date/time

def create_screenings_table():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

# CREATE BASE SCREENINGS TABLE
# The table is created with all required columns.
# Existing tables are NOT deleted.

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS screenings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                image_path VARCHAR(255),
                age VARCHAR(20),
                tobacco VARCHAR(50),
                alcohol VARCHAR(50),
                lesion_duration VARCHAR(100),
                previous_lesion VARCHAR(100),
                prediction VARCHAR(50),
                confidence FLOAT,
                risk_score FLOAT,
                final_score FLOAT,
                risk_status VARCHAR(50),
                gradcam_path VARCHAR(255),
                explanation TEXT,
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        connection.commit()

# IMPORTANT DATABASE MIGRATION
# If the screenings table was created previously WITHOUT the patient clinical columns, then CREATE TABLE IF NOT EXISTS will NOT add them.
# Therefore we check every required column and add only the missing columns.Existing records are preserved.

        required_columns = {
            "age": "VARCHAR(20) NULL",
            "tobacco": "VARCHAR(50) NULL",
            "alcohol": "VARCHAR(50) NULL",
            "lesion_duration": "VARCHAR(100) NULL",
            "previous_lesion": "VARCHAR(100) NULL",
            "prediction": "VARCHAR(50) NULL",
            "confidence": "FLOAT NULL",
            "risk_score": "FLOAT NULL",
            "final_score": "FLOAT NULL",
            "risk_status": "VARCHAR(50) NULL",
            "gradcam_path": "VARCHAR(255) NULL",
            "explanation": "TEXT NULL"
        }

# CHECK AND ADD MISSING COLUMNS
        for column_name, column_definition in required_columns.items():

            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'screenings'
                AND COLUMN_NAME = %s
            """, (column_name,))

            column_exists = cursor.fetchone()[0]

            if column_exists == 0:
                print(
                    f"Adding missing screening column: "
                    f"{column_name}"
                )

                alter_query = f"""
                    ALTER TABLE screenings
                    ADD COLUMN
                    {column_name}
                    {column_definition}
                """

                cursor.execute(alter_query)

        connection.commit()
        print("✅ Screenings table ready.")
    except Exception as e:
        print("❌ Create screenings table error:", e)

        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# CREATE ADMINS TABLE
# Admin accounts are separate from patient accounts.
# Patient accounts:users table
# Admin account: admins table
# The default system administrator is:
#    Email: admin@gmail.com
#     Password: 1234
# The password is stored as a bcrypt hash.
# IMPORTANT: This function does NOT delete existing admin accounts.It only creates the default admin if the email does not exist.

def create_admin_table():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

# CREATE ADMINS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                first_login_at DATETIME NULL,
                profile_photo VARCHAR(255) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()

        # CHECK WHETHER DEFAULT ADMIN ALREADY EXISTS

        cursor.execute("""
            SELECT id
            FROM admins
            WHERE email = %s
        """, ("admin@gmail.com",))

        admin = cursor.fetchone()

        # CREATE DEFAULT ADMIN ONLY IF IT DOES NOT EXIST

        if admin is None:
            import bcrypt

            admin_password = "1234"

            hashed_password = bcrypt.hashpw(
                admin_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute("""
                INSERT INTO admins (
                    fullname,
                    email,
                    password
                )
                VALUES (%s, %s, %s)
            """, (
                "admin",
                "admin@gmail.com",
                hashed_password
            ))

            connection.commit()

            print("✅ Default admin account created.")
            print("   Email: admin@gmail.com")
            print("   Password: 1234")
        else:
            print("✅ Default admin account already exists.")
        print("✅ Admins table ready.")
    except Exception as e:
        print("❌ Admin table error:", e)
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
