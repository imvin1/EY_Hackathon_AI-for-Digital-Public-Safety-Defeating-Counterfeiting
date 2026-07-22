import logging
import uuid
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from backend.app.config import settings
from backend.app.models.arrest_scam import (
    ArrestScamAnalysisRequest, 
    ArrestScamAnalysisResponse, 
    MhaAlert, 
    CallerProfile, 
    MediaIndicators
)

logger = logging.getLogger("defeatshield.arrest_scam_service")

class ArrestScamDetectionService:
    def __init__(self):
        # Configure Gemini API client
        self.use_gemini = False
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_gemini = True
                logger.info("Gemini API successfully configured for Arrest Scam service.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini API client. Using local heuristic fallback: {e}")
        else:
            logger.warning("No Gemini API Key provided. Using local heuristic fallback.")

        # Precompiled lists of high-impact digital arrest threat vectors
        self.coercive_keywords = {
            "digital arrest": 0.95,
            "cbse": 0.30,
            "cbi": 0.90,
            "customs": 0.85,
            "contraband": 0.90,
            "drugs found": 0.90,
            "money laundering": 0.85,
            "supreme court": 0.80,
            "police custody": 0.90,
            "do not disconnect": 0.95,
            "stay on video call": 0.95,
            "arrest warrant": 0.90,
            "enforcement directorate": 0.90,
            "illegal parcel": 0.85,
            "mdma": 0.90,
            "secret code": 0.70,
            "national security": 0.80
        }

    async def analyze_scam_session(self, request: ArrestScamAnalysisRequest) -> ArrestScamAnalysisResponse:
        """
        Processes transcript text and call metadata to estimate digital arrest likelihood,
        cross-references audio/video metrics, and fires MHA alert if thresholds are crossed.
        """
        try:
            # 1. Evaluate Caller ID spoofing signatures
            spoof_confidence = request.caller.spoofing_confidence
            if request.caller.is_voip:
                spoof_confidence = max(spoof_confidence, 0.75)
            if request.caller.carrier_mismatch:
                spoof_confidence = max(spoof_confidence, 0.80)

            # 2. Extract script template matching via LLM or Heuristics
            scam_prob, coercion_score, matched_templates = await self._analyze_transcript(request.transcript)

            # 3. Incorporate Audio/Video anomaly signals
            synthetic_voice_prob = 0.0
            cv_flag_uniform = False
            cv_flag_backdrop = False

            if request.media:
                synthetic_voice_prob = request.media.voice_synthetic_probability
                cv_flag_uniform = request.media.fake_uniform_detected
                cv_flag_backdrop = request.media.fake_backdrop_detected

            # Adjust probability based on multiple vectors (sensor fusion)
            final_prob = scam_prob
            if synthetic_voice_prob > 0.7:
                final_prob = min(1.0, final_prob + 0.15)
            if cv_flag_uniform:
                final_prob = min(1.0, final_prob + 0.20)
            if cv_flag_backdrop:
                final_prob = min(1.0, final_prob + 0.15)
            if spoof_confidence > 0.8:
                final_prob = min(1.0, final_prob + 0.10)

            # Gather indicators triggered
            indicators = []
            if spoof_confidence > 0.7: indicators.append("VOIP_SPOOF_SIGNATURE")
            if cv_flag_uniform: indicators.append("FAKE_UNIFORM_VISUAL_SIGN")
            if cv_flag_backdrop: indicators.append("FAKE_GOVERNMENT_BACKDROP")
            if synthetic_voice_prob > 0.7: indicators.append("SYNTHETIC_SPEECH_PATTERN")
            if coercion_score > 0.75: indicators.append("SEVERE_PSYCHOLOGICAL_COERCION")

            # 4. Generate MHA Alert if threshold is exceeded
            alert_generated = False
            alert_details = None
            if final_prob >= settings.ai.SCAM_NLP_THRESHOLD:
                alert_generated = True
                severity = "CRITICAL" if final_prob > 0.90 else "HIGH"
                
                reasons = matched_templates.copy()
                if indicators:
                    reasons.extend(indicators)

                alert_details = MhaAlert(
                    alert_id=f"MHA-ALERT-{uuid.uuid4().hex[:12].upper()}",
                    target_phone=request.caller.phone_number,
                    severity=severity,
                    reasons=reasons,
                    alert_timestamp=datetime.utcnow(),
                    forwarded_to_telecom=True,
                    forwarded_to_cyber_cell=True
                )
                logger.info(f"MHA Alert generated for phone number: {request.caller.phone_number} with severity {severity}")

            return ArrestScamAnalysisResponse(
                call_id=request.call_id,
                scam_probability=round(final_prob, 3),
                coercion_score=round(coercion_score, 3),
                matched_script_templates=matched_templates,
                spoofing_indicators_triggered=indicators,
                mha_alert_generated=alert_generated,
                alert_details=alert_details,
                confidence_level=0.92 if self.use_gemini else 0.78
            )

        except Exception as e:
            logger.error(f"Error executing Arrest Scam Analysis for call {request.call_id}: {e}", exc_info=True)
            # Safe production fallback response to prevent server error
            return ArrestScamAnalysisResponse(
                call_id=request.call_id,
                scam_probability=0.5,
                coercion_score=0.5,
                matched_script_templates=["FALLBACK_ERROR_PARSING"],
                spoofing_indicators_triggered=["PROCESSING_TIMEOUT"],
                mha_alert_generated=False,
                alert_details=None,
                confidence_level=0.1
            )

    async def _analyze_transcript(self, transcript: str) -> tuple[float, float, list[str]]:
        """
        Uses Gemini LLM to parse transcript logic or falls back to custom keywords.
        Returns: (scam_probability, coercion_score, matched_templates)
        """
        if self.use_gemini:
            try:
                prompt = (
                    "You are a specialized public safety AI classifier. Analyze the following transcript of an incoming phone call. "
                    "Determine if the caller is running a 'Digital Arrest Scam' (where they pretend to be police, customs, CBI, ED, "
                    "or judicial officials accusing the victim of a drug package, money laundering, CBSE infraction, or other crimes, "
                    "and ordering them to stay on video and keep quiet).\n\n"
                    f"Call Transcript:\n\"{transcript}\"\n\n"
                    "Provide your evaluation output exactly in the following raw format (no markdown code blocks, just raw lines):\n"
                    "ScamProbability: <float between 0.0 and 1.0>\n"
                    "CoercionScore: <float between 0.0 and 1.0 based on level of threat/isolation techniques>\n"
                    "MatchedTemplates: <comma-separated list of matches like 'Customs Drug Importation', 'CBI Fake Warrant', 'ED Money Laundering', 'CBSE Student Harassment'>\n"
                )
                
                # Perform API call asynchronously in executor
                response: GenerateContentResponse = self.gemini_model.generate_content(prompt)
                lines = response.text.strip().split("\n")
                
                scam_prob = 0.0
                coercion = 0.0
                templates = []
                
                for line in lines:
                    if line.startswith("ScamProbability:"):
                        scam_prob = float(line.split(":")[1].strip())
                    elif line.startswith("CoercionScore:"):
                        coercion = float(line.split(":")[1].strip())
                    elif line.startswith("MatchedTemplates:"):
                        val = line.split(":")[1].strip()
                        if val and val.lower() != "none":
                            templates = [t.strip() for t in val.split(",")]
                
                return scam_prob, coercion, templates
            except Exception as e:
                logger.error(f"Gemini API execution failed: {e}. Falling back to heuristic model.", exc_info=True)

        # Heuristic fallback parsing
        transcript_lower = transcript.lower()
        score = 0.0
        matched_templates = []
        matched_keywords_count = 0
        
        for kw, weight in self.coercive_keywords.items():
            if kw in transcript_lower:
                score += weight
                matched_keywords_count += 1
                
        # Normalize heuristics
        scam_prob = min(0.98, (score / 4.0)) if matched_keywords_count > 0 else 0.05
        coercion_score = min(0.95, (score / 4.5)) if matched_keywords_count > 0 else 0.05
        
        # Script matching logic
        if any(w in transcript_lower for w in ["customs", "illegal parcel", "fedex", "dhl"]):
            matched_templates.append("Customs Drug Importation Scam")
        if any(w in transcript_lower for w in ["cbi", "supreme court", "arrest warrant", "digital arrest"]):
            matched_templates.append("CBI Fake Judicial Warrant")
        if any(w in transcript_lower for w in ["money laundering", "bank account validation", "enforcement directorate"]):
            matched_templates.append("ED Money Laundering Scam")
            
        if not matched_templates and scam_prob > 0.4:
            matched_templates.append("Undetermined Threat Coercion Script")
            
        return scam_prob, coercion_score, matched_templates

arrest_scam_service = ArrestScamDetectionService()
