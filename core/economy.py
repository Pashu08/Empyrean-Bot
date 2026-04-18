import discord
from discord.ext import commands
from utils.database import get_player_data, update_val, adjust_val

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wallet", aliases=['bal', 'money'])
    async def wallet(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        data = get_player_data(target.id)

        if not data:
            return await ctx.send("❌ This user has not started their journey.")

        embed = discord.Embed(title=f"💰 {target.display_name}'s Treasury", color=0xf1c40f)
        embed.add_field(name="⚖️ Silver", value=f"`{data['silver']:,}`", inline=True)
        embed.add_field(name="🪙 Copper", value=f"`{data['copper']:,}`", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="give")
    async def give(self, ctx, target: discord.Member, amount: int, currency: str):
        """Usage: !give @user 100 silver (or copper)"""
        if amount <= 0:
            return await ctx.send("❌ The amount must be positive.")
        
        currency = currency.lower()
        if currency not in ['silver', 'copper']:
            return await ctx.send("❌ Specify `silver` or `copper`.")

        sender_data = get_player_data(ctx.author.id)
        receiver_data = get_player_data(target.id)

        if not receiver_data:
            return await ctx.send("❌ Receiver has not started their journey.")

        if sender_data[currency] < amount:
            return await ctx.send(f"❌ You do not have enough {currency}.")

        # Perform Transfer
        adjust_val(ctx.author.id, currency, -amount)
        adjust_val(target.id, currency, amount)

        embed = discord.Embed(description=f"✅ **Transfer Successful**", color=0x2ecc71)
        embed.add_field(name="From", value=ctx.author.mention)
        embed.add_field(name="To", value=target.mention)
        embed.add_field(name="Amount", value=f"{amount} {currency.capitalize()}")
        await ctx.send(embed=embed)

    @commands.command(name="f_create")
    async def f_create(self, ctx, *, family_name: str):
        """Creates a family. Cost: 1,000 Silver."""
        user_id = ctx.author.id
        data = get_player_data(user_id)

        if not data:
            return await ctx.send("❌ Start your journey first.")

        if data['family_id'] != 0:
            return await ctx.send("❌ You are already part of a Family.")

        if data['silver'] < 1000:
            short = 1000 - data['silver']
            return await ctx.send(f"❌ **FOUNDATION FAILED:** You need `{short}` more Silver to establish a Family.")

        # Deduction and Creation
        # Note: family_id logic will be expanded when we build the full Family System.
        # For now, we set them as 'Head' (using a temporary ID or rank flag).
        adjust_val(user_id, 'silver', -1000)
        update_val(user_id, 'family_id', user_id) # Uses Founder ID as Family ID for now

        embed = discord.Embed(title="🏮 FAMILY ESTABLISHED", color=0x9b59b6)
        embed.description = f"The **{family_name}** has been founded by {ctx.author.mention}."
        embed.add_field(name="Cost Paid", value="⚖️ `1,000 Silver`")
        embed.set_footer(text="The foundation of a great Sect begins here.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
