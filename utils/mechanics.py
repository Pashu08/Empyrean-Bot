import time
import random

# --- ECONOMY SETTINGS ---
COPPER_TO_SILVER = 500  # The new standard

# --- TALENT & CONSTITUTION DATA ---
# Includes labels for the !talents and !bodies manuals
TALENTS = {
    'Clouded Roots': {'mult': 1.0, 'grade': '⚪ Mortal', 'color': 0x95a5a6},
    'Clear Veins': {'mult': 1.3, 'grade': '🟢 Earth', 'color': 0x2ecc71},
    'Spirit Bone': {'mult': 1.8, 'grade': '🔵 Heaven', 'color': 0x3498db},
    'Heavenly Soul': {'mult': 2.5, 'grade': '🟣 Mystic', 'color': 0x9b59b6},
    'Primordial Heart': {'mult': 4.0, 'grade': '🟡 Saint', 'color': 0xf1c40f},
    'Eternal Dao Body': {'mult': 6.0, 'grade': '🔴 God', 'color': 0xe74c3c}
}

CONSTITUTIONS = {
    'Common Frame': {'v_mod': 1.0, 'p_mod': 1.0, 'grade': '⚪ Common'},
    'Bronze Skin': {'v_mod': 1.2, 'p_mod': 1.0, 'grade': '🟢 Toughened'},
    'Jade Meridians': {'v_mod': 1.0, 'p_mod': 1.5, 'grade': '🔵 Refined'},
    'Sun-Forged Physique': {'v_mod': 2.0, 'p_mod': 1.0, 'grade': '🟣 Heroic'},
    'Asura Bloodline': {'v_mod': 1.0, 'p_mod': 2.5, 'grade': '🟡 Ancient'},
    'Indestructible Vajra': {'v_mod': 3.0, 'p_mod': 3.0, 'grade': '🔴 Eternal'}
}

# --- TWIN PILLAR REQUIREMENTS ---
# Hard gates for External and Internal Ki for each breakthrough
# Format: { 'Major Realm': { 'Next Stage': (Ext Req, Int Req) } }
REQUIREMENTS = {
    'Mortal': {'Third-rate Warrior': (0, 1000)}, # Mortal uses 'Progress' as Int Ki
    'Third-rate Warrior': {
        'Middle': (500, 500), 
        'Late': (1200, 1200), 
        'Peak': (2500, 2500), 
        'Second-rate Warrior': (5000, 5000)
    },
    'Second-rate Warrior': {
        'Middle': (8000, 8000), 
        'Late': (12000, 12000), 
        'Peak': (18000, 18000), 
        'First-rate Warrior': (25000, 25000)
    },
    'First-rate Warrior': {
        'Middle': (35000, 35000), 
        'Late': (50000, 50000), 
        'Peak': (70000, 70000), 
        'Peak Warrior': (100000, 100000)
    },
    'Peak Warrior': {
        'Middle': (150000, 150000), 
        'Late': (220000, 220000), 
        'Peak': (300000, 300000), 
        'Master': (500000, 500000)
    },
    'Master': {
        'Middle': (750000, 750000), 
        'Late': (1000000, 1000000), 
        'Peak': (1500000, 1500000), 
        'Grandmaster': (2500000, 2500000)
    },
    'Grandmaster': {
        'Middle': (5000000, 5000000), 
        'Late': (10000000, 10000000), 
        'Peak': (20000000, 20000000), 
        'Transcendent Realm': (50000000, 50000000)
    }
}

# --- BREAKTHROUGH CHANCES ---
CHANCES = {
    'Third-rate Warrior': 90,
    'Second-rate Warrior': 70,
    'First-rate Warrior': 50,
    'Peak Warrior': 30,
    'Master': 15,
    'Grandmaster': 5,
    'Transcendent Realm': 1
}

# --- CALCULATIONS ---

def calculate_cp(rank, internal, external, con_name):
    """Calculates Combat Power based on Pillars and Constitution (Whole Numbers)."""
    if rank == 'Mortal':
        return int(internal / 10) # Simple CP for mortals
    
    # Warriors get a boost from Constitution
    base_cp = (internal * 1) + (external * 1.5)
    cp_mult = CONSTITUTIONS.get(con_name, {}).get('p_mod', 1.0)
    return int(base_cp * cp_mult)

def calculate_energy_refill(current, max_val, last_updated):
    """Refills 1 Energy per minute (Whole Numbers)."""
    now = int(time.time())
    if last_updated == 0:
        return int(current), now
    
    seconds_passed = now - last_updated
    refill = seconds_passed // 60
    return int(min(max_val, current + refill)), now

def get_vessel_limit(rank, stage, con_name):
    """Vessel capacity is determined by the CURRENT rank requirement + Constitution."""
    if rank == 'Mortal':
        return 100
    
    # Find the requirement for the current stage to set the limit
    # If they are 'Initial', their limit is the 'Middle' requirement
    req_data = REQUIREMENTS.get(rank, {})
    next_stage_map = {'Initial': 'Middle', 'Middle': 'Late', 'Late': 'Peak', 'Peak': 'Next Rank'}
    
    # Default to a base if something goes wrong
    base_cap = 1000 
    
    target = next_stage_map.get(stage, 'Middle')
    if target in req_data:
        base_cap = req_data[target][1] # Use the Internal Ki req as base cap
    
    mod = CONSTITUTIONS.get(con_name, {}).get('v_mod', 1.0)
    return int(base_cap * mod)
