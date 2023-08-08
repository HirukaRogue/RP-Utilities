import bot_token
import discord
import asyncio
from discord.ext import commands
import os
from rpu_database import Database


bot_status = ["initializing", "active", "shutting down"]
DEFAULT_PREFIX = "rpu->"
EXTENSIONS = ['jishaku',]
INTENTS = discord.Intents.default()
INTENTS.message_content = True

class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=INTENTS,
            command_prefix = self.prefix_setup(),
            case_insensitive=True
        )
        self.database = Database()
        self.db_loop = self.database.dev_client.get_io_loop()
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
        await self.database.close()

    async def prefix_setup(self, ctx: commands.context):
        prefix = self.loop.run_until_complete(self.database.get_prefix(guild_id=ctx.guild.id))
        if prefix:
            return prefix
        else:
            return DEFAULT_PREFIX

class prefix():
    def __init__(self) -> None:
        pass
        self.bot = Bot()

    @commands.group(invoke_without_command = True)
    async def prefix(self, ctx: commands.Context, *, prefix: str) -> None:
        await self.bot.loop.run_until_complete(self.bot.database.set_prefix(guild_id=ctx.guild.id, prefix=prefix))
        await ctx.send(f"Prefix set to `{prefix}`!")
    @prefix.command()
    async def reset(self, ctx: commands.Context) -> None:
        await self.bot.loop.run_until_complete(self.bot.database.remove_prefix(guild_id=ctx.guild.id))
        await ctx.send(f"The prefix has been reset to `{DEFAULT_PREFIX}`.")

Bot().run(bot_token.return_token())