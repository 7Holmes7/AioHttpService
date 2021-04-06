from aioredis import create_redis_pool


# noinspection PyShadowingNames
async def add_redis(service):
    service['redis'] = await create_redis_pool('redis://localhost', db=1)


# noinspection PyShadowingNames
async def dispose_redis(service):
    service['redis'].close()
    await service['redis'].wait_closed()
