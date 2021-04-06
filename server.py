from aiohttp import web
from redis import add_redis, dispose_redis


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    await service['redis'].set(name, name)
    text = "Hello, " + name
    return web.Response(text=text)


service = web.Application()
service.on_startup.append(add_redis)
service.on_cleanup.append(dispose_redis)
service.add_routes([web.get('/', handle),
                    web.get('/{name}', handle)])

if __name__ == '__main__':
    web.run_app(service)
