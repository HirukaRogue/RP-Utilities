import discord
from discord.ext import commands
from discord import app_commands
import re

import random


class SelectionCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("MathCog.py is ready")

    @commands.command(help="select")
    async def select(self, ctx, *args: str):
        matches = [i for i in args]
        number = len(matches) - 1
        selected = matches[random.randint(0, number)]
        embed = discord.Embed(title="Selected:", description=selected)
        await ctx.send(embed=embed)

    @app_commands.command(
        name="select", description="Select one random option from the inputed options"
    )
    @app_commands.describe(
        args="set options to be selected randomly. Note: Place all of the options between () to work"
    )
    async def select_slash(self, interaction: discord.Interaction, args: str):
        pattern = r"\((.*?)\)"
        matches = re.findall(pattern, args)
        number = len(matches) - 1
        selected = matches[random.randint(0, number)]
        embed = discord.Embed(title="Selected:", description=selected)
        await interaction.response.send_message(embed=embed)


async def setup(client):
    await client.add_cog(SelectionCog(client))
