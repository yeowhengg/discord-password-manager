import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument
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

db = Database(DB_USER, DB_PW, DB_HOST, DB)

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
async def register_master_password(ctx: commands.Context):

    author_id = ctx.author.id
    user_exist = await db.check_user_exist(author_id)

    if user_exist:
        await ctx.author.send(f"You have already registered. Do you want to reset? (not implemented yet)")
        return

    await ctx.author.send("Type in your master password")

    try:
        msg = await bot.wait_for("message", timeout=30)

        if msg:
            full_user_tag = ctx.author.name + "#" +  ctx.author.discriminator
            await db.data_insert(author_id, full_user_tag, msg.content)
            await ctx.author.send(f"You have chosen {msg.content} as your master password")

    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply in time!")
    

@bot.command()
@commands.dm_only()
async def platform_password_stored(ctx: commands.Context):

    try:
        await ctx.author.send("Enter your master password")
        msg = await bot.wait_for("message", timeout=30)
        if msg:
            author_id = ctx.author.id

            m_pass = await db.check_master_password(author_id, msg.content)
            if not m_pass:
                await ctx.author.send("Your master password do not match")
                return

            res = await db.retrieve_platform(author_id)

            if not res:
                await ctx.author.send("You currently have not saved any password with this bot")
                return

            platform_stored = "All platform password stored with us:"
            
            res_val = [dict(x) for x in res]
            for platforms in res_val:
                platform_stored += f"\n{platforms['platform']}"
            
            await ctx.author.send(platform_stored)

    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply in time!")


@bot.command()
@commands.dm_only()
async def save_platform_password(ctx: commands.Context):

    try:
        await ctx.author.send("Enter the platform of your choice")
        platform_msg = await bot.wait_for("message", timeout=30)
        platform = platform_msg.content

        await ctx.author.send(f"Enter the password for {platform}")
        password_msg = await bot.wait_for("message", timeout=30)
        password = password_msg.content

        if platform and password:
            author_id = ctx.author.id
            res = await db.store_password(author_id, platform, password)

            if not res:
                await ctx.author.send(f"Something went wrong...")
                return

            await ctx.author.send(f"Successfully saved password for {platform}")

            
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply in time!")


@bot.command()
@commands.dm_only()
async def view_saved_password(ctx: commands.Context):
    choice_output = "1. View all platform passwords\n2. Choose platform password to retrieve\n3. Quit"
    author_id = ctx.author.id

    try:

        await ctx.author.send("Enter your master password")
        m_pw_msg = await bot.wait_for("message", timeout=30)
        if m_pw_msg:

            m_pass = await db.check_master_password(author_id, m_pw_msg.content)
            if not m_pass:
                await ctx.author.send("Your master password do not match")
                return

        await ctx.author.send(choice_output)

        choice_msg = await bot.wait_for("message", timeout=30)
        choice = choice_msg.content

        while True:
            if choice == "3":
                break

            if choice != "1" and choice != "2":
                await ctx.author.send("Invalid option selected.")
                await ctx.author.send(choice_output)
                choice_msg = await bot.wait_for("message", timeout=30)
                continue

            break
            
        if choice == "1":
            platform_res = await db.retrieve_platform(author_id)

            if not platform_res:
                await ctx.author.send("You currently have not saved any password with this bot")
                return

            res = await db.retrieve_all_password(author_id)
            if not res:
                await ctx.author.send("Something went wrong...")
                return

            passwords = "Passwords - \n"
            res_val = [dict(x) for x in res]
            
            for platforms in res_val:
                passwords += f"{platforms['platform']}: {platforms['password']}\n"
            
            await ctx.author.send(passwords)
        
        if choice == "2":
            platform_arr = []
            platform_res = await db.retrieve_platform(author_id)

            if not platform_res:
                await ctx.author.send("You currently have not saved any password with this bot")
                return

            platform_stored = "Choose the platform: \n"
            
            res_val = [dict(x) for x in platform_res]
            for idx, platform in enumerate(res_val, start=1):
                platform_arr.append(platform['platform'])
                platform_stored += f"{idx}: {platform['platform']}\n"
            
            await ctx.author.send(platform_stored)

            while True:
                platform_choice_msg = await bot.wait_for("message", timeout=30)
                platform_choice = platform_choice_msg.content
                
                try:
                    res = await db.retrieve_platform_password(author_id, platform_arr[int(platform_choice) -1])
                    
                    if not res:
                        await ctx.author.send("Something went wrong...")
                        return

                    res_val = [dict(x) for x in res]

                    passwords = ""
                    for platforms in res_val:
                        passwords += f"{platforms['platform']}: {platforms['password']}\n"

                    await ctx.author.send(passwords)
                    
                except IndexError:
                    await ctx.author.send("Invalid option selected.")
                    await ctx.author.send(platform_stored)
                    continue


    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply in time!")

    

    
            
        
    




        

        


# async def my_message(message): 
#     print(message.content)


# bot.add_listener(my_message, 'on_message')

asyncio.run(bot.run(BOT_TOKEN))





