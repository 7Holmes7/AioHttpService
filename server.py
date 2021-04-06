from aiohttp import web
from aiohttp_swagger import setup_swagger
from redis import add_redis, dispose_redis
from datetime import datetime
from json import dumps, loads


async def handle(request):
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
    name = request.match_info.get('currency', "USD")
    # await service['redis'].set(name, name)
    result = await service['redis'].hgetall(name)
    if not result:
        rates = {
            "base": name,
            "date": str(datetime.now()),
            "rates": dumps({
                "CAD": 1.260046,
                "CHF": 0.933058,
                "EUR": 0.806942,
                "GBP": 0.719154
            })
        }

        # rates = {
        #     "base": name,
        #     "date": str(datetime.now()),
        #     "rates": 123
        # }
        await service['redis'].hmset_dict(name, rates)
        return web.Response(text=f"New rates for {name}: {rates}")

    else:
        text = f"Data for {name}: {result}"
        return web.Response(text=text)


service = web.Application()
service.on_startup.append(add_redis)
service.on_cleanup.append(dispose_redis)
service.add_routes([web.get('/', handle),
                    web.get('/{currency}', handle)])

setup_swagger(service)

if __name__ == '__main__':
    web.run_app(service, host="127.0.0.1")
