# Script to manage existing files in the database

# Dependencies
from flask import Flask, jsonify, redirect
import os
import pymysql

# Import local dependencies
from db_connector import *

# Create a Flask app
app = Flask(__name__)

# Set the global BASE_DIR variable
BASE_DIR = '/usr/share/nginx/html/apps'

# Create a route to remove a file from the database
@app.route('/admin/delete/<int:app_id>', methods=['GET'])
def delete_file(app_id):
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    if connection is None:
        return jsonify({"error": "Unable to connect to the database"}), 500
        return None

    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for the file
        cursor.execute("SELECT * FROM apps WHERE app_id = %s", (app_id,))
        result = cursor.fetchone()

        # Try to delete the file from the filesystem using the file_path from the database
        try:
            os.remove(result[8])
        except:
            return jsonify({"error": "File not found", "app_id": app_id}), 404

        # Check if the file exists in the database
        if not result:
            return jsonify({"error": "File not found", "app_id": app_id}), 404

        # Delete the file from the database
        cursor.execute("DELETE FROM apps WHERE app_id = %s", (app_id,))
        connection.commit()

    # Close the connection
    connection.close()

    # Return the user to the admin page
    return redirect('/')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)