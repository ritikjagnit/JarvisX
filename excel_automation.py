import os
import time
import openpyxl
from voice_engine import speak

# Global state to keep track of the current in-memory workbook/worksheet/file path
_active_workbook = None
_active_worksheet = None
_active_filepath = None

def get_most_recent_excel_file():
    """Finds the most recently modified .xlsx file in Downloads, Desktop, or Documents."""
    user_home = os.path.expanduser("~")
    dirs_to_check = [
        os.path.join(user_home, "Downloads"),
        os.path.join(user_home, "Desktop"),
        os.path.join(user_home, "Documents")
    ]
    
    newest_file = None
    newest_time = 0
    
    for d in dirs_to_check:
        if not os.path.exists(d):
            continue
        try:
            for entry in os.scandir(d):
                if entry.is_file() and entry.name.endswith(".xlsx") and not entry.name.startswith("~$"):
                    mtime = entry.stat().st_mtime
                    if mtime > newest_time:
                        newest_time = mtime
                        newest_file = entry.path
        except Exception as e:
            print(f"[Excel] Error scanning directory {d}: {e}")
            
    return newest_file

def create_new_workbook():
    """Creates a new in-memory Excel workbook."""
    global _active_workbook, _active_worksheet, _active_filepath
    _active_workbook = openpyxl.Workbook()
    _active_worksheet = _active_workbook.active
    _active_worksheet.title = "Sheet1"
    _active_filepath = None
    print("[Excel] Created a new in-memory workbook.")
    return "Created a new Excel workbook in memory. You can add rows or save it now."

def add_row_to_active(data_str):
    """Appends a row of data (comma-separated or parsed) to the active worksheet."""
    global _active_workbook, _active_worksheet
    if _active_workbook is None or _active_worksheet is None:
        # Auto-create workbook if none exists
        create_new_workbook()
        
    # Clean trailing Hindi verbs/speech artifacts
    for suffix in [" likh do", " likho", " dal do", " daal do", " kro", " karo"]:
        if data_str.lower().endswith(suffix):
            data_str = data_str[:-len(suffix)].strip()
            
    # Clean up voice recognition digit-comma artifacts (e.g. "12,000" -> "12000")
    import re
    data_str = re.sub(r'(\d),(\d)', r'\1\2', data_str)
    
    # Split by comma or space if no commas
    if "," in data_str:
        row_data = [item.strip() for item in data_str.split(",")]
    else:
        row_data = [item.strip() for item in data_str.split()]
        
    # Append row
    _active_worksheet.append(row_data)
    row_desc = ", ".join(map(str, row_data))
    return f"Successfully added row: {row_desc} to the active sheet."

def save_active_workbook(filename=None):
    """Saves the active workbook to the user's Documents folder and opens it."""
    global _active_workbook, _active_worksheet, _active_filepath
    if _active_workbook is None:
        return "Shravani, there is no active Excel workbook to save. Speak 'Create Excel' first."

        
    try:
        docs_dir = os.path.join(os.path.expanduser("~"), "Documents", "Jarvis_Excel_Output")
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            
        if not filename:
            filename = f"jarvis_sheet_{int(time.time())}.xlsx"
        else:
            filename = filename.strip()
            if not filename.endswith(".xlsx"):
                filename += ".xlsx"
            
        filepath = os.path.join(docs_dir, filename)
        
        # Check if the file is open/locked
        try:
            _active_workbook.save(filepath)
            _active_filepath = filepath
        except PermissionError:
            # File is open in another process (e.g. Excel). Generate a unique filename.
            base, ext = os.path.splitext(filename)
            unique_filename = f"{base}_{int(time.time())}{ext}"
            filepath = os.path.join(docs_dir, unique_filename)
            _active_workbook.save(filepath)
            _active_filepath = filepath
            filename = unique_filename
            speak("The file was open in another app. I have saved it with a new name.")
        
        # Open the file on Windows
        os.startfile(filepath)
        return f"Successfully saved Excel workbook to {filename} and opened it."
    except Exception as e:
        return f"Failed to save Excel workbook: {e}"

def read_excel_workbook(filepath=None):
    """Reads and displays rows from the specified or most recent Excel workbook."""
    global _active_workbook, _active_worksheet, _active_filepath
    if not filepath:
        filepath = get_most_recent_excel_file()
        
    if not filepath or not os.path.exists(filepath):
        return "I couldn't find any Excel file to read."
        
    try:
        wb = openpyxl.load_workbook(filepath)
        sheet = wb.active
        
        # Load into active state so user can append more rows to it
        _active_workbook = wb
        _active_worksheet = sheet
        _active_filepath = filepath
        
        # Read first 10 rows
        rows = list(sheet.values)
        if not rows:
            return f"The sheet is empty in {os.path.basename(filepath)}."
            
        summary_lines = []
        for i, row in enumerate(rows[:10]):
            row_vals = [str(val) if val is not None else "" for val in row]
            summary_lines.append(f"Row {i+1}: " + " | ".join(row_vals))
            
        total_rows = len(rows)
        suffix = f"\n...and {total_rows - 10} more rows." if total_rows > 10 else ""
        
        res = f"Read {os.path.basename(filepath)} (Sheet: {sheet.title}, Total rows: {total_rows}):\n" + "\n".join(summary_lines) + suffix
        return res
    except Exception as e:
        return f"Failed to read Excel workbook: {e}"

