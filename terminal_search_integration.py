import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QLineEdit
from web_search import JarvisWebSearch

class SearchWorker(QThread):
    """Background worker to ensure UI doesn't freeze during network queries."""
    finished_signal = pyqtSignal(list, str)
    error_signal = pyqtSignal(str)

    def __init__(self, query: str, cmd_type: str, searcher: JarvisWebSearch):
        super().__init__()
        self.query = query
        self.cmd_type = cmd_type
        self.searcher = searcher

    def run(self):
        try:
            if self.cmd_type == 'search':
                results = self.searcher.search_web(self.query, max_results=3)
            elif self.cmd_type == 'news':
                results = self.searcher.search_news(self.query, max_results=3)
            else:
                results = []
            self.finished_signal.emit(results, self.cmd_type)
        except Exception as e:
            self.error_signal.emit(str(e))


class SearchTerminalIntegration:
    """
    Connects JarvisWebSearch to the PremiumTerminal. 
    Includes real-time networking animation and formatted outputs!
    """
    def __init__(self, terminal_widget: QTextEdit):
        self.terminal = terminal_widget
        self.searcher = JarvisWebSearch()
        self.worker = None
        
        # Loader Animation Setup
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_chars = ["/", "-", "\\", "|"]
        self.anim_idx = 0
        self.is_searching = False

    def handle_input(self, text: str) -> bool:
        """
        Parses commands. Returns True if handled by this integration.
        """
        text = text.strip()
        if text.startswith("/search "):
            query = text.replace("/search ", "", 1).strip()
            self._initiate_search(query, 'search')
            return True
        elif text.startswith("/news "):
            query = text.replace("/news ", "", 1).strip()
            self._initiate_search(query, 'news')
            return True
        return False

    def _initiate_search(self, query: str, cmd_type: str):
        if self.is_searching:
            self.terminal.append_message("SYSTEM", "A network task is already running.")
            return

        self.is_searching = True
        self.terminal.append_message("JARVIS-WEB", f"Establishing secure uplink for {cmd_type}: '{query}'")
        
        # Insert initial loading frame
        self.terminal.append('<span style="color: #ffaa00;">[ ] Engaging quantum search...</span>')
        
        # Spin up threads and timers
        self.anim_timer.start(150)
        self.worker = SearchWorker(query, cmd_type, self.searcher)
        self.worker.finished_signal.connect(self._on_success)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _update_animation(self):
        """Creates a smooth inline spinning loader directly in the terminal."""
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        
        char = self.anim_chars[self.anim_idx % len(self.anim_chars)]
        self.anim_idx += 1
        
        cursor.removeSelectedText()
        cursor.insertHtml(f'<span style="color: #ffaa00;">[{char}] Retrieving network packets...</span>')

    def _cleanup_animation(self):
        """Erases the loading frame."""
        self.is_searching = False
        self.anim_timer.stop()
        
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()

    def _on_success(self, results: list, cmd_type: str):
        self._cleanup_animation()
        
        if not results:
            self.terminal.append_message("JARVIS-WEB", "No databanks matched your query.")
            return

        self.terminal.append('<span style="color: #00ffcc; font-weight: bold;">[ CONNECTED ] ~ Displaying payload:</span><br>')
        
        if cmd_type == 'search':
            for i, res in enumerate(results):
                title = res.get('title', 'Unknown')
                snippet = res.get('snippet', '')
                link = res.get('link', '')
                self.terminal.append(f'<span style="color: #00ffcc; font-size: 14px; font-weight: bold;">[{i+1}] {title}</span>')
                self.terminal.append(f'<span style="color: #cccccc;">{snippet}</span>')
                self.terminal.append(f'<a href="{link}" style="color: #0088ff; text-decoration: none;">📄 Source Link</a><br><br>')
                
        elif cmd_type == 'news':
            for i, res in enumerate(results):
                title = res.get('title', 'Unknown')
                date = res.get('date', 'Recent')
                source = res.get('source', 'Web')
                link = res.get('link', '')
                self.terminal.append(f'<span style="color: #ff5555; font-size: 14px; font-weight: bold;">[{i+1}] {title}</span> <span style="color: #888888;">({date} | {source})</span>')
                self.terminal.append(f'<a href="{link}" style="color: #0088ff; text-decoration: none;">📰 Read Article</a><br><br>')
                
        self.terminal.append('<span style="color: #00ffcc; font-weight: bold;">--- CONNECTION CLOSED ---</span><br>')
        
        # Scroll to bottom automatically
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_error(self, error_msg: str):
        self._cleanup_animation()
        self.terminal.append_message("SYSTEM-ERROR", f"Uplink severed: {error_msg}")

# =====================================================================
# INTEGRATION EXAMPLE / DEMO APP
# =====================================================================
class PremiumTerminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 11))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #020617;
                color: #00ffcc;
                border: 2px solid #00ffff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
    def append_message(self, sender, message):
        """Appends formatted system messages simulating JARVIS interactions."""
        timestamp = time.strftime("%H:%M:%S")
        color = "#ffaa00" if sender != "JARVIS-WEB" else "#00ffcc"
        self.append(f'<span style="color: {color}; font-weight: bold;">[{timestamp}] {sender}:</span> <span style="color: #ffffff;">{message}</span>')

class DemoDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis Terminal Extension Test")
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        self.terminal = PremiumTerminal()
        self.terminal.append_message("SYSTEM", "Terminal online. Type '/search [query]' or '/news [topic]'")
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command here... (e.g., /search quantum computing)")
        self.input_field.setStyleSheet("background: #000; color: #fff; padding: 10px; border: 1px solid #00ffcc; font-size: 14px;")
        
        layout.addWidget(self.terminal)
        layout.addWidget(self.input_field)
        
        # Initialize Integration
        self.search_integration = SearchTerminalIntegration(self.terminal)
        
        # Connect Input
        self.input_field.returnPressed.connect(self.process_input)
        
    def process_input(self):
        text = self.input_field.text()
        self.input_field.clear()
        
        if not text.strip():
            return
            
        self.terminal.append_message("USER", text)
        
        # Route to search integration first
        handled = self.search_integration.handle_input(text)
        
        # If the search integration didn't handle it, run standard logic
        if not handled:
            self.terminal.append_message("JARVIS", f"Command generated: {text} (Standard Logic Mode)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DemoDashboard()
    demo.show()
    sys.exit(app.exec())
