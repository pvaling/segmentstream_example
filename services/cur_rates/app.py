from aiohttp import web

from views.rates import get_rates

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

app = web.Application()
app.add_routes([
    web.get('/', handle),
    web.get('/get_rates', get_rates),
    ])

web.run_app(app, port=9093)