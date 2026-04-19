import discord
from discord.ext import commands
from utils.database import get_player_data, update_val, adjust_val, delete_user
from utils.mechanics import TALENTS, CONSTITUTIONS

class ElderAuthority(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Strictly restricts these commands to the High Elder (Owner)."""
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="give_money")
    async def give_money(self, ctx, coin_type: str, amount: int, target: discord.Member):
        """Usage: !give_money copper 1000 @user"""
        coin_type = coin_type.lower()
        if coin_type not in ['copper', 'silver']:
            return await ctx.send("❌ Choose `copper` or `silver`.")
        
        adjust_val(target.id, coin_type, amount)
        await ctx.send(f"🏮 **ELDER DECREE:** Granted `{amount}` {coin_type.capitalize()} to {target.mention}.")

    @commands.command(name="audit")
    async def audit(self, ctx, target: discord.Member):
        """DMs the Elder a detailed report of a player's hidden stats."""
        data = get_player_data(target.id)
        if not data: return await ctx.send("❌ Player not found.")

        t_mult = TALENTS.get(data['talent'], {}).get('mult', 1.0)
        c_vmod = CONSTITUTIONS.get(data['constitution'], {}).get('v_mod', 1.0)
        c_pmod = CONSTITUTIONS.get(data['constitution'], {}).get('p_mod', 1.0)

        report = (
            f"🏮 **AUDIT REPORT: {target.name}**\n"
            f"`──────────────────────────────`\n"
            f"**Rank:** {data['rank']} ({data['stage']})\n"
            f"**Talent:** {data['talent']} (Gain: `{t_mult}x`)\n"
            f"**Body:** {data['constitution']} (Vessel: `{c_vmod}x` | Power: `{c_pmod}x`)\n"
            f"**Internal Ki:** `{data['internal_ki']}` / `{data['vessel_cap']}`\n"
            f"**External Ki:** `{data['external_ki']}`\n"
            f"**Mantra:** *{data['mantra']}*\n"
            f"`──────────────────────────────`"
        )
        
        try:
            await ctx.author.send(report)
            await ctx.send(f"✅ Audit for {target.mention} sent to your DMs.")
        except:
            await ctx.send("❌ I couldn't DM you. Please open your DMs.")

    @commands.command(name="pardon")
    async def pardon(self, ctx, target: discord.Member):
        """Instantly heals a player from jail or injuries."""
        update_val(target.id, 'jail_until', 0)
        await ctx.send(f"🏮 **ELDER MERCY:** {target.mention}'s injuries have been miraculously healed.")

    @commands.command(name="set_stats")
    async def set_stats(self, ctx, target: discord.Member, stat_type: str, value: int):
        """Directly sets Ki values. Usage: !set_stats @user internal 5000"""
        stat_type = stat_type.lower()
        column = ""
        if stat_type == "internal": column = "internal_ki"
        elif stat_type == "external": column = "external_ki"
        else: return await ctx.send("❌ Choose `internal` or `external`.")

        update_val(target.id, column, value)
        await ctx.send(f"🏮 **ELDER EDIT:** {target.mention}'s {stat_type.capitalize()} Ki set to `{value}`.")

    @commands.command(name="set_mantra_other")
    async def set_mantra_other(self, ctx, target: discord.Member, *, text: str):
        """Force-updates a player's mantra (for moderation)."""
        update_val(target.id, 'mantra', text)
        await ctx.send(f"✅ Mantra for {target.mention} has been reset by Elder Authority.")

    @commands.command(name="refill")
    async def refill(self, ctx, target: discord.Member):
        """Restores Energy and Ki to max instantly."""
        data = get_player_data(target.id)
        if not data: return
        update_val(target.id, 'energy_current', data['energy_max'])
        update_val(target.id, 'internal_ki', data['vessel_cap'])
        await ctx.send(f"🏮 **ELDER RESTORATION:** {target.mention} is now at peak condition.")

    @commands.command(name="reset_player")
    async def reset_player(self, ctx, target: discord.Member):
        """Wipes a player so they can !start fresh."""
        delete_user(target.id)
        await ctx.send(f"🏮 **ELDER AUTHORITY:** The soul of {target.mention} has been erased from the Archive.")

async def setup(bot):
    await bot.add_cog(ElderAuthority(bot))