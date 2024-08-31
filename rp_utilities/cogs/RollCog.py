import discord
from discord import app_commands
from discord.ext import commands
from ..miscellaneous import roll
import random


class RollCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Roll.py is ready")

    @commands.command(aliases=["r", "diceroll", "dice_roll", "dice"], help="roll")
    async def roll(self, ctx, args: str):
        await ctx.defer(ephemeral=True)
        if "#" in args:
            parts = args.split("#")

            if parts[0].isnumeric:
                num_str = roll(parts[1], "only_string", int(parts[0]))
            else:
                num_str = "Invalid Argument"

        else:
            num_str = roll(args, "only_string")
        embed = discord.Embed(title="🎲 Roll result", description=num_str)
        await ctx.send(embed=embed)

    @commands.command(aliases=["c", "coin"])
    async def coin_flip(self, ctx, instances: str | None = None):
        if instances is None:
            result = random.choice(["heads", "tails"])
            embed = discord.Embed(title="🪙 Coin Flip", description=result)
            await ctx.send(embed=embed)
            return

        if instances.isnumeric:
            max = int(instances)
            result = [random.choice(["heads", "tails"]) for _ in range(0, max)]
            embed = discord.Embed(title="🪙 Coin Flip", description=result)
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="🪙 Coin Flip", description="Invalid Input")
        await ctx.send(embed=embed)

    @app_commands.command(
        name="roll", description="roll 1 or more dices of any sides, can use DnD arguments"
    )
    @app_commands.describe(args="set the arguments of dice roll, like 1d20+5")
    async def roll_slash(self, interaction: discord.Interaction, args: str):
        await interaction.response.defer(thinking=True)
        if "#" in args:
            parts = args.split("#")

            if parts[0].isnumeric:
                num_str = roll(parts[1], "only_string", int(parts[0]))
            else:
                num_str = "Invalid Argument"

        else:
            num_str = roll(args, "only_string")
        embed = discord.Embed(title="🎲 Roll result", description=num_str)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="coin_flip", description="flip a number of coins or just 1 coin")
    @app_commands.describe(instances="number of coins to flip, ignore to flip just once")
    async def coin_flip_slash(self, interaction: discord.Interaction, instances: str | None = None):
        await interaction.response.defer(thinking=True)
        if instances is None:
            result = random.choice(["heads", "tails"])
            embed = discord.Embed(title="🪙 Coin Flip", description=result)
            await interaction.followup.send(embed=embed)
            return

        if instances.isnumeric:
            max = int(instances)
            result = [random.choice(["heads", "tails"]) for _ in range(0, max)]
            embed = discord.Embed(title="🪙 Coin Flip", description=result)
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(title="🪙 Coin Flip", description="Invalid Input")
        await interaction.followup.send(embed=embed)


async def setup(client):
    await client.add_cog(RollCog(client))
