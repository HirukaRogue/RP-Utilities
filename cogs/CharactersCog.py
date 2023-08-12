import discord
from discord.ext import commands
from discord.ext import menus
from copy import deepcopy
from dataclasses import dataclass

class CharactersCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("CharactersCog.py is ready")

    @commands.hybrid_group(name = "character", fallback="help", invoke_without_command = True, aliases = ["char"])
    async def _character(self, ctx):
        await ctx.send("character related commands, use default if you are a starter.")

    @_character.group(name = "default",invoke_without_command = True, aliases = ["def"])
    async def _character_default(self, ctx):
        await ctx.send("""default characters creation
                       This is for when you don't plan to use templates or
                       you are a newbie with this bot. Also this option is
                       The first way of creating character in this beta version.
                       """)

    @_character.command(name = "search")
    async def _character_search(self, ctx, search: str | None):
        user = ctx.author.id
        prompt_result = f"Your result with {search}" if search else "All your characters"

        search_result = await ctx.bot.database.search_default_character(user_id=user, name=search, prompt_prefix=None)
        search_pivot = await ctx.bot.database.search_default_character(user_id=user, name=None, prompt_prefix=search)
        search_result = search_pivot | search_result if search_result and search_pivot else search_result
        search_result = await ctx.bot.database.search_default_character(user_id=user, name=None, prompt_prefix=None) if search_result is None else search_result
        
        prompt_result = "No results found" if search_result is None else prompt_result
        pages = []
        embed = discord.Embed(
            title="Search Result",
            description=prompt_result
        )
        embed.set_author(name="RP Utilities")
        
        page = []
        
        display = 10
        if search_result is not None:
            page_count = 0
            for num,i in enumerate(search_result):
                name = i["name"]
                prompt = i["prompt_prefix"]
                pfp = i["image_url"]

                page.append(name,prompt,pfp)
                
                if num < len(search_result) or num%display > 0:
                    page_count = page_count + 1
                    emb = deepcopy(embed)
                    
                    print("\n".join([str(x["name"]) for x in page]))
                    # emb.add_field(name="Name", value = "\n".join([str(x["name"]) for x in page]))
                    # emb.add_field(name="Prompt", value = [f"{x[prompt]}\n" if x is not page[display-1] else x[name] for x in page])
                    # emb.add_field(name="profile pic", value = [f"{x[pfp]}\n" if x is not page[display-1] else x[pfp] for x in page])
                    emb.set_footer(text=f"Page {page_count}/{int(len(search_result)/display)}")

                    page = []

                    pages.append(emb)

        pages = [embed] if len(pages) == 0 else pages
        print(pages)
        menu_formatter = List_source(pages, per_page=1)
        
        result_menu = PageMenu(menu_formatter)
        await result_menu.start(ctx)

    @_character_default.command(name="create_default", aliases = ["create"], with_app_command = False)
    async def _character_default_create(self, ctx, name: str, prompt: str, image: str | None):
        user = ctx.author.id
        
        response = "Error, the character with this prompt already exist." if await ctx.bot.database.register_default_character(user_id=user, name=name, prompt_prefix=prompt, image=image) else "Character created."

        await ctx.send(response)

    # Slash version
    @_character_default.app_command.command(name = "create",)
    async def _character_default_create_slash(self, ctx: discord.Interaction, name: str, prompt: str, image_1: discord.Attachment | None, image_2: str | None):
        user = ctx.user.id
        url = image_1.url if image_1 else image_2
        
        response = "Error, the character with this prompt already exist." if await ctx.bot.database.register_default_character(user_id=user, name=name, prompt_prefix=prompt, image=url) else "Character created."

        await ctx.send(response)

    @_character_default.command(name="edit")
    async def _character_default_edit(self, ctx):
        await ctx.send("Edited")

    @_character_default.command(name="delete", aliases = ["del"])
    async def _character_default_delete(self, ctx, deleting_prompt: str):
        user = ctx.author.id

        # result = await ctx.bot.database.delete_default_character(user_id=user, name=deleting_prompt)
        # if result is "ERROR" or result:
        #     ctx.bot.database.search_default_character(user_id=user, name=deleting_prompt)

        # if result is "ERROR":
        #     await ctx.send("Character not found.")
        # if result is "SUCESS":
        #     await ctx.send("Character deleted.")
        # else:
        #     embed = discord.Embed(
        #     title="More than 1 result was found",
        #     description="Click a link to select one"
        #     )
        #     embed.add_field(name="Name", value= [i["name"] for i in result])
        #     embed.set_author(name="RP Utilities")

async def setup(client):
    await client.add_cog(CharactersCog(client))

class Character:
    name: str
    prompt: str
    image: str

    def set_values(self, doc):
        self.name: doc['name']
        self.prompt: doc['prompt_prefix']
        self.image: doc['image_url']

class PageMenu(menus.MenuPages):
    
    @menus.button("First page")
    async def on_first(self, payload):
        await self.show_page(0)

    @menus.button('Prev page')
    async def on_prev(self, payload):
        await self.show_checked_page(self.current_page - 1)
    
    @menus.button('Close search')
    async def on_close(self, payload):
        self.stop()

    @menus.button('Next page')
    async def on_prev(self, payload):
        await self.show_checked_page(self.current_page - 1)
    
    @menus.button("Last page")
    async def on_first(self, payload):
        max_pages = self._source.get_max_pages()
        last_page = max(max_pages - 1, 0)

class List_source(menus.ListPageSource):
    async def format_page(self, menu, entries):
        embed = entries
        return embed