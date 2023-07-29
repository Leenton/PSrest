import json
import base64
from Config import *
from entities.CmdletLibrary import CmdletLibrary
class Cmdlet():
    def __init__(
            self,
            cmdlet_library: CmdletLibrary,
            command: dict,
            ttl: float,
            platform = None,
            psversion = None
            ) -> None:
        
        self.function = None
        self.ttl = ttl
        self.platform = platform
        self.psversion = psversion
        self.value = self.parse(command)
        self.cmdlet_library = cmdlet_library

    def parse(self, command: dict) -> str:
        cmdlet = {}

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
                    cmdlet['mandatory'] = info.has_mandatory_parameters
                else:
                    raise Exception('Invalid cmdlet provided')

        if(command['parameters']):
            cmdlet['parameters'] = []
            if(isinstance(command['parameters'], (dict))):
                if(isinstance(command['parameters'], dict)):
                    for parameter_name, parameter_value in command['parameters'].items():
                        if(isinstance(parameter_name, (str, int))):
                            cmdlet['parameters'].append([parameter_name, self.sanitise(parameter_value)])
                        else:
                            raise Exception('Invalid parameter name provided')
                else:
                    for parameter_value in command['parameters']:
                        cmdlet['parameters'].append(self.sanitise(parameter_value))
            elif(isinstance(command['parameters'], None)):
                cmdlet['parameters'] = None
            else:
                raise Exception('Invalid parameters provided')

        if(cmdlet['cmdlet']):
            #convert the cmdlet dictionary into a valid poweshell command string.
            cmdlet_string = cmdlet['cmdlet']
            if(cmdlet['parameters']):
                for parameter in cmdlet['parameters']:
                    if(isinstance(parameter, list)):
                        cmdlet_string += f' -{parameter[0]} {parameter[1]}'
                    else:
                        cmdlet_string += f' {parameter}'

            if(cmdlet['mandatory'] and not cmdlet['parameters']):
                raise Exception('Mandatory parameters not provided')
            
            return cmdlet_string
        else:
            raise Exception('Invalid cmdlet provided')
    
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