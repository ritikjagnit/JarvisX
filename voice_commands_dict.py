"""
JARVIS COMPREHENSIVE VOICE COMMAND DICTIONARY
Contains ~50 intensive regex-mapped routing capabilities for natural language interpretation.
"""

import re

# Dummy Handler Registrations (Wire these strictly to your JarvisWebSearch module!)
def handle_general_search(query): return "Executing Search..."
def handle_question(query): return "Extracting QA Synthesis..."
def handle_news_search(query): return "Fetching Articles..."
def handle_definition(query): return "Scanning Definitions..."
def handle_wikipedia(query): return "Downloading Wiki Data..."
def handle_calculation(query): return "Crunching Numbers..."
def handle_time_date(query): return "Inspecting Clock Constraints..."
def handle_weather(query): return "Checking Satellite Feeds via wttr.in..."


JARVIS_COMMAND_ROUTER = {
    
    # ==========================================================
    # 1. GENERAL WEB SEARCH PATTERNS
    # ==========================================================
    "search_01": {
        "command_pattern": r"^search for (.*)",
        "handler_function": handle_general_search,
        "response_template": "Here are the top web results for {query}: {result}",
        "examples": ["search for quantum computing advancements", "search for the best python libraries"]
    },
    "search_02": {
        "command_pattern": r"^find information about (.*)",
        "handler_function": handle_general_search,
        "response_template": "I located the following information regarding {query}: {result}",
        "examples": ["find information about artificial general intelligence"]
    },
    "search_03": {
        "command_pattern": r"^look up (.*)",
        "handler_function": handle_general_search,
        "response_template": "Looking up details on {query}. Based on web analytics: {result}",
        "examples": ["look up the lifespan of a sea turtle"]
    },
    "search_04": {
        "command_pattern": r"^get me details on (.*)",
        "handler_function": handle_general_search,
        "response_template": "Retrieving details for {query}... {result}",
        "examples": ["get me details on the new tesla model"]
    },
    "search_05": {
        "command_pattern": r"^can you search (.*)",
        "handler_function": handle_general_search,
        "response_template": "Certainly. My search indicates that {query} {result}",
        "examples": ["can you search black box testing"]
    },

    # ==========================================================
    # 2. QUESTION & ANSWER PATTERNS
    # ==========================================================
    "question_who_01": {
        "command_pattern": r"^who is (.*)",
        "handler_function": handle_question,
        "response_template": "{query} is defined as {result}",
        "examples": ["who is adele", "who is the current prime minister"]
    },
    "question_who_02": {
        "command_pattern": r"^who was (.*)",
        "handler_function": handle_question,
        "response_template": "Historically, {query} was {result}",
        "examples": ["who was albert einstein"]
    },
    "question_what_01": {
        "command_pattern": r"^what is (.*)",
        "handler_function": handle_question,
        "response_template": "According to my synthesis, {query} is {result}",
        "examples": ["what is an LLM", "what is the capital of Japan"]
    },
    "question_how_01": {
        "command_pattern": r"^how to (.*)",
        "handler_function": handle_question,
        "response_template": "To {query}, you generally follow these steps: {result}",
        "examples": ["how to bake a cake", "how to install windows"]
    },
    "question_how_many_01": {
        "command_pattern": r"^how many (.*)",
        "handler_function": handle_question,
        "response_template": "Regarding how many {query}, the answer is {result}",
        "examples": ["how many planets are in the solar system"]
    },
    "question_when_01": {
        "command_pattern": r"^when did (.*)",
        "handler_function": handle_question,
        "response_template": "The event '{query}' occurred in {result}",
        "examples": ["when did world war two begin"]
    },
    "question_where_01": {
        "command_pattern": r"^where is (.*)",
        "handler_function": handle_question,
        "response_template": "{query} is located at {result}",
        "examples": ["where is the burj khalifa"]
    },
    "question_why_01": {
        "command_pattern": r"^why do (.*)",
        "handler_function": handle_question,
        "response_template": "Many sources explain that {query} because {result}",
        "examples": ["why do cats purr"]
    },

    # ==========================================================
    # 3. NEWS & CURRENT EVENTS PATTERNS
    # ==========================================================
    "news_01": {
        "command_pattern": r"^latest news about (.*)",
        "handler_function": handle_news_search,
        "response_template": "Here are the essential headlines regarding {query}: {result}",
        "examples": ["latest news about stock markets"]
    },
    "news_02": {
        "command_pattern": r"^what's happening in (.*)",
        "handler_function": handle_news_search,
        "response_template": "Recent events unfolding in {query} include: {result}",
        "examples": ["what's happening in europe"]
    },
    "news_03": {
        "command_pattern": r"^any news on (.*)",
        "handler_function": handle_news_search,
        "response_template": "Yes, I filtered recent publications. On the topic of {query}, {result}",
        "examples": ["any news on SpaceX"]
    },
    "news_04": {
        "command_pattern": r"^tell me the news",
        "handler_function": handle_news_search,
        "response_template": "Here is your global executive news briefing: {result}",
        "examples": ["tell me the news"]
    },
    "news_05": {
        "command_pattern": r"^recent updates on (.*)",
        "handler_function": handle_news_search,
        "response_template": "Looking through rapid updates on {query}, I found: {result}",
        "examples": ["recent updates on the olympics"]
    },

    # ==========================================================
    # 4. DEFINITIONS & DICTIONARY PATTERNS
    # ==========================================================
    "def_01": {
        "command_pattern": r"^define (.*)",
        "handler_function": handle_definition,
        "response_template": "The grammatical definition of {query} is: {result}",
        "examples": ["define soliloquy", "define quantum mechanics"]
    },
    "def_02": {
        "command_pattern": r"^meaning of (.*)",
        "handler_function": handle_definition,
        "response_template": "In most contexts, the meaning of '{query}' relates to {result}",
        "examples": ["meaning of dichotomy"]
    },
    "def_03": {
        "command_pattern": r"^what does (.*) mean",
        "handler_function": handle_definition,
        "response_template": "The term '{query}' translates to: {result}",
        "examples": ["what does proactive mean"]
    },
    "def_04": {
        "command_pattern": r"^synonym for (.*)",
        "handler_function": handle_definition,
        "response_template": "Similar words to '{query}' include: {result}",
        "examples": ["synonym for excellent"]
    },
    "def_05": {
        "command_pattern": r"^antonym of (.*)",
        "handler_function": handle_definition,
        "response_template": "Direct opposites of '{query}' are: {result}",
        "examples": ["antonym of optimistic"]
    },

    # ==========================================================
    # 5. WIKIPEDIA / DEEP ENCYCLOPEDIA PATTERNS
    # ==========================================================
    "wiki_01": {
        "command_pattern": r"^wiki (.*)",
        "handler_function": handle_wikipedia,
        "response_template": "Pulling encyclopedic data... {result}",
        "examples": ["wiki albert einstein"]
    },
    "wiki_02": {
        "command_pattern": r"^tell me about (.*)",
        "handler_function": handle_wikipedia,
        "response_template": "Here is a brief biographical/historical summary of {query}: {result}",
        "examples": ["tell me about the roman empire"]
    },
    "wiki_03": {
        "command_pattern": r"^who exactly is (.*)",
        "handler_function": handle_wikipedia,
        "response_template": "Diving deep... {query} is widely recognized as {result}",
        "examples": ["who exactly is leonardo da vinci"]
    },
    "wiki_04": {
        "command_pattern": r"^history of (.*)",
        "handler_function": handle_wikipedia,
        "response_template": "The extensive history surrounding {query} outlines that {result}",
        "examples": ["history of coffee"]
    },

    # ==========================================================
    # 6. CALCULATIONS / MATHEMATICS / WOLFRAM
    # ==========================================================
    "math_01": {
        "command_pattern": r"^calculate (.*)",
        "handler_function": handle_calculation,
        "response_template": "The numerical calculation for {query} resolves to: {result}",
        "examples": ["calculate 450 divided by 30"]
    },
    "math_02": {
        "command_pattern": r"^what is (\d+.*)",
        "handler_function": handle_calculation,
        "response_template": "Computing math syntax... The result is {result}",
        "examples": ["what is 2 + 2", "what is 50 percent of 1000"]
    },
    "math_03": {
        "command_pattern": r"^square root of (.*)",
        "handler_function": handle_calculation,
        "response_template": "The mathematical square root of {query} is {result}",
        "examples": ["square root of 144"]
    },
    "math_04": {
        "command_pattern": r"^solve this math (.*)",
        "handler_function": handle_calculation,
        "response_template": "Processing equation {query}... the solution is {result}",
        "examples": ["solve this math 15 * 6"]
    },
    "math_05": {
        "command_pattern": r"^convert (.*) to (.*)",
        "handler_function": handle_calculation,
        "response_template": "Mathematical Conversion: {query} translates directly into {result}",
        "examples": ["convert 100 kilometers to miles"]
    },

    # ==========================================================
    # 7. TIME & DATE PROTOCOLS
    # ==========================================================
    "time_01": {
        "command_pattern": r"^what time is it",
        "handler_function": handle_time_date,
        "response_template": "The current established time is {result}",
        "examples": ["what time is it"]
    },
    "time_02": {
        "command_pattern": r"^today's date",
        "handler_function": handle_time_date,
        "response_template": "For your records, today's date is {result}",
        "examples": ["today's date"]
    },
    "time_03": {
        "command_pattern": r"^what day is it",
        "handler_function": handle_time_date,
        "response_template": "Today's calendar day is {result}",
        "examples": ["what day is it"]
    },
    "time_04": {
        "command_pattern": r"^current time in (.*)",
        "handler_function": handle_time_date,
        "response_template": "Cross-checking local timezones... it is currently {result} in {query}",
        "examples": ["current time in London"]
    },
    "time_05": {
        "command_pattern": r"^how many days until (.*)",
        "handler_function": handle_time_date,
        "response_template": "Calculating calendar discrepancies... {query} is {result} days away.",
        "examples": ["how many days until Christmas"]
    },

    # ==========================================================
    # 8. WEATHER FORECASTING API (Using free endpoints logic)
    # ==========================================================
    "weather_01": {
        "command_pattern": r"^weather in (.*)",
        "handler_function": handle_weather,
        "response_template": "Scanning radar metrics for {query}... The current climate reads {result}",
        "examples": ["weather in Tokyo"]
    },
    "weather_02": {
        "command_pattern": r"^what's the weather like",
        "handler_function": handle_weather,
        "response_template": "Looking outside locally... {result}",
        "examples": ["what's the weather like"]
    },
    "weather_03": {
        "command_pattern": r"^is it going to rain in (.*)",
        "handler_function": handle_weather,
        "response_template": "Atmospheric predictions for {query} state that {result}",
        "examples": ["is it going to rain in seattle"]
    },
    "weather_04": {
        "command_pattern": r"^temperature in (.*)",
        "handler_function": handle_weather,
        "response_template": "Thermal mapping of {query} displays {result}",
        "examples": ["temperature in dubai"]
    },
    "weather_05": {
        "command_pattern": r"^humidity in (.*)",
        "handler_function": handle_weather,
        "response_template": "The humidity metric for {query} is reading at {result}",
        "examples": ["humidity in miami"]
    }
}

