# This script will execute a complete database recomputation that will allow for reset of the primary key values

# Import dependencies
import os

# Import local dependencies
from db_connector import *

# Function to recompute the database
def db_recompute():
    # Print running message
    print("DB_RECOMPUTE: Beginning database recompute...")

    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    if connection is None:
        print("DB_RECOMPUTE: Unable to connect to the database")
        return
    
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
        return
    finally:
        # Close the connection
        print("DB_RECOMPUTE: Recompute successful")
        connection.close()

# Main function
def main():
    db_recompute()

# Run the main function
if __name__ == '__main__':
    main()