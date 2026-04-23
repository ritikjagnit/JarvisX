from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout


class ChatPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)

        layout.addWidget(self.chat_area)

        self.setLayout(layout)

    def add_message(self, sender, message):

        self.chat_area.append(f"{sender}: {message}")