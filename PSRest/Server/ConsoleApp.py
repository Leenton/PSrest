
import sys, getopt
import json
from configuration import Console, setup_credential_database

def main(argv):
    opts, args = getopt.getopt(
        argv,"hi:o:",
        [
            "method=",
            'name=',
            'description=',
            'authentication=',
            'enabledActions=',
            'disabledActions=',
            'enabledModules=',
            'id='
        ]
    )

    request = {'mandatory' : []}
    for opt, arg in opts:
        if opt == '-h':
            print ('Use the Powershell Cmdlet(s) instead.')
            sys.exit()
            
        elif opt in ("-x", "--method"):
            if arg.lower() in ('add', 'remove', 'get', 'set', 'version', 'config'):
                request['method'] = arg.lower()
            else:
                print('Invalid method')
                sys.exit()
            
            if request["method"] in ('remove', 'set'):
                request['mandatory'].append('id')
            
            if request["method"] in ('add',):
                request['mandatory'].append('name')
                request['mandatory'].append('authentication')
                request['mandatory'].append('description')

        elif opt in ("-i", "--id"):
            request['id'] = arg

        elif opt in ("-n", "--name"):
            request['name'] = arg

        elif opt in ("-d", "--description"):
            request['description'] = arg

        elif opt in ("-a", "--authentication"):
            if arg.lower() in ('client_credential', 'access_token'):
                request['authentication'] = arg
            else:
                print('Invalid authentication type')
                sys.exit()

        elif opt in ("-m", "--enabledModules"):
            request['enabledModules'] = arg.split(',')
        
        elif opt in ("-e", "--enabledActions"):
            request['enabledActions'] = arg.split(',')
        
        elif opt in ("-d", "--disabledActions"):
            request['disabledActions'] = arg.split(',')

    # Verify that all mandatory fields are present
    for field in request['mandatory']:
        if field not in request:
            print('Missing mandatory field: ' + field)
            sys.exit()
    
    #run the request
    console = Console()
    result = console.run(request)

    print(json.dumps({'data': result}))

if __name__ == "__main__":
    setup_credential_database()
    main(sys.argv[1:])

