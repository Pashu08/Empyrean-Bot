import discord
from discord.ext import commands
from utils.database import get_player_data, update_val, adjust_val, delete_user # Added delete_user here
from utils.mechanics import calculate_vessel_limit, TALENTS, CONSTITUTIONS

class ElderAuthority(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Ensures only the Bot Owner can use these commands."""
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="add_silver")
    async def add_silver(self, ctx, target: discord.Member, amount: int):
        adjust_val(target.id, 'silver', amount)
        await ctx.send(f"🏮 **ELDER EDIT:** Added `{amount}` Silver to {target.mention}.")

    @commands.command(name="set_rank")
    async def set_rank(self, ctx, target: discord.Member, *, rank_name: str):
        """Usage: !set_rank @user Second-rate Warrior"""
        data = get_player_data(target.id)
        if not data: return await ctx.send("❌ Target not found.")

        update_val(target.id, 'rank', rank_name)
        
        # Auto-update Vessel Cap for the new rank
        new_vessel = calculate_vessel_limit(data['vessel_cap'], data['constitution'], rank_name)
        update_val(target.id, 'vessel_cap', new_vessel)

        await ctx.send(f"🏮 **ELDER EDIT:** {target.mention} rank set to `{rank_name}`. Vessel adjusted to `{new_vessel}`.")

    @commands.command(name="set_talent")
    async def set_talent(self, ctx, target: discord.Member, *, talent_name: str):
        if talent_name not in TALENTS:
            return await ctx.send(f"❌ Invalid Talent. Choose: {', '.join(TALENTS.keys())}")
        
        update_val(target.id, 'talent', talent_name)
        await ctx.send(f"🏮 **ELDER EDIT:** {target.mention} talent set to `{talent_name}`.")

    @commands.command(name="set_pillar")
    async def set_pillar(self, ctx, target: discord.Member, pillar: str, value: float):
        """Usage: !set_pillar @user density 2.5"""
        pillar = pillar.lower()
        if pillar not in ['density', 'control']:
            return await ctx.send("❌ Choose `density` or `control`.")
        
        column = 'ki_density' if pillar == 'density' else 'ki_control'
        update_val(target.id, column, value)
        await ctx.send(f"🏮 **ELDER EDIT:** {target.mention}'s Ki {pillar.capitalize()} set to `{value}`.")

    @commands.command(name="refill")
    async def refill(self, ctx, target: discord.Member):
        """Instantly restores Energy and Ki to max."""
        data = get_player_data(target.id)
        if not data: return
        
        update_val(target.id, 'energy_current', data['energy_max'])
        update_val(target.id, 'internal_ki', data['vessel_cap'])
        await ctx.send(f"🏮 **ELDER EDIT:** {target.mention} has been fully restored.")

    @commands.command(name="reset_player")
    async def reset_player(self, ctx, target: discord.Member):
        """Wipes a player's soul so they can !start again."""
        data = get_player_data(target.id)
        if not data:
            return await ctx.send("❌ This player doesn't exist in the Archive.")

        delete_user(target.id)
        
        embed = discord.Embed(
            title="🏮 ELDER AUTHORITY: SOUL WIPE",
            description=f"The presence of {target.mention} has been erased from the world.",
            color=0xff0000
        )
        embed.set_footer(text="They are now free to use !start to begin a new life.")
        await ctx.send(embed=embed)

    @commands.command(name="shutdown")
    async def shutdown(self, ctx):
        await ctx.send("🏮 **The Archive is closing...** (System Shutdown)")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(ElderAuthority(bot))
