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

# 4. Global Error Handling (Thematic Warnings)
@bot.event
async def on_command_error(ctx, error):
    # Handle Cooldowns (Spam Protection)
    if isinstance(error, commands.CommandOnCooldown):
        msg = f"🏮 **WARNING:** Your meridians are trembling! Slow down. Wait `{error.retry_after:.1f}s`."
        return await ctx.send(msg, delete_after=5) # Auto-deletes to keep chat clean

    # Ignore commands that don't exist (prevents spam from typos)
    if isinstance(error, commands.CommandNotFound):
        return

    # Log other errors for debugging
    print(f"⚠️ Error in command '{ctx.command}': {error}")
    traceback.print_exc()

# 5. On Ready Event
@bot.event
async def on_ready():
    # Run the Auto-Fixer to prepare the database columns
    init_db()
    print(f'\n--- {bot.user.name} IS ONLINE ---')
    print(f'Elder Authority: {bot.owner_id}')
    print('----------------------------------\n')

# 6. Main Run Function
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping bot...")
