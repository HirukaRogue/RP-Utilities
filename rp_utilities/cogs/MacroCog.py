import discord
from discord.ext import commands
from discord import app_commands

from ..macros import Macro
from copy import deepcopy

from ..miscellaneous import unify
from ..pagination import Paginator


class MacroCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("MacroCog.py is ready")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        checker = message.content
        if not checker.startswith("+>") and not checker.startswith("->"):
            return

        command = await self.client.database.quick_search_macro(
            prefix=checker, id=message.author.id if checker.startswith("+>") else message.guild.id
        )

        if (
            command["type"] == "server"
            and not message.author.guild_permissions.administrator
            and command["attribute"] != "public"
        ):
            return

        result = await Macro().exemac(
            args=command["cmd"],
            database=self.client.database,
            guild_id=message.guild.id,
            author_id=message.author.id,
            bot=self.client,
            starter=checker.startswith("->"),
        )

        if not isinstance(result, tuple):
            for i in result:
                print(f"{i = }")
                if isinstance(i, list):
                    z = i[0]
                else:
                    z = i or None

                if isinstance(z, discord.Embed):
                    await message.channel.send(embed=z)
                elif isinstance(z, Paginator):
                    ctx = await self.client.get_context(message)
                    await z.start(ctx)
                elif isinstance(z, list):
                    y = i
                    while True:
                        if isinstance(y, str) or isinstance(y, float):
                            break
                        y = y[0]
                    embed = discord.Embed(description=y)
                    await message.channel.send(embed=embed)
                elif z is not None:
                    embed = discord.Embed(description=i)
                    await message.channel.send(embed=embed)

    @commands.hybrid_group(name="macro", fallback="help", help="macro")
    async def _macro(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = discord.Embed(
            description="With macros you can make shortcut to execute commands from the bot without needing to execute it manulally"
        )
        await ctx.send(embed=embed)

    @_macro.command(
        name="docs",
        description="Shows the link for macro documentation, it countains the tutorial for it",
    )
    async def _macro_docs(self, ctx):
        embed = discord.Embed(
            title="Macros Documentation",
            description="macros documentation: [Click Here](https://rp-utilities.gitbook.io/rp-utilities-macro-documentation 'Click to open documentation')\n",
        )
        await ctx.send(embed=embed)

    @_macro.command(
        name="search",
        help="macro search",
        description="Allows you to search your macros like google, leave search in blank to get a list of commands",
    )
    @app_commands.describe(search="Your search input")
    async def _macro_search(self, ctx, search: str | None):
        user = ctx.author.id
        server = ctx.guild.id
        prompt_result = (
            f"Your result with {search}" if search else "All your macros and server macros"
        )
        search_result = list()

        if search is None:
            search_result = await ctx.bot.database.search_macro(id=user)
            if ctx.author.guild_permissions.administrator:
                search_pivot = await ctx.bot.database.search_macro(id=server)
                if search_pivot:
                    search_result = unify(search_result, search_pivot)
        else:
            search_result = await ctx.bot.database.search_macro(id=user, search=search)
            if ctx.author.guild_permissions.administrator:
                search_pivot = await ctx.bot.database.search_macro(id=server, search=search)
                if search_pivot:
                    search_result = unify(search_result, search_pivot)

        prompt_result = "No results found" if search_result is None else prompt_result
        pages = list()
        embed = discord.Embed(title="Search Result", description=prompt_result)
        embed.set_author(name="RP Utilities")
        display = 10
        if search_result is not None:
            page_count = 0
            page = list()

            for num, i in enumerate(search_result):
                keys = list(i.keys())
                data = {keys[0]: i["prefix"], keys[2]: i["type"], keys[3]: i["attribute"]}

                page.append(data)

                if num >= len(search_result) - 1 or (num + 1) % display == 0:
                    page_count = page_count + 1
                    emb = deepcopy(embed)

                    prefixes = ""
                    types = ""
                    attributes = ""

                    for data in page:
                        piv_str = f"{data['prefix']}\n" if data is not page[-1] else data["prefix"]
                        prefixes = prefixes + piv_str
                        piv_str = f"{data['type']}\n" if data is not page[-1] else data["type"]
                        types = types + piv_str
                        piv_str = (
                            f"{data['attribute']}\n" if data is not page[-1] else data["attribute"]
                        )
                        attributes = attributes + piv_str
                    emb.add_field(name="Prefix", value=prefixes)
                    emb.add_field(name="type", value=types)
                    emb.add_field(name="attribute", value=attributes)

                    emb.set_footer(
                        text=f"Page {page_count}/{(int(len(search_result)/display))+1 if len(search_result)%display != 0 else int(len(search_result)/display)}"
                    )

                    page = list()

                    pages.append(emb)

        pages = [embed] if len(pages) == 0 else pages
        result_menu = Paginator(pages)

        await result_menu.start(ctx)

    @_macro.command(
        name="create", help="macro create", desription="Allows you to create your own macros"
    )
    @app_commands.describe(
        prefix="Your macro prefix, starts with +> for user macro or -> for server macro",
        args="Your macro code, here you type what your macro will do",
        macro_attr="Your macro attribute, here you define as private, public or protected, by default the macro is programmed to be private",
    )
    async def _macro_create(
        self,
        ctx,
        prefix: str,
        args: str,
        macro_attr: str | None = "private",
    ):
        await ctx.defer(ephemeral=True)
        if not prefix.startswith("+>") and not prefix.startswith("->"):
            await ctx.send("Your macro prefix shall start with +> or ->")
        elif macro_attr not in ("public", "private", "protected"):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="Your macro attribute need to be or 'private' or 'public' or 'protected'",
            )
        elif (
            prefix.startswith("->")
            and ctx.guild is not None
            and not ctx.author.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="You don't have admin permissions to set a server macro with ->",
            )
        elif macro_attr in ("public", "protected") and prefix.startswith("+>"):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="user side macro with +> cannot be set to 'public' or 'protected",
            )
        elif ctx.guild is None and prefix.startswith("->"):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="You must be in a server to create a server macro with ->",
            )
        elif ctx.author is None:
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="Something went wrong, someone is trying to hack the bot",
            )
        else:
            executioner = await Macro().exemac(
                args,
                ctx.bot.database,
                ctx.guild.id,
                ctx.author.id,
                ctx.bot,
                prefix.startswith("->"),
            )
            if isinstance(executioner, tuple):
                embed = discord.Embed(
                    title="Macro creation failure ❌",
                    description=f"{executioner[0]}\nDraft:`{args}`\nIf you are having difficulty use the command `/macro docs` to read the tutorial",
                )
            else:
                stored = await ctx.bot.database.register_macro(
                    prefix=prefix,
                    args=args,
                    macro_type=(
                        "user"
                        if prefix.startswith("+>")
                        else "server" if prefix.startswith("->") else None
                    ),
                    macro_attr=macro_attr,
                    id=ctx.author.id if prefix.startswith("+>") else ctx.guild.id,
                )
                if stored == "ERROR":
                    embed = discord.Embed(
                        title="Macro creation failure ❌",
                        description="A macro with that prefix already exists, try with another prefix",
                    )
                elif stored == "SUCESS":
                    embed = discord.Embed(title="Macro creation sucess :white_check_mark:")
                else:
                    embed = discord.Embed(
                        title="Macro creation failure ❌", description="Something went wrong"
                    )

        await ctx.send(embed=embed)

    @_macro.command(
        name="edit_prefix",
        help="macro edit prefix",
        desription="Allows you to edit your macro prefix",
    )
    @app_commands.describe(
        old_prefix="Your macro actual prefix", new_prefix="Your macro new prefix"
    )
    async def _macro_edit_prefix(self, ctx, old_prefix: str, new_prefix: str):
        await ctx.defer(ephemeral=True)
        if (not old_prefix.startswith("+>") or not new_prefix.startswith("+>")) and (
            not old_prefix.startswith("->") or not new_prefix.startswith("->")
        ):
            embed = discord.Embed(
                title="Macro edition failure ❌", description="All macros starts with +> or with ->"
            )
        elif old_prefix.startswith("+>") != new_prefix.startswith("+>") and old_prefix.startswith(
            "->"
        ) != new_prefix.startswith("->"):
            embed = discord.Embed(
                title="Macro edition failure ❌",
                description="You cannot change a user macro to server macro or a server macro to user macro",
            )
        elif (
            (old_prefix.startswith("->") or new_prefix.startswith("->"))
            and ctx.guild is not None
            and not ctx.author.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="You don't have admin permissions to change a server macro prefix in this server",
            )
        else:
            result = await ctx.bot.database.update_macro(
                old_prefix=old_prefix, new_prefix=new_prefix, id=ctx.author.id
            )
            if result == "ERROR 1":
                result = await ctx.bot.database.update_macro(
                    old_prefix=old_prefix, new_prefix=new_prefix, id=ctx.guild.id
                )

            if result == "SUCESS":
                embed = discord.Embed(title="Macro edition sucess :white_check_mark:")
            elif result == "ERROR 1":
                embed = discord.Embed(
                    title="Macro edition failure ❌",
                    description=f"There is no macro named '{old_prefix}'",
                )
            else:
                embed = discord.Embed(
                    title="Macro edition failure ❌", description="Something went wrong"
                )

        await ctx.send(embed=embed)

    @_macro.command(
        name="edit_code",
        help="macro edit code",
        description="Allows you to edit the code of your macro",
    )
    @app_commands.describe(prefix="Your macro prefix", args="Your macro new code")
    async def _macro_edit_code(self, ctx, prefix: str, args: str):
        await ctx.defer(ephemeral=True)
        if not prefix.startswith("+>") and not prefix.startswith("->"):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="Your macro prefix shall start with +> or ->",
            )
        elif (
            prefix.startswith("->")
            and ctx.guild is not None
            and not ctx.author.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="You don't have admin permissions change a server macro code",
            )
        else:
            executioner = await Macro().exemac(
                args,
                ctx.bot.database,
                ctx.guild.id,
                ctx.author.id,
                ctx.bot,
                prefix.startswith("->"),
            )
            if isinstance(executioner, tuple):
                embed = discord.Embed(
                    title="Macro edition failure ❌",
                    description=f"{executioner[0]}\nDraft:`{args}`\nIf you are having difficulty use the command `/macro docs` to read the tutorial",
                )
            else:
                result = await ctx.bot.database.update_macro(
                    old_prefix=prefix, args=args, id=ctx.author.id
                )
                if result == "ERROR 1":
                    result = await ctx.bot.database.update_macro(
                        old_prefix=prefix, args=args, id=ctx.guild.id
                    )

                if result == "SUCESS":
                    embed = discord.Embed(title="Macro edition sucess :white_check_mark:")
                elif result == "ERROR 1":
                    embed = discord.Embed(
                        title="Macro edition failure",
                        description=f"There is no macro named '{prefix}'",
                    )
                else:
                    embed = discord.Embed(
                        title="Macro edition failure ❌", description="Something went wrong"
                    )

        await ctx.send(embed=embed)

    @_macro.command(
        name="edit_attribute",
        help="macro edit attribute",
        description="Allows you to edit the attribute of your server macro to public, private or protected",
    )
    @app_commands.describe(
        prefix="Your server macro prefix",
        attr="Your macro new attribute (private, public or protected)",
    )
    async def _macro_edit_attribute(self, ctx, prefix: str, attr: str):
        await ctx.defer(ephemeral=True)
        if not prefix.startswith("+>") and not prefix.startswith("->"):
            embed = discord.Embed(
                title="Macro edition failure ❌",
                description="All macros shall starts with +> or ->",
            )
        elif prefix.startswith("+>"):
            embed = discord.Embed(
                title="Macro edition failure ❌",
                description="User macros cannot have their attribute be changed",
            )
        elif attr not in ("public", "private", "protected"):
            await ctx.send(
                "Your macro attribute need to be or 'private' or 'public' or 'protected'"
            )
        elif not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="You don't have admin permissions to change the attribute of a server command",
            )
        else:
            result = await ctx.bot.database.update_macro(
                old_prefix=prefix, macro_attr=attr, id=ctx.guild.id
            )
            if result == "SUCESS":
                embed = discord.Embed(title="Macro edition sucess :white_check_mark:")
            elif result == "ERROR 1":
                embed = discord.Embed(
                    title="Macro edition failure ❌",
                    description=f"There is no macro named '{prefix}'",
                )
            elif result == "ERROR 3":
                embed = discord.Embed(
                    title="Macro edition failure ❌",
                    description="The macro is not a server macro to edit attribute",
                )
            else:
                embed = discord.Embed(
                    title="Macro edition failure ❌", description="Something went wrong"
                )
        await ctx.send(embed=embed)

    @_macro.command(
        name="show_command", help="macro show command", description="Shows your macro command"
    )
    @app_commands.describe(prefix="Your macro prefix")
    async def _macro_show_command(self, ctx, prefix):
        await ctx.defer(ephemeral=True)
        if not prefix.startswith("+>") and not prefix.startswith("->"):
            embed = discord.Embed(
                title="Macro show up failure ❌",
                description="All macros shall starts with +> or ->",
            )
        else:
            command = await self.client.database.quick_search_macro(
                prefix=prefix, id=ctx.author.id if prefix.startswith("+>") else ctx.guild.id
            )
            if command is None:
                embed = discord.Embed(
                    title="Macro show up failure ❌",
                    description=f"There is no macro with name {prefix}",
                )
            elif (
                command["attribute"] in ["private", "protected"]
                and not ctx.author.guild_permissions.administrator
                and prefix.startswith("->")
            ):
                embed = discord.Embed(
                    title="Macro show up failure ❌",
                    description="You don't have permission to see the commands from private or protected commands",
                )
            else:
                embed = discord.Embed(title="Macro command text", description=f"`{command['cmd']}`")
        await ctx.send(embed=embed)

    @_macro.command(
        name="delete",
        help="macro delete",
        description="Allows you to delete a macro using their prefix",
    )
    @app_commands.describe(prefix="Your macro prefix")
    async def _macro_delete(self, ctx, prefix):
        await ctx.defer(ephemeral=True)
        if not prefix.startswith("+>") and not prefix.startswith("->"):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="Your macro prefix shall start with +> or ->",
            )
        elif (
            prefix.startswith("->")
            and ctx.guild is not None
            and not ctx.author.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="Macro creation failure ❌",
                description="You don't have admin permissions to delete a server macro in this server",
            )
        else:
            result = await ctx.bot.database.delete_macro(prefix=prefix, id=ctx.author.id)
            if result == "ERROR":
                result = await ctx.bot.database.delete_macro(prefix=prefix, id=ctx.guild.id)

            if result == "ERROR":
                embed = discord.Embed(
                    title="Macro deletion failure ❌",
                    description="There is no macro with such name in the server or in your user",
                )

                await ctx.send(embed=embed)

            elif result == "SUCESS":
                embed = discord.Embed(title="Macro deletion sucess :white_check_mark:")

                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(
                    title="Macro deletion failure ❌", description="Something went wrong"
                )

                await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(MacroCog(client))
