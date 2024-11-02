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
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
    except IOError:
        print(f"Error reading file: {file_path}")
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
        print(f"Error reading file: {file_path}")
        return None
    return md5_hash.hexdigest()

# Function to initialize the database
def init_db():
    # Create the connection to the database 5 retries, 5 seconds apart
    for i in range(5):
        try:
            connection = pymysql.connect(**db_config)
            break
        except pymysql.MySQLError as e:
            print(f"DB_INIT: Error connecting to database: {e} - Retry: {i+1} Max Retries: 5")
            time.sleep(5)
    
    # If the connection still fails, exit the script
    if not connection.open:
        print("DB_INIT: Unable to connect to the database")
        return

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
                    md5_hash VARCHAR(255) NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    filesize VARCHAR(255) NOT NULL,
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
                print(f"DB_INIT: Adding {file} to the database...")

                # Create the connection to the database
                connection = pymysql.connect(**db_config)
                
                # Compute the hash
                sha256_hash = calculate_sha256(file_path)

                # Compute the MD5 hash
                md5_hash = calculate_md5(file_path)
                
                # Check if either hash couldn't be computed
                if sha256_hash is None:
                    print("DB_INIT: Error computing SHA256 hash for {file}, Setting to N/A...")
                    sha256_hash = 'N/A'
                if md5_hash is None:
                    print("DB_INIT: Error computing MD5 hash for {file}, Setting to N/A...")
                    md5_hash = 'N/A'

                # Get the filesize
                filesize = os.path.getsize(file_path)

                # Grab the current date
                last_updated = time.strftime('%Y-%m-%d %H:%M:%S')

                print(f"DB_INIT: File info for {file}: {filename}, N/A, {sha256_hash}, {md5_hash}, {last_updated}, {filesize}, {filename}, {file_path}")

                # Create the cursor
                with connection.cursor() as cursor:
                    # Insert the app into the database
                    cursor.execute("INSERT INTO apps (app_name, app_version, sha256_hash, md5_hash, last_updated, filesize, filename, path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (filename, 'N/A', sha256_hash, md5_hash, last_updated, filesize, filename, file_path))

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