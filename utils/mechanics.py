import time
from discord.ext import commands

# MOVED OUTSIDE: So mortal.py can find it
def calculate_ki_refill(current_ki, max_ki, last_time):
    now = int(time.time())
    if last_time == 0 or last_time is None: 
        return current_ki, now
        
    minutes_passed = (now - last_time) // 60
    if minutes_passed >= 1:
        regained = minutes_passed * 2 
        return min(current_ki + regained, max_ki), now
        
    return current_ki, last_time

class Mechanics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Mechanics(bot))
