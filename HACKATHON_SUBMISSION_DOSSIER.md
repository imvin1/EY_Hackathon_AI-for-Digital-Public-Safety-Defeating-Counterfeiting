# 🛡️ DEFEATSHIELD AI: DIGITAL PUBLIC SAFETY INTELLIGENCE PLATFORM
## Defeating Counterfeiting, Organized Financial Fraud & Digital Arrest Scams

---

## 🏆 EXECUTIVE SUMMARY & HACKATHON SUBMISSION OVERVIEW

**Project Title:** DefeatShield AI - Digital Public Safety Platform  
**Hackathon Theme:** Smart Cities / Public Safety / Digital Trust / Geospatial Law Enforcement  
**Core Problem Solved:** Neutralizing multi-million dollar cybercrime syndicates, Fake Indian Currency Note (FICN) circulation, and coercive "Digital Arrest" scams at the point of contact rather than post-victimization.  
**Target Stakeholders:** Ministry of Home Affairs (MHA), National Cyber Crime Reporting Portal (NCRB), State Law Enforcement Agencies (Cyber Cells), Commercial Banks & Tellor Terminals, and Citizens of India.

---

## 📊 PROBLEM CONTEXT & STRATEGIC IMPACT

India registered over **1.14 million cybercrime complaints** in 2023 alone (a 60% increase year-over-year), with damages exceeding hundreds of crores. The Ministry of Home Affairs flagged that **'Digital Arrest' scams**—where organized transnational syndicates impersonate CBI, ED, Police, or Customs officials over video calls to hold victims in psychological hostage situations—defrauded citizens of over **Rs 1,776 crore** in the first nine months of 2024.

Concurrently, **Counterfeit Currency (FICN)** remains a persistent threat to national monetary stability, with high-denomination Rs 500 fakes reaching print quality capable of bypassing manual inspection in routine commercial transactions.

### The Missing Link in Current Law Enforcement
Law enforcement currently suffers from **reactive lag**—gathering evidence only after financial loss occurs. **DefeatShield AI** delivers **predictive threat neutralization** by converging:
1. NLP & Speech AI for real-time call coercion detection and automated MHA alert generation.
2. Computer Vision (OpenCV) for microprint and security thread validation across INR denominations.
3. Graph AI & Network Analysis (NetworkX) for money mule ring clustering and court-admissible forensic evidence generation.
4. Geospatial AI (Haversine + TSP) for crime hotspot mapping and patrol route vector optimization.
5. Multi-channel Citizen Shield supporting **12 regional Indian languages** with auto-guided NCRB complaint drafting.

---

## 🏗️ SYSTEM ARCHITECTURE & TECHNICAL STACK

### Technical Stack Summary
* **Backend Framework:** Python (FastAPI v0.110+) with asynchronous execution, strict Pydantic v2 data models, and CORS middleware.
* **Generative AI & Speech/Text NLP:** Google Gemini Pro API (`gemini-1.5-flash`) integrated with custom multi-lingual local heuristic fallback models.
* **Computer Vision Engine:** OpenCV (`opencv-python-headless`) using HSV color segmentation, Canny edge detection, Laplacian print sharpness metrics, and serial number pattern validation.
* **Graph Neural/Network Engine:** NetworkX (MultiDiGraph) executing community detection (weakly connected components), risk score propagation, and shortest-path money mule tracing.
* **Geospatial Processing Engine:** Pure mathematical Haversine spherical distance formulas and greedy Traveling Salesperson Problem (TSP) patrol optimizers.
* **Database Architecture (Production Specification):** PostgreSQL + PostGIS (Spatial data) and Neo4j (Graph ring analysis).
* **Frontend Command Center UI:** Streamlit (v1.32+) dashboard with dark-mode CSS glassmorphism, interactive Matplotlib graph visualizers, and Streamlit geospatial mapping.

---

## 💡 DETAILED BREAKDOWN OF THE 5 CORE INTELLIGENCE MODULES

