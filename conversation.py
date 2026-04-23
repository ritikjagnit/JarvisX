import random

responses = {
    "hello": ["Hello Boss! How can I help you today?", "Greetings! Systems are online.", "Hi there! I am listening."],
    "hi jarvis": ["Hello! Ready for your commands.", "Always online, Boss."],
    "how are you": ["I'm operating perfectly. And you?", "Doing well! All background processes are stable."],
    "your name": ["I am Jarvis, your personal offline AI assistant.", "They call me Jarvis."],
    "who are you": ["I am Jarvis, an advanced AI system designed for your personal computer. I handle everything from system control to complex automation.", "I am your personal AI assistant, Jarvis."],
    "what can you do": ["I can open your apps, search the web, manage your files, remember your preferences, take notes, and multitask completely offline!"],
    "thank you": ["You're welcome, Boss.", "Glad I could assist you.", "Anytime!"],
    "who created you": ["I was developed by Ritik as part of the Jarvis Project.", "My architecture was designed by my Boss."],
}

def process_conversation(command):
    for key, replies in responses.items():
        if key in command:
            return random.choice(replies)
    return None
