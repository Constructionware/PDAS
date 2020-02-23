
import asyncio
import itertools
import json
import logging
import time

import graphene

from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.applications import Starlette
from starlette.background import BackgroundTasks
from starlette.exceptions import HTTPException
from starlette.graphql import GraphQLApp
from starlette.responses import (HTMLResponse, JSONResponse, PlainTextResponse,
                                 RedirectResponse, StreamingResponse)



from starlette.routing import Route, Router, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect

logger = logging.getLogger(__name__)

#from pda import listen

templates = Jinja2Templates(directory='templates')


def home(request):
    return templates.TemplateResponse('index.html',{'request': request})


router =[
    Route('/', endpoint=home, methods=['GET']),
    Mount('/static', StaticFiles(directory='templates/static'), name='static')

]

app = Starlette( routes=router, debug=True)


@app.route('/home')
async def homepage(request):
    """$ http :8000"""

    content = {
        'request': request.method,
        'url': repr(request.url),
        'headers': repr(request.headers),
        'query': repr(request.query_params),
        'path': repr(request.path_params),
        'cookies': repr(request.cookies),
        'body': None,
        }
    content['body'] = repr(await request.body())
    return JSONResponse(content)



@app.route('/get/plain_text')
async def get_plain_text(request):
    """$ http :8000/get/plain_text"""

    return PlainTextResponse('spam')


@app.route('/get/json')
async def get_json(request):
    """$ http :8000/get/json"""

    return JSONResponse({'hello': 'world'})


@app.route('/get/use_template')
async def get_use_template(request):
    """$ http :8000/get/use_template"""

    template = app.get_template('use_template.html')
    content = template.render(request=request)
    return HTMLResponse(content)


@app.route('/put', methods=['PUT'])
async def put(request):
    """$ http put :8000/put spam=spamspamspam"""

    content = repr(await request.body())
    response = PlainTextResponse(content)
    return response


@app.route('/put/json', methods=['PUT'])
async def put_json(request):
    """$ http put :8000/put/json spam=spamspamspam"""

    content = await request.json()
    response = JSONResponse(content)
    return response


@app.route('/post/json', methods=['POST'])
async def post_json(request):
    """$ http post :8000/post/json spam=spamspamspam"""

    return await put_json(request)


@app.route('/post/form', methods=['POST'])
async def post_form(request):
    """$ http -f post :8000/post/form spam=spamspamspam"""

    content = await request.form()
    response = PlainTextResponse(repr(content))
    return response



@app.route('/redirect')
async def redirect(request):
    """$ http :8000/redirect"""

    return RedirectResponse(url=request.url_for('get_json'))


async def _slow_add(a, b):
    await asyncio.sleep(1)
    return a + b



async def _slow_sum(nums):
    nums = list(nums)
    yield 'slow sum {}: '.format(repr(nums))

    while len(nums) > 1:
        pair = itertools.zip_longest(*([iter(nums)] * 2), fillvalue=0)
        coroutines = [_slow_add(a, b) for a, b in pair]
        g = asyncio.gather(*coroutines)
        nums = await g
    yield str(nums[0])


@app.route('/async_stream')
async def async_stream(request):
    """$ http :8000/async_stream"""

    return StreamingResponse(_slow_sum(range(10)), media_type='text/plain')


async def _background(value):
    await asyncio.sleep(3)
    logger.info('background task: %s', value)



@app.route('/background')
async def background(request):
    """$ http :8000/background"""

    tasks = BackgroundTasks()
    tasks.add_task(_background, value='spam')
    tasks.add_task(_background, value='ham')
    tasks.add_task(_background, value='eggs')

    return JSONResponse({'background': 'logging'}, background=tasks)

#------------------------------------------------------------------
names = ['ian', 'paul','admin']
session =  set()
cookie = dict(
        id= 'WM20999',
        value= None,
        expires= 1200,
        name= None,
        max_age= 2600,
        path= 'session/get',
        domain= 'http://192.168.0.17:3601/',
        secure= True,
        httpOnly= True,
        issuer= 'The Worksman',
        issue_date= time.ctime(),
        comment= 'The Worksman Application Socket Server Tracking Cookie.'

      )
