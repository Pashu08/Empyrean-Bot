import discord
from discord.ext import commands
import time
import random
from utils.database import get_player_data, update_val, adjust_val
from utils.mechanics import calculate_energy_refill

class MortalAwakening(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_energy_bar(self, current, max_val):
        """Creates a visual energy bar."""
        filled = int((current / max_val) * 10)
        bar = "🟩" * filled + "⬜" * (10 - filled)
        return f"{bar} `{current}/{max_val}`"

    @commands.command(name="temper", aliases=['t'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def temper(self, ctx):
        user_id = ctx.author.id
        data = get_player_data(user_id)

        if not data:
            return await ctx.send("✨ **Your soul is not yet bound.** Type `!start` to begin.")

        if data['rank'] != 'Mortal':
            return await ctx.send("🏮 **NOTICE:** Your shell is already tempered. Use Warrior commands.")

        if data['progress'] >= 100:
            return await ctx.send("🏮 **LIMIT REACHED:** You are ready. Use `!breakthrough`.")

        # Recovery Check
        now = int(time.time())
        if data['jail_until'] > now:
            rem = (data['jail_until'] - now) // 60
            return await ctx.send(f"🚫 **RECOVERY:** Wait `{max(1, rem)}m` for your body to heal.")

        # Energy Refill (Whole Numbers)
        current_energy, _ = calculate_energy_refill(data['energy_current'], data['energy_max'], data['last_updated'])

        # Collapse Logic
        if current_energy < 10:
            update_val(user_id, 'jail_until', now + 600)
            update_val(user_id, 'energy_current', 0)
            update_val(user_id, 'last_updated', now)
            return await ctx.send("🚨 **COLLAPSE:** You fainted from exhaustion. 10m recovery required.")

        # Success
        new_progress = min(data['progress'] + 10, 100)
        new_energy = current_energy - 10
        update_val(user_id, 'progress', new_progress)
        update_val(user_id, 'energy_current', new_energy)
        update_val(user_id, 'last_updated', now)

        embed = discord.Embed(title="🔥 BODY TEMPERING", color=0xe67e22)
        embed.description = f"**Rank:** {data['rank']}\n---"
        embed.add_field(name="📈 Progress", value=f"`+10%` ({new_progress}/100%)", inline=False)
        embed.add_field(name="⚡ Energy", value=self.get_energy_bar(new_energy, data['energy_max']), inline=False)
        
        if new_progress == 100:
            embed.set_footer(text="The mortal wall is crumbling... !breakthrough is ready.")
            
        await ctx.send(embed=embed)

    @commands.command(name="encounter", aliases=['e'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def encounter(self, ctx):
        user_id = ctx.author.id
        data = get_player_data(user_id)
        if not data: return
        
        now = int(time.time())
        if data['jail_until'] > now: return await ctx.send("🚫 You are too injured to wander.")

        # Rank-Based Energy Cost & Scaling
        is_warrior = data['rank'] != 'Mortal'
        energy_cost = 25 if is_warrior else 10
        
        current_energy, _ = calculate_energy_refill(data['energy_current'], data['energy_max'], data['last_updated'])
        
        if current_energy < energy_cost:
            return await ctx.send(f"⚠️ You need `{energy_cost}` Energy to wander.")

        # The Loot Table
        roll = random.randint(1, 100)
        result_text = ""
        color = 0x95a5a6
        
        if roll <= 40: # 40% Silence
            result_text = "🍃 The mountains are silent. You find nothing but peace."
        elif roll <= 70: # 30% Copper
            amt = random.randint(100, 300) if is_warrior else random.randint(10, 50)
            adjust_val(user_id, 'copper', amt)
            result_text = f"🪙 **Loot:** You found a discarded pouch containing `{amt} Copper`."
            color = 0xb87333
        elif roll <= 85: # 15% Spirit Herb
            update_val(user_id, 'energy_current', min(data['energy_max'], current_energy + 20))
            result_text = "🌿 **Rare Find:** You consumed a Spirit Herb! Restored `20 Energy`."
            color = 0x2ecc71
        elif roll <= 95: # 10% Silver
            amt = random.randint(5, 15) if is_warrior else random.randint(1, 3)
            adjust_val(user_id, 'silver', amt)
            result_text = f"🥈 **Fortune:** You discovered a hidden cache! Gained `{amt} Silver`."
            color = 0xbdc3c7
        else: # 5% Scuffle
            loss = 25 if is_warrior else 10
            update_val(user_id, 'energy_current', max(0, current_energy - loss))
            result_text = f"💢 **Scuffle:** A wild beast attacked! You escaped but lost `{loss} extra Energy`."
            color = 0xe74c3c

        # Final Update
        update_val(user_id, 'energy_current', max(0, current_energy - energy_cost))
        update_val(user_id, 'last_updated', now)

        embed = discord.Embed(title="🌍 WORLD ENCOUNTER", description=result_text, color=color)
        embed.set_footer(text=f"Energy Spent: {energy_cost}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MortalAwakening(bot))
