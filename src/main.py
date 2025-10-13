from config.db_config import get_connection # for getting a connection to the database

from upload_file import add_file_to_db

from database.user_consent import init_db, has_user_consented, ask_for_consent # for user consent management


def main():
    print("STARTING BACKEND SETUP...") # print a message to the console
    
    init_db() # initialize the database
    
    if not has_user_consented():
        print("⚠️ User consent not found. Asking for consent...")
        ask_for_consent()
    else:
        print("✅ User already consented. Proceeding with backend setup.")


    conn = get_connection()
    if conn:
        print("WE ARE GOOOOOOOD!")
        conn.close()
    else:
        print("WE ARE NOT GOOOOOOOD!")
        return
    
    # this is a simple command-line interface to upload files. We Need to discuss in class about how we want to run these processes in the future.
    # we will not want them all stored in the same place, so we will need to modify this code later.
    while True:
        choice = input("\nDo you want to upload a ZIP file? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            filepath = input("Enter the path to your zip file: ")
            add_file_to_db(filepath)
        elif choice in ['n', 'no']:
            print("Goodbye!")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    main()
