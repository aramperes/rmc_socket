import os

from aiohttp import web

from rmc_socket import RMCSocketServer

if __name__ == '__main__':
    host = os.environ.get("RMC_SOCKET_HOST", default="0.0.0.0")
    port = int(os.environ.get("RMC_SOCKET_PORT", default=8082))
    server = RMCSocketServer(
        redis_host=os.environ.get("REDIS_HOST", default="127.0.0.1"),
        redis_port=int(os.environ.get("REDIS_PORT", default=6379))
    )

    web.run_app(server.web, host=host, port=port)
    print("Running")
