from aiohttp import web
from service import create_service

if __name__ == '__main__':
    web.run_app(create_service(), host="127.0.0.1")