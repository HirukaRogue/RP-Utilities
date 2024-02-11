from typing import Mapping, Optional, List, Any

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Command


class Help(commands.HelpCommand):
    def __init__(self):
       attributes = {
           "name": "help",
           "cooldown": commands.CooldownMapping.from_cooldown(2, 5.0, commands.BucketType.user),
           "description": "This is a list of commands for RP Utilities"
        }
       super().__init__(command_attrs = attributes)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signature = [self.get_command_signature(c) for c in filtered]
            if command_signature:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signature), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    
    async def send_command_help(self, command):
        description = await self.set_description(command)
        embed = discord.Embed(title=self.get_command_signature(command), description=description)
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    async def set_description(self, command):
        match command.help:
            case "math":
                description = "Make basic operations, such as 2+2, you can create math expression to it solve for you. Useful for when you need to make complex calculation but you don't want to bother calculating it by yourself"
            case "roll":
                description = "Roll 1 or more dices of any sides like RPG dices, you can add modifiers, multiply, etc to gather results, (number)df allows you to roll fate dices, (number)dc allows you to flip coins without adding or reducing anything to your roll expression"
            case "select":
                description = "Select an option you offer by text, for example it selects one random option between apple, pineaple and pear, returning one of those options. with prefix you don't need to surround the options with (), so you can use regular "" to separate the options without having problem of the bot gather options in a way you don't want to. With slash you need to set the options by (), inserting it inside the parentesis"
            case "character":
                description = "Section of commands related to character creation, in this beta version you can only set default characters"
            case "character search":
                description = "Search your character by what you type, the searcher search by character name and character prefix/prompt"
            case "character default":
                description = "Section of commands related to default character creation"
            case "character default create":
                description = "Create a character to roleplay, you can optionally annex image or paste URL to set your character profile picture"
            case "character default delete":
                description = "Delete a character by name or by their prefix.\nNote: If you have two characters with the same name the bot will return both characters and their respective prefix/prompt"
            case "character default edit name":
                description = "Edit the name of your character by their actual name, if you have two or more characters with same name it will return a list of those characters with same name and request you change the name by their prefix/prompt"
            case "character default edit name by prompt":
                description = "Edit the name of your character by their prefix/prompt"
            case "character default edit prompt":
                description = "Edit the character prefix/prompt by their actual prompt"
            case "character default image":
                description = "Shows the profile picture of your character by their name, if you have two or more characters with same name, it will show a list of them"
            case "character default image set":
                description = "Change/set the profile picture of your character by their name, if you have two or more characters with same name, it will show a list of them and will request you change the profile picture by their prefix/prompt"
            case "character default image by prompt":
                description = "Shows the profile picture of your character by their prefix/prompt"
            case "character default image by prompt set":
                description = "Change/set the profile picture of your character by their prompt"

        return description

    async def send_error_message(self, error: str):
        embed = discord.Embed(title="Error", description=error)
        channel = self.get_destination()
        await channel.send(embed=embed)