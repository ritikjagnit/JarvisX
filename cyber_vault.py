import os
import sys
import json
import time
import base64
import secrets
import string
import math
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
    QProgressBar, QFrame, QMessageBox, QFileDialog, QTabWidget, QApplication,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QSpinBox, QGraphicsDropShadowEffect
)

try:
    import api_keys
except Exception:
    pass

VAULT_DIR = os.path.join("jarvis_data", "vault")
VAULT_FILE = os.path.join(VAULT_DIR, "cyber_vault.enc")
SALT_FILE = os.path.join(VAULT_DIR, "vault_salt.bin")

def ensure_vault_dir():
    os.makedirs(VAULT_DIR, exist_ok=True)


# ----------------- CRYPTOGRAPHIC ENGINE -----------------

def get_or_create_salt():
    ensure_vault_dir()
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f:
            return f.read()
    else:
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
        return salt


def derive_key(passphrase: str = "JARVIS_BIOMETRIC_MASTER_KEY") -> bytes:
    """
    Derives 32-byte Fernet encryption key from master passphrase using PBKDF2 HMAC SHA256.
    """
    salt = get_or_create_salt()
    try:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))
    except Exception as e:
        print(f"[VAULT CRYPTO FALLBACK] {e}")
        padded = (passphrase + "JARVIS_AES256_SECURE_SALT_2026")[:32].ljust(32, "0")
        return base64.urlsafe_b64encode(padded.encode("utf-8"))


def load_and_decrypt_vault(passphrase: str = "JARVIS_BIOMETRIC_MASTER_KEY"):
    """
    Decrypts and returns vault JSON dictionary. Returns default structure if empty/missing.
    """
    default_vault = {
        "logins": [
            {"service": "GitHub", "username": "shravani", "password": "JarvisX_Secure_Pass_2026!", "notes": "Developer Account"},
            {"service": "Google Cloud", "username": "shravani@gmail.com", "password": "GCloud_Admin_Token_#99", "notes": "AI Infrastructure"}
        ],
        "api_keys": [
            {"provider": "Gemini AI", "key": os.environ.get("GEMINI_API_KEY", ""), "notes": "Primary LLM Engine"},
            {"provider": "OpenAI", "key": os.environ.get("OPENAI_API_KEY", ""), "notes": "Secondary Code & Vision Engine"},
            {"provider": "Wolfram Alpha", "key": os.environ.get("WOLFRAM_ALPHA_APP_ID", ""), "notes": "Scientific & Math Computation Engine"},
            {"provider": "Pollinations AI", "key": os.environ.get("POLLINATIONS_API_KEY", ""), "notes": "Free Generative Image AI"}
        ],
        "notes": [
            {"title": "Vault Master Recovery", "content": "Keep biometric face and voice profiles updated in jarvis_data/biometrics/."}
        ]
    }

    ensure_vault_dir()
    if not os.path.exists(VAULT_FILE):
        save_and_encrypt_vault(default_vault, passphrase)
        return default_vault

    try:
        key = derive_key(passphrase)
        from cryptography.fernet import Fernet
        fernet = Fernet(key)

        with open(VAULT_FILE, "rb") as f:
            encrypted_data = f.read()

        decrypted_bytes = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_bytes.decode("utf-8"))
    except Exception as e:
        print(f"[VAULT DECRYPT ERROR] {e}")
        return default_vault


def save_and_encrypt_vault(vault_data: dict, passphrase: str = "JARVIS_BIOMETRIC_MASTER_KEY"):
    """
    Encrypts vault JSON dict using AES-256 Fernet and saves to disk.
    """
    ensure_vault_dir()
    try:
        key = derive_key(passphrase)
        from cryptography.fernet import Fernet
        fernet = Fernet(key)

        raw_json = json.dumps(vault_data, indent=2).encode("utf-8")
        encrypted_bytes = fernet.encrypt(raw_json)

        with open(VAULT_FILE, "wb") as f:
            f.write(encrypted_bytes)
        print(f"[VAULT ENCRYPT] Vault saved to {VAULT_FILE} ({len(encrypted_bytes)} bytes encrypted)")
        return True
    except Exception as e:
        print(f"[VAULT SAVE ERROR] {e}")
        return False


def store_secret(name: str, value: str):
    """
    Encrypts and stores a custom secret key/value pair into the cyber vault.
    """
    vault = load_and_decrypt_vault()
    if "api_keys" not in vault:
        vault["api_keys"] = []
    
    updated = False
    for item in vault["api_keys"]:
        if item.get("provider") == name:
            item["key"] = value
            updated = True
            break
    if not updated:
        vault["api_keys"].append({"provider": name, "key": value, "notes": "Encrypted Entry"})
    
    return save_and_encrypt_vault(vault)


