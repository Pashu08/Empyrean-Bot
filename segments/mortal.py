import discord
from discord.ext import commands
import sqlite3
import random
import time

class MortalAwakening(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="temper", aliases=['t'])
    async def temper(self, ctx):
        user_id = ctx.author.id
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        now = int(time.time())

        # 1. Archive Restriction Check (Jail/Plateau/Faint)
        cursor.execute('SELECT energy_current, progress, jail_until FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("❌ **Identity unknown. Type `!start` first.**")
            conn.close()
            return

        energy, progress, jail_time = result

        if jail_time > now:
            remaining = (jail_time - now) // 60
            embed = discord.Embed(title="🚫 ARCHIVE NOTICE: RESTRICTION", color=0x8B0000)
            embed.description = f"Subject is in a state of **Collapse or Meditation**. Remaining: `{remaining}m`."
            await ctx.send(embed=embed)
            conn.close()
            return

        # 2. Faint System (If Energy is < 10)
        if energy < 10:
            lockout_time = now + 300 
            cursor.execute("UPDATE users SET jail_until = ? WHERE user_id = ?", (lockout_time, user_id))
            conn.commit()
            conn.close()
            await ctx.send("🚨 **COLLAPSE:** You pushed too hard with no Qi! Your body has shut down. **(5m Lockout)**")
            return

        # 3. Plateau Risk (10% Chance)
        if random.random() < 0.10:
            lockout_time = now + 300 
            cursor.execute('UPDATE users SET energy_current = energy_current - 10, jail_until = ? WHERE user_id = ?', 
                           (lockout_time, user_id))
            conn.commit()
            conn.close()
            
            embed = discord.Embed(title="⚠️ ARCHIVE NOTICE: PLATEAU", color=0xFFA500)
            embed.description = "Your meridians have jammed. You must meditate to clear the blockage. **(5m Lockout)**"
            await ctx.send(embed=embed)
            return

        # 4. Success Logic
        new_progress = min(progress + 10, 100)
        cursor.execute('UPDATE users SET progress = ?, energy_current = energy_current - 10 WHERE user_id = ?', 
                       (new_progress, user_id))
        conn.commit()
        conn.close()

        # 5. Success Display
        embed = discord.Embed(title="🔥 BODY TEMPERING: SUCCESS", color=0xe67e22)
        embed.description = f"{ctx.author.mention} endures the pain to strengthen their foundation!"
        embed.add_field(name="📈 Progress", value=f"`+{10}%` (`{new_progress}/100%`)", inline=True)
        embed.add_field(name="⚡ Qi Remaining", value=f"`{energy - 10}`", inline=True)
        embed.set_footer(text="The path to immortality is paved with pain.")
        await ctx.send(embed=embed)

    @commands.command(name="encounter", aliases=['e'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def encounter(self, ctx):
        user_id = ctx.author.id
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT energy_current, jail_until FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("❌ **Identity unknown. Type `!start` first.**")
            conn.close()
            return
            
        energy, jail_time = result
        now = int(time.time())

        if jail_time > now:
            remaining = (jail_time - now) // 60
            await ctx.send(f"🚫 **Jailed.** `{remaining}m` remaining.")
            conn.close()
            return

        if energy < 5:
            await ctx.send("❌ **Insufficient Qi (Need 5).**")
            conn.close()
            return

        roll = random.randint(1, 100)
        
        if roll <= 50: # 50% Success
            gain = random.randint(2, 5)
            msg = f"📦 **Common Find:** You found `{gain}` Copper coins."
            cursor.execute("UPDATE users SET copper = copper + ? WHERE user_id = ?", (gain, user_id))
        elif roll <= 70: # 20% Fail
            msg = "⚠️ **Minor Setback:** You tripped into a thorn bush. Found nothing."
        elif roll <= 85: # 15% Success
            msg = "💎 **Uncommon Discovery:** You found `12` Copper coins!"
            cursor.execute("UPDATE users SET copper = copper + 12 WHERE user_id = ?", (user_id,))
        elif roll <= 92: # 7% Rare Silver
            msg = "🥈 **Rare Discovery:** You found `1` Silver piece in a hidden cache!"
            cursor.execute("UPDATE users SET silver = silver + 1 WHERE user_id = ?", (user_id,))
        elif roll <= 97: # 5% Spirit Herb
            msg = "🌀 **Rare Blessing:** Spirit Herb found! **+15 Energy restored.**"
            cursor.execute("UPDATE users SET energy_current = energy_current + 15 WHERE user_id = ?", (user_id,))
        else: # 3% Jail
            msg = "🚨 **CRITICAL FAILURE:** Trespassed on Elder's land! **10m Jail.**"
            cursor.execute("UPDATE users SET jail_until = ? WHERE user_id = ?", (now + 600, user_id))

        cursor.execute("UPDATE users SET energy_current = energy_current - 5 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        embed = discord.Embed(title="🧭 ENCOUNTER LOG", description=msg, color=0xC0C0C0)
        embed.set_footer(text=f"Qi Left: {energy - 5}")
        await ctx.send(embed=embed)
        
            @encounter.error
    async def encounter_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            if seconds < 60:
                await ctx.send(f"⏳ **PATIENCE:** Your soul is weary. Rest for `{int(seconds)}s` before exploring again.")
            else:
                minutes = round(seconds / 60)
                await ctx.send(f"⏳ **PATIENCE:** Your soul is weary. Rest for `{minutes}m` before exploring again.")
        else:
            raise error


async def setup(bot):
    await bot.add_cog(MortalAwakening(bot))
