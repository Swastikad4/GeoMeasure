import os
import re
import zipfile
from pathlib import Path
from fastapi import HTTPException, status
from app.config import settings

def sanitize_filename(filename: str) -> str:
    # Remove directory separators and unsafe characters
    base_name = os.path.basename(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name)
    return clean_name or "uploaded_file"

def validate_file_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: .kml, .zip (containing Shapefile)."
        )
    return ext

def safe_extract_zip(zip_path: Path, target_dir: Path) -> Path:
    """
    Safely extract a zip archive preventing Zip Slip directory traversal attacks.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    target_dir_resolved = target_dir.resolve()

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            # Resolve destination path
            dest_path = (target_dir / member.filename).resolve()
            
            # Check for path traversal attempts
            if not str(dest_path).startswith(str(target_dir_resolved)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Security risk: archive contains malicious path '{member.filename}'."
                )
        
        # Extract files safely
        zip_ref.extractall(target_dir_resolved)

    return target_dir_resolved
