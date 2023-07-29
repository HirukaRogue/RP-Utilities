import discord
from discord.ext import commands

class Character(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Character.py is ready")

    @commands.command(name="character.create")
    async def create_character(self, ctx):
        await ctx.send("Created")

    @commands.command(name="character.edit")
    async def create_character(self, ctx):
        await ctx.send("Edited")

    @commands.command(name="character.delete")
    async def create_character(self, ctx):
        await ctx.send("Edited")

async def setup(client):
    await client.add_cog(Character(client))