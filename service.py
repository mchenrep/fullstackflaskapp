import sqlite3
from threading import Thread, Lock
from datetime import datetime
from queue import Queue
import logging

# Logging setup
logging.basicConfig(filename='service.log', filemode='w', level=logging.INFO)


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
                raise e
            finally:
                self.task_queue.task_done()

    # ------------------------------------------- SQLite Functions ------------------------------------------------------

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
        
        try:
            with self.lock: # safely access db (without race conditions)
                # Log transaction
                data = [from_account, to_account, amount, datetime.now()]
                cursor.execute('''
                    INSERT INTO transactions (from_account, to_account, amount, timestamp) VALUES (?,?,?,?)
                ''', data)

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
                else:
                    cursor.execute('''
                        UPDATE accounts 
                        SET balance = balance - ?
                        WHERE id = ?    
                    ''', (amount, from_account)) 

                # Get To balance
                cursor.execute('''
                    SELECT balance
                    FROM accounts 
                    WHERE id = ?    
                ''', (to_account,))
                to_balance = cursor.fetchone()[0]
                
                # Complete transaction
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
            raise e
        finally:
            # Close connection and cursor
            cursor.close()
            connection.close()

