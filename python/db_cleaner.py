# Simple script to run on a schedule to remove files from the db that are no longer on the filesystem

# Dependencies
import os
import time
import pymysql

# Configure the DB connection
db_config = {
    'user': os.getenv('QUARK_DB_USER'),
    'password': os.getenv('QUARK_DB_PASS'),
    'host': os.getenv('QUARK_DB_HOST', 'quark-apps-server-db'),
    'database': os.getenv('QUARK_DB_NAME')
}

# Function to remove files from the database that are no longer on the filesystem
def clean_db():
    # Print running message
    print("DB_CLEANER: Beginning database cleanup...")
    
    # Create the connection to the database 5 retries, 5 seconds apart
    for i in range(5):
        try:
            connection = pymysql.connect(**db_config)
            break
        except pymysql.MySQLError as e:
            print(f"DB_CLEANER: Error connecting to database: {e} - Retry: {i+1} Max Retries: 5")
            time.sleep(5)
    
    # If the connection still fails, exit the script
    if not connection.open:
        print("DB_CLEANER: Unable to connect to the database")
        return

    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for all files
        cursor.execute("SELECT * FROM apps")
        files = cursor.fetchall()

        # Check if each file exists on the filesystem
        for file in files:
            file_path = file[8]
            if not os.path.exists(file_path):
                print(f"DB_CLEANER: File not found: {file_path}")
                # Delete the file from the database
                cursor.execute("DELETE FROM apps WHERE path = %s", (file_path,))
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