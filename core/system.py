import discord
from discord.ext import commands
import time

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        """A visual guide to the Archive's commands."""
        embed = discord.Embed(
            title="🏮 THE ARCHIVE: COMMAND MANUAL",
            description="*Navigate your path with precision. Paragraphs are for scholars; action is for cultivators.*",
            color=0x7f8c8d
        )

        # Category 1: The Beginning (Mortal)
        mortal_cmds = (
            "**!start** - Bind your soul to the Archive.\n"
            "**!p / !profile** - View your current identity.\n"
            "**!t / !temper** - Strengthen your mortal shell.\n"
            "**!breakthrough** - Shatter your limits (100% progress)."
        )
        embed.add_field(name="🌱 Mortal Path", value=mortal_cmds, inline=False)

        # Category 2: Wealth & Sects
        economy_cmds = (
            "**!bal / !wallet** - Check your Silver and Copper.\n"
            "**!give [user] [amt] [type]** - Transfer wealth.\n"
            "**!f_create [name]** - Establish a Family (1,000 Silver)."
        )
        embed.add_field(name="💰 Economy & Lineage", value=economy_cmds, inline=False)

        # Category 3: System
        system_cmds = (
            "**!help** - Display this manual.\n"
            "**!ping** - Check Archive latency."
        )
        embed.add_field(name="⚙️ System", value=system_cmds, inline=False)

        # Secret Category: Elder (Only shows for Owner)
        if await self.bot.is_owner(ctx.author):
            elder_cmds = (
                "**!add_silver** | **!set_rank**\n"
                "**!set_talent** | **!set_pillar**\n"
                "**!refill** | **!shutdown**"
            )
            embed.add_field(name="🏮 Elder Authority (Owner Only)", value=elder_cmds, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author.name} • Version 1.0")
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Checks the bot's response time."""
        start_time = time.time()
        message = await ctx.send("⌛ *Measuring connection to the Heavens...*")
        end_time = time.time()
        
        latency = round(self.bot.latency * 1000)
        api_speed = round((end_time - start_time) * 1000)
        
        await message.edit(content=f"🏮 **Archive Latency:** `{latency}ms` | **Gate Speed:** `{api_speed}ms`")

async def setup(bot):
    await bot.add_cog(System(bot))
