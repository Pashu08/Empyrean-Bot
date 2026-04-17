import sqlite3
from discord.ext import commands

def init_db():
    conn = sqlite3.connect('cultivation.db')
    cursor = conn.cursor()
    
    # 1. Base Table Creation
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        rank TEXT DEFAULT 'Mortal',
        progress INTEGER DEFAULT 0,
        energy_max INTEGER DEFAULT 100,
        energy_current INTEGER DEFAULT 50,
        copper INTEGER DEFAULT 0,
        silver INTEGER DEFAULT 0,
        gold INTEGER DEFAULT 0,
        last_updated INTEGER DEFAULT 0,
        jail_until INTEGER DEFAULT 0,
        faint_count INTEGER DEFAULT 0
    )''')

    # 2. The Auto-Fixer (Migration Logic)
    # If any of these are missing in your old file, the bot adds them automatically.
    required_columns = {
        "rank": "TEXT DEFAULT 'Mortal'",
        "progress": "INTEGER DEFAULT 0",
        "energy_max": "INTEGER DEFAULT 100",
        "energy_current": "INTEGER DEFAULT 50",
        "copper": "INTEGER DEFAULT 0",
        "silver": "INTEGER DEFAULT 0",
        "gold": "INTEGER DEFAULT 0",
        "last_updated": "INTEGER DEFAULT 0",
        "jail_until": "INTEGER DEFAULT 0",
        "faint_count": "INTEGER DEFAULT 0"
    }

    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [info[1] for info in cursor.fetchall()]

    for column, definition in required_columns.items():
        if column not in existing_columns:
            print(f"🛠️ DATABASE SAFETY: Adding missing column [{column}]...")
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
            except Exception as e:
                print(f"❌ Error adding {column}: {e}")

    conn.commit()
    conn.close()
    print("✨ Database System Initialized & Verified.")

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Database(bot))
