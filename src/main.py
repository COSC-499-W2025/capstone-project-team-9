from config.db_config import get_connection # for getting a connection to the database

def main():
    print("STARTING BACKEND SETUP...") # print a message to the console
    conn = get_connection()
    if conn:
        print("WE ARE GOOOOOOOD!")
        conn.close()
    else:
        print("WE ARE NOT GOOOOOOOD!")

if __name__ == "__main__":
    main()
