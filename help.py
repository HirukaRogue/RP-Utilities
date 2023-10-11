import discord
from bot import bot

class Help:
    def __init__(self, guild: discord.Guild) -> None:
        self.prefix = bot.database.get_prefix(guild_id=guild.id)

    @property
    def roll(self):
        roll_help = f'''
/roll or {self.prefix}roll is a command where you use to make dice rolls, there are 3 types of dices:
- `d(face numbers_, standard`
- `df, or fate dices`
- `dc, coin flip dices`
to execute a dice roll you need to use the command and write the arguments.
example:
- `/roll 1d20+5`
you can also use # to start instances of rolling
example:
- `/roll 4#2d10+7`
'''
        return roll_help
    
    @property
    def math(self):
        math_help = f'''
math you can operate with making matematical operations to the bot, offering the problem and it solving the problem.
example:
- `/math (4+5)/3*5`
prefix version example:
- `{self.prefix}math (4+5)/3*5`
'''
        return math_help
    
    def select(self):
        select_help = f'''
select allows you to make a random selection from what you use as input
example:
- `{self.prefix}select bees tomato backpack`
so it randomly will output bess, tomato or backpack, if you use slash command don't forget to surround each input with ()
example:
- /select (bees) (tomato) (backpack)
'''
        return select_help
    
    @property
    def character(self):
        character_help = f'''
character related commands, use default if you are a starter.
available commands:
- `/character default`
- `/character search`
prefix available commands:
- `{self.prefix}character default`
- `{self.prefix}character search`
'''
        return character_help
    
    def char_search(self):
        character_search_help = f'''
with this command you search your characer, type nothing to output all your character list, or type something to search, typing full name will search the character full name, search prompt and you will search the character by prompt
'''
        return character_search_help

    def char_default(self):
        character_default_help = f'''
default characters creation. This is for when you don't plan to use templates or you are a newbie with this bot. Also this option is The first way of creating character in this beta version.
available commands:
- `/character default create`
- `/character default edit_name`
- `/character default edit_name_by_prompt`
- `/character default edit_prompt`
- `/character default image`
- `/character default image_set`
- `/character default image_by_prompt`
- `/character default image_set_by_prompt`
prefix available commands:
- `{self.prefix}character default create`
- `{self.prefix}character default edit_name`
- `{self.prefix}character default edit_name_by_prompt`
- `{self.prefix}character default edit_prompt`
- `{self.prefix}character default image`
- `{self.prefix}character default image_set`
- `{self.prefix}character default image_by_prompt`
- `{self.prefix}character default image_set_by_prompt`
'''
        return character_default_help
    
    @property
    def char_default_create(self):
        character_default_create_help = f'''
create your own character with this function
syntax:
`/character default create (your character name) (your character prompt)`
or
`/character default create (your character name) (your character prompt) (your character profile picture url)`
you can upload your character profile picture to define it as your character profile picture
prefix version:
`{self.prefix}character default create (your character name) (your character prompt)`
or
`{self.prefix}character default create (your character name) (your character prompt) (your character profile picture url)`
'''
        return character_default_create_help
    
    @property
    def char_default_edit_name(self):
        character_default_edit_name_help = f'''
edit the name of your character using their old name as parameter
syntax:
`/character default edit_name (your character old name) (your character new name)`
prefix version:
`{self.prefix}character default edit_name (your character old name) (your character new name)`
'''
        return character_default_edit_name_help
    
    def char_default_edit_name_by_prompt(self):
        character_default_edit_name_by_prompt_help = f'''
edit the name of your character using their prompt as parameter
syntax:
`/character default edit_name (your character prompt) (your character new name)`
prefix version:
`{self.prefix}character default edit_name (your character prompt) (your character new name)`
'''
        return character_default_edit_name_by_prompt_help
    
    def char_default_edit_prompt(self):
        character_default_edit_prompt_help = f'''
edit the prompt of your character
syntax:
`/character default edit_prompt (your character old promt) (your character new prompt)`
prefix version:
`{self.prefix}character default edit_prompt (your character old promt) (your character new prompt)`
'''
        return character_default_edit_prompt_help
    
    def char_default_delete(self):
        character_default_delete_help = f'''
delete your character
syntax:
`/character default delete (your delete arguments)`
prefix version:
`{self.prefix}character default delete (your delete arguments)`
your delete arguments can be your character name or prompt
'''
        return character_default_delete_help
    
    @property
    def char_default_image(self):
        character_default_image_help = f'''
show your character profile picture
syntax:
`/character default image (your character name)`
prefix version:
`{self.prefix}character default image (your character name)`
'''
        return character_default_image_help
    
    @property
    def char_default_image_set(self):
        character_default_image_set_help = f'''
set a new profile picture to your character by name
syntax:
`/character default image_set (your character name) (Anex)`
or
`/character default image_set (your character name) (Your character new profile picture URL)`
prefix version:
`{self.prefix}character default image_set (your character name) (Anex)`
or
`{self.prefix}character default image_set (your character name) (Your character new profile picture URL)`
'''
        return character_default_image_set_help
    
    @property
    def char_default_image_by_prompt(self):
        character_default_image_by_prompt_help = f'''
show your character profile picture by prompt
syntax:
`/character default image (your character prompt)`
prefix version:
`{self.prefix}character default image (your character prompt)`
'''
        return character_default_image_by_prompt_help
    
    @property
    def char_default_image_set_by_prompt(self):
        character_default_image_set_by_prompt_help = f'''
set a new profile picture to your character by prompt
syntax:
`/character default image_set (your character prompt) (Anex)`
or
`/character default image_set (your character prompt) (Your character new profile picture URL)`
prefix version:
`{self.prefix}character default image_set (your character prompt) (Anex)`
or
`{self.prefix}character default image_set (your character prompt) (Your character new profile picture URL)`
'''
        return character_default_image_set_by_prompt_help