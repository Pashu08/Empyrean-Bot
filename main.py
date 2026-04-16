import discord
from discord.ext import commands
import os
import asyncio
import traceback
from utils.database import init_db
from dotenv import load_dotenv

# --- SECRETS SETUP ---
load_dotenv()

# --- BOT SETUP ---
intents = discord.Intents.all() # Changed to 'all' to ensure everything works

# 1. FIX: I recognized your ID from the photo you sent!
MY_ID = 756012403291848804  

bot = commands.Bot(command_prefix='!', intents=intents, owner_id=MY_ID)

# 2. FIX: This line stops the "Help is already existing" crash
bot.remove_command('help')

# --- THE AUTO-LOADER ---
async def load_extensions():
    # Only loads folders that actually exist
    for folder in ['core', 'segments', 'utils']:
        if os.path.exists(f'./{folder}'):
            for filename in os.listdir(f'./{folder}'):
                if filename.endswith('.py'):
                    # Skip database.py and mechanics.py if they don't have 'setup' yet
                    if filename in ['database.py', 'mechanics.py']:
                        continue
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Successfully Loaded: {folder}/{filename}')
                    except Exception:
                        print(f'❌ CRITICAL ERROR LOADING {filename}:')
                        traceback.print_exc()

@bot.event
async def on_ready():
    init_db()
    print(f'--- {bot.user.name} IS NOW ONLINE (Professional Build) ---')
    print(f'Logged in as: {bot.user.name} (ID: {bot.user.id})')
    print(f'Elder Authority recognized for ID: {bot.owner_id}')
    print('----------------------------------------------------')

# --- ENGINE START ---
async def main():
    async with bot:
        await load_extensions()
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("❌ ERROR: No DISCORD_TOKEN found in .env file!")
            return
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n--- BOT SHUTDOWN (Manual) ---")