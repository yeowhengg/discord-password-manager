import asyncpg

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

        await self.pool.execute(
            """CREATE TABLE IF NOT EXISTS platform_password (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            platform TEXT, 
            password TEXT
            )"""

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


    async def user_insert(self, user_id, user_tag, master_password):
        await self.pool.execute(
            """ INSERT INTO discord_user_profile (user_id, user_tag, master_password)
                                VALUES ($1, $2, $3)
                                RETURNING user_id""",
        user_id, user_tag, master_password)

    
    async def check_master_password(self, user_id, master_password):
        res = await self.pool.fetchrow( 
            """ SELECT user_id FROM discord_user_profile WHERE user_id = $1 AND master_password = $2 """, user_id, master_password
        )
        if res:
            return True
        
        return False


    async def retrieve_platform(self, user_id):
        res = await self.pool.fetch(
            """ SELECT DISTINCT(platform) FROM platform_password WHERE user_id = $1 """, user_id
        )
        if res:
            return res
        
        return False

    
    async def retrieve_all_password(self, user_id):
        res = await self.pool.fetch(
            """ SELECT platform, password FROM platform_password WHERE user_id = $1 """, user_id
        )

        if res:
            return res
        
        return False
    

    async def retrieve_platform_password(self, user_id, platform):
        res = await self.pool.fetch(
            """ SELECT platform, password FROM platform_password WHERE user_id = $1 AND platform = $2 """, user_id, platform
        )

        if res:
            return res
        
        return False

    
    async def store_password(self, user_id, platform, password):
        res = await self.pool.execute(
            """ INSERT INTO platform_password (user_id, platform, password)
                VALUES ($1, $2, $3) """, user_id, platform, password
        )

        if res:
            return True
        
        return False
    
    

            