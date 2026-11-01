import os
import sys
import json
import time
import re
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
    QProgressBar, QFrame, QMessageBox, QFileDialog, QTabWidget, QApplication, QComboBox,
    QButtonGroup, QRadioButton, QGraphicsDropShadowEffect
)

INTERVIEW_DIR = os.path.join("jarvis_data", "interviews")

def ensure_interview_dir():
    os.makedirs(INTERVIEW_DIR, exist_ok=True)


# ----------------- QUESTION GENERATOR ENGINE -----------------

DEFAULT_ROLE_QUESTIONS = {
    "full stack": [
        "Can you explain the difference between client-side rendering (CSR) and server-side rendering (SSR), and when would you choose one over the other?",
        "How do RESTful APIs differ from GraphQL, and how do you handle state management across complex frontend applications?",
        "Explain database indexing in PostgreSQL/MySQL. How does it speed up queries and what are the trade-offs?",
        "How do you secure web applications against Cross-Site Scripting (XSS) and SQL Injection attacks?",
        "Tell me about a challenging full-stack bug you encountered in production and how you debugged and resolved it."
    ],
    "ai": [
        "Explain the fundamental difference between supervised, unsupervised, and reinforcement learning with real-world examples.",
        "How do transformer architectures work, and why are self-attention mechanisms crucial for Large Language Models?",
        "What is overfitting in machine learning models, and what techniques do you use to prevent it?",
        "How do vector databases like ChromaDB or FAISS enable Retrieval-Augmented Generation (RAG)?",
        "Describe a complex AI project you built. What loss function did you optimize and what metrics did you use to evaluate performance?"
    ]
}

DEFAULT_MCQ_QUESTIONS = {
    "full stack": [
        {
            "question": "What is the primary advantage of indexing a database column in PostgreSQL or MySQL?",
            "options": [
                "A) Accelerates query execution speed for SELECT filters",
                "B) Reduces total disk storage space",
                "C) Automatically encrypts data at rest",
                "D) Prevents SQL injection attacks"
            ],
            "correct_option": "A",
            "explanation": "Indexing builds B-Tree or Hash data structures that drastically improve search performance from O(N) full table scans to O(log N) lookups."
        },
        {
            "question": "Which HTTP status code signifies that a resource was successfully created on the server?",
            "options": [
                "A) 200 OK",
                "B) 201 Created",
                "C) 204 No Content",
                "D) 302 Found"
            ],
            "correct_option": "B",
            "explanation": "HTTP 201 Created is the standard REST status code returned after a successful POST request creates a new resource."
        },
        {
            "question": "In React, what hook is used to handle side-effects like data fetching and subscriptions?",
            "options": [
                "A) useState",
                "B) useEffect",
                "C) useContext",
                "D) useReducer"
            ],
            "correct_option": "B",
            "explanation": "useEffect handles lifecycle side-effects such as API calls, manual DOM mutations, and event subscriptions."
        },
        {
            "question": "Which security header helps prevent Cross-Site Scripting (XSS) attacks in modern web apps?",
            "options": [
                "A) Content-Security-Policy (CSP)",
                "B) Access-Control-Allow-Origin",
                "C) Strict-Transport-Security",
                "D) X-Frame-Options"
            ],
            "correct_option": "A",
            "explanation": "Content-Security-Policy restricts origins from which scripts can be loaded and executed, mitigating XSS risks."
        },
        {
            "question": "What is the main difference between Docker containers and Virtual Machines?",
            "options": [
                "A) Containers share host OS kernel, making them lightweight",
                "B) VMs run faster than containers",
                "C) Containers require full hypervisors like ESXi",
                "D) VMs cannot run Linux operating systems"
            ],
            "correct_option": "A",
            "explanation": "Docker containers package application code and dependencies while sharing the host OS kernel, whereas VMs bundle full guest operating systems."
        }
    ],
    "ai": [
        {
            "question": "What is the primary role of the Self-Attention mechanism in Transformer architectures?",
            "options": [
                "A) Dynamically weighs relationships between all tokens in a sequence",
                "B) Compresses images into 2D convolutional feature maps",
                "C) Reduces learning rate automatically during training",
                "D) Converts text directly into speech audio"
            ],
            "correct_option": "A",
            "explanation": "Self-attention computes Query, Key, Value matrix dot-products to measure contextual relationships across all sequence positions."
        },
        {
            "question": "Which loss function is commonly used for multi-class classification problems?",
            "options": [
                "A) Mean Squared Error (MSE)",
                "B) Categorical Cross-Entropy",
                "C) Binary Cross-Entropy",
                "D) Hinge Loss"
            ],
            "correct_option": "B",
            "explanation": "Categorical Cross-Entropy measures probability distribution discrepancy for multi-class targets paired with Softmax."
        },
        {
            "question": "How do Vector Databases (like ChromaDB/FAISS) search for semantically similar text embeddings?",
            "options": [
                "A) Cosine Similarity / Euclidean Distance on high-dimensional vectors",
                "B) Exact string matching with Regex",
                "C) Binary Search Trees on ASCII character codes",
                "D) SHA-256 Hashing"
            ],
            "correct_option": "A",
            "explanation": "Vector databases perform Approximate Nearest Neighbor (ANN) search measuring cosine or L2 distances between dense embeddings."
        },
        {
            "question": "What technique is used to prevent neural networks from overfitting by randomly disabling nodes during training?",
            "options": [
                "A) Batch Normalization",
                "B) Dropout",
                "C) Gradient Clipping",
                "D) Data Augmentation"
            ],
            "correct_option": "B",
            "explanation": "Dropout randomly sets node activations to zero with probability P during training, preventing co-adaptation of features."
        },
        {
            "question": "What is Retrieval-Augmented Generation (RAG) in LLM applications?",
            "options": [
                "A) Augmenting LLM prompts with relevant external documents fetched from a vector index",
                "B) Training a model from scratch on private data",
                "C) Fine-tuning transformer weights using LoRA",
                "D) Converting text prompts into synthetic images"
            ],
            "correct_option": "A",
            "explanation": "RAG retrieves domain knowledge snippets from an external knowledge base and feeds them into the LLM context prompt."
        }
    ]
}


