class PSProcessor():
    def __init__(self) -> None:
        pass

    def execute():
        pass

    def recieve():
        return []

'''
The idea is simple, we launch as many simultanius powershell sessions we can get away with, and start and jobs on different powershell sessions/ processes

we have 1 process that generates jobs from commands that are sent to the user. 

1 process that executes these jobs, 

1 process that retrives the state of all the jobs, and puts the status into a QUE

Each request, basically puts a job on a queue, then just waits around on the job queue, for a job that looks like theirs (matching ID)

This job is then taken by python and formated into a valid response for the end user. 




'''