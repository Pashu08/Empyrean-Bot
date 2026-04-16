import discord
from discord.ext import commands
import os
import asyncio
import traceback  # <--- Essential for seeing the actual bugs
from utils.database import init_db
from dotenv import load_dotenv

# --- SECRETS SETUP ---
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
                        # Clear old versions from memory and load fresh
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Successfully Loaded: {folder}/{filename}')
                    except Exception:
                        # THIS is what will show you why the bot is glitching
                        print(f'❌ CRITICAL ERROR LOADING {filename}:')
                        traceback.print_exc()

@bot.event
async def on_ready():
    init_db()
    print(f'--- {bot.user.name} IS NOW ONLINE (Professional Build) ---')
    print(f'Logged in as: {bot.user.name} (ID: {bot.user.id})')
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

