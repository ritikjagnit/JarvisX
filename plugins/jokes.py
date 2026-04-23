import random

jokes = [

    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why did the developer go broke? Because he used up all his cache.",
    "Programmer ne girlfriend se kaha: tum meri WiFi ho, bina tumhare connection hi nahi banta.",
    "Life ek code ki tarah hai — jitna debug karo utni errors milti hain.",
    "I changed my password to incorrect so whenever I forget, it reminds me.",
    "Engineer ka dard: code chal raha ho to dar lagta hai, samajh nahi aata kaise chal raha hai."
]

last_joke = None


def tell_joke():

    global last_joke

    joke = random.choice(jokes)

    while joke == last_joke:
        joke = random.choice(jokes)

    last_joke = joke

    return joke