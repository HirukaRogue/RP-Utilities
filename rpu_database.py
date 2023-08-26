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

    ### BUFFERS ###
    # This section is to help the bot on performance

    # This is a buffer initiator and associator
    async def buffer(self, user_id):
        buffer = await self.db.buffer.find_one({'user_id':user_id})
        if buffer is None:
            await self.db.buffer.insert_one({
                'user_id': user_id,
                'buffer': list()
            })
            buffer = await self.db.buffer.find_one({'user_id':user_id})
        
        buffer = buffer['buffer']

        return buffer
    
    # this is a buff register
    async def buffer_reg(self, user_id, registry):
        buffer = await self.db.buffer.find_one({'user_id':user_id})
        if buffer is None:
            buffer = await self.db.buffer.insert_one({
                'user_id': user_id,
                'buffer': list()
            })

        buffer = buffer["buffer"]

        buffer.append(registry)
        if len(buffer) > 10:
            buffer['buffer'].pop(0)
        
        await self.db.buffer.update_one({
            'user_id': user_id
        }, {'$set': {'buffer': buffer}})

    ### ANONIMITY ###
    # This is for those who wants to turns their actions anoomynously

    #anonimity
    async def anonimity_check(self, user_id):
        checker = await self.db.anonimity.find_one({'user_id':user_id})
        if checker is None:
            await self.db.anonimity.insert_one({
                'user_id': user_id,
                'anonimity': False
            })
            checker = await self.db.anonimity.find_one({'user_id':user_id})
        
        checker = checker['anonimity']

        return checker
    
    #switch true or false anonymous mode
    async def switch_anonimous_mode(self, user_id):
        checker = await self.db.anonimity.find_one({'user_id':user_id})
        
        switch = bool

        if checker is None:
            checker = await self.db.anonimity.insert_one({
                'user_id': user_id,
                'anonimity': True
            })
        elif checker['anonimity']:
            switch = False
        else:
            switch = True

        await self.db.anonimity.update_one({
            'user_id': user_id
        }, {'$set': {'anonimity': switch}})

        return switch

    ### DEFAULT CHARACTERS ###
    # This is the standard version of creating characters, when you don't use templates you use default

    # This function will search docs using user ID, character name and/or prompt_prefix
    async def search_default_character(self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None) -> None:
        documents = list()
        init = True
        if name and prompt_prefix:
            cursor = self.db.characters.find({'user_id': user_id, 'name': {'$regex': name},'prompt_prefix': {'$regex': prompt_prefix}}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                data = cursor.next_object()
                documents.append(data)
        elif prompt_prefix:
            cursor = self.db.characters.find({'user_id': user_id, 'prompt_prefix': {'$regex': prompt_prefix}}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                data = cursor.next_object()
                documents.append(data)
        elif name:
            cursor = self.db.characters.find({'user_id': user_id, 'name': {'$regex': name}}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                data = cursor.next_object()
                documents.append(data)
        else:
            cursor = self.db.characters.find({'user_id': user_id}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                data = cursor.next_object()
                documents.append(data)
        
        return documents if len(documents) > 0 else None
    
    # Quicker version of search
    async def quick_search_default_character(self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None) -> None:
        documents = list()
        init = True
        if name and prompt_prefix:
            cursor = self.db.characters.find({'user_id': user_id, 'name': name,'prompt_prefix': prompt_prefix}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                data = cursor.next_object()
                documents.append(data)
        elif prompt_prefix:
            cursor = self.db.characters.find({'user_id': user_id, 'prompt_prefix': prompt_prefix}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                data = cursor.next_object()
                documents.append(data)
        elif name:
            cursor = self.db.characters.find({'user_id': user_id, 'name': name}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                data = cursor.next_object()
                documents.append(data)
        else:
            cursor = self.db.characters.find({'user_id': user_id}, no_cursor_timeout = True)
            while (await cursor.fetch_next):
                data = cursor.next_object()
                documents.append(data)

        return documents if len(documents) > 0 else None

    # this function will register the newly created character
    async def register_default_character(self, *, user_id: int, name: str, prompt_prefix: str, image: str | None = None) -> None:
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
    async def delete_default_character(self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None) -> None:
        documents = await self.search_default_character(user_id=user_id, name=name, prompt_prefix=prompt_prefix)

        if documents is None:
            return "ERROR"
        elif len(documents) == 1:
            if name:
                await self.db.characters.delete_one({'user_id': user_id, 'name': name})
            elif prompt_prefix:
                await self.db.characters.delete_one({'user_id': user_id, 'prompt_prefix': prompt_prefix})
            return "SUCESS"
        else:
            return documents

    # this function will update any stuffs related to the character
    async def update_default_character(self, *, user_id: int, old_name: str | None = None, old_prompt_prefix: str | None = None, new_name: str | None = None, new_prompt_prefix: str | None = None, new_image: str | None = None) -> None:
        documents = await self.quick_search_default_character(user_id=user_id, name=old_name, prompt_prefix=old_prompt_prefix)
        
        if documents is None:
            return "ERROR"
        elif len(documents) == 1:
            documents = documents[0]
            if new_name:
                await self.db.characters.update_one({
                    'user_id': user_id,
                    'prompt_prefix': documents['prompt_prefix'],
                    'image_url': documents['image_url']
                },{"$set": {'name': new_name}})
            elif new_prompt_prefix:
                await self.db.characters.update_one({
                    'user_id': user_id,
                    'name': documents['name'],
                    'image_url': documents['image_url']
                },{'$set': {'prompt_prefix': new_prompt_prefix}})
            elif new_image:
                await self.db.characters.update_one({
                    'user_id': user_id,
                    'name': documents['name'],
                    'prompt_prefix': documents['prompt_prefix']
                },{'$set': {'image_url': new_image}})
            return "SUCESS"
        else:
            return documents