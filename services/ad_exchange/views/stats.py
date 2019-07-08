from aiohttp import web
import datetime
import random


async def get_stats(request):
    data = [
        {
            'date': datetime.datetime.now().strftime('%d.%m.%Y'),
            'revenue': random.randint(10, 50),
        }
    ]
    return web.json_response(data)
