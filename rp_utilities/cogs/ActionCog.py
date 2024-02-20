import discord
from discord.ext import commands
from discord import Intents
from functools import lru_cache


class ActionCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Action.py is ready")

    @commands.command(aliases=["interact", "action", "act", "roleplay"])
    async def rp(self, ctx):
        await ctx.send(
            "To interact type your character propt and them type a message, it will respond with a webhook and the message will be presented in an embed"
        )

    @commands.hybrid_group(
        name="annonymous_mode",
        fallback="help",
        aliases=[
            "annonymode",
        ],
    )
    async def _annonymous_mode(self, ctx):
        await ctx.send(
            "Anonymous mode makes your tupper messages being anonymous, type the command with switch to switch your anonymous mode"
        )

    @_annonymous_mode.command(
        name="switch",
    )
    async def _annonymous_mode_switch(self, ctx):
        anonimity = await ctx.bot.database.switch_anonimous_mode(ctx.author.id)

        if anonimity:
            embed = discord.Embed(description="You are now in Anonymous Mode")
        else:
            embed = discord.Embed(description="You are not in Anonymous Mode now")

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user or message.webhook_id:
            return

        message_instance = await self.message_instances(message.author.id, message.content)

        if message.reference:
            if message.reference.resolved.webhook_id:
                if message.content.startswith("=>switch->"):
                    prompt = message.content.replace("=>switch->", "")
                    parse = message.reference.resolved.embeds

                    respose = message.reference.resolved.content

                    author = (
                        f"<@{message.author.id}>"
                        if not await self.client.database.anonimity_check(message.author.id)
                        else "Anonymous"
                    )

                    webhooks = await message.channel.webhooks()
                    webhook = discord.utils.find(
                        lambda webhook: webhook.token is not None, webhooks
                    )
                    if webhook is None:
                        webhook = await message.channel.create_webhook(name="Characters Webhook")

                    await message.channel.purge(limit=1)

                    prompt_instance = await self.client.database.quick_search_default_character(
                        user_id=message.author.id, prompt_prefix=prompt
                    )

                    if prompt_instance:
                        prompt_instance = prompt_instance[0]

                        if webhook is list:
                            webhook = webhook[0]

                        embed = parse[0]

                        webhook_message = await webhook.send(
                            wait=True,
                            username=prompt_instance["name"],
                            avatar_url=prompt_instance["image_url"],
                            content=respose,
                            embed=embed,
                        )

                        await webhook.delete_message(message.reference.message_id)
                        await self.client.database.webhook_log_reg(
                            user_id=message.author.id, message_id=webhook_message.id
                        )

                elif message.content.startswith("=>edit->"):
                    belongs_to = await self.client.database.webhook_log_confirm(
                        user_id=message.author.id, message_id=message.reference.message_id
                    )
                    await message.channel.purge(limit=1)
                    if belongs_to:
                        edition_message = message.content.replace("=>edit->", "")
                        embed = discord.Embed(description=edition_message)
                        webhooks = await message.channel.webhooks()
                        webhook = discord.utils.find(
                            lambda webhook: webhook.token is not None, webhooks
                        )

                        await webhook.edit_message(message.reference.message_id, embed=embed)

        if message_instance is not None:
            author = (
                f"<@{message.author.id}>"
                if not await self.client.database.anonimity_check(message.author.id)
                else "Anonymous"
            )
            webhooks = await message.channel.webhooks()
            webhook = discord.utils.find(lambda webhook: webhook.token is not None, webhooks)
            if webhook is None:
                webhook = await message.channel.create_webhook(name="Characters Webhook")

            await message.channel.purge(limit=1)

            respose = ""
            if message.reference:
                print("entered")
                ref = (
                    message.reference
                    if isinstance(message.reference.resolved, discord.Message)
                    else None
                )
                if ref:
                    parse = ref.resolved.content[:25]
                    parse = parse + "..."
                    respose = f"response to <@{ref.resolved.author.id}>:\n> {parse}\n[jump]({ref.jump_url} 'Click to go to the message')\n"

            for i in message_instance:
                prompt_instance = await self.client.database.quick_search_default_character(
                    user_id=message.author.id, prompt_prefix=i[0]
                )

                if webhook is list:
                    webhook = webhook[0]

                embed = discord.Embed(description=i[1])

                webhook_message = await webhook.send(
                    wait=True,
                    username=prompt_instance["name"],
                    avatar_url=prompt_instance["image_url"],
                    content=f"{respose}character of {author}",
                    embed=embed,
                )
                await self.client.database.webhook_log_reg(
                    user_id=message.author.id, message_id=webhook_message.id
                )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if (
            await self.client.database.webhook_log_confirm(
                user_id=reaction.member.id, message_id=reaction.message_id
            )
            and reaction.emoji.name == "❌"
        ):
            channel = self.client.get_channel(reaction.channel_id)
            webhooks = await channel.webhooks()
            webhook = discord.utils.find(lambda webhook: webhook.token is not None, webhooks)
            if webhook:
                await webhook.delete_message(reaction.message_id)

    async def message_instances(self, user_id, message_disc):
        instances = message_disc.split(":", 1)
        prefix = instances[0]
        prefix = prefix + ":"
        instances[0] = prefix
        instances = [instances]

        if len(instances[0]) > 1:
            if len(instances[0][0]) < 18:
                second_message = instances[0][1].split("\n", 1)

                checker = instances[0][1].split(":", 1)

                is_second_message = True if len(checker[0]) < 17 and len(checker) > 1 else False

                char = await self.client.database.quick_search_default_character(
                    user_id=user_id, prompt_prefix=prefix
                )
                if char:
                    instances[0][0] = prefix
                    if is_second_message:
                        instances[0].pop(1)
                        instances[0].append(second_message[0])
                        instances.append(self.message_instances(user_id, second_message))
                    return instances
        return None


async def setup(client):
    await client.add_cog(ActionCog(client))
