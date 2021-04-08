from json import loads
from typing import Optional
from aiohttp import web
from endpoints.feeling import VALID_REDIS_KEY, OLD_REDIS_KEY


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
    request_params: dict = request.query
    if set(request_params.keys()) != {'from', 'to', 'amount'}:
        return web.json_response(data={'error': 'invalid params'})

    actual_currency: bytes = await request.app['redis'].hget(VALID_REDIS_KEY, request_params['from'])
    if actual_currency is None:
        old_currency: bytes = await request.app['redis'].hget(OLD_REDIS_KEY, request_params['from'])

        if old_currency is None:
            return web.json_response(
                data={'error': f"{request_params['from']} is not supported"})
        else:
            return web.json_response(data=get_converting_result(old_currency,
                                                                request_params,
                                                                add_info="Those rates already have not actual"))
    else:
        return web.json_response(data=get_converting_result(actual_currency, request_params))


def get_converting_result(currency: bytes,
                          request_params: dict,
                          add_info: Optional[str] = None) -> dict:
    currencies: dict = loads(currency.decode())
    if request_params['to'] in currencies:
        result_amount: float = round(currencies[request_params['to']] * int(request_params['amount']), 2)
        result = {
            'result': f"{request_params['amount']} {request_params['from']} = {result_amount} {request_params['to']}"}
        if add_info:
            result.update({'info': add_info})
        return result
    else:
        return {'error': f"{request_params['from']} -> {request_params['to']} is not supported"}
