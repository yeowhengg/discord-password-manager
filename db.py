import asyncpg
from asyncpg import UniqueViolationError

class Database:
    def __init__(self, user, pw, host, db):
        self.pool = None
        self.user = user
        self.pw = pw
        self.host = host
        self.db = db

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            host=self.host, database=self.db, user=self.user, password=self.pw
        )
        print("Pool successfully created.")

    async def create_tables(self) -> None:
        await self.pool.execute(
            """CREATE TABLE IF NOT EXISTS discord_user_profile (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE,
            user_tag TEXT,
            master_password TEXT
            )"""
        )
        print("User Profile Table successfully created.")

        await self.pool.execute(
            """CREATE TABLE IF NOT EXISTS password_storer (
            id SERIAL PRIMARY KEY,
            user_id BIGINT references discord_user_profile(user_id),
            platform TEXT, 
            password TEXT
            )"""
        )
        print("2NF table created")

        
    async def close_pool(self):
        await self.pool.close()
        print("Pool closed")

    async def check_user_exist(self, user_id):
        res = await self.pool.fetchrow(
            """ SELECT user_id FROM discord_user_profile WHERE user_id = $1 """, user_id
            )
        if res:
            return res['user_id']
            
        return False

    async def data_insert(self, user_id, user_tag, master_password):
        await self.pool.execute(
            """ INSERT INTO discord_user_profile (user_id, user_tag, master_password)
                                VALUES ($1, $2, $3)
                                RETURNING user_id""",
        user_id, user_tag, master_password)

            