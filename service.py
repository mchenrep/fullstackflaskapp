import sqlite3
from socket import *
from threading import Thread
import datetime
import sys

def connect():
    '''
        Helper function to connect to 'bank.db' database
        - Returns cursor
    '''
    connection = sqlite3.connect('bank.db')
    cursor = connection.cursor()
    return connection, cursor

def handle_transaction(from_account, to_account, amount):
    '''
        Function to handle transactions
        - Logs them into database under 'transactions' table, then updates to_account and from_account
    '''
    connection, cursor = connect()

    # Log transaction
    data = [from_account, to_account, amount, datetime.now()]
    cursor.execute('''
        INSERT INTO transactions (from_account, to_account, amount, timestamp) VALUES (?,?,?,?)
    ''', data)

    # Update to and from accounts
    # From Account
    cursor.execute('''
        SELECT balance
        FROM accounts 
        WHERE id = ?    
    ''', (from_account,))
    from_balance = cursor.fetchone()
    
    cursor.execute('''
        UPDATE accounts 
        SET balance = ?
        WHERE id = ?    
    ''', (from_balance-amount, from_account)) 

    # To Account
    cursor.execute('''
        SELECT balance
        FROM accounts 
        WHERE id = ?    
    ''', (to_account,))
    to_balance = cursor.fetchone()
    
    cursor.execute('''
        UPDATE accounts 
        SET balance = ?
        WHERE id = ?    
    ''', (to_balance+amount, to_account)) 


    # Commit and close
    connection.commit()
    cursor.close()
    connection.close()

