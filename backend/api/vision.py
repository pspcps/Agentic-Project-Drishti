import logging
from typing import Annotated

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StringConstraints

from agents.vision_analysis import VisionAnalysisAgent
from utils.image_analysis import AnalysisError

router = APIRouter()
vision_agent = VisionAnalysisAgent()
logger = logging.getLogger(__name__)
DocumentId = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[^/]+$", max_length=250)]


class MediaEvent(BaseModel):
    fileUrl: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2048)]
    zone: DocumentId
    docId: DocumentId
    autoIncident: bool = False


@router.post("/analyze-media")
def analyze_media(payload: MediaEvent):
    try:
        return vision_agent.handle_media_event(payload.model_dump())
    except AnalysisError as exc:
        return JSONResponse(
            status_code=exc.http_status,
            content={"success": False, "status": "analysis_failed", "code": exc.code, "error": str(exc)},
        )
    except Exception:
        logger.exception("Unexpected image analysis failure")
        return JSONResponse(
            status_code=503,
            content={"success": False, "status": "analysis_failed", "code": "analysis_unavailable",
                     "error": "Analysis is unavailable. Check the service configuration or review the image manually."},
        )
