from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import router


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI instance
    """
    app = FastAPI(
        title="Sovereign AI Verifier API",
        description="REST API for intelligent social support application processing",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # ===== CORS CONFIGURATION =====
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change to specific domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ===== INCLUDE ROUTES =====
    app.include_router(router)
    
    # ===== ROOT ENDPOINT =====
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": "Sovereign AI Verifier",
            "version": "1.0.0",
            "docs": "/docs",
            "status": "running"
        }
    
    # ===== EXCEPTION HANDLERS =====
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle general exceptions."""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc)
            }
        )
    
    return app