from falcon.asgi import App
import uvicorn
from falcon.status_codes import HTTP_401, HTTP_200
import json

class Test(object):
    async def on_get(self, req, resp):
        auth = req.get_header('Authorization')
        if(auth == None):
            resp.status = HTTP_401
            resp.append_header('WWW-Authenticate', 'Basic realm=<realm>, charset="UTF-8"')
        else:
            resp.status = HTTP_200
            resp.content_type = 'application/json'
            resp.text = json.dumps({'title': auth})



App2 = App()
App2.add_route('/', Test()) #Page to get all running processes


if __name__ == '__main__':
    uvicorn.run(App2, host='0.0.0.0', port=80, log_level='info')