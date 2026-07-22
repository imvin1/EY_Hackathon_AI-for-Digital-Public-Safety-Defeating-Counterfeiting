from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CitizenRiskQuery(BaseModel):
    query_id: str
    query_text: str = Field(..., description="The SMS, WhatsApp text, or description of the suspicious call/voice message")
    input_medium: str = Field(..., description="SMS, WHATSAPP, PHONE_CALL, UPI_ID, WEBSITE_URL")
    sender_identifier: Optional[str] = Field(None, description="The phone number, UPI ID, shortcode, or URL being queried")
    language_code: str = Field(default="en", description="One of 12 regional language codes: en, hi, ta, te, bn, mr, kn, gu, ml, pa, or, as")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NcrbReportingGuide(BaseModel):
    portal_category: str = Field(..., description="Category for National Cyber Crime Reporting Portal reporting")
    portal_subcategory: str = Field(..., description="Subcategory for reporting")
    draft_complaint_text: str = Field(..., description="Pre-filled, structured legal description of the scam incident to copy-paste")
    suggested_evidence_attachments: List[str] = Field(default_factory=list, description="Documents citizen should attach (e.g. Call logs, screenshots)")
    direct_portal_url: str = "https://cybercrime.gov.in"

class CitizenRiskResponse(BaseModel):
    query_id: str
    risk_level: str = Field(..., description="SAFE, SUSPICIOUS, HIGH_RISK, CRITICAL")
    risk_score: float = Field(..., ge=0.0, le=1.0)
    detected_scam_type: Optional[str] = None
    risk_factors: List[str] = Field(default_factory=list, description="Specific features making this message/contact risky")
    dynamic_advisory: str = Field(..., description="Actionable advisory translated into the queried language")
    ncrb_guide: NcrbReportingGuide
    timestamp: datetime
