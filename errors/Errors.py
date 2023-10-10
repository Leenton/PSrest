class UnkownCmdlet(Exception):
    '''
    Exception raised when the cmdlet requested does not exist in the current environment
    '''
    def __init__(self, message='Cmdlet is not supported.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message 

class InvalidCmdlet(Exception):
    '''
    Exception raised when the cmdlet requested is invalid
    '''
    def __init__(self, message='Cmdlet is invalid.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

class InvalidCmdletParameter(Exception):
    '''
    Exception raised when the cmdlet parameters are invalid
    '''
    def __init__(self, message='Cmdlet parameters are invalid.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message 

class InvalidToken(Exception):
    '''
    Exception raised when supplied an invalid token
    '''
    def __init__(self, message='Access token is invalid.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

class InvalidTicket(Exception):
    '''
    Exception raised when supplied an invalid ticket
    '''
    def __init__(self, message='Ticket is invalid.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

class InvalidCredentials(Exception):
    '''
    Exception raised when supplied invalid credentials
    '''
    def __init__(self, message='Credentials are invalid.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

class InvalidTimeRange(Exception):
    '''
    Exception raised when supplied an invalid time range
    '''
    def __init__(self, message='Time range specified is invalid.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
    
class InvalidEventType(Exception):
    '''
    Exception raised when supplied an unknown event type
    '''
    def __init__(self, message='Event type specified is invalid.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
class UnAuthorised(Exception):
    '''
    Exception raised for users who are not authorised to perform an action
    '''
    def __init__(self, message='Unauthorised action requested, check your permissions.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

class UnSuppotedPSVersion(Exception):
    '''
    Exception raised when the PowerShell version requested is not supported in the current environment
    '''
    def __init__(self, version, message='PowerShell version specified is not available.'):
        self.version = version
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Powershell version: "{self.version}" is not available in the current environment/configuration.'

class UnSupportedPlatform(Exception):
    '''
    Exception raised when the platform requested is not supported in the current environment
    '''
    def __init__(self, platform, message='Platform is not available.'):
        self.platform = platform
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Platform: "{self.platform}" is not available in the current environment/configuration.'
    
class SchedulerException(Exception):
    '''
    Exception raised when the scheduler fails.
    '''
    def __init__(self, message='Scheduler failed.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

class ProcessorException(Exception):
    '''
    Exception raised when the processor fails.
    '''
    def __init__(self, message='Processor failed.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
    
class PSRQueueException(Exception):
    '''
    Exception raised when the PSRQueue encounters an error.
    '''
    def __init__(self, message='PSRQueue failed.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
    
class StreamTimeout(Exception):
    '''
    Exception raised when the PSResponseStream times out waiting for a response.
    '''
    def __init__(self, message='Stream timed out.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'
