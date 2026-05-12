# Full-stack Flask Asynchronous Banking Transaction Demo
Live Demo: [Click Here](https://flask-asynchronous-banking-transaction.onrender.com/)

This Flask-based application features a concurrent backend service that asynchronously processes banking transactions using worker threads and a task queue. The frontend uses Bootstrap5 and Jinja2 in its templates for managing accounts, submitting transfers, and viewing transaction history through a clean and responsive web interface.  

## Features
- Asynchronous transaction processing  
- Worker thread queue system  
- Account lookup and transaction history  
- Basic transaction validation  
- Flask/Jinja2 Frontend  
- Bootstrap5 Responsive UI  
- SQLite persistence  

## System Design
The request flow looks something like:  
```
Flask recieves request for transfer and validates input -> request gets added to queue -> worker thread processes transaction (further validation occurs) -> SQLite database gets updated -> transaction history and account details get updated in UI   
```

## Asychronous Design
An asynchronous design is used here for concurrency. The application uses a multithreaded worker system to asynchronously process transaction requests outside of Flask then uses a lock to serialize SQLite operations to prevent race conditions from occurring.  

## Technology Used
Backend:  
- Python  
- Flask  
- SQLite  
- threading (Thread, Lock), queue (Queue)  
  
Frontend:  
- HTML  
- Jinja2  
- Bootstrap 5  

## Database Design
There are 2 tables, accounts and transactions.  

Accounts:
- id
- name
- balance

Transactions:
- id
- to account
- from account
- amount
- timestamp

## Limitations
Some limitations must be acknowledged for this project because it is mainly meant for demonstration. Some of these include using SQLite for the database, which is not ideal for high concurrency, the queue is stored in memory (thus, not persistent), and worker threads will restart if the app process does.  

## How to Run
1. Clone repository  
```git clone https://github.com/mchenrep/fullstackflaskapp```  
2. Create virtual environment and install all dependencies from requirements.txt  
```pip install requirements.txt```
3. Initialize database and seed it  
```python .\schema.py```  
```python .\seed.py```  
4. Run the Flask app  
```python .\app.py```

## Screenshots
Home:  
![Home Page](screenshots/homepage.png)  

Accounts:  
![Accounts View](screenshots/accounts.png)  

Transfer:  
![Transfer](screenshots/transfer.png)
![Success](screenshots/success.png)

Account Details:  
![Account Detail View](screenshots/detailview.png)  

## Future Improvements
If I were to improve this project for the future, here are a list of things I would implement:  
1. Persistent queue system  
2. Migration to a server database (such as PostgresSQL)
3. Transaction status tracking  
4. Authentication system + log in 