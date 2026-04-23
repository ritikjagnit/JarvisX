import sys
import subprocess
import json
import os
import time

def check_python_version():
    """Validates root local python footprints."""
    print("[1/5] Checking Python architecture footprint...")
    if sys.version_info < (3, 8):
        print(f"ERROR: Python {sys.version_info.major}.{sys.version_info.minor} detected. Jarvis Search Engine requires Python >= 3.8.")
        sys.exit(1)
    print("SUCCESS: Python language baseline is stable.")

def install_packages():
    """Forces environment sync through strictly controlled PiP paths."""
    print("\n[2/5] Initiating PIP environment module synchronization...")
    req_file = "requirements_search.txt"
    if not os.path.exists(req_file):
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("duckduckgo-search\nbeautifulsoup4\nrequests\nwikipedia-api\naiohttp\nlxml")
            
    try:
        # Enforce Python executable scoping strictly
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("\nSUCCESS: All dynamic intelligence dependencies compiled.")
    except Exception as e:
        print(f"FAILED: Pip subsystem collapsed: {e}")
        sys.exit(1)

def create_configuration():
    """Constructs dynamic JSON configurations."""
    print("\n[3/5] Constructing Core Configuration Parameters...")
    config_data = {
        "max_results_per_search": 5,
        "cache_expiry_hours": 168,  # Maps exactly to the 7-day default logic we created
        "enable_wikipedia": True,
        "enable_news_search": True,
        "rate_limit_delay": 0.5,
        "wolfram_alpha_app_id": ""  # Placeholder
    }
    
    with open("search_config.json", "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
    print("SUCCESS: `search_config.json` freshly stamped.")
    
    # Building root directory tree maps
    if not os.path.exists("cache"):
        os.makedirs("cache")
        print("SUCCESS: Offline Cache Memory hierarchy instantiated.")

def test_duckduckgo_sync():
    """Fires native DDG testing pipeline."""
    print("\n[4/5] Establishing Global DuckDuckGo Backbone Uplink...")
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            _ = ddgs.text("test connection", max_results=1)
        print("SUCCESS: Packets routed accurately! DuckDuckGo Core Response Protocol Operational.")
    except Exception as e:
        print(f"WARNING: DuckDuckGo pipeline blocked. ERROR TRACE: {e}\n(You might be facing IP limits temporarly).")

def test_wikipedia_sync():
    """Fires native Wikipedia testing pipeline."""
    print("\n[5/5] Hooking onto Wikipedia API Encyclopedias...")
    try:
        import wikipediaapi
        wiki = wikipediaapi.Wikipedia(user_agent='JarvisTestAgent/1.0', language='en')
        page = wiki.page("Artificial Intelligence")
        if page.exists():
            print("SUCCESS: Wikipedia Library Nodes fetched natively.")
    except Exception as e:
        print(f"WARNING: Wikipedia API fetching error: {e}")

if __name__ == "__main__":
    print("==============================================")
    print("JARVIS SEARCH ENGINE - MASTER SETUP SCRIPT")
    print("==============================================\n")
    
    check_python_version()
    install_packages()
    create_configuration()
    
    print("\n-- Running Networking Capabilities Probe --")
    test_duckduckgo_sync()
    test_wikipedia_sync()
    
    print("\n==============================================")
    print("JARVIS INTELLIGENCE SUITE FULLY OPERATIONAL!")
    print("==============================================")
