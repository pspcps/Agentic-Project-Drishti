"""Loopback development entry point for the existing upload and analysis routers."""

from fastapi import FastAPI

from api.upload import router as upload_router
from api.vision import router as vision_router

app = FastAPI(title="Project Drishti image API (local development)")
app.include_router(upload_router, prefix="/api")
app.include_router(vision_router, prefix="/api")
