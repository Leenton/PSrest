class CmdletInfo():
    def __init__(self, command: str, mandatory_parameters: bool, module: str, version: dict, help: str):
        self.command = command
        self.mandatory_parameters = mandatory_parameters
        self.module = module
        self.version = version
        self.help = help
