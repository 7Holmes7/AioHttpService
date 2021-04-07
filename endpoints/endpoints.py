from json import dumps, loads
from aiohttp_requests import requests
from aiohttp import web

CURRENCY_TOP = ['GBP', 'HKD', 'IDR', 'ILS', 'DKK', 'INR', 'CHF', 'MXN', 'CZK', 'SGD', 'THB', 'HRK', 'EUR', 'MYR', 'NOK',
                'CNY', 'BGN', 'PHP', 'PLN', 'ZAR', 'CAD', 'ISK', 'BRL', 'RON', 'NZD', 'TRY', 'JPY', 'RUB', 'KRW', 'USD',
                'AUD', 'HUF', 'SEK']

# 0 1
# 1 0
# 0 0
# 1 1


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

    redis_key = 'valid_currencies' if int(request_params['merge']) == 1 else 'old_currencies'
    redis_dict = {}
    for currency in CURRENCY_TOP:
        response = await requests.get('https://api.ratesapi.io/api/latest', params={'base': currency})
        rates = await response.json()
        if 'error' in rates:
            continue
        redis_dict[currency] = dumps(rates['rates'])
        await request.app['redis'].hmset_dict(redis_key, redis_dict)
    return web.json_response(data={'result': "Storage was filled with data"})


async def convert(request):
    """
    Description end-point
    ---
    tags:
    - Converting
    summary: Convert currency
    description: This end-point allow to convert currency.
    produces:
    - application/json
    parameters:
    - in: query
      name: from
      type: string
      description: currency from which we convert
      required: true
    - in: query
      name: to
      type: string
      description: currency into which we convert
      required: true
    - in: query
      name: amount
      type: integer
      description: amount of currency units
      required: true
    responses:
        "200":
            description: successful operation. Return converting data
        "405":
            description: invalid HTTP Method
    """
    request_params = request.query
    if set(request_params.keys()) == {'from', 'to', 'amount'} and len(request_params) == 3:

        currency = await request.app['redis'].hget('valid_currencies', request_params['from'])
        if currency is None:
            return web.json_response(
                data={'error': f"{request_params['from']} is not supported"})
        else:
            currencies = loads(currency.decode())
            if request_params['to'] in currencies:
                result_amount = round(currencies[request_params['to']] * int(request_params['amount']), 2)
                result = {
                    'result': f"{request_params['amount']} {request_params['from']} = {result_amount} {request_params['to']}"}
                return web.json_response(data=result)
            else:
                return web.json_response(
                    data={'error': f"{request_params['from']} -> {request_params['to']} is not supported"})

    else:
        return web.json_response(data={'error': 'invalid params'})
