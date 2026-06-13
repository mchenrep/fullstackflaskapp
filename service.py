import os
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.pool import ThreadedConnectionPool
from threading import Thread
from datetime import datetime
from queue import Queue
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s"
)

class TransactionService:
    def __init__(self, worker_count=4):
        # define workers and initialize queue
        self.worker_count = worker_count
        self.task_queue = Queue(maxsize=1000)
        self.pool = ThreadedConnectionPool(
            1, 20,
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.workers = []
 
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
        self.task_queue.put(task, block=True, timeout=2)

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

    # ------------------------------------------- PostgreSQL Functions ------------------------------------------------------

    def connect(self):
        '''
            Helper function to connect to the PostgreSQL database
            - Returns connection from the connection pool
        '''

        return self.pool.getconn()

    def handle_transaction(self, task):
        '''
            Function to handle transactions
            - Updates 'to_account' and 'from_account' and then logs them into database under 'transactions' table,
        '''
        connection = self.connect()
        from_account, to_account, amount = task["from"], task["to"], task["amount"]
        
        # Validate transaction
        self.validate_transaction(from_account, to_account, amount)
        
        # Execute transaction
        try:
            # Use context manager for both connection and cursor
            with connection:
                with connection.cursor() as cursor:
                    # Validate existence of both accounts
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM accounts
                        WHERE id IN (%s, %s)
                    """, (from_account, to_account))

                    if cursor.fetchone()[0] != 2:
                        raise ValueError("One or more accounts do not exist")

                    # Update 'From' balance
                    cursor.execute('''
                        UPDATE accounts 
                        SET balance = balance - %s
                        WHERE id = %s
                        AND balance >= %s   
                    ''', (amount, from_account, amount)) 

                    # Validate
                    if cursor.rowcount == 0:
                        raise ValueError("Insufficient funds")

                    # Update 'To' balance
                    cursor.execute('''
                        UPDATE accounts 
                        SET balance = balance + %s
                        WHERE id = %s    
                    ''', (amount, to_account)) 

                    # Add transaction to 'transactions' tables
                    cursor.execute("""
                        INSERT INTO transactions
                        (from_account, to_account, amount, timestamp)
                        VALUES (%s, %s, %s, %s)
                    """, (from_account, to_account, amount, datetime.now()))
        except Exception as e:
            logging.error(e)
            raise 
        finally:
            # Close connection
            self.pool.putconn(connection)

    def get_accounts(self) -> list[dict]:
        '''
            Gets all accounts from the 'accounts' table in the db.
        '''
        connection = self.connect()

        try:
            with connection:
                # use DictCursor to return dictionary like rows
                with connection.cursor(cursor_factory=DictCursor) as cursor:
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
            self.pool.putconn(connection)

    def get_account_by_id(self, id) -> dict:
        '''
            Gets account details from a single account from the 'accounts' table in the db based on id.
        '''
        connection = self.connect()
        
        try:
            with connection:
                # use DictCursor to return dictionary like rows
                with connection.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute('''
                        SELECT *
                        FROM accounts
                        WHERE id = %s
                    ''', (id,))
                    account_details = cursor.fetchone()
                    return account_details
        except Exception as e:
            logging.error(e)
            raise 
        finally:
            self.pool.putconn(connection)   

    def validate_transaction(self, from_account, to_account, amount) -> bool:
        '''
            Helper function to validate transactions
            - Raises ValueError for: same account and negative amounts
        '''
        # Negative amount
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Same account
        if from_account == to_account:
            raise ValueError("Cannot transfer to same account")
        
       
    def get_transactions_by_id(self, id) -> list[dict]:
        '''
            Gets all transactions from the 'transactions' table where 'id' is either the to or from account
        '''
        connection = self.connect()

        try:
            # use DictCursor to return dictionary like rows
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute('''
                    SELECT *
                    FROM transactions
                    WHERE to_account = %s
                    OR from_account = %s
                    ORDER BY timestamp DESC
                ''', (id,id))
                transactions = cursor.fetchall()
                return transactions
        except Exception as e:
            logging.error(e)
            raise 
        finally:
            self.pool.putconn(connection)