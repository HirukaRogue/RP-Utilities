import bot_token
import discord
import asyncio
from discord.ext import commands
import os
from rpu_database import Database


bot_status = ["initializing", "active", "shutting down"]
PREFIX = "rpu->"
EXTENSIONS = ['jishaku',]
INTENTS = discord.Intents.default()
INTENTS.message_content = True

class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=INTENTS,
            command_prefix=PREFIX,
            case_insensitive=True
        )
        self.database = Database()
        print("Bot Connected!")

    async def setup_hook(self) -> None:
        await self.database.connect("mongodb://localhost:27017")
        for extension in EXTENSIONS:
            await self.load_extension(extension)
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    async def close(self) -> None:
        await super().close()
        # await self.database.close()

#asyncio.run(Bot.main(), debug=False)
if __name__ is "__main__":
    bot = Bot()
    bot.run(bot_token.return_token())