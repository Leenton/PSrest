import json
import base64
from configuration.Config import *
from entities.CmdletLibrary import CmdletLibrary

class Cmdlet():
    def __init__(
            self,
            cmdlet_library: CmdletLibrary,
            command: dict,
            ttl: float,
            depth: int,
            platform = None,
            psversion = None
            ) -> None:
        
        self.function = None
        self.ttl = ttl
        self.depth = depth
        self.platform = platform
        self.psversion = psversion
        self.cmdlet_library = cmdlet_library
        self.value = self.parse(command)

    def parse(self, command: dict) -> str:
        cmdlet = {}

        try:
            if(command['cmdlet']):
                if(ARBITRARY_COMMANDS):
                    self.function = command['cmdlet']
                    return command['cmdlet']
                else:
                    #verify cmdlet exists
                    info = self.cmdlet_library.get_cmdlet(command['cmdlet'].lower())
                    if(info):
                        cmdlet['cmdlet'] = info
                        self.function = info.command
                        cmdlet['mandatory'] = info.mandatory_parameters
                    else:
                        raise UnkownCmdlet(self, 'Cmdlet does not exist in the current environment, or you do not have permission to run it.')
        except KeyError:
            raise InvalidCmdlet(self, 'No cmdlet provided')
        
        try:
            cmdlet['parameters'] = []

            if(isinstance(command['parameters'], (dict))):
                for parameter_name, parameter_value in command['parameters'].items():
                    if(isinstance(parameter_name, (str))):
                        cmdlet['parameters'].append([parameter_name, self.sanitise(parameter_value)])
                    else:
                        raise InvalidCmdletParameter(self, 'Invalid parameter name provided, or parameter name is not a string.')


            elif(isinstance(command['parameters'], (list))):
                for parameter_value in command['parameters']:
                    cmdlet['parameters'].append(self.sanitise(parameter_value))

            else:
                raise InvalidCmdletParameter(self, 'Poorly formatted parameters provided')
        except KeyError:
            cmdlet['parameters'] = None

        if(cmdlet['cmdlet']):
            #Convert the cmdlet dictionary into a valid poweshell command string.
            cmdlet_string = cmdlet['cmdlet'].command
            if(cmdlet['parameters']):
                for parameter in cmdlet['parameters']:
                    if(isinstance(parameter, list)):
                        cmdlet_string += f' -{parameter[0]} {parameter[1]}'
                    else:
                        cmdlet_string += f' {parameter}'

            if(cmdlet['mandatory'] and not cmdlet['parameters']):
                raise InvalidCmdletParameter(self, 'Mandatory parameters not provided')
            
            return cmdlet_string
        else:
            raise InvalidCmdlet(self)
    
    def sanitise(self, parameter: int | bool | None | list | dict | str) -> str:

        if(isinstance(parameter, (int, float))):
            return f'{parameter}'
        
        elif(isinstance(parameter, bool)):
            if(parameter):
                return '$true'
            else:
                return '$false'
        
        elif(isinstance(parameter, list)):
            return '@(' + ','.join([self.sanitise(element) for element in parameter]) + ')'
        
        elif(isinstance(parameter, dict)):
            #We need to convert the dictionary into a string, then base64 encode it, then convert it into a powershell object.
            #This is because we can't pass a dictionary to powershell, so we need to convert it into a string, then convert it back into a dictionary.
            obj = json.dumps({"obj" : parameter})
            obj = base64.b64encode(bytes(obj, 'utf-8'))
            obj = obj.decode('utf-8')
            #TODO: This is a bit of a hack, we should probably find a better way pass around dictionaries,
            return f'(([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("{obj}")) | ConvertFrom-Json).obj)'
        
        elif(isinstance(parameter, str)):
            string = json.dumps({"string" : parameter})
            string = base64.b64encode(bytes(string, 'utf-8'))
            string = string.decode('utf-8')
            #TODO: This is a bit of a hack, we should probably find a better way pass around strings,
            #      we are offloading the sanitisation to the powershell process, which is not ideal.
            #      We should probably find a way to do this in python, rather than rely on microsoft's powershell implementation.
            return f'(([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("{string}")) | ConvertFrom-Json).string)'
        else:
            return '$null'
        
class InvalidCmdlet(Exception):
    '''
    Exception raised when the cmdlet requested is invalid
    '''
    def __init__(self, cmdlet: Cmdlet, message='Cmdlet is invalid.'):
        self.cmdlet = cmdlet
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Cmdlet: "{self.cmdlet.function}" is invalid.'
    
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
    