import yaml
from aiohttp import web

from views.predictor import make_prediction

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

app = web.Application()

with open("config.yaml", "r") as f:
    config = yaml.load(f)
if config:
    app.config = config

app.add_routes([
    web.get('/', handle),
    web.get('/make_prediction', make_prediction),
    ])

web.run_app(app, port=9094)