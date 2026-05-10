# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from constants import ALLOW_CORS_ORIGINS

from backend import models, database
from backend.routes import routers

# Initialize app
app = FastAPI(title="PONS Dictionary Client API")
#models.Base.metadata.drop_all(bind=database.engine)
models.Base.metadata.create_all(bind=database.engine)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
for r in routers:
    app.include_router(r)