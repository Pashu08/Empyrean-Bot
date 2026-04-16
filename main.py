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
intents = discord.Intents.default()
intents.message_content = True 

# 1. FIX: Add your actual Discord User ID here (Numbers only, no quotes)
# This is why your Admin commands weren't showing up!
MY_ID = 123456789012345678 # <--- CHANGE THIS TO YOUR ID

bot = commands.Bot(command_prefix='!', intents=intents, owner_id=MY_ID)

# --- THE AUTO-LOADER ---
async def load_extensions():
    # 2. FIX: Added 'utils' to the folder list so commands.py actually loads!
    for folder in ['core', 'segments', 'utils']:
        if os.path.exists(f'./{folder}'):
            for filename in os.listdir(f'./{folder}'):
                if filename.endswith('.py'):
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