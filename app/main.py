from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import search, blast
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EMBL-EBI SearchBot API",
    description="Backend API for natural language biological search.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(blast.router, prefix="/api/blast", tags=["BLAST"])

# Mount frontend files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    logger.warning(f"Frontend directory not found at {frontend_dir}. Skipping static files mount.")

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing EMBL-EBI SearchBot Backend...")
    # TODO: Initialize Elasticsearch and seed data if available
    try:
        from app.search.elasticsearch_service import es_service
        await es_service.initialize()
    except Exception as e:
        logger.warning(f"Elasticsearch fallback active. Could not initialize ES: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "EMBL-EBI SearchBot Prototype"}
