from json import dumps
from aiohttp_requests import requests
from aiohttp import web

CURRENCY_TOP = ['GBP', 'HKD', 'IDR', 'ILS', 'DKK', 'INR', 'CHF', 'MXN', 'CZK', 'SGD', 'THB', 'HRK', 'EUR', 'MYR', 'NOK',
                'CNY', 'BGN', 'PHP', 'PLN', 'ZAR', 'CAD', 'ISK', 'BRL', 'RON', 'NZD', 'TRY', 'JPY', 'RUB', 'KRW', 'USD',
                'AUD', 'HUF', 'SEK']
VALID_REDIS_KEY = 'valid_rates'
OLD_REDIS_KEY = 'old_rates'


async def feel_storage(request):
    """
     Description end-point
     ---
     tags:
     - Feeling storage
     summary: Feeling Storage
     description: This end-point allow to feel storage system.
     produces:
     - application/json
     parameters:
     - in: query
       name: merge
       type: integer
       description: feeling flag for storage
       required: true
     responses:
     "200":
       description: successful operation
     """

    request_params = request.query
    if 'merge' not in request_params and int(request_params['merge']) not in [0, 1]:
        return web.json_response(data={'error': "Parameter merge is incorrect"})

    first_feeling: bool = not await request.app['redis'].exists(VALID_REDIS_KEY)

    if first_feeling:
        await load_external_data(request.app['redis'], VALID_REDIS_KEY)
        return web.json_response(data={'result': "Storage was filled with data in first time"})
    else:
        if int(request_params['merge']) == 1:
            await load_external_data(request.app['redis'], VALID_REDIS_KEY)
            return web.json_response(data={'result': "Storage was overwritten with data"})
        else:
            await request.app['redis'].rename(VALID_REDIS_KEY, OLD_REDIS_KEY)
            await load_external_data(request.app['redis'], VALID_REDIS_KEY)
            return web.json_response(data={'result': "Storage was filled with data"})


async def load_external_data(redis, feeling_key):
    redis_dict = {}
    for currency in CURRENCY_TOP:
        response = await requests.get('https://api.ratesapi.io/api/latest', params={'base': currency})
        rates = await response.json()
        if 'error' in rates:
            continue
        redis_dict[currency] = dumps(rates['rates'])
        await redis.hmset_dict(feeling_key, redis_dict)
