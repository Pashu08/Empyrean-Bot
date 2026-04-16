import discord
from discord.ext import commands
import sqlite3
import time

class Foundation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # [ UTILITY: KI REGEN CALCULATOR ]
    # ==========================================
    def get_refilled_energy(self, current_energy, max_energy, last_time):
        now = int(time.time())
        if last_time == 0: return current_energy, now
        minutes_passed = (now - last_time) // 60
        if minutes_passed >= 1:
            regained = minutes_passed * 2
            return min(current_energy + regained, max_energy), now
        return current_energy, last_time

    # ==========================================
    # [ CORE ACTION: SOUL AWAKENING ]
    # ==========================================
    @commands.command(name="start")
    async def start(self, ctx):
        user_id = ctx.author.id
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        
        if cursor.fetchone():
            # Cinematic Welcome Back
            embed = discord.Embed(title="✨ ARCHIVE RECOGNITION", color=0x3498db)
            embed.description = "The Archive hums as it recognizes your soul. Your foundation is already set, Cultivator."
            embed.set_footer(text="Seek progress via !p or !temper.")
            await ctx.send(embed=embed)
        else:
            now = int(time.time())
            # Initialize user with 50 Ki
            cursor.execute("INSERT INTO users (user_id, last_updated, energy_current) VALUES (?, ?, 50)", (user_id, now))
            conn.commit()
            
            embed = discord.Embed(
                title="📜 ARCHIVE DATA: SOUL RECOGNIZED",
                color=0xC0C0C0 
            )
            embed.add_field(name="👤 Subject", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="💠 Foundation", value="`Mortal Root`", inline=True)
            embed.add_field(name="✨ Status", value="`Active / Unwritten`", inline=True)
            
            embed.add_field(
                name="⚔️ Guidance", 
                value="The Great Void has recorded your name. Your path is your own to carve.", 
                inline=False
            )
            
            embed.set_footer(text="Type !temper to begin your first refinement.")
            await ctx.send(embed=embed)
        conn.close()

    # ==========================================
    # [ CORE ACTION: CULTIVATOR PROFILE ]
    # ==========================================
    @commands.command(name="p", aliases=['profile'])
    async def profile(self, ctx):
        user_id = ctx.author.id
        conn = sqlite3.connect('cultivation.db')
        cursor = conn.cursor()
        cursor.execute('SELECT rank, progress, energy_current, energy_max, last_updated FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            await ctx.send("❌ **Your presence is not recorded. Type `!start` to begin.**")
            conn.close()
            return

        rank, prog, old_e, max_e, l_time = user
        cur_e, new_time = self.get_refilled_energy(old_e, max_e, l_time)
        
        cursor.execute('UPDATE users SET energy_current = ?, last_updated = ? WHERE user_id = ?', (cur_e, new_time, user_id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="💎 CULTIVATOR STATUS: RECORDED", 
            color=0xC0C0C0 
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        embed.add_field(name="👤 Identity", value=f"{ctx.author.mention}", inline=True)
        embed.add_field(name="💠 Foundation", value=f"`{rank}`", inline=True)
        embed.add_field(name="📈 Progress", value=f"`{prog}%` to Next Rank", inline=False)
        
        # --- ULTRA-COMPACT MOBILE KI BAR (6 Blocks) ---
        # Using 6 blocks and diamond emojis ensures this stays on one line
        blocks = int((cur_e / max_e) * 6)
        bar = "🔹" * blocks + "🔸" * (6 - blocks)
        
        embed.add_field(name="⚡ Ki Reserve", value=f"{bar} `{cur_e}/{max_e}`", inline=False)
        
        embed.set_footer(text="The Archive tracks all. Refine your soul.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Foundation(bot))
