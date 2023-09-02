import discord
from discord.ext import commands
from discord import app_commands

from sympy import *

class MathCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("MathCog.py is ready")

    @commands.command()
    async def math(self, ctx, args: str):
        string_result = args
        result = sympify(args)
        string_result = f"Problem: {args}\nSolution:{result}"
        embed = discord.Embed(
            description=string_result
        )
        await ctx.send(embed=embed)
    
    @app_commands.command(name="math")
    async def math_slash(self, interaction: discord.Interaction, args: str):
        string_result = args
        result = sympify(args)
        string_result = f"Problem: {args}\nSolution:{result}"
        embed = discord.Embed(
            description=string_result
        )
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(MathCog(client))