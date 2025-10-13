from config.db_config import get_connection # for getting a connection to the database
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

if __name__ == "__main__":
    main()
