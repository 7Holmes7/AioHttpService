from aiohttp import web
from aiohttp_swagger import setup_swagger
from redis import add_redis, dispose_redis
from datetime import datetime
from json import dumps, loads
from aiohttp_requests import requests

CURRENCY_TOP = ['GBP', 'HKD', 'IDR', 'ILS', 'DKK', 'INR', 'CHF', 'MXN', 'CZK', 'SGD', 'THB', 'HRK', 'EUR', 'MYR', 'NOK',
                'CNY', 'BGN', 'PHP', 'PLN', 'ZAR', 'CAD', 'ISK', 'BRL', 'RON', 'NZD', 'TRY', 'JPY', 'RUB', 'KRW', 'USD',
                'AUD', 'HUF', 'SEK']


async def feel(request):
    """
    ---
    description: This end-point allow to test that redis works.
    tags:
    - Redis check
    produces:
    - text/plain
    responses:
        "200":
            description: successful operation. Return data from redis
        "405":
            description: invalid HTTP Method
    """
    redis_dict = {'valid': 1, 'date': str(datetime.now().date())}
    for currency in CURRENCY_TOP:
        response = await requests.get('https://api.ratesapi.io/api/latest', params={'base': currency})
        rates = await response.json()
        if 'error' in rates:
            print(rates)
            continue
        redis_dict[currency] = dumps(rates['rates'])
    await service['redis'].hmset_dict('currencies', redis_dict)
    return web.Response(text="Redis server was filled")


async def get_data(request):
    get_params = request.query
    from_ = get_params.get('from')
    to_ = get_params.get('to')
    amount = get_params.get('amount')
    a = 'amount' in get_params
    b = '231' in get_params
    redis_result = await service['redis'].hgetall('currencies')
    return web.json_response(data=str(redis_result))


async def convert(request):
    """
    ---
    description: This end-point allow to test that redis works.
    tags:
    - Redis check
    produces:
    - text/plain
    responses:
        "200":
            description: successful operation. Return data from redis
        "405":
            description: invalid HTTP Method
    """
    get_params = request.query
    if set(get_params.keys()) == {'from', 'to', 'amount'} and len(get_params) == 3:

        currency = await service['redis'].hget('currencies', get_params['from'])
        if currency is None:
            return web.json_response(
                data={'error': f"{get_params['from']} is not supported"})
        else:
            currencies = loads(currency.decode())
            if get_params['to'] in currencies:
                result_amount = round(currencies[get_params['to']] * int(get_params['amount']), 2)
                return web.json_response(data={
                    'result': f"{get_params['amount']} {get_params['from']} = {result_amount} {get_params['to']}"})
            else:
                return web.json_response(
                    data={'error': f"{get_params['from']} -> {get_params['to']} is not supported"})

    else:
        return web.json_response(data={'error': 'invalid params'})


service = web.Application()
service.on_startup.append(add_redis)
service.on_cleanup.append(dispose_redis)
service.add_routes([web.post('/feel', feel),
                    web.get('/get', get_data),
                    web.get('/convert', convert)])

setup_swagger(service)

if __name__ == '__main__':
    web.run_app(service, host="127.0.0.1")
