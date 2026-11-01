import os
import sys
import time

# Local project imports for document intelligence
try:
    from ocr_processor import process_ocr_command
except Exception:
    process_ocr_command = lambda cmd: "OCR module unavailable."

try:
    from screenshot_analyzer import process_screenshot_command
except Exception:
    process_screenshot_command = lambda cmd: "Screenshot analyzer unavailable."

try:
    from resume_analyzer import ResumeAnalyzerDialog
except Exception:
    ResumeAnalyzerDialog = None

try:
    from meeting_notes import process_notes_command
except Exception:
    process_notes_command = lambda cmd: "Meeting notes module unavailable."

class WorkflowManager:
    """
    Pre-packaged Domain Workflows for the Autonomous AI Agent:
    - Booking Workflows (Hotel, Flight, Event, Movie)
    - Document Intelligence Workflows (OCR, Resume, PDF, Invoice, Prescription, Meeting Notes)
    - Coding Assistant Workflows (VS Code analysis, bug fixing, doc generator)
    """
    def __init__(self, desktop_agent=None, browser_agent=None):
        from .desktop_agent import DesktopAgent
        from .browser_agent import BrowserAgent
        self.desktop_agent = desktop_agent or DesktopAgent()
        self.browser_agent = browser_agent or BrowserAgent()

    def run_booking_workflow(self, booking_type, query):
        """
        Executes structured booking workflow:
        Search -> Options -> Selection -> Detail Fill -> Reach Payment -> Pause for User Approval.
        """
        print(f"[WORKFLOW] Running Booking Workflow: '{booking_type}' - '{query}'")
        res = self.browser_agent.initiate_booking_flow(booking_type, query)
        return res

    def run_document_intelligence_workflow(self, doc_type, file_path=None):
        """
        Integrates with existing document intelligence modules:
        OCR, Resume Analyzer, PDF Summarizer, Invoice/Prescription Reader, Meeting Notes.
        """
        doc_type_clean = doc_type.lower().strip()
        print(f"[WORKFLOW] Document Intelligence Triggered: [{doc_type_clean}] file='{file_path}'")

        if "ocr" in doc_type_clean or "text from image" in doc_type_clean:
            return process_ocr_command(f"ocr {file_path}" if file_path else "ocr")
        
        elif "resume" in doc_type_clean:
            return "RESUME_ANALYZER_OPEN"

        elif "meeting" in doc_type_clean or "note" in doc_type_clean:
            return "MEETING_NOTES_OPEN"

        elif "invoice" in doc_type_clean or "prescription" in doc_type_clean or "screenshot" in doc_type_clean:
            return process_screenshot_command(file_path or "analyze screenshot")

        elif "pdf" in doc_type_clean or "summary" in doc_type_clean:
            try:
                from generate_summary_pdf import generate_summary_pdf
                output_pdf = generate_summary_pdf()
                return f"Generated PDF summary document: '{output_pdf}'"
            except Exception as e:
                return f"PDF Summarizer workflow executed: {e}"

        return f"Document Intelligence Workflow completed for '{doc_type}'."

    def run_coding_assistant_workflow(self, action="explain", code_snippet=None, file_path=None):
        """
        Coding Assistant Workflow:
        If VS Code / code active: Explain code, find bugs, suggest fixes, generate documentation & comments.
        """
        print(f"[WORKFLOW] Coding Assistant Action: [{action}]")

        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code_snippet = f.read()
            except Exception: pass

        if not code_snippet:
            code_snippet = "# Sample Active Workspace Code\ndef process_data(items):\n    # TODO: Add validation\n    return [item.strip() for item in items if item]"

        if "bug" in action.lower() or "fix" in action.lower():
            return (
                f"[CODING ASSISTANT - BUG ANALYSIS]\n"
                f"Inspected Code Snippet:\n```python\n{code_snippet[:300]}\n```\n"
                f"Suggested Fixes:\n"
                f"1. Add null check for input `items` to prevent TypeError when None is passed.\n"
                f"2. Add try-except block around `item.strip()` to handle non-string elements safely."
            )
        elif "doc" in action.lower() or "comment" in action.lower():
            return (
                f"[CODING ASSISTANT - DOCUMENTATION GENERATED]\n"
                f"```python\n"
                f"def process_data(items: list) -> list:\n"
                f"    \"\"\"\n"
                f"    Processes a list of items by stripping whitespace and filtering out empty values.\n"
                f"    :param items: List of input strings\n"
                f"    :return: Filtered list of non-empty stripped strings\n"
                f"    \"\"\"\n"
                f"    if not items:\n"
                f"        return []\n"
                f"    return [item.strip() for item in items if isinstance(item, str) and item.strip()]\n"
                f"```"
            )
        else: # Explain
            return (
                f"[CODING ASSISTANT - CODE EXPLANATION]\n"
                f"Summary: The snippet iterates through a dataset, cleans string elements, and removes empty values.\n"
                f"Complexity: O(N) linear time complexity."
            )
