"""
Plugins: Code & Full-Stack Website Generator Bridge
Redirects to the Autonomous AI Coder Agent (coder_agent.py)
"""
from coder_agent import is_coding_command, process_coding_command

def process_code_command(command, status_callback=None):
    if is_coding_command(command):
        return process_coding_command(command, status_callback=status_callback)
    return None