def generate_role_questions(target_role="Full Stack AI Engineer", difficulty="Mid-Level"):
    target_lower = target_role.lower()
    for r_key in DEFAULT_ROLE_QUESTIONS:
        if r_key in target_lower:
            return DEFAULT_ROLE_QUESTIONS[r_key]

    return [
        f"What core technical skills and architectural patterns are essential for a successful {target_role}?",
        f"How do you approach performance optimization and scalability when building applications for {target_role}?",
        "Describe a time when you had to debug a critical issue under tight deadlines. What was your step-by-step troubleshooting process?",
        "How do you ensure code quality, test coverage, and security compliance in your development workflow?",
        "Why are you interested in this position, and how do your technical accomplishments align with our engineering goals?"
    ]


def generate_role_mcqs(target_role="Full Stack AI Engineer", difficulty="Mid-Level"):
    """
    Generates 5 MCQ questions tailored to target_role and difficulty level.
    Returns list of dicts: [ { question, options: [A, B, C, D], correct_option: 'A', explanation: ... } ]
    """
    target_lower = target_role.lower()

    # Try Gemini AI MCQ Generation
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model_candidates = [
                "gemini-2.0-flash", 
                "gemini-2.0-flash-lite", 
                "gemini-2.0-flash-lite-preview-02-05",
                "gemini-1.5-flash-002",
                "gemini-1.5-flash-001"
            ]

            prompt = f"""
            You are an Executive Technical Recruiter creating a Multiple Choice (MCQ) Quiz for "{target_role}" ({difficulty}).
            Generate 5 high-quality technical MCQ questions.

            Return a valid JSON array of objects, where each object has:
            - "question": String question text
            - "options": Array of 4 strings (e.g. ["A) ...", "B) ...", "C) ...", "D) ..."])
            - "correct_option": Single character string ("A", "B", "C", or "D")
            - "explanation": 2-sentence explanation of why the correct option is right.
            """

            for model_name in model_candidates:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    text_resp = response.text.strip()
                    if "```json" in text_resp:
                        text_resp = text_resp.split("```json")[1].split("```")[0].strip()
                    elif "```" in text_resp:
                        text_resp = text_resp.split("```")[1].split("```")[0].strip()

                    res_list = json.loads(text_resp)
                    print(f"[MCQ GENERATOR SUCCESS] Generated MCQs with Gemini model: {model_name}")
                    return res_list
                except Exception as m_err:
                    print(f"[GEMINI MCQ MODEL TRY] {model_name} failed: {m_err}")
                    continue
    except Exception as e:
        print(f"[MCQ GENERATOR NOTICE] Switching to local MCQ taxonomy: {e}")

    for r_key in DEFAULT_MCQ_QUESTIONS:
        if r_key in target_lower:
            return DEFAULT_MCQ_QUESTIONS[r_key]

    return DEFAULT_MCQ_QUESTIONS["full stack"]


