import json
import uuid
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from app.config import settings
from app.database import create_file_record, update_file_record, get_file_record
from app.utils.security import sanitize_filename, validate_file_extension, safe_extract_zip
from app.services.geospatial_service import GeospatialService

logger = logging.getLogger(__name__)

class FileService:
    @staticmethod
    def _get_file_dir(file_id: str) -> Path:
        target_dir = settings.UPLOAD_DIR / file_id
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    @classmethod
    async def save_and_validate_upload(cls, upload_file: UploadFile) -> Tuple[str, Path, str, str]:
        """
        Validates and saves the uploaded file to disk.
        Returns:
            (file_id, saved_path, clean_filename, extension)
        """
        raw_filename = upload_file.filename or "uploaded_file"
        clean_name = sanitize_filename(raw_filename)
        ext = validate_file_extension(clean_name)

        file_id = uuid.uuid4().hex[:12]
        file_dir = cls._get_file_dir(file_id)
        saved_file_path = file_dir / clean_name

        # Read in chunks to enforce MAX_FILE_SIZE_MB
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        total_size = 0

        with open(saved_file_path, "wb") as f:
            while chunk := await upload_file.read(1024 * 1024):  # 1MB chunks
                total_size += len(chunk)
                if total_size > max_bytes:
                    saved_file_path.unlink(missing_ok=True)
                    shutil.rmtree(file_dir, ignore_errors=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB."
                    )
                f.write(chunk)

        if total_size == 0:
            saved_file_path.unlink(missing_ok=True)
            shutil.rmtree(file_dir, ignore_errors=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty (0 bytes)."
            )

        return file_id, saved_file_path, clean_name, ext

    @classmethod
    def locate_geospatial_file(cls, file_dir: Path, saved_file_path: Path, ext: str) -> Path:
        """
        Resolves the actual geospatial dataset file (.kml or .shp from zip).
        """
        if ext == ".kml":
            return saved_file_path

        if ext == ".zip":
            extracted_dir = file_dir / "extracted"
            safe_extract_zip(saved_file_path, extracted_dir)

            # Search recursively for .shp file
            shp_files = list(extracted_dir.rglob("*.shp"))
            if not shp_files:
                # Also check uppercase
                shp_files = list(extracted_dir.rglob("*.SHP"))
            
            if not shp_files:
                raise ValueError("No Shapefile (.shp) found within the uploaded ZIP archive.")

            return shp_files[0]

        raise ValueError(f"Unsupported file type '{ext}'.")

    @classmethod
    def process_file(cls, file_id: str, saved_file_path: Path, clean_name: str, ext: str) -> Dict[str, Any]:
        """
        Processes the uploaded geospatial file and stores the metadata.
        """
        file_dir = cls._get_file_dir(file_id)
        file_type = "KML" if ext == ".kml" else "Shapefile (ZIP)"

        # Initialize record in DB
        create_file_record(
            file_id=file_id,
            filename=clean_name,
            file_type=file_type,
            file_path=str(saved_file_path),
            status="PROCESSING"
        )

        try:
            target_geo_file = cls.locate_geospatial_file(file_dir, saved_file_path, ext)
            features, summary, crs_name, warning = GeospatialService.process_geospatial_file(target_geo_file)

            # Save extracted features and summary to local JSON cache
            cache_file = file_dir / "processed_data.json"
            cache_payload = {
                "file_id": file_id,
                "crs": crs_name,
                "warning": warning,
                "summary": summary.model_dump(),
                "features": features
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f)

            # Update DB record to COMPLETED
            update_file_record(
                file_id=file_id,
                status="COMPLETED",
                feature_count=len(features),
                crs=crs_name,
                error_message=warning  # Can carry any non-fatal warning
            )

            record = get_file_record(file_id)
            return {
                "id": file_id,
                "filename": clean_name,
                "file_type": file_type,
                "feature_count": len(features),
                "crs": crs_name,
                "status": "COMPLETED",
                "warning_message": warning,
                "summary": summary.model_dump(),
                "created_at": record.get("created_at") if record else ""
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to process geospatial file {file_id}: {error_msg}", exc_info=True)
            update_file_record(
                file_id=file_id,
                status="FAILED",
                feature_count=0,
                error_message=error_msg
            )
            # Re-raise clean ValueError for route handler to format
            raise ValueError(f"Geospatial processing failed: {error_msg}")

    @classmethod
    def get_processed_data(cls, file_id: str) -> Optional[Dict[str, Any]]:
        file_dir = cls._get_file_dir(file_id)
        cache_file = file_dir / "processed_data.json"
        if not cache_file.exists():
            return None
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
