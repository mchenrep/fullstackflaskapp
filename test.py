from service import TransactionServer
import time

server = TransactionServer()
server.start()

for _ in range(100):
    server.submit_task(1, 2, 5)
    
time.sleep(2)