"""A simple driver for simulating application events"""
import asyncio
from database_handler import DatabaseHandler
from auth_handler import AuthHandler

async def view_all():
    async with DatabaseHandler.acquire() as conn:
        print(await conn.fetch("SELECT * FROM user_auth"))

async def run():
    await DatabaseHandler.load()
    res = await AuthHandler.sign_up("example@gmail.com", "yeehaw", "George", "M")
    print(res)
    res = await AuthHandler.log_in("example@gmail.com", "yeehaw")
    print(res)
    await view_all()

asyncio.run(run())