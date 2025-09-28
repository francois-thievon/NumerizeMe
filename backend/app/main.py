from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .core.config import get_settings
from .db.base import Base, engine, get_db
from .api import auth, users, questionnaires, matches, test
from .db.init_db import init_questionnaires

# Configuration du logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Création des tables dans la base de données
Base.metadata.create_all(bind=engine)

def init_db():
    db = next(get_db())
    init_questionnaires(db)

settings = get_settings()
app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Available routes:")
    for route in app.routes:
        logger.info(f"Route: {route.path}, methods: {route.methods}")

# Configuration CORS pour permettre les requêtes depuis l'app Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de test
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Inclusion des routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(questionnaires.router, prefix="/api/questionnaires", tags=["questionnaires"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(test.router, prefix="/api/test", tags=["test"])

@app.get("/")
async def root():
    return {
        "message": f"Bienvenue sur l'API {settings.PROJECT_NAME}",
        "version": settings.PROJECT_VERSION
    }
