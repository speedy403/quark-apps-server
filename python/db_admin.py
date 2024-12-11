# Script to manage existing files in the database

# Dependencies
from flask import Flask, redirect, request, render_template
import os
import datetime

# Import local dependencies
from db_connector import *
from db_scanner import *

# Create a Flask app
app = Flask(__name__)

# Set the global BASE_DIR variable
BASE_DIR = '/usr/share/nginx/html/apps'

# Create a route to upload a new file to the database
@app.route('/admin/upload', methods=['POST'])
def upload_file():
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()
    
    # Check if the connection is valid
    try:
        if connection is None:
            return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    except:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    
    # Check if the file is in the request
    if 'app' not in request.files:
        return redirect(f'/error.html?error=No+file+part+in+the+request')

    # Create the cursor
    with connection.cursor() as cursor:
        # Get the file from the request
        file = request.files['app']
        if file.filename == '':
            return redirect(f'/error.html?error=No+selected+file')
        
        # Check if the file already exists in the database
        cursor.execute("SELECT * FROM apps WHERE filename = %s", (file.filename,))
        result = cursor.fetchone()
        if result:
            return redirect(f'/error.html?error=File+already+exists+in+the+database')

        # Save the file to the filesystem
        file_path = os.path.join(BASE_DIR, file.filename)
        file.save(file_path)

        # Get the app version from the form
        app_version = request.form['app_version']

        # Calculate the SHA256 hash of the file
        sha256_hash = calculate_sha256(file_path)

        # Calculate the MD5 hash of the file
        md5_hash = calculate_md5(file_path)

        # Insert the file into the database
        cursor.execute("INSERT INTO apps (app_name, app_version, sha256_hash, md5_hash, filesize, filename, path) VALUES (%s, %s, %s, %s, %s, %s, %s)", (file.filename, app_version, sha256_hash, md5_hash, os.path.getsize(file_path), file.filename, file_path))
        connection.commit()

    # Close the connection
    connection.close()

    # Return the user to the admin page
    return redirect('/')


# Create a route to scan for new files in the database
@app.route('/admin/scan', methods=['GET'])
def scan():
    # Call the function from the db_scanner.py file
    scan_apps()

    # Return the user to the admin page
    return redirect('/')


# Create a route to remove a file from the database
@app.route('/admin/delete/<int:app_id>', methods=['GET'])
def delete_file(app_id):
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    try:
        if connection is None:
            return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    except:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')

    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for the file
        cursor.execute("SELECT * FROM apps WHERE app_id = %s", (app_id,))
        result = cursor.fetchone()

        # Try to delete the file from the filesystem using the file_path from the database
        try:
            os.remove(result[8])
        except:
            return redirect(f'/error.html?error=Unable+to+delete+file+from+the+filesystem')

        # Check if the file exists in the database
        if not result:
            return redirect(f'/error.html?error=Unable+to+delete+file+from+the+filesystem')

        # Delete the file from the database
        cursor.execute("DELETE FROM apps WHERE app_id = %s", (app_id,))
        connection.commit()

    # Close the connection
    connection.close()

    # Return the user to the admin page
    return redirect('/')


# Function to recompute the database
@app.route('/admin/recompute', methods=['GET'])
def db_recompute():
    # Print running message
    print("DB_RECOMPUTE: Beginning database recompute...")

    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    try:
        if connection is None:
            return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    except:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    
    # Attempt app_id recompute
    try:
        # Recompute the app_id column
        with connection.cursor() as cursor:
            # Drop the column
            cursor.execute("ALTER TABLE apps DROP COLUMN app_id")
            # Add the column back
            cursor.execute("ALTER TABLE apps ADD COLUMN app_id INT PRIMARY KEY AUTO_INCREMENT FIRST")
            connection.commit()
    except:
        # If the recompute fails, print an error message
        print("DB_RECOMPUTE: Error recomputing app_id column")
        return redirect(f'/error.html?error=Error+recomputing+app_id+column')
    
    finally:
        # Close the connection
        print("DB_RECOMPUTE: Recompute successful")
        connection.close()

        # Return the user to the admin page
        return redirect('/')


# Function to redirect the user to the correct update page for an app
@app.route('/admin/update/<int:app_id>', methods=['GET'])
def update_file(app_id):
    return redirect(f'/update.html?app_id={app_id}')

