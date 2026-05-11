# Full-stack Flask Asynchronous Banking Transaction Demo
This Flask-based application features a concurrent backend service that asynchronously processes banking transactions using worker threads and a task queue. The frontend uses Bootstrap5 and Jinja2 in its templates for managing accounts, submitting transfers, and viewing transaction history through a clean and responsive web interface.\

## Features
- Asynchronous transaction processing\
- Worker thread queue system\
- Account lookup and transaction history\
- Basic transaction validation\
- Flask/Jinja2 Frontend\
- Bootstrap5 Responsive UI\
- SQLite persistence\

## System Design
The request flow looks something like:\
```
Flask recieves request for transfer and validates input -> request gets added to queue -> worker thread processes transaction -> SQLite database gets updated -> transaction history and account details get updated in UI \
```