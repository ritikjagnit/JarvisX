import os
import sys
import json
import time
import re
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
    QProgressBar, QFrame, QMessageBox, QFileDialog, QTabWidget, QApplication, QGraphicsDropShadowEffect
)

RESUME_DIR = os.path.join("jarvis_data", "resumes")

def ensure_resume_dir():
    os.makedirs(RESUME_DIR, exist_ok=True)


# ----------------- RESUME TEXT EXTRACTOR -----------------

def extract_resume_text(filepath):
    """
    Extracts plain text content from PDF, DOCX, or TXT resume files.
    """
    if not os.path.exists(filepath):
        return ""

    ext = os.path.splitext(filepath)[1].lower()
    text_content = ""

    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(filepath)
            text_content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            print(f"[RESUME EXTRACTOR] DOCX parse error: {e}")

    elif ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
        except Exception as e:
            print(f"[RESUME EXTRACTOR] pypdf parse notice: {e}")
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                    text_content = re.sub(rb'[^\x20-\x7E\n\r\t]', b' ', content).decode("ascii", errors="ignore")
            except Exception as e2:
                print(f"[RESUME EXTRACTOR] PDF fallback notice: {e2}")

    elif ext in [".txt", ".md"]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()
        except Exception as e:
            print(f"[RESUME EXTRACTOR] TXT parse error: {e}")

    return text_content.strip()


# ----------------- GEMINI AI DEEP ANALYZER -----------------

def analyze_resume_with_gemini(resume_text, target_role="Full Stack Python & AI Engineer"):
    """
    Analyzes resume text dynamically using Gemini AI or Dynamic NLP engine across ATS score,
    strengths, weaknesses, missing keywords, and actionable step-by-step improvement roadmap.
    Returns dict: { ats_score, summary_verdict, strengths, weaknesses, missing_keywords, improvement_roadmap }
    """
    if not resume_text or len(resume_text.strip()) < 30:
        resume_text = (
            "Shravani - Software Engineer\n"
            "Skills: Python, PyQt6, OpenCV, Streamlit, Machine Learning, Git.\n"
            "Projects: JarvisX Local AI Assistant with Biometric Auth and Automated Document Generators.\n"
            "Education: Bachelor of Computer Engineering."
        )

    # Try Gemini API with robust model fallbacks
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
            You are an elite AI Career Coach and Executive ATS Resume Evaluator.
            Analyze the following resume specifically for the target job role "{target_role}":
            "{resume_text}"

            Return a valid JSON object with the following keys:
            - "ats_score": Integer (0 to 100) representing ATS screening readiness for "{target_role}"
            - "summary_verdict": 2-sentence executive summary of resume suitability for "{target_role}"
            - "strengths": Array of strings highlighting strong technical skills and project metrics
            - "weaknesses": Array of strings identifying red flags, passive language, missing metrics, or gaps for "{target_role}"
            - "missing_keywords": Array of strings listing high-demand missing skills for "{target_role}"
            - "improvement_roadmap": Array of strings detailing step-by-step actionable recommendations to make the resume top 1% strong for "{target_role}" ("Tu ye ye kar jisse resume strong banega")
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

                    res_dict = json.loads(text_resp)
                    print(f"[RESUME ANALYZER SUCCESS] Evaluated with Gemini model: {model_name}")
                    return res_dict
                except Exception as m_err:
                    print(f"[GEMINI MODEL TRY] {model_name} failed: {m_err}")
                    continue

    except Exception as e:
        print(f"[RESUME ANALYZER NOTICE] Switching to Dynamic NLP Evaluation Engine: {e}")

    # Dynamic NLP Evaluation Engine (100% Customized to Resume Text & Target Role)
    return dynamic_local_resume_analysis(resume_text, target_role)


