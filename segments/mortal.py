import discord
from discord.ext import commands
import time
from utils.database import get_player_data, update_val, adjust_val
from utils.mechanics import calculate_energy_refill

class MortalAwakening(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="temper", aliases=['t'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def temper(self, ctx):
        user_id = ctx.author.id
        data = get_player_data(user_id)

        # 1. Start Check
        if not data:
            return await ctx.send("✨ **Your soul is not yet bound.** Type `!start` to begin.")

        # 2. Rank Check (Mortal Only)
        if data['rank'] != 'Mortal':
            return await ctx.send("🏮 **NOTICE:** You have already transcended. Use Warrior commands to progress.")

        # 3. Progress Check
        if data['progress'] >= 100:
            return await ctx.send("🏮 **THE MORTAL LIMIT:** You are ready. Use **!breakthrough** to unlock your potential.")

        # 4. Restriction Check (Jail)
        now = int(time.time())
        if data['jail_until'] > now:
            remaining = (data['jail_until'] - now) // 60
            return await ctx.send(f"🚫 **RECOVERY:** Your body is broken. Wait `{max(1, remaining)}m` longer.")

        # 5. Energy Calculation
        current_energy, new_time = calculate_energy_refill(
            data['energy_current'], 
            data['energy_max'], 
            data['last_updated']
        )

        # 6. Energy/Collapse Check
        if current_energy < 10:
            update_val(user_id, 'jail_until', now + 600) # 10 min jail
            adjust_val(user_id, 'faint_count', 1)
            update_val(user_id, 'energy_current', 0)
            update_val(user_id, 'last_updated', now)
            return await ctx.send("🚨 **COLLAPSE:** You pushed too hard and fainted. You need 10 minutes to recover.")

        # 7. Success Logic
        new_progress = min(data['progress'] + 10, 100)
        update_val(user_id, 'progress', new_progress)
        update_val(user_id, 'energy_current', current_energy - 10)
        update_val(user_id, 'last_updated', now)

        # 8. Visual Feedback
        embed = discord.Embed(title="🔥 BODY TEMPERING: SUCCESS", color=0xe67e22)
        embed.add_field(name="📈 Progress", value=f"`+10%` ({new_progress}/100%)")
        embed.add_field(name="⚡ Energy", value=f"`{round(current_energy - 10, 1)}/{data['energy_max']}`")
        
        if new_progress == 100:
            embed.set_footer(text="Your mortal shell is cracking... !breakthrough is available.")
            
        await ctx.send(embed=embed)

    @commands.command(name="encounter", aliases=['e'])
    async def encounter(self, ctx):
        # We can add randomized events here later (e.g., finding Copper)
        await ctx.send("🍃 You wander the area, but find nothing but silence... for now.")

async def setup(bot):
    await bot.add_cog(MortalAwakening(bot))
