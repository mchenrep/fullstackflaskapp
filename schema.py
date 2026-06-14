import os
import psycopg2
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Connect to postgres database
connection = psycopg2.connect(
    dbname = DB_NAME,
    user = DB_USER,
    password = DB_PASSWORD,
    host = DB_HOST,
    port = DB_PORT
)

cursor = connection.cursor()

# Create table schemas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        balance REAL
    )
''')

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        from_account INTEGER,
        to_account INTEGER,
        amount REAL,
        timestamp TEXT
    )
    '''
)

connection.commit()
cursor.close()
connection.close()
