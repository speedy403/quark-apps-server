# Simple script to scan for new apps on the filesystem and add them to the database

# Dependencies
import os
import time
import hashlib

# Import local dependencies
from db_connector import *

# Function to calculate the SHA256 hash of a file
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
    except IOError:
        print(f"DB_SCANNER: Error reading file: {file_path}")
        return None
    return sha256_hash.hexdigest()

# Function to calculate the MD5 hash of a file
def calculate_md5(file_path):
    md5_hash = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
    except IOError:
        print(f"DB_SCANNER: Error reading file: {file_path}")
        return None
    return md5_hash.hexdigest()

# Function to scan for new apps
def scan_apps():
    # Print a message
    print("DB_SCANNER: Scanning for new apps...")
    
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()
    
    # Check if the connection is valid
    try:
        if not connection.open:
            print("DB_SCANNER: Unable to connect to the database")
            return None
    except:
        print("DB_SCANNER: Unable to connect to the database")
        return None

    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for all apps
        cursor.execute("SELECT * FROM apps")
        apps = cursor.fetchall()
    
    # Close the connection
    connection.close()

    # Iterate through the directory
    for root, dirs, files in os.walk('/usr/share/nginx/html/apps'):
        for file in files:

            # Grab the filename
            filename = os.path.basename(file)

            # Create the file path
            file_path = os.path.join(root, filename)

            # Check if it is in the database
            found = False
            for app in apps:
                # Compare the filename to the filename in the database
                if app[8] == file_path:
                    found = True
                    break
            
            # If not found, add it to the database
            if not found:
                print(f"DB_SCANNER: Adding {file} to the database...")

                # Create the connection to the database 5 retries, 5 seconds apart
                connection = db_connect()

                # Check if the connection is valid
                if connection is None:
                    print("DB_SCANNER: Unable to connect to the database")
                    return None
                
                # Compute the hash
                sha256_hash = calculate_sha256(file_path)

                # Compute the MD5 hash
                md5_hash = calculate_md5(file_path)
                
                # Check if either hash couldn't be computed
                if sha256_hash is None:
                    print("DB_SCANNER: Error computing SHA256 hash for {file}, Setting to N/A...")
                    sha256_hash = 'N/A'
                if md5_hash is None:
                    print("DB_SCANNER: Error computing MD5 hash for {file}, Setting to N/A...")
                    md5_hash = 'N/A'

                # Get the filesize
                filesize = os.path.getsize(file_path)

                # Grab the current date
                last_updated = time.strftime('%Y-%m-%d %H:%M:%S')

                print(f"DB_SCANNER: File info for {file}: {filename}, N/A, {sha256_hash}, {md5_hash}, {last_updated}, {filesize}, {filename}, {file_path}")

                # Create the cursor
                with connection.cursor() as cursor:
                    # Insert the app into the database
                    cursor.execute("INSERT INTO apps (app_name, app_version, sha256_hash, md5_hash, last_updated, filesize, filename, path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (filename, 'N/A', sha256_hash, md5_hash, last_updated, filesize, filename, file_path))

                    # Commit the changes
                    connection.commit()

                    # Print a message
                    print(f"DB_SCANNER: {file} added to the database")

                    # Close the connection
                    connection.close()