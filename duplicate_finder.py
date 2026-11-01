import os
import hashlib
from collections import defaultdict
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QFileDialog, QProgressBar, QFrame, QApplication, QGraphicsDropShadowEffect
)

# ----------------- HASH & CORE SCAN ENGINE -----------------

def calculate_sha256(filepath, chunk_size=65536):
    """Calculates SHA256 cryptographic hash of a file in 64KB chunks."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"[DUPLICATE FINDER WARNING] Failed to hash {filepath}: {e}")
        return None

def find_duplicates(directory_path, progress_callback=None):
    """
    High-performance 2-pass duplicate scanner:
    Pass 1: Group by file size.
    Pass 2: Calculate SHA256 hash for files with identical sizes.
    Returns dict: { sha256_hash: [filepath1, filepath2, ...] }
    """
    directory_path = os.path.abspath(os.path.expanduser(directory_path))
    if not os.path.exists(directory_path):
        return {}

    # Pass 1: Size Grouping
    size_map = defaultdict(list)
    total_discovered = 0

    for root, _, files in os.walk(directory_path):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                if os.path.isfile(full_path) and not os.path.islink(full_path):
                    size = os.path.getsize(full_path)
                    if size > 0: # Ignore 0-byte empty files
                        size_map[size].append(full_path)
                        total_discovered += 1
                        if progress_callback and total_discovered % 20 == 0:
                            progress_callback(0, 0, f"Scanning folders... Discovered {total_discovered} files ({f})")
            except Exception:
                continue

    # Filter out sizes with only 1 file
    potential_duplicates = {size: paths for size, paths in size_map.items() if len(paths) > 1}
    
    # Pass 2: SHA256 Hashing
    hash_map = defaultdict(list)
    scanned_count = 0
    total_potential = sum(len(paths) for paths in potential_duplicates.values())

    if total_potential == 0 and progress_callback:
        progress_callback(100, 100, f"Discovered {total_discovered} files. No candidate duplicates found.")

    for size, paths in potential_duplicates.items():
        for path in paths:
            scanned_count += 1
            if progress_callback:
                progress_callback(scanned_count, total_potential, f"Hashing {os.path.basename(path)} ({scanned_count}/{total_potential})")
            
            h = calculate_sha256(path)
            if h:
                hash_map[h].append(path)

    # Return only hashes with 2 or more identical files
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}

def format_bytes(size_bytes):
    """Formats bytes to human readable string (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# ----------------- SCAN WORKER THREAD -----------------

class DuplicateScanWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        try:
            results = find_duplicates(
                self.directory, 
                progress_callback=lambda current, total, path: self.progress.emit(current, total, path)
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


# ----------------- DUPLICATE FINDER DIALOG UI -----------------

class DuplicateFinderDialog(QDialog):
    """
    Independent PyQt6 Cyberpunk UI Dialog for Duplicate File Scanning & Cleanup.
    """
    def __init__(self, initial_dir=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("INTELLIGENT AI DUPLICATE FILE DETECTOR")
        self.resize(850, 600)
        self.initial_dir = initial_dir or os.path.expanduser("~/Downloads")

        self.setStyleSheet("""
            QDialog {
                background: #090d16;
                border: 2px solid #00ffff;
                border-radius: 14px;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background: rgba(15, 23, 42, 0.8);
                color: #00ffff;
                border: 1px solid #00ffff;
                border-radius: 6px;
                padding: 8px;
                font-family: Consolas;
            }
            QPushButton {
                background: rgba(0, 255, 255, 0.15);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.4);
                color: #ffffff;
            }
            QTreeWidget {
                background: #020617;
                color: #f8fafc;
                border: 1px solid #0066ff;
                border-radius: 8px;
            }
            QTreeWidget::item:hover {
                background: rgba(0, 255, 255, 0.2);
            }
            QProgressBar {
                border: 1px solid #00ffff;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                background: #020617;
            }
            QProgressBar::chunk {
                background-color: #00ffff;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 255, 255, 120))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self.scan_results = {}
        self.worker = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title Header
        title = QLabel("🔍 DUPLICATE FILE DETECTOR (SHA256 HASH ENGINE)")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Folder Selector Row
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit(self.initial_dir)
        dir_layout.addWidget(self.dir_input)

        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_btn)

        scan_btn = QPushButton("🚀 START SCAN")
        scan_btn.setStyleSheet("background: rgba(0, 255, 136, 0.25); color: #00ff88; border-color: #00ff88;")
        scan_btn.clicked.connect(self.start_scan)
        dir_layout.addWidget(scan_btn)

        layout.addLayout(dir_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Select a folder and click 'START SCAN' to detect duplicate files.")
        self.status_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.status_label)

        # Tree Widget for Duplicates Display
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File Name / Path", "Size", "SHA256 Hash / Status"])
        self.tree.setColumnWidth(0, 450)
        self.tree.setColumnWidth(1, 100)
        layout.addWidget(self.tree)

        # Action Buttons
        btn_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("☑️ Select Duplicates")
        select_all_btn.clicked.connect(self._select_all_duplicates)
        btn_layout.addWidget(select_all_btn)

        deselect_btn = QPushButton("☐ Deselect All")
        deselect_btn.clicked.connect(self._deselect_all)
        btn_layout.addWidget(deselect_btn)

        delete_btn = QPushButton("🗑️ DELETE SELECTED DUPLICATES")
        delete_btn.setStyleSheet("background: rgba(255, 0, 68, 0.25); color: #ff0044; border-color: #ff0044;")
        delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

    def _browse_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan", self.dir_input.text())
        if folder:
            self.dir_input.setText(folder)

    def start_scan(self):
        target_dir = self.dir_input.text().strip()
        if not os.path.exists(target_dir):
            QMessageBox.warning(self, "Invalid Directory", f"Directory does not exist: {target_dir}")
            return

        self.tree.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Scanning target directory: {target_dir}...")

        self.worker = DuplicateScanWorker(target_dir)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_scan_finished)
        self.worker.error.connect(self._on_scan_error)
        self.worker.start()

    def _on_progress(self, current, total, status_text):
        if total > 0:
            val = int((current / total) * 100)
            self.progress_bar.setValue(val)
        else:
            self.progress_bar.setValue(0)
        self.status_label.setText(status_text)

    def _on_scan_finished(self, results):
        self.progress_bar.setVisible(False)
        self.scan_results = results

        total_duplicate_groups = len(results)
        total_duplicate_files = sum(len(paths) - 1 for paths in results.values())
        wasted_bytes = 0

        self.tree.clear()
        for sha_hash, paths in results.items():
            first_path = paths[0]
            try:
                size_bytes = os.path.getsize(first_path)
            except Exception:
                size_bytes = 0
            
            wasted_bytes += size_bytes * (len(paths) - 1)
            size_str = format_bytes(size_bytes)

            # Parent Group Node
            group_node = QTreeWidgetItem(self.tree)
            group_node.setText(0, f"Group: {os.path.basename(first_path)} ({len(paths)} copies)")
            group_node.setText(1, size_str)
            group_node.setText(2, f"SHA256: {sha_hash[:16]}...")
            group_node.setForeground(0, QColor("#00ffff"))

            # Child File Nodes
            for idx, filepath in enumerate(paths):
                child = QTreeWidgetItem(group_node)
                child.setText(0, filepath)
                child.setText(1, size_str)

                if idx == 0:
                    child.setText(2, "[ORIGINAL - KEEP]")
                    child.setForeground(2, QColor("#00ff88"))
                else:
                    child.setText(2, "[DUPLICATE]")
                    child.setForeground(2, QColor("#ff4466"))
                    child.setCheckState(0, Qt.CheckState.Unchecked)

            group_node.setExpanded(True)

        if total_duplicate_groups == 0:
            self.status_label.setText("Scan Complete: Clean! No duplicate files found.")
        else:
            wasted_str = format_bytes(wasted_bytes)
            self.status_label.setText(f"Scan Complete: Found {total_duplicate_groups} duplicate groups ({total_duplicate_files} duplicate files, ~{wasted_str} space can be freed).")

    def _on_scan_error(self, err_msg):
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Scan error: {err_msg}")

    def _select_all_duplicates(self):
        for i in range(self.tree.topLevelItemCount()):
            group_node = self.tree.topLevelItem(i)
            for j in range(group_node.childCount()):
                child = group_node.child(j)
                if child.text(2) == "[DUPLICATE]":
                    child.setCheckState(0, Qt.CheckState.Checked)

    def _deselect_all(self):
        for i in range(self.tree.topLevelItemCount()):
            group_node = self.tree.topLevelItem(i)
            for j in range(group_node.childCount()):
                child = group_node.child(j)
                child.setCheckState(0, Qt.CheckState.Unchecked)

    def delete_selected(self):
        selected_files = []
        for i in range(self.tree.topLevelItemCount()):
            group_node = self.tree.topLevelItem(i)
            for j in range(group_node.childCount()):
                child = group_node.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    selected_files.append(child.text(0))

        if not selected_files:
            QMessageBox.information(self, "No Selection", "Please check the checkbox for duplicate files you wish to delete.")
            return

        # Double Confirmation Dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to permanently delete {len(selected_files)} duplicate file(s)?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = 0
            freed_bytes = 0
            for filepath in selected_files:
                try:
                    size = os.path.getsize(filepath)
                    os.remove(filepath)
                    deleted_count += 1
                    freed_bytes += size
                except Exception as e:
                    print(f"[DELETE ERROR] Failed to delete {filepath}: {e}")

            freed_str = format_bytes(freed_bytes)
            QMessageBox.information(self, "Cleanup Successful", f"Successfully deleted {deleted_count} duplicate file(s).\nFreed Disk Space: {freed_str}")
            self.start_scan() # Refresh scan after deletion

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    dialog = DuplicateFinderDialog()
    dialog.show()
    sys.exit(app.exec())
