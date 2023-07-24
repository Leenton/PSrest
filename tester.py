
import os.path
from datetime import datetime
from threading import Thread
from uuid import uuid4
#for i in range(1, 10):

def wreck_io():
    print(datetime.timestamp(datetime.now()))
    for x in range(1, 10000000):
        os.path.isfile(uuid4().hex) 
    print(datetime.timestamp(datetime.now()))
    print("done")


thread1 = Thread(target=wreck_io)
thread2 = Thread(target=wreck_io)
thread3 = Thread(target=wreck_io)
thread4 = Thread(target=wreck_io)
thread5 = Thread(target=wreck_io)
thread6 = Thread(target=wreck_io)
thread7 = Thread(target=wreck_io)
thread8 = Thread(target=wreck_io)
thread9 = Thread(target=wreck_io)
thread10 = Thread(target=wreck_io)

thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
thread6.start()
thread7.start()
thread8.start()
thread9.start()
thread10.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()
thread5.join()
thread6.join()
thread7.join()
thread8.join()
thread9.join()
thread10.join()