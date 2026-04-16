import sqlite3
from discord.ext import commands

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def init_db():
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        # This creates the table with all the stats you need
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            rank TEXT DEFAULT 'Mortal',
            progress INTEGER DEFAULT 0,
            energy_max INTEGER DEFAULT 100,
            energy_current INTEGER DEFAULT 50,
            copper INTEGER DEFAULT 0,
            silver INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 0,
            last_updated INTEGER DEFAULT 0
        )''')
        conn.commit()
        conn.close()
        print("✨ Database System Initialized.")

# This is the "Start Button" the laptop was looking for
async def setup(bot):
    await bot.add_cog(Database(bot))