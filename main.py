import discord
from discord.ext import commands
import os
import asyncio
import traceback
from utils.database import init_db
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
MY_ID = 756012403291848804  

bot = commands.Bot(command_prefix='!', intents=intents, owner_id=MY_ID)
bot.remove_command('help')

async def load_extensions():
    for folder in ['core', 'segments', 'utils']:
        if os.path.exists(f'./{folder}'):
            for filename in os.listdir(f'./{folder}'):
                if filename.endswith('.py'):
                    # Load everything without skipping
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Successfully Loaded: {folder}/{filename}')
                    except Exception:
                        print(f'❌ ERROR LOADING {filename}:')
                        traceback.print_exc()

@bot.event
async def on_ready():
    init_db()
    print(f'--- {bot.user.name} IS NOW ONLINE ---')
    print(f'Elder Authority recognized for: {bot.owner_id}')

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv('DISCORD_TOKEN')
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