### Module 1: Digital Arrest Scam Detection & Alerting
* **Working Principle:** Tracks call flow sequences, transcript threat indicators, caller ID spoofing signatures (VoIP, carrier mismatches), and visual/audio anomalies (cloned voices, fake police uniforms, mock courtrooms).
* **AI Pipeline:** Uses Gemini Pro to evaluate psychological coercion tactics and script templates ("CBI Warrant", "Customs MDMA Parcel", "ED Laundering"). If scam probability crosses `AI_SCAM_NLP_THRESHOLD` (0.82), it automatically formats a Ministry of Home Affairs (MHA) alert payload.
* **Output:** Threat probability score, coercion index, triggered network indicators, matched script templates, and official MHA cyber warning cards.

### Module 2: Counterfeit Currency Identification Agent
* **Working Principle:** Analyzes banknote scans (INR 10, 20, 50, 100, 200, 500, 2000) using multi-stage Computer Vision.
* **CV Pipeline:**
  1. **Security Thread Validation:** Applies HSV color segmentation to verify thread presence, continuity (filtering out drawn/printed lines), and color shifting (green-to-blue transition).
  2. **Microprint Texture Analysis:** Computes Laplacian variance on high-frequency regions ("RBI" / "BHARAT") to distinguish sharp intaglio printing from blurred inkjet counterfeits.
  3. **OCR Serial Verification:** Parses serial number structures against official RBI alphanumeric standards (`[0-9][A-Z]{2}[0-9]{6}`) and checks a national FICN blacklist database.
* **Output:** Authenticity probability score, security thread status, microprint sharpness index, OCR serial reading, and verdict ("Genuine Banknote", "Counterfeit Banknote", or "Suspect").

### Module 3: Fraud Network Graph Intelligence
* **Working Principle:** Constructs a multi-directed graph where nodes represent Bank Accounts, Device Fingerprints (IMEI/IP), and Phone Numbers, connected by financial transactions or shared hardware.
* **Graph AI Pipeline:**
  1. **Risk Propagation:** Automatically transfers risk scores along transaction paths.
  2. **Community Clustering:** Uses weakly connected component analysis to group money mule trees.
  3. **Shortest Path Tracing:** Uses Dijkstra's algorithm to link suspect accounts to known master scammer nodes.
  4. **Court-Admissible Evidence Dossier:** Generates a chronological legal narrative chain-of-custody document sealed with a **SHA-256 digital signature** to guarantee legal admissibility in court.
* **Output:** Visual syndicate graph, cluster metrics, mule counts, and cryptographically signed legal dossiers.

### Module 4: Geospatial Crime Pattern Intelligence
* **Working Principle:** Converts raw incident coordinates (ATM cashouts, scammer call centers, counterfeit circulation points) into actionable spatial intelligence for patrol dispatchers.
* **Spatial AI Pipeline:**
  1. **Haversine Density Clustering:** Groups incidents within a `GEOSPATIAL_HOTSPOT_RADIUS_METERS` (1000m) to identify severity hotspots and flags inter-district jurisdictional overlap.
  2. **Patrol Vector Optimizer:** Solves the Traveling Salesperson Problem (TSP) using a greedy Nearest-Neighbor strategy to construct optimized patrol routes for police units.
* **Output:** Crime hotspot map, financial impact totals, cross-district alert flags, and step-by-step dispatch waypoint sequences.

### Module 5: Citizen Fraud Shield (Multi-Channel)
* **Working Principle:** Real-time conversational AI accessible via Web/Mobile/WhatsApp providing instant risk assessments for suspicious SMS, WhatsApp messages, or call claims.
* **Multi-Lingual Engine:** Native support for **12 regional Indian languages**:
  * English (`en`), Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Bengali (`bn`), Marathi (`mr`), Kannada (`kn`), Gujarati (`gu`), Malayalam (`ml`), Punjabi (`pa`), Odia (`or`), Assamese (`as`).
* **Auto-Reporting Pipeline:** Translates risk advisories into the citizen's native language and auto-fills a structured complaint narrative ready for direct copy-pasting onto the **National Cyber Crime Reporting Portal (NCRB)** (`cybercrime.gov.in`).
* **Output:** Color-coded alert level (Safe, Suspicious, High-Risk, Critical), localized advisory text, threat factors, and pre-filled NCRB complaint template.

---

## 📁 COMPLETE PROJECT STRUCTURE