def dynamic_local_resume_analysis(resume_text, target_role):
    """
    Performs dynamic, role-tailored ATS evaluation customized to uploaded resume text and target_role.
    """
    resume_lower = resume_text.lower()
    target_lower = target_role.lower()

    # Role-Specific High-Demand Skill Taxonomies
    ROLE_KEYWORDS = {
        "python": ["python", "django", "flask", "fastapi", "pytest", "numpy", "pandas", "pyqt6"],
        "ai": ["machine learning", "deep learning", "pytorch", "tensorflow", "opencv", "llm", "gemini", "langchain", "nlp", "vector db"],
        "data": ["sql", "pandas", "numpy", "scikit-learn", "data visualization", "tableau", "power bi", "etl", "big data"],
        "full stack": ["react", "node.js", "typescript", "javascript", "html", "css", "rest api", "postgresql", "mongodb", "docker"],
        "frontend": ["react", "vue", "angular", "typescript", "javascript", "html5", "css3", "tailwind", "webpack"],
        "backend": ["node.js", "express", "python", "java", "spring boot", "postgresql", "redis", "docker", "microservices"],
        "devops": ["docker", "kubernetes", "aws", "azure", "terraform", "ci/cd", "jenkins", "linux", "bash", "ansible"],
        "java": ["java", "spring boot", "hibernate", "maven", "junit", "microservices", "sql"],
        "web": ["html", "css", "javascript", "react", "bootstrap", "php", "web development"]
    }

    matched_role_keys = [r_key for r_key in ROLE_KEYWORDS if r_key in target_lower]
    if not matched_role_keys:
        matched_role_keys = ["python", "ai", "full stack"]

    required_keywords = set()
    for r_key in matched_role_keys:
        required_keywords.update(ROLE_KEYWORDS[r_key])

    present_keywords = [kw.title() for kw in required_keywords if kw in resume_lower]
    missing_keywords = [kw.title() for kw in required_keywords if kw not in resume_lower]

    sections = {
        "Experience / Projects": any(k in resume_lower for k in ["experience", "project", "work", "built", "developed", "architected"]),
        "Skills / Technical Stack": any(k in resume_lower for k in ["skill", "technolog", "proficien", "stack"]),
        "Education": any(k in resume_lower for k in ["education", "bachelor", "degree", "university", "college", "b.tech", "b.e", "b.sc"]),
        "Certifications / Contact": any(k in resume_lower for k in ["email", "phone", "linkedin", "github", "contact", "certificat"])
    }

    found_sections = [name for name, found in sections.items() if found]
    missing_sections = [name for name, found in sections.items() if not found]

    has_quantifiable_metrics = bool(re.search(r'\b\d+%\b|\b\d+\s*ms\b|\$\d+|\b\d+\+\s*users\b|\b\d+\s*projects\b', resume_lower))

    score = 45
    if required_keywords:
        cov_ratio = len(present_keywords) / len(required_keywords)
        score += int(cov_ratio * 35)

    score += len(found_sections) * 4
    if has_quantifiable_metrics:
        score += 8
    if len(resume_text.split()) > 150:
        score += 4

    ats_score = min(98, max(30, score))

    strengths = []
    if present_keywords:
        strengths.append(f"Demonstrated core skill match for '{target_role}': {', '.join(present_keywords[:5])}.")
    if sections["Experience / Projects"]:
        strengths.append("Structured Project / Work Experience section detailing implementations.")
    if has_quantifiable_metrics:
        strengths.append("Includes measurable impact metrics and quantifiable results.")
    if not strengths:
        strengths.append(f"Basic content structure detected suitable for technical refinement towards {target_role}.")

    weaknesses = []
    if missing_keywords:
        weaknesses.append(f"Missing high-priority keywords specifically required for '{target_role}': {', '.join(missing_keywords[:4])}.")
    if not has_quantifiable_metrics:
        weaknesses.append("Lacks quantifiable ROI metrics (e.g. 'improved latency by 35%', 'handled 500+ daily active users', 'reduced error rate by 40%').")
    if missing_sections:
        weaknesses.append(f"Missing essential ATS section headers: {', '.join(missing_sections)}.")
    weaknesses.append(f"Bullet points need stronger action verbs tailored for '{target_role}' (e.g. 'Architected', 'Deployed', 'Engineered', 'Optimized').")

    roadmap = []
    roadmap.append(f"Step 1: Add a dedicated 'Technical Skills' section containing missing keywords for {target_role}: {', '.join(missing_keywords[:4])}.")
    if not has_quantifiable_metrics:
        roadmap.append("Step 2: Add exact numerical metrics to your project bullets (e.g. 'Optimized model accuracy to 94%', 'Accelerated search runtime by 40%').")
    roadmap.append(f"Step 3: Rewrite your project bullet points using strong action verbs relevant to {target_role} ('Architected', 'Deployed', 'Engineered').")
    if missing_sections:
        roadmap.append(f"Step 4: Create standard section headers for ATS screeners: {', '.join(missing_sections)}.")
    roadmap.append("Step 5: Format in standard 1-page layout using clean single-column structure and standard fonts (Calibri/Arial 10-11pt).")

    return {
        "ats_score": ats_score,
        "summary_verdict": f"Evaluated resume specifically against target role '{target_role}'. Achieved an ATS score of {ats_score}/100 with {len(present_keywords)} key skills matched and {len(missing_keywords)} critical keywords missing for this role.",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "missing_keywords": missing_keywords[:6],
        "improvement_roadmap": roadmap
    }


