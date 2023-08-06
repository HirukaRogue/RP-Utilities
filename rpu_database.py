import motor
import asyncio
import pymongo
import motor.motor_asyncio

# mongodb+srv://HirukaRogue:<password>@rpucloudserver.bscpl0p.mongodb.net/?retryWrites=true&w=majority

# CREATE_PREFIXES_TABLE = """\
# CREATE TABLE IF NOT EXISTS prefixes (
#     id SERIAL PRIMARY KEY,
#     guild_id BIGINT,
#     prefix TEXT
# )
# """
# CREATE_CHARACTERS_TABLE = """\
# CREATE TABLE IF NOT EXISTS characters (
#     id SERIAL PRIMARY KEY,
#     user_id BIGINT,
#     guild_id BIGINT,
#     character_name TEXT,
#     character_prefix TEXT,
#     character_profile LINK
# )
# """
# CREATE_MACRO_TABLE = """\
# CREATE TABLE IF NOT EXISTS templates (
#     id SERIAL PRIMARY KEY,
#     guild_id BIGINT,
#     user_id BIGINT,
#     macro_name TEXT,
#     macro TEXT
# )
# """

# client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
# db = client.test_database
# pymongo.MongoClient().test_database.test_collection.insert_many([{'i': i} for i in range(2000)])

# pymongo.MongoClient().test_database.test_collection.delete_many({})

class Database:
    def __init__(self) -> None:
        self.dev_client: motor.motor_asyncio.AsyncIOMotorClient | None = None
        if self.dev_client is not None:
            self.database = self.dev_client.rpu_database
            print("Database connected!")
        else:
            self.database = None
            print("Cannot connect to Database!")

    async def connect(self, connection_uri: str, /) -> None:
        self.dev_client = motor.motor_asyncio.AsyncIOMotorClient(connection_uri)

    # async def close(self) -> None:
    #     await self.connection.close()
