import PSRestQueue
import asyncio
from time import sleep

queue = PSRestQueue.PSRestQueue()
counter = 0
while(True):
    result = asyncio.run(queue.put('test' + str(counter)))
    counter += 1
    sleep(0.01)



# import socket
# import json
# soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# soc.bind("/tmp/ps.sock")




# s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# print('Socket created')
# s.bind("./PSRestQueue17")
# print('Socket bind complete')
# s.listen(64)
# print('Socket now listening')
# conn, addr = s.accept()
# print("Connected")
# s.close()

# with conn:
#     while True:
#         data = conn.recv(1024)
#         print(data)
#         if data:
#             break
#     conn.sendall(json.dumps({"Command": "Write-Host 'Hello World'", "Ticket": "1234"}).encode('utf-8'))