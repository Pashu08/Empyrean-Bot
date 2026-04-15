import discord
from discord.ext import commands
import sqlite3

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wallet", aliases=['cash', 'money', 'bal', 'w'])
    async def wallet(self, ctx):
        user_id = ctx.author.id
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        
        # We only select Copper and Silver now
        cursor.execute('SELECT copper, silver FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            await ctx.send("❌ **Your treasury does not exist. Type `!start` to open your account.**")
            return

        c, s = result
        
        # --- THE UPGRADED "SILVER ARCHIVE" TREASURY ---
        embed = discord.Embed(
            title="🏦 TREASURY DATA: VERIFIED",
            color=0xC0C0C0 # Professional Silver Theme
        )
        
        embed.add_field(name="👤 Owner", value=f"{ctx.author.mention}", inline=False)
        
        # Clean two-currency display
        embed.add_field(name="🥈 Silver", value=f"`{s}`", inline=True)
        embed.add_field(name="🪙 Copper", value=f"`{c}`", inline=True)
        
        embed.set_footer(text="Wealth is but a tool for the journey to the peak.")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
