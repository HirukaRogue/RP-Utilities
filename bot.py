import bot_token
import discord
from discord.ext import commands
import os
from rpu_database import Database


bot_status = ["initializing", "active", "shutting down"]

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.database = Database()
        print("Bot Connected!")

    async def setup_hook(self) -> None:
        await self.database.connect("mongodb://localhost:27017")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    async def close(self) -> None:
        await super().close()
        # await self.database.close()

#asyncio.run(Bot.main(), debug=False)
Bot(command_prefix='rpu->', intents=discord.Intents.all()).run(bot_token.return_token())