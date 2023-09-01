import discord
from discord.ext import commands
import re

class MacroCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping.py is ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        checker = message.content
        if not checker.startswith("##"):
            return
        
    @commands.hybrid_group(name="macro", fallback="help")
    async def _macro(self, ctx):
        await ctx.send("With macros you can make shortcut to execute commands from the bot without needing to execute it manulally")
    
    @_macro.command(name="create")
    async def _macro_create(self, ctx, prefix, args):
        if not prefix.startswith("##"):
            ctx.send("Your macro prefix shall start with ##")
        else:
            pattern = r'!(\w+)\s*\((.*?)\)'
            commandos = re.findall(pattern, args)
            print(commandos)
            await ctx.send("Testado")


    @_macro.command(name="edit")
    async def _macro_create(self, ctx, prefix, args):
        ...

    @_macro.command(name="delete")
    async def _macro_create(self, ctx, prefix):
        ...

async def setup(client):
    await client.add_cog(MacroCog(client))