"""
BoonMindX Capital Shield API - Main Application
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import API_TITLE, API_VERSION, API_PREFIX, ALLOWED_ORIGINS
from app.core.version import API_VERSION as VERSION
from app.routes import signal, risk, filter, regime, healthz, metrics
from app.routes import dashboard_metrics
from app.api import billing
import os

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=VERSION,
    description="Deterministic Risk Filtering API for Quant Funds"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(signal.router, prefix=API_PREFIX, tags=["Signals"])
app.include_router(risk.router, prefix=API_PREFIX, tags=["Risk"])
app.include_router(filter.router, prefix=API_PREFIX, tags=["Filter"])
app.include_router(regime.router, prefix=API_PREFIX, tags=["Regime"])
app.include_router(healthz.router, prefix=API_PREFIX, tags=["Health"])
app.include_router(metrics.router, prefix=API_PREFIX, tags=["Metrics"])
app.include_router(dashboard_metrics.router, prefix=API_PREFIX, tags=["Dashboard"])
app.include_router(billing.router, prefix=API_PREFIX, tags=["Billing"])

# Mount dashboard static files
dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/dashboard", StaticFiles(directory=dashboard_path, html=True), name="dashboard")

# Redirect /dashboard to /dashboard/
@app.get("/dashboard", include_in_schema=False)
async def dashboard_root():
    return RedirectResponse(url="/dashboard/")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": API_TITLE,
        "version": VERSION,
        "status": "operational",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    from app.core.config import HOST, PORT
    
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )

