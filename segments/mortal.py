import discord
from discord.ext import commands
import sqlite3
import random
import time
from utils.mechanics import calculate_ki_refill

class MortalAwakening(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="temper", aliases=['t'])
    @commands.cooldown(1, 5, commands.BucketType.user) # <--- Added 5s Cooldown
    async def temper(self, ctx):
        user_id = ctx.author.id
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT energy_current, energy_max, last_updated, progress, jail_until, faint_count FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("✨ **Your soul is not yet bound to the Archive.** Type `!start` to begin.")
            conn.close()
            return

        old_ki, max_ki, l_time, progress, jail_time, faint_count = result
        ki, new_time = calculate_ki_refill(old_ki, max_ki, l_time)
        
        cursor.execute('UPDATE users SET energy_current = ?, last_updated = ? WHERE user_id = ?', (ki, new_time, user_id))
        conn.commit()

        now = int(time.time())
        if progress >= 100:
            await ctx.send("🏮 **THE MORTAL LIMIT:** Use **!breakthrough**.")
            conn.close()
            return

        if jail_time > now:
            remaining = (jail_time - now) // 60
            await ctx.send(f"🚫 **RESTRICTION:** `{max(1, remaining)}m` left.")
            conn.close()
            return

        if ki < 10:
            cursor.execute("UPDATE users SET jail_until = ?, faint_count = faint_count + 1 WHERE user_id = ?", (now + 600, user_id))
            conn.commit()
            conn.close()
            await ctx.send("🚨 **COLLAPSE:** No Ki!")
            return

        new_progress = min(progress + 10, 100)
        cursor.execute('UPDATE users SET progress = ?, energy_current = energy_current - 10 WHERE user_id = ?', (new_progress, user_id))
        conn.commit()
        conn.close()

        embed = discord.Embed(title="🔥 BODY TEMPERING: SUCCESS", color=0xe67e22)
        embed.add_field(name="📈 Progress", value=f"`+10%` ({new_progress}/100%)")
        embed.add_field(name="⚡ Ki Left", value=f"`{ki - 10}`")
        await ctx.send(embed=embed)

    @commands.command(name="encounter", aliases=['e'])
    async def encounter(self, ctx):
        # Your encounter code remains here
        pass

async def setup(bot):
    await bot.add_cog(MortalAwakening(bot))
