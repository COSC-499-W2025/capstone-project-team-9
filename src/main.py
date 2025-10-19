from config.db_config import get_connection # for getting a connection to the database

from upload_file import add_file_to_db

from config.db_config import get_connection  # for getting a connection to the database
from upload_file import add_file_to_db
from consent.consent_manager import ConsentManager
from database.user_preferences import init_user_preferences_table, get_user_preferences, update_user_preferences
from database.file_storage import init_file_table, store_file_in_db, count_files_by_name
from parsing.upload_handler import load_zip_bytes, WrongFormatError
import os


def main():
    print("STARTING BACKEND SETUP...") # print a message to the console

    # # Initialize the user preference table (create it if it doesn't exist)
    # init_user_preferences_table()

    # Start ConsentManager
    manager = ConsentManager(user_id="default_user")
    manager.initialize()

    # Check/request user consent
    if not manager.request_consent_if_needed():
        print("✗ Consent not granted. Exiting...")
        return
    else:
        print("✅ User consent granted. Proceeding with backend setup.")

    conn = get_connection()
    if conn:
        print("WE ARE GOOOOOOOD!")
        conn.close()
    else:
        print("WE ARE NOT GOOOOOOOD!")
        return
    
    # Init required tables
    try:
        init_user_preferences_table()
        init_file_table()
        print("✅ Tables ready.")
    except Exception as e:
        print(f"✗ Table init failed: {e}")
        return
    
    # this is a simple command-line interface to upload files. We Need to discuss in class about how we want to run these processes in the future.
    # we will not want them all stored in the same place, so we will need to modify this code later.
    # Simple CLI for ZIP upload
    while True:
        choice = input("\nDo you want to upload a ZIP file? (y/n): ").lower().strip()
        if choice in ('y', 'yes'):
            filepath = input("Enter the path to your zip file: ").strip()
            try:
                data = load_zip_bytes(filepath)
                file_name = os.path.basename(filepath)

                inserted = store_file_in_db(file_name, data)
                if inserted:
                    total = count_files_by_name(file_name)
                    print(f"✅ Uploaded '{file_name}' to database. (total with this name: {total})")
                else:
                    print(f"✗ A file named '{file_name}' already exists. Upload rejected (no overwrite).")

            except (FileNotFoundError, WrongFormatError) as e:
                print(f"✗ {e}")
            except Exception as e:
                print(f"✗ Failed to store file: {e}")

        elif choice in ('n', 'no'):
            print("Goodbye!")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    main()
