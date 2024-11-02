# Import dependencies
import os
import pymysql
import time

# Configure the DB connection
db_config = {
    'user': os.getenv('QUARK_DB_USER'),
    'password': os.getenv('QUARK_DB_PASS'),
    'host': os.getenv('QUARK_DB_HOST', 'quark-apps-server-db'),
    'database': os.getenv('QUARK_DB_NAME')
}

# Function to connect to the database
def db_connect():
    # Create the connection to the database 5 retries, 5 seconds apart
    for i in range(5):
        try:
            connection = pymysql.connect(**db_config)
            if connection.open:
                return connection
        except pymysql.MySQLError as e:
            print(f"DB_CONNECTOR: Error connecting to database: {e} - Retry: {i+1} Max Retries: 5")
            time.sleep(5)
    
    # If the connection still fails, exit the script
    if not connection.open:
        print("DB_CONNECTOR: Unable to connect to the database")
        return None