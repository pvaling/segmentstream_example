import aiohttp_jinja2

@aiohttp_jinja2.template('index.html')
async def index(request):

    text = "Hell1231 234 2342o, asdasd"
    return {'text': text}
