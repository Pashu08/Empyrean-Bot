import discord
from discord.ext import commands
import os
import asyncio
import traceback
from utils.database import init_db
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Bot Setup
intents = discord.Intents.all()
# Your ID remains the owner for Elder Authority commands
MY_ID = 756012403291848804  

bot = commands.Bot(command_prefix='!', intents=intents, owner_id=MY_ID)
bot.remove_command('help')

# 3. Extension Loader (The Cog System)
async def load_extensions():
    # We only load folders that contain Cogs/Commands
    # 'utils' is skipped here because it's a library folder
    for folder in ['core', 'segments']:
        if os.path.exists(f'./{folder}'):
            for filename in os.listdir(f'./{folder}'):
                if filename.endswith('.py'):
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Successfully Loaded: {folder}/{filename}')
                    except Exception:
                        print(f'❌ ERROR LOADING {folder}/{filename}:')
                        traceback.print_exc()

# 4. On Ready Event
@bot.event
async def on_ready():
    # Run the Auto-Fixer to prepare the database columns
    init_db()
    print(f'\n--- {bot.user.name} IS ONLINE ---')
    print(f'Elder Authority: {bot.owner_id}')
    print('----------------------------------\n')

# 5. Main Run Function
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping bot...")
