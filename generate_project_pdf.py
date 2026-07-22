from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "DefeatShield_AI_Project_Details.pdf"

styles = getSampleStyleSheet()
style_title = styles['Title']
style_title.fontSize = 20
style_title.leading = 24
style_body = styles['BodyText']
style_body.fontSize = 10.5
style_body.leading = 14
style_heading = styles['Heading2']
style_heading.fontSize = 13
style_heading.leading = 16

content = []
content.append(Paragraph("DefeatShield AI - Project Details", style_title))
content.append(Paragraph("AI-powered digital public safety platform for countering counterfeit currency, fraud rings, and digital arrest scams", style_body))
content.append(Spacer(1, 10))

sections = [
    ("1. Project Overview", "DefeatShield AI is a multi-module public safety platform developed for the EY AI Hackathon. It combines AI-driven analysis, computer vision, fraud network intelligence, geospatial optimization, and citizen protection workflows into a single command-center experience."),
    ("2. Core Objectives", "Protect citizens from digital arrest scams, detect counterfeit banknotes, expose fraud networks, optimize patrol deployment, and provide a citizen-facing fraud shield."),
    ("3. Tech Stack", "Frontend: Streamlit; Backend: FastAPI, Uvicorn, Pydantic v2; AI/ML: Google Gemini, OpenCV, NetworkX, NumPy, Pandas, Matplotlib; Database/Infra: SQLAlchemy, PostgreSQL, Neo4j-ready architecture"),
    ("4. Project Structure", "frontend/app.py: Streamlit dashboard entry point; backend/app/main.py: FastAPI application entry point; backend/app/routers/: API routing layer; backend/app/services/: business logic and AI workflows; backend/app/models/: Pydantic request/response schemas"),
    ("5. Run Instructions", "From the project root, run: python -m streamlit run app.py. To run the backend API, use: python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000"),
    ("6. Notes", "The Streamlit app uses a root launcher file so it can be started directly from the workspace folder without path-related issues. If a dependency is missing, install it from backend/requirements.txt."),
]

for title, body in sections:
    content.append(Paragraph(title, style_heading))
    content.append(Paragraph(body, style_body))
    content.append(Spacer(1, 6))

content.append(PageBreak())
content.append(Paragraph("Summary", style_heading))
content.append(Paragraph("This project demonstrates how AI, data science, and secure software engineering can work together to strengthen digital public safety and incident response workflows.", style_body))

doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
doc.build(content)
print(f"PDF created: {OUTPUT}")
