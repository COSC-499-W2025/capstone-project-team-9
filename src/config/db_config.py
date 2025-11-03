import os # for getting environment variables
import psycopg # for connecting to the database
from dotenv import load_dotenv # for loading environment variables from the .env file

load_dotenv()  # loads the .env file

def get_connection():
    try: # try to connect to the database
        conn = psycopg.connect( # connect to the database
            dbname=os.getenv("POSTGRES_DB"), # database name
            user=os.getenv("POSTGRES_USER"), # username
            password=os.getenv("POSTGRES_PASSWORD"), # password
            host=os.getenv("POSTGRES_HOST"), # host
            port=os.getenv("POSTGRES_PORT") # port
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None
