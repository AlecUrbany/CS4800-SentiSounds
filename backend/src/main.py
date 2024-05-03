"""The main driver for beginning the program's execution"""

import asyncio

from api import app
from hypercorn.asyncio import serve
from hypercorn.config import Config

if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    config.accesslog = "-"

    asyncio.run(serve(app, config))
