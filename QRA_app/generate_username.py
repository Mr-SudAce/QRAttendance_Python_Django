import random
from QRA_app.models import User


def generate_username(first_name=None, last_name=None):
    first = (first_name or "").lower()
    last = (last_name or "").lower()
    random_nums = random.randint(100, 999)

    base_options = [
        f"{first}-{last}",
        f"{last}-{first}",
        f"{first}_{last}",
        f"{last}_{first}",
    ]

    for _ in range(10):
        base = random.choice(base_options)
        number = random_nums
        username = f"{base}{number}"

        if not User.objects.filter(username=username).exists():
            return username

    return f"{first}{last}{random_nums}"
