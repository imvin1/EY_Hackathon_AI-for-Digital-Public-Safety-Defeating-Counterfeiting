from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SecurityThreadValidation(BaseModel):
    is_continuous: bool = Field(..., description="Flag if the security thread is continuous rather than printed/drawn")
    color_shift_valid: bool = Field(..., description="Flag if color shifting properties (green to blue) are detected")
    alignment_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of correct security thread alignment")

class MicroprintAnalysis(BaseModel):
    is_microprint_sharp: bool = Field(..., description="Flag if microtext print ('RBI' / 'BHARAT' in Hindi) is legible under magnification")
    sharpness_score: float = Field(..., ge=0.0, le=1.0)
    anomalies_detected: bool = Field(default=False)

class OCRValidationResult(BaseModel):
    extracted_serial_number: str = Field(..., description="Extracted banknote serial number")
    format_matches_rbi_standards: bool = Field(..., description="True if serial number pattern matches RBI guidelines")
    serial_number_confidence: float = Field(..., ge=0.0, le=1.0)
    is_blacklisted: bool = Field(default=False, description="Flag if serial number is listed in national counterfeit databases")

class CurrencyValidationResponse(BaseModel):
    note_id: str
    denomination: int = Field(..., description="INR Denomination detected: 10, 20, 50, 100, 200, 500, 2000")
    is_genuine: bool = Field(..., description="False if classified as suspect/counterfeit")
    authenticity_probability: float = Field(..., ge=0.0, le=1.0)
    security_thread: SecurityThreadValidation
    microprint: MicroprintAnalysis
    ocr_result: OCRValidationResult
    system_verdict: str = Field(..., description="Final text summary verdict (Genuine, Suspect, Counterfeit)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
