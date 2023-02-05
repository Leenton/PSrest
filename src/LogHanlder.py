from queue import Queue

class LogHanlder():
    '''
    Log class reads logs from a logging queue, and writes them to a file, and prints them to the console. 
    '''
    
    def __init__(self):
        self.filename = ''
        self.file = open('', 'w')
        self.file.write('')
        self.log_queue = Queue()

    def start(self):
        while True:
            log_message = self.log_queue.get()
            self.file.write(log_message)
            print(log_message)
