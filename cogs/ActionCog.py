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

    @commands.command(aliases = ['interact', 'action', 'act', 'roleplay'])
    async def rp(self, ctx):
        await ctx.send("To interact type your character propt and them type a message, it will respond with a webhook and the message will be presented in an embed")

    @commands.hybrid_group(name="annonymous_mode", fallback="help", aliases=["annonymode",])
    async def _annonymous_mode(self, ctx):
        await ctx.send("Anonymous mode makes your tupper messages being anonymous, type the command with switch to switch your anonymous mode")
    
    @_annonymous_mode.command(name="switch",)
    async def _annonymous_mode_switch(self, ctx):
        anonimity = await ctx.bot.database.switch_anonimous_mode(ctx.author.id)

        if anonimity:
            await ctx.send("You are now in Anonymous Mode")
        else:
            await ctx.send("You aren't in Anonymous Mode now")

    @commands.Cog.listener()
    async def on_message(self, message: Intents.message_content):
        if message.author == self.client.user:
            return

        buffer = await self.client.database.buffer(message.author.id)

        message_instance = await self.message_instances(message.author.id, message.content, buffer)

        if message_instance is not None:
            author = f"<@{message.author.id}>" if not await self.client.database.anonimity_check(message.author.id) else "Anonymous"
            webhook = await message.channel.webhooks()
            if len(webhook) == 0:
                await message.channel.create_webhook(name="Characters Webhook")
            else:
                webhook = webhook[0]

            for i in message_instance:
                in_db = True
                for j in buffer:
                    if i[0] in j["prompt_prefix"]:
                        embed = discord.Embed(
                            description=i[1]
                        )

                        await webhook.send(username=j["name"], avatar_url=j["image_url"], content=f"character of {author}", embed=embed) 
                        in_db = False
                        break
                
                if in_db:
                    prompt_instance = await self.client.database.quick_search_default_character(user_id=message.author.id, prompt_prefix=i[0])
                    prompt_instance = prompt_instance[0]

                    if webhook is list:
                        webhook = webhook[0]
                    
                    embed = discord.Embed(
                            description=i[1]
                    )

                    await webhook.send(username=prompt_instance["name"], avatar_url=prompt_instance["image_url"], content=f"character of {author}", embed=embed)   

    async def message_instances(self, user_id, message_disc, buffer):
        instances = message_disc.split(':', 1)
        prefix = instances[0]
        prefix = prefix+':'
        instances[0] = prefix
        instances = [instances]

        if len(instances[0]) > 1:
            if len(instances[0][0]) < 18:
                second_message = instances[0][1].split('\n', 1)

                checker = instances[0][1].split(':', 1)

                is_second_message = True if len(checker[0]) < 17 and len(checker) > 1 else False

                for i in buffer:
                    if instances[0][0] in i["prompt_prefix"]:
                        if is_second_message:
                            instances[0].pop(1)
                            instances[0].append(second_message[0])
                            instances.append(self.message_instances(user_id, second_message, buffer))
                        return instances
                
                prompt = await self.client.database.quick_search_default_character(user_id=user_id, prompt_prefix=instances[0][0])
                if prompt:
                    prompt = prompt[0]
                    await self.client.database.buffer_reg(user_id, prompt)
                    if is_second_message:
                        instances[0].pop(1)
                        instances[0].append(second_message[0])
                        instances.append(self.message_instances(user_id, second_message, buffer))
                    return instances
        return None

async def setup(client):
    await client.add_cog(ActionCog(client))