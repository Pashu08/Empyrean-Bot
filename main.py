import discord
from discord.ext import commands
import os
import asyncio
from utils.database import init_db
from dotenv import load_dotenv

# --- SECRETS SETUP ---
# This loads the variables from your .env file
load_dotenv()

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

# --- THE AUTO-LOADER ---
async def load_extensions():
    # We are loading from CORE (Foundation) and SEGMENTS (Gameplay)
    for folder in ['core', 'segments']:
        if os.path.exists(f'./{folder}'):
            for filename in os.listdir(f'./{folder}'):
                if filename.endswith('.py'):
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Successfully Loaded: {folder}/{filename}')
                    except Exception as e:
                        print(f'❌ Error loading {filename}: {e}')

@bot.event
async def on_ready():
    init_db()
    print(f'--- {bot.user.name} IS NOW ONLINE (Professional Build) ---')

# --- ENGINE START ---
async def main():
    async with bot:
        await load_extensions()
        # This looks for "DISCORD_TOKEN" inside your .env file
        token = os.getenv('DISCORD_TOKEN')
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