# ----------------- GEMINI AI RESPONSE EVALUATOR -----------------

def evaluate_interview_response(question, user_answer, target_role="Software Engineer"):
    if not user_answer or len(user_answer.strip()) < 10:
        return {
            "accuracy_score": 35,
            "confidence_score": 40,
            "keypoints_covered": ["Brief answer provided."],
            "missing_concepts": ["Answer was too concise or vague.", "Missing technical depth and concrete implementation examples."],
            "ideal_answer": f"A comprehensive answer should clearly define the core concept, provide concrete technical architectural trade-offs, and share a practical production example relevant to {target_role}.",
            "feedback": "Elaborate further on your answer! Use the STAR method (Situation, Task, Action, Result) and include specific technical terms."
        }

    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model_candidates = [
                "gemini-2.0-flash", 
                "gemini-2.0-flash-lite", 
                "gemini-2.0-flash-lite-preview-02-05",
                "gemini-1.5-flash-002",
                "gemini-1.5-flash-001"
            ]

            prompt = f"""
            You are an Executive Technical Recruiter conducting a mock interview for "{target_role}".
            Question: "{question}"
            Candidate Answer: "{user_answer}"

            Return JSON object:
            - "accuracy_score": Integer (0 to 100)
            - "confidence_score": Integer (0 to 100)
            - "keypoints_covered": Array of strings
            - "missing_concepts": Array of strings
            - "ideal_answer": 2-sentence model answer
            - "feedback": 2-sentence actionable coaching advice
            """

            for model_name in model_candidates:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    text_resp = response.text.strip()
                    if "```json" in text_resp:
                        text_resp = text_resp.split("```json")[1].split("```")[0].strip()
                    elif "```" in text_resp:
                        text_resp = text_resp.split("```")[1].split("```")[0].strip()

                    return json.loads(text_resp)
                except Exception:
                    continue
    except Exception:
        pass

    ans_lower = user_answer.lower()
    word_count = len(user_answer.split())
    score = 55 + (15 if word_count > 30 else 0) + (10 if word_count > 60 else 0)
    return {
        "accuracy_score": min(96, score),
        "confidence_score": min(95, score - 5),
        "keypoints_covered": [f"Provided clear communication with {word_count} words.", "Addressed question topic with context."],
        "missing_concepts": ["Include more specific architectural trade-offs or performance metrics."],
        "ideal_answer": f"For {target_role}, an ideal answer defines the fundamental principle clearly and references production deployment metrics.",
        "feedback": f"Solid answer! Add numerical metrics (e.g. 'reduced latency by 40%') to reach 95%+ score."
    }


# ----------------- SCORECARD EXPORTER -----------------

