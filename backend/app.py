from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_connection, create_user_table
import bcrypt

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "✅ Flask connected to MySQL successfully!"


# -------------------- SIGNUP --------------------

@app.route("/signup", methods=["POST"])
def signup():

    try:
        data = request.get_json()

        fullname = data["fullname"]
        email = data["email"]
        password = data["password"]

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO users(fullname,email,password)
        VALUES(%s,%s,%s)
        """

        cursor.execute(
            query,
            (
                fullname,
                email,
                hashed_password.decode("utf-8")
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "message": "User registered successfully!"
        }), 200

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500


# -------------------- LOGIN --------------------

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        email = data["email"]
        password = data["password"]

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email=%s"

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:

            if bcrypt.checkpw(
                password.encode("utf-8"),
                user["password"].encode("utf-8")
            ):

                return jsonify({
                    "success": True,
                    "message": "Login Successful!"
                })

            else:

                return jsonify({
                    "success": False,
                    "message": "Incorrect Password!"
                })

        else:

            return jsonify({
                "success": False,
                "message": "Email not found!"
            })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# -------------------- MAIN --------------------

if __name__ == "__main__":
    create_user_table()
    app.run(debug=True)
