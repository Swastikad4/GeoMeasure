import os
from pathlib import Path

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./geospatial.db")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "uploads")).resolve()
    ALLOWED_EXTENSIONS: set = {".kml", ".zip"}
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ]

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
