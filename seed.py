import sqlite3

connection = sqlite3.connect('bank.db')
cursor = connection.cursor()

dataset = [
    ("Alice Johnson", 1250),
    ("Bob Smith", 820.50),
    ("Carol Davis", 5400.25),
    ("David Lee", 230.75)
]

cursor.executemany('''
    INSERT INTO accounts (name, balance) VALUES (?,?)
''', dataset)

connection.commit()
cursor.close()
connection.close()