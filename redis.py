from aioredis import create_redis_pool


async def add_redis(service):
    service['redis'] = await create_redis_pool(service['config']['redis_address'], db=1)


async def dispose_redis(service):
    service['redis'].close()
    await service['redis'].wait_closed()
