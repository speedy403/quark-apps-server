# Simple script to run on a schedule to remove files from the db that are no longer on the filesystem

# Dependencies
import os
import time

# Import local dependencies
from db_connector import *

# Function to remove files from the database that are no longer on the filesystem
def clean_db():
    # Print running message
    print("DB_CLEANER: Beginning database cleanup...")
    
    # Wait 10 seconds before starting to allow for database and container startup
    time.sleep(10)
    
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    try:
        if connection is None:
            print("DB_CLEANER: Unable to connect to the database")
            return None
    except:
        print("DB_CLEANER: Unable to connect to the database")
        return None
    
    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for all files
        cursor.execute("SELECT * FROM quark.apps;")
        files = cursor.fetchall()

        # Check if each file exists on the filesystem
        for file in files:
            file_path = file[7]
            if not os.path.exists(file_path):
                print(f"DB_CLEANER: File not found: {file_path}")
                # Delete the file from the database
                cursor.execute("DELETE FROM quark.apps WHERE path = %s", (file_path,))
                connection.commit()
        
    # Close the connection
    connection.close()

    # Print finished message
    print("DB_CLEANER: Database cleanup complete: Waiting...")

# Main function
def main():
    while True:
        clean_db()
        time.sleep(10)  # Run every 10 seconds for debugging
        # time.sleep(3600) # Run every hour in production
    
if __name__ == '__main__':
    main()