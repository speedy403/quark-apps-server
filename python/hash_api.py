# Script to handle sha256 and md5 requests from the API

# Dependencies
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# Import local dependencies
from db_connector import *

# Create a Flask app
app = Flask(__name__)

# Enable CORS for the entire application
CORS(app)

# Set the global BASE_DIR variable
BASE_DIR = '/usr/share/nginx/html/apps'

# Function to retrieve the SHA256 hash of a file
@app.route('/api/sha256/<path:file_path>', methods=['GET'])
def get_sha256(file_path):
    # Connect to the database
    connection = db_connect()

    # Check if connection was successful
    if not connection:
        return jsonify({"error": "Unable to connect to the database"}), 500
    
    # Merge the file path with the base directory
    file_path = os.path.join(BASE_DIR, file_path)

    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for the SHA256 hash
        cursor.execute("SELECT sha256_hash FROM apps WHERE path = %s", (file_path))
        result = cursor.fetchone()
    
    # Close the connection
    connection.close()

    # Check if the file exists in the database
    if not result:
        return jsonify({"error": "File not found", "file_path": file_path}), 404
    else:
        return result[0]

# Function to retrieve the MD5 hash of a file
@app.route('/api/md5/<path:file_path>', methods=['GET'])
def get_md5(file_path):
    # Connect to the database
    connection = db_connect()

    # Check if connection was successful
    if not connection:
        return jsonify({"error": "Unable to connect to the database"}), 500
    
    # Merge the file path with the base directory
    file_path = os.path.join(BASE_DIR, file_path)

    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for the MD5 hash
        cursor.execute("SELECT md5_hash FROM apps WHERE path = %s", (file_path))
        result = cursor.fetchone()
    
    # Close the connection
    connection.close()

    # Check if the file exists in the database
    if not result:
        return jsonify({"error": "File not found", "file_path": file_path}), 404
    else:
        return result[0]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)