"""The still-image analysis contract shared by the API and evaluation runner."""

import io
import os
import time
from typing import Literal

import httpx
from google import genai
from google.genai import errors, types
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field, ValidationError

MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
IMAGE_FORMATS = {"image/jpeg": "JPEG", "image/png": "PNG"}
HAZARDS = ("smokeDetected", "fireDetected", "stampedeDetected", "medicalEmergency", "potentialRisk")

PROMPT = """Review the attached still image for event safety. Base findings on visible evidence.
Estimate the number of visible people and their apparent density in the frame.
Flag visible smoke, fire, possible crowd crush or medical distress, or another visible hazard.
Mark uncertain when lighting, blur, obstruction, or ambiguous evidence prevents a reliable
assessment. Explain what an operator should verify in suggestedAction. A still image cannot
establish movement, medical diagnosis, or that the rest of the venue is safe.
Use incidentType "none" when there is no visible incident."""


class AnalysisError(Exception):
    def __init__(self, code, message, http_status):
        super().__init__(message)
        self.code = code
        self.http_status = http_status


class ImageFindings(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    personCount: int = Field(ge=0)
    crowdDensity: Literal["low", "moderate", "high"]
    smokeDetected: bool
    fireDetected: bool
    stampedeDetected: bool
    medicalEmergency: bool
    potentialRisk: bool
    incidentRecommended: bool
    uncertain: bool
    incidentType: str = Field(min_length=1, max_length=100)
    suggestedAction: str = Field(min_length=1, max_length=600)


def validate_image(data, mime_type):
    if mime_type not in IMAGE_FORMATS:
        raise AnalysisError("unsupported_type", "Choose a JPEG or PNG image.", 415)
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise AnalysisError("invalid_size", "Choose a nonempty image up to 5 MiB.", 413)
    try:
        with io.BytesIO(data) as stream, Image.open(stream, formats=list(IMAGE_FORMATS.values())) as image:
            if (image.format != IMAGE_FORMATS[mime_type]
                    or image.width * image.height > MAX_IMAGE_PIXELS
                    or getattr(image, "is_animated", False)):
                raise ValueError("Unsupported image format or dimensions")
            image.verify()
        with io.BytesIO(data) as stream, Image.open(stream) as image:
            image.load()
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        raise AnalysisError(
            "invalid_image", "Use a complete still JPEG or PNG of at most 20 megapixels.", 422
        ) from exc


class ImageAnalyzer:
    def __init__(self, generate, *, pause=time.sleep):
        self.generate = generate
        self.pause = pause

    def analyze(self, data, mime_type):
        validate_image(data, mime_type)
        for attempt in range(2):
            try:
                raw = self.generate(data, mime_type)
                findings = ImageFindings.model_validate_json(raw)
                break
            except (ValidationError, ValueError) as exc:
                raise AnalysisError(
                    "invalid_model_response", "Gemini returned unusable findings. Try again or review the image manually.", 502
                ) from exc
            except httpx.TimeoutException as exc:
                if attempt == 0:
                    self.pause(0.5)
                    continue
                raise AnalysisError("model_timeout", "Gemini timed out. Try again or review the image manually.", 504) from exc
            except (errors.APIError, httpx.TransportError) as exc:
                code = getattr(exc, "code", None)
                transient = isinstance(exc, httpx.TransportError) or code in {408, 429, 500, 502, 503, 504}
                if transient and attempt == 0:
                    self.pause(0.5)
                    continue
                if code in {408, 504}:
                    raise AnalysisError("model_timeout", "Gemini timed out. Try again or review the image manually.", 504) from exc
                message = "Gemini is unavailable. Try again shortly." if transient else "Check the Vertex model, region and service permissions."
                raise AnalysisError("model_unavailable", message, 503) from exc

        result = findings.model_dump()
        if findings.uncertain:
            status = "uncertain"
        elif any(result[key] for key in HAZARDS) or findings.incidentRecommended:
            status = "detected"
        else:
            status = "no_detection"
        return {"status": status, **result}


def vertex_analyzer():
    model = os.getenv("DRISHTI_VISION_MODEL", "gemini-2.5-pro")
    client = genai.Client(
        vertexai=True,
        project=os.environ["GCP_PROJECT"],
        location=os.getenv("GCP_REGION", "us-central1"),
        http_options=types.HttpOptions(
            timeout=20_000, retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    def generate(data, mime_type):
        response = client.models.generate_content(
            model=model,
            contents=[PROMPT, types.Part.from_bytes(data=data, mime_type=mime_type)],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ImageFindings,
                temperature=0,
            ),
        )
        return response.text

    return ImageAnalyzer(generate)
