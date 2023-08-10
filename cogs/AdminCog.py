from typing import Literal, Optional
import discord
from discord.ext import commands
from discord.ext.commands import Context
import os
import sys

class AdminCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin.py is ready")
    
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.command(
        aliases=["purge"], description="Bulk deletes messages from the channel."
    )
    async def clear(
        self,
        ctx: Context,
        amount: Optional[int | Literal["all"]],
        user: discord.User | None = None,
    ) -> None:
        if not (amount or user):
            await ctx.send_help(ctx.command)

        messages = await ctx.channel.purge(
            limit=amount + 1 if isinstance(amount, int) else None,
            check=lambda message: message.author == user if user else True,
        )
        message_count = len(messages) - 1 if ctx.message in messages else len(messages)
        await  ctx.send(f'Cleared {message_count} message{"s" if message_count != 1 else ""}.',
            allowed_mentions=discord.AllowedMentions.none(),
            delete_after=10,
        )

async def setup(client):
    await client.add_cog(AdminCog(client))