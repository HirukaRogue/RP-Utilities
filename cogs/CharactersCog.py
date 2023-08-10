import discord
from discord.ext import commands
import rpu_database

class CharactersCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("CharactersCog.py is ready")

    @commands.HybridGroup(name = "character", invoke_without_command = True, aliases = ["char"])
    async def character(self, ctx):
        await ctx.send("character related commands, use default if you are a starter.")

    @character.command(name = "default",invoke_without_command = True, aliases = ["def"])
    async def default(self, ctx):
        await ctx.send("""default characters creation
                       This is for when you don't plan to use templates or
                       you are a newbie with this bot. Also this option is
                       The first way of creating character in this beta version.
                       """)

    @default.command(name = "search")
    async def search(self, ctx, search: str | None):
        user = ctx.user.id

        search_result = rpu_database.Database.search_default_character(user_id=user, name=search) or rpu_database.Database.search_default_character(user_id=user,prompt_prefix=search)
        embed = discord.Embed(
            title=f"Your characters searched with {search}"
        )

    @default.command(name="create", aliases = ["create"])
    async def create(self, ctx, name: str, prompt: str, image: discord.Attatchment | str | None):
        user = ctx.user.id
        url = image.url if image and isinstance(image, discord.Attachment) else image
        
        response = ["Error, the character with this prompt already exist." if rpu_database.Database.register_default_character(user, name, prompt, url) else "Character created."]

        await ctx.send(response)

    @default.command(name="edit")
    async def edit(self, ctx):
        await ctx.send("Edited")

    @default.command(name="delete", aliases = ["del"])
    async def delete(self, ctx):
        await ctx.send("Deleted")

async def setup(client):
    await client.add_cog(CharactersCog(client))