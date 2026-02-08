import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# If running from repo source (backend/), keep data at repo root.
# If running from container where config.py is at /app, keep data in /app/data.
ROOT_DIR = (
    os.path.dirname(BASE_DIR)
    if os.path.basename(BASE_DIR) == "backend"
    else BASE_DIR
)
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(DATA_DIR, "salarium.db"))

JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
