import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.errors import register_error_handlers
from app.routers import auth, imports

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Import contrôlé de résultats d'audit",
    description="Import CSV de constats d'audit, consultation et suivi de correction.",
    version="1.0.0",
    lifespan=lifespan,
)
register_error_handlers(app)

app.include_router(auth.router)
app.include_router(imports.router)
