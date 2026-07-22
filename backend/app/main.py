import time
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from backend.app.config import settings
from backend.app.routers.arrest_scam import router as arrest_scam_router
from backend.app.routers.counterfeit import router as counterfeit_router
from backend.app.routers.fraud_network import router as fraud_network_router
from backend.app.routers.geospatial import router as geospatial_router
from backend.app.routers.citizen_shield import router as citizen_shield_router

# Setup structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("defeatshield.main")

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="DefeatShield AI - A production-grade multi-agent public safety and fraud intelligence platform. Designed to combat counterfeit currency, transaction fraud rings, digital arrest scams, and facilitate real-time inter-district law enforcement coordination.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to trusted domains in production settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Performance Tracking Middleware
@app.middleware("http")
async def track_latency_and_perf_headers(request: Request, call_next):
    """
    Measures endpoint execution latency and appends processing duration headers
    for auditing and telemetry pipelines.
    """
    start_time = time.perf_counter()
    
    # Process request
    response = await call_next(request)
    
    process_duration = time.perf_counter() - start_time
    response.headers["X-Response-Time-Seconds"] = f"{process_duration:.4f}"
    
    # Trace execution logs
    logger.info(
        f"API CALL - {request.method} {request.url.path} | "
        f"Latency: {process_duration*1000:.2f}ms | Status Code: {response.status_code}"
    )
    return response

# 3. Custom Global Exception Definitions
class MLInferenceTimeoutException(Exception):
    """
    Custom exception raised when PyTorch/Transformers or Gemini inference
    exceeds allocated time limits.
    """
    def __init__(self, model_name: str, duration_limit_sec: float):
        self.model_name = model_name
        self.duration_limit_sec = duration_limit_sec
        super().__init__(f"ML Model '{model_name}' inference execution timed out after {duration_limit_sec}s limit.")

# 4. Custom Global Exception Handlers
@app.exception_handler(MLInferenceTimeoutException)
async def ml_timeout_exception_handler(request: Request, exc: MLInferenceTimeoutException):
    logger.error(f"ML Model Timeout on path {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "error_type": "ML_INFERENCE_TIMEOUT",
            "message": "The AI inference engine failed to compute a response within the allocated SLA time limit.",
            "model_name": exc.model_name,
            "threshold_seconds": exc.duration_limit_sec,
            "system_advisory": "Perform request retry with lowered batch sizing or check hardware accelerator allocations."
        }
    )

@app.exception_handler(SQLAlchemyError)
async def database_error_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.critical(f"Database connectivity/query failure on path {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error_type": "DATABASE_TRANSACTION_FAILURE",
            "message": "Critical connection failure encountered on PostgreSQL/Neo4j database node pools.",
            "details": str(exc) if settings.DEBUG else "Transaction rolled back due to internal database cluster issues.",
            "system_advisory": "Contact system administrators to verify connection pools and host credentials."
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Payload validation failure on path {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_type": "SCHEMA_VALIDATION_FAILURE",
            "message": "The request payload failed to parse against strict Pydantic models.",
            "validation_details": exc.errors(),
            "system_advisory": "Inspect request JSON body keys, formats, or image upload parameters."
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled system exception on path {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_type": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred during request execution.",
            "details": str(exc) if settings.DEBUG else "Review server execution traces for debugging details."
        }
    )

# 5. API v1 Router Registration
app.include_router(arrest_scam_router, prefix=settings.API_V1_STR)
app.include_router(counterfeit_router, prefix=settings.API_V1_STR)
app.include_router(fraud_network_router, prefix=settings.API_V1_STR)
app.include_router(geospatial_router, prefix=settings.API_V1_STR)
app.include_router(citizen_shield_router, prefix=settings.API_V1_STR)

# Root Health/Connectivity Endpoint
@app.get("/", tags=["Health Index"])
async def get_system_health():
    """
    Reports overall framework, configuration, and API gateway health statuses.
    """
    return {
        "status": "operational",
        "system_name": settings.PROJECT_NAME,
        "api_version_str": settings.API_V1_STR,
        "database_configuration": {
            "postgres_host": settings.db.POSTGRES_HOST,
            "neo4j_uri": settings.db.NEO4J_URI
        },
        "ai_model_thresholds": {
            "digital_arrest_confidence": settings.ai.SCAM_NLP_THRESHOLD,
            "counterfeit_matching_limit": settings.ai.CURRENCY_MIN_TEMPLATE_MATCH,
            "network_suspicion_trigger": settings.ai.GRAPH_CLUSTER_EPSILON
        },
        "timestamp": time.time()
    }
