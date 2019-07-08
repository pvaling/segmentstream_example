from aiohttp import web
import datetime
import random


async def get_revenue(request):
    data = [
        {
            'date': datetime.datetime.now().strftime('%d.%m.%Y'),
            'revenue': random.randint(10, 50),
            'api_variation': '3'
        }
    ]
    return web.json_response(data)
