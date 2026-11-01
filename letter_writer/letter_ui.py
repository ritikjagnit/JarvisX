"""
PyQt6 UI Dialog for AI Letter Writer & Notepad Automation feature.
"""

import sys
import os
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
    QProgressBar, QFrame, QMessageBox, QApplication
)

from .letter_generator import process_letter_command, generate_ai_letter, get_user_profile
from .letter_intent import parse_letter_intent
from .notepad_automation import open_notepad_and_type, save_letter_file

class LetterWorker(QThread):
    status_signal = pyqtSignal(str)
    completed_signal = pyqtSignal(str, bool)

    def __init__(self, command, parent=None):
        super().__init__(parent)
        self.command = command

    def run(self):
        def callback(stage, status):
            self.status_signal.emit(f"Status:\n{status}")

        response = process_letter_command(self.command, status_callback=callback)
        self.completed_signal.emit(response, True)


class LetterWriterDialog(QDialog):
    """
    Modern dark-themed PyQt6 GUI Dialog for AI Letter Writer.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS - AI Letter Writer & Notepad Automation")
        self.resize(650, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #0f172a;
                color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #e2e8f0;
            }
            QLineEdit, QTextEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                color: #f8fafc;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #3b82f6;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #94a3b8;
            }
        """)

        self.last_generated_text = ""

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header
        header = QLabel("AI LETTER WRITER")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #38bdf8;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Input Frame
        input_label = QLabel("Enter Request / Voice Command:")
        input_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(input_label)

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("e.g. Write a leave application for college for 3 days")
        layout.addWidget(self.cmd_input)

        # Action Buttons Layout
        btn_box = QHBoxLayout()
        self.btn_generate = QPushButton("Generate & Write to Notepad")
        self.btn_generate.clicked.connect(self.start_generation)
        btn_box.addWidget(self.btn_generate)

        self.btn_save = QPushButton("Save Letter (.txt)")
        self.btn_save.setStyleSheet("background-color: #059669;")
        self.btn_save.clicked.connect(self.save_letter)
        self.btn_save.setEnabled(False)
        btn_box.addWidget(self.btn_save)

        layout.addLayout(btn_box)

        # Status Label
        self.status_box = QLabel("Status: Ready")
        self.status_box.setStyleSheet("background-color: #1e293b; border-left: 4px solid #38bdf8; padding: 10px; border-radius: 4px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(self.status_box)

        # Output Preview Box
        preview_label = QLabel("Letter Preview:")
        preview_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(False)
        self.preview_text.setPlaceholderText("Generated letter preview will appear here...")
        layout.addWidget(self.preview_text)

        self.setLayout(layout)

    def start_generation(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            QMessageBox.warning(self, "Input Required", "Please enter a letter request or command.")
            return

        self.btn_generate.setEnabled(False)
        self.status_box.setText("Status:\nGenerating Letter...")
        self.status_box.setStyleSheet("background-color: #1e293b; border-left: 4px solid #f59e0b; padding: 10px; border-radius: 4px; font-weight: bold; color: #f59e0b;")

        # Start Worker Thread
        self.worker = LetterWorker(cmd)
        self.worker.status_signal.connect(self.update_status)
        self.worker.completed_signal.connect(self.on_completed)
        self.worker.start()

    def update_status(self, text):
        self.status_box.setText(text)

    def on_completed(self, response_text, success):
        self.btn_generate.setEnabled(True)
        self.status_box.setText(f"Status:\n{response_text} ✓")
        self.status_box.setStyleSheet("background-color: #1e293b; border-left: 4px solid #10b981; padding: 10px; border-radius: 4px; font-weight: bold; color: #10b981;")

        # Load generated letter into preview box from context or generator
        params = parse_letter_intent(self.cmd_input.text())
        profile = get_user_profile()
        self.last_generated_text = generate_ai_letter(params, profile)
        self.preview_text.setText(self.last_generated_text)
        self.btn_save.setEnabled(True)

    def save_letter(self):
        text = self.preview_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "No Content", "No letter content to save.")
            return

        success, path = save_letter_file(text, filename_hint="JARVIS_Letter")
        if success:
            QMessageBox.information(self, "Letter Saved", f"Letter saved successfully to:\n{path}")
        else:
            QMessageBox.critical(self, "Save Failed", f"Failed to save letter:\n{path}")


def open_letter_writer_dialog(parent=None):
    dialog = LetterWriterDialog(parent)
    dialog.exec()
