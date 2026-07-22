import logging
import uuid
from datetime import datetime
import google.generativeai as genai
from typing import Dict, Any, Tuple, List

from backend.app.config import settings
from backend.app.models.citizen_shield import (
    CitizenRiskQuery,
    CitizenRiskResponse,
    NcrbReportingGuide
)

logger = logging.getLogger("defeatshield.citizen_shield_service")

class CitizenShieldService:
    def __init__(self):
        # Configure Gemini API
        self.use_gemini = False
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_gemini = True
                logger.info("Gemini API successfully configured for Citizen Shield service.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini API client. Using local multi-lingual database: {e}")
        else:
            logger.warning("No Gemini API Key provided. Using local multi-lingual database.")

        # Multi-lingual local fallback advisories (12 languages)
        self.language_advisories: Dict[str, Dict[str, str]] = {
            "en": {
                "safe": "This contact seems safe. No indicators of scam found.",
                "suspicious": "CRITICAL ADVISORY: This message contains pressure tactics. Do NOT click any links, do NOT share OTPs, and do NOT send money. Report immediately.",
                "draft_complaint": "I received a suspicious message claiming to represent {source}. They requested me to {action} immediately. I suspect this is a scam."
            },
            "hi": {
                "safe": "यह संदेश सुरक्षित प्रतीत होता है। धोखाधड़ी का कोई संकेत नहीं मिला।",
                "suspicious": "महत्वपूर्ण सलाह: इस संदेश में दबाव बनाने की कोशिश की गई है। किसी भी लिंक पर क्लिक न करें, ओटीपी साझा न करें, और पैसे न भेजें। तुरंत रिपोर्ट करें।",
                "draft_complaint": "मुझे {source} का प्रतिनिधित्व करने का दावा करने वाला एक संदिग्ध संदेश मिला। उन्होंने मुझसे तुरंत {action} करने का अनुरोध किया। मुझे संदेह है कि यह एक घोटाला है।"
            },
            "ta": {
                "safe": "இந்தத் தொடர்பு பாதுகாப்பானது எனத் தெரிகிறது. மோசடி குறிப்புகள் எதுவும் இல்லை.",
                "suspicious": "முக்கிய ஆலோசனை: இந்தச் செய்தி உங்களை வற்புறுத்தும் தொனியில் உள்ளது. எந்த இணைப்பையும் கிளிக் செய்ய வேண்டாம், OTP-ஐப் பகிர வேண்டாம், பணம் அனுப்ப வேண்டாம். உடனே புகாரளிக்கவும்.",
                "draft_complaint": "{source} இலிருந்து பேசுவதாகக் கூறி எனக்கு ஒரு சந்தேகத்திற்கிடமான செய்தி வந்தது. அவர்கள் என்னை உடனடியாக {action} செய்யச் சொன்னார்கள். இது மோசடி என சந்தேகிக்கிறேன்."
            },
            "te": {
                "safe": "ఈ సంప్రదింపు సురక్షితంగా ఉన్నట్లు అనిపిస్తుంది. ఎలాంటి మోసం గుర్తులు లేవు.",
                "suspicious": "ముఖ్యమైన సలహా: ఈ సందేశంలో ఒత్తిడి తెచ్చే వ్యూహాలు ఉన్నాయి. లింక్‌లపై క్లిక్ చేయవద్దు, OTP షేర్ చేయవద్దు, డబ్బు పంపవద్దు. వెంటనే నివేదించండి.",
                "draft_complaint": "{source} ప్రతినిధిని అని క్లెయిమ్ చేస్తూ నాకు అనుమానాస్పద సందేశం వచ్చింది. వారు నన్ను వెంటనే {action} చేయమని కోరారు. ఇది మోసం అని నేను అనుమానిస్తున్నాను."
            },
            "bn": {
                "safe": "এই যোগাযোগটি নিরাপদ বলে মনে হচ্ছে। স্ক্যামের কোনো লক্ষণ পাওয়া যায়নি।",
                "suspicious": "গুরুত্বপূর্ণ পরামর্শ: এই বার্তায় চাপ সৃষ্টির কৌশল রয়েছে। কোনো লিঙ্কে ক্লিক করবেন না, ওটিপি শেয়ার করবেন না এবং টাকা পাঠাবেন না। অবিলম্বে রিপোর্ট করুন।",
                "draft_complaint": "আমি {source} এর প্রতিনিধি দাবি করে একটি সন্দেহজনক বার্তা পেয়েছি। তারা আমাকে অবিলম্বে {action} করার অনুরোধ করেছিল। আমার সন্দেহ এটি একটি প্রতারণা।"
            },
            "mr": {
                "safe": "हा संपर्क सुरक्षित वाटतो. फसवणुकीचे कोणतेही संकेत आढळले नाहीत.",
                "suspicious": "महत्त्वाची सूचना: या संदेशात दबावाचे तंत्र वापरले आहे. कोणत्याही लिंकवर क्लिक करू नका, ओटीपी शेअर करू नका आणि पैसे पाठवू नका. त्वरित तक्रार करा.",
                "draft_complaint": "मला {source} चे प्रतिनिधित्व करत असल्याचा दावा करणारा संशयास्पद संदेश मिळाला. त्यांनी मला त्वरित {action} करण्यास सांगितले. ही फसवणूक असावी असा संशय आहे."
            },
            "kn": {
                "safe": "ಈ ಸಂಪರ್ಕವು ಸುರಕ್ಷಿತವಾಗಿದೆ ಎಂದು ತೋರುತ್ತದೆ. ಯಾವುದೇ ವಂಚನೆ ಲಕ್ಷಣಗಳಿಲ್ಲ.",
                "suspicious": "ಪ್ರಮುಖ ಸಲಹೆ: ಈ ಸಂದೇಶವು ಒತ್ತಡದ ತಂತ್ರಗಳನ್ನು ಒಳಗೊಂಡಿದೆ. ಯಾವುದೇ ಲಿಂಕ್ ಕ್ಲಿಕ್ ಮಾಡಬೇಡಿ, ಒಟಿಪಿ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ, ಹಣ ಕಳುಹಿಸಬೇಡಿ. ತಕ್ಷಣ ವರದಿ ಮಾಡಿ.",
                "draft_complaint": "{source} ಪ್ರತಿನಿಧಿಸುತ್ತಿರುವುದಾಗಿ ಹೇಳಿಕೊಳ್ಳುವ ಅನುಮಾನಾಸ್ಪದ ಸಂದೇಶ ನನಗೆ ಬಂದಿದೆ. ಅವರು ತಕ್ಷಣ {action} ಮಾಡಲು ವಿನಂತಿಸಿದರು. ಇದು ವಂಚನೆ ಎಂದು ನಾನು ಶಂಕಿಸುತ್ತೇನೆ."
            },
            "gu": {
                "safe": "આ સંપર્ક સુરક્ષિત લાગે છે. છેતરપિંડીના કોઈ સંકેતો મળ્યા નથી.",
                "suspicious": "મહત્વપૂર્ણ સલાહ: આ સંદેશમાં દબાણ લાવવાની યુક્તિઓ છે. કોઈ લિંક પર ક્લિક કરશો નહીં, OTP શેર કરશો નહીં, અને પૈસા મોકલશો નહીં. તરત જ રિપોર્ટ કરો.",
                "draft_complaint": "મને {source} હોવાનો દાવો કરતો એક શંકાસ્પદ સંદેશ મળ્યો. તેમણે મને તરત જ {action} કરવા વિનંતી કરી. મને શંકા છે કે આ છેતરપિંડી છે."
            },
            "ml": {
                "safe": "ഈ കോൺടാക്റ്റ് സുരക്ഷിതമാണെന്ന് തോന്നുന്നു. തട്ടിപ്പ് സൂചനകളൊന്നുമില്ല.",
                "suspicious": "പ്രധാന ഉപദേശം: ഈ സന്ദേശത്തിൽ ഭീഷണിപ്പെടുത്തുന്ന സ്വഭാവമുണ്ട്. ലിങ്കുകളിൽ ക്ലിക്ക് ചെയ്യരുത്, OTP പങ്കിടരുത്, പണം അയക്കരുത്. ഉടനടി റിപ്പോർട്ട് ചെയ്യുക.",
                "draft_complaint": "{source} നെ പ്രതിനിധീകരിക്കുന്നു എന്ന് അവകാശപ്പെടുന്ന സംശയാസ്പദമായ സന്ദേശം എനിക്ക് ലഭിച്ചു. അവർ എന്നോട് ഉടനടി {action} ചെയ്യാൻ ആവശ്യപ്പെട്ടു. ഇതൊരു തട്ടിപ്പാണെന്ന് ഞാൻ സംശയിക്കുന്നു."
            },
            "pa": {
                "safe": "ਇਹ ਸੰਪਰਕ ਸੁਰੱਖਿਅਤ ਜਾਪਦਾ ਹੈ। ਕਿਸੇ ਧੋਖਾਧੜੀ ਦਾ ਕੋਈ ਸੰਕੇਤ ਨਹੀਂ ਮਿਲਿਆ।",
                "suspicious": "ਮਹੱਤਵਪੂਰਨ ਸਲਾਹ: ਇਸ ਸੁਨੇਹੇ ਵਿੱਚ ਦਬਾਅ ਬਣਾਉਣ ਦੀ ਕੋਸ਼ਿਸ਼ ਕੀਤੀ ਗਈ ਹੈ। ਲਿੰਕਾਂ 'ਤੇ ਕਲਿੱਕ ਨਾ ਕਰੋ, OTP ਸਾਂਝਾ ਨਾ ਕਰੋ, ਅਤੇ ਪੈਸੇ ਨਾ ਭੇਜੋ। ਤੁਰੰਤ ਰਿਪੋਰਟ ਕਰੋ।",
                "draft_complaint": "ਮੈਨੂੰ {source} ਦੀ ਨੁਮਾਇੰਦਗੀ ਕਰਨ ਦਾ ਦਾਅਵਾ ਕਰਨ ਵਾਲਾ ਇੱਕ ਸ਼ੱਕੀ ਸੁਨੇਹਾ ਮਿਲਿਆ ਹੈ। ਉਹਨਾਂ ਨੇ ਮੈਨੂੰ ਤੁਰੰत {action} ਕਰਨ ਲਈ ਕਿਹਾ। ਮੈਨੂੰ ਸ਼ੱਕ ਹੈ ਕਿ ਇਹ ਧੋਖਾਧੜੀ ਹੈ।"
            },
            "or": {
                "safe": "ଏହି ଯୋଗାଯୋଗ ସୁରକ୍ଷିତ ମନେହୁଏ। କୌଣସି ଠକେଇର ସୂଚନା ମିଳିନାହିଁ ।",
                "suspicious": "ଗୁରୁତ୍ୱପୂର୍ଣ୍ଣ ପରାମର୍ଶ: ଏହି ବାର୍ତ୍ତାରେ ଚାପ ପ୍ରୟୋଗ କୌଶଳ ରହିଛି। କୌଣସି ଲିଙ୍କ କ୍ଲିକ୍ କରନ୍ତୁ ନାହିଁ, OTP ସେୟାର କରନ୍ତୁ ନାହିଁ ଏବଂ ଟଙ୍କା ପଠାନ୍ତୁ ନାହିଁ । ତୁରନ୍ତ ରିପୋର୍ଟ କରନ୍ତୁ।",
                "draft_complaint": "ମୋତେ {source} ର ପ୍ରତିନିଧି ଦାବି କରି ଏକ ସନ୍ଦେହଜନକ ବାର୍ତ୍ତା ମିଳିଛି। ସେମାନେ ମୋତେ ତୁରନ୍ତ {action} କରିବାକୁ କହିଥିଲେ। ମୁଁ ସନ୍ଦେହ କରୁଛି ଏହା ଏକ ଠକେଇ।"
            },
            "as": {
                "safe": "এই যোগাযোগ সুৰক্ষিত যেন লাগিছে। কোনো জালিয়াতিৰ লক্ষণ পোৱা নগ'ল।",
                "suspicious": "গুৰুত্বপূৰ্ণ পৰামৰ্শ: এই বাৰ্তাটোত চাপ সৃষ্টি কৰাৰ কৌশল আছে। কোনো লিংকত ক্লিক নকৰিব, অ'টিপি শ্বেয়াৰ নকৰিব, আৰু ধন পঠিয়াব নালাগে। লগে লগে ৰিপৰ্ট কৰক।",
                "draft_complaint": "মই {source} ক প্ৰতিনিধিত্ব কৰা বুলি দাবী কৰা এটা সন্দেহজনক বাৰ্তা পাইছো। তেওঁলোকে মোক লগে লগে {action} কৰিবলৈ অনুৰোধ কৰিছিল। মই সন্দেহ কৰো এইটো এটা প্ৰৱঞ্চনা।"
            }
        }

    async def evaluate_risk(self, query: CitizenRiskQuery) -> CitizenRiskResponse:
        """
        Assesses a citizen's query about a potential scam contact,
        translates alerts and advisories dynamically, and prepares prefilled NCRB details.
        """
        lang = query.language_code.lower()
        if lang not in self.language_advisories:
            lang = "en"  # Default fallback

        raw_text = query.query_text
        sender_id = query.sender_identifier or "Unknown Sender"
        medium = query.input_medium.upper()

        # Step 1: Run core classification via LLM or fallback heuristics
        risk_score, scam_type, risk_factors = await self._classify_scam_urgency(raw_text, medium)

        # Map threat level
        if risk_score >= 0.80:
            risk_level = "CRITICAL"
        elif risk_score >= 0.60:
            risk_level = "HIGH_RISK"
        elif risk_score >= 0.30:
            risk_level = "SUSPICIOUS"
        else:
            risk_level = "SAFE"

        # Step 2: Build NCRB pre-filled guidelines
        ncrb_category = "Online Financial Fraud"
        ncrb_subcategory = "UPI/NetBanking Related Fraud"
        
        if scam_type == "Digital Arrest":
            ncrb_category = "Cyber Impersonation / Coercion"
            ncrb_subcategory = "Impersonating Police or Law Enforcement Officials"
        elif scam_type == "Phishing / Link Fraud":
            ncrb_category = "Online Financial Fraud"
            ncrb_subcategory = "Phishing Website / Malicious Link"
        elif scam_type == "Lottery / Part-time Job scam":
            ncrb_category = "Social Media Fraud"
            ncrb_subcategory = "Part-time Job scam"

        # Step 3: Get advisory text in target language
        advisory_msg = ""
        complaint_draft = ""

        if self.use_gemini:
            # Generate translated advisory and structured draft complaint using Gemini
            advisory_msg, complaint_draft = await self._generate_gemini_advisory(
                raw_text=raw_text,
                sender_id=sender_id,
                risk_level=risk_level,
                scam_type=scam_type,
                lang=lang
            )
        
        # Heuristic fallback if Gemini is disabled or failed
        if not advisory_msg or not complaint_draft:
            logger.info("Using local multilingual fallback database.")
            advisory_template = self.language_advisories[lang]["suspicious" if risk_score >= 0.3 else "safe"]
            advisory_msg = advisory_template
            
            source_term = "Unknown Authority"
            action_term = "transfer money / verify credentials"
            
            if "electric" in raw_text.lower() or "power" in raw_text.lower():
                source_term = "State Electricity Department"
                action_term = "pay unpaid bills immediately or power will be disconnected"
            elif "delivery" in raw_text.lower() or "fedex" in raw_text.lower() or "customs" in raw_text.lower():
                source_term = "Customs / Courier Hub"
                action_term = "pay clearance customs fees on illegal parcels"
            elif "part-time" in raw_text.lower() or "job" in raw_text.lower() or "telegram" in raw_text.lower():
                source_term = "Part-Time Recruitment Firm"
                action_term = "deposit security money to unlock premium tasks"
            elif "cbi" in raw_text.lower() or "police" in raw_text.lower() or "warrant" in raw_text.lower():
                source_term = "CBI / Police Officers"
                action_term = "log into a Skype video session under digital arrest"

            complaint_draft = self.language_advisories[lang]["draft_complaint"].format(
                source=source_term,
                action=action_term
            )
            
            # Append sender detail
            complaint_draft += f" [Details: Sender ID / Number: {sender_id}, Medium: {medium}]"

        ncrb_guide = NcrbReportingGuide(
            portal_category=ncrb_category,
            portal_subcategory=ncrb_subcategory,
            draft_complaint_text=complaint_draft,
            suggested_evidence_attachments=[
                f"Screenshot of {medium} message/call details",
                "Transaction receipt showing wallet transfers (if any)",
                "Sender identifier trace / headers"
            ]
        )

        return CitizenRiskResponse(
            query_id=query.query_id,
            risk_level=risk_level,
            risk_score=round(risk_score, 3),
            detected_scam_type=scam_type,
            risk_factors=risk_factors,
            dynamic_advisory=advisory_msg,
            ncrb_guide=ncrb_guide,
            timestamp=datetime.utcnow()
        )

    async def _classify_scam_urgency(self, text: str, medium: str) -> Tuple[float, str, List[str]]:
        """
        Heuristic classification mapping high risk indicators.
        Returns: (risk_score, scam_type, risk_factors)
        """
        text_lower = text.lower()
        score = 0.05
        scam_type = "Unspecified Risk"
        factors = []

        # Scenarios mapping
        # 1. Digital Arrest Coercion
        if any(x in text_lower for x in ["cbi", "supreme court", "digital arrest", "police custody", "drugs found", "contraband"]):
            score = max(score, 0.90)
            scam_type = "Digital Arrest"
            factors.append("IMPERSONATION_OF_LEO")
            factors.append("THREATS_OF_CUSTODY")

        # 2. Phishing link/Verification Scam
        elif any(x in text_lower for x in ["click here to update", "electricity bill", "power disconnect", "kyc update", "suspend account"]):
            score = max(score, 0.75)
            scam_type = "Phishing / Link Fraud"
            factors.append("ACCOUNT_SUSPENSION_SCAM")
            factors.append("URGENT_KYC_REQUEST")

        # 3. Part-time Job / Easy Money
        elif any(x in text_lower for x in ["part-time", "earn money daily", "like youtube video", "telegram task", "daily payout"]):
            score = max(score, 0.70)
            scam_type = "Lottery / Part-time Job scam"
            factors.append("PART_TIME_JOB_LURE")
            factors.append("EASY_MONEY_TRAP")

        if "http" in text_lower or ".com" in text_lower or ".in/" in text_lower:
            score = min(1.0, score + 0.10)
            factors.append("SUSPICIOUS_HYPERLINK")

        if any(x in text_lower for x in ["immediate", "hurry", "within 2 hours", "else your service"]):
            score = min(1.0, score + 0.15)
            factors.append("ARTIFICIAL_URGENCY_TTACTIC")

        return score, scam_type, factors

    async def _generate_gemini_advisory(
        self, 
        raw_text: str, 
        sender_id: str, 
        risk_level: str, 
        scam_type: str, 
        lang: str
    ) -> Tuple[str, str]:
        """
        Uses Gemini LLM to translate response advisories and generate structured drafts.
        """
        try:
            prompt = (
                f"Analyze the following suspicious fraud contact information:\n"
                f"Source Text: \"{raw_text}\"\n"
                f"Sender ID: \"{sender_id}\"\n"
                f"Scam Type: {scam_type}\n"
                f"Target Language Code: {lang}\n\n"
                "Return exactly two blocks of text, separated by '===SPLIT==='.\n"
                "Block 1: A brief 2-sentence citizen alert advisory explaining why this is suspicious, translated into the target language.\n"
                "Block 2: A pre-filled draft cyber crime complaint narrative (in English or the target language) suitable for copying into the India National Cyber Crime Portal (NCRB) detailing the facts of this scam attempt.\n"
            )

            response = self.gemini_model.generate_content(prompt)
            parts = response.text.split("===SPLIT===")
            if len(parts) >= 2:
                return parts[0].strip(), parts[1].strip()
            return parts[0].strip(), f"Suspect transaction message from {sender_id}. Text: {raw_text}"
        except Exception as e:
            logger.error(f"Error calling Gemini in CitizenShieldService: {e}", exc_info=True)
            return "", ""

citizen_shield_service = CitizenShieldService()
