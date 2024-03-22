import discord
from discord.ext import commands

class TemplateCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Template.py is ready")

    @commands.command(aliases = ['template.create'])
    async def create_template(self, ctx: discord.ext.commands.Context):
        user_id = ctx.author.id
        server_id = ctx.guild.id
        
        template_creation=discord.Embed(
        color=0x00FFFF,
        title="Creating template",
        description="set your template stuffs here")
        
        template_creation.add_field(name="test field", value="test field", inline=True)
        template_creation.set_footer(text="1/1 page")

        await ctx.send(embed = template_creation)
        # data = {
        # "name": "",
        # "age": "",
        # "gender": ""
        # }

        # Database.add_template(self=Database, user_id=user_id, guild_id=server_id, data=data)

        # await ctx.send(f"Template Created")

    @commands.command(aliases = ['template.edit'])
    async def edit_template(self, ctx):
        
        await ctx.send(f"Template Edited")
    
    @commands.command(aliases = ['template.delete'])
    async def delete_template(self, ctx):
        
        await ctx.send(f"Template Deleted")

async def setup(client):
    await client.add_cog(TemplateCog(client))