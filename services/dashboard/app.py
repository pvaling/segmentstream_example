import yaml
import aiohttp_jinja2
import jinja2

from aiohttp import web
from settings import config, BASE_DIR
from views.index import index
from views.dashboard import get_stats


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello 3, " + name
    return web.Response(text=text)


app = web.Application()
app.config = config

aiohttp_jinja2.setup(app,
    loader=jinja2.FileSystemLoader(str(BASE_DIR / 'dashboard' / 'templates')))
path_to_static_folder = 'static'

app.add_routes([
    # web.get('/', index),
    web.get('/{account}', index),
    web.get('/get_stats', get_stats),
    web.static('/static', path_to_static_folder)
    ])


# web.run_app(app, port=9095)

if __name__ == '__main__':
    web.run_app(app, port=9095)
