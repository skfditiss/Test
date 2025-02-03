import logging
from flask import Flask, jsonify, request
import unittest

# Configure logging for the app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)

# Simple in-memory storage for users
users = []

# Data Models
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email
        }

# Business Logic
class UserService:
    @staticmethod
    def add_user(users, name, email):
        user = User(name, email)
        users.append(user)
        return user

    @staticmethod
    def get_user(users, name):
        return next((user for user in users if user.name == name), None)

# Routes
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Flask SonarQube Testing App"})


@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({"users": [user.to_dict() for user in users]})


@app.route('/users', methods=['POST'])
def add_user():
    user_data = request.get_json()
    if "name" not in user_data or "email" not in user_data:
        return jsonify({"error": "Missing required fields"}), 400
    user = UserService.add_user(users, user_data["name"], user_data["email"])
    logger.info(f"Added user: {user.name}")
    return jsonify({"message": "User added successfully", "user": user.to_dict()}), 201


@app.route('/users/<string:name>', methods=['GET'])
def get_user(name):
    user = UserService.get_user(users, name)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()})


# Unit Tests
class FlaskAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome to the Flask SonarQube Testing App', response.get_data(as_text=True))

    def test_add_user(self):
        user_data = {
            "name": "John Doe",
            "email": "johndoe@example.com"
        }
        response = self.client.post('/users', json=user_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('User added successfully', response.get_data(as_text=True))

    def test_get_users(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.get_json())

    def test_get_user(self):
        response = self.client.get('/users/John Doe')
        self.assertEqual(response.status_code, 200)
        self.assertIn('John Doe', response.get_json()['user']['name'])

    def test_user_not_found(self):
        response = self.client.get('/users/Nonexistent User')
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', response.get_data(as_text=True))


# SonarQube Configuration (For reference, not functional in this script)
# Create a sonar-project.properties file in the root directory to configure the SonarQube scanner.
# You can run sonar-scanner after running tests to upload results to SonarQube.

# Main entry point for the app
if __name__ == '__main__':
    app.run(debug=True)