def export_interview_scorecard(session_data, target_role="Software Engineer"):
    ensure_interview_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    docx_path = os.path.join(INTERVIEW_DIR, f"Interview_Scorecard_{timestamp}.docx")
    pdf_path = os.path.join(INTERVIEW_DIR, f"Interview_Scorecard_{timestamp}.pdf")

    # Export DOCX
    try:
        import docx
        from docx.shared import Inches, Pt, RGBColor

        doc = docx.Document()
        title_p = doc.add_paragraph()
        r = title_p.add_run(f"INTELLIGENT AI MOCK INTERVIEW SCORECARD")
        r.font.size = Pt(18); r.font.bold = True

        sub_p = doc.add_paragraph()
        sub_p.add_run(f"Target Role: {target_role}  |  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        avg_acc = int(sum(item.get("accuracy_score", 70) for item in session_data) / max(1, len(session_data)))
        doc.add_heading(f"Overall Performance Score: {avg_acc}/100", level=1)

        for idx, item in enumerate(session_data, 1):
            doc.add_heading(f"Question {idx}: {item.get('question', '')}", level=2)
            if "selected_option" in item:
                doc.add_paragraph(f"Candidate Selected: Option {item.get('selected_option')} | Result: {'CORRECT ✅' if item.get('is_correct') else 'INCORRECT ❌'}")
                doc.add_paragraph(f"Explanation: {item.get('explanation', '')}")
            else:
                doc.add_paragraph(f"Candidate Answer: {item.get('user_answer', 'N/A')}")
                doc.add_paragraph(f"Scores: Accuracy {item.get('accuracy_score', 0)}% | Confidence {item.get('confidence_score', 0)}%")
                doc.add_paragraph(f"Feedback: {item.get('feedback', '')}")

        doc.save(docx_path)
    except Exception as e:
        print(f"[SCORECARD DOCX ERROR] {e}")
        docx_path = None

    # Export PDF
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, Spacer

        pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        story = []
        story.append(Paragraph("INTELLIGENT AI MOCK INTERVIEW SCORECARD", styles['Heading1']))
        story.append(Paragraph(f"Target Role: <b>{target_role}</b>  |  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))

        avg_acc = int(sum(item.get("accuracy_score", 70) for item in session_data) / max(1, len(session_data)))
        story.append(Paragraph(f"Overall Performance Score: <b>{avg_acc}/100</b>", styles['Heading2']))

        for idx, item in enumerate(session_data, 1):
            story.append(Paragraph(f"Question {idx}: {item.get('question', '')}", styles['Heading3']))
            if "selected_option" in item:
                story.append(Paragraph(f"Candidate Selected: <b>Option {item.get('selected_option')}</b> | Result: <b>{'CORRECT ✅' if item.get('is_correct') else 'INCORRECT ❌'}</b>", styles['Normal']))
                story.append(Paragraph(f"Explanation: {item.get('explanation', '')}", styles['Normal']))
            else:
                story.append(Paragraph(f"Candidate Answer: {item.get('user_answer', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"Scores: Accuracy: {item.get('accuracy_score', 0)}% | Confidence: {item.get('confidence_score', 0)}%", styles['Normal']))
                story.append(Paragraph(f"Feedback: {item.get('feedback', '')}", styles['Normal']))
            story.append(Spacer(1, 6))

        pdf_doc.build(story)
    except Exception as e:
        print(f"[SCORECARD PDF ERROR] {e}")
        pdf_path = None

    return docx_path, pdf_path


# ----------------- INTERVIEW COACH DIALOG UI -----------------

class InterviewCoachDialog(QDialog):
    """
    Sci-Fi Cyberpunk UI Dialog featuring both MCQ Quiz Mode and Descriptive Voice Interview Mode.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("INTELLIGENT AI MOCK INTERVIEW COACH & MCQ QUIZ")
        self.resize(980, 700)
        ensure_interview_dir()

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
                padding: 10px 18px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.4);
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton#opt_btn {
                background: #090d16;
                color: #ffffff;
                border: 1.5px solid #0066ff;
                border-radius: 8px;
                text-align: left;
                padding: 10px 14px;
                font-size: 12px;
            }
            QPushButton#opt_btn:hover {
                background: rgba(0, 255, 255, 0.2);
                border-color: #00ffff;
            }
            QPushButton#start_btn {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
                border-color: #00ff88;
            }
            QPushButton#start_btn:hover {
                background: rgba(0, 255, 136, 0.5);
                color: #ffffff;
            }
            QLineEdit, QComboBox {
                background: #090d16;
                color: #00ffff;
                border: 1px solid #0066ff;
                border-radius: 6px;
                padding: 8px;
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
            shadow.setBlurRadius(30)
            shadow.setColor(QColor(0, 255, 255, 150))
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)
        except Exception:
            pass

        self.questions = []
        self.mcqs = []
        self.current_q_idx = 0
        self.session_data = []
        self.mcq_correct_count = 0

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        title = QLabel("🎙️ INTELLIGENT AI MOCK INTERVIEW COACH & MCQ QUIZ")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Top Control Bar: Mode + Role + Difficulty
        top_bar = QHBoxLayout()

        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        top_bar.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["📝 MCQ QUIZ MODE", "🗣️ DESCRIPTIVE INTERVIEW MODE"])
        top_bar.addWidget(self.mode_combo)

        role_label = QLabel("Role:")
        role_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        top_bar.addWidget(role_label)

        self.role_input = QLineEdit()
        self.role_input.setText("Full Stack Python & AI Engineer")
        top_bar.addWidget(self.role_input)

        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Junior", "Mid-Level", "Senior / Lead"])
        self.diff_combo.setCurrentIndex(1)
        top_bar.addWidget(self.diff_combo)

        start_btn = QPushButton("🚀 START SESSION")
        start_btn.setObjectName("start_btn")
        start_btn.clicked.connect(self._start_session)
        top_bar.addWidget(start_btn)

        layout.addLayout(top_bar)

        # Question Header Box
        q_box = QVBoxLayout()
        q_header = QHBoxLayout()

        self.q_num_label = QLabel("Question 1 / 5:")
        self.q_num_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.q_num_label.setStyleSheet("color: #00ffff;")
        q_header.addWidget(self.q_num_label)

        speak_q_btn = QPushButton("🔊 REPEAT QUESTION")
        speak_q_btn.clicked.connect(self._speak_current_question)
        q_header.addWidget(speak_q_btn)

        q_box.addLayout(q_header)

        self.q_text_label = QLabel("Select mode and click 'START SESSION' to begin.")
        self.q_text_label.setWordWrap(True)
        self.q_text_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.q_text_label.setStyleSheet("color: #ffffff; background: #090d16; border: 1px solid #0066ff; border-radius: 8px; padding: 12px;")
        q_box.addWidget(self.q_text_label)

        layout.addLayout(q_box)

        # Stacked Answer Input: MCQ Options Widget vs Descriptive Box Widget
        self.mcq_widget = QWidget()
        mcq_layout = QVBoxLayout(self.mcq_widget)
        mcq_layout.setContentsMargins(0, 0, 0, 0)
        mcq_layout.setSpacing(6)

        self.opt_buttons = []
        for i in range(4):
            btn = QPushButton(f"Option {chr(65+i)}")
            btn.setObjectName("opt_btn")
            btn.clicked.connect(lambda _, idx=i: self._select_mcq_option(idx))
            self.opt_buttons.append(btn)
            mcq_layout.addWidget(btn)

        layout.addWidget(self.mcq_widget)

        self.desc_widget = QWidget()
        desc_layout = QVBoxLayout(self.desc_widget)
        desc_layout.setContentsMargins(0, 0, 0, 0)

        ans_label = QLabel("Your Answer (Type or Speak):")
        ans_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        desc_layout.addWidget(ans_label)

        self.ans_edit = QTextEdit()
        self.ans_edit.setPlaceholderText("Type your detailed technical answer here...")
        desc_layout.addWidget(self.ans_edit)

        sub_bar = QHBoxLayout()
        eval_btn = QPushButton("⚡ EVALUATE ANSWER")
        eval_btn.setObjectName("start_btn")
        eval_btn.clicked.connect(self._evaluate_descriptive_answer)
        sub_bar.addWidget(eval_btn)
        desc_layout.addLayout(sub_bar)

        layout.addWidget(self.desc_widget)
        self.desc_widget.hide()

        # Score & Feedback Layout
        score_layout = QHBoxLayout()
        acc_label = QLabel("Performance Score:")
        acc_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        score_layout.addWidget(acc_label)

        self.acc_bar = QProgressBar()
        self.acc_bar.setRange(0, 100)
        self.acc_bar.setValue(0)
        score_layout.addWidget(self.acc_bar)

        next_q_btn = QPushButton("▶️ NEXT QUESTION")
        next_q_btn.clicked.connect(self._next_question)
        score_layout.addWidget(next_q_btn)

        layout.addLayout(score_layout)

        # Tabbed Feedback Output
        self.tabs = QTabWidget()

        self.explanation_edit = QTextEdit()
        self.explanation_edit.setStyleSheet("color: #00ff88;")
        self.explanation_edit.setPlaceholderText("AI Explanation and Answer Analysis will appear here...")
        self.tabs.addTab(self.explanation_edit, "✨ AI EXPLANATION & FEEDBACK")

        layout.addWidget(self.tabs)

        # Bottom Action Bar
        bottom_bar = QHBoxLayout()
        self.status_label = QLabel("Status: Select Mode & click 'START SESSION'.")
        self.status_label.setStyleSheet("color: #94a3b8;")
        bottom_bar.addWidget(self.status_label)

        export_btn = QPushButton("📄 EXPORT SCORECARD (DOCX/PDF)")
        export_btn.clicked.connect(self._export_scorecard)
        bottom_bar.addWidget(export_btn)

        open_folder_btn = QPushButton("📁 OPEN FOLDER")
        open_folder_btn.clicked.connect(self._open_folder)
        bottom_bar.addWidget(open_folder_btn)

        layout.addLayout(bottom_bar)

    def _start_session(self):
        is_mcq = "MCQ" in self.mode_combo.currentText()
        role = self.role_input.text().strip() or "Full Stack AI Engineer"
        diff = self.diff_combo.currentText()

        self.current_q_idx = 0
        self.session_data = []
        self.mcq_correct_count = 0

        if is_mcq:
            self.mcq_widget.show()
            self.desc_widget.hide()
            self.status_label.setText(f"Status: 🤖 Generating 5 MCQ questions for '{role}'...")
            QApplication.processEvents()

            self.mcqs = generate_role_mcqs(target_role=role, difficulty=diff)
            self._show_current_mcq()
        else:
            self.mcq_widget.hide()
            self.desc_widget.show()
            self.status_label.setText(f"Status: 🤖 Generating 5 interview questions for '{role}'...")
            QApplication.processEvents()

            self.questions = generate_role_questions(target_role=role, difficulty=diff)
            self._show_current_descriptive()

    def _show_current_mcq(self):
        if not self.mcqs:
            return

        self.q_num_label.setText(f"MCQ Question {self.current_q_idx + 1} / {len(self.mcqs)}:")
        mcq = self.mcqs[self.current_q_idx]

        self.q_text_label.setText(mcq.get("question", ""))
        options = mcq.get("options", ["A)", "B)", "C)", "D)"])

        for i, opt in enumerate(options[:4]):
            self.opt_buttons[i].setText(opt)
            self.opt_buttons[i].setEnabled(True)
            self.opt_buttons[i].setStyleSheet("""
                QPushButton#opt_btn {
                    background: #090d16;
                    color: #ffffff;
                    border: 1.5px solid #0066ff;
                    border-radius: 8px;
                    text-align: left;
                    padding: 10px 14px;
                    font-size: 12px;
                }
                QPushButton#opt_btn:hover {
                    background: rgba(0, 255, 255, 0.2);
                    border-color: #00ffff;
                }
            """)

        self.explanation_edit.clear()
        self.status_label.setText(f"Status: MCQ Question {self.current_q_idx + 1} loaded. Click an option button.")
        self._speak_current_question()

    def _select_mcq_option(self, opt_idx):
        if not self.mcqs:
            return

        mcq = self.mcqs[self.current_q_idx]
        selected_letter = chr(65 + opt_idx)
        correct_letter = mcq.get("correct_option", "A").upper()

        is_correct = (selected_letter == correct_letter)
        if is_correct:
            self.mcq_correct_count += 1
            self.opt_buttons[opt_idx].setStyleSheet("background: rgba(0, 255, 136, 0.3); border: 2px solid #00ff88; color: #00ff88; font-weight: bold;")
            res_msg = f"✨ CORRECT! Option {selected_letter} is right."
        else:
            self.opt_buttons[opt_idx].setStyleSheet("background: rgba(239, 68, 68, 0.3); border: 2px solid #ef4444; color: #ef4444; font-weight: bold;")
            # Find and highlight correct button
            for i in range(4):
                if chr(65 + i) == correct_letter:
                    self.opt_buttons[i].setStyleSheet("background: rgba(0, 255, 136, 0.3); border: 2px solid #00ff88; color: #00ff88; font-weight: bold;")
            res_msg = f"❌ INCORRECT. You selected Option {selected_letter}, but correct answer is Option {correct_letter}."

        for btn in self.opt_buttons:
            btn.setEnabled(False)

        pct = int((self.mcq_correct_count / (self.current_q_idx + 1)) * 100)
        self.acc_bar.setValue(pct)
        self.acc_bar.setFormat(f"Quiz Score: {self.mcq_correct_count} / {self.current_q_idx + 1} ({pct}%)")

        exp_text = (
            f"=== {res_msg} ===\n\n"
            f"📌 EXPLANATION:\n{mcq.get('explanation', '')}"
        )
        self.explanation_edit.setPlainText(exp_text)

        self.session_data.append({
            "question": mcq.get("question", ""),
            "selected_option": selected_letter,
            "correct_option": correct_letter,
            "is_correct": is_correct,
            "accuracy_score": 100 if is_correct else 0,
            "explanation": mcq.get("explanation", "")
        })

        self.status_label.setText(f"Status: {res_msg}")
        try:
            from voice_engine import speak
            speak(res_msg)
        except Exception:
            pass

    def _show_current_descriptive(self):
        if not self.questions:
            return

        self.q_num_label.setText(f"Descriptive Question {self.current_q_idx + 1} / {len(self.questions)}:")
        current_q = self.questions[self.current_q_idx]
        self.q_text_label.setText(current_q)
        self.ans_edit.clear()
        self.acc_bar.setValue(0)
        self.explanation_edit.clear()
        self.status_label.setText(f"Status: Question {self.current_q_idx + 1} loaded. Type/speak your answer.")
        self._speak_current_question()

    def _evaluate_descriptive_answer(self):
        if not self.questions:
            return

        user_ans = self.ans_edit.toPlainText().strip()
        current_q = self.questions[self.current_q_idx]
        role = self.role_input.text().strip() or "Software Engineer"

        eval_res = evaluate_interview_response(current_q, user_ans, target_role=role)
        acc = eval_res.get("accuracy_score", 70)
        self.acc_bar.setValue(acc)

        exp_text = (
            f"=== ACCURACY SCORE: {acc}% ===\n\n"
            f"🎯 KEYPOINTS COVERED:\n" + "\n".join([f"• {s}" for s in eval_res.get("keypoints_covered", [])]) + "\n\n"
            f"⚠️ MISSING CONCEPTS:\n" + "\n".join([f"• {m}" for m in eval_res.get("missing_concepts", [])]) + "\n\n"
            f"✨ MODEL IDEAL ANSWER:\n{eval_res.get('ideal_answer', '')}\n\n"
            f"🚀 COACH FEEDBACK:\n{eval_res.get('feedback', '')}"
        )
        self.explanation_edit.setPlainText(exp_text)

        self.session_data.append({
            "question": current_q,
            "user_answer": user_ans,
            "accuracy_score": acc,
            "feedback": eval_res.get("feedback", "")
        })

    def _speak_current_question(self):
        q_text = ""
        if "MCQ" in self.mode_combo.currentText():
            if self.mcqs and self.current_q_idx < len(self.mcqs):
                m = self.mcqs[self.current_q_idx]
                q_text = m.get("question", "") + " Options are: " + ". ".join(m.get("options", []))
        else:
            if self.questions and self.current_q_idx < len(self.questions):
                q_text = self.questions[self.current_q_idx]

        if q_text:
            try:
                from voice_engine import speak
                speak(q_text)
            except Exception:
                pass

    def _next_question(self):
        is_mcq = "MCQ" in self.mode_combo.currentText()
        max_len = len(self.mcqs) if is_mcq else len(self.questions)

        if self.current_q_idx < max_len - 1:
            self.current_q_idx += 1
            if is_mcq:
                self._show_current_mcq()
            else:
                self._show_current_descriptive()
        else:
            self.status_label.setText("Status: 🏁 Session complete! Click 'EXPORT SCORECARD' to save report.")
            QMessageBox.information(self, "Session Complete", "Interview session complete! Review your score or export performance scorecard.")

    def _export_scorecard(self):
        if not self.session_data:
            QMessageBox.warning(self, "No Session Data", "Please answer at least one question to export a scorecard.")
            return

        role = self.role_input.text().strip() or "Software Engineer"
        docx_p, pdf_p = export_interview_scorecard(self.session_data, target_role=role)
        self.status_label.setText(f"Status: Scorecard saved in {INTERVIEW_DIR}")
        QMessageBox.information(self, "Scorecard Exported", f"Interview Scorecard saved successfully:\n• DOCX: {os.path.basename(docx_p)}\n• PDF: {os.path.basename(pdf_p)}")

    def _open_folder(self):
        if os.path.exists(INTERVIEW_DIR):
            os.startfile(INTERVIEW_DIR)
