import discord
from discord.ext import commands
from utils.database import get_player_data
from utils.mechanics import TALENTS, CONSTITUTIONS, COPPER_TO_SILVER
import time

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=['h'])
    async def help_command(self, ctx):
        """A dynamic guide that changes based on your rank."""
        user_id = ctx.author.id
        data = get_player_data(user_id)
        
        embed = discord.Embed(
            title="🏮 THE ARCHIVE: COMMAND MANUAL",
            description="*Paragraphs are for scholars; action is for cultivators.*\n`──────────────────────────────`",
            color=0x7f8c8d
        )

        # 1. General Commands (Available to all)
        gen_cmds = (
            "**!p / !profile** - View your identity.\n"
            "**!s / !status** - Quick status check.\n"
            "**!mantra [text]** - Set your profile bio.\n"
            "**!talents** - View Soul-Root rarities.\n"
            "**!bodies** - View Constitution rarities."
        )
        embed.add_field(name="📜 General Knowledge", value=gen_cmds, inline=False)

        # 2. Path-Specific Commands
        if not data or data['rank'] == 'Mortal':
            mortal_cmds = (
                "**!start** - Bind your soul.\n"
                "**!t / !temper** - Harden your shell (+Progress).\n"
                "**!e / !encounter** - Search for scraps.\n"
                "**!bt / !breakthrough** - Attempt to reach 3rd-rate Warrior."
            )
            embed.add_field(name="🌱 Mortal Path", value=mortal_cmds, inline=False)
        else:
            warrior_cmds = (
                "**!tr / !train** - Build the Body (External Ki).\n"
                "**!b / !breathe** - Build the Soul (Internal Ki).\n"
                "**!e / !encounter** - Hunt for wealth and herbs.\n"
                "**!bt / !breakthrough** - Advance Stages and Realms."
            )
            embed.add_field(name="⚔️ Warrior Path", value=warrior_cmds, inline=False)

        # 3. Economy (The 500:1 Ratio)
        econ_cmds = (
            f"💰 **Rate:** 1 Silver = `{COPPER_TO_SILVER}` Copper\n"
            "🏰 **Family Cost:** `100 Silver`"
        )
        embed.add_field(name="💰 Economy & Lineage", value=econ_cmds, inline=False)

        # 4. Elder Authority (Only for you)
        if await self.bot.is_owner(ctx.author):
            elder_cmds = (
                "**!give_money [type] [amt] [user]**\n"
                "**!pardon [user]** | **!audit [user]**\n"
                "**!set_mantra_other [user] [text]**"
            )
            embed.add_field(name="🏮 Elder Authority", value=elder_cmds, inline=False)

        embed.set_footer(text=f"The Archive recognizes {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(name="talents")
    async def talents_manual(self, ctx):
        """Displays all Soul-Root grades and multipliers."""
        embed = discord.Embed(title="📜 MANUAL OF SOUL-ROOTS", color=0x3498db)
        embed.description = "Your talent determines the speed of your **Internal Ki** gain.\n`──────────────────────────────`"
        
        for name, info in TALENTS.items():
            embed.add_field(
                name=f"{info['grade']} {name}", 
                value=f"Gain Speed: `{info['mult']}x`", 
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="bodies")
    async def bodies_manual(self, ctx):
        """Displays all Constitution grades and multipliers."""
        embed = discord.Embed(title="📜 MANUAL OF CONSTITUTIONS", color=0xe67e22)
        embed.description = "Your body determines your **Combat Power** and **Vessel Capacity**.\n`──────────────────────────────`"
        
        for name, info in CONSTITUTIONS.items():
            val = f"Vessel Size: `{info['v_mod']}x` | Power: `{info['p_mod']}x`"
            embed.add_field(name=f"{info['grade']} {name}", value=val, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Checks the bot's response time."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏮 **Archive Latency:** `{latency}ms`")

async def setup(bot):
    await bot.add_cog(System(bot))