#------------------------------------------------------------------
@app.websocket_route('/ws')
async def ws(websocket):
    """$ wsdump.py ws://0.0.0.0:8000/ws"""

    await websocket.accept(subprotocol=None)
    cid = websocket.client.port
   
    try:
        while True:
            t = await websocket.receive_text()

            if t == 'close':
                
                break
            
               
            else:
                print('SOCKET RECEIVED', t)
                print(websocket.headers)
                
                await websocket.send_text( f'Hi {t}!')
                await asyncio.sleep(5)
            

                await websocket.send_json({
                    #'websocket': dir(websocket),
                    #'headers:': websocket.headers.getlist(),
                    "path": websocket.url.path,
                    "port": websocket.url.port,
                    "scheme": websocket.url.scheme,
                    "cookies": websocket.cookies,
                    #"keys": websocket.keys
                    "path": websocket['path']
                    

                    
                    })
                
            
               

    except WebSocketDisconnect as d:
        if d.code == 1000:
            logger.debug('Disconnected. code %s', d.code)
        else:
            logger.info('Disconnected. code %s', d.code)
    else:
    
        await websocket.close()



class GraphHello(graphene.ObjectType):
    """GraphQL Application example
    {
      a: hello(name: "a")
      b: hello(name: "b")
      c: hello(name: "c")
      d: hello(name: "d")
      e: hello(name: "e")
      f: helloSync(name: "f")
      g: helloSync(name: "g")
      h: helloSync(name: "h")
    }
    """
    hello = graphene.String(name=graphene.String())
    hello_sync = graphene.String(name=graphene.String())
    

    async def resolve_hello(self, info, name):
        names = ['ian','Ian','Admin', 'admin']
      
        if name == 'ian':
            name = f'Authed User: {name.capitalize()}'
        else:
            name = "Annonymous"

        await asyncio.sleep(0.2)

        return f'Hello {name}'
    
    def resolve_hello_sync(self, info, name):
       

        if name =='ian':
            name = f'Authed User: {name.capitalize()}'
        else:
            name = "Annonymous"
        time.sleep(.0251)
        return f'Hello {name}'


app.add_route('/graphql',
              GraphQLApp(schema=graphene.Schema(query=GraphHello),
                         executor_class=AsyncioExecutor,
                         ),
              )


@app.route('/raise_error')
async def raise_error(request):
    raise ValueError('spam')


@app.route('/raise_http_exception')
async def raise_http_exception(request):
    raise HTTPException(410)


app2 = Router()



@app2.route('/')
async def app2_home(request):
    return PlainTextResponse('app2_home')


app.mount('/app2', app2)

"""
@app.websocket_route('/ws')
async def websocket_endpoint(self, scope, receive, send):
    websocket = WebSocket(scope=scope, receive=receive, send=send)
    await websocket.accept()
    # Process incoming messages
    # query parameters
    #search = websocket.query_params['search']
    # path Parameters
    path_param = request.path_params['username']
    while True:
        mesg = await websocket.receive_text()
        # receive Bytes
        #await websocket.receive_bytes(data)
        # receive JSON
        #await websocket.receive_json(data, mode="binary")
        await websocket.send_text(mesg.replace("Client", "Server"))
        # send text
        #await websocket.send_text(data)
        # send Bytes
        #await websocket.send_bytes(data)
        # send JSON
        #await websocket.send_json(data, mode="binary")
        # SEND RAW ASGI MESSAGES 
        #await websocket.send(message)
        #await websocket.receive()
    #await websocket.close()#code=1000)
"""

if __name__ == '__main__':
    from uvicorn import run 
    run(
        "app:app",
        host='0.0.0.0',
        port= 3601,
        limit_concurrency=1000,
        limit_max_requests=500,
        loop='asyncio',
        access_log=False,
        reload=True
        
        )

    

