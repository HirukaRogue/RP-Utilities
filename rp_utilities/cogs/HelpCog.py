import discord
from discord.ext import commands
from help import Help


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = Help()
        bot.help_command.cog = self

    def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command

    @commands.Cog.listener()
    async def on_ready(self):
        print("HelpCog.py is ready")


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
