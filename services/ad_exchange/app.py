import yaml
from aiohttp import web
from views.stats import get_stats


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "v4 - Hello, " + name
    return web.Response(text=text)

app = web.Application()
app.add_routes([
    web.get('/', handle),
    web.get('/get_stats', get_stats),
    ])

web.run_app(app, port=9092)
