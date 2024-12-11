# Import local dependencies
from db_connector import *

# attempt to connect to the database and pull down a list of all apps
def debug():
    # Create the connection to the database 5 retries, 5 seconds apart
    connection = db_connect()

    # Check if the connection is valid
    try:
        if not connection.open:
            print("DB_READER: Unable to connect to the database")
            return None
    except:
        print("DB_READER: Unable to connect to the database")
        return {"status": "failure", "message": "Unable to connect to the database"}

    # Query the database
    with connection.cursor() as cursor:
        # Read all the apps from the database
        cursor.execute("SELECT * FROM quark.apps;")
        apps = cursor.fetchall()

    #
    print("DB_READER: Reading data from the database...")

    # Convert to a list of dictionaries
    apps_list = []
    bad_apps = []
    for app in apps:
        if(len(app) != 9):
            print("DB_READER: Invalid number of columns in the database: App: " + str(app))
            bad_apps.append(app)
            continue
        apps_list.append({
            'app_id': app[0],
            'app_name': app[1],
            'app_version': app[2],
            'sha256_hash': app[3],
            'md5_hash': app[4],
            'last_updated': app[5],
            'filesize': app[6],
            'filename': app[7],
            'path': app[8]
        })

    # Print the bad apps
    if len(bad_apps) > 0:
        print("DB_READER: Bad apps: " + str(bad_apps))
    else:
        print("DB_READER: No bad apps found")

    # Close the connection
    connection.close()

    # Return the data as a JSON object
    return apps_list, bad_apps

# Run the debug function
if __name__ == '__main__':
    debug()