# ==========================================================
# PARSER UTILITY FUNCTION
# ==========================================================
def identify_and_route_command(voice_input: str) -> dict:
    """
    Sweeps vertically through the 50 definitions to trap incoming intent dynamically.
    Returns the mapped module payload or None.
    """
    cleaned_input = voice_input.lower().strip()
    
    for command_id, metrics in JARVIS_COMMAND_ROUTER.items():
        pattern = metrics["command_pattern"]
        matched = re.search(pattern, cleaned_input)
        
        if matched:
            query_arg = ""
            # Safely grab the first capturing group if it exists
            if matched.groups():
                query_arg = matched.group(1).strip()
                
            return {
                "id": command_id,
                "handler": metrics["handler_function"],
                "template": metrics["response_template"],
                "target_query": query_arg,
                "original_voice": voice_input
            }
            
    return None

if __name__ == "__main__":
    # Internal Unit Test Engine
    print("Testing Regex Capabilities Against Voice Routings...\n")
    
    tests = [
        "what is 150 times 10",
        "latest news about quantum technology",
        "define cognitive dissonance",
        "weather in New York"
    ]
    
    for t in tests:
        identified = identify_and_route_command(t)
        if identified:
            mock_result = identified["handler"](identified["target_query"])
            final_tts_block = identified["template"].format(query=identified["target_query"], result=mock_result)
            print(f"User:   {t}\nJarvis: {final_tts_block}\n")
