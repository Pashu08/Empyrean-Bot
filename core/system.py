import discord
from discord.ext import commands

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):
        embed = discord.Embed(
            title="📜 ARCHIVE COMMANDS", 
            description="*The path to immortality begins with a single command.*",
            color=0x2b2d31
        )
        
        # --- Public Section ---
        embed.add_field(
            name="⚖️ STATUS & ASSETS", 
            value="• `!start` — Bind Soul\n• `!p` — View Profile\n• `!inv` — Check Wallet", 
            inline=False
        )
        embed.add_field(
            name="🔥 CULTIVATION", 
            value="• `!t` — Body Tempering\n• `!e` — World Encounter", 
            inline=False
        )

        # --- Elder Section (ONLY YOU CAN SEE THIS) ---
        if ctx.author.id == self.bot.owner_id:
            embed.add_field(
                name="🏮 ELDER AUTHORITY", 
                value="• **`!set_stat`** `[user] [stat] [val]`\n• **`!shutdown`** — *Seal the Archive*", 
                inline=False
            )
            embed.set_footer(text="Elder status recognized. Authority active.")
        else:
            embed.set_footer(text=f"Disciple {ctx.author.name}, stay focused on your path.")

        await ctx.send(embed=embed)

    @commands.command(name="shutdown")
    async def shutdown(self, ctx):
        if ctx.author.id != self.bot.owner_id:
            return await ctx.send("❌ **Your authority is insufficient.**")
        
        await ctx.send("🌌 **The Elder has spoken. The Heavens are closing. The Archive is sealed.**")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(System(bot))
