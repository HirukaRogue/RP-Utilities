import discord
from discord.ext import commands
from discord import app_commands

import random

class SelectionCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("MathCog.py is ready")

    @commands.command()
    async def select(self, ctx, *args: str):
        matches = [i for i in args]
        number = len(matches) - 1
        selected = matches[random.randint(0, number)]
        embed = discord.Embed(
            title="Selected:",
            description=selected
        )
        ctx.send(embed=embed)
    
    @app_commands.command(name="select")
    async def select_slash(self, ctx: discord.Interaction, args: str):
        matches = args.split(" ")
        number = len(matches) - 1
        selected = matches[random.randint(0, number)]
        embed = discord.Embed(
            title="Selected:",
            description=selected
        )
        await ctx.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(SelectionCog(client))