# Function to update the file in the database
@app.route('/admin/update', methods=['POST'])
def update_file_post():
    try:
        # Create the connection to the database 5 retries, 5 seconds apart
        connection = db_connect()

        # Check if the connection is valid
        try:
            if connection is None:
                return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
        except:
            return redirect(f'/error.html?error=Unable+to+connect+to+the+database')

        # Check if the file is in the request
        if 'app' not in request.files:
            return redirect(f'/error.html?error=No+file+part+in+the+request')

        # Create the cursor
        with connection.cursor() as cursor:
            # Get the file from the request
            file = request.files['app']
            if file.filename == '':
                return redirect(f'/error.html?error=No+selected+file')

            # Get the app_id from the form
            app_id = request.form['app_id']

            # Query the database for the existing file information
            cursor.execute("SELECT filename FROM apps WHERE app_id = %s", (app_id,))
            result = cursor.fetchone()

            if not result:
                return redirect(f'/error.html?error=App+ID+not+found+in+the+database')

            # Use the filename from the database
            file_path = os.path.join(BASE_DIR, result[0])
            
            # Save the updated file to the filesystem
            file.save(file_path)

            # Get the app version from the form
            app_version = request.form['app_version']

            # Calculate the SHA256 hash of the file
            sha256_hash = calculate_sha256(file_path)

            # Calculate the MD5 hash of the file
            md5_hash = calculate_md5(file_path)

            # Get the current date and time
            last_updated = datetime.datetime.now()

            # Update the file in the database
            cursor.execute("UPDATE apps SET app_version = %s, sha256_hash = %s, md5_hash = %s, last_updated = %s, filesize = %s, filename = %s, path = %s WHERE app_id = %s", (app_version, sha256_hash, md5_hash, last_updated, os.path.getsize(file_path), result[0], file_path, app_id))

            # Commit the changes
            connection.commit()

        # Close the connection
        connection.close()

        # Return the user to the admin page
        return redirect('/')
    
    except:
        return redirect(f'/error.html?error=Error+adding+file+to+the+database')


# Function to edit a database entry
@app.route('/admin/edit/<int:app_id>', methods=['GET'])
def edit_file(app_id):
    # get the current information from the database to fill the form
    app_id = app_id

    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    try:
        if connection is None:
            return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    except:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    
    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for the app information
        cursor.execute("SELECT * FROM apps WHERE app_id = %s", (app_id,))
        result = cursor.fetchone()

    # Close the connection
    connection.close()

    # Display the edit page with the information
    return render_template('edit.html', app_id=app_id, app_name=result[1], app_version=result[2], sha256_hash=result[3], md5_hash=result[4], last_updated=result[5], filesize=result[6], filename=result[7], path=result[8])

# Function to submit the edit
@app.route('/admin/edit', methods=['POST'])
def edit_file_post():
    # Get the form data
    app_id = request.form.get('app_id', None)
    app_name = request.form.get('app_name', None)
    app_version = request.form.get('app_version', None)
    sha256_hash = request.form.get('sha256_hash', None)
    md5_hash = request.form.get('md5_hash', None)
    last_updated = request.form.get('last_updated', None)
    filesize = request.form.get('filesize', None)
    filename = request.form.get('filename', None)
    path = request.form.get('path', None)
    
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    try:
        if connection is None:
            return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    except:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    
    # get the current information from the database to fill missing form fields
    with connection.cursor() as cursor:
        # Query the database for the app information
        cursor.execute("SELECT * FROM apps WHERE app_id = %s", (app_id,))
        result = cursor.fetchone()

    # Check if result is None
    if result is None:
        return redirect(f'/error.html?error=App+ID+not+found+in+the+database')

    # Check if the form fields are empty
    app_name = app_name if app_name else result[1]
    app_version = app_version if app_version else result[2]
    sha256_hash = sha256_hash if sha256_hash else result[3]
    md5_hash = md5_hash if md5_hash else result[4]
    last_updated = last_updated if last_updated else result[5]
    filesize = filesize if filesize else result[6]
    filename = filename if filename else result[7]
    path = path if path else result[8]

    # If the version is different, update the last_updated field
    if app_version != result[2]:
        last_updated = datetime.datetime.now()
    
    # Create the cursor
    with connection.cursor() as cursor:
        cursor.execute("UPDATE apps SET app_name = %s, app_version = %s, sha256_hash = %s, md5_hash = %s, last_updated = %s, filesize = %s, filename = %s, path = %s WHERE app_id = %s", (app_name, app_version, sha256_hash, md5_hash, last_updated, filesize, filename, path, app_id))

        # Commit the changes
        connection.commit()
    
    # Close the connection
    connection.close()

    # Return the user to the admin page
    return redirect('/')


# Function to recalculate the sums of a given file
@app.route('/admin/sums/<int:app_id>', methods=['GET'])
def recalculate_file(app_id):
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    try:
        if connection is None:
            return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    except:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    
    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for the app information
        cursor.execute("SELECT * FROM apps WHERE app_id = %s", (app_id,))
        result = cursor.fetchone()

    # Check if the file exists
    if not result:
        return redirect(f'/error.html?error=App+ID+not+found+in+the+database')

    # Recalculate the SHA256 hash of the file
    sha256_hash = calculate_sha256(result[8])

    # Recalculate the MD5 hash of the file
    md5_hash = calculate_md5(result[8])

    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    if connection is None:
        return redirect(f'/error.html?error=Unable+to+connect+to+the+database')
    
    # Create the cursor
    with connection.cursor() as cursor:
        # Update the file in the database
        cursor.execute("UPDATE apps SET sha256_hash = %s, md5_hash = %s WHERE app_id = %s", (sha256_hash, md5_hash, app_id))

        # Commit the changes
        connection.commit()
    
    # Close the connection
    connection.close()

    # Return the user to the admin page
    return redirect('/')

# Function to display the error page
@app.errorhandler(500)
def internal_error(error):
    return redirect(f'/error.html?error=Internal+server+error')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)