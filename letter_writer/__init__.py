"""
AI Letter Writer & Notepad Automation Module for JARVIS AI Assistant.
"""

from .letter_intent import is_letter_command, parse_letter_intent
from .letter_generator import generate_ai_letter, process_letter_command
from .notepad_automation import open_notepad_and_type, save_letter_file

__all__ = [
    "is_letter_command",
    "parse_letter_intent",
    "generate_ai_letter",
    "process_letter_command",
    "open_notepad_and_type",
    "save_letter_file"
]
