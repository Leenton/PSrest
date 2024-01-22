class VersionNumber():
    def __init__(self, version: str):
        version = version.split('.')
        self.major = version[0]
        self.minor = version[1]
        self.build = version[2]

    def __str__(self):
        return f'{self.major}.{self.minor}.{self.build}'
    
    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor and self.build == other.build
    
    def __gt__(self, other):
        if(self.major > other.major):
            return True
        elif(self.major < other.major):
            return False
        else:
            if(self.minor > other.minor):
                return True
            elif(self.minor < other.minor):
                return False
            else:
                if(self.build > other.build):
                    return True
                else:
                    return False
                
    def __lt__(self, other):
        if(self.major < other.major):
            return True
        elif(self.major > other.major):
            return False
        else:
            if(self.minor < other.minor):
                return True
            elif(self.minor > other.minor):
                return False
            else:
                if(self.build < other.build):
                    return True
                else:
                    return False
    
    def __ge__(self, other):
        if(self.major > other.major):
            return True
        elif(self.major < other.major):
            return False
        else:
            if(self.minor > other.minor):
                return True
            elif(self.minor < other.minor):
                return False
            else:
                if(self.build >= other.build):
                    return True
                else:
                    return False
    
    def __le__(self, other):
        if(self.major < other.major):
            return True
        elif(self.major > other.major):
            return False
        else:
            if(self.minor < other.minor):
                return True
            elif(self.minor > other.minor):
                return False
            else:
                if(self.build <= other.build):
                    return True
                else:
                    return False
    