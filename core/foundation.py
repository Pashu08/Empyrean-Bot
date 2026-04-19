import discord
from discord.ext import commands
import random
import time
from utils.database import get_player_data, create_user, update_val, adjust_val
from utils.mechanics import (
    TALENTS, 
    CONSTITUTIONS, 
    calculate_cp, 
    get_vessel_limit, 
    calculate_energy_refill
)

class Foundation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_bar(self, current, max_val, color="🟩"):
        """Creates a clean visual bar with whole numbers."""
        if max_val <= 0: return "⬜" * 10
        percentage = min(current / max_val, 1)
        filled = int(percentage * 10)
        bar = color * filled + "⬜" * (10 - filled)
        return f"{bar} `{int(current)}/{int(max_val)}`"

    @commands.command(name="start")
    async def start(self, ctx):
        user_id = ctx.author.id
        if get_player_data(user_id):
            return await ctx.send("❌ **Your soul is already bound.** Use `!p` to see your journey.")

        # Weighted rolls for rarities
        talent = random.choices(list(TALENTS.keys()), weights=[50, 25, 15, 7, 2, 1])[0]
        constitution = random.choices(list(CONSTITUTIONS.keys()), weights=[50, 25, 15, 7, 2, 1])[0]

        create_user(user_id, talent, constitution)
        
        embed = discord.Embed(
            title="🏮 THE ARCHIVE OPENS",
            description="Your name has been inscribed in the annals of the Mortal World.\n\n*Use `!temper` to begin hardening your shell.*",
            color=0x2ecc71
        )
        embed.set_footer(text="Your potential is hidden until you reach the Warrior stage.")
        await ctx.send(embed=embed)

    @commands.command(name="profile", aliases=['p'])
    async def profile(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        data = get_player_data(target.id)

        if not data:
            return await ctx.send(f"❌ **{target.display_name}** has not started their journey.")

        rank = data['rank']
        stage = data['stage']
        energy, _ = calculate_energy_refill(data['energy_current'], data['energy_max'], data['last_updated'])
        
        # Color based on Talent Grade for prestige
        color = TALENTS.get(data['talent'], {}).get('color', 0x95a5a6) if rank != 'Mortal' else 0x7f8c8d
        
        title = f"📜 {target.display_name} | {rank}"
        if rank != 'Mortal':
            title = f"🏮 {target.display_name} | {rank} ({stage})"

        embed = discord.Embed(title=title, color=color)
        embed.description = f"*{data['mantra']}*\n`──────────────────────────────`"

        # --- MORTAL LAYOUT ---
        if rank == 'Mortal':
            embed.add_field(name="⚡ Energy", value=self.get_bar(energy, data['energy_max'], "🟧"), inline=False)
            embed.add_field(name="📈 Tempering Progress", value=self.get_bar(data['progress'], 100, "⬜"), inline=False)
            embed.add_field(name="💰 Wealth", value=f"🪙 `{data['copper']}` | 🥈 `{data['silver']}`", inline=False)
            embed.set_footer(text="The path to Ki is currently blocked.")

        # --- WARRIOR LAYOUT ---
        else:
            vessel = get_vessel_limit(rank, stage, data['constitution'])
            cp = calculate_cp(rank, data['internal_ki'], data['external_ki'], data['constitution'])
            
            # Potential Section
            t_grade = TALENTS[data['talent']]['grade']
            c_grade = CONSTITUTIONS[data['constitution']]['grade']
            
            embed.add_field(name="🧬 Foundation", value=f"**Talent:** `{data['talent']}` {t_grade}\n**Body:** `{data['constitution']}` {c_grade}", inline=True)
            embed.add_field(name="⚔️ Combat Power", value=f"📊 `{cp:,}`", inline=True)
            
            # The Twin Pillars
            embed.add_field(name="✨ Internal Ki (Soul)", value=self.get_bar(data['internal_ki'], vessel, "🟦"), inline=False)
            embed.add_field(name="💪 External Ki (Body)", value=f"`{data['external_ki']:,}`", inline=True)
            embed.add_field(name="⚡ Energy", value=self.get_bar(energy, data['energy_max'], "🟧"), inline=True)
            
            # Economy
            embed.add_field(name="💰 Wealth", value=f"🪙 `{data['copper']:,}` | 🥈 `{data['silver']:,}`", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="set_mantra", aliases=['mantra'])
    async def set_mantra(self, ctx, *, text: str):
        """Allows players to set their own profile bio."""
        if len(text) > 60:
            return await ctx.send("❌ Your mantra is too long! Keep it under 60 characters.")
        
        update_val(ctx.author.id, 'mantra', text)
        await ctx.send(f"✅ **Mantra Updated:** *\"{text}\"*")

    @commands.command(name="status", aliases=['s'])
    async def status(self, ctx):
        """A quick, compact status view."""
        data = get_player_data(ctx.author.id)
        if not data: return
        
        energy, _ = calculate_energy_refill(data['energy_current'], data['energy_max'], data['last_updated'])
        msg = f"👤 **{ctx.author.name}** | {data['rank']}\n⚡ Energy: `{energy}/100` | 🪙 `{data['copper']}`"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Foundation(bot))