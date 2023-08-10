import discord
from discord.ext import commands

class ActionCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Action.py is ready")
    
    @commands.command(aliases = ['interact', 'action', 'act', 'roleplay'])
    async def rp(self, ctx):
        await ctx.send(f"Interacting")

async def setup(client):
    await client.add_cog(ActionCog(client))