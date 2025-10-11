from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from .routes.auth import router as auth_router
from .routes.persons import router as persons_router
from .routes.salaries import router as salaries_router
from .routes.salary_templates import router as salary_templates_router
from .routes.category_stats import router as category_stats_router
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

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(persons_router, prefix="/api/persons", tags=["persons"])
    app.include_router(salaries_router, prefix="/api/salaries", tags=["salaries"])
    app.include_router(salary_templates_router, prefix="/api/salary-templates", tags=["salary-templates"])
    app.include_router(category_stats_router, prefix="/api/category-stats", tags=["category-stats"])
    app.include_router(stats_router, prefix="/api/stats", tags=["stats"])

    register_tortoise(
        app,
        db_url=f"sqlite://{DB_PATH}",
        modules={"models": ["app.models.user", "app.models.person", "app.models.salary_record", "app.models.salary_template"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )

    return app


app = create_app()