roll_help = '''
roll or (prefix)roll is a command where you use to make dice rolls, there are 3 types of dices:
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

math_help = '''
math you can operate with making matematical operations to the bot, offering the problem and it solving the problem.
example:
- `/math (4+5)/3*5`
'''

select_help = '''
select allows you to make a random selection from what you use as input
example:
- `(prefix)select bees tomato backpack`
so it randomly will output bess, tomato or backpack, if you use slash command don't forget to surround each input with ()
example:
- /select (bees) (tomato) (backpack)
'''

character_help = '''
character related commands, use default if you are a starter.
available commands:
- `/character default`
- `/character search`
'''

character_search_help = '''
with this command you search your characer, type nothing to output all your character list, or type something to search, typing full name will search the character full name, search prompt and you will search the character by prompt
'''

character_default_help = '''
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
'''

character_default_create_help = '''
create your own character with this function
syntax:
`/character default create (your character name) (your character prompt)`
or
`/character default create (your character name) (your character prompt) (your character profile picture url)`
you can upload your character profile picture to define it as your character profile picture
'''

character_default_edit_name_help = '''
edit the name of your character using their old name as parameter
syntax:
`/character default edit_name (your character old name) (your character new name)`
'''

class Help:
    async def roll():
        return roll_help
    
    async def math():
        return math_help
    
    async def select():
        return select_help
    
    async def character():
        return character_help
    
    async def char_search():
        return character_search_help

    async def char_default():
        return character_default_help
    
    async def char_default_create():
        return character_default_create_help
    
    async def char_default_edit_name():
        return character_default_edit_name_help