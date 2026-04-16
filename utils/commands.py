import discord
from discord.ext import commands
import sqlite3
import sys

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_cmd(self, ctx):
        is_owner = await self.bot.is_owner(ctx.author)
        
        embed = discord.Embed(title="📜 THE ARCHIVE: MORTAL SCROLL", color=0xC0C0C0)
        
        # Public Sections
        embed.add_field(name="🔥 GROWTH", value="`!t` (Temper)\n`!e` (Encounter)", inline=True)
        embed.add_field(name="💰 WEALTH", value="`!shop` (Market)\n`!buy [item]`", inline=True)
        embed.add_field(name="⚖️ STATUS", value="`!p` (Profile)\n`!inv` (Wallet)", inline=True)

        # Secret Admin Section
        if is_owner:
            embed.add_field(name="🔒 ELDER AUTHORITY", value="`!set_stat [user] [stat] [val]`\n`!shutdown` (Kill Switch)", inline=False)
            embed.color = 0x8B0000 # Darker red for Admin view
        
        await ctx.send(embed=embed)

    @commands.command(name="set_stat")
    @commands.is_owner()
    async def set_stat(self, ctx, target: discord.Member, stat: str, value: int):
        allowed = ['copper', 'silver', 'energy_current', 'progress', 'jail_until']
        if stat not in allowed:
            return await ctx.send(f"❌ Invalid stat. Use: {', '.join(allowed)}")

        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {stat} = ? WHERE user_id = ?", (value, target.id))
        conn.commit()
        conn.close()
        await ctx.send(f"✅ **Elder Authority:** `{stat}` updated.")

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("🏮 **The Archive is closing. Souls are being preserved...**")
        # This properly closes the bot and exits the script
        await self.bot.close()
        sys.exit()

async def setup(bot):
    await bot.add_cog(Utility(bot))
