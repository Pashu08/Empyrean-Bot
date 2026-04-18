import discord
from discord.ext import commands
import random
from utils.database import get_player_data, create_user, update_val
from utils.mechanics import TALENTS, CONSTITUTIONS, calculate_ki_gain, calculate_vessel_limit, calculate_cp

class Foundation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_bar(self, current, max_val, length=10):
        """Creates a visual progress bar."""
        if max_val <= 0: return " [░░░░░░░░░░] "
        filled = int((current / max_val) * length)
        return f" `[{'█' * filled}{'░' * (length - filled)}]` "

    @commands.command(name="start")
    async def start(self, ctx):
        user_id = ctx.author.id
        if get_player_data(user_id):
            return await ctx.send("❌ **Your path has already begun.** Use `!p` to see your progress.")

        # Secretly roll Talent and Constitution
        talent = random.choices(list(TALENTS.keys()), weights=[50, 25, 15, 7, 2, 1])[0]
        constitution = random.choices(list(CONSTITUTIONS.keys()), weights=[50, 25, 15, 7, 2, 1])[0]

        create_user(user_id, talent, constitution)
        
        embed = discord.Embed(
            title="🏮 THE ARCHIVE OPENS",
            description="You have been registered as a **Mortal**. Your journey begins in the dust, but your end... that is for you to decide.",
            color=0x2ecc71
        )
        embed.add_field(name="📜 Current Goal", value="Use `!temper` to strengthen your mortal shell.")
        embed.set_footer(text="Your hidden potential is dormant. Awaken it at 100% progress.")
        await ctx.send(embed=embed)

    @commands.command(name="profile", aliases=['p'])
    async def profile(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        data = get_player_data(target.id)

        if not data:
            return await ctx.send(f"❌ **{target.display_name}** has not started their journey.")

        rank = data['rank']
        
        # Calculate Current Stats
        if rank == 'Mortal':
            embed = discord.Embed(title=f"📜 {target.display_name}'s Mortal Identity", color=0x95a5a6)
            embed.add_field(name="🏮 Rank", value=f"`{rank}`", inline=True)
            embed.add_field(name="💰 Wealth", value=f"🪙 `{data['copper']}` | ⚖️ `{data['silver']}`", inline=True)
            
            progress = data['progress']
            embed.add_field(name=f"📈 Body Tempering ({progress}%)", value=self.get_bar(progress, 100, 15), inline=False)
            embed.set_footer(text="The internal world is still locked to you.")
        
        else:
            # Warrior Profile (The Dashboard)
            current_ki, _ = calculate_ki_gain(
                data['internal_ki'], data['last_updated'], 
                rank, data['talent'], data['vessel_cap']
            )
            vessel_max = calculate_vessel_limit(data['vessel_cap'], data['constitution'], rank)
            cp = calculate_cp(rank, data['ki_density'], data['ki_control'], data['constitution'])

            embed = discord.Embed(title=f"🏮 {target.display_name} | {rank}", color=0x3498db)
            
            # Zone 1: Identity
            embed.add_field(name="🧬 Potential", value=f"**Talent:** `{data['talent']}`\n**Body:** `{data['constitution']}`", inline=True)
            embed.add_field(name="🎭 Path", value=f"`{data['path']}`", inline=True)
            embed.add_field(name="⚔️ Combat Power", value=f"`{cp:,}`", inline=True)

            # Zone 2: Pillars
            ki_bar = self.get_bar(current_ki, vessel_max, 12)
            embed.add_field(name=f"🌀 Internal Ki ({int(current_ki)}/{vessel_max})", value=ki_bar, inline=False)
            
            pillar_stats = f"**Density:** `{data['ki_density']}` | **Control:** `{data['ki_control']}`"
            embed.add_field(name="💎 Pillars of Power", value=pillar_stats, inline=False)

            # Zone 3: Economy
            embed.add_field(name="💰 Wealth", value=f"🪙 `{data['copper']}` | ⚖️ `{data['silver']}`", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="breakthrough")
    async def breakthrough(self, ctx):
        user_id = ctx.author.id
        data = get_player_data(user_id)

        if not data or data['rank'] != 'Mortal':
            return await ctx.send("❌ This ceremony is only for Mortals at their limit.")

        if data['progress'] < 100:
            return await ctx.send(f"❌ Your body is not ready. Progress: `{data['progress']}/100%`")

        # THE CEREMONY
        new_rank = "Third-rate Warrior"
        update_val(user_id, 'rank', new_rank)
        update_val(user_id, 'progress', 0)
        update_val(user_id, 'path', 'Neutral') # Initial path

        embed = discord.Embed(
            title="🌌 THE AWAKENING",
            description=f"Congratulations, **{ctx.author.name}**. Your mortal chains have shattered.",
            color=0xf1c40f
        )
        embed.add_field(name="🏮 New Rank", value=f"`{new_rank}`", inline=False)
        embed.add_field(name="🧬 Talent Revealed", value=f"**{data['talent']}**", inline=True)
        embed.add_field(name="💪 Constitution Revealed", value=f"**{data['constitution']}**", inline=True)
        
        embed.set_footer(text="The world of Ki is now open. Use !profile to see your new stats.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Foundation(bot))
