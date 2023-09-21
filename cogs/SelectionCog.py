import discord
from discord.ext import commands
from discord import app_commands
import re

import random

from help import Help

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

    @commands.command()
    async def select_help(self, ctx):
        embed = discord.Embed(
            description=Help.select()
        )

        ctx.send(embed=embed)
    
    @app_commands.command(name="select")
    async def select_slash(self, ctx: discord.Interaction, args: str | None = None):
        if args:
            pattern = r'\((.*?)\)'
            matches = re.findall(pattern, args)
            number = len(matches) - 1
            selected = matches[random.randint(0, number)]
            embed = discord.Embed(
                title="Selected:",
                description=selected
            )
            await ctx.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
            description=Help.select()
            )

            ctx.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(SelectionCog(client))