import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse

from app.database import get_file_record, list_file_records
from app.services.file_service import FileService
from app.schemas.file_schema import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_geospatial_file(file: UploadFile = File(...)):
    """
    Upload and process a geospatial file (.kml or .zip Shapefile).
    """
    try:
        file_id, saved_path, clean_name, ext = await FileService.save_and_validate_upload(file)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload validation failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": f"Upload validation failed: {str(e)}"}
        )

    try:
        result = FileService.process_file(file_id, saved_path, clean_name, ext)
        return {
            "success": True,
            "data": result,
            "message": "File processed successfully"
        }
    except ValueError as ve:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "message": f"Processing error: {str(ve)}"}
        )
    except Exception as e:
        logger.error(f"Unexpected processing error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "An error occurred while processing the geospatial file."}
        )

@router.get("/samples/{sample_name}")
def get_sample_file(sample_name: str):
    """
    Returns pre-generated sample geospatial files for quick testing.
    """
    sample_dir = Path(__file__).parent.parent.parent.parent / "sample_data"
    safe_name = Path(sample_name).name
    target_path = (sample_dir / safe_name).resolve()
    
    if not str(target_path).startswith(str(sample_dir.resolve())) or not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample file '{sample_name}' not found."
        )
    return FileResponse(target_path, filename=safe_name)

@router.get("/")
def get_all_files():
    """
    Returns list of all uploaded and processed files.
    """
    records = list_file_records()
    return {
        "success": True,
        "data": records,
        "message": f"Retrieved {len(records)} file records."
    }

@router.get("/{file_id}/")
def get_file_info(file_id: str):
    """
    Retrieves file metadata, processing summary, and CRS info.
    """
    record = get_file_record(file_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' was not found."
        )

    processed_data = FileService.get_processed_data(file_id)
    summary = processed_data.get("summary") if processed_data else None

    response_data = {
        "id": record["id"],
        "filename": record["filename"],
        "file_type": record["file_type"],
        "feature_count": record["feature_count"],
        "crs": record["crs"],
        "status": record["status"],
        "error_message": record["error_message"],
        "created_at": record["created_at"],
        "summary": summary
    }

    return {
        "success": True,
        "data": response_data,
        "message": "File details retrieved successfully"
    }

@router.get("/{file_id}/features/")
def get_file_features(file_id: str):
    """
    Returns extracted geospatial features including geometry types,
    properties, measurements, and GeoJSON shapes for map display.
    """
    record = get_file_record(file_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' was not found."
        )

    if record["status"] != "COMPLETED":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": f"File is in status '{record['status']}'. Features are unavailable."
            }
        )

    processed_data = FileService.get_processed_data(file_id)
    if not processed_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed feature data is missing or corrupted."
        )

    return {
        "success": True,
        "data": {
            "file_id": file_id,
            "crs": record["crs"],
            "feature_count": record["feature_count"],
            "features": processed_data.get("features", [])
        },
        "message": "Features retrieved successfully"
    }

@router.get("/{file_id}/measurements/")
def get_file_measurements(file_id: str):
    """
    Returns geometry measurements (area in m², length in m) and overall summary.
    """
    record = get_file_record(file_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID '{file_id}' was not found."
        )

    if record["status"] != "COMPLETED":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": f"File is in status '{record['status']}'. Measurements are unavailable."
            }
        )

    processed_data = FileService.get_processed_data(file_id)
    if not processed_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed measurement data is missing or corrupted."
        )

    measurements_list = [
        {
            "feature_id": f["feature_id"],
            "geometry_type": f["geometry_type"],
            "measurement": f["measurement"]
        }
        for f in processed_data.get("features", [])
    ]

    return {
        "success": True,
        "data": {
            "file_id": file_id,
            "crs": record["crs"],
            "summary": processed_data.get("summary", {}),
            "measurements": measurements_list
        },
        "message": "Measurements retrieved successfully"
    }
