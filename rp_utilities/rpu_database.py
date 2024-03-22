import aiosqlite

PREFIX_TABLE = """
CREATE TABLE IF NOT EXISTS prefixes (
    guild_id INT,
    prefix TEXT
    )
"""

ANONIMITY_TABLE = """
CREATE TABLE IF NOT EXISTS anonimity (
    user_id INT,
    anonymous INT
    )
"""

WEBHOOK_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS webhook_logs (
    user_id INT,
    message_id INT
    )
"""

DEFAULT_CHARACTER_TABLE = """
CREATE TABLE IF NOT EXISTS default_characters (
    id INT PRIMARY KEY,
    user_id INT,
    char_name TEXT,
    prompt TEXT,
    profile_pic TEXT
    )
"""

MACRO_TABLE = """
CREATE TABLE IF NOT EXISTS macros (
    id INT PRIMARY KEY,
    belong_id INT,
    macro_prefix TEXT,
    command TEXT,
    type TEXT,
    attribute TEXT
    )
"""


class Database:
    async def connect(self):
        self.db = await aiosqlite.connect("rpu.db")

        await self.db.execute(PREFIX_TABLE)
        await self.db.execute(ANONIMITY_TABLE)
        await self.db.execute(WEBHOOK_LOG_TABLE)
        await self.db.execute(DEFAULT_CHARACTER_TABLE)
        await self.db.execute(MACRO_TABLE)
        await self.db.commit()

        print("Database connected!")

    async def close(self):
        await self.db.close()

    ### PREFIXES ###
    # this section is for prefixes

    # this function will create a new prefix for a guild
    async def set_prefix(self, *, guild_id: int, prefix: str) -> None:
        cursor = await self.db.execute("SELECT * FROM prefixes WHERE guild_id = ?", (guild_id,))

        result = await cursor.fetchone()

        if result is None:
            await self.db.execute(
                "INSERT INTO prefixes (guild_id, prefix) VALUES (?, ?)", (guild_id, prefix)
            )
            await self.db.commit()

        else:
            await self.db.execute(
                "UPDATE prefixes SET prefix = ? WHERE guild_id = ?", (prefix, guild_id)
            )
            await self.db.commit()

    # this function will delete the prefix of a guild, reseting it to the standard one
    async def remove_prefix(self, *, guild_id: int) -> None:
        result = await self.db.execute_fetchall(
            "SELECT * FROM prefixes WHERE guild_id = ?", (guild_id,)
        )

        if result is not None:
            await self.db.execute("DELETE FROM prefixes WHERE guild_id = ?", (guild_id,))
            await self.db.commit()

    # this function will grab the prefix of the bot in a guild, if there is none the prefix will be the default one
    async def get_prefix(self, *, guild_id: int) -> str | None:
        cursor = await self.db.execute(
            "SELECT prefix FROM prefixes WHERE guild_id = ?", (guild_id,)
        )

        result = await cursor.fetchone()

        if result is not None:
            return result["prefix"]
        else:
            return None

    ### BUFFERS ###
    # This section is to help the bot on performance

    ### ANONIMITY ###
    # This is for those who wants to turns their actions anoomynously

    # anonimity
    async def anonimity_check(self, user_id):
        cursor = await self.db.execute(
            "SELECT anonymous FROM anonimity WHERE user_id = ?", (user_id,)
        )

        result = await cursor.fetchone()

        if result is None or result["anonymous"] == 0:
            return False
        else:
            return True

    # switch true or false anonymous mode
    async def switch_anonimous_mode(self, user_id):
        cursor = await self.db.execute(
            "SELECT anonymous FROM anonimity WHERE user_id = ?", (user_id,)
        )

        result = await cursor.fetchone()

        if result is None:
            await self.db.execute(
                "INSERT INTO anonimity (user_id, anonymous) VALUES (?, ?)", (user_id, True)
            )
            await self.db.commit()

            return True

        elif result["anonymous"] == 1:
            await self.db.execute(
                "UPDATE anonimity SET anonymous = ? WHERE user_id = ?", (False, user_id)
            )
            await self.db.commit()

            return False

        else:
            await self.db.execute(
                "UPDATE anonimity SET anonymous = ? WHERE user_id = ?", (True, user_id)
            )
            await self.db.commit()

            return True

    ### WEBHOOK LOG ###
    # to keep track which webhook belongs to the log serves well

    # this function serves as a webhook tracker each time a new message is made
    async def webhook_log_reg(self, *, user_id: int, message_id: int):
        await self.db.execute(
            "INSERT INTO webhook_logs (user_id, message_id) VALUES (?, ?)", (user_id, message_id)
        )
        await self.db.commit()

    async def webhook_log_confirm(self, *, user_id: int, message_id: int):
        cursor = await self.db.execute(
            "SELECT * FROM webhook_logs WHERE user_id = ? and message_id = ?", (user_id, message_id)
        )

        result = await cursor.fetchone()

        if result is None:
            return False
        else:
            return True

    ### DEFAULT CHARACTERS ###
    # This is the standard version of creating characters, when you don't use templates you use default

    # this is a quicker version of quick search for characters using their prompt_prefix
    async def quick_search_default_character(
        self, *, user_id: int, prompt_prefix: str
    ) -> None | dict:
        cursor = await self.db.execute(
            "SELECT * FROM default_characters WHERE user_id = ? and prompt = ?",
            (user_id, prompt_prefix),
        )

        result = await cursor.fetchone()

        if result:
            data = {
                "name": result[2],
                "prompt_prefix": result[3],
                "image_url": result[4],
            }
            return data
        else:
            return None

    # This function will search docs using user ID, character name and/or prompt_prefix
    async def search_default_character(
        self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None
    ) -> None | list:
        if name or prompt_prefix:
            cursor = await self.db.execute_fetchall(
                r"SELECT * FROM default_characters WHERE user_id = ? and (prompt like %?% or char_name like %?%)",
                (user_id, prompt_prefix, name),
            )

            result = list({"name": i[2], "prompt_prefix": i[3], "image_url": i[4]} for i in cursor)

            if len(result) > 0:
                return result
            else:
                return None

        else:
            cursor = await self.db.execute_fetchall(
                "SELECT * FROM default_characters WHERE user_id = ?",
                (user_id,),
            )

            result = list({"name": i[2], "prompt_prefix": i[3], "image_url": i[4]} for i in cursor)

            if len(result) > 0:
                return result
            else:
                return None

    # this function will register the newly created character
    async def register_default_character(
        self, *, user_id: int, name: str, prompt_prefix: str, image: str | None = None
    ) -> None | str:
        cursor = await self.db.execute_fetchall(
            "SELECT * FROM default_characters WHERE user_id = ? and prompt = ?",
            (user_id, prompt_prefix),
        )

        result = list({"name": i[2], "prompt_prefix": i[3], "image_url": i[4]} for i in cursor)

        if len(result) == 0:
            await self.db.execute(
                "INSERT INTO default_characters (user_id, char_name, prompt, profile_pic) VALUES (?, ?, ?, ?)",
                (user_id, name, prompt_prefix, image),
            )

            await self.db.commit()

            return None

        else:
            return "ERROR"

    # this function will delete a character by name or prompt_prefix
    async def delete_default_character(
        self, *, user_id: int, name: str | None = None, prompt_prefix: str | None = None
    ) -> None | str | list:
        cursor = await self.db.execute_fetchall(
            "SELECT * FROM default_characters WHERE user_id = ? and (prompt = ? or char_name = ?)",
            (user_id, prompt_prefix, name),
        )

        result = list({"name": i[2], "prompt_prefix": i[3], "image_url": i[4]} for i in cursor)

        if len(result) > 0:
            if len(result) == 1:
                if name:
                    await self.db.execute(
                        "DELETE FROM default_characters WHERE user_id = ? and char_name = ?",
                        (user_id, name),
                    )
                    await self.db.commit()

                    return "SUCESS"
                elif prompt_prefix:
                    await self.db.execute(
                        "DELETE FROM default_characters WHERE user_id = ? and prompt = ?",
                        (user_id, prompt_prefix),
                    )
                    await self.db.commit()

                    return "SUCESS"
            else:
                return result

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
        cursor = await self.db.execute_fetchall(
            "SELECT * FROM default_characters WHERE user_id = ? and (prompt = ? or char_name = ?)",
            (user_id, old_prompt_prefix, old_name),
        )

        result = list({"name": i[2], "prompt_prefix": i[3], "image_url": i[4]} for i in cursor)

        if len(result) > 0:
            if len(result) == 1:
                if new_name:
                    await self.db.execute(
                        "UPDATE default_characters SET char_name = ? WHERE user_id = ? and (char_name = ? or prompt = ?)",
                        (new_name, user_id, old_name, old_prompt_prefix),
                    )
                    await self.db.commit()

                    return "SUCESS"
                elif new_prompt_prefix:
                    await self.db.execute(
                        "UPDATE default_characters SET prompt = ? WHERE user_id = ? and (char_name = ? or prompt = ?)",
                        (new_prompt_prefix, user_id, old_name, old_prompt_prefix),
                    )
                    await self.db.commit()

                    return "SUCESS"
                elif new_image:
                    await self.db.execute(
                        "UPDATE default_characters SET profile_pic = ? WHERE user_id = ? and (char_name = ? or prompt = ?)",
                        (new_image, user_id, old_name, old_prompt_prefix),
                    )
                    await self.db.commit()

                    return "SUCESS"
            else:
                return result

        else:
            return "ERROR"

    ### MACROS ###
    # Macros are complicated, but yet useful for manage stuffs easier in RPGs and RPs

    # This function will search macros from the user and the server they are within
    async def search_macro(self, *, search: str | None = None, id: int) -> None | list:
        if search:
            cursor = await self.db.execute_fetchall(
                r"SELECT * FROM macros WHERE belong_id = ? and macro_prefix LIKE %?%",
                (id, search),
            )
        else:
            cursor = await self.db.execute_fetchall(
                r"SELECT * FROM macros WHERE belong_id = ?",
                (id,),
            )

        result = list(
            {
                "prefix": i[2],
                "cmd": i[3],
                "type": i[4],
                "attribute": i[5],
            }
            for i in cursor
        )

        if len(result) > 0:
            return result

        else:
            return None

    # This is a quicker version of search macro
    async def quick_search_macro(self, *, prefix: str, id: int):
        cursor = await self.db.execute(
            "SELECT * FROM macros WHERE belong_id = ? and macro_prefix = ?",
            (id, prefix),
        )

        result = await cursor.fetchone()

        if result:
            data = {
                "prefix": result[2],
                "cmd": result[3],
                "type": result[4],
                "attribute": result[5],
            }
            return data
        else:
            return None

    # This function will register the Macros of server or bot users
    async def register_macro(
        self, *, prefix: str, args: str, macro_type: str, macro_attr: str, id: int
    ):
        cursor = await self.db.execute_fetchall(
            "SELECT * FROM macros WHERE belong_id = ? and macro_prefix = ? and command = ? and type = ?",
            (id, prefix, args, macro_type),
        )

        result = list(
            {
                "prefix": i[2],
                "cmd": i[3],
                "type": i[4],
                "attribute": i[5],
            }
            for i in cursor
        )

        if len(result) == 0:
            await self.db.execute(
                "INSERT INTO macros (belong_id, macro_prefix, command, type, attribute) VALUES (?, ?, ?, ?, ?)",
                (id, prefix, args, macro_type, macro_attr),
            )
            await self.db.commit()

            return "SUCESS"
        else:
            return "ERROR"

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
        cursor = await self.db.execute_fetchall(
            "SELECT * FROM macros WHERE belong_id = ? and macro_prefix = ?",
            (id, old_prefix),
        )

        result = list(
            {
                "prefix": i[2],
                "cmd": i[3],
                "type": i[4],
                "attribute": i[5],
            }
            for i in cursor
        )

        if len(result[0]) > 0:
            if len(result) == 1:
                if new_prefix:
                    await self.db.execute(
                        "UPDATE macros SET macro_prefix = ? WHERE belong_id = ?", (new_prefix, id)
                    )
                    await self.db.commit()

                    return "SUCESS"

                elif args:
                    await self.db.execute(
                        "UPDATE macros SET command = ? WHERE belong_id = ?", (args, id)
                    )
                    await self.db.commit()

                    return "SUCESS"

                elif macro_attr:
                    if result[0]["type"] == "server":
                        await self.db.execute(
                            "UPDATE macros SET attribute = ? WHERE belong_id = ?", (macro_attr, id)
                        )
                        await self.db.commit()

                        return "SUCESS"

                    else:
                        return "ERROR 3"

                else:
                    "ERROR 2"

        else:
            return "ERROR 1"

    # This function will delete macros from database
    async def delete_macro(self, *, prefix: str, id: int):
        cursor = await self.db.execute(
            "SELECT * FROM macros WHERE belong_id = ? and macro_prefix = ?",
            (id, prefix),
        )

        result = cursor.fetchone()

        if result is not None:
            await self.db.execute(
                "DELETE FROM macros WHERE belong_id = ? and macro_prefix = ?", (id, prefix)
            )
            await self.db.commit()

            return "SUCESS"

        else:
            return "ERROR"
