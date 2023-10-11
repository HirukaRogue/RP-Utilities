import discord
from discord.ext import commands
from discord.ext import menus
from discord import ui
import asyncio

from pagination import Paginator
from milascenous import is_link
from milascenous import unify
from help import Help

from copy import deepcopy

class CharactersCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("CharactersCog.py is ready")

    @commands.hybrid_group(name = "character", fallback="help", invoke_without_command = True, aliases = ["char"])
    async def _character(self, ctx):
        embed = discord.Embed(
            description=await Help.character()
        )
        await ctx.send(embed)

    @_character.group(name = "default", fallback="help", invoke_without_command = True, aliases = ["def"])
    async def _character_default(self, ctx):
        embed = discord.Embed(
            description=await Help.char_default()
        )
        await ctx.send(embed)

    @_character.command(name = "search")
    async def _character_search(self, ctx, search: str | None):
        user = ctx.author.id
        prompt_result = f"Your result with {search}" if search else "All your characters"
        search_result = list()

        if search is None:
            search_result = await ctx.bot.database.search_default_character(user_id=user)

        else:
            search_pivot = await ctx.bot.database.search_default_character(user_id=user, name=search)
            if search_pivot:
                search_result = search_pivot
            
            search_pivot = await ctx.bot.database.search_default_character(user_id=user, prompt_prefix=search)
            if  search_pivot and len(search_result) == 0:
                search_result = search_pivot
            elif search_pivot:
                search_result = unify(search_result,search_pivot)

        prompt_result = "No results found" if search_result is None else prompt_result
        pages = list()
        embed = discord.Embed(
            title="Search Result",
            description=prompt_result
        )
        embed.set_author(name="RP Utilities")
        

        display = 10
        if search_result is not None:
            page_count = 0
            page = list()

            for num,i in enumerate(search_result):
                keys = list(i.keys())
                data = {
                        keys[0]: i['name'],
                        keys[1]: i['prompt_prefix'],
                        keys[2]: i['image_url']
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
        result_menu = Paginator(pages)

        await result_menu.start(ctx)
    
    @_character.command(name = "search_help")
    async def _character_search_help(self, ctx):
        embed = discord.Embed(
            description=await Help.char_search()
        )
        await ctx.send(embed)

    @_character_default.command(name="create_default", aliases = ["create"], with_app_command = False)
    async def _character_default_create(self, ctx, name: str | None, prompt: str | None, image: str | None):
        if name and prompt:
            user = ctx.author.id
            
            if len(prompt) <= 17 and not prompt.startswith("#") and prompt.endswith(":"):
                response = "Error, the character with this prompt already exist." if await ctx.bot.database.register_default_character(user_id=user, name=name, prompt_prefix=prompt, image=image) else "Character created."
            elif len(prompt) > 17:
                response = "Your prompt cannot have more than 16 characters"
            elif prompt.startswith("##"):
                response = "You cannot start your prompt with #, since # is reserved for macros"
            elif not prompt.endswith(":"):
                response = "Your prompt shall ends with :"

            await ctx.send(response)
        else:
            embed = discord.Embed(
            description=await Help.char_default_create(ctx.guild.id)
            )
            await ctx.send(embed)

    # Slash version
    @_character_default.app_command.command(name = "create",)
    async def _character_default_create_slash(self, interaction: discord.Interaction, name: str | None, prompt: str | None, image_1: discord.Attachment | None, image_2: str | None):
        if name and prompt:
            user = interaction.user.id
            url = image_1.url if image_1 else image_2

            if len(prompt) <= 17 and not prompt.startswith("#") and prompt.endswith(":"):
                response = "Error, the character with this prompt already exist." if await self.client.database.register_default_character(user_id=user, name=name, prompt_prefix=prompt, image=url) else "Character created."
            elif len(prompt) > 17:
                response = "Your prompt cannot have more than 16 characters"
            elif prompt.startswith("##"):
                response = "You cannot start your prompt with #, since # is reserved for macros"
            elif not prompt.endswith(":"):
                response = "Your prompt shall ends with :"

            await interaction.response.send_message(response)
        else:
            embed = discord.Embed(
            description=await Help.char_default_create()
            )
            await interaction.response.send_message(embed)

    @_character_default.command(name="edit_name")
    async def _character_default_edit_name(self, ctx, old_name: str | None, new_name: str | None):
        if old_name and new_name:
            user = ctx.author.id

            result = await ctx.bot.database.update_default_character(user_id = user, old_name = old_name, new_name = new_name)
            
            if result == "ERROR":
                ctx.send("Character name not found")
            elif result == "SUCESS":
                ctx.send(f"Character name edited from {old_name} to {new_name}")
            else:
                embed = discord.Embed(
                    title="There is more than 1 result for what you want to edit",
                    description="try again with 'edit name with prompt'"
                )
                names = ""

                for data in result:
                    piv_str = f"{data['name']}\n" if data is not result[-1] else data['name']
                    names = names+piv_str

                embed.add_field(name="Name", value=names)

                embed.set_author(name="RP Utilities")
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
            description=await Help.char_default_edit_name()
            )
            await ctx.send(embed)

    @_character_default.command(name="edit_name_by_prompt")
    async def _character_default_edit_name_by_prompt(self, ctx, prompt: str | None, new_name: str | None):
        if prompt and new_name:
            user = ctx.author.id

            result = await ctx.bot.database.update_default_character(user_id = user, old_prompt_prefix = prompt, new_name=new_name)
            
            if result == "ERROR":
                await ctx.send("Character name not found")
            elif result == "SUCESS":
                await ctx.send(f"Character name edited of prompt {prompt} to {new_name}")
        else:
            embed = discord.Embed(
            description=await Help.char_default_edit_name_by_prompt(ctx.guild.id)
            )
            await ctx.send(embed)

    @_character_default.command(name="edit_prompt")
    async def _character_default_edit_prompt(self, ctx, old_prompt: str | None, new_prompt: str | None):
        if old_prompt and new_prompt:
            user = ctx.author.id

            result = await ctx.bot.database.update_default_character(user_id = user, old_prompt_prefix = old_prompt, new_prompt_prefix=new_prompt)
            
            if result == "ERROR":
                await ctx.send("Character name not found")
            elif result == "SUCESS":
                await ctx.send(f"Character prompt edited from {old_prompt} to {new_prompt}")
        else:
            embed = discord.Embed(
            description=await Help.char_default_edit_prompt()
            )
            await ctx.send(embed)

    @_character_default.command(name="delete", aliases = ["del"])
    async def _character_default_delete(self, ctx, deleting_prompt: str | None):
        if deleting_prompt:
            user = ctx.author.id

            result = await ctx.bot.database.delete_default_character(user_id=user, prompt_prefix=deleting_prompt)
            if result == "ERROR":
                result = await ctx.bot.database.delete_default_character(user_id=user, name=deleting_prompt)
            elif result and result != "SUCESS":
                sub_result = await ctx.bot.database.search_default_character(user_id=user, name=deleting_prompt)
                result = unify(result, sub_result)

            if result == "ERROR":
                await ctx.send("Character not found.")
            elif result == "SUCESS":
                await ctx.send("Character deleted.")
            else:
                names = ""
                prompts = ""

                embed = discord.Embed(
                title="There is more than 1 result for what you want to delete",
                description="type the full name or prefix to delete the one you want"
                )
                for data in result:
                    piv_str = f"{data['name']}\n" if data is not result[-1] else data['name']
                    names = names + piv_str
                    piv_str = f"{data['prompt_prefix']}\n" if data is not result[-1] else data['prompt_prefix']
                    prompts = prompts + piv_str
                
                embed.add_field(name="Name", value=names)
                embed.add_field(name="Prompt", value=prompts)

                embed.set_author(name="RP Utilities")
                await ctx.send(embed=embed)
        
        else:
            embed = discord.Embed(
            description=await Help.char_default_delete()
            )
            await ctx.send(embed)
            
    @_character_default.command(name="image", aliases=["img", "pfp", "profile"])
    async def _character_default_image(self, ctx, name: str | None):
        if name:
            user = ctx.author.id

            result = await ctx.bot.database.quick_search_default_character(user_id=user, name=name)

            if result is None:
                await ctx.send(f"you have no characters with name {name}")
            elif len(result) == 1:
                result = result[0]
                await ctx.send(result['image_url'])
            else:
                embed = discord.Embed(
                    title="There is more than 1 result for what you want to show image",
                    description="try again showing image with prompt'"
                )
                names = ""
                prompts = ""
                images = ""

                for data in result:
                    piv_str = f"{data['name']}\n" if data is not result[-1] else data['name']
                    names = names+piv_str
                    piv_str = f"{data['prompt_prefix']}\n" if data is not result[-1] else data['prompt_prefix']
                    prompts = prompts + piv_str
                    if is_link(data['image_url']):
                        piv_str = f"[Link]({data['image_url']} \'Click to open\')\n" if data is not result[-1] else f"[Link]({data['image_url']} \'Click to open\')"
                    else:
                        piv_str = "None\n" if data is not result[-1] else "None"
                    images = images + piv_str

                embed.add_field(name="Name", value=names)

                embed.set_author(name="RP Utilities")
                await ctx.send(embed=embed)
        
        else:
            embed = discord.Embed(
            description=await Help.char_default_image()
            )
            await ctx.send(embed)

    @_character_default.command(name="set image", aliases=["img_set", "pfp_set", "profile_set"], with_app_command = False)
    async def _character_default_image_set(self, ctx, name: str | None, image: str | None):
        if name and image:
            user = ctx.author.id

            result = await ctx.bot.database.update_default_character(user_id=user, old_name=name, new_image=image)

            if result is None:
                await ctx.send(f"you have no characters with name {name}")
            elif result == "SUCESS":
                await ctx.send(f"image set to {image}")
            else:
                embed = discord.Embed(
                    title="There is more than 1 result for what you want to set image",
                    description="try again set image with prompt"
                )
                names = ""
                prompts = ""
                images = ""

                for data in result:
                    piv_str = f"{data['name']}\n" if data is not result[-1] else data['name']
                    names = names+piv_str
                    piv_str = f"{data['prompt_prefix']}\n" if data is not result[-1] else data['prompt_prefix']
                    prompts = prompts + piv_str
                    if is_link(data['image_url']):
                        piv_str = f"[Link]({data['image_url']} \'Click to open\')\n" if data is not result[-1] else f"[Link]({data['image_url']} \'Click to open\')"
                    else:
                        piv_str = "None\n" if data is not result[-1] else "None"
                    images = images + piv_str

                embed.add_field(name="Name", value=names)

                embed.set_author(name="RP Utilities")
                await ctx.send(embed=embed)

        else:
            embed = await discord.Embed(
            description=await Help.char_default_image_set()
            )
            await ctx.send(embed)

    @_character_default.app_command.command(name = "image_set",)
    async def _character_default_image_set_slash(self, interaction: discord.Interaction, name: str | None, image1: discord.Attachment | None, image2: str | None):
        if name and image1 or name and image2:
            user = interaction.user.id
            url = image1.url if image1 else image2

            result = await self.client.database.update_default_character(user_id=user, old_name=name, new_image=url)

            if result is None:
                await interaction.response.send_message(f"you have no characters with name {name}")
            elif result == "SUCESS":
                await interaction.response.send_message(f"image set to {url}")
            else:
                embed = discord.Embed(
                    title="There is more than 1 result for what you want to set image",
                    description="try again set image with prompt"
                )
                names = ""
                prompts = ""
                images = ""

                for data in result:
                    piv_str = f"{data['name']}\n" if data is not result[-1] else data['name']
                    names = names+piv_str
                    piv_str = f"{data['prompt_prefix']}\n" if data is not result[-1] else data['prompt_prefix']
                    prompts = prompts + piv_str
                    if is_link(data['image_url']):
                        piv_str = f"[Link]({data['image_url']} \'Click to open\')\n" if data is not result[-1] else f"[Link]({data['image_url']} \'Click to open\')"
                    else:
                        piv_str = "None\n" if data is not result[-1] else "None"
                    images = images + piv_str

                embed.add_field(name="Name", value=names)

                embed.set_author(name="RP Utilities")
                await interaction.response.send_message(embed=embed)

        else:
            embed = discord.Embed(
            description=await Help.char_default_image_set()
            )
            await interaction.response.send_message(embed)
    
    @_character_default.command(name="image_by_prompt", aliases=["img_by_prompt", "pfp_by_prompt", "profile_by_prompt"])
    async def _character_default_image_by_prompt(self, ctx, prompt: str | None):
        if prompt:
            user = ctx.author.id

            result = await self.client.database.quick_search_default_character(user_id=user, old_prompt_prefix=prompt)

            if result is None:
                await ctx.send(f"you have no characters with prompt {prompt}")
            else:
                result = result[0]
                await ctx.send(result['image_url'])
        
        else:
            embed = discord.Embed(
            description=await Help.char_default_image_by_prompt()
            )
            await ctx.send(embed)

    @_character_default.command(name="set image by prompt", aliases=["img_set_by_prompt", "pfp_set_by_prompt", "profile_set_by_prompt"], with_app_command = False)
    async def _character_default_image_by_prompt_set(self, ctx, prompt: str | None, image: str | None):
        if prompt and image:
            user = ctx.author.id

            result = await self.client.database.quick_search_default_character(user_id=user, old_prompt_prefix=prompt, new_image=image)

            if result is None:
                await ctx.send(f"you have no characters with prompt {prompt}")
            else:
                await ctx.send(f"image set to {image}")
        
        else:
            embed = await discord.Embed(
            description=Help.char_default_image_set_by_prompt()
            )
            await ctx.send(embed)

    @_character_default.app_command.command(name = "image_set_by_prompt",)
    async def _character_default_image_set_by_prompt_slash(self, interaction: discord.Interaction, prompt: str | None, image1: discord.Attachment | None, image2: str | None):
        if prompt and image1 or prompt and image2:
            user = interaction.user.id
            url = image1.url if image1 else image2

            result = await self.client.database.quick_search_default_character(user_id=user, prompt_prefix=prompt, new_image=url)

            if result is None:
                await interaction.response.send_message(f"you have no characters with prompt {prompt}")
            else:
                await interaction.response.send_message(f"image set to {url}")
        
        else:
            embed = discord.Embed(
            description=await Help.char_default_image_set_by_prompt()
            )
            await interaction.response.send_message(embed)

            
async def setup(client):
    await client.add_cog(CharactersCog(client))