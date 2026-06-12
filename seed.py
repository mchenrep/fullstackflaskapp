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

dataset = [
    ("Alice Johnson", 1250),
    ("Bob Smith", 820.50),
    ("Carol Davis", 5400.25),
    ("David Lee", 230.75)
]

cursor.executemany('''
    INSERT INTO accounts (name, balance) VALUES (%s,%s)
''', dataset)

connection.commit()
cursor.close()
connection.close()