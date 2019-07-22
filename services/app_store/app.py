import yaml
from aiohttp import web
from views.app_store_1 import get_revenue as get_revenue_1
from views.app_store_2 import get_revenue as get_revenue_2
from views.app_store_3 import get_revenue as get_revenue_3


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

app = web.Application()
app.add_routes([
    web.get('/', handle),
    web.get('/store1', get_revenue_1),
    web.get('/store2', get_revenue_2),
    web.get('/store3', get_revenue_3)
    ])

web.run_app(app, port=9091)
