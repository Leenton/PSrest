# # Importing the library
# import psutil
 
# # Calling psutil.cpu_precent() for 4 seconds
# while(True):
#     print('The CPU usage is: ', psutil.cpu_percent(1))
#     print('RAM memory % used:', psutil.virtual_memory()[3])

# from datetime import datetime
# import os
# # open('test.txt', 'w').close()
# import sqlite3
# start = datetime.timestamp(datetime.now())
# db = sqlite3.connect('test.db')
# # db.execute('CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
# for x in range(1000):
#     cursor = db.cursor()
#     cursor.execute('SELECT * from test')
#     data = cursor.fetchall()

# end = datetime.timestamp(datetime.now())

# print(end - start)
from time import sleep


try:
    while(True):
        print('Doing shit!')
        sleep(0.1)
except KeyboardInterrupt:
    print("We are out!")
    exit(0)