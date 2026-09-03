import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router
from app.api.analysis import router as analysis_router
from app.api.documents import router as documents_router
from app.api.evaluation import router as evaluation_router

logger = logging.getLogger("ventureos.main")

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="VentureOS API",
    description="AI-Powered Startup Intelligence Platform — Multi-Agent Strategy & Evaluation",
    version="0.9.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js frontend during development
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# PART 15: Central Safe Error Handling
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Standardized HTTP error handler with safe client responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catches unhandled errors, logs complete stack trace on server,
    and returns a sanitized error response without leaking keys or internals.
    """
    logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "An internal server error occurred while processing the analysis.",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(router)
app.include_router(analysis_router)
app.include_router(documents_router)
app.include_router(evaluation_router)
