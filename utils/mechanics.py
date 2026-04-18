import time

# --- TALENT & CONSTITUTION DATA ---

TALENTS = {
    'Clouded Roots': {'multiplier': 1.0},
    'Clear Veins': {'multiplier': 1.3},
    'Spirit Bone': {'multiplier': 1.8},
    'Heavenly Soul': {'multiplier': 2.5},
    'Primordial Heart': {'multiplier': 4.0},
    'Eternal Dao Body': {'multiplier': 6.0}
}

CONSTITUTIONS = {
    'Common Frame': {'vessel_mod': 1.0, 'cp_mod': 1.0},
    'Bronze Skin': {'vessel_mod': 1.2, 'cp_mod': 1.0},
    'Jade Meridians': {'vessel_mod': 1.0, 'cp_mod': 1.5},
    'Sun-Forged Physique': {'vessel_mod': 2.0, 'cp_mod': 1.0},
    'Asura Bloodline': {'vessel_mod': 1.0, 'cp_mod': 2.5},
    'Indestructible Vajra': {'vessel_mod': 3.0, 'cp_mod': 3.0}
}

# --- CALCULATIONS ---

def calculate_ki_gain(current_ki, last_updated, rank, talent_name, vessel_cap):
    """Calculates how much Ki a player gained while AFK."""
    now = int(time.time())
    if last_updated == 0:
        return current_ki, now

    seconds_passed = now - last_updated
    # Base gain: 1 Ki per minute (approx 0.016 per second)
    base_rate = 0.0166 

    # Determine Multiplier (Locked to 1.0 for Mortals)
    multiplier = 1.0
    if rank != 'Mortal':
        multiplier = TALENTS.get(talent_name, {}).get('multiplier', 1.0)

    gained_ki = seconds_passed * base_rate * multiplier
    new_ki = current_ki + gained_ki

    # VESSEL LEAK LOGIC
    # If Ki exceeds the Vessel Capacity, it stops growing (or you could add a penalty)
    if new_ki > vessel_cap:
        new_ki = vessel_cap
    
    return round(new_ki, 2), now

def calculate_cp(rank, ki_density, ki_control, constitution_name):
    """Calculates Combat Power based on pillars and constitution."""
    # Base CP from pillars
    base_cp = (ki_density * 50) + (ki_control * 50)
    
    # Constitution Modifier (Locked to 1.0 for Mortals)
    cp_mult = 1.0
    if rank != 'Mortal':
        cp_mult = CONSTITUTIONS.get(constitution_name, {}).get('cp_mod', 1.0)
    
    return round(base_cp * cp_mult)

def calculate_vessel_limit(base_cap, constitution_name, rank):
    """Calculates the maximum Ki a player can hold."""
    if rank == 'Mortal':
        return 100 # Mortals have a tiny, fixed vessel
    
    mod = CONSTITUTIONS.get(constitution_name, {}).get('vessel_mod', 1.0)
    return int(base_cap * mod)

# --- ENERGY REFILL (For !temper command) ---

def calculate_energy_refill(current_energy, max_energy, last_updated):
    """Simple refill for the Mortal energy used in !temper."""
    now = int(time.time())
    if last_updated == 0:
        return current_energy, now
    
    # Refill 10 energy every 10 minutes (1 per minute)
    seconds_passed = now - last_updated
    refill_amount = seconds_passed * (10 / 600)
    
    new_energy = min(max_energy, current_energy + refill_amount)
    return round(new_energy, 2), now