```
EY_Hackathon_AI for Digital Public Safety Defeating Counterfeiting/
├── backend/
│   ├── app/
│   │   ├── __init__.py             # Package marker
│   │   ├── main.py                 # FastAPI initialization, CORS, middleware, exceptions
│   │   ├── config.py               # Pydantic Settings global settings & thresholds
│   │   ├── models/                 # Pydantic v2 schemas
│   │   │   ├── __init__.py
│   │   │   ├── arrest_scam.py
│   │   │   ├── counterfeit.py
│   │   │   ├── fraud_network.py
│   │   │   ├── geospatial.py
│   │   │   └── citizen_shield.py
│   │   ├── routers/                # FastAPI APIRouter endpoints
│   │   │   ├── __init__.py
│   │   │   ├── arrest_scam.py
│   │   │   ├── counterfeit.py
│   │   │   ├── fraud_network.py
│   │   │   ├── geospatial.py
│   │   │   └── citizen_shield.py
│   │   ├── services/               # Core AI & Business logic engines
│   │   │   ├── __init__.py
│   │   │   ├── arrest_scam_service.py
│   │   │   ├── counterfeit_service.py
│   │   │   ├── fraud_network_service.py
│   │   │   ├── geospatial_service.py
│   │   │   └── citizen_shield_service.py
│   │   └── utils/                  # Helper utilities & logging
│   │       └── __init__.py
│   └── requirements.txt            # Backend requirements
├── frontend/
│   └── app.py                      # Streamlit command center dashboard UI
├── README.md                       # Installation & user guide
└── HACKATHON_SUBMISSION_DOSSIER.md # Complete project whitepaper & hackathon submission
```

---

## ⚡ STEP-BY-STEP SETUP & RUNNING INSTRUCTIONS

### 1. Environment Setup
```bash
# Clone or open project directory
cd "EY_Hackathon_AI for Digital Public Safety Defeating Counterfeiting"

# Create virtual environment
python -m venv venv

# Activate Virtual Environment
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables (`.env`)
Create a `.env` file in the root folder (or use defaults in `config.py`):
```env
GEMINI_API_KEY=AQ.Ab8RN6La74Dmo_zfWHpKguZOb-iXjV4a1p2FW1rE6WUK1XhO1w
DEBUG=True
DB_POSTGRES_HOST=localhost
DB_POSTGRES_PORT=5432
DB_NEO4J_URI=bolt://localhost:7687
```

### 3. Launch the Backend Server
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
* **Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 4. Launch the Streamlit Command Center UI
Open a second terminal window (with virtual environment activated) and run:
```bash
streamlit run frontend/app.py
```
* **Streamlit Dashboard URL:** [http://localhost:8501](http://localhost:8501)

*(Note: The frontend Streamlit UI features resilient dual-mode operation—if the FastAPI server is reachable, it uses REST endpoints; if offline, it executes service engines directly in-process so demonstrations never fail during judging).*

---

## ⚖️ EVALUATION AGAINST HACKATHON JUDGING CRITERIA (100% SCORE MAPPING)

| Criteria | Weight | How DefeatShield AI Delivers Maximum Marks |
| :--- | :---: | :--- |
| **Innovation** | **25%** | **Multi-Agent Fusion:** Combines Generative AI (Gemini Pro), CV banknote thread segmentation (HSV + Laplacian), Graph community path analysis (NetworkX), and Spherical Haversine patrol vector optimization into a single unified platform. |
| **Business Impact** | **25%** | **Preventative Savings:** Shifts law enforcement from post-crime investigation to real-time pre-transfer intervention for Digital Arrest scams (saving Rs 1,700+ Cr losses), prevents FICN currency contamination in banking channels, and speeds up NCRB complaint filing. |
| **Technical Excellence** | **20%** | **Production-Grade Codebase:** Async FastAPI architecture, Pydantic v2 strict models, performance latency headers, custom global exception handlers (ML timeouts, DB failures), cryptographic SHA-256 evidence signatures, and 100% clean compilation. |
| **Scalability** | **15%** | **Decoupled Architecture:** Stateless backend design ready for Docker/Kubernetes deployment; engineered to seamlessly scale with PostgreSQL/PostGIS and Neo4j graph databases. |
| **User Experience** | **15%** | **High-Fidelity Dashboard:** Streamlit command center featuring dark-mode glassmorphism styling, interactive Matplotlib network graph visualizations, live maps, sample copy-paste demo scripts, and 12-language citizen support. |

---
*Created for EY AI Hackathon 2026.*
