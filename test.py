from service import TransactionServer
import time

service = TransactionServer()
service.start()

for _ in range(100):
    service.submit_task(1, 2, 1)

service.task_queue.join()

service.print_test()