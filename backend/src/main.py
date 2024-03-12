"""A simple driver for simulating application events"""
import asyncio
from database_handler import DatabaseHandler
from auth_handler import AuthHandler

async def view_all():
    async with DatabaseHandler.acquire() as conn:
        print(await conn.fetch("SELECT * FROM user_auth"))

async def run():
    await DatabaseHandler.load()
    AuthHandler.sign_up("jojomedhat2004@gmail.com", "yeehaw", "George", "M")

    entered = input("Enter Recieved Code: ")

    res = await AuthHandler.authenticate_user("jojomedhat2004@gmail.com", "yeehaw", entered, "George", "M")
    print(res)

    res = await AuthHandler.log_in("jojomedhat2004@gmail.com", "yeehaw")
    print(res)

    await view_all()

asyncio.run(run())