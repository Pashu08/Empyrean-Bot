import discord
from discord.ext import commands
import time
import random
from utils.database import get_player_data, update_val, adjust_val
from utils.mechanics import (
    calculate_energy_refill, 
    REQUIREMENTS, 
    CHANCES, 
    TALENTS, 
    CONSTITUTIONS,
    get_vessel_limit
)

class WarriorCultivation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_bar(self, current, max_val, color_emoji="🟩"):
        """Creates a visual progress bar."""
        if max_val <= 0: return "⬜" * 10
        filled = int((current / max_val) * 10)
        bar = color_emoji * min(filled, 10) + "⬜" * max(0, (10 - filled))
        return f"{bar} `{int(current)}/{int(max_val)}`"

    @commands.command(name="train", aliases=['tr'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def train(self, ctx):
        """Builds External Ki (The Vessel/Container)."""
        user_id = ctx.author.id
        data = get_player_data(user_id)

        if not data or data['rank'] == 'Mortal':
            return await ctx.send("🏮 **NOTICE:** Mortals must use `!temper`. Only Warriors can perform high-level training.")

        # Energy Check
        current_energy, _ = calculate_energy_refill(data['energy_current'], data['energy_max'], data['last_updated'])
        if current_energy < 25:
            return await ctx.send("⚠️ Training your physical shell requires `25 Energy`.")

        # Calculation
        con_mult = CONSTITUTIONS.get(data['constitution'], {}).get('v_mod', 1.0)
        gain = int(random.randint(15, 30) * con_mult)
        
        new_ext = data['external_ki'] + gain
        now = int(time.time())

        update_val(user_id, 'external_ki', new_ext)
        update_val(user_id, 'energy_current', current_energy - 25)
        update_val(user_id, 'last_updated', now)

        embed = discord.Embed(title="🥋 PHYSICAL TRAINING", color=0x3498db)
        embed.description = f"You pushed your body to the limit.\n**Gain:** `+{gain} External Ki`"
        embed.add_field(name="💪 External Ki (Body)", value=f"`{new_ext}`", inline=True)
        embed.add_field(name="⚡ Energy", value=f"`{current_energy - 25}/{data['energy_max']}`", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="breathe", aliases=['b'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def breathe(self, ctx):
        """Builds Internal Ki (The Essence/Water)."""
        user_id = ctx.author.id
        data = get_player_data(user_id)

        if not data or data['rank'] == 'Mortal':
            return await ctx.send("🏮 **NOTICE:** You haven't sensed Ki yet. Temper your body first.")

        # Energy Check
        current_energy, _ = calculate_energy_refill(data['energy_current'], data['energy_max'], data['last_updated'])
        if current_energy < 25:
            return await ctx.send("⚠️ Deep breathing requires `25 Energy`.")

        # Vessel Check (Can't breathe more than body can hold)
        vessel = get_vessel_limit(data['rank'], data['stage'], data['constitution'])
        if data['internal_ki'] >= vessel:
            return await ctx.send(f"🏮 **VESSEL FULL:** Your body cannot hold more Ki. `!train` or `!breakthrough`.")

        # Calculation
        talent_mult = TALENTS.get(data['talent'], {}).get('mult', 1.0)
        gain = int(random.randint(15, 30) * talent_mult)
        
        new_int = min(vessel, data['internal_ki'] + gain)
        now = int(time.time())

        update_val(user_id, 'internal_ki', new_int)
        update_val(user_id, 'energy_current', current_energy - 25)
        update_val(user_id, 'last_updated', now)

        embed = discord.Embed(title="🧘 MEDITATIVE BREATHING", color=0x9b59b6)
        embed.description = f"You circulated Ki through your meridians.\n**Gain:** `+{gain} Internal Ki`"
        embed.add_field(name="✨ Internal Ki (Soul)", value=self.get_bar(new_int, vessel, "🟦"), inline=False)
        embed.add_field(name="⚡ Energy", value=f"`{current_energy - 25}/{data['energy_max']}`", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="breakthrough", aliases=['bt'])
    async def breakthrough(self, ctx):
        """Attempts to move to the next Stage or Realm."""
        user_id = ctx.author.id
        data = get_player_data(user_id)
        if not data: return

        rank = data['rank']
        stage = data['stage']
        
        # --- FIX: Mortal vs Warrior Logic Split ---
        if rank == 'Mortal':
            target_rank = 'Third-rate Warrior'
            req_ext, req_int = REQUIREMENTS['Mortal'][target_rank]
            # Mortals use 'progress' as their internal measurement
            current_internal = data['progress']
            current_external = 0 
            display_target = target_rank
            is_major = True
        else:
            # Warrior Stage Logic
            stage_map = {'Initial': 'Middle', 'Middle': 'Late', 'Late': 'Peak', 'Peak': 'Next Rank'}
            target = stage_map.get(stage, 'Middle')
            current_internal = data['internal_ki']
            current_external = data['external_ki']
            
            if target == 'Next Rank':
                realm_list = list(REQUIREMENTS.keys())
                current_idx = realm_list.index(rank)
                if current_idx + 1 >= len(realm_list):
                    return await ctx.send("🌌 You have reached the apex of the Transcendent Realm.")
                target_rank = realm_list[current_idx + 1]
                req_ext, req_int = REQUIREMENTS[rank][target_rank]
                display_target = target_rank
                is_major = True
            else:
                req_ext, req_int = REQUIREMENTS[rank][target]
                display_target = f"{rank} ({target})"
                is_major = False

        # --- Check Requirements ---
        if current_external < req_ext or current_internal < req_int:
            return await ctx.send(
                f"❌ **THE HEAVENS REJECT YOU:**\n"
                f"Requirements for `{display_target}`:\n"
                f"• Body (Ext): `{current_external}/{req_ext}`\n"
                f"• Soul (Int): `{current_internal}/{req_int}`"
            )

        # --- Success Roll ---
        chance = CHANCES.get(rank, 50)
        roll = random.randint(1, 100)

        if roll <= chance:
            if rank == 'Mortal':
                update_val(user_id, 'rank', 'Third-rate Warrior')
                update_val(user_id, 'stage', 'Initial')
                update_val(user_id, 'progress', 0)
                update_val(user_id, 'internal_ki', 0) # Initialize Ki
                msg = f"🎊 **AWAKENING!** You have stepped into the **Third-rate Warrior** realm!"
            elif is_major:
                update_val(user_id, 'rank', target_rank)
                update_val(user_id, 'stage', 'Initial')
                msg = f"🎊 **ASCENSION!** Welcome to the **{target_rank}** realm!"
            else:
                update_val(user_id, 'stage', target)
                msg = f"✨ **SUCCESS!** You have reached the **{target} Stage**."
            
            # Auto-update Vessel Capacity for the new stage
            new_vessel = get_vessel_limit(
                target_rank if is_major else rank, 
                'Initial' if is_major else target, 
                data['constitution']
            )
            update_val(user_id, 'vessel_cap', new_vessel)
            color = 0x2ecc71
        else:
            # Failure Penalty (30% loss)
            penalty_ext = int(data['external_ki'] * 0.7)
            penalty_int = int(data['internal_ki'] * 0.7) if rank != 'Mortal' else int(data['progress'] * 0.7)
            
            if rank == 'Mortal':
                update_val(user_id, 'progress', penalty_int)
            else:
                update_val(user_id, 'external_ki', penalty_ext)
                update_val(user_id, 'internal_ki', penalty_int)
            
            msg = f"💥 **MERIDIAN COLLAPSE!** The breakthrough failed. You lost 30% of your Ki in the backlash."
            color = 0xe74c3c

        embed = discord.Embed(title="⚡ BREAKTHROUGH ATTEMPT", description=msg, color=color)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WarriorCultivation(bot))