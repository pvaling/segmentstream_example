from datetime import datetime, timedelta

import aiohttp_jinja2
from motor import motor_asyncio


@aiohttp_jinja2.template('index.html')
async def index(request):
    account = request.match_info.get('account', 'Anonymous')

    config = request.app.config

    fact_data, predict_data = await get_data_from_mongo(account, config)

    context = {
        'account': account,
        'fact_data': fact_data,
        'predict_data': predict_data,
    }

    return context


async def get_data_from_mongo(account, config):
    client = await make_connection(config)
    db = client['ss_stats']
    fact_data = await get_fact_data(account, db)
    predict_data = await get_predict_data(account, db)

    return fact_data, predict_data


async def get_predict_data(account, db):
    mongo_docs = []
    coll = db['revenue_predictions']
    cursor = coll.find(
        {
            'account': account,
            'date': {
                '$gte': datetime.now(),
                '$lte': datetime.now() + timedelta(days=2)
            }
        }
    ).sort('date')
    for document in await cursor.to_list(length=100):
        mongo_docs.append(document)
    return mongo_docs


async def get_fact_data(account, db):
    coll = db['revenue']
    cursor = coll.find(
        {
            'account': account,
            'date': {
                '$gte': datetime.now() - timedelta(days=7),
                '$lte': datetime.now()
            }
        }
    ).sort('date')
    mongo_docs = []
    for document in await cursor.to_list(length=100):
        mongo_docs.append(document)
    return mongo_docs


async def make_connection(config):
    mongo_host = config.get('mongo', {}).get('host')
    mongo_port = config.get('mongo', {}).get('port')
    client = motor_asyncio.AsyncIOMotorClient(mongo_host, mongo_port)
    return client
