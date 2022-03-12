import os
import sys
from pathlib import Path

from steam.steam_user import SteamUser
from config import *



async def test():
    user = SteamUser(USERNAME, PASSWORD, {"shared_secret": SHARED_SECRET, "identity_secret": IDENTITY_SECRET})
    await user.login()
    print(await user.fetch_confirmations())

if __name__ == "__main__":
    import asyncio

    event = asyncio.new_event_loop()
    asyncio.set_event_loop(event)
    event.run_until_complete(test())
