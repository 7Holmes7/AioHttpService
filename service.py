from aiohttp import web
from aiohttp_swagger import setup_swagger
from redis import add_redis, dispose_redis
from endpoints.converting import convert
from endpoints.feeling import feel_storage
from config import CONFIG


async def create_service(config: dict):
    service = web.Application()
    service['config'] = config
    service.on_startup.append(add_redis)
    service.on_cleanup.append(dispose_redis)
    service.add_routes([web.post('/database', feel_storage),
                        web.get('/convert', convert)])

    setup_swagger(service)

    return service

if __name__ == '__main__':
    web.run_app(create_service(CONFIG))
