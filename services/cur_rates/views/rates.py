from decimal import Decimal

from aiohttp import web
import datetime


async def get_rates(request):

    date_from_query = request.query.get('date', None)

    rates = {
        '06.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '07.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '08.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '09.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '10.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '11.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '12.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '13.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '14.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '15.07.2019': {
            'RUB': {
                'rate': str(Decimal(63.5))
            }
        },
        '16.07.2019': {
            'RUB': {
                'rate': str(Decimal(65.5))
            }
        },
        '17.07.2019': {
            'RUB': {
                'rate': str(Decimal(65.5))
            }
        },
    }

    out = rates.get(date_from_query, None)

    return web.json_response(out)
