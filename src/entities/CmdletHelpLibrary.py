class CmdletHelpLibrary():
    def __init__(self):
        self.cmdlets = []
        #get all the exposed modules

        #get all the commands from all the exposed modules

        #add all the commands to the cmdlets list

        #remove all the commands that are not exposed


    
    def add_cmdlet(self, cmdlet):
        self.cmdlets[cmdlet.name] = cmdlet
    
    def get_cmdlet(self, cmdlet_name):
        cmdlet = self.cmdlets[cmdlet_name]
        return cmdlet

    