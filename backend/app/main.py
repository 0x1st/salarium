from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
        @app.get("/{full_path:path}")
        def spa_fallback(full_path: str):
            """Return static asset if exists; otherwise index.html for SPA routes."""
            # Do not interfere with API paths
            if full_path.startswith("api"):
                raise HTTPException(status_code=404, detail="Not Found")

            # Serve real static asset to avoid MIME mismatches in production
            asset_path = os.path.join(static_dir, full_path)
            if os.path.isfile(asset_path):
                return FileResponse(asset_path)

            # Fallback to SPA entry for client-side routing
            index_path = os.path.join(static_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)

            raise HTTPException(status_code=404, detail="Not Found")

        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()
