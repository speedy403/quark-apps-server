# This script is used to initialize the database and scan for new apps not already in the database

# Import local dependencies
from db_scanner import scan_apps
from db_init import init_db

# Main function
def main():
    # Initialize the database if not already initialized
    init_db()

    # Scan for new apps not already in the database
    scan_apps()

if __name__ == '__main__':
    main()