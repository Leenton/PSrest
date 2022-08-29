from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json, configparser, ssl

hello = {
    "id": "04", 
    "name": "sunil", 
    "department": "HR"
}

class AppServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.headers)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(hello), "utf-8"))
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(hello), "utf-8"))
    
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(hello), "utf-8"))

    def do_PUT(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(hello), "utf-8"))
    
    def do_DELETE(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(hello), "utf-8"))
    
    def do_PATCH(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(hello), "utf-8"))

if __name__ == "__main__":
    
    #Load configuration details form the config file in the config file. 

    CONFIG = configparser.ConfigParser()      
    CONFIG.read_file(open((str(Path(__file__).parent.parent) + "/config"), "r")) 
    HOSTNAME = CONFIG.get('Server', 'HOSTNAME')
    PORT = CONFIG.get('Server', 'PORT')

    #Start the http server on the local machine. 

    PSServer = HTTPServer((HOSTNAME, int(PORT)), AppServer)
    '''PSServer.socket = ssl.wrap_socket(
        PSServer.socket,
        server_side=True,
        certfile='/Users/leenton/python/localhost.pem'
    )'''
    
    
    print("Server started http://%s:%s" % (HOSTNAME, PORT))

    try:
        PSServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    PSServer.server_close()
    print("Server stopped.")