import os
from flask import Flask, jsonify, request
import sqlite3
import logging
import random
import string

app = Flask(__name__)

# Vulnerable: Insecure secret key, hardcoded in the code
app.secret_key = "supersecretkey"

# Vulnerable: SQLite database with no encryption and no input sanitization
DATABASE = 'app.db'

# Vulnerable: Insecure logging setup, sensitive data logged
logging.basicConfig(level=logging.DEBUG)

# Vulnerable: Weak password hashing (no hashing done at all)
users_db = {"admin": "password123"}

# Vulnerable: Insecure cookie handling, no secure flags
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in users_db and users_db[username] == password:
        response = jsonify({"message": "Login successful"})
        response.set_cookie("user", username)  # Vulnerable cookie (no secure or httponly flags)
        return response
    return jsonify({"message": "Invalid credentials"}), 401

# Vulnerable: Insecure random token generation (predictable)
def generate_token():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

# Vulnerable: Insecure SQL query with user input directly (SQL injection)
@app.route('/user_data', methods=['GET'])
def get_user_data():
    user_id = request.args.get('user_id')  # Vulnerable to SQL injection
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL Injection
    result = cursor.fetchone()
    connection.close()
    
    if result:
        return jsonify({"user": result})
    return jsonify({"message": "User not found"}), 404

# Vulnerable: Sensitive data stored in plain text (API key hardcoded)
@app.route('/get_api_data', methods=['GET'])
def get_api_data():
    api_key = "my_secret_api_key"  # Sensitive data hardcoded
    if request.headers.get('API-Key') == api_key:
        return jsonify({"data": "Sensitive API data"})
    return jsonify({"message": "Unauthorized"}), 403

# Vulnerable: Insecure file upload without validation
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    
    # Vulnerable: No file type validation, could upload dangerous files like .exe
    file.save(os.path.join('/tmp', file.filename))  # Insecure file save location
    return jsonify({"message": "File uploaded successfully"})

# Vulnerable: Missing exception handling, sensitive details exposed
@app.route('/dangerous', methods=['GET'])
def dangerous_function():
    # Vulnerable: Division by zero error, sensitive traceback could be exposed
    x = 1 / 0  # This will raise ZeroDivisionError
    return jsonify({"result": x})

# Vulnerable: Insecure JWT generation, token not properly signed
@app.route('/generate_token', methods=['POST'])
def generate_jwt_token():
    user_data = request.json
    token = generate_token()  # Vulnerable token generation
    return jsonify({"token": token})

# Vulnerable: XSS (Cross-site Scripting) in response rendering
@app.route('/hello', methods=['GET'])
def hello():
    user_input = request.args.get('name')
    # Vulnerable: No escaping of user input, XSS risk
    return f"<h1>Hello, {user_input}</h1>"

# Vulnerable: Insecure session management (no expiration time)
@app.route('/get_session_data', methods=['GET'])
def get_session_data():
    session_data = request.cookies.get('user')
    if session_data:
        return jsonify({"message": f"Hello {session_data}"})
    return jsonify({"message": "Session expired"}), 401

# Vulnerable: Insecure password management (no salt or hashing)
@app.route('/change_password', methods=['POST'])
def change_password():
    username = request.form.get('username')
    new_password = request.form.get('new_password')
    
    if username in users_db:
        users_db[username] = new_password  # Vulnerable: Password is stored as plain text
        return jsonify({"message": "Password changed successfully"})
    return jsonify({"message": "User not found"}), 404

if __name__ == '__main__':
    # Vulnerable: Default Flask config
    app.run(debug=True)  # debug=True leaks sensitive information in error pages
