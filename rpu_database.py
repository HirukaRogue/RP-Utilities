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
            self.db = self.dev_client['rpu_database_alpha']
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
        if await self.db['prefixes'].find_one({'guild_id':guild_id}) is None:
            await self.db['prefixes'].insert_one({
                'guild_id': guild_id,
                'prefix': prefix
            })
        else:
            await self.db['prefixes'].update_one({
                'guild_id': guild_id,
                'prefix': prefix
            })

    # this function will delete the prefix of a guild, reseting it to the standard one
    async def remove_prefix(self, *, guild_id: int) -> None:
        document = await self.db['prefixes'].find_one({'guild_id': guild_id})

        if document is not None:
            await self.db['prefixes'].delete_one({'guild_id': guild_id})

    # this function will grab the prefix of the bot in a guild, if there is none the prefix will be the default one
    async def get_prefix(self, *, guild_id: int) -> str | None:
        document = await self.db['prefixes'].find_one({'guild_id': guild_id})
        
        if document is not None:
            return document["prefix"]
        else:
            return None

    ### BUFFERS ###
    # This section is to help the bot on performance

    # This is a buffer initiator and associator
    async def buffer(self, user_id):
        buffer = await self.db['buffer'].find_one({'user_id': user_id})
        if buffer is None:
            await self.db['buffer'].insert_one({
                'user_id': user_id,
                'buffer': list()
            })
            buffer = await self.db['buffer'].find_one({'user_id': user_id})
        
        buffer = buffer['buffer']

        database = await self.db['characters'].find_one({'user_id': user_id})
        char_list = database['characters']
        char_buffer = list()
        if len(buffer) > 0:
            for i in buffer:
                char_buffer.append(char_list[i])

        return char_buffer
    
    # this is a buff register
    async def buffer_reg(self, user_id, registry):
        buffer = await self.db['buffer'].find_one({'user_id': user_id})
        if buffer is None:
            buffer = await self.db.buffer.insert_one({
                'user_id': user_id,
                'buffer': list()
            })

        buffer = buffer["buffer"]
        database = await self.db['characters'].find_one({'user_id': user_id})
        char_list = database['characters']
        for num, i in enumerate(char_list):
            if i == registry:
                buffer.append(num)
                if len(buffer) > 10:
                    buffer.pop(0)
                break

        await self.db['buffer'].update_one({
            'user_id': user_id
        }, {'$set': {'buffer': buffer}})

    ### ANONIMITY ###
    # This is for those who wants to turns their actions anoomynously

    #anonimity
    async def anonimity_check(self, user_id):
        checker = await self.db['anonimity'].find_one({'user_id':user_id})
        if checker is None:
            await self.db['anonimity'].insert_one({
                'user_id': user_id,
                'anonimity': False
            })
            checker = await self.db['anonimity'].find_one({'user_id':user_id})
        
        checker = checker['anonimity']

        return checker
    
    #switch true or false anonymous mode
    async def switch_anonimous_mode(self, user_id):
        checker = await self.db['anonimity'].find_one({'user_id':user_id})
        
        switch = bool

        if checker is None:
            checker = await self.db['anonimity'].insert_one({
                'user_id': user_id,
                'anonimity': True
            })
        elif checker['anonimity']:
            switch = False
        else:
            switch = True

        await self.db['anonimity'].update_one({
            'user_id': user_id
        }, {'$set': {'anonimity': switch}})

        return switch

    ### WEBHOOK LOG ###
    # to keep track which webhook belongs to the log serves well

    #this function serves as a webhook tracker each time a new message is made
    async def webhook_log_reg(self, *, user_id: int, message_id: int):
        database = await self.db['webhook_log'].find_one({'user_id': user_id})
        if database is None:
            await self.db['webhook_log'].insert_one({
                'user_id': user_id,
                'webhook_log': list()
            })
            database = await self.db['webhook_log'].find_one({'user_id': user_id})
        
        message_list = database['webhook_log']

        message_list.append(message_id)
        if len(message_list) > 256:
            message_list.pop(0)
        
        await self.db['webhook_log'].update_one({
            'user_id': user_id
        }, {'$set': {'webhook_log': message_list}})

    async def webhook_log_confirm(self, *, user_id: int, message_id: int):
        database = await self.db['webhook_log'].find_one({'user_id': user_id})
        if database:
            message_list = database['webhook_log']
        else:
            return False

        if message_id in message_list:
            return True
        else:
            return False

    ### DEFAULT CHARACTERS ###
    # This is the standard version of creating characters, when you don't use templates you use default

    # This function will search docs using user ID, character name and/or prompt_prefix
    async def search_default_character(self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None) -> None:
        database = await self.db['characters'].find_one({'user_id': user_id})
        documents = list()
        if database:
            char_list = database['characters']
            if name and prompt_prefix:
                for i in char_list:
                    if name in i['name'] and prompt_prefix in i['prompt_prefix']:
                        documents.append(i)
            elif prompt_prefix:
                for i in char_list:
                    if prompt_prefix in i['prompt_prefix']:
                        documents.append(i)
            elif name:
                for i in char_list:
                    if name in i['name']:
                        documents.append(i)
            else:
                for i in char_list:
                    documents.append(i)
        
        return documents if len(documents) > 0 else None

    # this function will register the newly created character
    async def register_default_character(self, *, user_id: int, name: str, prompt_prefix: str, image: str | None = None) -> None:
        data = {
            'name': name,
            'prompt_prefix': prompt_prefix,
            'image_url': image
        }

        database = await self.db['characters'].find_one({'user_id': user_id})
        if not database:
            await self.db['characters'].insert_one({'user_id': user_id,
                                                    'characters': list()
                                                    })
            database = await self.db['characters'].find_one({'user_id': user_id})

        char_list = database['characters']
        if len(char_list) > 0:
            for i in char_list:
                if i['prompt_prefix'] == data['prompt_prefix']:
                    return "ERROR"            

        char_list.append(data)

        await self.db['characters'].update_one({'user_id': user_id}, {'$set': {'characters': char_list}})
    
    # this function will delete a character by name or prompt_prefix
    async def delete_default_character(self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None) -> None:
        database = await self.db['characters'].find_one({'user_id': user_id})
        
        if database:
            char_list = database['characters']

            instances = list()

            for num, i in enumerate(char_list):
                if name in i['name'] or prompt_prefix in i['prompt_prefix']:
                    instances.append(num)

            if len(instances) == 0:
                return "ERROR"
            elif len(instances) == 1:
                char_list.pop(instances[0])
                await self.db['characters'].update_one({'user_id': user_id}, {'$set': {'characters': char_list}})
                return "SUCESS"
            else:
                documents = list()
                for i in instances:
                    documents.append(char_list[i])
                return documents
        else:
            return "ERROR"

    # this function will update any stuffs related to the character
    async def update_default_character(self, *, user_id: int, old_name: str | None = None, old_prompt_prefix: str | None = None, new_name: str | None = None, new_prompt_prefix: str | None = None, new_image: str | None = None) -> None:
        database = self.db['characters'].find_one({'user_id': user_id})
        
        if database:
            char_list = database['characters']

            instances = list()

            for num, i in enumerate(char_list):
                if old_name in i['name'] or old_prompt_prefix in i['prompt_prefix']:
                    instances.append(num)

            if len(instances) == 0:
                return "ERROR"
            elif len(instances) == 1:
                document = char_list[instances[0]]
                if new_name:
                    document = {
                        'name': new_name,
                        'prompt_prefix': document['prompt_prefix'],
                        'image_url': document['image_url']
                    }
                    char_list[instances[0]] = document
                elif new_prompt_prefix:
                    document = {
                        'name': document['name'],
                        'prompt_prefix': new_prompt_prefix,
                        'image_url': document['image_url']
                    }
                    char_list[instances[0]] = document
                elif new_image:
                    document = {
                        'name': document['name'],
                        'prompt_prefix': document['prompt_prefix'],
                        'image_url': new_image
                    }
                    char_list[instances[0]] = document
                await self.db['characters'].update_one({'user_id': user_id}, {'$set': {'characters': char_list}})
                return "SUCESS"
            else:
                documents = list()
                for i in instances:
                    documents.append(char_list[i])
                return documents
        else:
            return "ERROR"