from Config import * 
import jwt
import json
import argon2
import sqlite3
import sys, getopt
import json
from datetime import datetime, timedelta

def main(argv):
    print(argv)
    inputfile = ''
    outputfile = ''
    opts, args = getopt.getopt(argv,"hi:o:",["get","add","remove","set", "name="])
    for opt, arg in opts:
        if opt == '-h':
            print ('Use the Powershell Cmdlet(s) instead.')
            sys.exit()
        elif opt in ("-g", "--get"):
            get = True
            print(get)
        elif opt in ("-a", "--add"):
            add = True
            print(add)
        elif opt in ("-r", "--remove"):
            remove = True
            print(remove)
        elif opt in ("-s", "--set"):
            set = True
            print(set)
        elif opt in ("-n", "--name"):
            name = arg
            print(name)

if __name__ == "__main__":
   main(sys.argv[1:])

