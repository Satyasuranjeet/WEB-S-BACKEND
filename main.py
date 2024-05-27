from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://satya:satya@cluster0.8thgg4a.mongodb.net/')
client = MongoClient(MONGO_URI)
db = client['WebscraperDB']
users_collection = db['users']

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Python Backend API!'})

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL not provided'}), 400

    html = get_html(url)
    if not html:
        return jsonify({'error': 'Failed to fetch HTML content'}), 500

    soup = BeautifulSoup(html, 'html.parser')
    return jsonify({'html': soup.prettify()})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email or password not provided'}), 400

    hashed_password = generate_password_hash(password)

    # Check if user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'User already exists'}), 400

    # Insert new user into database
    users_collection.insert_one({'email': email, 'password': hashed_password})
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email or password not provided'}), 400

    user = users_collection.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({'message': 'Login successful'}), 200

if __name__ == "__main__":
    app.run(debug=True)
