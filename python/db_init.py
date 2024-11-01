# Simple script to run on initial container startup to ensure the database is initialized

# Dependencies
import os
import pymysql

# Configure the DB connection
db_config = {
    'user': os.getenv('QUARK_DB_USER'),
    'password': os.getenv('QUARK_DB_PASS'),
    'host': os.getenv('QUARK_DB_HOST'),
    'database': os.getenv('QUARK_DB_NAME')
}

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
            exit()
        else:
            # Create the table
            cursor.execute("""
                CREATE TABLE apps (
                    app_id INT PRIMARY KEY AUTO_INCREMENT,
                    app_name VARCHAR(255) NOT NULL,
                    app_version VARCHAR(255) NOT NULL,
                    md5_hash VARCHAR(255) NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    filename VARCHAR(255) NOT NULL,
                    path VARCHAR(255) NOT NULL
            """)

            # Commit the changes
            connection.commit()

            # Close the connection
            connection.close()

            # Print a message
            print("DB_INIT: Database initialized")

# Function to scan for new apps
def scan_apps():
    # Create the connection to the database
    connection = pymysql.connect(**db_config)

    # Create the cursor
    with connection.cursor() as cursor:
        # Query the database for all apps
        cursor.execute("SELECT * FROM apps")
        apps = cursor.fetchall()

        # Print the apps
        for app in apps:
            print(app)
    
    # Close the connection
    connection.close()

    # Iterate through the directory
    for root, dirs, files in os.walk('/apps'):
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

                # Create the cursor
                with connection.cursor() as cursor:
                    # Insert the app into the database
                    cursor.execute("INSERT INTO apps (app_name, app_version, md5_hash, filename) VALUES (%s, %s, %s, %s)", (file, '1.0.0', '1234567890', file))

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