from aiohttp import web
from service import create_service
from config import CONFIG

if __name__ == '__main__':
    web.run_app(create_service(CONFIG))
