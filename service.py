import sqlite3
from socket import *
from threading import Thread, Lock
from datetime import datetime
from queue import Queue
import logging

class TransactionServer:
    def __init__(self, worker_count=4):
        # define workers and initialize queue
        self.worker_count = worker_count
        self.task_queue = Queue()
        self.workers = []
        self.lock = Lock()

    def start(self):
        # start threads
        for _ in range(self.worker_count):
            thread = Thread(target=self.loop, daemon=True)
            thread.start()
            self.workers.append(thread)

    def submit_task(self, from_account, to_account, amount):
        task = {
            "from" : from_account,
            "to" : to_account,
            "amount": amount
        }
        self.task_queue.put(task)

    def loop(self):
        while True:
            task = self.task_queue.get()
            try:
                self.handle_transaction(task)
            except Exception as e:
                print(e)
            finally:
                self.task_queue.task_done()


    # ------------------------------------------- SQLite ------------------------------------------------------

    def connect(self):
        '''
            Helper function to connect to 'bank.db' database
            - Returns cursor
        '''
        connection = sqlite3.connect('bank.db')
        cursor = connection.cursor()
        return connection, cursor

    def handle_transaction(self, task):
        '''
            Function to handle transactions
            - Logs them into database under 'transactions' table, then updates to_account and from_account
        '''
        connection, cursor = self.connect()
        from_account, to_account, amount = task["from"], task["to"], task["amount"]
        
        with self.lock:
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
            from_balance = cursor.fetchone()[0] # fetchone returns a tuple
            
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
            to_balance = cursor.fetchone()[0]
            
            cursor.execute('''
                UPDATE accounts 
                SET balance = ?
                WHERE id = ?    
            ''', (to_balance+amount, to_account)) 

        # Commit and close
        connection.commit()
        cursor.close()
        connection.close()