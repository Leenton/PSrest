# Importing the library
import psutil
 
# Calling psutil.cpu_precent() for 4 seconds
while(True):
    print('The CPU usage is: ', psutil.cpu_percent(1))
    print('RAM memory % used:', psutil.virtual_memory()[3])
