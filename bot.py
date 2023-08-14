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
            command_prefix = prefix_setup,
            case_insensitive=True
        )
        self.database = Database()
        print("Bot Connected!")

    async def setup_hook(self) -> None:
        await self.database.connect("mongodb://localhost:27017")
        self.db_loop = self.database.dev_client.get_io_loop()
        for extension in EXTENSIONS:
            await self.load_extension(extension)
        await self.add_cog(PrefixCog(self))
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    async def close(self) -> None:
        await super().close()
        await self.database.close()

async def prefix_setup(bot, message):
        prefix = await bot.database.get_prefix(guild_id=message.guild.id)
        if prefix:
            return prefix
        else:
            return DEFAULT_PREFIX

class PrefixCog(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.group(invoke_without_command = True)
    async def _prefix(self, ctx: commands.Context, *, prefix: str) -> None:
        await self.bot.database.set_prefix(guild_id=ctx.guild.id, prefix=prefix)
        await ctx.send(f"Prefix set to `{prefix}`.")
    @_prefix.command()
    async def _prefix_reset(self, ctx: commands.Context) -> None:
        await self.bot.database.remove_prefix(guild_id=ctx.guild.id)
        await ctx.send(f"The prefix has been reset to `{DEFAULT_PREFIX}`.")

Bot().run(bot_token.return_token())