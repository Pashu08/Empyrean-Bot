import discord
from discord.ext import commands
import sqlite3
import sys

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_cmd(self, ctx):
        # Professional check for Owner status
        is_owner = await self.bot.is_owner(ctx.author)
        
        # Creating a cleaner, darker aesthetic
        embed = discord.Embed(
            title="✨ THE EMPYREAN ARCHIVE ✨", 
            description="*Choose your path, Mortal.*",
            color=0x2f3136
        )
        
        # Organized Grid Layout
        embed.add_field(name="🔥 GROWTH", value="`!t` • Temper\n`!e` • Encounter", inline=True)
        embed.add_field(name="💰 WEALTH", value="`!shop` • Market\n`!buy` • Purchase", inline=True)
        embed.add_field(name="⚖️ STATUS", value="`!p` • Profile\n`!inv` • Wallet", inline=True)

        # The Elder Authority section (Visible only to you)
        if is_owner:
            embed.add_field(
                name="🏮 ELDER AUTHORITY", 
                value="`!set_stat [user] [stat] [val]`\n`!shutdown` (Emergency Exit)", 
                inline=False
            )
            embed.color = 0xffd700 # Changes the side-bar color to Gold for you
        
        embed.set_footer(text="Empyrean Bot • First Stage: Mortal")
        await ctx.send(embed=embed)

    @commands.command(name="set_stat")
    @commands.is_owner()
    async def set_stat(self, ctx, target: discord.Member, stat: str, value: int):
        allowed = ['copper', 'silver', 'energy_current', 'progress', 'jail_until']
        if stat not in allowed:
            return await ctx.send(f"❌ **Invalid Stat.** Choose: {', '.join(allowed)}")

        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {stat} = ? WHERE user_id = ?", (value, target.id))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ **Elder Authority:** Set `{stat}` to `{value}` for **{target.display_name}**.")

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("🏮 **The Archive is closing. Souls are being preserved...**")
        await self.bot.close()
        sys.exit()

async def setup(bot):
    await bot.add_cog(Utility(bot))