from aiohttp import web

async def get_stats():
    return web.json_response(
        {
            'revenue': 100,
            'accuracy': 0.5
        }
    )
