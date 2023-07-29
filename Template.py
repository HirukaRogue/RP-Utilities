import discord
from discord.ext import commands

class Template(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Template.py is ready")

    @commands.command(aliases = ['template.create'])
    async def create_template(self, ctx: discord.ext.commands.Context):
        
        await ctx.send(f"Template Edited")

    @commands.command(aliases = ['template.edit'])
    async def edit_template(self, ctx):
        
        await ctx.send(f"Template Edited")
    
    @commands.command(aliases = ['template.delete'])
    async def delete_template(self, ctx):
        
        await ctx.send(f"Template Deleted")

async def setup(client):
    await client.add_cog(Template(client))