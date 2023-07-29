import discord
from discord.ext import commands
import os
import sys

class Developer(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Developer.py is ready")

    @commands.command()
    async def restart(self, ctx):
        await ctx.send("Restarting...")
        os.execlp('RP Utilities', 'RP Utilities', "bot.py", *sys.argv)

async def setup(client):
    await client.add_cog(Developer(client))