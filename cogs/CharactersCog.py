import discord
from discord.ext import commands
from discord.ext import menus
from copy import deepcopy
from urllib.parse import urlparse

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
        search_result = list()

        if search is None:
            search_result = await ctx.bot.database.search_default_character(user_id=user, name=None, prompt_prefix=None)
        
        else:
            search_pivot = await ctx.bot.database.search_default_character(user_id=user, name=search, prompt_prefix=None)
            if search_pivot:
                search_result = search_pivot

            search_pivot = await ctx.bot.database.search_default_character(user_id=user, name=None, prompt_prefix=search)
            if  search_pivot and search_result[0] is None:
                search_result = search_pivot
            elif search_pivot:
                search_result = search_pivot + search_result


        prompt_result = "No results found" if search_result is None else prompt_result
        pages = list()
        embed = discord.Embed(
            title="Search Result",
            description=prompt_result
        )
        embed.set_author(name="RP Utilities")
        

        display = 1
        if search_result[0] is not None:
            page_count = 0
            page = list()

            for num,i in enumerate(search_result):
                keys = list(i.keys())
                data = {
                        keys[2]: i['name'],
                        keys[3]: i['prompt_prefix'],
                        keys[4]: i['image_url']
                        }

                page.append(data)
                
                if num >= len(search_result)-1 or (num+1)%display == 0:
                    page_count = page_count + 1
                    emb = deepcopy(embed)

                    names = ''
                    prompts = ''
                    images = ''

                    for data in page:
                        piv_str = f"{data['name']}\n" if data is not page[-1] else data['name']
                        names = names + piv_str
                        piv_str = f"{data['prompt_prefix']}\n" if data is not page[-1] else data['prompt_prefix']
                        prompts = prompts + piv_str
                        if is_link(data['image_url']):
                            piv_str = f"[Link]({data['image_url']} \'Click to open\')\n" if data is not page[-1] else f"[Link]({data['image_url']} \'Click to open\')"
                        else:
                            piv_str = "None\n" if data is not page[-1] else "None"
                        images = images + piv_str
                    emb.add_field(name="Name", value = names)
                    emb.add_field(name="Prompt", value = prompts)
                    emb.add_field(name="profile pic", value = images)
                    
                    emb.set_footer(text=f"Page {page_count}/{(int(len(search_result)/display))+1 if len(search_result)%display != 0 else int(len(search_result)/display)}")

                    page = list()

                    pages.append(emb)

        pages = [embed] if len(pages) == 0 else pages
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

def is_link(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

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