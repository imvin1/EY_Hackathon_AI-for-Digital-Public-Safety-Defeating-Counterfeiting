import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl

class SecuritySettings(BaseSettings):
    """
    Cryptographic and authentication settings.
    """
    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    JWT_SECRET_KEY: str = Field(
        default="super-secure-production-grade-secret-key-ey-hackathon-2026",
        description="Key used for signing JWT tokens"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

class DatabaseSettings(BaseSettings):
    """
    Database settings for PostgreSQL (with PostGIS) and Neo4j graph database.
    """
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "public_safety_db"
    
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

class ModuleSettings(BaseSettings):
    """
    Thresholds and configurations for each of the 5 AI modules.
    """
    model_config = SettingsConfigDict(
        env_prefix="AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    # Module 1: Digital Arrest Scam Detection
    SCAM_NLP_THRESHOLD: float = Field(default=0.82, description="Similarity threshold for call script template matching")
    SCAM_SPEECH_ANOMALY_THRESHOLD: float = Field(default=0.75, description="Audio frequency variance anomaly threshold")
    
    # Module 2: Counterfeit Currency Agent
    CURRENCY_MIN_OCR_CONFIDENCE: float = Field(default=0.90, description="Minimum confidence score for OCR validation")
    CURRENCY_MIN_TEMPLATE_MATCH: float = Field(default=0.85, description="Min threshold for currency feature matching")
    CURRENCY_MICROPRINT_RESOLUTION_MIN: int = Field(default=300, description="Min DPI required for microprint scans")

    # Module 3: Fraud Network Graph
    GRAPH_CLUSTER_EPSILON: float = Field(default=0.35, description="Density clustering parameter for fraud networks")
    GRAPH_HIGH_RISK_DEGREE: int = Field(default=5, description="Node degree trigger for high-risk alerts")
    
    # Module 4: Geospatial Crime Pattern
    GEOSPATIAL_HOTSPOT_RADIUS_METERS: float = Field(default=1000.0, description="Radius to cluster geospatial fraud incidents")
    GEOSPATIAL_PATROL_VECTORS_LIMIT: int = Field(default=10, description="Max patrol routes generated in optimization")

    # Module 5: Citizen Shield
    CITIZEN_SHIELD_RISK_ALERT_LEVEL: float = Field(default=0.70, description="Risk level triggering MHA reporting warning")
    SUPPORTED_LANGUAGES_COUNT: int = 12

class Settings(BaseSettings):
    """
    Global settings aggregator.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    PROJECT_NAME: str = "DefeatShield AI - Digital Public Safety Platform"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # API Keys
    GEMINI_API_KEY: str = Field(
        default="AQ.Ab8RN6La74Dmo_zfWHpKguZOb-iXjV4a1p2FW1rE6WUK1XhO1w",
        description="Google Gemini Pro API key for LLM agents"
    )
    
    # Nested configurations
    db: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    ai: ModuleSettings = ModuleSettings()

# Single instances initialized on import
settings = Settings()
