from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from .routes.auth import router as auth_router
from .routes.persons import router as persons_router
from .routes.salaries import router as salaries_router
from .routes.stats import router as stats_router
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CORS_ORIGINS, DB_PATH


def create_app() -> FastAPI:
    app = FastAPI(title="Salarium", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add simple no-store cache headers for stats endpoints to ensure fresh data after salary mutations
    @app.middleware("http")
    async def add_cache_headers(request, call_next):
        response = await call_next(request)
        try:
            path = request.url.path
            if path.startswith("/api/stats"):
                response.headers["Cache-Control"] = "no-store"
        except Exception:
            pass
        return response

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(persons_router, prefix="/api/persons", tags=["persons"])
    app.include_router(salaries_router, prefix="/api/salaries", tags=["salaries"])
    app.include_router(stats_router, prefix="/api/stats", tags=["stats"])

    register_tortoise(
        app,
        db_url=f"sqlite://{DB_PATH}",
        modules={"models": [
            "app.models.user",
            "app.models.person",
            "app.models.salary_record",
        ]},
        generate_schemas=True,
        add_exception_handlers=True,
    )

    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    if os.path.exists(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()
