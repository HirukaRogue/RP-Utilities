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
            self.db = self.dev_client["rpu_database"]
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
        if await self.db["prefixes"].find_one({"guild_id": guild_id}) is None:
            await self.db["prefixes"].insert_one({"guild_id": guild_id, "prefix": prefix})
        else:
            await self.db["prefixes"].update_one({"guild_id": guild_id, "prefix": prefix})

    # this function will delete the prefix of a guild, reseting it to the standard one
    async def remove_prefix(self, *, guild_id: int) -> None:
        document = await self.db["prefixes"].find_one({"guild_id": guild_id})

        if document is not None:
            await self.db["prefixes"].delete_one({"guild_id": guild_id})

    # this function will grab the prefix of the bot in a guild, if there is none the prefix will be the default one
    async def get_prefix(self, *, guild_id: int) -> str | None:
        document = await self.db["prefixes"].find_one({"guild_id": guild_id})

        if document is not None:
            return document["prefix"]
        else:
            return None

    ### BUFFERS ###
    # This section is to help the bot on performance

    ### ANONIMITY ###
    # This is for those who wants to turns their actions anoomynously

    # anonimity
    async def anonimity_check(self, user_id):
        checker = await self.db["anonimity"].find_one({"user_id": user_id})
        if checker is None:
            await self.db["anonimity"].insert_one({"user_id": user_id, "anonimity": False})
            checker = await self.db["anonimity"].find_one({"user_id": user_id})

        checker = checker["anonimity"]

        return checker

    # switch true or false anonymous mode
    async def switch_anonimous_mode(self, user_id):
        checker = await self.db["anonimity"].find_one({"user_id": user_id})

        switch = bool

        if checker is None:
            checker = await self.db["anonimity"].insert_one({"user_id": user_id, "anonimity": True})
        elif checker["anonimity"]:
            switch = False
        else:
            switch = True

        await self.db["anonimity"].update_one({"user_id": user_id}, {"$set": {"anonimity": switch}})

        return switch

    ### WEBHOOK LOG ###
    # to keep track which webhook belongs to the log serves well

    # this function serves as a webhook tracker each time a new message is made
    async def webhook_log_reg(self, *, user_id: int, message_id: int):
        database = await self.db["webhook_log"].find_one({"user_id": user_id})
        if database is None:
            await self.db["webhook_log"].insert_one({"user_id": user_id, "webhook_log": list()})
            database = await self.db["webhook_log"].find_one({"user_id": user_id})

        message_list = database["webhook_log"]

        message_list.append(message_id)
        if len(message_list) > 256:
            message_list.pop(0)

        await self.db["webhook_log"].update_one(
            {"user_id": user_id}, {"$set": {"webhook_log": message_list}}
        )

    async def webhook_log_confirm(self, *, user_id: int, message_id: int):
        database = await self.db["webhook_log"].find_one({"user_id": user_id})
        if database:
            message_list = database["webhook_log"]
        else:
            return False

        if message_id in message_list:
            return True
        else:
            return False

    ### DEFAULT CHARACTERS ###
    # This is the standard version of creating characters, when you don't use templates you use default

    # this is a quicker version of quick search for characters using their prompt_prefix
    async def quick_search_default_character(
        self, *, user_id: int, prompt_prefix: str
    ) -> None | dict:
        database = await self.db["characters"].find_one({"user_id": user_id})
        if database:
            char_list = database["characters"]
            if prompt_prefix in char_list:
                return char_list[prompt_prefix]
            else:
                return None
        else:
            return None

    # This function will search docs using user ID, character name and/or prompt_prefix
    async def search_default_character(
        self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None
    ) -> None | list:
        database = await self.db["characters"].find_one({"user_id": user_id})
        documents = list()
        if database:
            char_list = database["characters"]
            if name and prompt_prefix:
                for i in char_list.values():
                    if name in i["name"] and prompt_prefix in i["prompt_prefix"]:
                        documents.append(i)
            elif prompt_prefix:
                for i in char_list.values():
                    if prompt_prefix in i["prompt_prefix"]:
                        documents.append(i)
            elif name:
                for i in char_list.values():
                    if name in i["name"]:
                        documents.append(i)
            else:
                for i in char_list.values():
                    documents.append(i)

        return documents if len(documents) > 0 else None

    # this function will register the newly created character
    async def register_default_character(
        self, *, user_id: int, name: str, prompt_prefix: str, image: str | None = None
    ) -> None | str:
        data = {prompt_prefix: {"name": name, "prompt_prefix": prompt_prefix, "image_url": image}}

        database = await self.db["characters"].find_one({"user_id": user_id})
        if not database:
            await self.db["characters"].insert_one({"user_id": user_id, "characters": dict()})
            database = await self.db["characters"].find_one({"user_id": user_id})

        char_list = database["characters"]

        if prompt_prefix not in char_list:
            char_list = char_list | data

            await self.db["characters"].update_one(
                {"user_id": user_id}, {"$set": {"characters": char_list}}
            )
            return None
        else:
            return "ERROR"

    # this function will delete a character by name or prompt_prefix
    async def delete_default_character(
        self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None
    ) -> None | str | list:
        database = await self.db["characters"].find_one({"user_id": user_id})

        if database:
            char_list = database["characters"]

            char_sub_list = list()
            for i in char_list.values():
                if name and prompt_prefix:
                    if name in i["name"] or prompt_prefix in i["prompt_prefix"]:
                        char_sub_list.append(i)
                elif name:
                    if name in i["name"]:
                        char_sub_list.append(i)
                elif prompt_prefix:
                    if prompt_prefix in i["prompt_prefix"]:
                        char_sub_list.append(i)

            if len(char_sub_list) == 0:
                return "ERROR"
            else:
                if len(char_sub_list) == 1:
                    if name:
                        del char_list[char_sub_list[0]["prompt_prefix"]]
                    elif prompt_prefix:
                        del char_list[prompt_prefix]
                    await self.db["characters"].update_one(
                        {"user_id": user_id}, {"$set": {"characters": char_list}}
                    )
                    return "SUCESS"
                else:
                    return char_sub_list
        else:
            return "ERROR"

    # this function will update any stuffs related to the character
    async def update_default_character(
        self,
        *,
        user_id: int,
        old_name: str | None = None,
        old_prompt_prefix: str | None = None,
        new_name: str | None = None,
        new_prompt_prefix: str | None = None,
        new_image: str | None = None,
    ) -> None | str | list:
        database = await self.db["characters"].find_one({"user_id": user_id})

        if database:
            char_list = database["characters"]

            if old_prompt_prefix in char_list:
                if new_name:
                    char_list[old_prompt_prefix]["name"] = new_name
                    return "SUCESS"
                elif new_prompt_prefix:
                    new_data = {
                        new_prompt_prefix: {
                            "name": char_list[old_prompt_prefix]["name"],
                            "prompt_prefix": new_prompt_prefix,
                            "image_url": char_list[old_prompt_prefix]["image_url"],
                        }
                    }
                    del char_list[old_prompt_prefix]
                    char_list.update(new_data)
                    return "SUCESS"
                elif new_image:
                    char_list[old_prompt_prefix]["image_url"] = new_image
                    return "SUCESS"
            elif old_name:
                char_sub_list = list()
                for i in char_list.values():
                    if "name" in i:
                        if old_name in i["name"]:
                            char_sub_list.append(i)

                if len(char_sub_list) == 0:
                    return "ERROR"
                elif len(char_sub_list) > 1:
                    return char_sub_list
                else:
                    if new_name:
                        char_list[char_sub_list[0]["prompt_prefix"]]["name"] = new_name
                        await self.db["characters"].update_one(
                            {"user_id": user_id}, {"$set": {"characters": char_list}}
                        )
                        return "SUCESS"
                    elif new_prompt_prefix:
                        new_data = {
                            new_prompt_prefix: {
                                "name": char_list[char_sub_list[0]["prompt_prefix"]]["name"],
                                "prompt_prefix": new_prompt_prefix,
                                "image_url": char_list[char_sub_list[0]["prompt_prefix"]][
                                    "image_url"
                                ],
                            }
                        }
                        del char_list[old_prompt_prefix]
                        char_list.update(new_data)
                        await self.db["characters"].update_one(
                            {"user_id": user_id}, {"$set": {"characters": char_list}}
                        )
                        return "SUCESS"
                    elif new_image:
                        char_list[char_sub_list[0]["prompt_prefix"]]["image_url"] = new_image
                        await self.db["characters"].update_one(
                            {"user_id": user_id}, {"$set": {"characters": char_list}}
                        )
                        return "SUCESS"
        else:
            return "ERROR"

    ### MACROS ###
    # Macros are complicated, but yet useful for manage stuffs easier in RPGs and RPs

    # This function will search macros from the user and the server they are within
    async def search_macro(self, *, search: str | None = None, id: int) -> None | list:
        database = await self.db["macros"].find_one({"id": id})

        if not database:
            await self.db["macros"].insert_one({"id": id, "macros": dict()})
            database = await self.db["macros"].find_one({"id": id})

        macros = database["macros"]

        if search is None:
            return list(macros.values())

        results = list()

        for i in macros.values():
            if search in i["prefix"]:
                results.append(i)

        return results if len(results) > 0 else None

    # This is a quicker version of search macro
    async def quick_search_macro(self, *, prefix: str, id: int):
        database = await self.db["macros"].find_one({"id": id})

        if not database:
            await self.db["macros"].insert_one({"id": id, "macros": dict()})
            database = await self.db["macros"].find_one({"id": id})

        macros = database["macros"]

        if len(macros) == 0:
            return "ERROR"
        elif prefix not in macros:
            return "ERROR"
        else:
            return macros[prefix]

    # This function will register the Macros of server or bot users
    async def register_macro(
        self, *, prefix: str, args: str, macro_type: str, macro_attr: str, id: int
    ):
        macro_data = {
            prefix: {
                "prefix": prefix,
                "cmd": args,
                "type": macro_type,
                "attribute": macro_attr,
            }
        }

        database = await self.db["macros"].find_one({"id": id})

        if not database:
            await self.db["macros"].insert_one({"id": id, "macros": dict()})
            database = await self.db["macros"].find_one({"id": id})

        macros = database["macros"]

        if prefix in macros:
            return "ERROR"

        else:
            macros.update(macro_data)
            await self.db["macros"].update_one({"id": id}, {"$set": {"macros": macros}})
            return "SUCESS"

    # This function will update macros from database
    async def update_macro(
        self,
        *,
        old_prefix: str,
        new_prefix: str | None = None,
        args: str | None = None,
        macro_attr: str | None = None,
        id: int,
    ):
        database = await self.db["macros"].find_one({"id": id})

        if not database:
            await self.db["macros"].insert_one({"id": id, "macros": dict()})
            database = await self.db["macros"].find_one({"id": id})

        macros = database["macros"]

        if old_prefix in macros:
            if new_prefix:
                new_data = {
                    new_prefix: {
                        "prefix": new_prefix,
                        "cmd": macros[old_prefix]["cmd"],
                        "type": macros[old_prefix]["type"],
                        "attribute": macros[old_prefix]["attribute"],
                    }
                }
                del macros[old_prefix]
                macros.update(new_data)
            elif args:
                macros[old_prefix]["cmd"] = args
            elif macro_attr:
                if macros[old_prefix]["type"] == "server":
                    macros[old_prefix]["attribute"] = macro_attr
                else:
                    return "ERROR 3"
            else:
                return "ERROR 2"

            await self.db["macros"].update_one({"id": id}, {"$set": {"macros": macros}})
            return "SUCESS"
        else:
            return "ERROR 1"

    # This function will delete macros from database
    async def delete_macro(self, *, prefix: str, id: int):
        database = await self.db["macros"].find_one({"id": id})

        if not database:
            await self.db["macros"].insert_one({"id": id, "macros": dict()})
            database = await self.db["macros"].find_one({"id": id})

        macros = database["macros"]

        if prefix in macros:
            del macros[prefix]
            await self.db["macros"].update_one({"id": id}, {"$set": {"macros": macros}})
            return "SUCESS"
        else:
            return "ERROR"
