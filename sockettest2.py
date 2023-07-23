# import PSRestQueue
# import asyncio
# from time import sleep

# queue = PSRestQueue.PSRestQueue()
# counter = 0
# while(True):
#     print(counter)
#     result = asyncio.run(queue.put('test' + str(counter)))
#     counter += 1
#     sleep(1)



import socket

while True:
    soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    soc.settimeout(86000)
    soc.connect("./PSRestQueue14")
    data = soc.recv(1024^3) #limit to 1GiB
    print(data)
    soc.close()

# s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# print('Socket created')
# s.bind("./tmp_socket4")
# print('Socket bind complete')
# s.listen(1)
# print('Socket now listening')
# conn, addr = s.accept()
# print("Connected")
# s.close()

# with conn:
#     print('Connected by', addr)
#     while True:
#         data = conn.recv(1024)
#         print(data)
#         if not data:
#             break