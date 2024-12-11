# Simple script to run on initial container startup to ensure the database is initialized

# Dependencies


# Import local dependencies
from db_connector import *
from db_scanner import scan_apps

# Function to initialize the database
def init_db():
    # Print running message
    print("DB_INIT: Initializing the database...")
    
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    try:
        if connection is None:
            print("DB_INIT: Unable to connect to the database")
            return None
    except:
        print("DB_INIT: Unable to connect to the database")
        return None

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
            cursor.execute('CREATE TABLE apps (app_id INT PRIMARY KEY AUTO_INCREMENT, app_name VARCHAR(255) NOT NULL, app_version VARCHAR(255) NOT NULL, sha256_hash VARCHAR(255) NOT NULL, md5_hash VARCHAR(255) NOT NULL, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, filesize VARCHAR(255) NOT NULL, filename VARCHAR(255) NOT NULL, path VARCHAR(255) NOT NULL);')

            # Commit the changes
            connection.commit()

            # Close the connection
            connection.close()

            # Print a message
            print("DB_INIT: Database initialized")