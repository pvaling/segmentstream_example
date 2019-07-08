import datetime
import pprint

from aiohttp import web
from motor import motor_asyncio


def fit(data):
    return True

async def predict(date_for_prediction):
    # %%
    from sklearn.linear_model import LinearRegression

    import numpy as np
    from sklearn.preprocessing import PolynomialFeatures

    mongo_docs = await get_data_from_db(date_for_prediction)

    data = []
    for index, item in enumerate(mongo_docs):
        data.append((index, float(item['revenue'])))
    # %%

    X = [(x[0],) for x in data]
    y = [(x[1],) for x in data]

    X = np.array(X)
    y = np.array(y)

    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)

    poly.fit(X_poly, y)
    lin2 = LinearRegression()
    lin2.fit(X_poly, y)
    accuracy = lin2.score(X_poly, y)

    predicted_revenue = lin2.predict(
        X=poly.fit_transform(np.array([(len(mongo_docs),)]))
    )
    # accuracy = 1

    output_revenue = round(float(list(predicted_revenue)[0][0]), 2)
    return output_revenue, accuracy


async def make_prediction(request):

    date_from_query = request.query.get('date', None)
    date_from_query = datetime.datetime.strptime(date_from_query, '%d.%m.%Y')

    predicted_revenue, accuracy = await predict(date_from_query)

    return web.json_response(
        {
            'revenue': predicted_revenue,
            'accuracy': accuracy
        }
    )


async def get_data_from_db(date_from_query):
    client = motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    db = client['ss_stats']
    coll = db['revenue']
    cursor = coll.find(
        {
            'date': {
                '$gte': date_from_query - datetime.timedelta(days=7),
                '$lte': date_from_query
            }
        }
    ).sort('date')

    mongo_docs = []
    for document in await cursor.to_list(length=100):
        pprint.pprint(document)
        mongo_docs.append(document)
    return mongo_docs
