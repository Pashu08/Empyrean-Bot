import time

def calculate_ki_refill(current_ki, max_ki, last_time):
    now = int(time.time())
    if last_time == 0 or last_time is None: 
        return current_ki, now
        
    minutes_passed = (now - last_time) // 60
    if minutes_passed >= 1:
        # One central place to change refill speed!
        regained = minutes_passed * 2 
        return min(current_ki + regained, max_ki), now
        
    return current_ki, last_time
