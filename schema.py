import sqlite3

# Connect to 'bank.db' database
connection = sqlite3.connect('bank.db')
cursor = connection.cursor()

# Drop tables if they exist
cursor.execute('''
    DROP TABLE IF EXISTS accounts;
''')

cursor.execute('''
    DROP TABLE IF EXISTS transactions;
''')

# Create table schemas
cursor.execute('''
    CREATE TABLE accounts (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        balance REAL
    )
''')

cursor.execute(
    '''
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY,
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
