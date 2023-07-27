from entities.Cmdlet import Cmdlet
from entities.PSTicket import PSTicket
class InvalidToken(Exception):
    '''
    Exception raised when supplied an invalid token
    '''
    def __init__(self, message='Access token is invalid.'):
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

class UnkownCmdlet(Exception):
    '''
    Exception raised when the cmdlet requested does not exist in the current environment
    '''
    def __init__(self, cmdlet: Cmdlet, message='Cmdlet is not supported.'):
        self.cmdlet = cmdlet
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Cmdlet: "{self.cmdlet.function}" does not exist in the current environment.'

class InvalidCmdletParameter(Exception):
    '''
    Exception raised when the cmdlet parameters are invalid
    '''
    def __init__(self, parameter: str, cmdlet: Cmdlet, message='Cmdlet parameters are invalid.'):
        self.parameter = parameter
        self.cmdlet = cmdlet
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'The value for parameter "{self.parameter}" is not a valid parameter, or was not provided to the function "{self.cmdlet.function}".'

class CmdletExecutionError(Exception):
    '''
    Exception raised when the cmdlet execution fails
    '''
    def __init__(self, cmdlet: Cmdlet, message='Cmdlet execution failed.'):
        self.cmdlet = cmdlet
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Cmdlet: "{self.cmdlet.function}" failed to execute.'

class CmdletExecutionTimeout(Exception):
    '''
    Exception raised when the cmdlet execution times out
    '''
    def __init__(self, cmdlet: Cmdlet, message='Cmdlet execution timed out.'):
        self.cmdlet = cmdlet
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Cmdlet: "{self.cmdlet.function}" timed out after {self.cmdlet.ttl} seconds.'
    
class ExpiredPSTicket(Exception):
    '''
    Exception raised when the ticket has expired before a valid response was received from the PSProcessor
    '''
    def __init__(self, ticket: PSTicket, message='Timed out waiting to process command.'):
        self.ticket = ticket
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Ticket: "{self.ticket.id}" has expired after waiting {self.ticket.ttl} seconds while executing cmdlet: {self.ticket.command}'
    
class SchedulerException(Exception):
    '''
    Exception raised when the scheduler fails.
    '''
    def __init__(self, message='Scheduler failed.'):
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