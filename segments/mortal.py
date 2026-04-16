import discord
from discord.ext import commands
import sqlite3
import random
import time
from utils.mechanics import calculate_ki_refill

class MortalAwakening(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # [ CORE ACTION: BODY TEMPERING ]
    # ==========================================
    @commands.command(name="temper", aliases=['t'])
    async def temper(self, ctx):
        user_id = ctx.author.id
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        
        # 1. Fetch Data
        cursor.execute('SELECT energy_current, energy_max, last_updated, progress, jail_until, faint_count FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("✨ **Your soul is not yet bound to the Archive.** Type `!start` to begin.")
            conn.close()
            return

        old_ki, max_ki, l_time, progress, jail_time, faint_count = result
        
        # --- PASSIVE REFILL TRIGGER ---
        ki, new_time = calculate_ki_refill(old_ki, max_ki, l_time)
        cursor.execute('UPDATE users SET energy_current = ?, last_updated = ? WHERE user_id = ?', (ki, new_time, user_id))
        conn.commit()

        # 2. Progress Cap Check
        if progress >= 100:
            embed = discord.Embed(title="🏮 THE MORTAL LIMIT", color=0xff0000)
            embed.description = (
                "Your physical vessel has reached its absolute peak. Any further tempering "
                "will shatter your bones. You must undergo a **!breakthrough** to evolve."
            )
            await ctx.send(embed=embed)
            conn.close()
            return

        # 3. Archive Restriction Check
        now = int(time.time())
        if jail_time > now:
            remaining = (jail_time - now) // 60
            embed = discord.Embed(title="🚫 ARCHIVE NOTICE: RESTRICTION", color=0x8B0000)
            embed.description = f"Subject is in a state of **Collapse or Meditation**. Remaining: `{max(1, remaining)}m`."
            await ctx.send(embed=embed)
            conn.close()
            return

        # 4. Faint System
        if ki < 10:
            faint_timers = {0: 120, 1: 300, 2: 600} 
            lockout_duration = faint_timers.get(faint_count, 600)
            
            cursor.execute("UPDATE users SET jail_until = ?, faint_count = faint_count + 1 WHERE user_id = ?", 
                           (now + lockout_duration, user_id))
            conn.commit()
            conn.close()
            await ctx.send(f"🚨 **COLLAPSE:** You pushed too hard with no Ki! Your body has shut down. **({lockout_duration//60}m Lockout)**")
            return

        # 5. [EVENT: MERIDIAN CONGESTION] (Updated Topic 2)
        if random.random() < 0.10:
            lockout_time = now + 120 # 2 Minute Lockout
            cursor.execute('UPDATE users SET energy_current = energy_current - 10, jail_until = ? WHERE user_id = ?', 
                           (lockout_time, user_id))
            conn.commit()
            conn.close()
            
            embed = discord.Embed(title="⚠️ MERIDIAN CONGESTION", color=0xFFA500)
            embed.description = (
                "Your veins are overheating! Stop forcing your progress.\n\n"
                "**Wait 2 minutes for your body to cool down.**"
            )
            await ctx.send(embed=embed)
            return

        # 6. Success Logic
        new_progress = min(progress + 10, 100)
        cursor.execute('UPDATE users SET progress = ?, energy_current = energy_current - 10 WHERE user_id = ?', 
                       (new_progress, user_id))
        conn.commit()
        conn.close()

        # 7. Success Display
        embed = discord.Embed(title="🔥 BODY TEMPERING: SUCCESS", color=0xe67e22)
        embed.description = f"{ctx.author.mention} endures the pain to strengthen their foundation!"
        embed.add_field(name="📈 Progress", value=f"`+10%` ({new_progress}/100%)", inline=True)
        embed.add_field(name="⚡ Ki Left", value=f"`{ki - 10}`", inline=True)
        embed.set_footer(text="The path to immortality is paved with pain.")
        await ctx.send(embed=embed)

    # ==========================================
    # [ SIDE ACTION: MORTAL ENCOUNTER ]
    # ==========================================
    @commands.command(name="encounter", aliases=['e'])
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def encounter(self, ctx):
        user_id = ctx.author.id
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT energy_current, energy_max, last_updated, jail_until FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            await ctx.send("✨ **Your soul is not yet bound to the Archive.** Type `!start` to begin.")
            conn.close()
            return
            
        old_ki, max_ki, l_time, jail_time = result
        
        ki, new_time = calculate_ki_refill(old_ki, max_ki, l_time)
        cursor.execute('UPDATE users SET energy_current = ?, last_updated = ? WHERE user_id = ?', (ki, new_time, user_id))
        conn.commit()

        now = int(time.time())
        if jail_time > now:
            remaining = (jail_time - now) // 60
            await ctx.send(f"🚫 **RECOVERY:** Your soul is settling. `{max(1, remaining)}m` remaining.")
            conn.close()
            return

        if ki < 5:
            await ctx.send("❌ **Insufficient Ki (Need 5).**")
            conn.close()
            return

        roll = random.randint(1, 100)
        
        if roll <= 50: 
            gain = random.randint(2, 4)
            msg = f"📦 **Common Find:** You found `{gain}` Copper coins."
            cursor.execute("UPDATE users SET copper = copper + ? WHERE user_id = ?", (gain, user_id))
        elif roll <= 70: 
            msg = "⚠️ **Minor Setback:** You tripped into a thorn bush. Found nothing."
        elif roll <= 85: 
            msg = "💎 **Uncommon Discovery:** You found `8` Copper coins!"
            cursor.execute("UPDATE users SET copper = copper + 8 WHERE user_id = ?", (user_id,))
        elif roll <= 92: 
            msg = "💰 **JACKPOT:** You found a traveler's lost pouch with `20` Copper coins!"
            cursor.execute("UPDATE users SET copper = copper + 20 WHERE user_id = ?", (user_id,))
        elif roll <= 97: 
            msg = "🌀 **Rare Blessing:** Spirit Herb found! **+15 Ki restored.**"
            cursor.execute("UPDATE users SET energy_current = energy_current + 15 WHERE user_id = ?", (user_id,))
        else: 
            msg = "🚨 **CRITICAL FAILURE:** Trespassed on Elder's land! **10m Jail.**"
            cursor.execute("UPDATE users SET jail_until = ? WHERE user_id = ?", (now + 600, user_id))

        cursor.execute("UPDATE users SET energy_current = energy_current - 5 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        embed = discord.Embed(title="🧭 ENCOUNTER LOG", description=msg, color=0xC0C0C0)
        embed.set_footer(text=f"Ki Left: {ki - 5}")
        await ctx.send(embed=embed)

    @encounter.error
    async def encounter_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            minutes = int(seconds // 60)
            sec = int(seconds % 60)
            await ctx.send(f"⏳ **MEDITATION REQUIRED:** Your soul is weary from travel. Return to the void for `{minutes}m {sec}s` to recover.")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(MortalAwakening(bot))
