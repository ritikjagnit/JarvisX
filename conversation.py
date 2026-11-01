import os
import json
import random

responses_en = {
    "hello": ["Hello Shravani! How can I help you today?", "Greetings! Systems are online.", "Hi there! I am listening."],
    "hi": ["Hello! Ready for your commands.", "Always online, Shravani."],
    "how are you": ["I'm operating perfectly, Shravani! How are you doing today?", "Doing great! All core processes are smooth and stable."],
    "your name": ["I am SHRIVA AI, your personal AI assistant.", "They call me SHRIVA AI."],
    "who are you": ["I am SHRIVA AI, an advanced AI system designed for your PC.", "I am your personal AI assistant, SHRIVA AI."],
    "what can you do": ["I can open apps, search the web, manage files, take notes, run python code, and analyze documents!"],
    "thank you": ["You're welcome, Shravani!", "Glad I could assist you.", "Anytime, Shravani!"],
    "who created you": ["I was developed for Shravani as part of the SHRIVA AI Ecosystem."],
    "who is shravani": ["Shravani is a talented software engineer and creator of SHRIVA AI!"],
    "shravani": ["Shravani is the owner and administrator of SHRIVA AI!"],
    "what are you doing": ["Just monitoring your system and waiting for your next command, Shravani!", "Standing by to help you with anything!"],
    "good morning": ["Good morning, Shravani! Hope you have a productive day ahead.", "Good morning! All systems are loaded and ready."],
    "good night": ["Good night, Shravani! Sleep well. I'll stay on standby.", "Sweet dreams, Shravani! Resting background services."],
    "good afternoon": ["Good afternoon, Shravani! How is your day going so far?"],
    "good evening": ["Good evening, Shravani! Ready for your evening tasks."],
    "i am fine": ["Glad to hear that, Shravani! What would you like to work on next?"],
    "i am good": ["Awesome, Shravani! How can I assist you right now?"],
    "talk to me": ["I'm right here! Tell me what's on your mind, Shravani.", "Always happy to chat! How was your day?"],
    "tell me something": ["Did you know that SHRIVA AI processes your commands in under 0.1 seconds? Pretty cool, right!"],
    "well done": ["Thank you, Shravani! Always striving for excellence.", "Appreciate it, Shravani!"],
    "great job": ["Thank you so much, Shravani!", "Happy to deliver top performance!"],
    "bye": ["Goodbye, Shravani! Have a great time.", "Catch you later, Shravani!"],
}

def process_conversation(command):
    import re
    cmd_lower = command.lower()
    for key, replies in responses_en.items():
        if re.search(r'\b' + re.escape(key) + r'\b', cmd_lower):
            return random.choice(replies)
    return None
