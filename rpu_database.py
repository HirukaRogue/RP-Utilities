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

    async def remove_prefix(self, *, guild_id: int) -> None:
        document = await self.db.prefixes.find_one({'guild_id': guild_id})

        if document is not None:
            await self.db.prefixes.delete_one({'guild_id': guild_id})

    async def get_prefix(self, *, guild_id: int) -> str | None:
        document = await self.db.prefixes.find_one({'guild_id': guild_id})
        
        if document is not None:
            return document["prefix"]
        else:
            return None