# ----------------- REPORT EXPORTERS -----------------

def export_resume_analysis_report(analysis_data, original_filename="Resume"):
    """
    Exports full AI Resume Analysis & Career Roadmap into formatted DOCX and PDF documents.
    """
    ensure_resume_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    docx_path = os.path.join(RESUME_DIR, f"Resume_AI_Analysis_{timestamp}.docx")
    pdf_path = os.path.join(RESUME_DIR, f"Resume_AI_Analysis_{timestamp}.pdf")

    # Export DOCX
    try:
        import docx
        from docx.shared import Inches, Pt, RGBColor

        doc = docx.Document()
        for s in doc.sections:
            s.top_margin = Inches(0.75)
            s.bottom_margin = Inches(0.75)
            s.left_margin = Inches(0.75)
            s.right_margin = Inches(0.75)

        title_p = doc.add_paragraph()
        r = title_p.add_run("INTELLIGENT AI RESUME & CAREER ANALYSIS REPORT")
        r.font.name = "Arial"
        r.font.size = Pt(18)
        r.font.bold = True
        r.font.color.rgb = RGBColor(2, 6, 23)

        sub_p = doc.add_paragraph()
        r_sub = sub_p.add_run(f"ATS Score: {analysis_data.get('ats_score', 80)}/100  |  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        r_sub.font.size = Pt(11)
        r_sub.font.bold = True
        r_sub.font.color.rgb = RGBColor(0, 136, 204)

        doc.add_heading("Executive Verdict", level=1)
        doc.add_paragraph(analysis_data.get("summary_verdict", ""))

        doc.add_heading("Key Strengths & Highlights", level=1)
        for item in analysis_data.get("strengths", []):
            doc.add_paragraph(item, style='List Bullet')

        doc.add_heading("Weaknesses & Red Flags to Fix", level=1)
        for item in analysis_data.get("weaknesses", []):
            doc.add_paragraph(item, style='List Bullet')

        doc.add_heading("Missing High-Demand Keywords", level=1)
        for item in analysis_data.get("missing_keywords", []):
            doc.add_paragraph(item, style='List Bullet')

        doc.add_heading("Actionable Step-by-Step Improvement Roadmap", level=1)
        for item in analysis_data.get("improvement_roadmap", []):
            doc.add_paragraph(item, style='List Bullet')

        doc.save(docx_path)
        print(f"[RESUME REPORT] DOCX saved to {docx_path}")
    except Exception as e:
        print(f"[RESUME REPORT DOCX ERROR] {e}")
        docx_path = None

    # Export PDF
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable

        pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor("#020617"), spaceAfter=4)
        sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#0088cc"), spaceAfter=10)
        h1_style = ParagraphStyle('H1', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#020617"), spaceBefore=10, spaceAfter=4)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13.5, textColor=colors.HexColor("#1e293b"), spaceAfter=4)
        bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#1e293b"), leftIndent=15, firstLineIndent=-10, spaceAfter=3)

        story = []
        story.append(Paragraph("INTELLIGENT AI RESUME & CAREER ANALYSIS REPORT", title_style))
        story.append(Paragraph(f"ATS Score: <b>{analysis_data.get('ats_score', 80)}/100</b>  |  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0088cc"), spaceAfter=10))

        story.append(Paragraph("Executive Verdict", h1_style))
        story.append(Paragraph(analysis_data.get("summary_verdict", ""), body_style))

        story.append(Paragraph("Key Strengths & Highlights", h1_style))
        for item in analysis_data.get("strengths", []):
            story.append(Paragraph(f"• {item}", bullet_style))

        story.append(Paragraph("Weaknesses & Red Flags to Fix", h1_style))
        for item in analysis_data.get("weaknesses", []):
            story.append(Paragraph(f"• {item}", bullet_style))

        story.append(Paragraph("Missing High-Demand Keywords", h1_style))
        for item in analysis_data.get("missing_keywords", []):
            story.append(Paragraph(f"• {item}", bullet_style))

        story.append(Paragraph("Actionable Step-by-Step Improvement Roadmap", h1_style))
        for item in analysis_data.get("improvement_roadmap", []):
            story.append(Paragraph(f"• {item}", bullet_style))

        pdf_doc.build(story)
        print(f"[RESUME REPORT] PDF saved to {pdf_path}")
    except Exception as e:
        print(f"[RESUME REPORT PDF ERROR] {e}")
        pdf_path = None

    return docx_path, pdf_path


