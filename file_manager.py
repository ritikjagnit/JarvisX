import os
import glob
import time

TARGET_DIRS = [
    os.path.join(os.path.expanduser('~'), 'Documents'),
    os.path.join(os.path.expanduser('~'), 'Desktop'),
    os.path.join(os.path.expanduser('~'), 'Downloads')
]

def find_latest_file(ext=None):
    files = []
    for d in TARGET_DIRS:
        if not os.path.exists(d): continue
        if ext:
            search_pattern = os.path.join(d, f"*{ext}")
        else:
            search_pattern = os.path.join(d, "*")
        files.extend([f for f in glob.glob(search_pattern) if os.path.isfile(f) and not f.endswith('crdownload')])
    
    if not files: return None
    return max(files, key=os.path.getctime)

def process_file_command(command):
    print(f"[DEBUG-FILE] File Manager evaluating command: {command}")

    # 1. Open Last Downloaded or Latest File System
    if "last download" in command or "recent download" in command:
        print("[DEBUG-FILE] Searching for latest global downloaded content...")
        latest = find_latest_file()
        if latest:
            os.startfile(latest)
            return f"Opening most recent file: {os.path.basename(latest)}"
        return "No recent files found in common directories."

    # 2. File search by partial name / Extension
    if "open file" in command or "find file" in command:
        query = command.replace("open file", "").replace("find file", "").strip()
        print(f"[DEBUG-FILE] Attempting deep search for file partially matching '{query}'")
        
        matches = []
        for d in TARGET_DIRS:
            if not os.path.exists(d): continue
            for root, dirs, files in os.walk(d):
                for f in files:
                    # Case insensitive partial match
                    if query.lower() in f.lower():
                        matches.append(os.path.join(root, f))
        
        if matches:
            # If multiple matching files exist, open the most recently updated one
            best_match = max(matches, key=os.path.getmtime)
            os.startfile(best_match)
            return f"Found and opening: {os.path.basename(best_match)}"
        else:
            return f"Could not find any file resembling {query}."

    return None
