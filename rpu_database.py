import motor
import asyncio
import pymongo
import motor.motor_asyncio

class Database:
    def __init__(self) -> None:
        self.dev_client: motor.motor_asyncio.AsyncIOMotorClient | None = None

    async def connect(self, connection_uri: str, /) -> None:
        self.dev_client = motor.motor_asyncio.AsyncIOMotorClient(connection_uri)
        if self.dev_client is not None:
            self.db = self.dev_client.rpu_database
            print("Database connected!")
        else:
            self.db = None
            print("Cannot connect to Database!")

    async def close(self) -> None:
        self.dev_client.close()


    ### PREFIXES ###
    # this section is for prefixes

    # this function will create a new prefix for a guild
    async def set_prefix(self, *, guild_id: int, prefix: str) -> None:
        if await self.db.prefixes.find_one({'guild_id':guild_id}) is None:
            await self.db.prefixes.insert_one({
                'guild_id': guild_id,
                'prefix': prefix
            })
        else:
            await self.db.prefixes.update_one({
                'guild_id': guild_id,
                'prefix': prefix
            })

    # this function will delete the prefix of a guild, reseting it to the standard one
    async def remove_prefix(self, *, guild_id: int) -> None:
        document = await self.db.prefixes.find_one({'guild_id': guild_id})

        if document is not None:
            await self.db.prefixes.delete_one({'guild_id': guild_id})

    # this function will grab the prefix of the bot in a guild, if there is none the prefix will be the default one
    async def get_prefix(self, *, guild_id: int) -> str | None:
        document = await self.db.prefixes.find_one({'guild_id': guild_id})
        
        if document is not None:
            return document["prefix"]
        else:
            return None



    ### DEFAULT CHARACTERS ###
    # This is the standard version of creating characters, when you don't use templates you use default

    # This function will search docs using user ID, character name and/or prompt_prefix
    async def search_default_character(self, *, user_id: int, name: str | None, prompt_prefix: str | None) -> None:
        documents = {}
        init = True
        if name:
            cursor = self.db.characters.find({'user_id': user_id, 'name': name}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                grid_out = cursor.next_object()
                data = await grid_out.read()
                if init:
                    documents = data
                    init = False
                else:
                    documents = documents | data
        elif prompt_prefix:
            cursor = self.db.characters.find({'user_id': user_id, 'prompt_prefix': prompt_prefix}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                grid_out = cursor.next_object()
                data = await grid_out.read()
                if init:
                    documents = data
                    init = False
                else:
                    documents = documents | data
        elif name and prompt_prefix:
            cursor = self.db.characters.find({'user_id': user_id, 'name': name,'prompt_prefix': prompt_prefix}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                grid_out = cursor.next_object()
                data = await grid_out.read()
                if init:
                    documents = data
                    init = False
                else:
                    documents = documents | data
        else:
            cursor = self.db.characters.find({'user_id': user_id}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                grid_out = cursor.next_object()
                data = await grid_out.read()
                if init:
                    documents = data
                    init = False
                else:
                    documents = documents | data
        
        return documents if documents else None

    # this function will register the newly created character
    async def register_default_character(self, *, user_id: int, name: str, prompt_prefix: str, image: str | None) -> None:
        data = {
            'user_id': user_id,
            'name': name,
            'prompt_prefix': prompt_prefix,
            'image_url': image
        }
        if await self.db.characters.find_one({'prompt_prefix': prompt_prefix}) is None:
            await self.db.characters.insert_one(data)
        else:
            return "ERROR"
    
    # this function will delete a character by name or prompt_prefix
    async def delete_default_character(self, *, user_id: int, name: str | None, prompt_prefix: str | None) -> None:
        documents = self.search_default_character(self, user_id, name, prompt_prefix)
        
        if len(documents) == 1:
            if name:
                await self.db.characters.delete_one({'user_id': user_id, 'name': name})
            elif prompt_prefix:
                await self.db.characters.delete_one({'user_id': user_id, 'prompt_prefix': prompt_prefix})
        elif documents:
            return documents
        else:
            return "ERROR"

    # this function will update any stuffs related to the character
    async def update_default_character(self, *, user_id: int, old_name: str | None, old_prompt_prefix: str | None, new_name: str | None, new_prompt_prefix, new_image: str | None) -> None:
        documents = self.search_default_character(self, user_id, old_name, old_prompt_prefix)
        
        if len(documents) == 1:
            if new_name:
                await self.db.characters.update_one({
                    'user_id': user_id,
                    'name': new_name,
                    'prompt_prefix': documents['prompt_prefix'],
                    'image_url': documents['image_url']
                })
            elif new_prompt_prefix:
                await self.db.characters.update_one({
                    'user_id': user_id,
                    'name': documents['name'],
                    'prompt_prefix': new_prompt_prefix,
                    'image_url': documents['image_url']
                })
            elif new_image:
                await self.db.characters.update_one({
                    'user_id': user_id,
                    'name': documents['name'],
                    'prompt_prefix': documents['prompt_prefix'],
                    'image_url': new_image
                })
        elif documents:
            return documents
        else:
            return "ERROR"