from aiohttp import web
from aiohttp_swagger import setup_swagger
from redis import add_redis, dispose_redis
from endpoints.endpoints import feel_storage, convert


async def create_service():
    service = web.Application()
    service.on_startup.append(add_redis)
    service.on_cleanup.append(dispose_redis)
    service.add_routes([web.post('/database', feel_storage),
                        web.get('/convert', convert)])

    setup_swagger(service)

    return service
