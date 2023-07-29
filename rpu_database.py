import motor

CREATE_PREFIXES_TABLE = """\
CREATE TABLE IF NOT EXISTS prefixes (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    prefix TEXT
)
"""
CREATE_DEFAULT_CHARACTERS_TABLE = """
CREATE TABLE IF NOT EXIST default_characters (
    id SERIAL PRIMARY KEY,
    user_id
    char_name
    char_prefix
)
"""

#CREATE_TEMPLATES_TABLE = """\
#CREATE TABLE IF NOT EXISTS templates (
#    id SERIAL PRIMARY KEY,
#    guild_id BIGINT,
#    user_id BIGINT,
#    template_name TEXT,
#    data JSONB
#)
#"""
#CREATE_CHARACTERS_TABLE = """\
#CREATE TABLE IF NOT EXISTS characters (
#    id SERIAL PRIMARY KEY,
#    user_id BIGINT,
#    template_bind BIGINT,
#    data JSONB
#)
#"""
#CREATE_MACRO_TABLE = """\
#CREATE TABLE IF NOT EXISTS templates (
#    id SERIAL PRIMARY KEY,
#    guild_id BIGINT,
#    user_id BIGINT,
#    macro_name TEXT,
#    macro TEXT
#)
#"""

class Database:
    def __init__(self) -> None:
        self.connection: asyncpg.Connection | None = None

    async def connect(self, connection_uri: str, /) -> None:
        self.connection = await asyncpg.connect(connection_uri)
        await self.connection.execute(CREATE_PREFIXES_TABLE)
        await self.connection.execute(CREATE_DEFAULT_CHARACTERS_TABLE)
        #await self.connection.execute(CREATE_TEMPLATES_TABLE)
        #await self.connection.execute(CREATE_CHARACTERS_TABLE)
        #await self.connection.execute(CREATE_MACRO_TABLE)

    async def 

    async def close(self) -> None:
        await self.connection.close()
