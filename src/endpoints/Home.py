from falcon.status_codes import * 
import aiofiles

class Home(object):
    async def on_get(self, req, resp):
        resp.status = HTTP_200
        resp.content_type = 'text/html'
        async with aiofiles.open('./src/html/home.html', 'rb') as f:
            resp.text = await f.read()