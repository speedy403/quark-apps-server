# Simple script to run on initial container startup to ensure the database is initialized

# Dependencies
import os
import time
import pymysql
import hashlib

# Configure the DB connection
db_config = {
    'user': os.getenv('QUARK_DB_USER'),
    'password': os.getenv('QUARK_DB_PASS'),
    'host': os.getenv('QUARK_DB_HOST', 'quark-apps-server-db'),
    'database': os.getenv('QUARK_DB_NAME')
}

# Function to calculate the SHA256 hash of a file
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

# Function to initialize the database
def init_db():
    # Create the connection to the database
    connection = pymysql.connect(**db_config)

    # Create the cursor
    with connection.cursor() as cursor:
        # Check if there is already a table
        cursor.execute("SHOW TABLES LIKE 'apps'")
        result = cursor.fetchone()

        # If the table already exists, do nothing
        if result:
            print("DB_INIT: Table already exists, skipping initialization")
            return
        else:
            print("DB_INIT: Table does not exist, initializing...")
            # Create the table
            cursor.execute('''
                CREATE TABLE apps (
                    app_id INT PRIMARY KEY AUTO_INCREMENT,
                    app_name VARCHAR(255) NOT NULL,
                    app_version VARCHAR(255) NOT NULL,
                    sha256_hash VARCHAR(255) NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    filename VARCHAR(255) NOT NULL,
                    path VARCHAR(255) NOT NULL
                );
            ''')

            # Commit the changes
            connection.commit()

            # Close the connection
            connection.close()

            # Print a message
            print("DB_INIT: Database initialized")

# Function to scan for new apps
def scan_apps():
    # Print a message
    print("DB_INIT: Scanning for new apps...")
    
    # Create the connection to the database
    connection = pymysql.connect(**db_config)

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
            # Check if it is in the database
            found = False
            for app in apps:
                # Compare the filename to the filename in the database
                if app[5] == file:
                    found = True
                    break
            
            # If not found, add it to the database
            if not found:
                print(f"DB_INIT: Adding {file} to the database...")

                # Create the connection to the database
                connection = pymysql.connect(**db_config)

                # Grab the filename
                filename = os.path.basename(file)

                # Create the file path
                file_path = os.path.join(root, filename)
                
                # Compute the hash
                sha256_hash = calculate_sha256(file_path)

                # Grab the current date
                last_updated = time.strftime('%Y-%m-%d %H:%M:%S')

                print(f"DB_INIT: File info for {file}: {filename}, N/A, {sha256_hash}, {last_updated}, {filename}, {file_path}")

                # Create the cursor
                with connection.cursor() as cursor:
                    # Insert the app into the database
                    cursor.execute("INSERT INTO apps (app_name, app_version, sha256_hash, last_updated, filename, path) VALUES (%s, %s, %s, %s, %s, %s)", (filename, 'N/A', sha256_hash, last_updated, filename, file_path))

                    # Commit the changes
                    connection.commit()

                    # Close the connection
                    connection.close()


# Main function
def main():
    # Initialize the database if not already initialized
    init_db()

    # Scan for new apps not already in the database
    scan_apps()

if __name__ == '__main__':
    main()