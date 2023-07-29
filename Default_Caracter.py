import discord
from discord.ext import commands

class Default_Character(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Default_Character.py is ready")

     @commands.group(name="default character", aliases="defchar", case_insensitive=false)
     async def default_character(self):
         ...

    @commands.command(name="character.create")
    async def create_character(self, ctx):
        await ctx.send("Created")

    @commands.command(name="character.edit")
    async def create_character(self, ctx):
        await ctx.send("Edited")

    @commands.command(name="character.delete")
    async def create_character(self, ctx):
        await ctx.send("Deleted")

async def setup(client):
    await client.add_cog(Default_Character(client))