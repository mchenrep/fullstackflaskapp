import sqlite3
from threading import Thread, Lock
from datetime import datetime
from queue import Queue
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)

class TransactionService:
    def __init__(self, worker_count=4):
        # define workers and initialize queue
        self.worker_count = worker_count
        self.task_queue = Queue()
        self.workers = []
        self.lock = Lock()
 
    # ------------------------------------------- Multithreading Functions -------------------------------------------------

    def start(self):
        '''
            Starts threads based on worker count
        '''
        for _ in range(self.worker_count):
            thread = Thread(target=self.loop, daemon=True)
            thread.start()
            self.workers.append(thread)

    def submit_task(self, from_account, to_account, amount):
        '''
            Creates transaction tasks and submits them to queue
        '''
        task = {
            "from" : from_account,
            "to" : to_account,
            "amount": amount
        }
        self.task_queue.put(task)

    def loop(self):
        '''
            Multithreading loop to accept tasks from queue indefinitely
            - Contains try/except/finally block to safely handle transaction tasks
            - Signals task completion to unblock .join calls
        '''
        while True:
            task = self.task_queue.get()
            try:
                self.handle_transaction(task)
            except Exception as e:
                logging.error(e)
            finally:
                self.task_queue.task_done()

    # ------------------------------------------- SQLite Functions ------------------------------------------------------

    def connect(self):
        '''
            Helper function to connect to 'bank.db' database
            - Returns cursor
        '''
        connection = sqlite3.connect('bank.db', timeout=5)
        connection.row_factory = sqlite3.Row # converts return into dictionary-like indexing instead of tuples
        cursor = connection.cursor()
        return connection, cursor

    def handle_transaction(self, task):
        '''
            Function to handle transactions
            - Logs them into database under 'transactions' table, then updates to_account and from_account
        '''
        connection, cursor = self.connect()
        from_account, to_account, amount = task["from"], task["to"], task["amount"]
           
        try:
            # Validate transaction
            if self.validate_transaction(from_account=from_account, to_account=to_account, amount=amount):
                with self.lock: # safely access db (without race conditions)
                    # Log transaction
                    data = [from_account, to_account, amount, datetime.now()]
                    cursor.execute('''
                        INSERT INTO transactions (from_account, to_account, amount, timestamp) VALUES (?,?,?,?)
                    ''', data)
                    
                    # Update 'From' balance
                    cursor.execute('''
                        UPDATE accounts 
                        SET balance = balance - ?
                        WHERE id = ?    
                    ''', (amount, from_account)) 
                
                    # Update 'To' balance
                    cursor.execute('''
                        UPDATE accounts 
                        SET balance = balance + ?
                        WHERE id = ?    
                    ''', (amount, to_account)) 

                    # Commit changes
                    connection.commit()
        except Exception as e:
            # Rollback if exception occurs
            connection.rollback()
            logging.error(e)
            raise 
        finally:
            # Close connection and cursor
            cursor.close()
            connection.close()

    def get_accounts(self):
        '''
            Gets all accounts from the 'accounts' table in the db.
        '''
        connection, cursor = self.connect()

        try:
            cursor.execute('''
                SELECT *
                FROM accounts
            ''')
            accounts = cursor.fetchall()
            return accounts
        except Exception as e:
            logging.error(e)
            raise 
        finally:
            cursor.close()
            connection.close()

    def get_account_by_id(self, id):
        '''
            Gets account details from a single account from the 'accounts' table in the db based on id.
        '''
        connection, cursor = self.connect()
        
        try:
            cursor.execute('''
                SELECT *
                FROM accounts
                WHERE id = ?
            ''', (id,))
            account_details = cursor.fetchone()
            return account_details
        except Exception as e:
            logging.error(e)
            raise 
        finally:
            cursor.close()
            connection.close()    

    def validate_transaction(self, to_account, from_account, amount):
        connection, cursor = self.connect()
        
        # Check if transfer is to same account
        if from_account == to_account:
            raise ValueError("Transfer cannot be from the same account")

        # Check if both accounts exist
        try:
            cursor.execute('''
                SELECT COUNT(*) 
                FROM accounts 
                WHERE id IN (?, ?);
            ''', (to_account, from_account)) # query returns count of matched ids in db (2 = both exist, 1 = 1 exists, 0 = none exists)
            if cursor.fetchone()[0] != 2:
                raise ValueError("1 or more accounts don't exist")

            # Get From balance
            cursor.execute('''
                SELECT balance
                FROM accounts 
                WHERE id = ?    
            ''', (from_account,))
            
            from_balance = cursor.fetchone()[0] # fetchone returns a tuple
                    
            # Validate transaction
            if from_balance < amount:
                raise ValueError("Insufficient funds")
            
            # If all checks pass, return True
            return True
        except Exception as e:
            logging.error(e)
            raise 
        finally:
            cursor.close()
            connection.close()