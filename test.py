from falcon.asgi import App
import uvicorn
import asyncio
import aiofiles
from falcon.status_codes import HTTP_200, HTTP_403, HTTP_404, HTTP_500

class Test(object):
    async def on_get(self, req, resp):
        resp.status = HTTP_200
        resp.content_type = 'text/plain'
        resp.stream = await aiofiles.open('/Users/leenton/test', 'rb')

PSRest = App()
# PSRest.add_route('/oauth', OAuth) #Page to get an access token
PSRest.add_route('/run', Test()) #Page to run commands


uvicorn.run(PSRest, host='0.0.0.0', port=80, log_level='info')