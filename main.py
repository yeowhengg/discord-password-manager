import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from db import Database
import asyncio

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_USER = os.environ["POSTGRES_USER"]
DB_PW = os.environ["POSTGRES_PASSWORD"]
DB_HOST = os.environ["POSTGRES_HOST"]
DB = os.environ["POSTGRES_DB"]

class App:
    def __init__(self, database: Database):
        self.db = database

    async def create_pool(self):
        await self.db.create_pool()

    async def create_tables(self):
        await self.db.create_tables()
    
    async def data_insert(self, user_id, user_tag, master_passsword):
        await self.db.data_insert(user_id, user_tag, master_passsword)

db = Database(DB_USER, DB_PW, DB_HOST, DB)
database = App(db)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print('Ready!')
    await db.create_pool()
    await db.create_tables()

def is_channel(ctx: commands.Context):
    return ctx.channel.id == 1098238173546561587

@bot.command()
async def start(ctx):
    if not is_channel(ctx):
        return

    await ctx.author.send("Type in .register_master_password {your master password} to create")

@bot.command()
@commands.dm_only()
async def register_master_password(ctx: commands.Context, *, args):
    author_id = ctx.author.id
    user_exist = await db.check_user_exist(author_id)

    if user_exist:
        await ctx.author.send(f"You have already registered. Do you want to reset? (not implemented yet)")
    
    else:
        full_user_tag = ctx.author.name + "#" +  ctx.author.discriminator
        await database.data_insert(author_id, full_user_tag, args)
        await ctx.author.send(f"You have chosen {args} as your password")

        


# async def my_message(message): 
#     print(message.content)


# bot.add_listener(my_message, 'on_message')

asyncio.run(bot.run(BOT_TOKEN))