def process_excel_command(command):
    """Processes incoming Excel-related voice/text commands with high resilience."""
    cmd_lower = command.lower().strip()
    
    # 1. Create Excel
    create_triggers = [
        "create excel", "create workbook", "new excel", "make excel", 
        "grade excel", "great excel", "create pixel", "excel sheet banao", 
        "excel banao", "excel file banao"
    ]
    if any(trigger in cmd_lower for trigger in create_triggers):
        return create_new_workbook()
        
    # 2. Save Excel
    save_triggers = [
        "save excel", "save workbook", "save sheet", "save file", 
        "save report", "save active workbook"
    ]
    if any(trigger in cmd_lower for trigger in save_triggers):
        # Parse potential filename
        filename = None
        phrases = [
            "save excel sheet as", "save excel workbook as", "save workbook as", 
            "save excel as", "save sheet as", "save report as", "save file as", 
            "save excel to", "save workbook to", "save sheet to", "save report to", 
            "save file to", "save excel", "save workbook", "save sheet", "save report", "save file"
        ]
        for phrase in phrases:
            if phrase in cmd_lower:
                idx = cmd_lower.find(phrase) + len(phrase)
                filename = command[idx:].strip()
                break
                
        if filename:
            filename = filename.replace(" ", "_")
            
        return save_active_workbook(filename)
        
    # 3. Read/Open Excel
    read_triggers = [
        "read excel", "open excel", "show excel", "view excel", 
        "read sheet", "open sheet", "show sheet", "view sheet"
    ]
    if any(trigger in cmd_lower for trigger in read_triggers):
        filename = None
        for phrase in read_triggers:
            if phrase in cmd_lower:
                idx = cmd_lower.find(phrase) + len(phrase)
                filename = command[idx:].strip()
                if filename:
                    break
        
        if filename:
            filename = filename.replace(" ", "_")
            if not filename.endswith(".xlsx"):
                filename += ".xlsx"
            docs_dir = os.path.join(os.path.expanduser("~"), "Documents", "Jarvis_Excel_Output")
            filepath = os.path.join(docs_dir, filename)
            if os.path.exists(filepath):
                return read_excel_workbook(filepath)
            
            for d in [os.path.join(os.path.expanduser("~"), "Downloads"), os.path.join(os.path.expanduser("~"), "Desktop")]:
                fp = os.path.join(d, filename)
                if os.path.exists(fp):
                    return read_excel_workbook(fp)
                    
        return read_excel_workbook()

    # 4. Add Row / Update Excel
    add_triggers = [
        "add row", "insert row", "add data", "insert data", "enter data", 
        "write row", "write data", "append row", "append data", "row add", 
        "data add", "excel me add", "excel sheet me", "write to excel", 
        "write in excel", "dal do", "daal do", "likh do", "likho"
    ]
    
    is_add_cmd = any(trigger in cmd_lower for trigger in add_triggers)
    if not is_add_cmd:
        has_excel_ref = "excel" in cmd_lower or "sheet" in cmd_lower
        has_action_ref = any(verb in cmd_lower for verb in ["add", "insert", "write", "put", "append", "likho", "likh do", "enter"])
        if has_excel_ref and has_action_ref:
            is_add_cmd = True

    if is_add_cmd:
        data_str = ""
        phrases = [
            "write to excel sheet", "write in excel sheet", "write to excel", "write in excel",
            "excel sheet me add kro", "excel sheet me add karo", "excel me add kro", "excel me add karo",
            "excel sheet me add", "excel me add", "add row to excel", "add data to excel",
            "add row", "add rows", "insert row", "insert rows", "add data", "insert data", 
            "enter data", "write row", "write data", "append row", "append data", "row add", 
            "data add", "put data", "put row", "excel sheet me", "excel me", "dal do", "daal do", 
            "likh do", "likho", "add", "insert", "write", "put"
        ]
        for phrase in phrases:
            if phrase in cmd_lower:
                idx = cmd_lower.find(phrase) + len(phrase)
                data_str = command[idx:].strip()
                for prep in ["to", "in", "into", "the", "a", "an"]:
                    if data_str.lower().startswith(prep + " "):
                        data_str = data_str[len(prep)+1:].strip()
                break
                
        if not data_str:
            return "Please specify the row content to add. For example, say: Add row apple, banana, orange."
            
        return add_row_to_active(data_str)
        
    return None
