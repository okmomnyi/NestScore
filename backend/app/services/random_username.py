import random

ADJECTIVES = [
    "Silent", "Swift", "Bright", "Clever", "Bold", "Calm", "Witty", "Eager",
    "Kind", "Smart", "Brave", "Cool", "Sharp", "Grand", "Fair", "Fast",
    "Deep", "Wild", "Great", "Coy", "Vivid", "Lush", "Sleek", "Daring"
]

NOUNS = [
    "Student", "Scholar", "Nestor", "Resident", "Tenancy", "Mustian",
    "Eagle", "Lion", "Falcon", "Panther", "Wolf", "Owl", "Lynx", "Badger",
    "Otter", "Raven", "Dolphin", "Panda", "Koala", "Tiger", "Fox", "Bear"
]

def generate_random_username() -> str:
    """Generates a random anonymous-style username."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    num = random.randint(100, 999)
    return f"{adj}{noun}{num}"