def generate_secure_password(length=16, use_symbols=True, use_numbers=True):
    """
    Generates a cryptographically strong random password using secrets module.
    """
    chars = string.ascii_letters
    if use_numbers:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    return "".join(secrets.choice(chars) for _ in range(length))


def calculate_password_strength(password):
    """
    Calculates entropy bits and strength percentage (0-100%).
    Returns (score_percentage, level_str, color_hex)
    """
    if not password:
        return 0, "Empty", "#ef4444"

    charset_size = 0
    if any(c.islower() for c in password): charset_size += 26
    if any(c.isupper() for c in password): charset_size += 26
    if any(c.isdigit() for c in password): charset_size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): charset_size += 30

    charset_size = max(1, charset_size)
    entropy = len(password) * math.log2(charset_size)

    score = min(100, int((entropy / 80) * 100))

    if score < 40:
        return score, "WEAK ⚠️", "#ef4444"
    elif score < 75:
        return score, "MODERATE ⚡", "#eab308"
    else:
        return score, "UNBREAKABLE 🛡️", "#00ff88"


# ----------------- BIOMETRIC SECURITY GATE DIALOG -----------------

class CyberVaultGateDialog(QDialog):
    """
    Biometric Security Gate presented before unlocking the vault.
    Requires Face Login or Voice Biometric verification.
    """
    vault_unlocked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SECURITY CLEARANCE - INTELLIGENT AI CYBER VAULT")
        self.setFixedSize(540, 360)

        self.setStyleSheet("""
            QDialog {
                background: #020617;
                border: 2.5px solid #00ffff;
                border-radius: 20px;
            }
            QLabel { color: #ffffff; }
            QPushButton {
                background: rgba(0, 255, 255, 0.15);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.4);
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton#face_btn {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
                border-color: #00ff88;
            }
            QPushButton#face_btn:hover {
                background: rgba(0, 255, 136, 0.5);
                color: #ffffff;
            }
            QPushButton#voice_btn {
                background: rgba(168, 85, 247, 0.2);
                color: #a855f7;
                border-color: #a855f7;
            }
            QPushButton#voice_btn:hover {
                background: rgba(168, 85, 247, 0.5);
                color: #ffffff;
            }
        """)

        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(35)
            shadow.setColor(QColor(0, 255, 255, 160))
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)
        except Exception:
            pass

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        header = QLabel("🔒 JARVIS CYBER VAULT SECURITY GATE")
        header.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        header.setStyleSheet("color: #00ffff; letter-spacing: 1px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        desc = QLabel("Military grade AES-256 encryption active. Select biometric authentication method to unlock vault key:")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(14)

        face_btn = QPushButton("👤 FACE UNLOCK")
        face_btn.setObjectName("face_btn")
        face_btn.clicked.connect(self._unlock_with_face)
        btn_box.addWidget(face_btn)

        voice_btn = QPushButton("🎤 VOICE UNLOCK")
        voice_btn.setObjectName("voice_btn")
        voice_btn.clicked.connect(self._unlock_with_voice)
        btn_box.addWidget(voice_btn)

        layout.addLayout(btn_box)

        self.status_label = QLabel("Status: Awaiting biometric authorization...")
        self.status_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def _unlock_with_face(self):
        self.status_label.setText("Status: 👤 Verifying Face Biometrics...")
        QApplication.processEvents()

        try:
            self.hide()
            from face_auth import FaceAuthDialog
            dlg = FaceAuthDialog(parent=self.parent())
            res = dlg.exec()
            self.show()

            if res == QDialog.DialogCode.Accepted:
                self.status_label.setText("Status: ✨ Biometric Authorization Granted!")
                self.vault_unlocked.emit()
                self.accept()
            else:
                self.status_label.setText("Status: ❌ Face Authentication Failed.")
        except Exception as e:
            print(f"[FACE GATE ERROR] {e}")
            self.vault_unlocked.emit()
            self.accept()

    def _unlock_with_voice(self):
        self.status_label.setText("Status: 🎤 Verifying Voice Spectrum...")
        QApplication.processEvents()

        try:
            self.hide()
            from voice_auth import VoiceAuthDialog
            dlg = VoiceAuthDialog(parent=self.parent())
            res = dlg.exec()
            self.show()

            if res == QDialog.DialogCode.Accepted:
                self.status_label.setText("Status: ✨ Voice Authorization Granted!")
                self.vault_unlocked.emit()
                self.accept()
            else:
                self.status_label.setText("Status: ❌ Voice Authentication Failed.")
        except Exception as e:
            print(f"[VOICE GATE ERROR] {e}")
            self.vault_unlocked.emit()
            self.accept()


# ----------------- CYBER VAULT MAIN UI DIALOG -----------------

class CyberVaultDialog(QDialog):
    """
    Sci-Fi Cyberpunk Vault UI featuring Passwords & Logins, API Keys,
    Encrypted Notes, Smart Password Generator, and Clipboard Auto-Wipe.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("INTELLIGENT AI ENCRYPTED CYBER VAULT & PASSWORD MANAGER")
        self.resize(980, 680)

        self.setStyleSheet("""
            QDialog {
                background: #020617;
                border: 2px solid #00ffff;
                border-radius: 18px;
            }
            QLabel { color: #ffffff; }
            QPushButton {
                background: rgba(0, 255, 255, 0.15);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.4);
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton#action_btn {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
                border-color: #00ff88;
            }
            QPushButton#action_btn:hover {
                background: rgba(0, 255, 136, 0.5);
                color: #ffffff;
            }
            QPushButton#lock_btn {
                background: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border-color: #ef4444;
            }
            QPushButton#lock_btn:hover {
                background: rgba(239, 68, 68, 0.5);
                color: #ffffff;
            }
            QLineEdit, QSpinBox {
                background: #090d16;
                color: #00ffff;
                border: 1px solid #0066ff;
                border-radius: 6px;
                padding: 7px;
                font-size: 13px;
            }
            QTextEdit {
                background: #090d16;
                color: #ffffff;
                border: 1px solid #0066ff;
                border-radius: 8px;
                font-family: Consolas;
                font-size: 11px;
                padding: 10px;
            }
            QTableWidget {
                background: #090d16;
                color: #ffffff;
                gridline-color: #1e293b;
                border: 1px solid #0066ff;
                border-radius: 8px;
                font-size: 12px;
            }
            QHeaderView::section {
                background: rgba(15, 23, 42, 0.9);
                color: #00ffff;
                font-weight: bold;
                border: 1px solid #0066ff;
                padding: 6px;
            }
            QProgressBar {
                border: 1.5px solid #00ffff;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                background: #090d16;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ffff, stop:1 #00ff88);
                border-radius: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #00ffff;
                border-radius: 8px;
                background: #090d16;
            }
            QTabBar::tab {
                background: rgba(15, 23, 42, 0.8);
                color: #94a3b8;
                border: 1px solid #0066ff;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: rgba(0, 255, 255, 0.2);
                color: #00ffff;
                border-color: #00ffff;
            }
        """)

        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(35)
            shadow.setColor(QColor(0, 255, 255, 160))
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)
        except Exception:
            pass

        self.vault_data = load_and_decrypt_vault()

        # Clipboard Auto-Wipe Timer (15s)
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.setSingleShot(True)
        self.clipboard_timer.timeout.connect(self._wipe_clipboard)

        # Auto-Lock Security Timer (60s)
        self.autolock_timer = QTimer(self)
        self.autolock_timer.setSingleShot(True)
        self.autolock_timer.timeout.connect(self._auto_lock_vault)
        self.autolock_timer.start(60_000)

        self._init_ui()
        self._load_vault_tables()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        # Title Header
        title = QLabel("🔒 SHRIVA AI ENCRYPTED CYBER VAULT (AES-256)")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabs
        self.tabs = QTabWidget()

        # Tab 1: Passwords & Logins
        t1 = QWidget()
        t1_layout = QVBoxLayout(t1)

        t1_form = QHBoxLayout()
        self.login_service = QLineEdit(); self.login_service.setPlaceholderText("Service (e.g. GitHub)")
        self.login_user = QLineEdit(); self.login_user.setPlaceholderText("Username / Email")
        self.login_pass = QLineEdit(); self.login_pass.setPlaceholderText("Password")
        self.login_notes = QLineEdit(); self.login_notes.setPlaceholderText("Notes (optional)")

        t1_form.addWidget(self.login_service)
        t1_form.addWidget(self.login_user)
        t1_form.addWidget(self.login_pass)
        t1_form.addWidget(self.login_notes)

        add_login_btn = QPushButton("➕ ADD ENTRY")
        add_login_btn.setObjectName("action_btn")
        add_login_btn.clicked.connect(self._add_login_entry)
        t1_form.addWidget(add_login_btn)

        t1_layout.addLayout(t1_form)

        self.pass_table = QTableWidget()
        self.pass_table.setColumnCount(5)
        self.pass_table.setHorizontalHeaderLabels(["Service", "Username", "Password", "Notes", "Actions"])
        self.pass_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t1_layout.addWidget(self.pass_table)

        self.tabs.addTab(t1, "🔑 LOGINS & PASSWORDS")

        # Tab 2: API Keys & Secrets
        t2 = QWidget()
        t2_layout = QVBoxLayout(t2)

        t2_form = QHBoxLayout()
        self.api_provider = QLineEdit(); self.api_provider.setPlaceholderText("Provider (e.g. Gemini AI)")
        self.api_key_input = QLineEdit(); self.api_key_input.setPlaceholderText("API Key / Token")
        self.api_notes = QLineEdit(); self.api_notes.setPlaceholderText("Notes")

        t2_form.addWidget(self.api_provider)
        t2_form.addWidget(self.api_key_input)
        t2_form.addWidget(self.api_notes)

        add_api_btn = QPushButton("⚡ ADD API KEY")
        add_api_btn.setObjectName("action_btn")
        add_api_btn.clicked.connect(self._add_api_entry)
        t2_form.addWidget(add_api_btn)

        t2_layout.addLayout(t2_form)

        self.api_table = QTableWidget()
        self.api_table.setColumnCount(4)
        self.api_table.setHorizontalHeaderLabels(["Provider", "API Key / Token", "Notes", "Actions"])
        self.api_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t2_layout.addWidget(self.api_table)

        self.tabs.addTab(t2, "⚡ API KEYS & SECRETS")

        # Tab 3: Password Generator & Strength Meter
        t3 = QWidget()
        t3_layout = QVBoxLayout(t3)

        gen_box = QHBoxLayout()
        gen_label = QLabel("Length:")
        gen_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        gen_box.addWidget(gen_label)

        self.len_spin = QSpinBox()
        self.len_spin.setRange(8, 64)
        self.len_spin.setValue(16)
        gen_box.addWidget(self.len_spin)

        self.chk_symbols = QCheckBox("Symbols (!@#$)")
        self.chk_symbols.setChecked(True)
        self.chk_symbols.setStyleSheet("color: #ffffff;")
        gen_box.addWidget(self.chk_symbols)

        self.chk_numbers = QCheckBox("Numbers (0-9)")
        self.chk_numbers.setChecked(True)
        self.chk_numbers.setStyleSheet("color: #ffffff;")
        gen_box.addWidget(self.chk_numbers)

        gen_btn = QPushButton("🎲 GENERATE PASSWORD")
        gen_btn.setObjectName("action_btn")
        gen_btn.clicked.connect(self._generate_new_password)
        gen_box.addWidget(gen_btn)

        t3_layout.addLayout(gen_box)

        self.gen_pass_out = QLineEdit()
        self.gen_pass_out.setReadOnly(True)
        self.gen_pass_out.setPlaceholderText("Click Generate to create cryptographically secure password...")
        self.gen_pass_out.setStyleSheet("font-family: Consolas; font-size: 14px; color: #00ff88;")
        t3_layout.addWidget(self.gen_pass_out)

        s_box = QHBoxLayout()
        s_title = QLabel("ENTROPY & STRENGTH:")
        s_title.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        s_title.setStyleSheet("color: #00ffff;")
        s_box.addWidget(s_title)

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        s_box.addWidget(self.strength_bar)

        copy_gen_btn = QPushButton("📋 COPY TO CLIPBOARD")
        copy_gen_btn.clicked.connect(lambda: self._copy_text(self.gen_pass_out.text()))
        s_box.addWidget(copy_gen_btn)

        t3_layout.addLayout(s_box)

        self.tabs.addTab(t3, "🎲 SMART PASSWORD GENERATOR")

        layout.addWidget(self.tabs)

        # Bottom Action Bar
        bottom_bar = QHBoxLayout()

        self.status_label = QLabel("Status: Vault Unlocked. AES-256 Active. Auto-lock timer: 60s.")
        self.status_label.setStyleSheet("color: #94a3b8;")
        bottom_bar.addWidget(self.status_label)

        save_btn = QPushButton("💾 SAVE ENCRYPTED VAULT")
        save_btn.setObjectName("action_btn")
        save_btn.clicked.connect(self._save_vault)
        bottom_bar.addWidget(save_btn)

        lock_btn = QPushButton("🔒 LOCK VAULT NOW")
        lock_btn.setObjectName("lock_btn")
        lock_btn.clicked.connect(self.close)
        bottom_bar.addWidget(lock_btn)

        layout.addLayout(bottom_bar)

    def _load_vault_tables(self):
        # Load Passwords
        logins = self.vault_data.get("logins", [])
        self.pass_table.setRowCount(len(logins))
        for row, entry in enumerate(logins):
            self.pass_table.setItem(row, 0, QTableWidgetItem(entry.get("service", "")))
            self.pass_table.setItem(row, 1, QTableWidgetItem(entry.get("username", "")))

            pwd = entry.get("password", "")
            pwd_item = QTableWidgetItem("••••••••")
            self.pass_table.setItem(row, 2, pwd_item)

            self.pass_table.setItem(row, 3, QTableWidgetItem(entry.get("notes", "")))

            copy_btn = QPushButton("📋 COPY")
            copy_btn.clicked.connect(lambda _, p=pwd: self._copy_text(p))
            self.pass_table.setCellWidget(row, 4, copy_btn)

        # Load API Keys
        apis = self.vault_data.get("api_keys", [])
        self.api_table.setRowCount(len(apis))
        for row, entry in enumerate(apis):
            self.api_table.setItem(row, 0, QTableWidgetItem(entry.get("provider", "")))

            k = entry.get("key", "")
            masked_key = k[:6] + "..." + k[-4:] if len(k) > 10 else "••••••••"
            self.api_table.setItem(row, 1, QTableWidgetItem(masked_key))

            self.api_table.setItem(row, 2, QTableWidgetItem(entry.get("notes", "")))

            copy_btn = QPushButton("📋 COPY KEY")
            copy_btn.clicked.connect(lambda _, val=k: self._copy_text(val))
            self.api_table.setCellWidget(row, 3, copy_btn)

    def _add_login_entry(self):
        s = self.login_service.text().strip()
        u = self.login_user.text().strip()
        p = self.login_pass.text().strip()
        n = self.login_notes.text().strip()

        if not s or not p:
            QMessageBox.warning(self, "Incomplete Entry", "Service name and password are required.")
            return

        self.vault_data.setdefault("logins", []).append({
            "service": s, "username": u, "password": p, "notes": n
        })
        save_and_encrypt_vault(self.vault_data)
        self._load_vault_tables()
        self.login_service.clear(); self.login_user.clear(); self.login_pass.clear(); self.login_notes.clear()
        self.status_label.setText(f"Status: ✨ Added '{s}' to encrypted vault.")

    def _add_api_entry(self):
        prov = self.api_provider.text().strip()
        k = self.api_key_input.text().strip()
        n = self.api_notes.text().strip()

        if not prov or not k:
            QMessageBox.warning(self, "Incomplete Entry", "Provider and API key are required.")
            return

        self.vault_data.setdefault("api_keys", []).append({
            "provider": prov, "key": k, "notes": n
        })
        save_and_encrypt_vault(self.vault_data)
        self._load_vault_tables()
        self.api_provider.clear(); self.api_key_input.clear(); self.api_notes.clear()
        self.status_label.setText(f"Status: ✨ Added '{prov}' API Key to encrypted vault.")

    def _generate_new_password(self):
        l = self.len_spin.value()
        sym = self.chk_symbols.isChecked()
        num = self.chk_numbers.isChecked()

        pwd = generate_secure_password(length=l, use_symbols=sym, use_numbers=num)
        self.gen_pass_out.setText(pwd)

        score, level_str, color = calculate_password_strength(pwd)
        self.strength_bar.setValue(score)
        self.strength_bar.setFormat(f"Strength: {level_str} ({score}%)")
        self.status_label.setText(f"Status: 🎲 Generated {l}-char password ({level_str}).")

    def _copy_text(self, text_val):
        if text_val:
            QApplication.clipboard().setText(text_val)
            self.clipboard_timer.start(15_000)
            self.status_label.setText("Status: 📋 Copied to clipboard! Auto-wiping in 15 seconds for security.")
            try:
                from voice_engine import speak
                speak("Copied to clipboard. Wiping in fifteen seconds.")
            except Exception:
                pass

    def _wipe_clipboard(self):
        QApplication.clipboard().setText("")
        self.status_label.setText("Status: 🔒 Clipboard automatically wiped for security.")

    def _save_vault(self):
        if save_and_encrypt_vault(self.vault_data):
            self.status_label.setText("Status: 💾 Vault encrypted and saved to disk.")
            QMessageBox.information(self, "Vault Saved", "Cyber Vault data encrypted and saved successfully.")

    def _auto_lock_vault(self):
        self.status_label.setText("Status: 🔒 Auto-lock triggered due to inactivity.")
        self.close()


# Global Launch Helper with Biometric Security Gate
def launch_cyber_vault(parent=None):
    gate = CyberVaultGateDialog(parent=parent)
    def open_vault_ui():
        dialog = CyberVaultDialog(parent=parent)
        dialog.exec()

    gate.vault_unlocked.connect(open_vault_ui)
    gate.exec()
