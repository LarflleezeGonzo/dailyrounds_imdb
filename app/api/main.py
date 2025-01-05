from fastapi import APIRouter

from app.api.routes import csv_upload, ping, movies

api_router = APIRouter()
api_router.include_router(ping.router)
api_router.include_router(csv_upload.router)
api_router.include_router(movies.router)

