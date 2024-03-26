import discord
from discord.ext import commands
from discord import app_commands


class ProfileCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("MathCog.py is ready")

    @commands.command()
    async def profile(self, ctx):
        embed = discord.Embed(title="Roleplay Utilities", description="A roleplay super tool bot")
        embed.add_field(
            name="Invite me",
            value="[Invite Link](https://discord.com/api/oauth2/authorize?client_id=1145338391530049596&permissions=2684430336&scope=bot 'Click to invite')",
        )
        embed.add_field(
            name="Support Server",
            value="[Server Link](https://discord.gg/qxYurDaAeA 'Click to enter')",
        )
        embed.add_field(
            name="Support the Bot", value="[Donate](https://patreon.com/user?u=99116894)"
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="profile", description="Shows the profile of the bot")
    async def profile_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Roleplay Utilities", description="A roleplay super tool bot")
        embed.add_field(
            name="Invite me",
            value="[Invite Link](https://discord.com/api/oauth2/authorize?client_id=1145338391530049596&permissions=2684430336&scope=bot 'Click to invite')",
        )
        embed.add_field(
            name="Support Server",
            value="[Server Link](https://discord.gg/qxYurDaAeA 'Click to enter')",
        )
        embed.add_field(
            name="Support the Bot", value="[Donate](https://patreon.com/user?u=99116894)"
        )
        await interaction.response.send_message(embed=embed)


async def setup(client):
    await client.add_cog(ProfileCog(client))
