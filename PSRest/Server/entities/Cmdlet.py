import json
import base64
from configuration import ARBITRARY_COMMANDS
from .CmdletInfoLibrary import CmdletInfoLibrary
from .CmdletResponse import CmdletResponse
from errors import UnkownCmdlet, InvalidCmdlet, InvalidCmdletParameter
from auth import Authorisation, AuthorisationSchema, AuthorisationToken

class Cmdlet():
    def __init__(
            self,
            cmdlet_library: CmdletInfoLibrary,
            authorisation: Authorisation,
            command: dict,
            ttl: float,
            depth: int,
            token: AuthorisationToken,
            platform = None,
            psversion = None
        ) -> None:

        self.function = None
        self.ttl = ttl
        self.depth = depth
        self.platform = platform
        self.psversion = psversion
        self.cmdlet_library = cmdlet_library
        self.array_wrap = command.get('array_wrap', False)
        self.value = self.parse(command)
        self.application_name =  token.user if authorisation.is_authorised(token, self.function, AuthorisationSchema.BEARER) else None

        if(self.application_name == None):
            raise UnkownCmdlet('Cmdlet does not exist in the current environment, or you do not have permission to run it.')

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
                        raise UnkownCmdlet('Cmdlet does not exist in the current environment, or you do not have permission to run it.')
        except KeyError:
            raise InvalidCmdlet('No cmdlet provided')
        
        try:
            cmdlet['parameters'] = []

            if(isinstance(command['parameters'], (dict))):
                for parameter_name, parameter_value in command['parameters'].items():
                    if(isinstance(parameter_name, (str))):
                        cmdlet['parameters'].append([parameter_name, self.sanitise(parameter_value)])
                    else:
                        raise InvalidCmdletParameter('Invalid parameter name provided, or parameter name is not a string.')


            elif(isinstance(command['parameters'], (list))):
                for parameter_value in command['parameters']:
                    cmdlet['parameters'].append(self.sanitise(parameter_value))

            else:
                raise InvalidCmdletParameter('Poorly formatted parameters provided')
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

    def serialise(self) -> dict:
        return {
            'function': self.function,
            'ttl': self.ttl,
            'depth': self.depth,
            'platform': self.platform,
            'psversion': self.psversion,
            'command': self.value,
            'ticket': None,
            'application_name': self.application_name,
            'array_wrap': self.array_wrap
        }

    async def invoke(self) -> CmdletResponse:
        response = CmdletResponse(self.serialise())
        await response.execute()
        return response