import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "salarium.db"))

JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")