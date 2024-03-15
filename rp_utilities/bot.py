import bot_token
import discord
import asyncio
from discord.ext import commands
import os
from rpu_database import Database
from help import Help
import logging

handler = logging.FileHandler(filename="rpu_log.log", encoding="utf-8", mode="w")

bot_status = ["initializing", "active", "shutting down"]
DEFAULT_PREFIX = "rpu->"
EXTENSIONS = [
    "jishaku",
]
INTENTS = discord.Intents.default()
INTENTS.message_content = True


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=INTENTS,
            command_prefix=prefix_setup,
            case_insensitive=True,
        )
        self.database = Database()
        self.help_command = commands.MinimalHelpCommand()
        print("Bot Connected!")

    async def setup_hook(self) -> None:
        await self.database.connect()
        for extension in EXTENSIONS:
            await self.load_extension(extension)
        await self.add_cog(PrefixCog(self))
        for filename in os.listdir("rp_utilities/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        await self.tree.sync()

    async def close(self) -> None:
        await super().close()
        await self.database.close()


async def prefix_setup(bot, message) -> str:
    prefix = await bot.database.get_prefix(guild_id=message.guild.id)
    if prefix:
        return prefix
    else:
        return DEFAULT_PREFIX


class PrefixCog(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="prefix", fallback="help", invoke_without_command=True)
    async def _prefix(self, ctx: commands.Context, *, prefix: str) -> None:
        await ctx.send("Use this command to set or reset the this bot prefix in your server")

    @_prefix.command(name="set")
    async def _prefix_set(self, ctx: commands.Context, *, prefix: str) -> None:
        await self.bot.database.set_prefix(guild_id=ctx.guild.id, prefix=prefix)
        await ctx.send(f"Prefix set to `{prefix}`.")

    @_prefix.command(name="reset")
    async def _prefix_reset(self, ctx: commands.Context) -> None:
        await self.bot.database.remove_prefix(guild_id=ctx.guild.id)
        await ctx.send(f"The prefix has been reset to `{DEFAULT_PREFIX}`.")


bot = Bot()


def run_bot():
    bot.run(
        bot_token.return_token(), log_handler=handler, log_level=logging.DEBUG, root_logger=True
    )
