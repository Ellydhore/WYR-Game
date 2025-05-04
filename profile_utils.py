import random

def generate_random_avatar_url(username_seed=None):
    seed = username_seed if username_seed else str(random.randint(1, 10000))
    return f"https://api.dicebear.com/9.x/dylan/svg?seed={seed}"
