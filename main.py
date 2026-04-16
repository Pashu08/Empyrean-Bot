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
intents = discord.Intents.all()
MY_ID = 756012403291848804  

bot = commands.Bot(command_prefix='!', intents=intents, owner_id=MY_ID)
bot.remove_command('help')

# --- THE AUTO-LOADER ---
async def load_extensions():
    # We load everything in these folders
    for folder in ['core', 'segments', 'utils']:
        if os.path.exists(f'./{folder}'):
            for filename in os.listdir(f'./{folder}'):
                if filename.endswith('.py'):
                    # We ONLY skip mechanics.py for now. 
                    # We MUST load database.py so the commands can use it!
                    if filename in ['mechanics.py']:
                        continue
                        
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Successfully Loaded: {folder}/{filename}')
                    except Exception:
                        print(f'❌ ERROR LOADING {filename}:')
                        traceback.print_exc()

@bot.event
async def on_ready():
    # This creates your 'cultivation.db' file if it doesn't exist
    init_db()
    print(f'--- {bot.user.name} IS NOW ONLINE ---')
    print(f'Elder Authority recognized for: {bot.owner_id}')
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
        print("\n--- BOT SHUTDOWN ---")