# ----------------- RESUME ANALYZER DIALOG UI -----------------

class ResumeAnalyzerDialog(QDialog):
    """
    Cyberpunk UI Dialog for Resume Upload, Gemini AI ATS Evaluation,
    Weakness Analysis, and Step-by-Step Improvement Roadmap.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("INTELLIGENT AI RESUME ANALYZER & CAREER BUILDER")
        self.resize(950, 660)
        ensure_resume_dir()

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
            QPushButton#analyze_btn {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
                border-color: #00ff88;
            }
            QPushButton#analyze_btn:hover {
                background: rgba(0, 255, 136, 0.5);
                color: #ffffff;
            }
            QLineEdit {
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
                font-size: 13px;
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

        self.uploaded_filepath = None
        self.resume_text = ""
        self.current_analysis_data = None
        self.generated_docx = None
        self.generated_pdf = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        title = QLabel("🚀 INTELLIGENT AI RESUME ANALYZER & CAREER ROADMAP BUILDER")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        top_bar = QHBoxLayout()

        upload_btn = QPushButton("📄 UPLOAD RESUME (PDF/DOCX)")
        upload_btn.clicked.connect(self._upload_resume_file)
        top_bar.addWidget(upload_btn)

        self.file_label = QLabel("No resume selected")
        self.file_label.setStyleSheet("color: #94a3b8; font-weight: bold;")
        top_bar.addWidget(self.file_label)

        role_label = QLabel("Target Job Role:")
        role_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        top_bar.addWidget(role_label)

        self.role_input = QLineEdit()
        self.role_input.setText("Full Stack Python & AI Engineer")
        top_bar.addWidget(self.role_input)

        analyze_btn = QPushButton("🚀 ANALYZE RESUME")
        analyze_btn.setObjectName("analyze_btn")
        analyze_btn.clicked.connect(self._run_analysis)
        top_bar.addWidget(analyze_btn)

        layout.addLayout(top_bar)

        score_layout = QHBoxLayout()
        score_title = QLabel("ATS READINESS SCORE:")
        score_title.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        score_title.setStyleSheet("color: #00ffff;")
        score_layout.addWidget(score_title)

        self.score_bar = QProgressBar()
        self.score_bar.setRange(0, 100)
        self.score_bar.setValue(0)
        self.score_bar.setFormat("Upload Resume & Click Analyze")
        score_layout.addWidget(self.score_bar)

        layout.addLayout(score_layout)

        self.tabs = QTabWidget()

        self.strengths_edit = QTextEdit()
        self.strengths_edit.setPlaceholderText("Executive summary and key resume strengths will be displayed here...")
        self.tabs.addTab(self.strengths_edit, "💪 STRENGTHS & HIGHLIGHTS")

        self.weaknesses_edit = QTextEdit()
        self.weaknesses_edit.setStyleSheet("color: #ff4466;")
        self.weaknesses_edit.setPlaceholderText("Resume flaws, passive language, and missing metrics will be listed here...")
        self.tabs.addTab(self.weaknesses_edit, "⚠️ WEAKNESSES & RED FLAGS")

        self.keywords_edit = QTextEdit()
        self.keywords_edit.setStyleSheet("color: #eab308;")
        self.keywords_edit.setPlaceholderText("Missing high-demand industry skills for your target role will appear here...")
        self.tabs.addTab(self.keywords_edit, "🛠️ MISSING KEYWORDS")

        self.roadmap_edit = QTextEdit()
        self.roadmap_edit.setStyleSheet("color: #00ff88;")
        self.roadmap_edit.setPlaceholderText("Actionable step-by-step instructions to make your resume top 1% strong will appear here...")
        self.tabs.addTab(self.roadmap_edit, "🚀 IMPROVEMENT ROADMAP")

        layout.addWidget(self.tabs)

        bottom_bar = QHBoxLayout()

        self.status_label = QLabel("Status: Select a PDF/DOCX resume file to begin AI analysis.")
        self.status_label.setStyleSheet("color: #94a3b8;")
        bottom_bar.addWidget(self.status_label)

        open_folder_btn = QPushButton("📁 OPEN FOLDER")
        open_folder_btn.clicked.connect(self._open_folder)
        bottom_bar.addWidget(open_folder_btn)

        self.export_btn = QPushButton("📄 EXPORT AI REPORT (DOCX/PDF)")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._export_report)
        bottom_bar.addWidget(self.export_btn)

        layout.addLayout(bottom_bar)

    def _upload_resume_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Resume File", "", "Resume Files (*.pdf *.docx *.txt);;All Files (*)"
        )
        if file_path:
            self.uploaded_filepath = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.resume_text = extract_resume_text(file_path)
            self.status_label.setText(f"Status: Loaded '{os.path.basename(file_path)}' ({len(self.resume_text)} characters). Click 'ANALYZE RESUME'.")

    def _run_analysis(self):
        if not self.resume_text:
            if self.uploaded_filepath:
                self.resume_text = extract_resume_text(self.uploaded_filepath)
            else:
                QMessageBox.warning(self, "No Resume Uploaded", "Please upload a PDF or DOCX resume file first.")
                return

        target_role = self.role_input.text().strip() or "Software Engineer"
        self.status_label.setText("Status: 🤖 Gemini AI is performing deep ATS evaluation & generating career roadmap...")
        QApplication.processEvents()

        analysis_data = analyze_resume_with_gemini(self.resume_text, target_role=target_role)
        self.current_analysis_data = analysis_data

        ats_score = analysis_data.get("ats_score", 75)
        self.score_bar.setValue(ats_score)
        self.score_bar.setFormat(f"ATS Score: {ats_score}/100")

        s_text = f"=== EXECUTIVE VERDICT ===\n{analysis_data.get('summary_verdict', '')}\n\n=== KEY STRENGTHS ===\n"
        s_text += "\n".join([f"• {item}" for item in analysis_data.get("strengths", [])])
        self.strengths_edit.setPlainText(s_text)

        w_text = f"=== WEAKNESSES & RED FLAGS ===\n"
        w_text += "\n".join([f"• {item}" for item in analysis_data.get("weaknesses", [])])
        self.weaknesses_edit.setPlainText(w_text)

        k_text = f"=== MISSING HIGH-DEMAND KEYWORDS FOR '{target_role.upper()}' ===\n"
        k_text += "\n".join([f"• {item}" for item in analysis_data.get("missing_keywords", [])])
        self.keywords_edit.setPlainText(k_text)

        r_text = f"=== ACTIONABLE STEP-BY-STEP IMPROVEMENT ROADMAP ===\n"
        r_text += "\n".join([f"• {item}" for item in analysis_data.get("improvement_roadmap", [])])
        self.roadmap_edit.setPlainText(r_text)

        self.export_btn.setEnabled(True)
        self.status_label.setText("Status: ✨ Resume Analysis complete! Review recommendations or export report.")
        try:
            from voice_engine import speak
            speak(f"Resume analysis complete. Your ATS score is {ats_score} out of 100. Step-by-step improvement roadmap generated.")
        except Exception:
            pass

    def _export_report(self):
        if not self.current_analysis_data:
            return

        docx_p, pdf_p = export_resume_analysis_report(self.current_analysis_data, self.uploaded_filepath or "Resume")
        self.generated_docx = docx_p
        self.generated_pdf = pdf_p
        self.status_label.setText(f"Status: Reports saved in {RESUME_DIR}")
        QMessageBox.information(self, "Reports Exported", f"AI Analysis Reports saved successfully:\n• DOCX: {os.path.basename(docx_p)}\n• PDF: {os.path.basename(pdf_p)}")

    def _open_folder(self):
        if os.path.exists(RESUME_DIR):
            os.startfile(RESUME_DIR)
