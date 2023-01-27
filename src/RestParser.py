from entities.Cmdlet import Cmdlet

#this file is filled with methods that that verify that the rebrequest we got is in fact a valid request. 

def validate_authorization():
    pass

def validate_encoding():
    pass

def validate_command():
    pass

def validate_params():
    pass

def parse(request):
    validate_authorization()
    validate_encoding()
    validate_command()
    validate_params()
    
    return Cmdlet()