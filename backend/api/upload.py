import logging
from pathlib import PurePath

from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4
from google.cloud import storage, firestore
from datetime import timedelta
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from utils.firestore_utils import add_document
from typing import Optional
from agents.vision_analysis import VISION_BUCKET
from utils.image_analysis import IMAGE_FORMATS, MAX_IMAGE_BYTES

router = APIRouter()

# Google Cloud setup
logger = logging.getLogger(__name__)

DEFAULT_BUCKET = "project-drishti-central1-bucket"
VENUE_BUCKET = "project-drishti-central1-bucket-venues"

# Request body model
class UploadRequest(BaseModel):
    filename: str
    mimetype: str
    zone: str
    notes: str = ""
    type: Optional[str] = None
    bucket: Optional[str] = None
    size: Optional[int] = None

@router.post("/upload/presigned-url")
def get_signed_upload_url(req: UploadRequest):
    try:
        if not all(value.strip() for value in (req.filename, req.mimetype, req.zone)):
            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"error": "Missing required fields."}
            )

        is_vision = req.type == "vision" or req.bucket == VISION_BUCKET
        if is_vision:
            if req.mimetype not in IMAGE_FORMATS:
                return JSONResponse(status_code=415, content={"error": "Choose a JPEG or PNG image."})
            if req.size is None or not 0 < req.size <= MAX_IMAGE_BYTES:
                return JSONResponse(status_code=413, content={"error": "Choose a nonempty image up to 5 MiB."})
            if "/" in req.zone or len(req.zone) > 250:
                return JSONResponse(status_code=422, content={"error": "Choose a valid zone."})
            suffix = PurePath(req.filename).suffix.lower()
            allowed = {".jpg", ".jpeg"} if req.mimetype == "image/jpeg" else {".png"}
            if suffix not in allowed:
                return JSONResponse(status_code=415, content={"error": "The extension must match the image format."})
            object_path = f"uploads/{uuid4()}{suffix}"
        else:
            object_path = f"uploads/{uuid4()}_{req.filename}"

        # Determine bucket name
        if is_vision:
            bucket_name = VISION_BUCKET
        elif req.bucket and req.bucket not in {DEFAULT_BUCKET, VENUE_BUCKET}:
            return JSONResponse(status_code=422, content={"error": "Unknown upload bucket."})
        elif req.bucket:
            bucket_name = req.bucket
        elif req.type == "venue":
            bucket_name = VENUE_BUCKET
        else:
            bucket_name = DEFAULT_BUCKET

        bucket = storage.Client().bucket(bucket_name)
        blob = bucket.blob(object_path)

        # Signed URL generation
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=5),
            method="PUT",
            content_type=req.mimetype,
            headers={"Content-Length": str(req.size)} if is_vision else None,
        )

        # Save metadata in Firestore
        media_doc = {
            "zone": req.zone,
            "notes": req.notes or "",
            "fileUrl": f"https://storage.googleapis.com/{bucket_name}/{object_path}",
            "objectPath": object_path,
            "type": "image" if req.mimetype.startswith("image") else "video",
            "timestamp": firestore.SERVER_TIMESTAMP,
        }

        doc_ref = add_document("media", media_doc)
        doc_id = doc_ref[1].id
        return {"url": url, "objectPath": object_path, "docId": doc_id, "fileUrl": media_doc["fileUrl"]}
    
    except Exception:
        logger.exception("Could not create signed upload")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Could not prepare the upload. Check the storage and signing configuration."}
        )
