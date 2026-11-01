import os
import sys
import shutil
import zipfile
import subprocess
import time
from pathlib import Path

# Local project imports
from open_app import open_app
from close_app import close_app
from file_manager import process_file_command

class DesktopAgent:
    """
    Desktop Automation Agent for controlling Windows OS.
    Handles app launching, file system operations, office document creation
    (PowerPoint, Excel, Word), screen capture, zip compression, and download organizing.
    """
    def __init__(self):
        self.downloads_path = Path(os.path.expanduser("~/Downloads"))
        self.documents_path = Path(os.path.expanduser("~/Documents"))
        self.desktop_path = Path(os.path.expanduser("~/Desktop"))

    def launch_app(self, app_name):
        """Open an application on Windows (e.g. Chrome, VS Code, Notepad)."""
        app_name_clean = app_name.strip()
        print(f"[DESKTOP AGENT] Launching application: {app_name_clean}")
        success = open_app(app_name_clean)
        if success:
            return f"Successfully opened '{app_name_clean}'."
        else:
            # Fallback to subprocess start
            try:
                subprocess.Popen(f"start {app_name_clean}", shell=True)
                return f"Launched '{app_name_clean}' via system shell."
            except Exception as e:
                return f"Could not launch '{app_name_clean}': {e}"

    def close_app(self, app_name):
        """Close a running application."""
        success = close_app(app_name)
        return f"Closed '{app_name}'." if success else f"Application '{app_name}' was not running."

    def create_folder(self, folder_name, parent_dir=None):
        """Create a new directory."""
        target_dir = Path(parent_dir) if parent_dir else self.documents_path
        folder_path = target_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"[DESKTOP AGENT] Created folder: {folder_path}")
        return f"Created folder '{folder_path}' successfully."

    def rename_file(self, old_path, new_name):
        """Rename a file or directory."""
        old_file = Path(old_path)
        if not old_file.exists():
            return f"File '{old_path}' does not exist."
        new_file = old_file.parent / new_name
        old_file.rename(new_file)
        print(f"[DESKTOP AGENT] Renamed '{old_path}' to '{new_file}'")
        return f"Renamed '{old_file.name}' to '{new_file.name}' successfully."

    def move_file(self, src_path, dest_dir):
        """Move a file to a target directory."""
        src = Path(src_path)
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            return f"Source file '{src_path}' does not exist."
        target_file = dest / src.name
        shutil.move(str(src), str(target_file))
        print(f"[DESKTOP AGENT] Moved '{src_path}' -> '{target_file}'")
        return f"Moved '{src.name}' to '{dest}' successfully."

    def delete_file(self, file_path, user_confirmed=False):
        """Delete a file or folder (STRICT SAFETY GATE: REQUIRES CONFIRMATION)."""
        target = Path(file_path)
        if not target.exists():
            return f"Target '{file_path}' does not exist."

        if not user_confirmed:
            return f"[SAFETY CONFIRMATION REQUIRED] Are you sure you want to permanently delete '{target.name}'? Say 'Yes, delete' to confirm."

        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        print(f"[DESKTOP AGENT] Deleted '{file_path}'")
        return f"Deleted '{target.name}' successfully."

    def take_screenshot(self, output_path=None):
        """Take a screenshot of the main display."""
        try:
            import pyautogui
            data_dir = Path(__file__).resolve().parent.parent / "jarvis_data"
            data_dir.mkdir(exist_ok=True)
            if not output_path:
                output_path = data_dir / f"screenshot_{int(time.time())}.png"
            output_path = Path(output_path)
            screenshot = pyautogui.screenshot()
            screenshot.save(str(output_path))
            print(f"[DESKTOP AGENT] Screenshot saved to: {output_path}")
            return f"Screenshot captured and saved to '{output_path.name}'."
        except Exception as e:
            return f"Failed to capture screenshot: {e}"

    def record_screen(self, duration_seconds=5, output_path=None):
        """Record screen for a specified duration."""
        try:
            import pyautogui
            import cv2
            import numpy as np

            data_dir = Path(__file__).resolve().parent.parent / "jarvis_data"
            data_dir.mkdir(exist_ok=True)
            if not output_path:
                output_path = data_dir / f"screen_record_{int(time.time())}.mp4"

            screen_size = pyautogui.size()
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(output_path), fourcc, 10.0, screen_size)

            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                img = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                out.write(frame)

            out.release()
            print(f"[DESKTOP AGENT] Screen recording saved to: {output_path}")
            return f"Screen recorded for {duration_seconds}s and saved to '{output_path.name}'."
        except Exception as e:
            return f"Screen recording fallback notice: {e}"

    def create_excel(self, file_name="Report.xlsx", sheets_data=None, output_dir=None):
        """Create an Excel spreadsheet with optional structured data."""
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Report Data"

            if sheets_data and isinstance(sheets_data, list):
                for row in sheets_data:
                    ws.append(row)
            else:
                ws.append(["ID", "Category", "Item Name", "Status", "Date"])
                ws.append([1, "System", "Jarvis AI Autonomous Core", "Active", time.strftime("%Y-%m-%d")])
                ws.append([2, "Task", "Excel Generation Module", "Completed", time.strftime("%Y-%m-%d")])

            target_dir = Path(output_dir) if output_dir else self.documents_path
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = target_dir / (file_name if file_name.endswith(".xlsx") else f"{file_name}.xlsx")
            wb.save(str(file_path))
            print(f"[DESKTOP AGENT] Excel created: {file_path}")
            return f"Created Excel file '{file_path.name}' in Documents."
        except Exception as e:
            return f"Failed to create Excel file: {e}"

    def create_word(self, file_name="Document.docx", title="Jarvis Autonomous Report", content=None, output_dir=None):
        """Create a Word document."""
        try:
            import docx
            doc = docx.Document()
            doc.add_heading(title, 0)
            
            if content:
                if isinstance(content, list):
                    for para in content:
                        doc.add_paragraph(para)
                else:
                    doc.add_paragraph(str(content))
            else:
                doc.add_paragraph("This document was generated automatically by the Jarvis AI Autonomous Agent System.")
                doc.add_paragraph(f"Generated Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")

            target_dir = Path(output_dir) if output_dir else self.documents_path
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = target_dir / (file_name if file_name.endswith(".docx") else f"{file_name}.docx")
            doc.save(str(file_path))
            print(f"[DESKTOP AGENT] Word doc created: {file_path}")
            return f"Created Word document '{file_path.name}' in Documents."
        except Exception as e:
            return f"Failed to create Word document: {e}"

    def create_powerpoint(self, file_name="Presentation.pptx", title="Artificial Intelligence Overview", slides_content=None, output_dir=None):
        """Create a PowerPoint presentation."""
        try:
            import pptx
            from pptx.util import Inches, Pt

            prs = pptx.Presentation()
            
            # Slide 1: Title Slide
            title_slide_layout = prs.slide_layouts[0]
            slide = prs.slides.add_slide(title_slide_layout)
            title_box = slide.shapes.title
            subtitle_box = slide.placeholders[1]
            title_box.text = title
            subtitle_box.text = "Prepared by Jarvis Autonomous AI Agent"

            # Default slide content if none provided
            if not slides_content:
                slides_content = [
                    {"title": "Introduction to AI", "body": "• Artificial Intelligence simulates human intelligence in machines.\n• Powers automation, language understanding, and vision systems."},
                    {"title": "Key Components", "body": "• Machine Learning & Deep Learning\n• Natural Language Processing (NLP)\n• Computer Vision & Robotics"},
                    {"title": "Future Outlook", "body": "• Autonomous Agents executing end-to-end workflows.\n• Human-AI pair programming & collaboration."}
                ]

            bullet_slide_layout = prs.slide_layouts[1]
            for s_data in slides_content:
                slide = prs.slides.add_slide(bullet_slide_layout)
                shapes = slide.shapes
                title_shape = shapes.title
                body_shape = shapes.placeholders[1]
                title_shape.text = s_data.get("title", "Slide Title")
                tf = body_shape.text_frame
                tf.text = s_data.get("body", "Content paragraph...")

            target_dir = Path(output_dir) if output_dir else self.documents_path
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = target_dir / (file_name if file_name.endswith(".pptx") else f"{file_name}.pptx")
            prs.save(str(file_path))
            print(f"[DESKTOP AGENT] PowerPoint created: {file_path}")
            return f"Created PowerPoint presentation '{file_path.name}' with {len(prs.slides)} slides in Documents."
        except Exception as e:
            return f"Failed to create PowerPoint presentation: {e}"

    def search_computer(self, query, search_dir=None):
        """Search local directory for files matching query."""
        search_dir = Path(search_dir) if search_dir else self.documents_path
        query_clean = query.lower().strip()
        matches = []
        try:
            for path in search_dir.rglob(f"*{query_clean}*"):
                matches.append(str(path))
                if len(matches) >= 10:
                    break
            if matches:
                return f"Found {len(matches)} item(s) matching '{query}':\n" + "\n".join(matches)
            return f"No files matching '{query}' were found in '{search_dir}'."
        except Exception as e:
            return f"Error searching computer: {e}"

    def organize_downloads(self):
        """Organize files in Downloads directory into categorized subfolders."""
        if not self.downloads_path.exists():
            return "Downloads folder does not exist."

        categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Executables": [".exe", ".msi", ".bat"],
            "Audio": [".mp3", ".wav", ".flac", ".m4a"],
            "Videos": [".mp4", ".mkv", ".avi", ".mov"]
        }

        moved_count = 0
        for item in self.downloads_path.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                for cat, extensions in categories.items():
                    if ext in extensions:
                        cat_dir = self.downloads_path / cat
                        cat_dir.mkdir(exist_ok=True)
                        dest = cat_dir / item.name
                        shutil.move(str(item), str(dest))
                        moved_count += 1
                        break

        print(f"[DESKTOP AGENT] Organized Downloads: {moved_count} files moved.")
        return f"Successfully organized Downloads folder ({moved_count} files sorted into categories)."

    def compress_files(self, source_paths, zip_name="Archive.zip", output_dir=None):
        """Compress list of files into a ZIP archive."""
        target_dir = Path(output_dir) if output_dir else self.documents_path
        target_dir.mkdir(parents=True, exist_ok=True)
        zip_path = target_dir / (zip_name if zip_name.endswith(".zip") else f"{zip_name}.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for src in source_paths:
                src_p = Path(src)
                if src_p.exists():
                    if src_p.is_file():
                        zipf.write(src_p, arcname=src_p.name)
                    elif src_p.is_dir():
                        for file in src_p.rglob("*"):
                            zipf.write(file, arcname=file.relative_to(src_p.parent))

        print(f"[DESKTOP AGENT] Compressed files into: {zip_path}")
        return f"Compressed files into '{zip_path.name}'."

    def extract_zip(self, zip_path, extract_to=None):
        """Extract a ZIP archive."""
        zip_p = Path(zip_path)
        if not zip_p.exists():
            return f"ZIP file '{zip_path}' does not exist."
        
        dest_dir = Path(extract_to) if extract_to else zip_p.parent / zip_p.stem
        dest_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_p, 'r') as zipf:
            zipf.extractall(dest_dir)

        print(f"[DESKTOP AGENT] Extracted '{zip_path}' -> '{dest_dir}'")
        return f"Extracted '{zip_p.name}' to '{dest_dir}'."
